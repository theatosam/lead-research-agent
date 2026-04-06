# Decision Log

Format: `[YYYY-MM-DD] DECISION: ... | REASONING: ... | CONTEXT: ...`

---

[2026-04-06] DECISION: Use Claude Haiku (claude-haiku-4-5-20251001) for batch lead qualification | REASONING: Haiku is significantly cheaper than Sonnet for bulk structured tasks; qualification is a scoring exercise against explicit criteria, not a reasoning-heavy task; batching 10 leads per call reduces total API calls to 3 for 25 leads | CONTEXT: Portfolio project — cost-efficiency signals professional judgment to clients reviewing the code; demonstrates model selection awareness rather than defaulting to the most capable model for every task

[2026-04-06] DECISION: Inject workflows/qualify.md verbatim into every Haiku qualification prompt | REASONING: Avoids hardcoding ICP logic in Python; makes the scoring criteria configurable by editing a Markdown file without touching code; aligns with the WAT architecture where Workflows are the source of truth for agent behavior | CONTEXT: Key portfolio differentiator — a client reviewing the project can update their ICP by editing qualify.md without needing a developer; the ICP is a business concern, not a code concern

[2026-04-06] DECISION: Feed qualify_leads reasoning output forward into draft_outreach prompt context | REASONING: Creates a genuine agent loop — the ICP diagnosis from step 2 directly informs the personalization in step 3, producing higher-quality drafts than if draft_outreach.py read raw lead data alone; the reasoning field contains specific fit signals that become the hook angle in outreach | CONTEXT: This is the architectural decision that separates a pipeline (sequence of scripts) from an agent (where outputs of one step improve the next); visible in draft_outreach.py as a concrete design choice that reviewers will notice

[2026-04-06] DECISION: Each tool is both importable as a Python module AND runnable as a standalone CLI script | REASONING: pipeline.py imports tool functions directly (faster, no subprocess overhead, cleaner stack traces); each tool can still be run independently for debugging or partial re-runs; enforced by the if __name__ == "__main__" pattern in each tool file | CONTEXT: Portfolio code is reviewed — clean architecture matters as much as functionality; a client debugging a failed draft step should be able to re-run just draft_outreach.py without running the full pipeline
