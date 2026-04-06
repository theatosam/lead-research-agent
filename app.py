"""
app.py — Lead Research Agent web dashboard.

Routes:
    GET  /        → configure page (upload CSV, set threshold)
    GET  /sample  → download sample CSV
    POST /run     → SSE stream: runs pipeline, yields progress + final results JSON
    POST /export  → push results to Google Sheets, returns status JSON
"""

import io
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, Response, jsonify, render_template, request, send_file

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "lead-research-dev-key")

# Ensure tools/ is importable
sys.path.insert(0, str(Path(__file__).parent))


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/sample")
def sample():
    sample_path = Path("data/sample_leads.csv")
    if not sample_path.exists():
        return "Sample file not found", 404
    return send_file(
        str(sample_path.resolve()),
        mimetype="text/csv",
        as_attachment=True,
        download_name="sample_leads.csv",
    )


@app.route("/run", methods=["POST"])
def run():
    """SSE endpoint. Streams pipeline progress then emits final results."""
    csv_file = request.files.get("csv")
    threshold = int(request.form.get("threshold", 45))

    if not csv_file or csv_file.filename == "":
        return jsonify({"error": "No CSV file uploaded"}), 400

    csv_bytes = csv_file.read()

    def generate():
        try:
            yield _sse({"type": "progress", "step": "start", "message": "Starting pipeline...", "pct": 0})

            # --- Step 1: Find ---
            from tools.find_leads import load_csv, normalize

            try:
                raw = load_csv(io.StringIO(csv_bytes.decode("utf-8")))
                leads, dupes = normalize(raw)
            except SystemExit:
                yield _sse({"type": "error", "message": "CSV validation failed — check your column headers."})
                return

            total = len(leads)
            yield _sse({
                "type": "progress", "step": "find",
                "message": f"Loaded {total} leads" + (f" ({dupes} duplicates removed)" if dupes else ""),
                "pct": 10,
            })

            # --- Step 2: Qualify ---
            import anthropic as _anthropic
            from tools.qualify_leads import load_icp, score_batch, merge_scores

            icp_path = Path("workflows/qualify.md")
            if not icp_path.exists():
                yield _sse({"type": "error", "message": "ICP file not found at workflows/qualify.md"})
                return

            icp_text = load_icp(str(icp_path))
            client = _anthropic.Anthropic()
            batch_size = 10
            batches = [leads[i: i + batch_size] for i in range(0, len(leads), batch_size)]
            all_scores = []

            for i, batch in enumerate(batches):
                results = score_batch(client, batch, i * batch_size, icp_text)
                all_scores.extend(results)
                pct = 10 + int(((i + 1) / len(batches)) * 40)
                yield _sse({
                    "type": "progress", "step": "qualify",
                    "message": f"Qualifying batch {i + 1}/{len(batches)}",
                    "pct": pct,
                })

            qualified_leads = merge_scores(leads, all_scores, threshold)
            qualified_count = sum(1 for l in qualified_leads if l["qualified"])
            yield _sse({
                "type": "progress", "step": "qualify",
                "message": f"{qualified_count} of {total} leads qualified",
                "pct": 50,
            })

            # --- Step 3: Draft ---
            from tools.draft_outreach import draft_one

            drafted_count = 0
            to_draft = [l for l in qualified_leads if l["qualified"]]

            for lead in qualified_leads:
                if not lead.get("qualified"):
                    continue
                drafted_count += 1
                subject, body = draft_one(client, lead)
                lead["draft_subject"] = subject
                lead["draft_body"] = body
                pct = 50 + int((drafted_count / max(len(to_draft), 1)) * 45)
                yield _sse({
                    "type": "progress", "step": "draft",
                    "message": f"Drafting {drafted_count}/{len(to_draft)} — {lead.get('company')}",
                    "pct": pct,
                })

            draft_count = sum(
                1 for l in qualified_leads
                if l.get("qualified") and l.get("draft_subject") and l.get("draft_subject") != "DRAFT_FAILED"
            )

            # Compute time saved: 15 min per qualified lead
            time_saved = round((qualified_count * 15) / 60, 1)

            stats = {
                "total": total,
                "qualified": qualified_count,
                "drafted": draft_count,
                "time_saved": time_saved,
            }

            yield _sse({"type": "progress", "step": "done", "message": "Complete", "pct": 100})
            yield _sse({"type": "done", "leads": qualified_leads, "stats": stats})

        except Exception as e:
            yield _sse({"type": "error", "message": f"Pipeline error: {str(e)}"})

    return Response(generate(), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.route("/export", methods=["POST"])
def export():
    """Accept leads JSON, push to Google Sheets."""
    data = request.get_json()
    if not data or "leads" not in data:
        return jsonify({"error": "No leads provided"}), 400

    sheet_id = os.getenv("GOOGLE_SHEET_ID")
    if not sheet_id:
        return jsonify({"error": "GOOGLE_SHEET_ID is not configured on this server."}), 400

    leads = data["leads"]

    # Write to a temp file-like path for sheets_export
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as tmp:
        json.dump(leads, tmp)
        tmp_path = tmp.name

    try:
        from tools.sheets_export import run as export_run
        export_run(tmp_path)
        return jsonify({"ok": True, "message": f"Exported {len(leads)} leads to Google Sheets."})
    except SystemExit as e:
        return jsonify({"error": f"Export failed (exit {e.code}). Check server logs."}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        Path(tmp_path).unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _sse(data: dict) -> str:
    return f"data: {json.dumps(data)}\n\n"


# ---------------------------------------------------------------------------
# Dev server entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True, port=5000, threaded=True)
