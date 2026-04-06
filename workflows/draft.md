# Workflow: Draft Outreach

## Objective

Generate a personalized cold email for each qualified lead. The draft should read like a person wrote it for that specific company — not a template with names swapped in. The ICP reasoning from the qualification step is the primary input for personalization.

## What Makes a Good Draft

The email has four parts, each serving a specific purpose:

**1. Hook (1 sentence)**: Opens with something specific about the company or contact. The source is the `reasoning` field from the qualify step — it names the exact fit signal. Do not open with "I hope this finds you well," "I came across your profile," or any generic opener.

**2. Pain statement (1–2 sentences)**: Describes the problem we solve in terms the prospect recognizes. Use a concrete time estimate or number where possible ("30–40% of founder time," "6 hours every Monday," "recurring admin that should run automatically"). Do not be abstract.

**3. Capability statement (1–2 sentences)**: Names a specific process we can handle, not a vague offer. Examples: "lead qualification and intake," "client onboarding sequences," "weekly reporting that gets generated automatically." Do not say "I can help automate your business."

**4. Soft CTA (1 sentence)**: A question that opens a conversation without demanding a commitment. Examples: "Would it be useful to see how this could work for [Company]?" / "Does this match anything you're dealing with right now?" Do not say "hop on a call," "schedule a demo," or "let's connect."

## Tone

Direct. Peer-to-peer. Conversational. The prospect is a founder or ops executive — they get pitched every day. Write as if you are a competent person reaching out to an equal, not a salesperson running a sequence.

## Length

The email body must be under 150 words. Brevity signals respect for their time.

## Subject Line Rules

- Under 10 words
- No generic phrases like "Quick question" alone
- Do not use "automate" or "automation"
- Should hint at the specific angle in the email body

Good subject examples:
- "Question about your client intake process"
- "How Clearpath handles weekly reporting"
- "The ops bottleneck at your stage"

## How the Agent Loop Works

The qualify step produces a `reasoning` field with two sentences: a fit diagnosis and a next-action instruction. This field is injected directly into the draft prompt as the "primary hook source." The draft tool is explicitly told to anchor the first sentence of the email on that reasoning.

This is not a coincidence — it is the architectural decision that makes the drafts non-generic. The qualification analysis flows forward to improve the outreach.

## How to Run

```bash
# Draft outreach for all qualified leads
python tools/draft_outreach.py --input output/leads_qualified.json --output output/leads_with_drafts.json

# Print to stdout without saving
python tools/draft_outreach.py --input output/leads_qualified.json
```

## Output

Each qualified lead in the output JSON will have two additional fields:
- `draft_subject` — the email subject line
- `draft_body` — the email body as plain text

Unqualified leads pass through unchanged (no draft fields).

If a draft fails (API error, parse error), `draft_subject` will be `"DRAFT_FAILED"` and `draft_body` will contain a recovery instruction. Re-run the tool — it will attempt to draft all qualified leads again.

## Editing Drafts

Drafts are generated for review, not for immediate sending. Read each one before sending. Edit freely — the tone guidelines above are instructions to the agent, not constraints on you. If a draft misses the mark, the fastest fix is to enrich the `notes` field for that lead and re-run draft_outreach.py.
