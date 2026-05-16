"""
04_enrich_emails_fast.py — Concurrent email enrichment (10x faster than 04_enrich_emails.py).

Same logic as 04_enrich_emails.py but uses ThreadPoolExecutor with 10 workers.
~15-25 min for 764 spas instead of ~2 hours.

Stage A: scrape contact page (free, ~60-70% hit rate)
Stage B: Hunter.io fallback (optional, +15-20%, requires HUNTER_API_KEY)

Run:
    python 04_enrich_emails_fast.py
    # optional: export HUNTER_API_KEY=...
"""

import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Optional, Tuple
from urllib.parse import urlparse

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Missing dependency. Run: pip install -r requirements.txt", file=sys.stderr)
    sys.exit(1)

from config import WITH_COMPETITORS_JSON, WITH_EMAILS_JSON


EMAIL_REGEX = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
)

GENERIC_EMAILS_TO_DEPRIORITIZE = [
    "noreply", "no-reply", "donotreply", "support@wix",
    "wordpress", "squarespace", "example.com", "godaddy",
    "sentry", "react", "@2x", "@3x",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
}

MAX_WORKERS = 10
REQUEST_TIMEOUT = 6


def get_domain(website: str) -> Optional[str]:
    if not website:
        return None
    try:
        netloc = urlparse(website).netloc
        return netloc.lower().lstrip("www.")
    except Exception:
        return None


def scrape_contact_page(website: str) -> Optional[str]:
    if not website:
        return None

    paths_to_try = ["", "/contact", "/contact-us", "/about", "/about-us"]
    candidates = []

    for path in paths_to_try:
        url = website.rstrip("/") + path
        try:
            r = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            if r.status_code != 200:
                continue

            soup = BeautifulSoup(r.text, "html.parser")

            for link in soup.find_all("a", href=True):
                if link["href"].startswith("mailto:"):
                    email = link["href"].replace("mailto:", "").split("?")[0].strip()
                    if "@" in email:
                        candidates.append(email)

            for match in EMAIL_REGEX.findall(r.text):
                candidates.append(match)

            if candidates:
                break

        except Exception:
            continue

    domain = get_domain(website)
    candidates = list(set(candidates))

    filtered = []
    for email in candidates:
        lower = email.lower()
        if any(g in lower for g in GENERIC_EMAILS_TO_DEPRIORITIZE):
            continue
        if "." not in email.split("@")[-1]:
            continue
        # Strip image URL artifacts that look like emails
        if any(suffix in lower for suffix in [".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"]):
            continue
        filtered.append(email)

    if not filtered:
        return None

    if domain:
        same_domain = [e for e in filtered if domain.split(".")[0] in e.lower()]
        if same_domain:
            return same_domain[0]

    return filtered[0]


def hunter_domain_search(domain: str, api_key: str) -> Optional[str]:
    url = "https://api.hunter.io/v2/domain-search"
    params = {"domain": domain, "api_key": api_key, "limit": 5}
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        emails = data.get("data", {}).get("emails", [])
        if not emails:
            return None

        for priority_keyword in ["owner", "ceo", "founder", "info", "hello", "contact"]:
            for e in emails:
                value = e.get("value", "")
                position = (e.get("position") or "").lower()
                if priority_keyword in value.lower() or priority_keyword in position:
                    return value

        return emails[0].get("value")
    except Exception:
        return None


def enrich_one(primary: Dict, hunter_key: Optional[str] = None) -> Tuple[Dict, str]:
    """Returns (enriched_primary, status) where status is 'stage_a', 'stage_b', or 'miss'."""
    primary["_email"] = None
    primary["_email_source"] = None
    website = primary.get("website") or ""

    if website:
        email = scrape_contact_page(website)
        if email:
            primary["_email"] = email
            primary["_email_source"] = "contact_page"
            return primary, "stage_a"

    if hunter_key and website:
        domain = get_domain(website)
        if domain:
            email = hunter_domain_search(domain, hunter_key)
            if email:
                primary["_email"] = email
                primary["_email_source"] = "hunter"
                return primary, "stage_b"

    return primary, "miss"


def main():
    with open(WITH_COMPETITORS_JSON) as f:
        primaries = json.load(f)

    hunter_key = os.environ.get("HUNTER_API_KEY")

    print(f"Enriching emails for {len(primaries)} primaries", file=sys.stderr)
    print(f"Concurrency: {MAX_WORKERS} workers", file=sys.stderr)
    print(f"Hunter.io: {'ENABLED' if hunter_key else 'DISABLED'}", file=sys.stderr)
    print(file=sys.stderr)

    stage_a = stage_b = miss = 0
    done = 0
    enriched = []
    start = time.time()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = {ex.submit(enrich_one, p, hunter_key): i for i, p in enumerate(primaries)}
        for future in as_completed(futures):
            try:
                primary, status = future.result()
            except Exception as exc:
                primary = primaries[futures[future]]
                primary["_email"] = None
                primary["_email_source"] = None
                status = "miss"

            enriched.append(primary)
            if status == "stage_a":
                stage_a += 1
            elif status == "stage_b":
                stage_b += 1
            else:
                miss += 1

            done += 1
            if done % 50 == 0:
                elapsed = time.time() - start
                rate = done / elapsed
                eta_min = (len(primaries) - done) / rate / 60
                print(
                    f"  {done:>4}/{len(primaries)} | "
                    f"Stage A: {stage_a} | Stage B: {stage_b} | Miss: {miss} | "
                    f"ETA: {eta_min:.1f} min",
                    file=sys.stderr,
                )

    total_hits = stage_a + stage_b
    rate = (total_hits / len(primaries)) * 100 if primaries else 0
    print(file=sys.stderr)
    print(f"Done in {(time.time() - start) / 60:.1f} min", file=sys.stderr)
    print(f"  Stage A (contact page): {stage_a}", file=sys.stderr)
    print(f"  Stage B (Hunter.io):    {stage_b}", file=sys.stderr)
    print(f"  Misses:                 {miss}", file=sys.stderr)
    print(f"  Total emails found:     {total_hits} ({rate:.1f}%)", file=sys.stderr)

    with open(WITH_EMAILS_JSON, "w") as f:
        json.dump(enriched, f, indent=2)

    print(f"\nSaved to {WITH_EMAILS_JSON}", file=sys.stderr)
    print(f"Next: python 05_export_csv.py", file=sys.stderr)


if __name__ == "__main__":
    main()
