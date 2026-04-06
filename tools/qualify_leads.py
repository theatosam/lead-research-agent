"""
qualify_leads.py — Score leads against an ICP using Claude Haiku in batches.

Usage:
    python tools/qualify_leads.py --input output/leads_normalized.json --icp workflows/qualify.md
    python tools/qualify_leads.py --input output/leads_normalized.json --icp workflows/qualify.md \
        --output output/leads_qualified.json --threshold 45

Importable function:
    from tools.qualify_leads import run
"""

import argparse
import json
import sys
import time
from pathlib import Path

import anthropic
from dotenv import load_dotenv

load_dotenv()

BATCH_SIZE = 10
MODEL = "claude-haiku-4-5-20251001"


def load_icp(icp_path: str) -> str:
    path = Path(icp_path)
    if not path.exists():
        print(f"[QUALIFY] ERROR: ICP file not found at {icp_path}", file=sys.stderr)
        sys.exit(1)
    return path.read_text(encoding="utf-8")


def build_system_prompt(icp_text: str) -> str:
    return f"""You are an ICP qualification engine for an AI agent developer. Your job is to score B2B leads against the ideal client profile below.

{icp_text}

Return ONLY a valid JSON array. One object per lead in the same order as the input. No explanation, no markdown, no text outside the JSON array."""


def build_user_prompt(batch: list[dict], offset: int) -> str:
    leads_input = [
        {
            "index": offset + i,
            "company": lead.get("company", ""),
            "role": lead.get("role", ""),
            "industry": lead.get("industry", ""),
            "company_size": lead.get("company_size", 0),
            "notes": lead.get("notes", ""),
        }
        for i, lead in enumerate(batch)
    ]
    return f"""Score the following {len(batch)} leads. Return a JSON array with one object per lead in the same order.

Each object must have exactly these keys:
- "id": the lead's index value from the input (integer)
- "score": integer 0–100 based on the four ICP dimensions
- "tier": "HIGH" if score >= 70, "MED" if score >= 45, "LOW" if score < 45
- "reasoning": exactly 2 sentences. Sentence 1 states the primary fit signal or disqualifier, referencing specific details. Sentence 2 states the recommended next action in one of these forms: "Prioritize — [reason]." / "Pursue when [condition]." / "Disqualify — [reason]."

Leads:
{json.dumps(leads_input, indent=2)}"""


def fallback_results(batch: list[dict], offset: int, reason: str) -> list[dict]:
    """Return fallback scored entries for a failed batch."""
    return [
        {
            "id": offset + i,
            "score": 0,
            "tier": "LOW",
            "reasoning": f"Qualification failed — {reason}. Re-run this lead.",
            "qualified": False,
        }
        for i in range(len(batch))
    ]


def score_batch(
    client: anthropic.Anthropic,
    batch: list[dict],
    offset: int,
    icp_text: str,
    retried: bool = False,
) -> list[dict]:
    """Score a single batch. Returns list of score dicts."""
    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=2048,
            system=build_system_prompt(icp_text),
            messages=[{"role": "user", "content": build_user_prompt(batch, offset)}],
        )
        raw = response.content[0].text.strip()

        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]

        results = json.loads(raw)
        return results

    except anthropic.RateLimitError:
        if retried:
            print(f"[QUALIFY] ERROR: Rate limit hit twice on batch at offset {offset}. Using fallback.", file=sys.stderr)
            return fallback_results(batch, offset, "rate limit exceeded")
        print(f"[QUALIFY] Rate limit hit — waiting 60s before retry...", file=sys.stderr)
        time.sleep(60)
        return score_batch(client, batch, offset, icp_text, retried=True)

    except anthropic.APIError as e:
        print(f"[QUALIFY] ERROR: API error on batch at offset {offset}: {e}", file=sys.stderr)
        return fallback_results(batch, offset, f"API error: {e}")

    except json.JSONDecodeError as e:
        print(f"[QUALIFY] ERROR: JSON parse failure on batch at offset {offset}: {e}", file=sys.stderr)
        print(f"[QUALIFY] Raw response: {raw[:500]}", file=sys.stderr)
        return fallback_results(batch, offset, "JSON parse error")


def merge_scores(leads: list[dict], score_results: list[dict], threshold: int) -> list[dict]:
    """Merge scoring results back into lead dicts by index."""
    score_map = {r["id"]: r for r in score_results}
    enriched = []
    for i, lead in enumerate(leads):
        result = score_map.get(i)
        if result:
            score = result.get("score", 0)
            tier = result.get("tier", "LOW")
            enriched.append({
                **lead,
                "score": score,
                "tier": tier,
                "reasoning": result.get("reasoning", ""),
                "qualified": score >= threshold,
            })
        else:
            enriched.append({
                **lead,
                "score": 0,
                "tier": "LOW",
                "reasoning": "Qualification result missing — re-run this lead.",
                "qualified": False,
            })
    return enriched


def run(
    input_path: str,
    icp_path: str,
    output_path: str | None = None,
    threshold: int = 45,
) -> list[dict]:
    """Score all leads against the ICP. Returns enriched lead list."""
    with open(input_path, encoding="utf-8") as f:
        leads = json.load(f)

    icp_text = load_icp(icp_path)
    client = anthropic.Anthropic()

    batches = [leads[i : i + BATCH_SIZE] for i in range(0, len(leads), BATCH_SIZE)]
    all_scores = []

    for batch_num, batch in enumerate(batches, start=1):
        offset = (batch_num - 1) * BATCH_SIZE
        results = score_batch(client, batch, offset, icp_text)
        all_scores.extend(results)
        scored_count = min(batch_num * BATCH_SIZE, len(leads))
        print(f"[QUALIFY] Batch {batch_num}/{len(batches)} — {len(batch)} leads scored.")

    enriched = merge_scores(leads, all_scores, threshold)
    qualified_count = sum(1 for lead in enriched if lead["qualified"])
    print(f"[QUALIFY] Done. {qualified_count} qualified of {len(enriched)} (threshold: {threshold}).")

    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(enriched, f, indent=2)
        print(f"[QUALIFY] Saved to {output_path}")

    return enriched


def main():
    parser = argparse.ArgumentParser(description="Score leads against an ICP using Claude Haiku.")
    parser.add_argument("--input", required=True, help="Path to normalized leads JSON")
    parser.add_argument("--icp", required=True, help="Path to ICP definition markdown (workflows/qualify.md)")
    parser.add_argument("--output", help="Path to save qualified leads JSON (optional)")
    parser.add_argument("--threshold", type=int, default=45, help="Minimum score to mark a lead as qualified (default: 45)")
    args = parser.parse_args()

    enriched = run(args.input, args.icp, args.output, args.threshold)

    if not args.output:
        print(json.dumps(enriched, indent=2))


if __name__ == "__main__":
    main()
