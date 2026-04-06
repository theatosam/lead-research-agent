"""
Generate individual step card images for Listing 1 gallery.
Creates one 1200x1200 image per step, fully readable.
Requires: playwright
"""

from pathlib import Path
from playwright.sync_api import sync_playwright

OUTPUT_DIR = Path(__file__).parent.parent / "assets" / "gallery" / "steps"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

STEPS = [
    {
        "number": "01",
        "label": "Step 01",
        "title": "DEFINE YOUR\nIDEAL CLIENT",
        "desc": "You provide your ICP — industry, company size, role, and the signals that matter. This becomes the agent's targeting spec.",
        "icon": """<svg width="80" height="80" viewBox="0 0 56 56" fill="none">
          <rect x="6" y="10" width="44" height="36" stroke="#C8391A" stroke-width="2" fill="none"/>
          <rect x="14" y="20" width="12" height="3" fill="#C4C0B8"/>
          <rect x="14" y="27" width="28" height="3" fill="#C4C0B8"/>
          <rect x="14" y="34" width="20" height="3" fill="#C4C0B8"/>
        </svg>""",
        "accent": False,
    },
    {
        "number": "02",
        "label": "Step 02",
        "title": "AI REVIEWS YOUR\nPROSPECT LIST",
        "desc": "The agent reviews each prospect in your list and scores them against your criteria. No manual sorting needed.",
        "icon": """<svg width="80" height="80" viewBox="0 0 56 56" fill="none">
          <circle cx="24" cy="24" r="14" stroke="#C4C0B8" stroke-width="2" fill="none"/>
          <path d="M34 34L48 48" stroke="#C8391A" stroke-width="2"/>
        </svg>""",
        "accent": False,
    },
    {
        "number": "03",
        "label": "Step 03",
        "title": "QUALIFIES AGAINST\nYOUR CRITERIA",
        "desc": "Each prospect is scored against your ICP. Anyone who doesn't fit is filtered out. You only see leads worth your time.",
        "icon": """<svg width="80" height="80" viewBox="0 0 56 56" fill="none">
          <rect x="6" y="6" width="44" height="44" stroke="#C4C0B8" stroke-width="2" fill="none"/>
          <path d="M16 28L24 36L40 20" stroke="#C8391A" stroke-width="2.5"/>
        </svg>""",
        "accent": False,
    },
    {
        "number": "04",
        "label": "Step 04",
        "title": "DRAFTS PERSONALISED\nOUTREACH",
        "desc": "For every qualified lead, the agent writes a personalised message referencing their specific situation. Not a template blast.",
        "icon": """<svg width="80" height="80" viewBox="0 0 56 56" fill="none">
          <path d="M8 14H48M8 14V42H48V14" stroke="#C4C0B8" stroke-width="2" fill="none"/>
          <path d="M8 14L28 30L48 14" stroke="#C8391A" stroke-width="2"/>
        </svg>""",
        "accent": False,
    },
    {
        "number": "05",
        "label": "Output",
        "title": "LEADS + DRAFTS\nDELIVERED",
        "desc": "A clean list of qualified leads, each with a personalised draft ready to review, approve, and send.",
        "icon": """<svg width="80" height="80" viewBox="0 0 56 56" fill="none">
          <rect x="6" y="8" width="44" height="40" stroke="#C8391A" stroke-width="2" fill="none"/>
          <rect x="14" y="18" width="8" height="8" fill="rgba(200,57,26,0.25)" stroke="#C8391A" stroke-width="1.5"/>
          <rect x="28" y="20" width="16" height="3" fill="#C4C0B8"/>
          <rect x="28" y="25" width="10" height="2" fill="#6B6660"/>
          <rect x="14" y="32" width="8" height="8" fill="rgba(200,57,26,0.25)" stroke="#C8391A" stroke-width="1.5"/>
          <rect x="28" y="34" width="16" height="3" fill="#C4C0B8"/>
          <rect x="28" y="39" width="10" height="2" fill="#6B6660"/>
        </svg>""",
        "accent": True,
    },
]


def build_html(step, index, total):
    title_color = "#C8391A" if step["accent"] else "#F5F2ED"
    border_color = "rgba(200,57,26,0.4)" if step["accent"] else "rgba(255,255,255,0.08)"
    title_lines = step["title"].replace("\n", "<br>")

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Mono:wght@300;400;500&family=Fraunces:ital,opsz,wght@1,9..144,300&display=swap" rel="stylesheet">
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    width: 1200px;
    height: 1200px;
    background: #0A0A0A;
    font-family: 'DM Mono', monospace;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    position: relative;
  }}
  .ember-bar {{
    position: absolute;
    left: 0; top: 0;
    width: 8px; height: 100%;
    background: #C8391A;
  }}
  .top-tag {{
    position: absolute;
    top: 56px; left: 72px;
    font-size: 14px;
    font-weight: 500;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: #C8391A;
  }}
  .progress {{
    position: absolute;
    top: 56px; right: 72px;
    font-size: 14px;
    font-weight: 500;
    letter-spacing: 0.15em;
    color: #3E3B38;
  }}
  .card {{
    width: 920px;
    background: #111111;
    border: 1px solid {border_color};
    padding: 72px 80px 64px;
    position: relative;
  }}
  .step-number {{
    font-family: 'Bebas Neue', sans-serif;
    font-size: 180px;
    color: rgba(200,57,26,0.08);
    line-height: 1;
    position: absolute;
    top: 16px; right: 32px;
    user-select: none;
  }}
  .step-label {{
    font-size: 13px;
    font-weight: 500;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: #6B6660;
    margin-bottom: 28px;
  }}
  .icon {{ margin-bottom: 36px; }}
  .step-title {{
    font-family: 'Bebas Neue', sans-serif;
    font-size: 88px;
    color: {title_color};
    line-height: 1.0;
    letter-spacing: 0.02em;
    margin-bottom: 40px;
  }}
  .step-desc {{
    font-size: 22px;
    font-weight: 300;
    color: #C4C0B8;
    line-height: 1.75;
    max-width: 680px;
  }}
  .bottom-bar {{
    position: absolute;
    bottom: 56px;
    left: 72px; right: 72px;
    display: flex;
    align-items: center;
    gap: 16px;
  }}
  .dot {{
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #2E2B28;
  }}
  .dot.active {{ background: #C8391A; }}
  .brand {{
    margin-left: auto;
    font-size: 12px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #3E3B38;
  }}
</style>
</head>
<body>
<div class="ember-bar"></div>
<div class="top-tag">AI Lead Research Agent</div>
<div class="progress">{index + 1} / {total}</div>

<div class="card">
  <div class="step-number">{step["number"]}</div>
  <div class="step-label">{step["label"]}</div>
  <div class="icon">{step["icon"]}</div>
  <div class="step-title">{title_lines}</div>
  <div class="step-desc">{step["desc"]}</div>
</div>

<div class="bottom-bar">
  {''.join(f'<div class="dot{"  active" if i == index else ""}"></div>' for i in range(total))}
  <div class="brand">Lead Capture Agent</div>
</div>

</body>
</html>"""


BEFORE_AFTER_HTML = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Mono:wght@300;400;500&family=Fraunces:ital,opsz,wght@1,9..144,300&display=swap" rel="stylesheet">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    width: 1200px;
    height: 1200px;
    background: #0A0A0A;
    font-family: 'DM Mono', monospace;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    position: relative;
  }
  .ember-bar {
    position: absolute;
    left: 0; top: 0;
    width: 8px; height: 100%;
    background: #C8391A;
  }
  .top-tag {
    position: absolute;
    top: 56px; left: 72px;
    font-size: 14px;
    font-weight: 500;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: #C8391A;
  }
  .progress {
    position: absolute;
    top: 56px; right: 72px;
    font-size: 14px;
    font-weight: 500;
    letter-spacing: 0.15em;
    color: #3E3B38;
  }
  .headline {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 72px;
    color: #F5F2ED;
    letter-spacing: 0.04em;
    margin-bottom: 56px;
    text-align: center;
  }
  .panels {
    display: flex;
    flex-direction: column;
    gap: 24px;
    width: 920px;
  }
  .panel {
    padding: 48px 56px;
    border: 1px solid rgba(255,255,255,0.07);
    background: #111111;
  }
  .panel.before { border-left: 6px solid #3E3B38; }
  .panel.after  { border-left: 6px solid #C8391A; background: #130C0A; }
  .panel-label {
    font-size: 13px;
    font-weight: 500;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    margin-bottom: 20px;
  }
  .panel.before .panel-label { color: #6B6660; }
  .panel.after  .panel-label { color: #C8391A; }
  .panel-text {
    font-size: 26px;
    font-weight: 300;
    color: #C4C0B8;
    line-height: 1.65;
  }
  .panel-text strong {
    color: #F5F2ED;
    font-weight: 400;
  }
  .panel.after .panel-text strong { color: #C8391A; }
  .bottom-bar {
    position: absolute;
    bottom: 56px;
    left: 72px; right: 72px;
    display: flex;
    align-items: center;
    gap: 16px;
  }
  .dot { width: 8px; height: 8px; border-radius: 50%; background: #2E2B28; }
  .dot.active { background: #C8391A; }
  .brand {
    margin-left: auto;
    font-size: 12px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #3E3B38;
  }
</style>
</head>
<body>
<div class="ember-bar"></div>
<div class="top-tag">AI Lead Research Agent</div>
<div class="progress">6 / 6</div>

<div class="headline">3 HOURS VS 15 MINUTES</div>

<div class="panels">
  <div class="panel before">
    <div class="panel-label">Before</div>
    <div class="panel-text">
      Hours spent manually sorting through prospects<br>
      Inconsistent qualification criteria<br>
      Generic copy paste outreach<br>
      Good contacts missed or forgotten
    </div>
  </div>
  <div class="panel after">
    <div class="panel-label">After</div>
    <div class="panel-text">
      <strong>Every contact scored automatically</strong> against your criteria<br>
      Consistent qualification every time<br>
      Personalised email drafted for each qualified contact<br>
      Full results exported and ready to action
    </div>
  </div>
</div>

<div class="bottom-bar">
  <div class="dot"></div>
  <div class="dot"></div>
  <div class="dot"></div>
  <div class="dot"></div>
  <div class="dot"></div>
  <div class="dot active"></div>
  <div class="brand">Lead Capture Agent</div>
</div>

</body>
</html>"""


TOTAL = len(STEPS) + 1  # 5 steps + 1 before/after


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1200, "height": 1200})

        for i, step in enumerate(STEPS):
            html = build_html(step, i, TOTAL)
            page.set_content(html, wait_until="networkidle")
            page.wait_for_timeout(1500)

            out_path = OUTPUT_DIR / f"step-{step['number']}.jpg"
            page.screenshot(path=str(out_path), type="jpeg", quality=92)
            print(f"[OK] {out_path.name}")

        # Before/After closing card
        page.set_content(BEFORE_AFTER_HTML, wait_until="networkidle")
        page.wait_for_timeout(1500)
        out_path = OUTPUT_DIR / "step-06-before-after.jpg"
        page.screenshot(path=str(out_path), type="jpeg", quality=92)
        print(f"[OK] {out_path.name}")

        browser.close()
    print(f"\nAll {TOTAL} cards saved to assets/gallery/steps/")


if __name__ == "__main__":
    main()
