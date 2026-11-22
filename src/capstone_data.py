"""Shared data loading and schema normalization for the IBM SpaceX capstone."""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd


def _norm(value: object) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value).strip().lower())


def standardize_columns(frame: pd.DataFrame) -> pd.DataFrame:
    aliases = {
        "Launch Site": {"launchsite", "launch_site"},
        "Payload Mass (kg)": {"payloadmass", "payloadmasskg", "payload_mass__kg_", "payload_mass_kg"},
        "Booster Version Category": {"boosterversioncategory", "booster_version_category"},
        "Booster Version": {"boosterversion", "booster_version"},
        "Flight Number": {"flightnumber", "flight_number", "flightno"},
        "Latitude": {"lat"},
        "Longitude": {"long", "lon", "lng"},
        "Class": {"class", "target", "landingsuccess", "landing_success"},
        "Landing Outcome": {"landingoutcome", "landing_outcome", "outcome"},
        "Date": {"date", "launchdate", "launch_date"},
    }
    lookup = {_norm(c): c for c in frame.columns}
    rename = {}
    for canonical, names in aliases.items():
        for candidate in {_norm(canonical), *(_norm(x) for x in names)}:
            if candidate in lookup and canonical not in frame.columns:
                rename[lookup[candidate]] = canonical
                break
    return frame.rename(columns=rename)


def normalize_class(series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    if numeric.notna().all() and set(numeric.unique()).issubset({0, 1}):
        return numeric.astype(int)
    text = series.astype("string").str.lower().str.strip()
    result = pd.Series(pd.NA, index=series.index, dtype="Int64")
    result[text.str.contains(r"success|landed|true", na=False)] = 1
    result[text.str.contains(r"failure|failed|no attempt|precluded|uncontrolled|controlled|false", na=False)] = 0
    return result


def derive_booster_category(frame: pd.DataFrame) -> pd.Series:
    if "Booster Version Category" in frame.columns:
        return frame["Booster Version Category"].astype("string").fillna("Unknown")
    if "Booster Version" not in frame.columns:
        return pd.Series("Unknown", index=frame.index, dtype="string")

    def category(value: object) -> str:
        value = str(value).strip()
        upper = value.upper()
        match = re.search(r"\bB([1-9])\b|\bBLOCK\s*([1-9])", upper)
        if match:
            return "Block " + (match.group(1) or match.group(2))
        for token in ("V1.0", "V1.1", "FT", "BLOCK 5"):
            if token in upper:
                return token
        return "Other"

    return frame["Booster Version"].map(category).astype("string")


def load_dash_frame(csv_path: str | Path | None = None) -> pd.DataFrame:
    path = Path(csv_path) if csv_path else Path("data/spacex_launch_dash.csv")
    if not path.exists():
        raise FileNotFoundError(f"Dashboard dataset not found: {path}")
    df = standardize_columns(pd.read_csv(path))
    required = {"Launch Site", "Payload Mass (kg)"}
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"{path} is missing required columns: {missing}; found {list(df.columns)}")

    if "Class" not in df.columns:
        if "Landing Outcome" not in df.columns:
            raise ValueError("Dashboard data must include Class or Landing Outcome.")
        df["Class"] = normalize_class(df["Landing Outcome"])
    else:
        df["Class"] = normalize_class(df["Class"])

    df["Payload Mass (kg)"] = pd.to_numeric(df["Payload Mass (kg)"], errors="coerce")
    df["Launch Site"] = df["Launch Site"].astype("string").str.strip()
    df["Booster Version Category"] = derive_booster_category(df)

    if "Flight Number" not in df.columns:
        df["Flight Number"] = np.arange(1, len(df) + 1)

    df = df.dropna(subset=["Launch Site", "Payload Mass (kg)", "Class"]).copy()
    df["Class"] = df["Class"].astype(int)
    df["Landing Outcome"] = df["Class"].map({0: "Unsuccessful", 1: "Successful"})
    if df.empty:
        raise ValueError(f"No valid rows remain after validating {path}.")
    return df
