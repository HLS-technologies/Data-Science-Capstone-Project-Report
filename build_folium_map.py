"""Generate a Folium map from the course spacex_launch_geo.csv.
Run from project root: python apps/build_folium_map.py
"""
from __future__ import annotations
import argparse, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from folium_map import build_map

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data", default=None, help="Path to spacex_launch_geo.csv")
    p.add_argument("--proximity", default="data/proximity_features.csv")
    p.add_argument("--output", default="outputs/spacex_launch_sites_map.html")
    args = p.parse_args()
    _, sites, proximity, output = build_map(
        csv_path=args.data, output_html=args.output,
        proximity_csv=args.proximity,
    )
    print(f"Map saved: {output}")
    print("Launch-site summary:")
    print(sites.to_string(index=False))
    if proximity.empty:
        print("\nNo source-verified proximity coordinates supplied. The map includes a measurement tool; "
              "populate data/proximity_features.csv with cited feature coordinates to calculate nearest-feature distances.")
    else:
        print("\nNearest-feature distances (km):")
        print(proximity.to_string(index=False))

if __name__ == "__main__":
    main()
