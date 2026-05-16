"""
02_filter_icp.py — Apply ICP filter to raw Apify output.

What it does:
- Loads data/01_raw_apify.json
- Dedups by GBP URL (multiple search queries return same place)
- Filters out chains (blocklist)
- Filters out categories that aren't med spas (hair salons, etc.)
- Enforces MIN_REVIEW_COUNT and MIN_STAR_RATING
- Splits into "primary targets" (full ICP match) and "competitor pool" (chains + adjacent spas for competitor matching)
- Saves to data/02_filtered_icp.json

Run:
    python 02_filter_icp.py
"""

import json
import sys
from typing import Dict, List, Tuple

from config import (
    CHAIN_BLOCKLIST,
    KEEP_CATEGORIES,
    DROP_CATEGORIES,
    MIN_REVIEW_COUNT,
    MIN_STAR_RATING,
    RAW_APIFY_JSON,
    FILTERED_JSON,
)


def normalize_name(name: str) -> str:
    return (name or "").lower().strip()


def is_chain(place: Dict) -> bool:
    name = normalize_name(place.get("title", ""))
    return any(chain in name for chain in CHAIN_BLOCKLIST)


def has_dropped_category(place: Dict) -> bool:
    """Check if any of the place's categories is in DROP_CATEGORIES."""
    cats = [normalize_name(c) for c in place.get("categories", [])]
    cats.append(normalize_name(place.get("categoryName", "")))
    return any(d in cat for cat in cats for d in DROP_CATEGORIES)


def has_kept_category(place: Dict) -> bool:
    """Check if any of the place's categories is in KEEP_CATEGORIES."""
    cats = [normalize_name(c) for c in place.get("categories", [])]
    cats.append(normalize_name(place.get("categoryName", "")))
    return any(k in cat for cat in cats for k in KEEP_CATEGORIES)


def passes_review_floor(place: Dict) -> bool:
    count = place.get("reviewsCount") or 0
    rating = place.get("totalScore") or 0
    return count >= MIN_REVIEW_COUNT and rating >= MIN_STAR_RATING


def main():
    with open(RAW_APIFY_JSON) as f:
        raw = json.load(f)

    print(f"Loaded {len(raw)} raw items", file=sys.stderr)

    # Dedup by GBP URL (cid) — multiple search queries return same place
    seen = set()
    deduped = []
    for place in raw:
        cid = place.get("placeId") or place.get("url", "")
        if cid and cid not in seen:
            seen.add(cid)
            deduped.append(place)
    print(f"After dedup: {len(deduped)} unique places", file=sys.stderr)

    primary_targets = []
    competitor_pool = []
    dropped = {"chain": 0, "category": 0, "low_reviews": 0, "no_categories": 0}

    for place in deduped:
        # Drop hard non-med-spa categories
        if has_dropped_category(place):
            dropped["category"] += 1
            continue

        # Must have at least one med-spa-ish category
        if not has_kept_category(place):
            dropped["no_categories"] += 1
            continue

        if is_chain(place):
            # Chains go in competitor pool but not primary targets
            competitor_pool.append(place)
            dropped["chain"] += 1
            continue

        if not passes_review_floor(place):
            # Low-review spas go in competitor pool but not primary targets
            competitor_pool.append(place)
            dropped["low_reviews"] += 1
            continue

        primary_targets.append(place)
        competitor_pool.append(place)  # primaries are also competitors of other primaries

    print(f"Primary targets (ICP-match): {len(primary_targets)}", file=sys.stderr)
    print(f"Competitor pool (all med spas including chains): {len(competitor_pool)}", file=sys.stderr)
    print(f"Dropped: {dropped}", file=sys.stderr)

    out = {
        "primary_targets": primary_targets,
        "competitor_pool": competitor_pool,
        "stats": {
            "raw": len(raw),
            "deduped": len(deduped),
            "primaries": len(primary_targets),
            "competitor_pool": len(competitor_pool),
            "dropped": dropped,
        },
    }

    with open(FILTERED_JSON, "w") as f:
        json.dump(out, f, indent=2)

    print(f"Saved filtered output to {FILTERED_JSON}", file=sys.stderr)
    print(f"Next step: python 03_assign_competitors.py", file=sys.stderr)


if __name__ == "__main__":
    main()
