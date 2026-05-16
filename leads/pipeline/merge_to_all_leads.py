"""
merge_to_all_leads.py — Combine master-list.csv (Apify) + 4 agent seed CSVs into all-leads.csv.

Dedup by (name lowercase, state lowercase). On collision, prefers the agent row
since it has owner_name + owner_credential the Apify rows don't.

Adds `source` column: 'agent_seed' | 'apify' | 'merged'.

Run:
    python merge_to_all_leads.py
"""

import csv
import os
import sys
from collections import OrderedDict

# Paths
LEADS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MASTER_CSV = os.path.join(LEADS_DIR, "master-list.csv")
ALL_LEADS_CSV = os.path.join(LEADS_DIR, "all-leads.csv")

AGENT_CSVS = [
    os.path.join(LEADS_DIR, "research-agent-seed-miami-tampa.csv"),
    os.path.join(LEADS_DIR, "research-agent-seed-phoenix-scottsdale.csv"),
    os.path.join(LEADS_DIR, "research-agent-seed-orlando-atlanta-nashville.csv"),
    os.path.join(LEADS_DIR, "research-agent-seed-austin-san-antonio.csv"),
]

# Master schema (unified output)
UNIFIED_HEADERS = [
    "source",
    "name", "city", "state", "zip",
    "owner_name", "owner_credential", "services",
    "phone", "website", "instagram", "email", "email_source",
    "google_review_count", "google_star_rating",
    "address", "gbp_url", "categories",
    "top_competitor_1_name", "top_competitor_1_reviews", "top_competitor_1_stars", "top_competitor_1_distance",
    "top_competitor_2_name", "top_competitor_2_reviews", "top_competitor_2_stars", "top_competitor_2_distance",
    "top_competitor_3_name", "top_competitor_3_reviews", "top_competitor_3_stars", "top_competitor_3_distance",
    "notes", "call_status", "call_attempts", "last_attempted",
]

# State normalization
STATE_CODE_TO_NAME = {
    "TX": "Texas", "FL": "Florida", "AZ": "Arizona",
    "GA": "Georgia", "TN": "Tennessee", "CA": "California",
    "NY": "New York", "MA": "Massachusetts", "CT": "Connecticut",
    "IL": "Illinois", "NC": "North Carolina", "SC": "South Carolina",
}
STATE_NAME_TO_CODE = {v: k for k, v in STATE_CODE_TO_NAME.items()}


def normalize_state(value):
    if not value:
        return ""
    v = value.strip()
    if v in STATE_CODE_TO_NAME:
        return STATE_CODE_TO_NAME[v]
    return v  # Already full name


def normalize_name(value):
    return (value or "").strip().lower()


def dedup_key(row):
    """Stable key for dedup: normalized name + normalized state."""
    return (normalize_name(row.get("name")), normalize_name(row.get("state")))


def load_agent_csv(path):
    """Load an agent-format CSV into list of unified-schema dicts."""
    if not os.path.exists(path):
        print(f"  Skipping missing file: {path}", file=sys.stderr)
        return []

    rows = []
    with open(path) as f:
        reader = csv.DictReader(f)
        for r in reader:
            unified = {h: "" for h in UNIFIED_HEADERS}
            unified["source"] = "agent_seed"
            unified["name"] = r.get("name", "").strip()
            unified["city"] = r.get("city", "").strip()
            unified["state"] = normalize_state(r.get("state", ""))
            unified["owner_name"] = r.get("owner_name", "").strip()
            unified["owner_credential"] = r.get("owner_credential", "").strip()
            unified["services"] = r.get("services", "").strip()
            unified["phone"] = r.get("phone", "").strip()
            unified["website"] = r.get("website", "").strip()
            unified["instagram"] = r.get("instagram_handle", "").strip()
            unified["email"] = r.get("email", "").strip()
            unified["email_source"] = "agent_research" if unified["email"] else ""
            unified["google_review_count"] = r.get("google_review_count", "").strip()
            unified["google_star_rating"] = r.get("google_star_rating", "").strip()
            unified["address"] = r.get("address", "").strip()
            unified["gbp_url"] = r.get("gbp_url", "").strip()
            unified["top_competitor_1_name"] = r.get("top_competitor_1_name", "").strip()
            unified["top_competitor_1_reviews"] = r.get("top_competitor_1_reviews", "").strip()
            unified["top_competitor_2_name"] = r.get("top_competitor_2_name", "").strip()
            unified["top_competitor_2_reviews"] = r.get("top_competitor_2_reviews", "").strip()
            unified["top_competitor_3_name"] = r.get("top_competitor_3_name", "").strip()
            unified["top_competitor_3_reviews"] = r.get("top_competitor_3_reviews", "").strip()
            unified["call_status"] = "not_called"
            unified["call_attempts"] = "0"
            rows.append(unified)
    return rows


def load_master_csv(path):
    """Load the Apify master-list.csv into unified-schema dicts."""
    if not os.path.exists(path):
        print(f"  Master CSV not found: {path}", file=sys.stderr)
        return []

    rows = []
    with open(path) as f:
        reader = csv.DictReader(f)
        for r in reader:
            unified = {h: r.get(h, "") for h in UNIFIED_HEADERS}
            unified["source"] = "apify"
            unified["state"] = normalize_state(r.get("state", ""))
            # owner_name/owner_credential/services don't exist in Apify output — leave blank
            rows.append(unified)
    return rows


def merge_rows(agent_rows, apify_rows):
    """Merge with agent rows winning on collision. Tracks source."""
    by_key = OrderedDict()

    # Agent rows go in first
    for row in agent_rows:
        k = dedup_key(row)
        if not k[0]:  # skip if no name
            continue
        by_key[k] = row

    # Apify rows: add if new, merge if exists
    duplicates = 0
    for row in apify_rows:
        k = dedup_key(row)
        if not k[0]:
            continue
        if k in by_key:
            existing = by_key[k]
            # Merge: agent wins on owner/services fields,
            # Apify fills phone/website/reviews if agent has empty
            for field in ["phone", "website", "google_review_count",
                          "google_star_rating", "address", "gbp_url",
                          "categories", "zip", "email"]:
                if not existing.get(field) and row.get(field):
                    existing[field] = row[field]
            # Apify competitor structure has stars + distance, agent doesn't
            for i in range(1, 4):
                for suffix in ["stars", "distance"]:
                    field = f"top_competitor_{i}_{suffix}"
                    if not existing.get(field) and row.get(field):
                        existing[field] = row[field]
            existing["source"] = "merged"
            duplicates += 1
        else:
            by_key[k] = row

    return list(by_key.values()), duplicates


def write_unified(rows, path):
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=UNIFIED_HEADERS, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for row in rows:
            writer.writerow({h: row.get(h, "") for h in UNIFIED_HEADERS})


def main():
    print("Loading agent seed CSVs...", file=sys.stderr)
    agent_rows = []
    for path in AGENT_CSVS:
        loaded = load_agent_csv(path)
        print(f"  {os.path.basename(path)}: {len(loaded)} rows", file=sys.stderr)
        agent_rows.extend(loaded)
    print(f"Total agent rows: {len(agent_rows)}", file=sys.stderr)

    print(f"\nLoading {os.path.basename(MASTER_CSV)}...", file=sys.stderr)
    apify_rows = load_master_csv(MASTER_CSV)
    print(f"Total Apify rows: {len(apify_rows)}", file=sys.stderr)

    print("\nMerging...", file=sys.stderr)
    unified, duplicates = merge_rows(agent_rows, apify_rows)
    print(f"Duplicates merged: {duplicates}", file=sys.stderr)
    print(f"Final unified row count: {len(unified)}", file=sys.stderr)

    # Source breakdown
    from collections import Counter
    sources = Counter(r["source"] for r in unified)
    print(f"Source breakdown: {dict(sources)}", file=sys.stderr)

    write_unified(unified, ALL_LEADS_CSV)
    print(f"\nWrote {len(unified)} rows to {ALL_LEADS_CSV}", file=sys.stderr)


if __name__ == "__main__":
    main()
