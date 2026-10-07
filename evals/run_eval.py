#!/usr/bin/env python3
"""Headless eval of the Somerville answer agent across models.

Runs inside an *isolated* oxy project (default ~/oxygen-eval: a copy of this repo
with a frozen copy of data/somerville.duckdb), never the production checkout, so
the live portal and the pipeline-refresh writer are untouched.

For each model in models.yaml it registers an OpenRouter model in the eval
project's config.yml, writes agents/eval_<name>.agent.yml (the answer agent with
only `model:` changed), asks every question via `oxy run`, and scores the final
prose against the question's truth_sql evaluated on the same snapshot.

Usage (on the box):
  python evals/run_eval.py --truths-only                 # print truths for review
  python evals/run_eval.py --pilot --reps 1              # cheap first pass
  python evals/run_eval.py --models haiku-4-5 --tiers simple --budget 2
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import math
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

import duckdb
import yaml

EVAL_DIR = Path(__file__).resolve().parent
ANSI = re.compile(r"\x1b\[[0-9;]*m")
NUM = re.compile(r"(?<![\w.])-?\$?(\d{1,3}(?:,\d{3})+|\d+)(\.\d+)?\s*(%|percent|k\b|thousand|million|m\b)?", re.I)
JUDGE_SLUG = "anthropic/claude-sonnet-5.5"


# ------------------------------------------------------------------ helpers
def load_yaml(path: Path) -> dict[str, Any]:
    with path.open() as f:
        return yaml.safe_load(f)


def openrouter_usage(key: str) -> float | None:
    """Cumulative account spend in USD, or None if the call fails."""
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/credits", headers={"Authorization": f"Bearer {key}"}
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return float(json.load(r)["data"]["total_usage"])
    except (urllib.error.URLError, KeyError, ValueError, TimeoutError):
        return None


def compute_truths(db_path: Path, questions: list[dict[str, Any]]) -> tuple[dict[str, list[tuple]], dict[str, str]]:
    """Truth rows per question id, plus errors for any truth_sql that fails."""
    con = duckdb.connect(str(db_path), read_only=True)
    truths: dict[str, list[tuple]] = {}
    errors: dict[str, str] = {}
    try:
        for q in questions:
            try:
                truths[q["id"]] = con.sql(q["truth_sql"]).fetchall()
            except duckdb.Error as e:
                errors[q["id"]] = str(e).splitlines()[0]
    finally:
        con.close()
    return truths, errors


def ensure_model(project: Path, cfg: dict[str, Any], m: dict[str, Any]) -> str:
    """Register the model in the eval project's config.yml; write its agent file."""
    oxy_name = f"eval-{m['name']}"
    config_path = project / "config.yml"
    config = load_yaml(config_path)
    models = [x for x in config.get("models", []) if x.get("name") != oxy_name]
    models.append({
        "name": oxy_name,
        "vendor": "anthropic",
        "model_ref": m["slug"],
        "key_var": cfg["key_var"],
        "api_url": cfg["api_url"],
    })
    config["models"] = models
    with config_path.open("w") as f:
        yaml.safe_dump(config, f, sort_keys=False)

    src = (project / "agents" / "answer_agent.agent.yml").read_text()
    agent = re.sub(r"(?m)^model:.*$", f"model: {oxy_name}", src, count=1)
    agent_path = project / "agents" / f"eval_{m['name']}.agent.yml"
    agent_path.write_text(agent)
    return str(agent_path.relative_to(project))


def ask(project: Path, agent_rel: str, question: str, timeout: int) -> tuple[str, int, float]:
    t0 = time.monotonic()
    try:
        p = subprocess.run(
            ["oxy", "run", agent_rel, question],
            cwd=project, capture_output=True, text=True, timeout=timeout,
        )
        out = p.stdout + ("\n[stderr]\n" + p.stderr if p.stderr.strip() else "")
        code = p.returncode
    except subprocess.TimeoutExpired as e:
        raw = e.stdout or ""
        out = (raw.decode(errors="replace") if isinstance(raw, bytes) else raw) + "\n[TIMEOUT]"
        code = -9
    return ANSI.sub("", out), code, time.monotonic() - t0


def final_answer(transcript: str) -> str:
    """The agent's closing prose: text after the last 'Output:' marker."""
    parts = re.split(r"(?m)^Output:\s*$", transcript)
    return parts[-1].split("[stderr]")[0].strip() if len(parts) > 1 else ""


def numbers_in(text: str) -> list[float]:
    vals = []
    for m in NUM.finditer(text):
        whole, frac, unit = m.group(1), m.group(2) or "", (m.group(3) or "").lower()
        v = float(whole.replace(",", "") + frac)
        if unit in ("k", "thousand"):
            v *= 1_000
        elif unit in ("million", "m"):
            v *= 1_000_000
        vals.append(-v if m.group(0).lstrip().startswith("-") else v)
    return vals


def score_numeric(q: dict[str, Any], truth: float, answer: str) -> bool:
    cands = numbers_in(answer)
    if q["answer_type"] == "percent":
        cands += [c * 100 for c in cands if abs(c) <= 1]  # 0.774 -> 77.4
    if "abs_tol" in q:
        # Sign-insensitive: "fell 14%" carries the sign in words, not digits.
        return any(abs(abs(c) - abs(truth)) <= q["abs_tol"] for c in cands)
    tol = q.get("rel_tol", 0.001) * max(abs(truth), 1e-9)
    return any(abs(c - truth) <= tol for c in cands)


def score_items(q: dict[str, Any], rows: list[tuple], answer: str) -> bool:
    text = answer.lower()
    prefix = q.get("match_prefix", "").lower()
    for (val, *_) in rows:
        needle = re.escape(f"{prefix}{str(val).lower()}").replace(r"\ ", r"\s*")
        if not re.search(rf"{needle}\b", text):
            return False
    return True


def judge(key: str, q: dict[str, Any], rows: list[tuple], answer: str) -> tuple[bool, str]:
    prompt = (
        "You grade answers from a civic-data analytics agent. Reply with JSON only: "
        '{"pass": true|false, "reason": "<one sentence>"}.\n\n'
        f"Question: {q['question']}\nRubric: {q['rubric']}\n"
        f"Ground-truth query result: {json.dumps(rows, default=str)}\n\nAgent answer:\n{answer[:6000]}"
    )
    # The judge model always reasons first; leave room for reasoning plus the verdict.
    body = json.dumps({
        "model": JUDGE_SLUG, "max_tokens": 4000, "reasoning": {"effort": "low"},
        "messages": [{"role": "user", "content": prompt}],
    }).encode()
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions", data=body,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            text = json.load(r)["choices"][0]["message"].get("content") or ""
        start = text.find("{")
        if start < 0:
            return False, f"JUDGE_ERROR: no JSON in {text[:80]!r}"
        # raw_decode reads the first JSON object and ignores anything after it
        # (the judge occasionally appends a second object or prose).
        verdict, _ = json.JSONDecoder().raw_decode(text[start:])
        return bool(verdict["pass"]), str(verdict.get("reason", ""))
    except (urllib.error.URLError, KeyError, ValueError, TimeoutError) as e:
        # A judge failure is recorded as a fail with the reason, never silently passed.
        return False, f"JUDGE_ERROR: {e}"


def score(key: str, q: dict[str, Any], rows: list[tuple], answer: str) -> tuple[bool, str]:
    if not answer:
        return False, "no final answer"
    t = q["answer_type"]
    if t in ("number", "percent"):
        truth = rows[0][0] if rows else None
        if truth is None:
            return False, "truth is NULL"
        return score_numeric(q, float(truth), answer), f"truth={float(truth):.4g}"
    if t == "items":
        return score_items(q, rows, answer), "truth=" + ", ".join(str(r[0]) for r in rows)
    if t == "judge":
        return judge(key, q, rows, answer)
    return False, f"unknown answer_type {t}"


# ------------------------------------------------------------------ main
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default=str(Path.home() / "oxygen-eval"))
    ap.add_argument("--models", nargs="*", help="model names from models.yaml")
    ap.add_argument("--pilot", action="store_true", help="only models marked pilot: true")
    ap.add_argument("--tiers", nargs="*", choices=["simple", "medium", "hard"])
    ap.add_argument("--questions", nargs="*", help="question ids")
    ap.add_argument("--reps", type=int, help="override repeats per question")
    ap.add_argument("--budget", type=float, default=25.0, help="stop when run spend (USD) exceeds this")
    ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--truths-only", action="store_true")
    args = ap.parse_args()

    project = Path(args.project).expanduser()
    if project.resolve() == (Path.home() / "oxygen-mvp").resolve():
        sys.exit("refusing to run against the production checkout; use the eval copy")
    cfg = load_yaml(EVAL_DIR / "models.yaml")
    questions = load_yaml(EVAL_DIR / "questions.yaml")["questions"]
    if args.tiers:
        questions = [q for q in questions if q["tier"] in args.tiers]
    if args.questions:
        questions = [q for q in questions if q["id"] in args.questions]

    truths, truth_errors = compute_truths(project / "data" / "somerville.duckdb", questions)
    if args.truths_only:
        for q in questions:
            result = truths.get(q["id"], f"TRUTH_SQL ERROR: {truth_errors.get(q['id'])}")
            print(f"{q['id']} [{q['tier']}] {q['question']}\n    -> {result}")
        return 1 if truth_errors else 0
    if truth_errors:
        sys.exit("truth_sql errors, fix before running models: " + json.dumps(truth_errors))

    key = os.environ.get(cfg["key_var"])
    if not key:
        sys.exit(f"{cfg['key_var']} not set")
    models = cfg["models"]
    if args.pilot:
        models = [m for m in models if m.get("pilot")]
    if args.models:
        models = [m for m in models if m["name"] in args.models]
    if not models or not questions:
        sys.exit("nothing to run")

    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = project / "evals" / "results" / run_id
    (out_dir / "transcripts").mkdir(parents=True, exist_ok=True)
    start_usage = openrouter_usage(key)
    rows_out: list[dict[str, Any]] = []
    model_cost: dict[str, float | None] = {}
    stopped = ""

    for m in models:
        agent_rel = ensure_model(project, cfg, m)
        reps = args.reps or m.get("reps", 1)
        before = openrouter_usage(key)
        for q in questions:
            for rep in range(1, reps + 1):
                transcript, code, secs = ask(project, agent_rel, q["question"], args.timeout)
                (out_dir / "transcripts" / f"{m['name']}__{q['id']}__{rep}.txt").write_text(transcript)
                answer = final_answer(transcript)
                ok, detail = score(key, q, truths[q["id"]], answer)
                rows_out.append({
                    "run_id": run_id, "model": m["name"], "slug": m["slug"], "qid": q["id"],
                    "tier": q["tier"], "rep": rep, "correct": int(ok), "exit_code": code,
                    "seconds": round(secs, 1), "detail": detail,
                    "answer": answer.replace("\n", " ")[:500],
                })
                print(f"{m['name']:18s} {q['id']} r{rep} {'PASS' if ok else 'FAIL'} {secs:5.1f}s  {detail[:80]}", flush=True)
            now = openrouter_usage(key)
            if start_usage is not None and now is not None and now - start_usage > args.budget:
                stopped = f"budget ${args.budget} exceeded after {m['name']} {q['id']}"
                break
        after = openrouter_usage(key)
        model_cost[m["name"]] = (after - before) if (before is not None and after is not None) else None
        if stopped:
            break

    if not rows_out:
        sys.exit("no results recorded")
    with (out_dir / "results.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows_out[0].keys()))
        w.writeheader()
        w.writerows(rows_out)

    lines = [f"# Eval run {run_id}", "", f"Questions: {len(questions)} | snapshot: {project / 'data' / 'somerville.duckdb'}", ""]
    if stopped:
        lines += [f"**Stopped early:** {stopped}", ""]
    lines += ["| model | simple | medium | hard | overall | spend $ | $ per correct |", "|---|---|---|---|---|---|---|"]
    for m in models:
        mr = [r for r in rows_out if r["model"] == m["name"]]
        if not mr:
            continue

        def acc(tier: str | None) -> str:
            sub = [r for r in mr if tier is None or r["tier"] == tier]
            return f"{sum(r['correct'] for r in sub)}/{len(sub)}" if sub else "-"

        cost = model_cost.get(m["name"])
        correct = sum(r["correct"] for r in mr)
        per = f"{cost / correct:.4f}" if cost is not None and correct else "-"
        spend = "-" if cost is None else f"{cost:.3f}"
        lines.append(f"| {m['name']} | {acc('simple')} | {acc('medium')} | {acc('hard')} | {acc(None)} | {spend} | {per} |")
    end_usage = openrouter_usage(key)
    total = (end_usage - start_usage) if (end_usage is not None and start_usage is not None) else math.nan
    lines += ["", f"Total run spend (incl. judge calls): ${total:.3f}"]
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nresults: {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
