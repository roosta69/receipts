"""
Receipts lead pipeline — configuration constants.

Edit this file to change cities, ICP thresholds, or chain blocklist.
Do NOT hardcode these in the scripts.
"""

# -- Target metros (city, state) ---------------------------------------------
# Ordered by NP/RN-friendly scope-of-practice + med-spa density per capita.

TARGET_METROS = [
    # Texas (NP full practice authority pending — but RN-led OK)
    ("Dallas", "TX"),
    ("Fort Worth", "TX"),
    ("Frisco", "TX"),
    ("Plano", "TX"),
    ("McKinney", "TX"),
    ("Austin", "TX"),
    ("Round Rock", "TX"),
    ("San Antonio", "TX"),
    ("Houston", "TX"),
    ("Sugar Land", "TX"),
    ("The Woodlands", "TX"),
    ("Katy", "TX"),

    # Florida (no full-NP-authority but high WTP + density)
    ("Miami", "FL"),
    ("Miami Beach", "FL"),
    ("Coral Gables", "FL"),
    ("Aventura", "FL"),
    ("Doral", "FL"),
    ("Tampa", "FL"),
    ("St. Petersburg", "FL"),
    ("Clearwater", "FL"),
    ("Orlando", "FL"),
    ("Winter Park", "FL"),
    ("Lake Mary", "FL"),
    ("Jacksonville", "FL"),
    ("Naples", "FL"),
    ("Sarasota", "FL"),

    # Arizona (NP full practice authority; highest per-capita med spa density)
    ("Phoenix", "AZ"),
    ("Scottsdale", "AZ"),
    ("Tempe", "AZ"),
    ("Chandler", "AZ"),
    ("Gilbert", "AZ"),
    ("Mesa", "AZ"),
    ("Paradise Valley", "AZ"),

    # Georgia (Atlanta metro spread)
    ("Atlanta", "GA"),
    ("Buckhead", "GA"),
    ("Sandy Springs", "GA"),
    ("Alpharetta", "GA"),
    ("Marietta", "GA"),

    # Tennessee (Nashville metro)
    ("Nashville", "TN"),
    ("Franklin", "TN"),
    ("Brentwood", "TN"),
    ("Knoxville", "TN"),
]

# Search queries to run per metro. Apify Google Maps Scraper will run each.
# Use 3 queries per city to catch different listing categories.
SEARCH_QUERIES_PER_METRO = [
    "med spa {city} {state}",
    "medical aesthetics {city} {state}",
    "botox {city} {state}",
]

# Max results per (query, city) — Apify free tier covers ~3500 total results
# at $1.50/1000. With 38 cities × 3 queries × 30 results = ~3420 raw results.
MAX_RESULTS_PER_QUERY = 30


# -- ICP thresholds ----------------------------------------------------------

MIN_REVIEW_COUNT = 60               # Proxy for $1M+ revenue + established
MIN_STAR_RATING = 4.0
MIN_ACTIVE_WITHIN_DAYS = 90         # Last review must be within this window
MIN_YEARS_OPERATING = 2             # Proxy for established


# -- Chain blocklist (case-insensitive substring match) -----------------------
# If the spa name contains any of these strings, exclude from primary targets.
# Stay in the chain reference list for competitor matching purposes.

CHAIN_BLOCKLIST = [
    # National injectable / med spa chains
    "ideal image",
    "laseraway",
    "allē",
    "alle spa",
    "skinspirit",
    "skin spirit",
    "sona med spa",
    "sona dermatology",
    "massage envy",
    "european wax",
    "lasertopia",
    "skin laundry",
    "milan laser",
    "lasercare",
    "hydromassage",
    "sono bello",
    "spavia",
    "amaira med spa",
    "the now",
    "soothe",
    # Discovered via 2026-05-15 Apify test scrape (Phoenix/Scottsdale) — multi-location
    "nakedmd",
    "look lab med spa",
    "dolce medical spa",
    "mdskin lounge",
    "mdskin bar",
    # Cross-vertical chains that sometimes appear in med-spa search
    "ulta beauty",
    "sephora",
    "drybar",
    "blo blow dry",
    "blo ",
    "kiehl's",
    "dermalogica",
    # Dermatology-MD chains (often offer Botox but ICP filter says no)
    "u.s. dermatology",
    "dermatology associates",
    "advanced dermatology",
    "forefront dermatology",
    "epiphany dermatology",
    "anne arundel dermatology",
]


# -- Filter rules ------------------------------------------------------------

# Categories from Google Places to keep
KEEP_CATEGORIES = [
    "medical spa",
    "medical clinic",
    "skin care clinic",
    "facial spa",
    "aesthetic medicine",
    "wellness center",
    "weight loss service",
]

# Categories to drop hard (means it's not a med spa)
DROP_CATEGORIES = [
    "hair salon",
    "barber shop",
    "nail salon",
    "tattoo shop",
    "massage therapist",
    "dental clinic",
    "dentist",
    "veterinarian",
    "gym",
    "yoga studio",
]


# -- Competitor assignment ---------------------------------------------------

COMPETITOR_RADIUS_MILES = 10
COMPETITORS_PER_PRIMARY = 3


# -- Apify --------------------------------------------------------------------

APIFY_ACTOR_ID = "compass/crawler-google-places"
# Free tier $5/mo covers ~3000 results at $1.50/1000.


# -- Output paths ------------------------------------------------------------

import os
PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__))
LEADS_DIR = os.path.dirname(PIPELINE_DIR)
DATA_DIR = os.path.join(PIPELINE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

RAW_APIFY_JSON = os.path.join(DATA_DIR, "01_raw_apify.json")
FILTERED_JSON = os.path.join(DATA_DIR, "02_filtered_icp.json")
WITH_COMPETITORS_JSON = os.path.join(DATA_DIR, "03_with_competitors.json")
WITH_EMAILS_JSON = os.path.join(DATA_DIR, "04_with_emails.json")

MASTER_CSV = os.path.join(LEADS_DIR, "master-list.csv")
COMPETITORS_CSV = os.path.join(LEADS_DIR, "competitors.csv")
