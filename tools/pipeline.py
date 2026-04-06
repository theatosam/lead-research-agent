"""
pipeline.py — End-to-end orchestration: find → qualify → draft → export.

Usage:
    python tools/pipeline.py --input data/sample_leads.csv
    python tools/pipeline.py --input data/sample_leads.csv --icp workflows/qualify.md --threshold 45
    python tools/pipeline.py --input data/sample_leads.csv --skip-sheets

Importable function:
    from tools.pipeline import run
"""

import argparse
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def run(
    input_path: str,
    icp_path: str = "workflows/qualify.md",
    threshold: int = 45,
    output_dir: str = "output",
    skip_sheets: bool = False,
) -> dict:
    """
    Run the full lead research pipeline.

    Returns a summary dict with counts at each stage.
    """
    from tools.find_leads import run as find_run
    from tools.qualify_leads import run as qualify_run
    from tools.draft_outreach import run as draft_run

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    normalized_path = str(output / "leads_normalized.json")
    qualified_path = str(output / "leads_qualified.json")
    drafts_path = str(output / "leads_with_drafts.json")

    print(f"\n[PIPELINE] Starting — input: {input_path}, threshold: {threshold}")
    print(f"[PIPELINE] ICP: {icp_path} | Output dir: {output_dir}\n")

    # Step 1: Find
    print("─" * 50)
    try:
        leads = find_run(input_path, normalized_path)
    except SystemExit as e:
        print(f"\n[PIPELINE] Step 1 failed — find_leads exited with code {e.code}.", file=sys.stderr)
        sys.exit(1)

    total = len(leads)
    print(f"[PIPELINE] Step 1/4 complete — {total} leads loaded.\n")

    # Step 2: Qualify
    print("─" * 50)
    try:
        qualified_leads = qualify_run(normalized_path, icp_path, qualified_path, threshold)
    except SystemExit as e:
        print(f"\n[PIPELINE] Step 2 failed — qualify_leads exited with code {e.code}.", file=sys.stderr)
        sys.exit(1)

    qualified_count = sum(1 for lead in qualified_leads if lead.get("qualified"))
    print(f"[PIPELINE] Step 2/4 complete — {qualified_count}/{total} leads qualified.\n")

    # Step 3: Draft
    print("─" * 50)
    try:
        drafted_leads = draft_run(qualified_path, drafts_path)
    except SystemExit as e:
        print(f"\n[PIPELINE] Step 3 failed — draft_outreach exited with code {e.code}.", file=sys.stderr)
        sys.exit(1)

    draft_count = sum(
        1 for lead in drafted_leads
        if lead.get("qualified") and lead.get("draft_subject") and lead.get("draft_subject") != "DRAFT_FAILED"
    )
    print(f"[PIPELINE] Step 3/4 complete — {draft_count} drafts written.\n")

    # Step 4: Export to Sheets (optional)
    print("─" * 50)
    sheets_enabled = (
        not skip_sheets
        and os.getenv("GOOGLE_SHEET_ID")
        and os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")
    )

    if sheets_enabled:
        try:
            from tools.sheets_export import run as export_run
            export_run(drafts_path)
            print(f"[PIPELINE] Step 4/4 complete — Google Sheet updated.\n")
        except SystemExit as e:
            print(f"\n[PIPELINE] Step 4 failed — sheets_export exited with code {e.code}.", file=sys.stderr)
            print(f"[PIPELINE] Results are still available at: {drafts_path}", file=sys.stderr)
    else:
        if skip_sheets:
            reason = "--skip-sheets flag set"
        else:
            reason = "GOOGLE_SHEET_ID not configured in .env"
        print(f"[PIPELINE] Step 4/4 skipped — {reason}.")
        print(f"[PIPELINE] To export manually: python tools/sheets_export.py --input {drafts_path}\n")

    print("═" * 50)
    print(
        f"[PIPELINE] Done. {total} prospects → {qualified_count} qualified "
        f"→ {draft_count} drafts → {drafts_path}"
    )
    print("═" * 50)

    return {
        "total": total,
        "qualified": qualified_count,
        "drafted": draft_count,
        "output_file": drafts_path,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Run the full lead research pipeline: find → qualify → draft → export."
    )
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    parser.add_argument(
        "--icp",
        default="workflows/qualify.md",
        help="Path to ICP definition markdown (default: workflows/qualify.md)",
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=45,
        help="Minimum ICP score to qualify a lead (default: 45)",
    )
    parser.add_argument(
        "--output-dir",
        default="output",
        help="Directory for intermediate and final output files (default: output/)",
    )
    parser.add_argument(
        "--skip-sheets",
        action="store_true",
        help="Skip Google Sheets export even if credentials are configured",
    )
    args = parser.parse_args()

    run(
        input_path=args.input,
        icp_path=args.icp,
        threshold=args.threshold,
        output_dir=args.output_dir,
        skip_sheets=args.skip_sheets,
    )


if __name__ == "__main__":
    main()
