"""Capture default and filtered views of the actual running Dash application."""
from __future__ import annotations
import argparse
from pathlib import Path
import subprocess
import sys
import time
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from capstone_data import load_dash_frame


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default=str(ROOT / "data" / "spacex_launch_dash.csv"))
    parser.add_argument("--output-dir", default=str(ROOT / "outputs" / "screenshots"))
    parser.add_argument("--port", type=int, default=8050)
    args = parser.parse_args()
    df = load_dash_frame(args.data)
    sites = sorted(df["Launch Site"].unique())
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    server = subprocess.Popen(
        [sys.executable, str(ROOT / "spacex_dash_app.py"), "--data", args.data,
         "--host", "127.0.0.1", "--port", str(args.port)],
        cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT
    )
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1600, "height": 1050})
            url = f"http://127.0.0.1:{args.port}"
            loaded = False
            for _ in range(60):
                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=5000)
                    page.wait_for_selector("#payload-outcome-scatter .js-plotly-plot", timeout=3000)
                    loaded = True
                    break
                except Exception:
                    time.sleep(1)
            if not loaded:
                raise RuntimeError("Dash app did not become ready.")
            page.wait_for_timeout(1200)
            page.screenshot(path=str(out / "dash_default.png"), full_page=True)
            page.locator("#site-dropdown").click()
            option = page.locator(".Select-option").filter(has_text=sites[0]).first
            if option.count() == 0:
                option = page.get_by_text(sites[0], exact=True).last
            option.click()
            page.wait_for_timeout(1200)
            page.screenshot(path=str(out / "dash_filtered_site.png"), full_page=True)
            browser.close()
    finally:
        server.terminate()
        try:
            server.wait(timeout=10)
        except subprocess.TimeoutExpired:
            server.kill()

if __name__ == "__main__":
    main()
