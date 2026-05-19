# Lead Pipeline

Bulk-scrapes Google Maps via Apify → filters to ICP → assigns 3 competitors per primary → enriches emails → exports two CSVs ready for Google Sheets.

## What you get

Two CSVs in `~/Desktop/review-agency/leads/`:

- **master-list.csv** — one row per ICP-fit med spa. Columns: name, city, state, zip, phone, website, instagram, email, review count, star rating, address, GBP URL, categories, top 3 competitors (inline), plus call-tracking columns (`call_status`, `call_attempts`, `last_attempted`, `notes`).
- **competitors.csv** — long-format competitor reference. Each row is one competitor of one primary spa, with rank, distance, review count, star rating, GBP URL.

Expected scale: 2,000-3,500 primary records across the configured 38 metros, plus their ~6,000-10,500 competitor records.

## Prerequisites

```bash
pip install -r requirements.txt
```

API keys / credentials needed:

| Service | Required? | How to get | Cost |
|---|---|---|---|
| **Apify** | Yes | https://console.apify.com/account/integrations | Free tier $5/mo covers ~3,300 results |
| **Hunter.io** | Optional (fallback only) | https://hunter.io/api-keys | Free tier 50 lookups/mo; $49/mo for 500 |
| **Google service account** | Optional (only if writing direct to Sheets) | See Google Sheets setup section below | Free |

If you skip Hunter, Stage A (contact-page scraping) still hits ~60-70% of spas with emails. Hunter adds ~15-20% on top.

If you skip the Google service account, you'll get two CSVs you can import to Google Sheets manually (File > Import > Upload) in 30 seconds. The Sheets integration is for re-runs where you don't want to lose the call-tracking columns you've been editing.

## Run the pipeline

```bash
cd ~/Desktop/review-agency/leads/pipeline

export APIFY_TOKEN=your_apify_token
# Optional:
export HUNTER_API_KEY=your_hunter_key

# Step 1 — Bulk scrape Google Maps (10-30 min, costs ~$3-5)
python 01_apify_scrape.py

# Step 2 — Dedup + apply ICP filter (instant)
python 02_filter_icp.py

# Step 3 — Assign 3 nearest competitors to each primary (instant)
python 03_assign_competitors.py

# Step 4 — Enrich emails (10-30 min depending on dataset size)
python 04_enrich_websites.py

# Step 5 — Export final CSVs (instant)
python 05_export_csv.py

# Step 6 — (optional) Write direct to Google Sheets, preserves your call-tracking edits
export GOOGLE_SHEET_ID=your_sheet_id_here
python 06_write_to_sheets.py
```

After step 5, two CSVs land in `~/Desktop/review-agency/leads/`. Import to Google Sheets via `File > Import > Upload`.

After step 6 (if configured), data goes directly into the Google Sheet you specified, with two tabs: "Primary Targets" and "Competitors". On re-runs, any tracking columns you've edited (`call_status`, `call_attempts`, `last_attempted`, `notes`) are preserved per spa by matching on GBP URL.

## What each step does

### `01_apify_scrape.py`
Runs the Apify Google Maps Scraper actor (`compass/crawler-google-places`) with one search per `(city, query template)` combination from `config.py`. Default config: 38 cities × 3 queries × 30 results = 3,420 raw results.

Output: `data/01_raw_apify.json`

### `02_filter_icp.py`
- Dedups by GBP URL (same place returned by multiple queries)
- Drops anything matching `CHAIN_BLOCKLIST`
- Drops categories in `DROP_CATEGORIES` (hair salons, nail salons, etc.)
- Requires at least one category in `KEEP_CATEGORIES`
- Enforces `MIN_REVIEW_COUNT` (default 60) and `MIN_STAR_RATING` (default 4.0)
- Splits into `primary_targets` (ICP-match) and `competitor_pool` (everything else, including chains)

Output: `data/02_filtered_icp.json`

### `03_assign_competitors.py`
For each primary target, computes haversine distance to every other place in `competitor_pool`. Selects the 3 nearest within 10 miles, breaking ties by review count. The chain spas come back in as "real competitors" since patients compare against them.

Output: `data/03_with_competitors.json`

### `04_enrich_websites.py` (combined email + owner-name enrichment, ~15-25 min for 1500 leads)

Fetches each spa's website + ~10 common About / Team / Founders pages in a single round-trip per spa, then extracts BOTH from the same HTML:

- **Email** — `mailto:` links first, then regex match on raw HTML. Skips generic noreply/wix/squarespace addresses. Optional Hunter.io fallback if `HUNTER_API_KEY` is set (~60-70% hit rate on its own, +15-20% with Hunter).
- **Owner name + credential** — three pattern matchers ranked by confidence:
  - **High:** explicit "Owner Sarah Whelan" / "Founded by Sarah Whelan" / "Lead Injector: Sarah Whelan"
  - **Medium:** name + credential pattern ("Sarah Whelan, RN" / "Dr. Marcus Liang, DO")
  - **Medium-low:** "Dr. Lastname" appearing 2+ times on the page
  - Filters out false positives ("Beverly Hills", "Sandy Springs", "Privacy Policy", etc.)
  - Tally-vote across pages; highest-confidence pick wins
  - ~45% hit rate observed on real-world med spa data

Why combined: each spa needs ~5-15 sec of network time per fetch. Doing two separate passes doubled the total runtime and doubled load on the spa's server. Single pass is meaningfully faster.

Output adds these fields to each row's dict:
- `_email`, `_email_source` (`contact_page` / `hunter`)
- `_owner_name`, `_owner_credential`, `_owner_confidence` (`high` / `med`)

Pipeline file: writes to `data/04_with_emails.json` (kept the filename for backward compat).

### `05_export_csv.py`
Writes the two final CSVs. Schema documented at top of the script. **As of 2026-05-18 the master schema includes `owner_name` and `owner_credential` columns** populated by `04_enrich_websites.py`.

Output:
- `~/Desktop/review-agency/leads/master-list.csv`
- `~/Desktop/review-agency/leads/competitors.csv`

### `06_write_to_sheets.py` (optional)
Alternative to step 5. Writes the same data directly to a Google Sheet you control. On re-runs, preserves tracking columns (`call_status`, `call_attempts`, `last_attempted`, `notes`) per spa by matching on GBP URL — so you can re-pull updated review counts without losing your outreach history.

Output: data lands in the Google Sheet specified by `GOOGLE_SHEET_ID`. Two tabs: "Primary Targets" + "Competitors".

## Google Sheets setup (one-time, ~10 min)

Required only if you use `06_write_to_sheets.py`. Skip if you're fine with CSVs.

1. **Create a Google Cloud project** at https://console.cloud.google.com — name it whatever (e.g. "receipts-leads")
2. **Enable two APIs** in your project:
   - Google Sheets API: https://console.cloud.google.com/apis/library/sheets.googleapis.com
   - Google Drive API: https://console.cloud.google.com/apis/library/drive.googleapis.com
3. **Create a service account**: IAM & Admin > Service Accounts > Create Service Account
   - Give it a name like "receipts-pipeline"
   - Skip the "Grant access" step — service accounts don't need IAM roles for Sheets API
4. **Generate a JSON key**: click your new service account > Keys tab > Add Key > Create New Key > JSON > Create
   - A JSON file downloads. Save it as `~/Desktop/review-agency/leads/pipeline/secrets/google-service-account.json`
   - **The `secrets/` folder is already in .gitignore** — this never gets committed.
5. **Create your Google Sheet** — new blank sheet, name it "Receipts Leads"
6. **Copy the Sheet ID** from the URL:
   `https://docs.google.com/spreadsheets/d/<THIS_IS_THE_ID>/edit`
7. **Share the Sheet with the service account**:
   - Open the JSON file, find the `client_email` field (looks like `receipts-pipeline@project-name.iam.gserviceaccount.com`)
   - In the Google Sheet, click Share, paste that email, give Editor access, uncheck "notify"
8. **Set env vars and run**:
   ```bash
   export GOOGLE_SHEET_ID=<the_id_from_step_6>
   python 06_write_to_sheets.py
   ```

If you want to put the JSON somewhere other than `secrets/google-service-account.json`, set `GOOGLE_CREDS_PATH` env var.

## Configuration

All knobs live in `config.py`:

- `TARGET_METROS` — which cities to scrape. Add/remove as you expand.
- `SEARCH_QUERIES_PER_METRO` — search string templates. Default: 3 per metro.
- `MAX_RESULTS_PER_QUERY` — controls cost. 30 × 3 × 38 = 3,420 results × $0.0015 = ~$5.
- `MIN_REVIEW_COUNT` — ICP review floor (proxy for $1M+ revenue). Default 60.
- `CHAIN_BLOCKLIST` — names that get excluded from primaries. Add new chains here.
- `COMPETITOR_RADIUS_MILES` — how far to look for competitors. Default 10.

## Cost summary (default config)

| Item | Cost |
|---|---|
| Apify scrape (~3,420 results) | $3.50-5.00 |
| Hunter.io (optional) | $0 free / $49/mo |
| Time (start-to-finish) | ~30-60 minutes |

## Re-running for new cities

To add new cities later:
1. Add to `TARGET_METROS` in `config.py`
2. Run `01_apify_scrape.py` again (it will pull new + already-seen data; that's fine)
3. Run the rest of the pipeline; dedup is handled

## What this does NOT do

- **Verify "single-owner" status** — Apify can't see ownership structure. Cold-call discovery (or a Phase 2 VA pass) catches this.
- **Verify "operating 2+ years"** — proxy via review count works ~85% of the time.
- **Distinguish single-location independent vs. small chain (2-3 locations)** — partial chain detection via name matching; not perfect.

## Retroactive enrichment scripts (standalone, not part of pipeline)

For master-list.csv or Excel files that already exist (e.g., the Google Sheets / Excel CRM file), these scripts fill in missing data without re-running the full pipeline:

- **`scrape_owner_names.py`** — operates directly on the Excel CRM file at `~/Desktop/google review_ ai call center .xlsx`. Reads MASTER tab, fills in `owner_name` + `owner_credential` for rows where they're blank. Same pattern matching as `04_enrich_websites.py`. ~21 min for 1,300 rows; ~45% hit rate.

- **`enrich_master_emails.py`** — operates directly on `master-list.csv` (the pipeline output). Fills in email column for rows where it's blank. Useful when you've added new rows manually and want to back-fill emails without re-running the full pipeline.

Both run as: `python3 scrape_owner_names.py` (or `python3 enrich_master_emails.py`).

## Troubleshooting

**"Module not found: apify_client"** → Run `pip install -r requirements.txt`

**"APIFY_TOKEN environment variable not set"** → `export APIFY_TOKEN=apify_api_xxxxx` (find in console.apify.com)

**Apify run shows 0 results** → Check the actor at https://apify.com/compass/crawler-google-places — they may have renamed it. Update `APIFY_ACTOR_ID` in config.py.

**Step 04 is slow** → Each spa needs ~5-15 sec of website fetching. 10 workers gets you through 1,500 spas in ~15-25 min. To speed up further: bump `MAX_WORKERS` to 20 (more aggressive, may trip anti-bot defenses on some sites).

**Want to scrape Google Maps without Apify?** Alternatives: Outscraper ($0.0008/record), SerpAPI, or Google Places API directly ($17 per 1K searches + $32 per 1K details).
