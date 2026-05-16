"""
05_export_csv.py — Export final master-list.csv + competitors.csv.

Schema (master-list.csv):
    name,city,state,zip,phone,website,instagram,email,email_source,
    google_review_count,google_star_rating,address,gbp_url,categories,
    top_competitor_1_name,top_competitor_1_reviews,top_competitor_1_stars,top_competitor_1_distance,
    top_competitor_2_name,top_competitor_2_reviews,top_competitor_2_stars,top_competitor_2_distance,
    top_competitor_3_name,top_competitor_3_reviews,top_competitor_3_stars,top_competitor_3_distance,
    notes,call_status,call_attempts,last_attempted

Schema (competitors.csv):
    primary_spa_name,primary_spa_city,competitor_rank,competitor_name,
    competitor_review_count,competitor_star_rating,competitor_distance_miles,competitor_gbp_url

Run:
    python 05_export_csv.py
"""

import csv
import json
import os
import re
import sys
from typing import Dict, Optional

from config import WITH_EMAILS_JSON, WITH_COMPETITORS_JSON, MASTER_CSV, COMPETITORS_CSV


def extract_instagram(place: Dict) -> Optional[str]:
    """Try to find an Instagram handle from website or social profile fields."""
    # Apify sometimes returns a 'instagrams' list on the place
    igs = place.get("instagrams") or place.get("socialProfiles", {}).get("instagram")
    if igs:
        if isinstance(igs, list):
            return igs[0]
        if isinstance(igs, str):
            return igs

    # Fallback — none found
    return None


def safe_str(val) -> str:
    if val is None:
        return ""
    return str(val).strip()


def safe_int(val) -> int:
    try:
        return int(val) if val is not None else 0
    except (ValueError, TypeError):
        return 0


def safe_float(val) -> float:
    try:
        return float(val) if val is not None else 0.0
    except (ValueError, TypeError):
        return 0.0


def parse_city_state_zip(place: Dict) -> tuple:
    """Extract city/state/zip from address fields."""
    city = safe_str(place.get("city"))
    state = safe_str(place.get("state"))
    zip_code = safe_str(place.get("postalCode") or place.get("zip"))

    if city and state:
        return city, state, zip_code

    # Fallback: parse from address string
    address = safe_str(place.get("address"))
    m = re.search(r",\s*([^,]+),\s*([A-Z]{2})\s+(\d{5})", address)
    if m:
        return m.group(1).strip(), m.group(2), m.group(3)
    return city, state, zip_code


def write_master_csv(primaries):
    fieldnames = [
        "name", "city", "state", "zip",
        "phone", "website", "instagram", "email", "email_source",
        "google_review_count", "google_star_rating",
        "address", "gbp_url", "categories",
        "top_competitor_1_name", "top_competitor_1_reviews", "top_competitor_1_stars", "top_competitor_1_distance",
        "top_competitor_2_name", "top_competitor_2_reviews", "top_competitor_2_stars", "top_competitor_2_distance",
        "top_competitor_3_name", "top_competitor_3_reviews", "top_competitor_3_stars", "top_competitor_3_distance",
        "notes", "call_status", "call_attempts", "last_attempted",
    ]

    with open(MASTER_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()

        for place in primaries:
            city, state, zip_code = parse_city_state_zip(place)
            comps = place.get("_competitors") or []
            row = {
                "name": safe_str(place.get("title")),
                "city": city,
                "state": state,
                "zip": zip_code,
                "phone": safe_str(place.get("phone") or place.get("phoneNumber")),
                "website": safe_str(place.get("website")),
                "instagram": safe_str(extract_instagram(place)),
                "email": safe_str(place.get("_email")),
                "email_source": safe_str(place.get("_email_source")),
                "google_review_count": safe_int(place.get("reviewsCount")),
                "google_star_rating": safe_float(place.get("totalScore")),
                "address": safe_str(place.get("address")),
                "gbp_url": safe_str(place.get("url")),
                "categories": "; ".join(place.get("categories") or []),
                "notes": "",
                "call_status": "not_called",
                "call_attempts": 0,
                "last_attempted": "",
            }
            for i in range(3):
                comp = comps[i] if i < len(comps) else {}
                row[f"top_competitor_{i+1}_name"] = safe_str(comp.get("name"))
                row[f"top_competitor_{i+1}_reviews"] = safe_int(comp.get("review_count"))
                row[f"top_competitor_{i+1}_stars"] = safe_float(comp.get("star_rating"))
                row[f"top_competitor_{i+1}_distance"] = safe_float(comp.get("distance_miles"))

            writer.writerow(row)

    print(f"Wrote {len(primaries)} rows to {MASTER_CSV}", file=sys.stderr)


def write_competitors_csv(primaries):
    fieldnames = [
        "primary_spa_name", "primary_spa_city", "competitor_rank",
        "competitor_name", "competitor_review_count", "competitor_star_rating",
        "competitor_distance_miles", "competitor_gbp_url",
    ]

    row_count = 0
    with open(COMPETITORS_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()

        for place in primaries:
            primary_name = safe_str(place.get("title"))
            city, _, _ = parse_city_state_zip(place)
            for rank, comp in enumerate(place.get("_competitors") or [], start=1):
                writer.writerow({
                    "primary_spa_name": primary_name,
                    "primary_spa_city": city,
                    "competitor_rank": rank,
                    "competitor_name": safe_str(comp.get("name")),
                    "competitor_review_count": safe_int(comp.get("review_count")),
                    "competitor_star_rating": safe_float(comp.get("star_rating")),
                    "competitor_distance_miles": safe_float(comp.get("distance_miles")),
                    "competitor_gbp_url": safe_str(comp.get("gbp_url")),
                })
                row_count += 1

    print(f"Wrote {row_count} competitor rows to {COMPETITORS_CSV}", file=sys.stderr)


def main():
    # Prefer email-enriched output (step 04), but fall back gracefully
    # to step 03 output if email enrichment was skipped.
    if os.path.exists(WITH_EMAILS_JSON):
        source = WITH_EMAILS_JSON
        print(f"Reading {WITH_EMAILS_JSON} (with emails)", file=sys.stderr)
    elif os.path.exists(WITH_COMPETITORS_JSON):
        source = WITH_COMPETITORS_JSON
        print(f"Reading {WITH_COMPETITORS_JSON} (email column will be blank)", file=sys.stderr)
    else:
        print(f"ERROR: No input found. Run 03_assign_competitors.py first.", file=sys.stderr)
        sys.exit(1)

    with open(source) as f:
        primaries = json.load(f)

    write_master_csv(primaries)
    write_competitors_csv(primaries)

    print(f"\nDone. Import to Google Sheets:", file=sys.stderr)
    print(f"  1. Open new Google Sheet", file=sys.stderr)
    print(f"  2. File > Import > Upload {MASTER_CSV} (separate sheet)", file=sys.stderr)
    print(f"  3. File > Import > Upload {COMPETITORS_CSV} (separate sheet)", file=sys.stderr)


if __name__ == "__main__":
    main()
