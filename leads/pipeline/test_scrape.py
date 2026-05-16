"""
test_scrape.py — Quick validation of Apify pipeline.

Runs ~120 records over Scottsdale + Phoenix to confirm:
- Apify token works
- Actor returns expected schema
- Output is parseable

Cost: ~$0.18 (negligible). Run before the full 01_apify_scrape.py.

Run:
    export APIFY_TOKEN=your_token
    python test_scrape.py
"""

import json
import os
import sys

try:
    from apify_client import ApifyClient
except ImportError:
    print("Run: pip install -r requirements.txt", file=sys.stderr)
    sys.exit(1)


def main():
    token = os.environ.get("APIFY_TOKEN")
    if not token:
        print("ERROR: APIFY_TOKEN env var not set", file=sys.stderr)
        sys.exit(1)

    client = ApifyClient(token)

    run_input = {
        "searchStringsArray": [
            "med spa Scottsdale AZ",
            "med spa Phoenix AZ",
        ],
        "maxCrawledPlacesPerSearch": 30,
        "language": "en",
        "countryCode": "us",
        "includeImages": False,
        "scrapeReviewsPersonalData": False,
        "maxReviews": 0,
        "scrapeImageAuthors": False,
    }

    print("Starting test scrape (2 queries x 30 results = ~60 expected)...", file=sys.stderr)
    print("Cost: ~$0.09-0.18", file=sys.stderr)

    run = client.actor("compass/crawler-google-places").call(run_input=run_input)
    print(f"Run ID: {run['id']}", file=sys.stderr)
    print(f"Dataset ID: {run['defaultDatasetId']}", file=sys.stderr)

    items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
    print(f"\nCollected {len(items)} items", file=sys.stderr)

    if items:
        print(f"\nSample item keys: {list(items[0].keys())[:20]}", file=sys.stderr)
        print(f"\nFirst result:")
        first = items[0]
        print(json.dumps({
            "title": first.get("title"),
            "address": first.get("address"),
            "phoneNumber": first.get("phone") or first.get("phoneNumber"),
            "website": first.get("website"),
            "reviewsCount": first.get("reviewsCount"),
            "totalScore": first.get("totalScore"),
            "url": first.get("url"),
            "categories": first.get("categories"),
        }, indent=2))

    out_path = os.path.join(os.path.dirname(__file__), "data", "test_scrape_output.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(items, f, indent=2)
    print(f"\nSaved full output to {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
