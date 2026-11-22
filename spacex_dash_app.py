"""Interactive IBM SpaceX Falcon 9 dashboard.
Run from repository root: python spacex_dash_app.py
"""
from __future__ import annotations
import argparse
from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, dcc, html

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
from capstone_data import load_dash_frame


def make_figures(data: pd.DataFrame, selected_site: str = "ALL",
                 payload_range: tuple[float, float] | list[float] | None = None):
    """Return actual dashboard figures, summary, and filtered rows."""
    low = float(data["Payload Mass (kg)"].min())
    high = float(data["Payload Mass (kg)"].max())
    if payload_range is not None:
        low, high = map(float, payload_range)
    filtered = data[data["Payload Mass (kg)"].between(low, high, inclusive="both")].copy()
    if selected_site and selected_site != "ALL":
        filtered = filtered[filtered["Launch Site"] == selected_site]

    successes = filtered.loc[filtered["Class"] == 1]
    counts = (successes.groupby("Launch Site", as_index=False)
              .size().rename(columns={"size": "Successful Landings"}))
    if counts.empty:
        pie = px.pie(title="No successful first-stage landings in this selection")
    else:
        pie = px.pie(counts, names="Launch Site", values="Successful Landings",
                     title="Successful First-Stage Landings by Launch Site", hole=0.38)
        pie.update_traces(textposition="inside", textinfo="label+value+percent")

    hover = [c for c in ["Flight Number", "Launch Site", "Booster Version"] if c in filtered.columns]
    scatter = px.scatter(
        filtered, x="Payload Mass (kg)", y="Class",
        color="Booster Version Category", hover_data=hover,
        title="Payload Mass vs First-Stage Landing Outcome",
        labels={"Class": "First-stage landing outcome",
                "Booster Version Category": "Booster version category"}
    )
    scatter.update_yaxes(tickmode="array", tickvals=[0, 1],
                         ticktext=["Unsuccessful (0)", "Successful (1)"], range=[-0.15, 1.15])
    scatter.update_traces(marker=dict(size=10, opacity=0.82,
                                      line=dict(width=0.5, color="white")))
    scatter.update_layout(legend_title_text="Booster category")

    n = len(filtered)
    if n:
        success_count = int((filtered["Class"] == 1).sum())
        unsuccessful_count = int((filtered["Class"] == 0).sum())
        summary = (f"Filtered records: {n} | Successful landings: {success_count} | "
                   f"Unsuccessful landings: {unsuccessful_count} | "
                   f"Observed landing success rate: {success_count/n:.1%} | "
                   f"Payload range: {low:,.0f}–{high:,.0f} kg")
    else:
        summary = "No records match the selected filters. Widen the payload range or choose another site."
    return pie, scatter, summary, filtered


def create_app(data_path: str | Path | None = None) -> Dash:
    csv_path = Path(data_path) if data_path else ROOT / "data" / "spacex_launch_dash.csv"
    df = load_dash_frame(csv_path)
    sites = sorted(df["Launch Site"].dropna().unique().tolist())
    pmin = float(df["Payload Mass (kg)"].min())
    pmax = float(df["Payload Mass (kg)"].max())
    if pmin == pmax:
        pmax = pmin + 1.0

    app = Dash(__name__, title="SpaceX Falcon 9 Landing Analytics",
               assets_folder=str(ROOT / "assets"))
    app.layout = html.Div([
        html.Header([
            html.Div("IBM APPLIED DATA SCIENCE CAPSTONE", className="eyebrow"),
            html.H1("SpaceX Falcon 9 Launch Records Dashboard"),
            html.P("Explore first-stage landing outcomes by launch site, payload mass, and booster category.")
        ], className="hero"),
        html.Main([
            html.Section([
                html.Div([
                    html.Label("Launch Site", htmlFor="site-dropdown"),
                    dcc.Dropdown(
                        id="site-dropdown",
                        options=[{"label": "All Launch Sites", "value": "ALL"}] +
                                [{"label": s, "value": s} for s in sites],
                        value="ALL", clearable=False
                    )
                ], className="filter-card"),
                html.Div([
                    html.Label("Payload Mass Range (kg)", htmlFor="payload-slider"),
                    dcc.RangeSlider(
                        id="payload-slider", min=pmin, max=pmax, step=max(1, (pmax-pmin)/100),
                        value=[pmin, pmax],
                        marks={pmin: f"{pmin:,.0f}", pmax: f"{pmax:,.0f}"},
                        tooltip={"placement": "bottom", "always_visible": True}
                    )
                ], className="filter-card slider-card")
            ], className="filters"),
            html.Div(id="record-summary", className="summary", role="status"),
            html.Section([
                dcc.Graph(id="success-pie-chart", config={"displaylogo": False}),
                dcc.Graph(id="payload-outcome-scatter", config={"displaylogo": False})
            ], className="charts"),
            html.P(
                "Class = 1 indicates successful first-stage landing; Class = 0 indicates unsuccessful first-stage landing. "
                "This is not the same as overall mission success.", className="footnote"
            )
        ], className="content")
    ], className="page")

    @app.callback(
        Output("success-pie-chart", "figure"),
        Output("payload-outcome-scatter", "figure"),
        Output("record-summary", "children"),
        Input("site-dropdown", "value"),
        Input("payload-slider", "value")
    )
    def update_dashboard(selected_site, payload_range):
        pie, scatter, summary, _ = make_figures(df, selected_site, payload_range)
        return pie, scatter, summary

    return app


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default=None)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8050)
    args = parser.parse_args()
    create_app(args.data).run(host=args.host, port=args.port, debug=False)


if __name__ == "__main__":
    main()
