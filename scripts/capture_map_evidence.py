"""Capture a screenshot of the generated interactive Folium HTML map."""
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "outputs" / "spacex_launch_sites_map.html"
OUT = ROOT / "outputs" / "screenshots" / "folium_launch_site_map.png"


def main():
    if not MAP.exists():
        raise FileNotFoundError(f"Map HTML does not exist: {MAP}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1600, "height": 1100}, device_scale_factor=1)
        page.goto(MAP.as_uri(), wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(2500)
        page.screenshot(path=str(OUT), full_page=True)
        browser.close()
    print("Folium screenshot saved:", OUT)


if __name__ == "__main__":
    main()
