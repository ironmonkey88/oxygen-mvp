-- dq_drift_fail_guardrail
--
-- Returns rows when any test in admin.fct_test_run has status='fail'
-- for the most recent run_id. A non-empty result fails the test, which
-- propagates to a non-zero `dbt test --select admin` exit, which run.sh
-- combines into the final exit code.
--
-- This is the seam that turns "fct_test_run captures a drift" into
-- "the pipeline run actually fails" -- required by STANDARDS.md sect.5.5
-- ("Pipeline returns non-zero exit code on test failure beyond
-- tolerance").

with latest_run as (
    select run_id
    from {{ ref('fct_test_run') }}
    group by run_id
    order by max(run_at) desc
    limit 1
)
select *
from {{ ref('fct_test_run') }} t
inner join latest_run lr on t.run_id = lr.run_id
where t.status = 'fail'
