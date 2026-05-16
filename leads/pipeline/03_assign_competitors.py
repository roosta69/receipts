"""
03_assign_competitors.py — For each primary target, find 3 nearest competitors.

What it does:
- Loads data/02_filtered_icp.json
- For each primary, computes haversine distance to every other place in the competitor pool
- Selects the 3 nearest within COMPETITOR_RADIUS_MILES with the highest review count
- Saves enriched primaries to data/03_with_competitors.json

Why this design:
- Apify already returned all med spas in the metro; we don't need a 2nd API call
- Nearest-3 ranked by review count gives the "biggest local rivals" — most useful for pitch

Run:
    python 03_assign_competitors.py
"""

import json
import math
import sys
from typing import Dict, List, Optional, Tuple

from config import (
    COMPETITOR_RADIUS_MILES,
    COMPETITORS_PER_PRIMARY,
    FILTERED_JSON,
    WITH_COMPETITORS_JSON,
)


def haversine_miles(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Distance in miles between two lat/lng points."""
    R = 3959  # Earth radius in miles
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def get_lat_lng(place: Dict) -> Optional[Tuple[float, float]]:
    loc = place.get("location") or {}
    lat = loc.get("lat") or place.get("lat")
    lng = loc.get("lng") or place.get("lng") or place.get("lon") or place.get("long")
    if lat is None or lng is None:
        return None
    return float(lat), float(lng)


def find_competitors(primary: Dict, pool: List[Dict], radius: float, n: int) -> List[Dict]:
    """Return up to n nearest competitors within radius, sorted by review count desc."""
    p_loc = get_lat_lng(primary)
    if p_loc is None:
        return []

    primary_id = primary.get("placeId") or primary.get("url")
    candidates = []

    for other in pool:
        if other is primary:
            continue
        other_id = other.get("placeId") or other.get("url")
        if other_id == primary_id:
            continue

        o_loc = get_lat_lng(other)
        if o_loc is None:
            continue

        dist = haversine_miles(p_loc[0], p_loc[1], o_loc[0], o_loc[1])
        if dist > radius:
            continue

        candidates.append((dist, other))

    # Sort by distance first (must be near), then break ties by review count
    candidates.sort(key=lambda x: (x[0], -(x[1].get("reviewsCount") or 0)))

    # Take top n by review count among the closest matches
    # Strategy: take 2× target by proximity, then re-rank by reviews, return top n
    closest = candidates[: n * 2]
    closest.sort(key=lambda x: -(x[1].get("reviewsCount") or 0))

    return [
        {
            "name": comp["title"],
            "review_count": comp.get("reviewsCount") or 0,
            "star_rating": comp.get("totalScore") or 0,
            "distance_miles": round(dist, 2),
            "gbp_url": comp.get("url"),
            "address": comp.get("address"),
        }
        for dist, comp in closest[:n]
    ]


def main():
    with open(FILTERED_JSON) as f:
        data = json.load(f)

    primaries = data["primary_targets"]
    pool = data["competitor_pool"]

    print(f"Assigning competitors for {len(primaries)} primaries...", file=sys.stderr)
    print(f"Competitor pool size: {len(pool)}", file=sys.stderr)
    print(f"Radius: {COMPETITOR_RADIUS_MILES}mi, top {COMPETITORS_PER_PRIMARY} per primary", file=sys.stderr)

    enriched = []
    no_loc = 0
    no_comps = 0

    for primary in primaries:
        if get_lat_lng(primary) is None:
            no_loc += 1
            continue

        comps = find_competitors(primary, pool, COMPETITOR_RADIUS_MILES, COMPETITORS_PER_PRIMARY)
        if not comps:
            no_comps += 1

        primary["_competitors"] = comps
        enriched.append(primary)

    print(f"Enriched: {len(enriched)}", file=sys.stderr)
    print(f"Skipped (no lat/lng): {no_loc}", file=sys.stderr)
    print(f"Found zero competitors within radius: {no_comps}", file=sys.stderr)

    with open(WITH_COMPETITORS_JSON, "w") as f:
        json.dump(enriched, f, indent=2)

    print(f"Saved to {WITH_COMPETITORS_JSON}", file=sys.stderr)
    print(f"Next step: python 04_enrich_emails.py", file=sys.stderr)


if __name__ == "__main__":
    main()
