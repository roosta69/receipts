"""
enrich_master_emails.py — Backfill emails directly on master-list.csv.

Reads master-list.csv → for rows with empty email + has website → scrapes contact page
→ writes back. Concurrent (10 workers). Used after round 2 (or any append) to fill
emails on freshly-added rows without re-running the full pipeline.

Run:
    python3 enrich_master_emails.py
"""

import csv
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from importlib import import_module

# Reuse the fast enricher's scrape_contact_page
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
fast = import_module("04_enrich_emails_fast")

from config import MASTER_CSV

MAX_WORKERS = 10


def main():
    with open(MASTER_CSV) as f:
        rows = list(csv.DictReader(f))
    fieldnames = list(rows[0].keys())

    needs = [(i, r) for i, r in enumerate(rows) if not r.get("email") and r.get("website")]
    print(f"Total rows: {len(rows)}", file=sys.stderr)
    print(f"Rows needing enrichment: {len(needs)}", file=sys.stderr)
    print(f"Concurrency: {MAX_WORKERS} workers", file=sys.stderr)

    if not needs:
        print("Nothing to enrich.", file=sys.stderr)
        return

    start = time.time()
    found = 0
    done = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = {ex.submit(fast.scrape_contact_page, r["website"]): i for i, r in needs}
        for future in as_completed(futures):
            i = futures[future]
            try:
                email = future.result()
            except Exception:
                email = None
            if email:
                rows[i]["email"] = email
                rows[i]["email_source"] = "contact_page"
                found += 1
            done += 1
            if done % 50 == 0:
                elapsed = time.time() - start
                rate = done / elapsed
                eta_min = (len(needs) - done) / rate / 60
                print(f"  {done}/{len(needs)} | found: {found} | ETA: {eta_min:.1f} min", file=sys.stderr)

    elapsed_min = (time.time() - start) / 60
    print(f"\nDone in {elapsed_min:.1f} min. Found {found} new emails.", file=sys.stderr)

    with open(MASTER_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved updated {MASTER_CSV}", file=sys.stderr)


if __name__ == "__main__":
    main()
