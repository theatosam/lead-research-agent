# Workflow: Find Leads

## Objective

Load a CSV file of B2B prospects and normalize it into a clean JSON list that the qualify and draft tools can consume. This step validates the data format, handles edge cases, and produces a consistent output regardless of the lead source.

## What Is a Lead?

A lead is a named contact at a named company with enough context to score. At minimum, we need a name, company, role, and some notes about the company. Email and company size are used for scoring and outreach but are not blocking — the pipeline will continue without them.

## Required CSV Columns

| Column | Type | Description |
|--------|------|-------------|
| `name` | string | Full name of the contact |
| `company` | string | Company name |
| `role` | string | Job title or role |
| `industry` | string | Industry or sector |
| `email` | string | Contact email address |
| `company_size` | integer | Number of employees (approximate is fine) |
| `notes` | string | Free-text description — recent activity, job postings, pain signals, tech stack |

The `notes` column is the most important input for qualification scoring. A lead with a thin notes field will score lower because the agent has less signal to work with. Enrich notes with anything publicly visible: LinkedIn posts, job postings, website copy, Upwork postings.

## How to Get Leads

**Apollo.io free tier**: Search by industry, company size, and title. Export as CSV. Rename columns to match the schema above if needed.

**LinkedIn Sales Navigator export**: Export search results. Add a `notes` column manually with relevant signals before running.

**Manual list**: Any spreadsheet works. Add the 7 columns and fill in what you know. Even a company name, role, and a sentence of notes is enough to run.

**Column name mismatch**: If your export uses different column names (e.g., `first_name` / `last_name` instead of `name`), combine them in a spreadsheet before passing to the tool.

## How to Run

```bash
# Basic — prints normalized JSON to stdout
python tools/find_leads.py --input data/sample_leads.csv

# Save output to file (recommended before qualifying)
python tools/find_leads.py --input data/sample_leads.csv --output output/leads_normalized.json
```

## Output Format

```json
[
  {
    "name": "Ryan Mitchell",
    "company": "Apex Consulting",
    "role": "Founder & CEO",
    "industry": "B2B Services",
    "email": "ryan@apexconsulting.com",
    "company_size": 14,
    "notes": "Founder-led consulting firm..."
  },
  ...
]
```

## Edge Cases

**Missing required column**: The tool exits with code 1 and names the missing column. Fix the CSV header and re-run.

**`company_size` is blank or non-numeric**: Set to 0 and a warning is printed to stderr. The lead is kept. Scoring will be conservative on the size dimension.

**`email` is blank**: The lead is kept. Qualification still runs. The Google Sheet export will show a blank email cell. Fix before sending outreach.

**Duplicate entries**: Detected by matching `company` + `email` (case-insensitive). First occurrence is kept, subsequent duplicates are removed with a stderr warning. If two rows share the same company but different emails, both are kept.

**UTF-8 encoding issues**: The tool reads files as UTF-8. If your CSV was exported from Excel, save it as "CSV UTF-8 (comma delimited)" before running.
