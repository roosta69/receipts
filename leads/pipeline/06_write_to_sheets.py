"""
06_write_to_sheets.py — Write the pipeline output directly to Google Sheets.

Alternative to 05_export_csv.py — writes the same data to a Google Sheet you control.
Critically: preserves any tracking columns you've edited (call_status, call_attempts,
last_attempted, notes) between pipeline runs. Only data columns get refreshed.

Setup (one-time, ~10 min):
  1. Create a Google Cloud project at https://console.cloud.google.com
  2. Enable Google Sheets API + Google Drive API
  3. Create a service account (IAM & Admin > Service Accounts > Create)
  4. Generate a JSON key for it (Keys tab > Add Key > JSON), download
  5. Save the JSON to `secrets/google-service-account.json` in this folder
  6. Create a new Google Sheet, copy its ID from the URL
     (https://docs.google.com/spreadsheets/d/THIS_PART_IS_THE_ID/edit)
  7. Share the Sheet with the service account email (it's in the JSON, looks like
     `something@project-id.iam.gserviceaccount.com`) — give it Editor access

Run:
    export GOOGLE_SHEET_ID=your_sheet_id_here
    python 06_write_to_sheets.py

Or to also still produce the CSV backups in parallel:
    python 05_export_csv.py && python 06_write_to_sheets.py
"""

import json
import os
import sys
from typing import Dict, List

try:
    import gspread
    from google.oauth2.service_account import Credentials
except ImportError:
    print("Missing dependency. Run: pip install -r requirements.txt", file=sys.stderr)
    sys.exit(1)

from config import WITH_EMAILS_JSON, PIPELINE_DIR

# Reuse the CSV exporter's data-flattening logic so both outputs are identical
sys.path.insert(0, PIPELINE_DIR)
from importlib import import_module
csv_exporter = import_module("05_export_csv")


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

DEFAULT_CREDS_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "secrets",
    "google-service-account.json",
)

# Tracking columns the user edits — we preserve these across runs
TRACKING_COLUMNS = ["call_status", "call_attempts", "last_attempted", "notes"]

MASTER_SHEET_NAME = "Primary Targets"
COMPETITORS_SHEET_NAME = "Competitors"

MASTER_HEADERS = [
    "name", "city", "state", "zip",
    "phone", "website", "instagram", "email", "email_source",
    "google_review_count", "google_star_rating",
    "address", "gbp_url", "categories",
    "top_competitor_1_name", "top_competitor_1_reviews", "top_competitor_1_stars", "top_competitor_1_distance",
    "top_competitor_2_name", "top_competitor_2_reviews", "top_competitor_2_stars", "top_competitor_2_distance",
    "top_competitor_3_name", "top_competitor_3_reviews", "top_competitor_3_stars", "top_competitor_3_distance",
    "notes", "call_status", "call_attempts", "last_attempted",
]

COMPETITOR_HEADERS = [
    "primary_spa_name", "primary_spa_city", "competitor_rank",
    "competitor_name", "competitor_review_count", "competitor_star_rating",
    "competitor_distance_miles", "competitor_gbp_url",
]


def get_client(creds_path: str) -> gspread.Client:
    """Authorize with Google via service account JSON."""
    if not os.path.exists(creds_path):
        raise FileNotFoundError(
            f"Service account JSON not found at {creds_path}.\n"
            "See setup instructions at top of this file."
        )
    creds = Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    return gspread.authorize(creds)


def get_or_create_worksheet(spreadsheet, name: str, headers: List[str]):
    """Return the named worksheet, creating it with headers if missing."""
    try:
        ws = spreadsheet.worksheet(name)
        # Sanity-check headers exist; if blank, write them
        existing = ws.row_values(1)
        if not existing:
            ws.update("A1", [headers])
            ws.freeze(rows=1)
        return ws
    except gspread.exceptions.WorksheetNotFound:
        ws = spreadsheet.add_worksheet(
            title=name,
            rows=max(2000, ws_min_rows := 100),
            cols=len(headers),
        )
        ws.update("A1", [headers])
        ws.freeze(rows=1)
        return ws


def read_existing_tracking(ws) -> Dict[str, Dict[str, str]]:
    """Read existing tracking columns keyed by gbp_url so we don't overwrite user edits."""
    try:
        records = ws.get_all_records()
    except Exception:
        return {}

    tracking = {}
    for row in records:
        gbp = row.get("gbp_url", "")
        if gbp:
            tracking[gbp] = {col: row.get(col, "") for col in TRACKING_COLUMNS}
    return tracking


def build_master_rows(primaries: List[Dict], existing_tracking: Dict) -> List[List]:
    """Build the list-of-lists payload for the Primary Targets sheet."""
    rows = []
    for place in primaries:
        city, state, zip_code = csv_exporter.parse_city_state_zip(place)
        comps = place.get("_competitors") or []
        gbp_url = csv_exporter.safe_str(place.get("url"))

        # Pull existing tracking values if this spa was already in the sheet
        tracking = existing_tracking.get(gbp_url, {
            "call_status": "not_called",
            "call_attempts": 0,
            "last_attempted": "",
            "notes": "",
        })

        row_dict = {
            "name": csv_exporter.safe_str(place.get("title")),
            "city": city,
            "state": state,
            "zip": zip_code,
            "phone": csv_exporter.safe_str(place.get("phone") or place.get("phoneNumber")),
            "website": csv_exporter.safe_str(place.get("website")),
            "instagram": csv_exporter.safe_str(csv_exporter.extract_instagram(place)),
            "email": csv_exporter.safe_str(place.get("_email")),
            "email_source": csv_exporter.safe_str(place.get("_email_source")),
            "google_review_count": csv_exporter.safe_int(place.get("reviewsCount")),
            "google_star_rating": csv_exporter.safe_float(place.get("totalScore")),
            "address": csv_exporter.safe_str(place.get("address")),
            "gbp_url": gbp_url,
            "categories": "; ".join(place.get("categories") or []),
            "notes": tracking.get("notes", ""),
            "call_status": tracking.get("call_status", "not_called"),
            "call_attempts": tracking.get("call_attempts", 0),
            "last_attempted": tracking.get("last_attempted", ""),
        }

        for i in range(3):
            comp = comps[i] if i < len(comps) else {}
            row_dict[f"top_competitor_{i+1}_name"] = csv_exporter.safe_str(comp.get("name"))
            row_dict[f"top_competitor_{i+1}_reviews"] = csv_exporter.safe_int(comp.get("review_count"))
            row_dict[f"top_competitor_{i+1}_stars"] = csv_exporter.safe_float(comp.get("star_rating"))
            row_dict[f"top_competitor_{i+1}_distance"] = csv_exporter.safe_float(comp.get("distance_miles"))

        rows.append([row_dict.get(h, "") for h in MASTER_HEADERS])

    return rows


def build_competitor_rows(primaries: List[Dict]) -> List[List]:
    """Build the list-of-lists payload for the Competitors sheet."""
    rows = []
    for place in primaries:
        primary_name = csv_exporter.safe_str(place.get("title"))
        city, _, _ = csv_exporter.parse_city_state_zip(place)
        for rank, comp in enumerate(place.get("_competitors") or [], start=1):
            rows.append([
                primary_name,
                city,
                rank,
                csv_exporter.safe_str(comp.get("name")),
                csv_exporter.safe_int(comp.get("review_count")),
                csv_exporter.safe_float(comp.get("star_rating")),
                csv_exporter.safe_float(comp.get("distance_miles")),
                csv_exporter.safe_str(comp.get("gbp_url")),
            ])
    return rows


def write_sheet(ws, headers: List[str], rows: List[List]):
    """Clear data rows (preserving headers) and write fresh data."""
    # Ensure enough rows; gspread auto-expands but we'll resize for cleanliness
    needed_rows = len(rows) + 1  # +1 for header
    if ws.row_count < needed_rows:
        ws.resize(rows=needed_rows + 100, cols=len(headers))

    # Clear existing data below the header row
    last_col_letter = chr(ord("A") + len(headers) - 1) if len(headers) <= 26 else "AZ"
    if ws.row_count > 1:
        ws.batch_clear([f"A2:{last_col_letter}{ws.row_count}"])

    if not rows:
        return

    # Batch-write all data in one API call
    ws.update(f"A2", rows, value_input_option="RAW")


def main():
    sheet_id = os.environ.get("GOOGLE_SHEET_ID")
    if not sheet_id:
        print("ERROR: GOOGLE_SHEET_ID environment variable not set.", file=sys.stderr)
        print("Get it from your Sheet URL: docs.google.com/spreadsheets/d/<THIS_PART>/edit", file=sys.stderr)
        sys.exit(1)

    creds_path = os.environ.get("GOOGLE_CREDS_PATH", DEFAULT_CREDS_PATH)

    print(f"Authorizing with Google...", file=sys.stderr)
    client = get_client(creds_path)

    print(f"Opening sheet {sheet_id}...", file=sys.stderr)
    spreadsheet = client.open_by_key(sheet_id)

    print(f"Loading pipeline data from {WITH_EMAILS_JSON}...", file=sys.stderr)
    with open(WITH_EMAILS_JSON) as f:
        primaries = json.load(f)

    # Master sheet — preserve tracking columns from any existing rows
    print(f"\nWriting '{MASTER_SHEET_NAME}' tab...", file=sys.stderr)
    master_ws = get_or_create_worksheet(spreadsheet, MASTER_SHEET_NAME, MASTER_HEADERS)
    existing_tracking = read_existing_tracking(master_ws)
    print(f"  Preserving tracking columns for {len(existing_tracking)} existing rows", file=sys.stderr)
    master_rows = build_master_rows(primaries, existing_tracking)
    write_sheet(master_ws, MASTER_HEADERS, master_rows)
    print(f"  Wrote {len(master_rows)} primary target rows", file=sys.stderr)

    # Competitors sheet — pure overwrite, no tracking to preserve
    print(f"\nWriting '{COMPETITORS_SHEET_NAME}' tab...", file=sys.stderr)
    comp_ws = get_or_create_worksheet(spreadsheet, COMPETITORS_SHEET_NAME, COMPETITOR_HEADERS)
    comp_rows = build_competitor_rows(primaries)
    write_sheet(comp_ws, COMPETITOR_HEADERS, comp_rows)
    print(f"  Wrote {len(comp_rows)} competitor reference rows", file=sys.stderr)

    sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit"
    print(f"\nDone. Open your sheet: {sheet_url}", file=sys.stderr)


if __name__ == "__main__":
    main()
