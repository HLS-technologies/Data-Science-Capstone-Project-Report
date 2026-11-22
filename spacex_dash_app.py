"""Interactive IBM SpaceX capstone dashboard.

Expected input: data/spacex_launch_dash.csv
Run from project root: python apps/spacex_dash_app.py
"""
from __future__ import annotations
import argparse, os, sys
from pathlib import Path
import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, dcc, html

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from capstone_data import load_dash_frame  # noqa: E402

GREEN = "#168A55"
RED = "#D64545"


def make_app(data_path: str | Path | None = None) -> Dash:
    df = load_dash_frame(data_path)
    sites = sorted(df["Launch Site"].dropna().unique().tolist())
    pmin = float(df["Payload Mass (kg)"].min())
    pmax = float(df["Payload Mass (kg)"].max())
    if pmin == pmax:
        pmax = pmin + 1.0
    step = max(1.0, (pmax - pmin) / 100)

    app = Dash(__name__, title="SpaceX Falcon 9 Landing Analytics", assets_folder=str(ROOT / "assets"))
    app.layout = html.Div([
        html.Header([
            html.Div("IBM APPLIED DATA SCIENCE CAPSTONE", className="eyebrow"),
            html.H1("SpaceX Falcon 9 Launch Records Dashboard"),
            html.P("Explore first-stage landing outcomes by launch site, payload mass, and booster category."),
        ], className="hero"),
        html.Main([
            html.Section([
                html.Div([
                    html.Label("Launch Site", htmlFor="site-dropdown"),
                    dcc.Dropdown(
                        id="site-dropdown",
                        options=[{"label": "All Launch Sites", "value": "ALL"}] +
                                [{"label": s, "value": s} for s in sites],
                        value="ALL", clearable=False,
                    ),
                ], className="filter-card"),
                html.Div([
                    html.Label("Payload Mass Range (kg)", htmlFor="payload-slider"),
                    dcc.RangeSlider(
                        id="payload-slider", min=pmin, max=pmax, step=step,
                        value=[pmin, pmax],
                        marks={round(pmin, 1): f"{pmin:,.0f}", round(pmax, 1): f"{pmax:,.0f}"},
                        tooltip={"placement": "bottom", "always_visible": True},
                    ),
                ], className="filter-card slider-card"),
            ], className="filters"),
            html.Div(id="record-summary", className="summary", role="status"),
            html.Section([
                dcc.Graph(id="success-pie-chart", config={"displaylogo": False}),
                dcc.Graph(id="payload-outcome-scatter", config={"displaylogo": False}),
            ], className="charts"),
            html.P(
                "Class = 1 indicates a successful first-stage landing; Class = 0 indicates an unsuccessful first-stage landing. "
                "This target is not the same as overall mission success.", className="footnote"
            ),
        ], className="content"),
    ], className="page")

    @app.callback(
        Output("success-pie-chart", "figure"),
        Output("payload-outcome-scatter", "figure"),
        Output("record-summary", "children"),
        Input("site-dropdown", "value"),
        Input("payload-slider", "value"),
    )
    def update_dashboard(selected_site: str, payload_range: list[float]):
        low, high = payload_range
        filtered = df[df["Payload Mass (kg)"].between(low, high, inclusive="both")].copy()
        if selected_site != "ALL":
            filtered = filtered[filtered["Launch Site"] == selected_site]

        # The rubric asks for successful-launch counts by launch site.
        successes = filtered.loc[filtered["Class"] == 1]
        site_counts = (successes.groupby("Launch Site", as_index=False)
                       .size().rename(columns={"size": "Successful Landings"}))
        if site_counts.empty:
            pie = px.pie(title="No successful landings in the selected filter")
        else:
            pie = px.pie(
                site_counts, names="Launch Site", values="Successful Landings",
                title="Successful First-Stage Landings by Launch Site", hole=0.38,
            )
            pie.update_traces(textposition="inside", textinfo="percent+label+value")
        pie.update_layout(legend_title_text="Launch site", margin=dict(l=20, r=20, t=65, b=20))

        hover_cols = [c for c in ["Flight Number", "Launch Site", "Booster Version", "Booster Version Category"] if c in filtered.columns]
        scatter = px.scatter(
            filtered, x="Payload Mass (kg)", y="Class",
            color="Booster Version Category", hover_data=hover_cols,
            title="Payload Mass vs First-Stage Landing Outcome",
            labels={"Class": "First-stage landing outcome", "Booster Version Category": "Booster category"},
        )
        scatter.update_yaxes(tickmode="array", tickvals=[0, 1], ticktext=["Unsuccessful", "Successful"], range=[-0.15, 1.15])
        scatter.update_traces(marker=dict(size=10, opacity=0.8, line=dict(width=0.5, color="white")))
        scatter.update_layout(legend_title_text="Booster category", margin=dict(l=25, r=20, t=65, b=25))

        if filtered.empty:
            summary = "No records match these filters. Widen the payload range or select another launch site."
        else:
            n = len(filtered)
            s = int((filtered["Class"] == 1).sum())
            u = int((filtered["Class"] == 0).sum())
            rate = s / n if n else 0
            summary = (f"Filtered records: {n} | Successful landings: {s} | Unsuccessful landings: {u} "
                       f"| Observed success rate: {rate:.1%} | Payload: {low:,.0f}–{high:,.0f} kg")
        return pie, scatter, summary

    return app


def main():
    parser = argparse.ArgumentParser(description="Run the SpaceX Falcon 9 Plotly Dash application.")
    parser.add_argument("--data", default=os.getenv("SPACEX_DASH_CSV"), help="Path to spacex_launch_dash.csv")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8050)
    args = parser.parse_args()
    app = make_app(args.data)
    app.run(host=args.host, port=args.port, debug=False)

if __name__ == "__main__":
    main()
