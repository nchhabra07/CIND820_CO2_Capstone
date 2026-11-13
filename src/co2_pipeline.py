"""Reusable proof-of-concept pipeline utilities for the CIND820 CO2 capstone.

The functions in this module reproduce the modelling preparation and initial
validation logic from the project notebooks without changing the methodology.
They are intentionally small and explicit so each stage can be demonstrated
live: data ingestion, period assessment, population filtering, target/feature
construction, chronological splitting, and initial model evaluation.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

CORE_COLUMNS = [
    "Total", "Coal", "Oil", "Gas", "Cement", "Flaring", "Per Capita",
]

LAGGED_NAME_MAP = {
    "Total": "Total_lag1",
    "Coal": "Coal_lag1",
    "Oil": "Oil_lag1",
    "Gas": "Gas_lag1",
    "Cement": "Cement_lag1",
    "Flaring": "Flaring_lag1",
    "Per Capita": "Per_Capita_lag1",
}

FEATURE_COLUMNS = list(LAGGED_NAME_MAP.values())
TARGET_COLUMN = "Target_Total_next_year"


def load_emissions_data(csv_path: str | Path) -> pd.DataFrame:
    """Load the authoritative GCB2022v27 MtCO2 flat file."""
    csv_path = Path(csv_path)
    df = pd.read_csv(csv_path)

    required = {"Country", "ISO 3166-1 alpha-3", "Year", *CORE_COLUMNS}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Dataset is missing required columns: {sorted(missing)}")

    return df


def assess_modelling_periods(
    df: pd.DataFrame,
    candidate_years: Iterable[int] = (1900, 1950, 1960, 1980, 1990, 2000),
) -> pd.DataFrame:
    """Compare candidate start years using completeness and zero-Total rates."""
    rows = []

    for start_year in candidate_years:
        subset = df[df["Year"] >= start_year]
        total_rows = len(subset)
        complete_rows = subset[CORE_COLUMNS].notna().all(axis=1).sum()
        valid_total = subset["Total"].dropna()

        rows.append({
            "Start Year": start_year,
            "Rows": total_rows,
            "Core Complete Rows": int(complete_rows),
            "Core Complete %": round(complete_rows / total_rows * 100, 1),
            "Zero Total %": round((valid_total.eq(0).sum() / len(valid_total)) * 100, 1),
        })

    return pd.DataFrame(rows)


def identify_excluded_entities(df: pd.DataFrame) -> pd.DataFrame:
    """Reproduce the notebook rule for historical/aggregate/special entities."""
    entity_reference = (
        df[["Country", "ISO 3166-1 alpha-3"]]
        .drop_duplicates()
        .sort_values("Country")
        .reset_index(drop=True)
    )

    missing_iso = entity_reference[entity_reference["ISO 3166-1 alpha-3"].isna()]
    known_special = entity_reference[
        entity_reference["Country"].isin(["Global", "International Transport"])
    ]

    return (
        pd.concat([missing_iso, known_special])
        .drop_duplicates()
        .sort_values("Country")
        .reset_index(drop=True)
    )


def build_forecasting_dataset(
    df: pd.DataFrame,
    start_year: int = 1960,
) -> tuple[pd.DataFrame, dict[str, object]]:
    """Construct the leakage-safe one-year-ahead complete-case modelling table."""
    excluded = identify_excluded_entities(df)

    model_df = df[
        (df["Year"] >= start_year)
        & (~df["Country"].isin(excluded["Country"]))
    ].copy()
    model_df = model_df.sort_values(["Country", "Year"]).reset_index(drop=True)

    grouped = model_df.groupby("Country")
    model_df[TARGET_COLUMN] = grouped["Total"].shift(-1)
    model_df["Target_Year"] = grouped["Year"].shift(-1)

    for source_col, lagged_col in LAGGED_NAME_MAP.items():
        model_df[lagged_col] = model_df[source_col]

    forecast_rows = model_df[model_df[TARGET_COLUMN].notna()].copy()
    complete_mask = forecast_rows[FEATURE_COLUMNS].notna().all(axis=1)
    final_model_df = forecast_rows[complete_mask].copy()

    gap = final_model_df["Target_Year"] - final_model_df["Year"]
    if not gap.eq(1).all():
        raise ValueError("Target construction produced a forecast gap other than one year.")

    diagnostics = {
        "start_year": start_year,
        "excluded_entities": excluded["Country"].tolist(),
        "excluded_entity_count": int(len(excluded)),
        "provisional_rows": int(len(model_df)),
        "provisional_entities": int(model_df["Country"].nunique()),
        "valid_target_rows": int(len(forecast_rows)),
        "complete_case_rows": int(len(final_model_df)),
        "complete_case_entities": int(final_model_df["Country"].nunique()),
        "predictor_year_min": int(final_model_df["Year"].min()),
        "predictor_year_max": int(final_model_df["Year"].max()),
    }

    return final_model_df, diagnostics


def chronological_split(
    model_df: pd.DataFrame,
    train_end: int = 2014,
    validation_start: int = 2015,
    validation_end: int = 2017,
    test_start: int = 2018,
    test_end: int = 2020,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Split observations in time order; no random shuffling is used."""
    train = model_df[model_df["Year"] <= train_end].copy()
    validation = model_df[
        model_df["Year"].between(validation_start, validation_end)
    ].copy()
    test = model_df[model_df["Year"].between(test_start, test_end)].copy()
    return train, validation, test


def split_summary(
    train: pd.DataFrame,
    validation: pd.DataFrame,
    test: pd.DataFrame,
) -> pd.DataFrame:
    """Return a compact evidence table for the chronological split."""
    rows = []
    for name, frame in (
        ("Training", train),
        ("Validation", validation),
        ("Test", test),
    ):
        rows.append({
            "Split": name,
            "Predictor Start Year": int(frame["Year"].min()),
            "Predictor End Year": int(frame["Year"].max()),
            "Rows": int(len(frame)),
            "Entities": int(frame["Country"].nunique()),
        })
    return pd.DataFrame(rows)


def regression_metrics(y_true, y_pred) -> dict[str, float]:
    """Calculate the three project regression metrics."""
    return {
        "MAE": float(mean_absolute_error(y_true, y_pred)),
        "RMSE": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "R2": float(r2_score(y_true, y_pred)),
    }


def evaluate_initial_models(
    train: pd.DataFrame,
    validation: pd.DataFrame,
    random_state: int = 42,
) -> tuple[pd.DataFrame, dict[str, object]]:
    """Fit the Milestone 3 initial models and compare them on validation data."""
    X_train = train[FEATURE_COLUMNS]
    y_train = train[TARGET_COLUMN]
    X_val = validation[FEATURE_COLUMNS]
    y_val = validation[TARGET_COLUMN]

    predictions = {
        "Persistence Baseline": validation["Total_lag1"],
    }

    models = {
        "Linear Regression": LinearRegression(),
        "Random Forest": RandomForestRegressor(
            n_estimators=200,
            random_state=random_state,
            n_jobs=-1,
        ),
        "Gradient Boosting": GradientBoostingRegressor(random_state=random_state),
    }

    for name, model in models.items():
        model.fit(X_train, y_train)
        predictions[name] = model.predict(X_val)

    rows = []
    for name in (
        "Persistence Baseline",
        "Linear Regression",
        "Random Forest",
        "Gradient Boosting",
    ):
        rows.append({"Model": name, **regression_metrics(y_val, predictions[name])})

    return pd.DataFrame(rows), models


def run_poc(csv_path: str | Path) -> dict[str, object]:
    """Run the compact end-to-end proof-of-concept pipeline."""
    df = load_emissions_data(csv_path)
    period_assessment = assess_modelling_periods(df)
    model_df, diagnostics = build_forecasting_dataset(df, start_year=1960)
    train, validation, test = chronological_split(model_df)
    comparison, models = evaluate_initial_models(train, validation)

    return {
        "raw_data": df,
        "period_assessment": period_assessment,
        "model_data": model_df,
        "diagnostics": diagnostics,
        "train": train,
        "validation": validation,
        "test": test,
        "split_summary": split_summary(train, validation, test),
        "initial_model_comparison": comparison,
        "models": models,
    }
