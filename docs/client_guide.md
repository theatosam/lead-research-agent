# Lead Research Agent — Client Guide

**Prepared by Ato Sam**
Version 1.0

---

## What You Received

This package contains three things:

1. **The agent code** — a Python-based AI system that finds, scores, and drafts outreach for your target prospects
2. **Sample data** — 25 realistic test leads in `data/sample_leads.csv` so you can run the system immediately and see what it produces
3. **This guide** — step-by-step instructions for setup, operation, and customization

The system takes a CSV list of prospects, scores each one against your ideal client criteria, and writes a personalized cold email for every qualified lead. Results go into a Google Sheet and local files.

---

## Before You Start

You will need:

- **Python 3.10 or later** — download from [python.org](https://python.org) if you do not have it. To check your version: `python --version`
- **An Anthropic API key** — sign up at [console.anthropic.com](https://console.anthropic.com). The key looks like `sk-ant-...`. Keep this private.
- **Google Sheets access (optional)** — only needed if you want the results pushed to a spreadsheet automatically. See the Google Sheets section below if you want this.

---

## Installation

Run these commands in your terminal (Command Prompt on Windows, Terminal on Mac):

```bash
# Step 1: Go to the project folder
cd lead-research-agent

# Step 2: Install dependencies
pip install -r requirements.txt

# Step 3: Create your credentials file
# On Mac / Linux:
cp .env.example .env
# On Windows:
copy .env.example .env
```

Now open the `.env` file in any text editor and replace the placeholder with your actual Anthropic API key:

```
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

Save the file. You are ready to run.

---

## Running the Agent

To run the full pipeline with the sample data:

```bash
python tools/pipeline.py --input data/sample_leads.csv --skip-sheets
```

The `--skip-sheets` flag tells the agent to save results locally rather than to Google Sheets. You can remove this flag later once Sheets is configured.

You will see output like this in your terminal:

```
[PIPELINE] Starting — input: data/sample_leads.csv, threshold: 45

──────────────────────────────────────────────────
[FIND] Loaded 25 leads from data/sample_leads.csv.
[PIPELINE] Step 1/4 complete — 25 leads loaded.

──────────────────────────────────────────────────
[QUALIFY] Batch 1/3 — 10 leads scored.
[QUALIFY] Batch 2/3 — 10 leads scored.
[QUALIFY] Batch 3/3 — 5 leads scored.
[QUALIFY] Done. 17 qualified of 25 (threshold: 45).
[PIPELINE] Step 2/4 complete — 17/25 leads qualified.

──────────────────────────────────────────────────
[DRAFT] 1/17 — Apex Consulting (Ryan Mitchell) drafted.
[DRAFT] 2/17 — Clearpath Digital (Laura Bennett) drafted.
...
[DRAFT] Done. 17/17 drafts written successfully.
[PIPELINE] Step 3/4 complete — 17 drafts written.

══════════════════════════════════════════════════
[PIPELINE] Done. 25 prospects → 17 qualified → 17 drafts → output/leads_with_drafts.json
══════════════════════════════════════════════════
```

When it finishes, open `output/leads_with_drafts.json` to see the full results. Each lead has:
- A score (0–100)
- A tier (HIGH, MED, or LOW)
- A reasoning note explaining the score
- A draft subject line
- A draft email body

---

## Using Your Own Lead List

Create a spreadsheet with these 7 column headers (exact spelling matters):

| Column | What to put here |
|--------|-----------------|
| `name` | Contact's full name |
| `company` | Company name |
| `role` | Their job title |
| `industry` | Their industry (e.g. Digital Agency, SaaS, Logistics) |
| `email` | Their email address |
| `company_size` | Approximate number of employees |
| `notes` | Anything publicly visible about them — LinkedIn posts, job postings, website copy, pain signals |

Save it as a CSV file (File → Download → CSV in Google Sheets, or Save As → CSV in Excel).

Run the pipeline with your file:

```bash
python tools/pipeline.py --input data/your_leads.csv --skip-sheets
```

**A note on the notes column**: This is the single most important field for quality output. The AI uses the notes to understand why a lead fits and to write a personalized opening line. A lead with a thin notes field will score lower and get a less specific email. Even one sentence about what they do and how they work is better than nothing.

---

## Changing Who the Agent Targets

Open `workflows/qualify.md` in any text editor. This file defines the four criteria the agent uses to score leads:

1. **Operational Maturity** — how much evidence there is of manual processes
2. **Company Size Fit** — whether the company is the right size
3. **Industry and Role Fit** — whether the industry and contact role match
4. **Budget Signal** — evidence they have budget for tools

To change who the agent targets, edit the descriptions under each dimension. For example, if your target client is larger companies (50–200 employees instead of 10–100), update the Dimension 2 section to reflect that. Save the file. The next time you run the pipeline, the new criteria will be used automatically — no Python required.

---

## Understanding Your Results

### ICP Score (0–100)

The total score across the four dimensions. Higher is better.

- **70–100 (HIGH)**: Strong match. These leads have direct buying authority, visible pain, and budget signals. Prioritize these.
- **45–69 (MED)**: Partial match. Worth pursuing — some dimensions are weaker but the overall profile is viable.
- **Below 45 (LOW)**: Below threshold. The agent does not draft outreach for these leads. They appear in your results with a "Below threshold" status so you can see them.

### Reasoning

Two sentences per lead:
- Sentence 1: What makes this lead a strong or weak fit, with a specific reason
- Sentence 2: What you should do next (Prioritize now / Pursue when X / Disqualify because Y)

Example:
> "Apex Consulting is a 14-person founder-led firm with a confirmed manual intake process visible in their LinkedIn job postings. Prioritize — the Founder & CEO has direct buying authority and the ops pain is confirmed."

### Draft Subject and Body

Generated by Claude for each qualified lead. These are drafts — read them before sending. The opening line is written to hook on the most relevant thing about that specific company, not a generic template. Edit freely to match your voice.

### Status column (Google Sheet)

| Status | Meaning |
|--------|---------|
| Draft ready | Outreach has been written — review and send |
| Below threshold | Lead scored below 45 — not drafted |
| Draft failed | API error during drafting — re-run Step 3 |

---

## Setting Up Google Sheets Export

If you want results pushed to a Google Sheet automatically:

**Step 1**: Create a Google Cloud project at [console.cloud.google.com](https://console.cloud.google.com)

**Step 2**: Enable two APIs: **Google Sheets API** and **Google Drive API**

**Step 3**: Go to IAM & Admin → Service Accounts → Create Service Account. Give it a name (e.g. "lead-agent"). Download the key as JSON and save it as `credentials.json` in the project folder.

**Step 4**: Open your target Google Sheet. Click Share. Add the service account's email address (it looks like `name@project.iam.gserviceaccount.com`) with Editor access.

**Step 5**: Add these two lines to your `.env` file:

```
GOOGLE_SHEET_ID=your-sheet-id-here
GOOGLE_CREDENTIALS_PATH=credentials.json
```

The Sheet ID is the long string in the URL: `https://docs.google.com/spreadsheets/d/**THIS_PART**/edit`

**Step 6**: Run the pipeline without `--skip-sheets`:

```bash
python tools/pipeline.py --input data/sample_leads.csv
```

A new tab named "Lead Research — [today's date]" will appear in your spreadsheet with all results.

---

## Common Questions

**What if I do not have a Google Sheets account?**
Use the `--skip-sheets` flag. All results are saved to `output/leads_with_drafts.json` which you can open in any code editor, or convert to CSV by importing it into Google Sheets manually.

**What if a draft says DRAFT_FAILED?**
Re-run Step 3 alone:
```bash
python tools/draft_outreach.py --input output/leads_qualified.json --output output/leads_with_drafts.json
```
This will attempt to draft all qualified leads again. The failure is usually a temporary API issue.

**What if all my leads score LOW?**
The notes column is too thin. The agent needs visible signals to score well. Go back to your CSV, enrich the notes field with anything publicly available about each company — LinkedIn posts, job postings, website copy — and re-run from Step 2:
```bash
python tools/qualify_leads.py --input output/leads_normalized.json --icp workflows/qualify.md --output output/leads_qualified.json
```

**Can I change how selective the agent is?**
Yes. The default threshold is 45 — leads scoring below 45 are not drafted. Raise it to be more selective, lower it to capture more leads:
```bash
python tools/pipeline.py --input data/your_leads.csv --threshold 60
```

**How much does it cost to run?**
The qualify step uses Claude Haiku (inexpensive, batch processing). The draft step uses Claude Sonnet (higher quality, one call per qualified lead). For 25 leads, expect under $0.20 in total API costs. Larger batches scale linearly.

---

## Getting Support

Your purchase includes the number of revisions listed in your project tier. If you need changes to the ICP criteria, outreach tone, output format, or any other aspect of the system, get in touch:

**Ato Sam** — [Upwork profile link]

For a revision, describe what you want changed and include a few examples if possible. Most changes are a matter of editing `workflows/qualify.md` or updating the system prompt in `tools/draft_outreach.py`.
