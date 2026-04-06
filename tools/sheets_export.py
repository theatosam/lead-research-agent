"""
sheets_export.py — Export qualified leads with drafts to a Google Sheet using gspread.

Usage:
    python tools/sheets_export.py --input output/leads_with_drafts.json

Environment variables required (in .env):
    GOOGLE_SHEET_ID          — ID of the target Google Sheet
    GOOGLE_CREDENTIALS_PATH  — Path to service account credentials JSON

Importable function:
    from tools.sheets_export import run
"""

import argparse
import json
import os
import sys
from datetime import date
from pathlib import Path

import gspread
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

COLUMNS = [
    "Company",
    "Contact",
    "Role",
    "Industry",
    "ICP Score",
    "Tier",
    "Reasoning",
    "Email",
    "Subject",
    "Draft Body",
    "Status",
]


def get_status(lead: dict) -> str:
    if not lead.get("qualified"):
        return "Below threshold"
    subject = lead.get("draft_subject", "")
    if subject == "DRAFT_FAILED" or not subject:
        return "Draft failed"
    return "Draft ready"


def lead_to_row(lead: dict) -> list:
    return [
        lead.get("company", ""),
        lead.get("name", ""),
        lead.get("role", ""),
        lead.get("industry", ""),
        lead.get("score", ""),
        lead.get("tier", ""),
        lead.get("reasoning", ""),
        lead.get("email", ""),
        lead.get("draft_subject", ""),
        lead.get("draft_body", ""),
        get_status(lead),
    ]


def get_unique_tab_name(spreadsheet: gspread.Spreadsheet, base_name: str) -> str:
    existing = [ws.title for ws in spreadsheet.worksheets()]
    if base_name not in existing:
        return base_name
    counter = 2
    while f"{base_name} ({counter})" in existing:
        counter += 1
    return f"{base_name} ({counter})"


def run(input_path: str) -> None:
    """Export leads to Google Sheets. Reads credentials from environment."""
    with open(input_path, encoding="utf-8") as f:
        leads = json.load(f)

    sheet_id = os.getenv("GOOGLE_SHEET_ID")
    credentials_path = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")

    if not sheet_id:
        print("[EXPORT] ERROR: GOOGLE_SHEET_ID is not set in .env", file=sys.stderr)
        sys.exit(1)

    if not Path(credentials_path).exists():
        print(f"[EXPORT] ERROR: Credentials file not found at '{credentials_path}'", file=sys.stderr)
        print("[EXPORT] Set GOOGLE_CREDENTIALS_PATH in .env to point to your service account JSON.", file=sys.stderr)
        sys.exit(1)

    try:
        credentials_json_str = os.getenv("GOOGLE_CREDENTIALS_JSON")
        if credentials_json_str:
            import json as _json
            creds = Credentials.from_service_account_info(_json.loads(credentials_json_str), scopes=SCOPES)
        elif Path(credentials_path).exists():
            creds = Credentials.from_service_account_file(credentials_path, scopes=SCOPES)
        else:
            print(f"[EXPORT] ERROR: No credentials found. Set GOOGLE_CREDENTIALS_JSON env var or place credentials.json at '{credentials_path}'", file=sys.stderr)
            sys.exit(1)
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(sheet_id)
    except Exception as e:
        print(f"[EXPORT] ERROR: Failed to connect to Google Sheets: {e}", file=sys.stderr)
        sys.exit(1)

    tab_name = get_unique_tab_name(spreadsheet, f"Lead Research — {date.today()}")

    try:
        worksheet = spreadsheet.add_worksheet(title=tab_name, rows=len(leads) + 5, cols=len(COLUMNS))
    except Exception as e:
        print(f"[EXPORT] ERROR: Could not create worksheet '{tab_name}': {e}", file=sys.stderr)
        fallback_path = Path(input_path).parent / "export_fallback.json"
        with open(fallback_path, "w", encoding="utf-8") as f:
            json.dump(leads, f, indent=2)
        print(f"[EXPORT] Data saved to fallback: {fallback_path}. Fix the Sheets error and re-run.", file=sys.stderr)
        sys.exit(1)

    try:
        rows = [COLUMNS] + [lead_to_row(lead) for lead in leads]
        worksheet.update(rows, value_input_option="RAW")

        # Format: freeze header row, bold it
        worksheet.freeze(rows=1)
        spreadsheet.batch_update({
            "requests": [
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": worksheet.id,
                            "startRowIndex": 0,
                            "endRowIndex": 1,
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "textFormat": {"bold": True},
                                "backgroundColor": {"red": 0.95, "green": 0.95, "blue": 0.95},
                            }
                        },
                        "fields": "userEnteredFormat(textFormat,backgroundColor)",
                    }
                }
            ]
        })

    except Exception as e:
        print(f"[EXPORT] ERROR: Failed mid-write: {e}", file=sys.stderr)
        fallback_path = Path(input_path).parent / "export_fallback.json"
        with open(fallback_path, "w", encoding="utf-8") as f:
            json.dump(leads, f, indent=2)
        print(f"[EXPORT] Data saved to fallback: {fallback_path}. Fix the Sheets error and re-run.", file=sys.stderr)
        sys.exit(1)

    draft_count = sum(1 for lead in leads if get_status(lead) == "Draft ready")
    print(f'[EXPORT] Sheet created: "{tab_name}". {len(leads)} rows written. {draft_count} with drafts.')


def main():
    parser = argparse.ArgumentParser(description="Export leads with drafts to Google Sheets.")
    parser.add_argument("--input", required=True, help="Path to leads with drafts JSON")
    args = parser.parse_args()
    run(args.input)


if __name__ == "__main__":
    main()
