"""
scrape_owner_names.py — Pulls owner names from each spa's website About/Team page,
writes back to MASTER!F (owner_name) and MASTER!G (owner_credential).

Strategy per spa:
1. Fetch homepage + /about, /about-us, /team, /meet-the-team, /our-team, /staff, /founders
2. Look for explicit ownership signals:
   - "Founder Sarah Whelan, RN"
   - "Owned by Sarah Whelan"
   - "Dr. Marcus Liang"
   - "[Name], RN/NP/PA/MD/DO/etc."
3. Score candidates, pick highest-confidence
4. Skip rows that already have owner_name set

Concurrent (10 workers), ~15-25 min for 1500 sites.

Run:
    python3 scrape_owner_names.py
"""

import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse

try:
    import requests
    from bs4 import BeautifulSoup
    from openpyxl import load_workbook
except ImportError:
    print("Run: pip install requests beautifulsoup4 openpyxl", file=sys.stderr)
    sys.exit(1)

XLSX = "/Users/tomnorth/Desktop/google review_ ai call center .xlsx"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
}
TIMEOUT = 6
MAX_WORKERS = 10

ABOUT_PATHS = ["", "/about", "/about-us", "/team", "/meet-the-team",
               "/our-team", "/staff", "/founders", "/who-we-are", "/meet-us"]

# Credentials we care about, ordered for preference matching
CREDENTIALS = [
    "MD", "DO", "DMD", "DDS", "NMD", "ND",
    "DNP", "FNP-C", "FNP-BC", "FNP", "NP-C", "NP-BC", "NP",
    "APRN", "ARNP", "AGPCNP-BC", "AGNP",
    "PA-C", "PA",
    "MSN", "BSN", "RN",
    "LE", "LME", "CRNA", "CANS", "CPSN",
]
CRED_RE = "|".join(re.escape(c) for c in CREDENTIALS)

# Pattern A: "Name, Credential" (most reliable)
P_NAME_CRED = re.compile(
    rf'\b(?P<name>(?:Dr\.?\s+)?[A-Z][a-z\']{{1,20}}(?:\s+[A-Z]\.?)?(?:\s+[A-Z][a-z\'-]{{1,20}}){{1,2}})\s*,\s*(?P<cred>{CRED_RE})\b'
)

# Pattern B: "Owner/Founder Sarah Whelan"
P_OWNER_NAME = re.compile(
    r'\b(?:Owner|Owner-Operator|Founder|Founded by|Owned by|Owner/Operator|Lead Injector|Medical Director|Practice Owner)\s*[:\-]?\s*'
    r'(?P<name>(?:Dr\.?\s+)?[A-Z][a-z\']{1,20}(?:\s+[A-Z]\.?)?(?:\s+[A-Z][a-z\'-]{1,20}){1,2})'
    r'(?:,\s*(?P<cred>' + CRED_RE + r'))?'
)

# Pattern C: "Dr. Sarah Connor" or "Dr Sarah Connor" anywhere
P_DR_NAME = re.compile(
    r'\bDr\.?\s+(?P<name>[A-Z][a-z\']{1,20}(?:\s+[A-Z]\.?)?(?:\s+[A-Z][a-z\'-]{1,20}){1,2})'
)

# Words that look like names but are common false positives
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


def get_domain(url):
    try:
        return urlparse(url).netloc.lower().lstrip("www.")
    except Exception:
        return ""


def normalize_url(url):
    """Ensure protocol; trim trailing slash."""
    if not url:
        return None
    url = url.strip()
    if not url:
        return None
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url.rstrip("/")


def fetch_pages(base_url):
    """Fetch homepage + a few common About paths. Return combined text."""
    if not base_url:
        return ""
    text_parts = []
    for path in ABOUT_PATHS:
        url = base_url + path
        try:
            r = requests.get(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
            if r.status_code != 200:
                continue
            soup = BeautifulSoup(r.text, "html.parser")
            # Drop scripts, styles, navs
            for tag in soup(["script", "style", "noscript", "svg"]):
                tag.decompose()
            text_parts.append(soup.get_text(separator=" ", strip=True))
        except Exception:
            continue
    return " ".join(text_parts)


def score_candidates(text):
    """Return list of (confidence, name, credential) candidates."""
    candidates = []

    # Pattern B: explicit owner/founder + name (HIGH confidence)
    for m in P_OWNER_NAME.finditer(text):
        name = m.group("name").strip()
        cred = (m.group("cred") or "").strip()
        if name in NOT_A_NAME or len(name.split()) < 2:
            continue
        candidates.append(("high", name, cred))

    # Pattern A: name + credential anywhere (MED confidence)
    for m in P_NAME_CRED.finditer(text):
        name = m.group("name").strip()
        cred = m.group("cred").strip()
        if name in NOT_A_NAME or len(name.split()) < 2:
            continue
        candidates.append(("med", name, cred))

    # Pattern C: Dr. Name (MED confidence — but only if appears 2+ times)
    dr_names = {}
    for m in P_DR_NAME.finditer(text):
        name = m.group("name").strip()
        if name in NOT_A_NAME or len(name.split()) < 1:
            continue
        full = f"Dr. {name}"
        dr_names[full] = dr_names.get(full, 0) + 1
    for full, count in dr_names.items():
        if count >= 2:
            candidates.append(("med", full, "MD"))

    return candidates


def best_pick(candidates):
    """Pick the best candidate. Prefer high-confidence + name with credential."""
    if not candidates:
        return None, None, None

    by_conf = {"high": [], "med": [], "low": []}
    for conf, name, cred in candidates:
        by_conf[conf].append((name, cred))

    # Tally votes — name that appears most across all matches wins within tier
    for conf in ["high", "med", "low"]:
        if not by_conf[conf]:
            continue
        votes = {}
        for name, cred in by_conf[conf]:
            key = name
            votes.setdefault(key, {"count": 0, "creds": []})
            votes[key]["count"] += 1
            if cred:
                votes[key]["creds"].append(cred)
        # Best = highest vote count
        best_name = max(votes.keys(), key=lambda k: votes[k]["count"])
        creds = votes[best_name]["creds"]
        best_cred = creds[0] if creds else ""
        return conf, best_name, best_cred

    return None, None, None


def scrape_one(website):
    """Returns (confidence, owner_name, owner_credential) — all None if nothing found."""
    base = normalize_url(website)
    if not base:
        return None, None, None
    try:
        text = fetch_pages(base)
        if not text:
            return None, None, None
        candidates = score_candidates(text)
        return best_pick(candidates)
    except Exception:
        return None, None, None


def main():
    print(f"Loading {XLSX}...", file=sys.stderr)
    wb = load_workbook(XLSX)
    ws = wb["MASTER"]

    # Determine columns by header row
    headers = [c.value for c in ws[1]]
    col_owner = headers.index("owner_name") + 1  # F
    col_cred = headers.index("owner_credential") + 1  # G
    col_website = headers.index("website") + 1  # J
    col_priority_idx = headers.index("priority") + 1 if "priority" in headers else None

    print(f"Columns — owner_name: {col_owner}, owner_credential: {col_cred}, website: {col_website}", file=sys.stderr)

    # Collect rows needing enrichment
    needs = []
    for row in range(2, ws.max_row + 1):
        existing_owner = ws.cell(row, col_owner).value
        website = ws.cell(row, col_website).value
        if not website:
            continue
        if existing_owner and str(existing_owner).strip():
            continue  # already populated (agent seeds + manual)
        needs.append((row, website))

    print(f"Rows needing enrichment: {len(needs)}", file=sys.stderr)
    print(f"Concurrency: {MAX_WORKERS} workers", file=sys.stderr)

    if not needs:
        print("Nothing to do.", file=sys.stderr)
        return

    found = {"high": 0, "med": 0, "low": 0}
    misses = 0
    start = time.time()
    done = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = {ex.submit(scrape_one, w): (r, w) for r, w in needs}
        for future in as_completed(futures):
            row, website = futures[future]
            try:
                conf, name, cred = future.result()
            except Exception:
                conf, name, cred = None, None, None

            if name:
                ws.cell(row, col_owner).value = name
                if cred:
                    ws.cell(row, col_cred).value = cred
                found[conf] = found.get(conf, 0) + 1
            else:
                misses += 1

            done += 1
            if done % 50 == 0:
                elapsed = time.time() - start
                rate = done / elapsed
                eta_min = (len(needs) - done) / rate / 60
                hits = sum(found.values())
                print(
                    f"  {done:>4}/{len(needs)} | "
                    f"high: {found.get('high',0)} | med: {found.get('med',0)} | miss: {misses} | "
                    f"hit rate: {hits/done*100:.0f}% | ETA: {eta_min:.1f}min",
                    file=sys.stderr,
                )

    print(f"\nDone in {(time.time() - start)/60:.1f} min", file=sys.stderr)
    total_hits = sum(found.values())
    print(f"  High-confidence (Owner/Founder explicitly named):  {found.get('high', 0)}", file=sys.stderr)
    print(f"  Med-confidence (Name + credential pattern):        {found.get('med', 0)}", file=sys.stderr)
    print(f"  Misses:                                            {misses}", file=sys.stderr)
    print(f"  Total found:                                       {total_hits} ({total_hits/len(needs)*100:.1f}%)", file=sys.stderr)

    print(f"\nSaving to {XLSX}...", file=sys.stderr)
    wb.save(XLSX)
    print(f"Saved.", file=sys.stderr)


if __name__ == "__main__":
    main()
