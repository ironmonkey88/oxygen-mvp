import dlt
import requests
import sys
from typing import Iterator

SODA_BASE = "https://data.somervillema.gov/resource/4pyi-uqq6.json"
PAGE_SIZE = 50_000
RAW_PATH = "file:///home/ubuntu/oxygen-mvp/data/raw"

ALL_COLUMNS = ",".join([
    "id", "classification", "category", "type", "origin_of_request",
    "most_recent_status_date", "most_recent_status", "date_created",
    "block_code", "ward",
    "accuracy", "courtesy", "ease", "overallexperience",
    "emergency_readiness_and_response_planning",
    "green_space_care_and_maintenance",
    "infrastructure_maintenance_and_repairs",
    "noise_and_activity_disturbances",
    "reliable_service_delivery",
    "navigating_city_services_and_policies",
    "public_space_cleanliness_and_environmental_health",
    "voting_and_election_information",
])


def fetch_year(year: int) -> Iterator[dict]:
    """Paginate through all 311 records for a given year via SODA API."""
    offset = 0
    # Use space separator (matches stored format) and >= / < to avoid boundary gaps
    where = f"date_created >= '{year}-01-01 00:00:00' AND date_created < '{year + 1}-01-01 00:00:00'"
    while True:
        params = {
            "$select": ALL_COLUMNS,
            "$limit": PAGE_SIZE,
            "$offset": offset,
            "$where": where,
            "$order": "id ASC",
        }
        resp = requests.get(SODA_BASE, params=params, timeout=60)
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        print(f"  {year} offset={offset}: fetched {len(batch)} rows")
        yield from batch
        if len(batch) < PAGE_SIZE:
            break
        offset += PAGE_SIZE


def run_year(year: int) -> None:
    @dlt.resource(
        name=f"requests_{year}",
        primary_key="id",
        write_disposition="replace",
    )
    def _resource():
        yield from fetch_year(year)

    pipeline = dlt.pipeline(
        pipeline_name=f"somerville_311_{year}",
        destination=dlt.destinations.filesystem(bucket_url=RAW_PATH),
        dataset_name="somerville_311",
    )

    info = pipeline.run(_resource(), loader_file_format="parquet")
    completed = [j for j in info.load_packages[0].jobs["completed_jobs"] if "parquet" in j.file_path]
    print(f"  {year}: {len(completed)} parquet file(s) written")


if __name__ == "__main__":
    years = [int(y) for y in sys.argv[1:]] if len(sys.argv) > 1 else list(range(2015, 2027))
    for year in sorted(years):
        print(f"\n--- Loading {year} ---")
        run_year(year)
