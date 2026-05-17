"""
round2_scrape.py — Self-contained second-pass Apify scrape for new states.

Targets 25 cities across CA, NV, CO, WA, UT, NC, IL, VA — all states NOT
covered in round 1. Independent of config.py to avoid stomping the round 1
state. Outputs to round2-specific files; merge later.

Expected: ~25 cities × 3 queries × 30 results = ~2,250 raw → ~500-700
ICP-fit primaries (rounding round1's 64% conversion rate).

Cost: ~$5-8 of Apify credit.

Run:
    export APIFY_TOKEN=...
    python3 round2_scrape.py
"""

import json
import math
import os
import sys
from typing import Dict, List

try:
    from apify_client import ApifyClient
except ImportError:
    print("Run: pip install -r requirements.txt", file=sys.stderr)
    sys.exit(1)


# -- Round 2 target cities (NEW states only) ---------------------------------

ROUND2_METROS = [
    # California (the biggest unaddressed market, NP full-practice from 2026)
    ("Los Angeles", "CA"),
    ("Beverly Hills", "CA"),
    ("Santa Monica", "CA"),
    ("Pasadena", "CA"),
    ("Newport Beach", "CA"),
    ("Irvine", "CA"),
    ("San Diego", "CA"),
    ("La Jolla", "CA"),

    # Nevada
    ("Las Vegas", "NV"),
    ("Henderson", "NV"),
    ("Reno", "NV"),

    # Colorado
    ("Denver", "CO"),
    ("Boulder", "CO"),
    ("Highlands Ranch", "CO"),

    # Washington
    ("Seattle", "WA"),
    ("Bellevue", "WA"),
    ("Kirkland", "WA"),

    # Utah
    ("Salt Lake City", "UT"),
    ("Park City", "UT"),

    # North Carolina
    ("Charlotte", "NC"),
    ("Raleigh", "NC"),

    # Illinois
    ("Chicago", "IL"),
    ("Naperville", "IL"),

    # Virginia (DC metro)
    ("Arlington", "VA"),
    ("Reston", "VA"),
]

SEARCH_QUERIES = [
    "med spa {city} {state}",
    "medical aesthetics {city} {state}",
    "botox {city} {state}",
]

MAX_RESULTS_PER_QUERY = 30
ACTOR_ID = "compass/crawler-google-places"

# Output paths
PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(PIPELINE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
ROUND2_RAW_JSON = os.path.join(DATA_DIR, "round2_raw_apify.json")


def main():
    token = os.environ.get("APIFY_TOKEN")
    if not token:
        print("ERROR: APIFY_TOKEN not set", file=sys.stderr)
        sys.exit(1)

    queries = []
    for city, state in ROUND2_METROS:
        for tmpl in SEARCH_QUERIES:
            queries.append(tmpl.format(city=city, state=state))

    print(f"Round 2: {len(ROUND2_METROS)} cities × {len(SEARCH_QUERIES)} queries = {len(queries)} searches", file=sys.stderr)
    print(f"Max results per search: {MAX_RESULTS_PER_QUERY}", file=sys.stderr)
    print(f"Expected raw output: ~{len(queries) * MAX_RESULTS_PER_QUERY}", file=sys.stderr)
    print(f"Expected cost: ~${len(queries) * MAX_RESULTS_PER_QUERY * 0.003:.2f}", file=sys.stderr)
    print(file=sys.stderr)

    client = ApifyClient(token)
    run_input = {
        "searchStringsArray": queries,
        "maxCrawledPlacesPerSearch": MAX_RESULTS_PER_QUERY,
        "language": "en",
        "countryCode": "us",
        "includeImages": False,
        "scrapeReviewsPersonalData": False,
        "maxReviews": 0,
        "scrapeImageAuthors": False,
    }

    print("Starting Apify run...", file=sys.stderr)
    run = client.actor(ACTOR_ID).call(run_input=run_input)
    print(f"Run ID: {run['id']}", file=sys.stderr)
    print(f"Dataset ID: {run['defaultDatasetId']}", file=sys.stderr)

    items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
    print(f"\nCollected {len(items)} round 2 raw items", file=sys.stderr)

    with open(ROUND2_RAW_JSON, "w") as f:
        json.dump(items, f, indent=2)

    print(f"Saved to {ROUND2_RAW_JSON}", file=sys.stderr)
    print(f"\nNext: python3 round2_process.py", file=sys.stderr)


if __name__ == "__main__":
    main()
