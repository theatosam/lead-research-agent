"""
draft_outreach.py — Generate personalized cold email drafts per qualified lead using Claude Sonnet.

Usage:
    python tools/draft_outreach.py --input output/leads_qualified.json
    python tools/draft_outreach.py --input output/leads_qualified.json --output output/leads_with_drafts.json

Importable function:
    from tools.draft_outreach import run
"""

import argparse
import json
import sys
from pathlib import Path

import anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-sonnet-4-6"

SYSTEM_PROMPT = """You are a cold outreach copywriter for Ato Sam, an AI agent developer who builds automation systems for small businesses. Your job is to write a personalized cold email for one specific prospect.

STRICT RULES:
- The email body must be under 150 words (not counting "Hi {name}," or the sign-off).
- Do NOT use the word "automate" or "automation" in the subject line.
- Do NOT open with "I hope this finds you well" or any generic opener.
- Do NOT use phrases like "I came across your profile" or "I noticed you".
- The first sentence must reference something specific about the company or role from the context provided.
- Structure: specific hook (1 sentence) → pain statement (1–2 sentences, use a concrete number or time estimate if possible) → capability statement (1–2 sentences naming a specific process) → soft CTA (1 sentence question — not "hop on a call", not "schedule a demo").
- Sign off as: Ato
- Tone: direct, peer-to-peer, conversational. It should read like a person wrote it, not a template.

Return ONLY a JSON object with two keys:
- "subject": the email subject line (under 10 words, no generic phrases like "Quick question" alone)
- "body": the full email body as plain text, using double newlines between paragraphs"""


def build_user_prompt(lead: dict) -> str:
    return f"""Write a cold email for this prospect:

Company: {lead.get('company', '')}
Contact name: {lead.get('name', '')}
Role: {lead.get('role', '')}
Industry: {lead.get('industry', '')}
Company size: {lead.get('company_size', 0)} employees
ICP Score: {lead.get('score', 0)}/100 — {lead.get('tier', '')}
ICP Reasoning: {lead.get('reasoning', '')}
Notes: {lead.get('notes', '')}

The ICP Reasoning above is your primary hook source — it contains the specific fit signal that should anchor the first sentence of the email."""


def draft_one(client: anthropic.Anthropic, lead: dict) -> tuple[str, str]:
    """Draft subject + body for one lead. Returns (subject, body)."""
    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": build_user_prompt(lead)}],
        )
        raw = response.content[0].text.strip()

        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]

        result = json.loads(raw)
        return result.get("subject", ""), result.get("body", "")

    except anthropic.APIError as e:
        print(f"[DRAFT] ERROR: API error for {lead.get('company')}: {e}", file=sys.stderr)
        return "DRAFT_FAILED", "Draft generation failed — API error. Re-run this lead with: python tools/draft_outreach.py"

    except json.JSONDecodeError as e:
        print(f"[DRAFT] ERROR: JSON parse failure for {lead.get('company')}: {e}", file=sys.stderr)
        return "DRAFT_FAILED", "Draft generation failed — parse error. Re-run this lead with: python tools/draft_outreach.py"


def run(
    input_path: str,
    output_path: str | None = None,
) -> list[dict]:
    """Draft outreach for all qualified leads. Returns full lead list with drafts added."""
    with open(input_path, encoding="utf-8") as f:
        leads = json.load(f)

    qualified = [lead for lead in leads if lead.get("qualified")]
    total_qualified = len(qualified)

    if total_qualified == 0:
        print("[DRAFT] No qualified leads found. Adjust threshold or enrich your lead notes.")
        return leads

    client = anthropic.Anthropic()
    drafted_count = 0

    for lead in leads:
        if not lead.get("qualified"):
            continue

        drafted_count += 1
        subject, body = draft_one(client, lead)
        lead["draft_subject"] = subject
        lead["draft_body"] = body

        status = "drafted" if subject != "DRAFT_FAILED" else "FAILED"
        print(f"[DRAFT] {drafted_count}/{total_qualified} — {lead.get('company')} ({lead.get('name')}) {status}.")

    success_count = sum(
        1 for lead in leads
        if lead.get("qualified") and lead.get("draft_subject") and lead.get("draft_subject") != "DRAFT_FAILED"
    )
    print(f"[DRAFT] Done. {success_count}/{total_qualified} drafts written successfully.")

    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(leads, f, indent=2)
        print(f"[DRAFT] Saved to {output_path}")

    return leads


def main():
    parser = argparse.ArgumentParser(description="Generate personalized outreach drafts for qualified leads.")
    parser.add_argument("--input", required=True, help="Path to qualified leads JSON")
    parser.add_argument("--output", help="Path to save leads with drafts JSON (optional)")
    args = parser.parse_args()

    leads = run(args.input, args.output)

    if not args.output:
        print(json.dumps(leads, indent=2))


if __name__ == "__main__":
    main()
