"""Validation, cleaning, and standardisation for sales datasets."""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


REQUIRED_SEMANTICS = ["order_date", "sales"]


def clean_sales_data(
    source: pd.DataFrame,
    mapping: dict[str, str | None],
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """
    Standardise selected source columns into canonical names.

    Required: order_date and sales.
    Optional: order_id, product, category, quantity, profit, region, unit_price, cost_price.
    Invalid dates and non-numeric sales rows are excluded and counted in the report.
    """
    if source is None or source.empty:
        raise ValueError("No data was provided.")

    missing = [key for key in REQUIRED_SEMANTICS if not mapping.get(key)]
    if missing:
        raise ValueError(
            "Required columns are not mapped: " + ", ".join(missing) +
            ". Select a date column and a sales/revenue column."
        )

    selected = {semantic: original for semantic, original in mapping.items()
                if original and original in source.columns}
    if "order_date" not in selected or "sales" not in selected:
        raise ValueError("Please map both Order Date and Sales columns.")

    rename = {original: semantic for semantic, original in selected.items()}
    df = source[list(rename.keys())].rename(columns=rename).copy()
    original_rows = len(df)

    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce", dayfirst=False)
    for col in ["sales", "quantity", "profit", "unit_price", "cost_price"]:
        if col in df.columns:
            # Remove common currency symbols and thousands separators.
            cleaned = (
                df[col].astype(str)
                .str.replace(",", "", regex=False)
                .str.replace("₹", "", regex=False)
                .str.replace("$", "", regex=False)
                .str.replace("£", "", regex=False)
                .str.strip()
            )
            df[col] = pd.to_numeric(cleaned, errors="coerce")

    invalid_date = int(df["order_date"].isna().sum())
    invalid_sales = int(df["sales"].isna().sum())
    df = df.dropna(subset=["order_date", "sales"]).copy()

    duplicate_rows = int(df.duplicated().sum())
    if duplicate_rows:
        df = df.drop_duplicates().copy()

    for col in ["order_id", "product", "category", "region"]:
        if col in df.columns:
            df[col] = df[col].astype("string").str.strip()
            df[col] = df[col].replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})

    if "quantity" in df.columns:
        # Keep unknown quantities as missing; do not invent units sold.
        df.loc[df["quantity"] < 0, "quantity"] = np.nan

    if "profit" not in df.columns and {"quantity", "unit_price", "cost_price"}.issubset(df.columns):
        df["profit"] = df["quantity"] * (df["unit_price"] - df["cost_price"])

    df["month"] = df["order_date"].dt.to_period("M").dt.to_timestamp()
    df["year"] = df["order_date"].dt.year
    df["month_name"] = df["order_date"].dt.strftime("%b")

    report = {
        "original_rows": original_rows,
        "clean_rows": len(df),
        "removed_invalid_dates": invalid_date,
        "removed_invalid_sales": invalid_sales,
        "removed_duplicates": duplicate_rows,
        "optional_fields_available": [
            field for field in ["order_id", "product", "category", "quantity", "profit", "region"]
            if field in df.columns
        ],
    }
    if df.empty:
        raise ValueError("No valid records remain after cleaning. Check the date and sales mappings.")
    return df.sort_values("order_date").reset_index(drop=True), report
