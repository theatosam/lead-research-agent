# Lead Research Agent

An AI agent that takes a list of B2B prospects, scores each one against your ideal client profile, and generates a personalized outreach email for every qualified lead — ready to review and send.

Built with Python and Claude AI. Output goes to a Google Sheet and local JSON files.

---

## What You Get

- **Qualified lead list** — every prospect scored 0–100 against your ICP with a tier (HIGH / MED / LOW)
- **Reasoning per lead** — two sentences explaining why the lead fits or doesn't, and what to do next
- **Personalized outreach drafts** — one email per qualified lead, written by Claude Sonnet with company-specific hooks, not generic templates
- **Google Sheet export** — all results in a structured CRM-ready spreadsheet with 11 columns
- **Full audit trail** — intermediate JSON files saved at every stage so you can re-run any step independently

---

## How It Works

```
Your CSV of prospects
        ↓
Step 1: Load + validate (find_leads.py)
        ↓
Step 2: Score against ICP — Claude Haiku (qualify_leads.py)
        ↓
Step 3: Draft personalized outreach — Claude Sonnet (draft_outreach.py)
        ↓
Step 4: Export to Google Sheet (sheets_export.py)
```

The ICP scoring criteria live in `workflows/qualify.md` — a plain Markdown file you can edit without touching any Python. Change the ICP, re-run Step 2, get new scores.

The qualification reasoning flows directly into the draft prompt. This is not a coincidence — it is the design. Claude's diagnosis of why a lead fits becomes the opening hook of the outreach email.

---

## Setup

**Requirements**: Python 3.10+, an [Anthropic API key](https://console.anthropic.com), and optionally a Google service account for Sheets export.

```bash
# 1. Clone the repo
git clone <repo-url>
cd lead-research-agent

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure credentials
cp .env.example .env
# Open .env and add your ANTHROPIC_API_KEY
```

For Google Sheets export, add your `GOOGLE_SHEET_ID` and `GOOGLE_CREDENTIALS_PATH` to `.env`. See [Google Sheets setup](#google-sheets-setup) below.

---

## Quickstart

Run the full pipeline with the included sample data:

```bash
python tools/pipeline.py --input data/sample_leads.csv
```

Output files appear in `output/`:
- `leads_normalized.json` — 25 cleaned leads
- `leads_qualified.json` — all 25 leads with scores, tiers, and reasoning
- `leads_with_drafts.json` — qualified leads with draft subject + body

To skip the Google Sheets step:

```bash
python tools/pipeline.py --input data/sample_leads.csv --skip-sheets
```

---

## Using Your Own Leads

Prepare a CSV with these 7 columns:

| Column | Description |
|--------|-------------|
| `name` | Contact full name |
| `company` | Company name |
| `role` | Job title |
| `industry` | Industry or sector |
| `email` | Contact email |
| `company_size` | Number of employees |
| `notes` | Free-text — job postings, pain signals, tech stack, LinkedIn activity |

The `notes` column is the most important. The more signal you include (job postings, process descriptions, pain language), the better the scoring and outreach quality.

```bash
python tools/pipeline.py --input data/your_leads.csv
```

---

## Changing Who the Agent Targets

Open `workflows/qualify.md`. This file defines the four scoring dimensions the agent uses to evaluate leads. Edit the descriptions to match your ideal client — no Python required.

To raise the qualification threshold (more selective):

```bash
python tools/pipeline.py --input data/sample_leads.csv --threshold 60
```

---

## Running Individual Steps

Each tool works standalone:

```bash
# Load and validate leads
python tools/find_leads.py --input data/sample_leads.csv --output output/leads_normalized.json

# Score leads against ICP
python tools/qualify_leads.py --input output/leads_normalized.json --icp workflows/qualify.md --output output/leads_qualified.json

# Draft outreach for qualified leads
python tools/draft_outreach.py --input output/leads_qualified.json --output output/leads_with_drafts.json

# Export to Google Sheets
python tools/sheets_export.py --input output/leads_with_drafts.json
```

---

## Output Format

### Google Sheet columns

| Column | Description |
|--------|-------------|
| Company | Company name |
| Contact | Prospect name |
| Role | Job title |
| Industry | Industry |
| ICP Score | 0–100 qualification score |
| Tier | HIGH (70+) / MED (45–69) / LOW (<45) |
| Reasoning | 2-sentence ICP diagnosis + next action |
| Email | Contact email |
| Subject | Draft email subject line |
| Draft Body | Full personalized email body |
| Status | Draft ready / Below threshold / Draft failed |

### Sample lead output

```json
{
  "name": "Ryan Mitchell",
  "company": "Apex Consulting",
  "role": "Founder & CEO",
  "industry": "B2B Services",
  "score": 94,
  "tier": "HIGH",
  "reasoning": "Apex Consulting is a 14-person founder-led firm with a confirmed manual intake process visible in their LinkedIn job postings. Prioritize — the Founder & CEO has direct buying authority and the ops pain is confirmed.",
  "qualified": true,
  "draft_subject": "Question about your client intake process",
  "draft_body": "Hi Ryan,\n\nApex fits the profile closely — founder-led, scaling advisory practice, at the stage where intake processes typically become a bottleneck.\n\nMost consulting firms at your stage hit the same wall: client intake managed via email eats 30–40% of a founder's week. I build AI agent systems that handle the full intake flow — qualification, onboarding sequences, document collection — without you managing any of it.\n\nWould it be useful to see a quick sketch of how this would work for Apex specifically?\n\nAto"
}
```

---

## Google Sheets Setup

1. Create a [Google Cloud service account](https://console.cloud.google.com/iam-admin/serviceaccounts)
2. Enable the Google Sheets API and Google Drive API for your project
3. Download the service account key as JSON and save it as `credentials.json` in the project root
4. Share your target Google Sheet with the service account email (editor access)
5. Add the Sheet ID to `.env`:

```
GOOGLE_SHEET_ID=1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms
GOOGLE_CREDENTIALS_PATH=credentials.json
```

The Sheet ID is the long string in the URL between `/d/` and `/edit`.

---

## Architecture

This project follows the WAT pattern (Workflows → Agent → Tools):

**Workflows** (`workflows/`) define the rules — the ICP scoring criteria, outreach tone guidelines, and pipeline SOPs. These are plain Markdown files, editable without code.

**Tools** (`tools/`) are deterministic Python scripts — one file per task. Each tool is independently testable and runnable. They do not make judgment calls; they execute defined logic.

**The agent loop** is visible in how `qualify_leads.py` passes its `reasoning` output forward to `draft_outreach.py`. The scoring analysis informs the personalization. This is what separates a pipeline (scripts in sequence) from an agent (where one step's output improves the next).

---

## Project Structure

```
tools/              Python scripts — one file per task
workflows/          Markdown SOPs — the agent's operating rules
data/               Lead input files
output/             Generated results (gitignored except .gitkeep)
decisions/          Architectural decision log
docs/               Client handover documentation
```
