"""
Generate individual step card images for Listing 1 gallery.
Creates one 1200x1200 image per step, fully readable.
Branded with the Autonomy Intelligence "Signal" identity.
Requires: playwright
"""

from pathlib import Path
from playwright.sync_api import sync_playwright

OUTPUT_DIR = Path(__file__).parent.parent / "assets" / "gallery" / "steps"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Signal palette (Autonomy Intelligence) ──
ACCENT = "oklch(50% 0.090 196)"
MUTED = "oklch(52% 0.014 215)"
FAINT = "oklch(66% 0.012 215)"
ACCENT_LINE = "oklch(80% 0.045 196)"

GLYPH = (
    '<svg width="18" height="18" viewBox="0 0 24 24">'
    f'<circle cx="12" cy="12" r="8.6" fill="none" stroke="{ACCENT}" stroke-width="2.6" '
    'stroke-linecap="round" stroke-dasharray="47 8" transform="rotate(-58 12 12)"/></svg>'
)

STEPS = [
    {
        "number": "01",
        "label": "Step 01",
        "title": "Define your\nideal client",
        "desc": "You provide your ICP — industry, company size, role, and the signals that matter. This becomes the agent's targeting spec.",
        "icon": f"""<svg width="80" height="80" viewBox="0 0 56 56" fill="none">
          <rect x="6" y="10" width="44" height="36" rx="2" stroke="{ACCENT}" stroke-width="2" fill="none"/>
          <rect x="14" y="20" width="12" height="3" rx="1.5" fill="{FAINT}"/>
          <rect x="14" y="27" width="28" height="3" rx="1.5" fill="{FAINT}"/>
          <rect x="14" y="34" width="20" height="3" rx="1.5" fill="{FAINT}"/>
        </svg>""",
        "accent": False,
    },
    {
        "number": "02",
        "label": "Step 02",
        "title": "AI reviews your\nprospect list",
        "desc": "The agent reviews each prospect in your list and scores them against your criteria. No manual sorting needed.",
        "icon": f"""<svg width="80" height="80" viewBox="0 0 56 56" fill="none">
          <circle cx="24" cy="24" r="14" stroke="{MUTED}" stroke-width="2" fill="none"/>
          <path d="M34 34L48 48" stroke="{ACCENT}" stroke-width="2" stroke-linecap="round"/>
        </svg>""",
        "accent": False,
    },
    {
        "number": "03",
        "label": "Step 03",
        "title": "Qualifies against\nyour criteria",
        "desc": "Each prospect is scored against your ICP. Anyone who doesn't fit is filtered out. You only see leads worth your time.",
        "icon": f"""<svg width="80" height="80" viewBox="0 0 56 56" fill="none">
          <rect x="6" y="6" width="44" height="44" rx="2" stroke="{MUTED}" stroke-width="2" fill="none"/>
          <path d="M16 28L24 36L40 20" stroke="{ACCENT}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>""",
        "accent": False,
    },
    {
        "number": "04",
        "label": "Step 04",
        "title": "Drafts personalised\noutreach",
        "desc": "For every qualified lead, the agent writes a personalised message referencing their specific situation. Not a template blast.",
        "icon": f"""<svg width="80" height="80" viewBox="0 0 56 56" fill="none">
          <path d="M8 14H48M8 14V42H48V14" stroke="{MUTED}" stroke-width="2" fill="none" stroke-linejoin="round"/>
          <path d="M8 14L28 30L48 14" stroke="{ACCENT}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>""",
        "accent": False,
    },
    {
        "number": "05",
        "label": "Output",
        "title": "Leads + drafts\ndelivered",
        "desc": "A clean list of qualified leads, each with a personalised draft ready to review, approve, and send.",
        "icon": f"""<svg width="80" height="80" viewBox="0 0 56 56" fill="none">
          <rect x="6" y="8" width="44" height="40" rx="2" stroke="{ACCENT}" stroke-width="2" fill="none"/>
          <rect x="14" y="18" width="8" height="8" rx="1" fill="{ACCENT_LINE}" stroke="{ACCENT}" stroke-width="1.5"/>
          <rect x="28" y="20" width="16" height="3" rx="1.5" fill="{MUTED}"/>
          <rect x="28" y="25" width="10" height="2" rx="1" fill="{FAINT}"/>
          <rect x="14" y="32" width="8" height="8" rx="1" fill="{ACCENT_LINE}" stroke="{ACCENT}" stroke-width="1.5"/>
          <rect x="28" y="34" width="16" height="3" rx="1.5" fill="{MUTED}"/>
          <rect x="28" y="39" width="10" height="2" rx="1" fill="{FAINT}"/>
        </svg>""",
        "accent": True,
    },
]


SIGNAL_TOKENS = """
  :root {
    --bg:            oklch(98.5% 0.004 95);
    --surface:       oklch(99.6% 0.002 95);
    --surface-sunk:  oklch(96.5% 0.005 95);
    --fg:            oklch(24% 0.015 215);
    --muted:         oklch(52% 0.014 215);
    --faint:         oklch(66% 0.012 215);
    --border:        oklch(90% 0.006 215);
    --border-strong: oklch(82% 0.008 215);
    --accent:        oklch(50% 0.090 196);
    --accent-hover:  oklch(44% 0.092 196);
    --accent-soft:   oklch(95% 0.020 196);
    --accent-line:   oklch(80% 0.045 196);
    --accent-ghost:  oklch(92% 0.028 196);
    --font-sans:     'Satoshi', -apple-system, sans-serif;
    --font-mono:     'JetBrains Mono', ui-monospace, monospace;
  }
"""

FONT_LINKS = """
<link rel="preconnect" href="https://api.fontshare.com">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://api.fontshare.com/v2/css?f[]=satoshi@400,500,700&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
"""


def build_html(step, index, total):
    title_color = "var(--accent-hover)" if step["accent"] else "var(--fg)"
    card_border = "var(--accent-line)" if step["accent"] else "var(--border)"
    card_bg = "var(--accent-soft)" if step["accent"] else "var(--surface)"
    num_color = "var(--accent-line)" if step["accent"] else "var(--accent-ghost)"
    title_lines = step["title"].replace("\n", "<br>")
    dots = "".join(
        f'<div class="dot{" active" if i == index else ""}"></div>' for i in range(total)
    )

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
{FONT_LINKS}
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
{SIGNAL_TOKENS}
  body {{
    width: 1200px;
    height: 1200px;
    background: var(--bg);
    font-family: var(--font-sans);
    -webkit-font-smoothing: antialiased;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    position: relative;
  }}
  .top-tag {{
    position: absolute;
    top: 60px; left: 72px;
    font-family: var(--font-mono);
    font-size: 14px;
    font-weight: 500;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--accent);
  }}
  .progress {{
    position: absolute;
    top: 60px; right: 72px;
    font-family: var(--font-mono);
    font-size: 14px;
    font-weight: 500;
    letter-spacing: 0.10em;
    color: var(--faint);
  }}
  .card {{
    width: 920px;
    background: {card_bg};
    border: 1px solid {card_border};
    border-radius: 10px;
    padding: 72px 80px 64px;
    position: relative;
  }}
  .step-number {{
    font-family: var(--font-mono);
    font-size: 140px;
    font-weight: 500;
    color: {num_color};
    line-height: 1;
    position: absolute;
    top: 36px; right: 48px;
    user-select: none;
  }}
  .step-label {{
    font-family: var(--font-mono);
    font-size: 13px;
    font-weight: 500;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--faint);
    margin-bottom: 28px;
  }}
  .icon {{ margin-bottom: 36px; }}
  .step-title {{
    font-size: 62px;
    font-weight: 700;
    color: {title_color};
    line-height: 1.05;
    letter-spacing: -0.025em;
    margin-bottom: 32px;
  }}
  .step-desc {{
    font-size: 22px;
    font-weight: 400;
    color: var(--muted);
    line-height: 1.65;
    max-width: 680px;
  }}
  .bottom-bar {{
    position: absolute;
    bottom: 60px;
    left: 72px; right: 72px;
    display: flex;
    align-items: center;
    gap: 14px;
  }}
  .dot {{
    width: 8px; height: 8px;
    border-radius: 50%;
    background: var(--border-strong);
  }}
  .dot.active {{ background: var(--accent); }}
  .brand {{
    margin-left: auto;
    display: flex;
    align-items: center;
    gap: 9px;
  }}
  .brand-stack {{ display: flex; flex-direction: column; gap: 1px; }}
  .brand-name {{
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.02em;
    color: var(--fg);
    line-height: 1.1;
  }}
  .brand-sub {{
    font-family: var(--font-mono);
    font-size: 8px;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--faint);
    line-height: 1.1;
  }}
</style>
</head>
<body>
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
  {dots}
  <div class="brand">{GLYPH}<div class="brand-stack"><span class="brand-name">Ato Sam</span><span class="brand-sub">Autonomy Intelligence</span></div></div>
</div>

</body>
</html>"""


def build_before_after(index, total):
    dots = "".join(
        f'<div class="dot{" active" if i == index else ""}"></div>' for i in range(total)
    )
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
{FONT_LINKS}
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
{SIGNAL_TOKENS}
  body {{
    width: 1200px;
    height: 1200px;
    background: var(--bg);
    font-family: var(--font-sans);
    -webkit-font-smoothing: antialiased;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    position: relative;
  }}
  .top-tag {{
    position: absolute;
    top: 60px; left: 72px;
    font-family: var(--font-mono);
    font-size: 14px;
    font-weight: 500;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--accent);
  }}
  .progress {{
    position: absolute;
    top: 60px; right: 72px;
    font-family: var(--font-mono);
    font-size: 14px;
    font-weight: 500;
    letter-spacing: 0.10em;
    color: var(--faint);
  }}
  .headline {{
    font-size: 64px;
    font-weight: 700;
    color: var(--fg);
    letter-spacing: -0.025em;
    margin-bottom: 52px;
    text-align: center;
  }}
  .panels {{
    display: flex;
    flex-direction: column;
    gap: 22px;
    width: 920px;
  }}
  .panel {{
    padding: 44px 52px;
    border-radius: 10px;
  }}
  .panel.before {{ border: 1px solid var(--border); background: var(--surface); }}
  .panel.after  {{ border: 1px solid var(--accent-line); background: var(--accent-soft); }}
  .panel-label {{
    font-family: var(--font-mono);
    font-size: 13px;
    font-weight: 500;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    margin-bottom: 20px;
  }}
  .panel.before .panel-label {{ color: var(--faint); }}
  .panel.after  .panel-label {{ color: var(--accent); }}
  .panel-text {{
    font-size: 25px;
    font-weight: 400;
    color: var(--muted);
    line-height: 1.6;
  }}
  .panel-text strong {{ color: var(--fg); font-weight: 600; }}
  .panel.after .panel-text strong {{ color: var(--accent-hover); }}
  .bottom-bar {{
    position: absolute;
    bottom: 60px;
    left: 72px; right: 72px;
    display: flex;
    align-items: center;
    gap: 14px;
  }}
  .dot {{ width: 8px; height: 8px; border-radius: 50%; background: var(--border-strong); }}
  .dot.active {{ background: var(--accent); }}
  .brand {{
    margin-left: auto;
    display: flex;
    align-items: center;
    gap: 9px;
  }}
  .brand-stack {{ display: flex; flex-direction: column; gap: 1px; }}
  .brand-name {{
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.02em;
    color: var(--fg);
    line-height: 1.1;
  }}
  .brand-sub {{
    font-family: var(--font-mono);
    font-size: 8px;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--faint);
    line-height: 1.1;
  }}
</style>
</head>
<body>
<div class="top-tag">AI Lead Research Agent</div>
<div class="progress">{index + 1} / {total}</div>

<div class="headline">3 hours vs 15 minutes</div>

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
  {dots}
  <div class="brand">{GLYPH}<div class="brand-stack"><span class="brand-name">Ato Sam</span><span class="brand-sub">Autonomy Intelligence</span></div></div>
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
        page.set_content(build_before_after(TOTAL - 1, TOTAL), wait_until="networkidle")
        page.wait_for_timeout(1500)
        out_path = OUTPUT_DIR / "step-06-before-after.jpg"
        page.screenshot(path=str(out_path), type="jpeg", quality=92)
        print(f"[OK] {out_path.name}")

        browser.close()
    print(f"\nAll {TOTAL} cards saved to assets/gallery/steps/")


if __name__ == "__main__":
    main()
