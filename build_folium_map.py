"""Generate the interactive Folium map with IBM lab proximity distances."""
from __future__ import annotations
import argparse
import html
from pathlib import Path
import sys

import folium
import pandas as pd
from folium.plugins import MarkerCluster, Fullscreen, MeasureControl, MiniMap, MousePosition
from geopy.distance import geodesic

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
from capstone_data import standardize_columns, normalize_class

FEATURE_COLORS = {"coastline": "#168aad", "railway": "#6a4c93",
                  "highway": "#f77f00", "city": "#d62828"}


def build_map(data_path, output_path, proximity_path=None):
    df = standardize_columns(pd.read_csv(data_path))
    required = ["Launch Site", "Latitude", "Longitude"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing geography columns {missing}; found {list(df.columns)}")

    if "Class" not in df.columns:
        if "Landing Outcome" not in df.columns:
            raise ValueError("Need Class or Landing Outcome column.")
        df["Class"] = normalize_class(df["Landing Outcome"])
    else:
        df["Class"] = normalize_class(df["Class"])

    for col in ["Latitude", "Longitude", "Payload Mass (kg)"]:
        if col in df:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    if "Payload Mass (kg)" not in df:
        df["Payload Mass (kg)"] = pd.NA
    if "Flight Number" not in df:
        df["Flight Number"] = range(1, len(df) + 1)
    df = df.dropna(subset=["Launch Site", "Latitude", "Longitude", "Class"]).copy()
    df["Class"] = df["Class"].astype(int)
    if df.empty:
        raise ValueError("No valid launch records.")

    site_summary = df.groupby("Launch Site", as_index=False).agg(
        Latitude=("Latitude", "mean"), Longitude=("Longitude", "mean"),
        Launches=("Flight Number", "count"), Success_Rate=("Class", "mean")
    )
    site_summary["Success_Rate"] *= 100
    site_lookup = {
        str(r["Launch Site"]): (float(r["Latitude"]), float(r["Longitude"]))
        for _, r in site_summary.iterrows()
    }

    prox_file = Path(proximity_path) if proximity_path else ROOT / "data" / "proximity_features.csv"
    proximity_results = pd.DataFrame()
    if prox_file.exists():
        prox = pd.read_csv(prox_file)
        required_prox = {"Launch Site", "Feature Type", "Feature Name", "Latitude", "Longitude"}
        missing = required_prox - set(prox.columns)
        if missing:
            raise ValueError(f"Proximity file missing columns: {sorted(missing)}")
        for col in ["Latitude", "Longitude"]:
            prox[col] = pd.to_numeric(prox[col], errors="coerce")
        prox = prox.dropna(subset=["Launch Site", "Feature Type", "Latitude", "Longitude"])
        rows = []
        for _, r in prox.iterrows():
            site = str(r["Launch Site"])
            if site not in site_lookup:
                raise ValueError(f"Proximity site {site!r} not present in launch data.")
            origin = site_lookup[site]
            target = (float(r["Latitude"]), float(r["Longitude"]))
            rows.append({
                "Launch Site": site,
                "Feature Type": str(r["Feature Type"]).lower(),
                "Feature Name": str(r["Feature Name"]),
                "Latitude": target[0], "Longitude": target[1],
                "Distance (km)": geodesic(origin, target).km,
                "Coordinate Source": r.get("Source", "IBM course Folium lab selected coordinate"),
            })
        proximity_results = pd.DataFrame(rows)

    m = folium.Map(location=[float(df["Latitude"].mean()), float(df["Longitude"].mean())],
                   zoom_start=4, control_scale=True, tiles="OpenStreetMap")
    Fullscreen(position="topleft").add_to(m)
    MiniMap(toggle_display=True).add_to(m)
    MeasureControl(primary_length_unit="kilometers", secondary_length_unit="miles").add_to(m)
    MousePosition(position="topright", separator=" | ", prefix="Lat/Lon:", num_digits=5).add_to(m)

    sites_layer = folium.FeatureGroup(name="Launch site markers", show=True)
    records_layer = folium.FeatureGroup(name="Launch records (clustered)", show=True)
    cluster = MarkerCluster().add_to(records_layer)
    proximity_layer = folium.FeatureGroup(name="Proximity points, distances and lines", show=True)

    for _, r in site_summary.iterrows():
        name = html.escape(str(r["Launch Site"]))
        popup = f"<b>{name}</b><br>Launch records: {int(r['Launches'])}<br>Observed landing success rate: {r['Success_Rate']:.1f}%"
        folium.Circle([r["Latitude"], r["Longitude"]], radius=1000,
                      color="#0b7285", fill=True, fill_opacity=0.08, weight=2).add_to(sites_layer)
        folium.Marker([r["Latitude"], r["Longitude"]],
                      popup=folium.Popup(popup, max_width=320),
                      tooltip=f"Launch site: {r['Launch Site']}",
                      icon=folium.Icon(color="blue", icon="rocket", prefix="fa")).add_to(sites_layer)

    for _, r in df.iterrows():
        success = int(r["Class"]) == 1
        outcome = "Successful" if success else "Unsuccessful"
        details = [
            f"<b>Flight:</b> {html.escape(str(r['Flight Number']))}",
            f"<b>Launch site:</b> {html.escape(str(r['Launch Site']))}",
            f"<b>Landing outcome:</b> {outcome}"
        ]
        if pd.notna(r["Payload Mass (kg)"]):
            details.append(f"<b>Payload:</b> {r['Payload Mass (kg)']:,.0f} kg")
        if "Booster Version" in r and pd.notna(r["Booster Version"]):
            details.append(f"<b>Booster:</b> {html.escape(str(r['Booster Version']))}")
        folium.CircleMarker([r["Latitude"], r["Longitude"]], radius=6,
                            color="green" if success else "red",
                            fill=True, fill_opacity=0.82,
                            popup=folium.Popup("<br>".join(details), max_width=320),
                            tooltip=f"Flight {r['Flight Number']}: {outcome}").add_to(cluster)

    if not proximity_results.empty:
        for _, r in proximity_results.iterrows():
            color = FEATURE_COLORS.get(r["Feature Type"], "#555555")
            origin = site_lookup[r["Launch Site"]]
            target = (r["Latitude"], r["Longitude"])
            label = f"{r['Feature Type'].upper()} {r['Distance (km)']:.2f} km"
            popup = (f"<b>{html.escape(r['Launch Site'])}</b><br>"
                     f"{html.escape(r['Feature Type'])}: {html.escape(r['Feature Name'])}<br>"
                     f"Straight-line distance: {r['Distance (km)']:.2f} km")
            folium.PolyLine([origin, target], color=color, weight=2.2,
                            opacity=0.85, tooltip=label).add_to(proximity_layer)
            folium.CircleMarker(target, radius=5, color=color, fill=True,
                                fill_color=color, fill_opacity=0.95,
                                popup=folium.Popup(popup, max_width=320),
                                tooltip=label).add_to(proximity_layer)
            label_offsets = {"coastline": 10, "railway": 28, "highway": 46, "city": 64}
            offset = label_offsets.get(r["Feature Type"], 10)
            folium.Marker(target, icon=folium.DivIcon(
                icon_size=(150, 18), icon_anchor=(-4, offset),
                html=f'<div style="font-size:10px;color:{color};font-weight:bold;'
                     f'background:rgba(255,255,255,.72);padding:1px 3px;border-radius:3px;'
                     f'white-space:nowrap;">{label}</div>'
            )).add_to(proximity_layer)

    sites_layer.add_to(m)
    records_layer.add_to(m)
    proximity_layer.add_to(m)
    folium.LayerControl(collapsed=False).add_to(m)

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    m.save(str(out))
    if not proximity_results.empty:
        proximity_results.to_csv(out.parent / "proximity_analysis.csv", index=False)
    return m, site_summary, proximity_results, out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default=str(ROOT / "data" / "spacex_launch_geo.csv"))
    parser.add_argument("--proximity", default=str(ROOT / "data" / "proximity_features.csv"))
    parser.add_argument("--output", default=str(ROOT / "outputs" / "spacex_launch_sites_map.html"))
    args = parser.parse_args()
    _, summary, proximity, out = build_map(args.data, args.output, args.proximity)
    print("Map saved:", out)
    print("Launch site summary:\n", summary.to_string(index=False))
    if not proximity.empty:
        print("\nProximity distances (straight-line km):")
        print(proximity.pivot(index="Launch Site", columns="Feature Type", values="Distance (km)").round(2))
        print("\nMean by feature:")
        print(proximity.groupby("Feature Type")["Distance (km)"].mean().round(2))


if __name__ == "__main__":
    main()
