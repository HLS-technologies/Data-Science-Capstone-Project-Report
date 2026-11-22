"""Capture overview and proximity close-ups of the generated interactive Folium map."""
from pathlib import Path
import re
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "outputs" / "spacex_launch_sites_map.html"
OUT = ROOT / "outputs" / "screenshots"


def main():
    if not MAP.exists():
        raise FileNotFoundError(f"Map HTML does not exist: {MAP}")
    OUT.mkdir(parents=True, exist_ok=True)
    html = MAP.read_text(encoding="utf-8")
    match = re.search(r"var (map_[A-Za-z0-9_]+) = L\.map", html)
    if not match:
        raise RuntimeError("Could not locate the Folium Leaflet map variable.")
    map_var = match.group(1)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1600, "height": 1100}, device_scale_factor=1)
        page.goto(MAP.as_uri(), wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(2500)
        page.screenshot(path=str(OUT / "folium_launch_site_map.png"), full_page=True)

        # Florida close-up: show launch-site markers, coastline/rail/highway/city
        # selected points, distance labels, and connecting polylines.
        page.evaluate(f"window['{map_var}'].setView([28.57, -80.60], 10)")
        page.wait_for_timeout(1200)
        page.screenshot(path=str(OUT / "folium_proximity_florida.png"), full_page=True)

        # Vandenberg close-up, including its selected proximity features.
        page.evaluate(f"window['{map_var}'].setView([34.64, -120.61], 11)")
        page.wait_for_timeout(1200)
        page.screenshot(path=str(OUT / "folium_proximity_vafb.png"), full_page=True)
        browser.close()

    print("Folium screenshots saved:", OUT)


if __name__ == "__main__":
    main()
