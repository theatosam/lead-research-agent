# Workflow: Pipeline

## Objective

Run the full lead research pipeline from a raw CSV to qualified leads with personalized outreach drafts and an optional Google Sheet export. This document covers how to run it, what it produces at each stage, and how to recover from failures.

## Overview

```
data/sample_leads.csv
        ↓
[Step 1: find_leads]     → Validate, normalize, deduplicate
        ↓ output/leads_normalized.json
[Step 2: qualify_leads]  → Score against ICP using Claude Haiku
        ↓ output/leads_qualified.json
[Step 3: draft_outreach] → Generate personalized emails using Claude Sonnet
        ↓ output/leads_with_drafts.json
[Step 4: sheets_export]  → Push all results to Google Sheet (optional)
        ↓ Google Sheet: "Lead Research — YYYY-MM-DD"
```

## How to Run

### Full pipeline (recommended)

```bash
python tools/pipeline.py --input data/sample_leads.csv
```

This runs all four steps. Google Sheets export runs automatically if `GOOGLE_SHEET_ID` is set in `.env`.

### Full pipeline without Sheets export

```bash
python tools/pipeline.py --input data/sample_leads.csv --skip-sheets
```

Results are saved to `output/leads_with_drafts.json`.

### With a custom ICP or threshold

```bash
python tools/pipeline.py --input data/my_leads.csv --icp workflows/qualify.md --threshold 55
```

Raise the threshold to narrow down to only strong matches. Lower it to cast a wider net.

## Running Individual Steps

Each tool can be run standalone. Useful when you want to re-run a specific step without redoing the whole pipeline.

### Step 1 — Load leads

```bash
python tools/find_leads.py --input data/sample_leads.csv --output output/leads_normalized.json
```

### Step 2 — Qualify

```bash
python tools/qualify_leads.py \
  --input output/leads_normalized.json \
  --icp workflows/qualify.md \
  --output output/leads_qualified.json \
  --threshold 45
```

### Step 3 — Draft outreach

```bash
python tools/draft_outreach.py \
  --input output/leads_qualified.json \
  --output output/leads_with_drafts.json
```

### Step 4 — Export to Sheets

```bash
python tools/sheets_export.py --input output/leads_with_drafts.json
```

## Inputs and Outputs at Each Step

| Step | Input | Output |
|------|-------|--------|
| find_leads | CSV with 7 columns | `leads_normalized.json` — array of lead objects |
| qualify_leads | `leads_normalized.json` | `leads_qualified.json` — leads + score, tier, reasoning, qualified |
| draft_outreach | `leads_qualified.json` | `leads_with_drafts.json` — qualified leads + draft_subject, draft_body |
| sheets_export | `leads_with_drafts.json` | Google Sheet tab with 11 columns |

## Environment Setup

Copy `.env.example` to `.env` and fill in:

```
ANTHROPIC_API_KEY=sk-ant-...           # Required for qualify and draft steps
GOOGLE_SHEET_ID=...                    # Required for Sheets export
GOOGLE_CREDENTIALS_PATH=credentials.json  # Required for Sheets export
```

The pipeline runs without Google credentials — Sheets export is skipped automatically if `GOOGLE_SHEET_ID` is not set.

## Troubleshooting

**API key not set**: `qualify_leads.py` will fail with an authentication error from the Anthropic SDK. Check that `ANTHROPIC_API_KEY` is set in `.env` and the `.env` file is in the project root.

**All leads score LOW**: The `notes` column in your CSV is too thin. The scoring agent needs visible signals — job postings, tech stack mentions, explicit pain language. Enrich the notes before re-running Step 2.

**Sheets export fails at auth**: Verify that `GOOGLE_CREDENTIALS_PATH` points to a valid service account JSON file, and that the service account has editor access to the target spreadsheet.

**A draft says DRAFT_FAILED**: Re-run Step 3. The pipeline continues past API errors, so you can re-run `draft_outreach.py` to attempt all qualified leads again. Previously succeeded drafts will be overwritten with fresh ones (which is fine — Sonnet produces consistent quality).

**Pipeline exits at Step 1 with "Missing required column"**: Your CSV is missing one of the 7 required columns. Check the header row against the column list in `workflows/find.md`.

**Rate limit on qualify**: The tool automatically waits 60 seconds and retries once. If you are running large batches (200+ leads), consider adding a `--batch-size` argument to slow down the requests.
