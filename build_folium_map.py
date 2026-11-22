"""Generate an interactive Folium map using the IBM capstone geography CSV."""
from __future__ import annotations
import argparse
import html
from pathlib import Path
import sys

import folium
import pandas as pd
from folium.plugins import MarkerCluster, Fullscreen, MeasureControl, MiniMap

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
from capstone_data import standardize_columns, normalize_class


def build_map(data_path: str | Path, output_path: str | Path):
    df = standardize_columns(pd.read_csv(data_path))
    required = ["Launch Site", "Latitude", "Longitude"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Geography dataset is missing columns {missing}; found {list(df.columns)}")
    if "Class" not in df.columns:
        if "Landing Outcome" not in df.columns:
            raise ValueError("Dataset must include class or Landing Outcome.")
        df["Class"] = normalize_class(df["Landing Outcome"])
    else:
        df["Class"] = normalize_class(df["Class"])
    for c in ["Latitude", "Longitude", "Payload Mass (kg)"]:
        if c in df:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    if "Payload Mass (kg)" not in df:
        df["Payload Mass (kg)"] = pd.NA
    if "Flight Number" not in df:
        df["Flight Number"] = range(1, len(df)+1)
    df = df.dropna(subset=["Launch Site", "Latitude", "Longitude", "Class"]).copy()
    df["Class"] = df["Class"].astype(int)
    if df.empty:
        raise ValueError("No valid geographic launch rows found.")

    site_summary = df.groupby("Launch Site", as_index=False).agg(
        Latitude=("Latitude", "mean"), Longitude=("Longitude", "mean"),
        Launches=("Flight Number", "count"), Success_Rate=("Class", "mean")
    )
    site_summary["Success_Rate"] *= 100
    m = folium.Map(location=[float(df.Latitude.mean()), float(df.Longitude.mean())],
                   zoom_start=4, control_scale=True, tiles="OpenStreetMap")
    Fullscreen(position="topleft").add_to(m)
    MiniMap(toggle_display=True).add_to(m)
    MeasureControl(primary_length_unit="kilometers", secondary_length_unit="miles").add_to(m)
    sites_layer = folium.FeatureGroup(name="Launch-site reference markers")
    records_layer = folium.FeatureGroup(name="Launch records (clustered)")
    clusters = MarkerCluster().add_to(records_layer)

    for _, row in site_summary.iterrows():
        popup = (f"<b>{html.escape(str(row['Launch Site']))}</b><br>"
                 f"Launch records: {int(row['Launches'])}<br>"
                 f"Observed landing success rate: {row['Success_Rate']:.1f}%")
        folium.Marker([row["Latitude"], row["Longitude"]],
                      popup=folium.Popup(popup, max_width=320),
                      tooltip=f"Launch site: {row['Launch Site']}",
                      icon=folium.Icon(color="blue", icon="rocket", prefix="fa")).add_to(sites_layer)

    for _, row in df.iterrows():
        success = int(row["Class"]) == 1
        outcome = "Successful" if success else "Unsuccessful"
        details = [f"<b>Flight:</b> {html.escape(str(row['Flight Number']))}",
                   f"<b>Launch site:</b> {html.escape(str(row['Launch Site']))}",
                   f"<b>Landing outcome:</b> {outcome}"]
        if pd.notna(row["Payload Mass (kg)"]):
            details.append(f"<b>Payload:</b> {row['Payload Mass (kg)']:,.0f} kg")
        if "Booster Version" in row and pd.notna(row["Booster Version"]):
            details.append(f"<b>Booster:</b> {html.escape(str(row['Booster Version']))}")
        folium.CircleMarker([row["Latitude"], row["Longitude"]], radius=6,
                            color="green" if success else "red", fill=True, fill_opacity=.82,
                            popup=folium.Popup("<br>".join(details), max_width=320),
                            tooltip=f"Flight {row['Flight Number']}: {outcome}").add_to(clusters)

    sites_layer.add_to(m)
    records_layer.add_to(m)
    folium.LayerControl(collapsed=False).add_to(m)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    m.save(str(out))
    return m, site_summary, out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default=str(ROOT / "data" / "spacex_launch_geo.csv"))
    parser.add_argument("--output", default=str(ROOT / "outputs" / "spacex_launch_sites_map.html"))
    args = parser.parse_args()
    _, summary, out = build_map(args.data, args.output)
    print("Map saved:", out)
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
