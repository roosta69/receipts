"""
04_enrich_websites.py — Combined website enrichment pass.

Fetches each spa's website + common About/Team pages ONCE, then extracts BOTH:
  - email (Stage A: contact-page scrape, Stage B: optional Hunter.io fallback)
  - owner_name + owner_credential (RN/NP/PA/MD/etc.)

Concurrent (10 workers). ~12-25 min for 1500 spas.

Why one combined script:
- Each spa needs ~5-15 sec of network time (the expensive part)
- Doing two separate passes doubled the total runtime AND doubled load on the spa's server
- Extracting both fields from the same fetched HTML is essentially free

Run:
    python3 04_enrich_websites.py
    # optional: export HUNTER_API_KEY=...     # adds Stage B email fallback
"""

import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Missing dependency. Run: pip install -r requirements.txt", file=sys.stderr)
    sys.exit(1)

from config import WITH_COMPETITORS_JSON, WITH_EMAILS_JSON


# =============================================================================
# Network + parsing config
# =============================================================================

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
}
REQUEST_TIMEOUT = 6
MAX_WORKERS = 10

# Pages we try to fetch per spa. Order matters — homepage first.
PAGES_TO_FETCH = [
    "", "/contact", "/contact-us", "/about", "/about-us",
    "/team", "/meet-the-team", "/our-team", "/staff",
    "/founders", "/who-we-are", "/meet-us",
]


# =============================================================================
# Email extraction
# =============================================================================

EMAIL_REGEX = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
)

GENERIC_EMAIL_DEPRIORITIZE = [
    "noreply", "no-reply", "donotreply", "support@wix",
    "wordpress", "squarespace", "example.com", "godaddy",
    "sentry", "react", "@2x", "@3x",
]


# =============================================================================
# Owner extraction
# =============================================================================

CREDENTIALS = [
    "MD", "DO", "DMD", "DDS", "NMD", "ND",
    "DNP", "FNP-C", "FNP-BC", "FNP", "NP-C", "NP-BC", "NP",
    "APRN", "ARNP", "AGPCNP-BC", "AGNP",
    "PA-C", "PA",
    "MSN", "BSN", "RN",
    "LE", "LME", "CRNA", "CANS", "CPSN",
]
CRED_RE = "|".join(re.escape(c) for c in CREDENTIALS)

# Pattern A: explicit "Owner Sarah Whelan" / "Founded by Sarah Whelan"
P_OWNER_NAME = re.compile(
    r'\b(?:Owner|Owner-Operator|Founder|Founded by|Owned by|Owner/Operator|Lead Injector|Medical Director|Practice Owner)\s*[:\-]?\s*'
    r'(?P<name>(?:Dr\.?\s+)?[A-Z][a-z\']{1,20}(?:\s+[A-Z]\.?)?(?:\s+[A-Z][a-z\'-]{1,20}){1,2})'
    r'(?:,\s*(?P<cred>' + CRED_RE + r'))?'
)

# Pattern B: "Sarah Whelan, RN" — name+credential
P_NAME_CRED = re.compile(
    rf'\b(?P<name>(?:Dr\.?\s+)?[A-Z][a-z\']{{1,20}}(?:\s+[A-Z]\.?)?(?:\s+[A-Z][a-z\'-]{{1,20}}){{1,2}})\s*,\s*(?P<cred>{CRED_RE})\b'
)

# Pattern C: "Dr. Sarah Connor" appearing multiple times = likely owner
P_DR_NAME = re.compile(
    r'\bDr\.?\s+(?P<name>[A-Z][a-z\']{1,20}(?:\s+[A-Z]\.?)?(?:\s+[A-Z][a-z\'-]{1,20}){1,2})'
)

# Common false positives — looks like a name but isn't
NOT_A_NAME = {
    "About Us", "Our Team", "Meet Us", "Beverly Hills", "South Beach",
    "South Carolina", "North Carolina", "South Tampa", "South Lamar",
    "North Miami", "Sandy Springs", "Coral Gables", "Paradise Valley",
    "Coconut Grove", "Park City", "Salt Lake", "Lake Mary", "Lake Forest",
    "Forest Hills", "Sea View", "Privacy Policy", "Terms Service",
    "Contact Us", "Read More", "Learn More", "Sign Up", "Log In",
    "New Patient", "Existing Patient", "Book Now", "Get Started",
    "Our Story", "The Team", "Cookie Policy", "All Rights",
    "Schedule Appointment", "Free Consultation", "Med Spa", "Medical Spa",
    "Wellness Center", "Beauty Clinic", "Aesthetic Center", "Skin Care",
    "Laser Treatment", "Hair Restoration", "Body Contouring", "Botox Treatment",
}


# =============================================================================
# Helpers
# =============================================================================

def get_domain(url: str) -> Optional[str]:
    if not url:
        return None
    try:
        return urlparse(url).netloc.lower().lstrip("www.")
    except Exception:
        return None


def normalize_url(url: str) -> Optional[str]:
    if not url:
        return None
    url = url.strip()
    if not url:
        return None
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url.rstrip("/")


# =============================================================================
# Fetch — single round-trip per spa, returns parsed soup + raw HTML per page
# =============================================================================

def fetch_pages(website: str) -> List[Dict]:
    """Fetch homepage + common About paths. Return list of dicts with soup + raw HTML + text."""
    base = normalize_url(website)
    if not base:
        return []
    chunks = []
    for path in PAGES_TO_FETCH:
        url = base + path
        try:
            r = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT,
                            allow_redirects=True)
            if r.status_code != 200:
                continue
            soup = BeautifulSoup(r.text, "html.parser")
            for tag in soup(["script", "style", "noscript", "svg"]):
                tag.decompose()
            chunks.append({
                "url": url,
                "html": r.text,
                "soup": soup,
                "text": soup.get_text(separator=" ", strip=True),
            })
        except Exception:
            continue
    return chunks


# =============================================================================
# Email extraction (from already-fetched chunks)
# =============================================================================

def extract_email(chunks: List[Dict], domain: Optional[str]) -> Optional[str]:
    candidates = []
    for chunk in chunks:
        # mailto: links (most reliable)
        for link in chunk["soup"].find_all("a", href=True):
            if link["href"].startswith("mailto:"):
                email = link["href"].replace("mailto:", "").split("?")[0].strip()
                if "@" in email:
                    candidates.append(email)
        # regex on full HTML
        for match in EMAIL_REGEX.findall(chunk["html"]):
            candidates.append(match)
        if candidates:
            break  # stop once we have something

    candidates = list(set(candidates))

    # Filter junk
    filtered = []
    for email in candidates:
        lower = email.lower()
        if any(g in lower for g in GENERIC_EMAIL_DEPRIORITIZE):
            continue
        if "." not in email.split("@")[-1]:
            continue
        if any(s in lower for s in [".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"]):
            continue
        filtered.append(email)

    if not filtered:
        return None

    # Prefer same-domain email
    if domain:
        same = [e for e in filtered if domain.split(".")[0] in e.lower()]
        if same:
            return same[0]

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


# =============================================================================
# Owner extraction (from already-fetched chunks)
# =============================================================================

def extract_owner(chunks: List[Dict]) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Returns (confidence, owner_name, owner_credential) — all None if no match."""
    if not chunks:
        return None, None, None

    full_text = " ".join(c["text"] for c in chunks)
    if not full_text:
        return None, None, None

    candidates = []

    # HIGH: explicit Owner/Founder + name
    for m in P_OWNER_NAME.finditer(full_text):
        name = m.group("name").strip()
        cred = (m.group("cred") or "").strip()
        if name in NOT_A_NAME or len(name.split()) < 2:
            continue
        candidates.append(("high", name, cred))

    # MED: name + credential
    for m in P_NAME_CRED.finditer(full_text):
        name = m.group("name").strip()
        cred = m.group("cred").strip()
        if name in NOT_A_NAME or len(name.split()) < 2:
            continue
        candidates.append(("med", name, cred))

    # MED: Dr. Name appearing 2+ times
    dr_names = {}
    for m in P_DR_NAME.finditer(full_text):
        name = m.group("name").strip()
        if name in NOT_A_NAME or len(name.split()) < 1:
            continue
        full = f"Dr. {name}"
        dr_names[full] = dr_names.get(full, 0) + 1
    for full, count in dr_names.items():
        if count >= 2:
            candidates.append(("med", full, "MD"))

    if not candidates:
        return None, None, None

    # Tally votes by confidence tier
    by_conf = {"high": [], "med": []}
    for conf, name, cred in candidates:
        by_conf[conf].append((name, cred))

    for conf in ["high", "med"]:
        if not by_conf[conf]:
            continue
        votes = {}
        for name, cred in by_conf[conf]:
            votes.setdefault(name, {"count": 0, "creds": []})
            votes[name]["count"] += 1
            if cred:
                votes[name]["creds"].append(cred)
        best_name = max(votes.keys(), key=lambda k: votes[k]["count"])
        creds = votes[best_name]["creds"]
        return conf, best_name, (creds[0] if creds else "")

    return None, None, None


# =============================================================================
# Per-spa worker
# =============================================================================

def enrich_one(primary: Dict, hunter_key: Optional[str] = None) -> Tuple[Dict, str]:
    """
    Fetches website once, extracts email + owner.
    Returns (enriched_primary, status_tag).
    """
    primary["_email"] = None
    primary["_email_source"] = None
    primary["_owner_name"] = None
    primary["_owner_credential"] = None
    primary["_owner_confidence"] = None

    website = primary.get("website") or ""
    if not website:
        return primary, "no_website"

    chunks = fetch_pages(website)

    # Always try Hunter for emails when chunks fail and key is available
    if not chunks:
        if hunter_key:
            domain = get_domain(website)
            if domain:
                email = hunter_domain_search(domain, hunter_key)
                if email:
                    primary["_email"] = email
                    primary["_email_source"] = "hunter"
                    return primary, "hunter_only"
        return primary, "fetch_failed"

    domain = get_domain(website)

    # Email extraction
    email = extract_email(chunks, domain)
    if email:
        primary["_email"] = email
        primary["_email_source"] = "contact_page"
    elif hunter_key and domain:
        email = hunter_domain_search(domain, hunter_key)
        if email:
            primary["_email"] = email
            primary["_email_source"] = "hunter"

    # Owner extraction
    conf, owner_name, owner_cred = extract_owner(chunks)
    if owner_name:
        primary["_owner_name"] = owner_name
        primary["_owner_credential"] = owner_cred
        primary["_owner_confidence"] = conf

    return primary, "ok"


# =============================================================================
# Main
# =============================================================================

def main():
    with open(WITH_COMPETITORS_JSON) as f:
        primaries = json.load(f)

    hunter_key = os.environ.get("HUNTER_API_KEY")

    print(f"Enriching {len(primaries)} primaries (websites: emails + owners)", file=sys.stderr)
    print(f"Concurrency: {MAX_WORKERS} workers", file=sys.stderr)
    print(f"Hunter.io: {'ENABLED' if hunter_key else 'DISABLED (set HUNTER_API_KEY to enable)'}", file=sys.stderr)
    print(file=sys.stderr)

    # Counters
    emails_found = 0
    hunter_emails = 0
    owners_high = 0
    owners_med = 0
    fetch_failed = 0
    no_website = 0
    done = 0
    start = time.time()

    enriched = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = {ex.submit(enrich_one, p, hunter_key): i for i, p in enumerate(primaries)}
        for future in as_completed(futures):
            try:
                primary, status = future.result()
            except Exception:
                primary = primaries[futures[future]]
                primary.setdefault("_email", None)
                primary.setdefault("_owner_name", None)
                status = "error"

            enriched.append(primary)
            if primary.get("_email"):
                emails_found += 1
                if primary.get("_email_source") == "hunter":
                    hunter_emails += 1
            if primary.get("_owner_name"):
                if primary.get("_owner_confidence") == "high":
                    owners_high += 1
                else:
                    owners_med += 1
            if status == "fetch_failed":
                fetch_failed += 1
            elif status == "no_website":
                no_website += 1

            done += 1
            if done % 50 == 0:
                elapsed = time.time() - start
                rate = done / elapsed
                eta_min = (len(primaries) - done) / rate / 60
                print(
                    f"  {done:>4}/{len(primaries)} | "
                    f"email: {emails_found} | owner: {owners_high + owners_med} | "
                    f"fail: {fetch_failed} | ETA: {eta_min:.1f}min",
                    file=sys.stderr,
                )

    elapsed_min = (time.time() - start) / 60
    print(f"\nDone in {elapsed_min:.1f} min", file=sys.stderr)
    print(f"\nEMAIL", file=sys.stderr)
    print(f"  Contact-page scrape: {emails_found - hunter_emails}", file=sys.stderr)
    print(f"  Hunter.io fallback:  {hunter_emails}", file=sys.stderr)
    print(f"  Total:               {emails_found} ({emails_found/len(primaries)*100:.1f}%)", file=sys.stderr)
    print(f"\nOWNER", file=sys.stderr)
    print(f"  High-confidence (Owner/Founder named): {owners_high}", file=sys.stderr)
    print(f"  Med-confidence (Name + credential):    {owners_med}", file=sys.stderr)
    print(f"  Total:                                 {owners_high + owners_med} ({(owners_high+owners_med)/len(primaries)*100:.1f}%)", file=sys.stderr)
    print(f"\nSITES", file=sys.stderr)
    print(f"  No website: {no_website}", file=sys.stderr)
    print(f"  Fetch failed: {fetch_failed}", file=sys.stderr)

    with open(WITH_EMAILS_JSON, "w") as f:
        json.dump(enriched, f, indent=2)

    print(f"\nSaved to {WITH_EMAILS_JSON}", file=sys.stderr)
    print(f"Next: python3 05_export_csv.py", file=sys.stderr)


if __name__ == "__main__":
    main()
