"""
01_apify_scrape.py — Bulk scrape Google Maps for med spas via Apify.

What it does:
- Calls the Apify Google Maps Scraper actor (compass/crawler-google-places)
- Runs SEARCH_QUERIES_PER_METRO × TARGET_METROS searches
- Saves raw JSON output to data/01_raw_apify.json

Cost: ~$1.50 per 1000 results. With ~38 cities × 3 queries × 30 results = ~3,420 results.
Free tier ($5/mo platform credit) covers the whole run.

Run:
    export APIFY_TOKEN=your_token_here
    python 01_apify_scrape.py

Get token from: https://console.apify.com/account/integrations
"""

import os
import sys
import json
from typing import List, Dict

try:
    from apify_client import ApifyClient
except ImportError:
    print("Missing dependency. Run: pip install -r requirements.txt", file=sys.stderr)
    sys.exit(1)

from config import (
    TARGET_METROS,
    SEARCH_QUERIES_PER_METRO,
    MAX_RESULTS_PER_QUERY,
    APIFY_ACTOR_ID,
    RAW_APIFY_JSON,
)


def build_search_strings() -> List[str]:
    """Generate the full list of search queries to run."""
    queries = []
    for city, state in TARGET_METROS:
        for template in SEARCH_QUERIES_PER_METRO:
            queries.append(template.format(city=city, state=state))
    return queries


def run_apify(token: str, queries: List[str]) -> List[Dict]:
    """Execute the Apify actor and collect dataset items."""
    client = ApifyClient(token)

    run_input = {
        "searchStringsArray": queries,
        "maxCrawledPlacesPerSearch": MAX_RESULTS_PER_QUERY,
        "language": "en",
        "countryCode": "us",
        # Include basic + contact info, skip review text (expensive + not needed)
        "includeImages": False,
        "scrapeReviewsPersonalData": False,
        "maxReviews": 0,
        "scrapeImageAuthors": False,
        # Get phone, website, opening hours, categories
        "placeMinimumStars": "",  # No filter at this stage; we filter in step 2
    }

    print(f"Starting Apify run with {len(queries)} queries...", file=sys.stderr)
    print(f"Expected total results: ~{len(queries) * MAX_RESULTS_PER_QUERY}", file=sys.stderr)
    print(f"Expected cost: ~${len(queries) * MAX_RESULTS_PER_QUERY * 0.0015:.2f}", file=sys.stderr)

    run = client.actor(APIFY_ACTOR_ID).call(run_input=run_input)
    print(f"Run finished. Run ID: {run['id']}", file=sys.stderr)
    print(f"Dataset ID: {run['defaultDatasetId']}", file=sys.stderr)

    # Fetch dataset items
    items = []
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        items.append(item)

    print(f"Collected {len(items)} raw items", file=sys.stderr)
    return items


def main():
    token = os.environ.get("APIFY_TOKEN")
    if not token:
        print("ERROR: APIFY_TOKEN environment variable not set.", file=sys.stderr)
        print("Get your token at https://console.apify.com/account/integrations", file=sys.stderr)
        sys.exit(1)

    queries = build_search_strings()
    items = run_apify(token, queries)

    with open(RAW_APIFY_JSON, "w") as f:
        json.dump(items, f, indent=2)

    print(f"Saved {len(items)} raw items to {RAW_APIFY_JSON}", file=sys.stderr)
    print(f"Next step: python 02_filter_icp.py", file=sys.stderr)


if __name__ == "__main__":
    main()
