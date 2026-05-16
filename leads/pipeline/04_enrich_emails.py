"""
04_enrich_emails.py — Find email addresses for each primary target.

Two-stage enrichment:
  Stage A — scrape spa's own contact page for `mailto:` links + email regex (free)
  Stage B — fallback to Hunter.io domain search (paid, optional)

Stage A typically hits ~60-70% of spas (the ones that publish an email).
Stage B fills in ~15-20% more.

Run:
    # Without Hunter (only Stage A):
    python 04_enrich_emails.py

    # With Hunter (Stages A + B):
    export HUNTER_API_KEY=your_key_here
    python 04_enrich_emails.py
"""

import json
import os
import re
import sys
import time
from typing import Dict, Optional
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

# Skip these generic emails when scraping contact pages
GENERIC_EMAILS_TO_DEPRIORITIZE = [
    "noreply", "no-reply", "donotreply", "support@wix",
    "wordpress", "squarespace", "example.com",
]


def get_domain(website: str) -> Optional[str]:
    if not website:
        return None
    try:
        netloc = urlparse(website).netloc
        return netloc.lower().lstrip("www.")
    except Exception:
        return None


def scrape_contact_page(website: str, timeout: int = 8) -> Optional[str]:
    """Try to extract an email from the spa's contact page or homepage."""
    if not website:
        return None

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                     "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    }

    # Try homepage + common contact paths
    paths_to_try = ["", "/contact", "/contact-us", "/about", "/about-us"]
    candidates = []

    for path in paths_to_try:
        url = website.rstrip("/") + path
        try:
            r = requests.get(url, headers=headers, timeout=timeout)
            if r.status_code != 200:
                continue

            soup = BeautifulSoup(r.text, "html.parser")

            # Look for mailto: links first (most reliable)
            for link in soup.find_all("a", href=True):
                if link["href"].startswith("mailto:"):
                    email = link["href"].replace("mailto:", "").split("?")[0].strip()
                    if "@" in email:
                        candidates.append(email)

            # Then regex scan
            for match in EMAIL_REGEX.findall(r.text):
                candidates.append(match)

            if candidates:
                break  # Got something, stop here

        except Exception:
            continue

    # Deduplicate, deprioritize generic, prefer same-domain
    domain = get_domain(website)
    candidates = list(set(candidates))

    # Filter out junk
    filtered = []
    for email in candidates:
        lower = email.lower()
        if any(g in lower for g in GENERIC_EMAILS_TO_DEPRIORITIZE):
            continue
        if "." not in email.split("@")[-1]:
            continue
        filtered.append(email)

    if not filtered:
        return None

    # Prefer same-domain emails
    if domain:
        same_domain = [e for e in filtered if domain in e.lower()]
        if same_domain:
            return same_domain[0]

    return filtered[0]


def hunter_domain_search(domain: str, api_key: str) -> Optional[str]:
    """Use Hunter.io to find emails on a domain."""
    url = "https://api.hunter.io/v2/domain-search"
    params = {"domain": domain, "api_key": api_key, "limit": 5}
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        emails = data.get("data", {}).get("emails", [])
        if not emails:
            return None

        # Prefer "owner" / "ceo" / generic info@
        for priority_keyword in ["owner", "ceo", "founder", "info", "hello", "contact"]:
            for e in emails:
                value = e.get("value", "")
                position = (e.get("position") or "").lower()
                if priority_keyword in value.lower() or priority_keyword in position:
                    return value

        return emails[0].get("value")
    except Exception as exc:
        print(f"  Hunter error for {domain}: {exc}", file=sys.stderr)
        return None


def main():
    with open(WITH_COMPETITORS_JSON) as f:
        primaries = json.load(f)

    hunter_key = os.environ.get("HUNTER_API_KEY")
    use_hunter = bool(hunter_key)

    print(f"Enriching emails for {len(primaries)} primaries", file=sys.stderr)
    print(f"Hunter.io: {'ENABLED' if use_hunter else 'DISABLED (set HUNTER_API_KEY to enable)'}", file=sys.stderr)

    stage_a_hits = 0
    stage_b_hits = 0

    for i, primary in enumerate(primaries):
        if i % 50 == 0:
            print(f"  Progress: {i}/{len(primaries)}", file=sys.stderr)

        website = primary.get("website") or ""
        primary["_email"] = None
        primary["_email_source"] = None

        # Stage A: scrape contact page
        if website:
            email = scrape_contact_page(website)
            if email:
                primary["_email"] = email
                primary["_email_source"] = "contact_page"
                stage_a_hits += 1
                continue

        # Stage B: Hunter.io fallback
        if use_hunter and website:
            domain = get_domain(website)
            if domain:
                email = hunter_domain_search(domain, hunter_key)
                if email:
                    primary["_email"] = email
                    primary["_email_source"] = "hunter"
                    stage_b_hits += 1
                    time.sleep(0.5)  # Rate-limit ourselves a bit

    total_hits = stage_a_hits + stage_b_hits
    rate = (total_hits / len(primaries)) * 100 if primaries else 0
    print(f"\nResults:", file=sys.stderr)
    print(f"  Stage A (contact page): {stage_a_hits}", file=sys.stderr)
    print(f"  Stage B (Hunter.io):    {stage_b_hits}", file=sys.stderr)
    print(f"  Total found:            {total_hits} ({rate:.1f}%)", file=sys.stderr)

    with open(WITH_EMAILS_JSON, "w") as f:
        json.dump(primaries, f, indent=2)

    print(f"Saved to {WITH_EMAILS_JSON}", file=sys.stderr)
    print(f"Next step: python 05_export_csv.py", file=sys.stderr)


if __name__ == "__main__":
    main()
