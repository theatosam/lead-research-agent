"""
find_leads.py — Load and normalize a CSV of prospects into a clean JSON list.

Usage:
    python tools/find_leads.py --input data/sample_leads.csv
    python tools/find_leads.py --input data/sample_leads.csv --output output/leads_normalized.json

Importable function:
    from tools.find_leads import run
"""

import argparse
import csv
import json
import sys
from pathlib import Path

REQUIRED_COLUMNS = {"name", "company", "role", "industry", "email", "company_size", "notes"}


def normalize(leads_raw: list[dict]) -> tuple[list[dict], int]:
    """Normalize raw CSV rows into clean lead dicts. Returns (leads, duplicate_count)."""
    seen = set()
    leads = []
    duplicates = 0

    for row in leads_raw:
        key = (row.get("company", "").strip().lower(), row.get("email", "").strip().lower())
        if key in seen:
            print(f"[FIND] WARN: Duplicate skipped — {row.get('company')} / {row.get('email')}", file=sys.stderr)
            duplicates += 1
            continue
        seen.add(key)

        company_size_raw = row.get("company_size", "").strip()
        try:
            company_size = int(company_size_raw)
        except (ValueError, TypeError):
            if company_size_raw:
                print(f"[FIND] WARN: Invalid company_size '{company_size_raw}' for {row.get('company')} — set to 0", file=sys.stderr)
            company_size = 0

        leads.append({
            "name": row.get("name", "").strip(),
            "company": row.get("company", "").strip(),
            "role": row.get("role", "").strip(),
            "industry": row.get("industry", "").strip(),
            "email": row.get("email", "").strip(),
            "company_size": company_size,
            "notes": row.get("notes", "").strip(),
        })

    return leads, duplicates


def load_csv(source) -> list[dict]:
    """Read CSV and validate required columns. source can be a file path (str) or a file-like object."""
    if isinstance(source, str):
        csv_path = Path(source)
        if not csv_path.exists():
            print(f"[FIND] ERROR: File not found at {source}", file=sys.stderr)
            sys.exit(1)
        f = open(csv_path, newline="", encoding="utf-8")
        close_after = True
    else:
        # File-like object (e.g. io.StringIO from web upload)
        import io
        if isinstance(source, (bytes, bytearray)):
            source = io.StringIO(source.decode("utf-8"))
        f = source
        close_after = False

    try:
        reader = csv.DictReader(f)
        columns = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - columns
        if missing:
            print(f"[FIND] ERROR: Missing required columns: {', '.join(sorted(missing))}", file=sys.stderr)
            print(f"[FIND] Required columns: {', '.join(sorted(REQUIRED_COLUMNS))}", file=sys.stderr)
            sys.exit(1)
        return list(reader)
    finally:
        if close_after:
            f.close()


def run(input_path: str, output_path: str | None = None) -> list[dict]:
    """Load, normalize, and optionally save leads. Returns normalized lead list."""
    raw = load_csv(input_path)
    leads, duplicates = normalize(raw)

    msg = f"[FIND] Loaded {len(leads)} leads from {input_path}."
    if duplicates:
        msg += f" {duplicates} duplicate(s) removed."
    print(msg)

    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(leads, f, indent=2)
        print(f"[FIND] Saved to {output_path}")

    return leads


def main():
    parser = argparse.ArgumentParser(description="Load and normalize a CSV of leads into JSON.")
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    parser.add_argument("--output", help="Path to save normalized JSON (optional; prints to stdout if omitted)")
    args = parser.parse_args()

    leads = run(args.input, args.output)

    if not args.output:
        print(json.dumps(leads, indent=2))


if __name__ == "__main__":
    main()
