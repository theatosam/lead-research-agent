"""
Render the standalone gallery HTML files to images for the Upwork listing.
Each listing-*.html is screenshotted to .jpg + .png at its body dimensions.
The sample deliverable is rendered to a multi-page PDF.
Requires: playwright
"""

from pathlib import Path
from playwright.sync_api import sync_playwright

GALLERY = Path(__file__).parent.parent / "assets" / "gallery"

# filename stem -> (width, height) of the HTML body
SCREENSHOTS = {
    "listing-1-workflow-diagram": (1200, 1200),
    "listing-1-output-table": (1200, 1200),
    "listing-1-output-draft": (1200, 1200),
    "listing-1-output-mockup": (1920, 1080),
}

# rendered to PDF instead of an image
PDFS = {
    "listing-1-sample-pdf": "letter",
}


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        for stem, (w, h) in SCREENSHOTS.items():
            src = GALLERY / f"{stem}.html"
            if not src.exists():
                print(f"[SKIP] {stem}.html not found")
                continue
            page = browser.new_page(viewport={"width": w, "height": h})
            page.goto(src.as_uri(), wait_until="networkidle")
            page.wait_for_timeout(1500)
            for ext, opts in (("jpg", {"type": "jpeg", "quality": 92}), ("png", {"type": "png"})):
                out = GALLERY / f"{stem}.{ext}"
                page.screenshot(path=str(out), **opts)
                print(f"[OK] {out.name}")
            page.close()

        for stem, fmt in PDFS.items():
            src = GALLERY / f"{stem}.html"
            if not src.exists():
                print(f"[SKIP] {stem}.html not found")
                continue
            page = browser.new_page()
            page.goto(src.as_uri(), wait_until="networkidle")
            page.wait_for_timeout(1500)
            out = GALLERY / f"{stem}.pdf"
            page.pdf(path=str(out), format=fmt, print_background=True)
            print(f"[OK] {out.name}")
            page.close()

        browser.close()
    print("\nGallery assets rendered to assets/gallery/")


if __name__ == "__main__":
    main()
