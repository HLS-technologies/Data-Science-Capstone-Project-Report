"""Smoke-test project data, dashboard figures, and Folium map generation."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from capstone_data import load_dash_frame
from spacex_dash_app import make_figures
from build_folium_map import build_map


def main():
    data_dir = ROOT / "data"
    required = [
        "dataset_part_2.csv", "dataset_part_3.csv",
        "spacex_launch_dash.csv", "spacex_launch_geo.csv"
    ]
    missing = [name for name in required if not (data_dir / name).exists()]
    if missing:
        raise FileNotFoundError(f"Missing IBM course datasets: {missing}")

    dash = load_dash_frame(data_dir / "spacex_launch_dash.csv")
    pie, scatter, summary, filtered = make_figures(dash)
    assert len(filtered) > 0
    assert len(pie.data) > 0
    assert len(scatter.data) > 0
    assert list(scatter.layout.yaxis.tickvals) == [0, 1]
    print("Dashboard data rows:", len(dash))
    print("Dashboard default summary:", summary)
    print("Pie traces:", len(pie.data), "| Scatter traces:", len(scatter.data))

    output = ROOT / "outputs" / "spacex_launch_sites_map.html"
    _, site_summary, map_path = build_map(data_dir / "spacex_launch_geo.csv", output)
    assert map_path.exists() and map_path.stat().st_size > 10_000
    print("Folium map:", map_path, "| Launch-site groups:", len(site_summary))
    print(site_summary.to_string(index=False))


if __name__ == "__main__":
    main()
