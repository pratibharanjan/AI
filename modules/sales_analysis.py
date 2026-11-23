"""EDA and business calculations for uploaded sales data."""
from __future__ import annotations
import pandas as pd
import numpy as np


def _has(df: pd.DataFrame, col: str) -> bool:
    return col in df.columns and df[col].notna().any()


def calculate_kpis(df: pd.DataFrame) -> dict:
    if df.empty:
        raise ValueError("No valid sales records are available for analysis.")
    revenue = float(df["sales"].sum())
    orders = int(df["order_id"].nunique()) if _has(df, "order_id") else int(len(df))
    units = float(df["quantity"].sum()) if _has(df, "quantity") else None
    profit = float(df["profit"].sum()) if _has(df, "profit") else None
    aov = revenue / orders if orders else None
    margin = (profit / revenue * 100) if profit is not None and revenue else None
    return {
        "total_revenue": revenue,
        "total_orders": orders,
        "units_sold": units,
        "total_profit": profit,
        "average_order_value": aov,
        "profit_margin_pct": margin,
        "transaction_rows": int(len(df)),
    }


def monthly_revenue(df: pd.DataFrame) -> pd.DataFrame:
    out = df.groupby("month", as_index=False)["sales"].sum().sort_values("month")
    out = out.rename(columns={"sales": "revenue"})
    out["previous_month_revenue"] = out["revenue"].shift(1)
    out["mom_growth_pct"] = np.where(
        out["previous_month_revenue"].notna() & (out["previous_month_revenue"] != 0),
        (out["revenue"] - out["previous_month_revenue"]) / out["previous_month_revenue"] * 100,
        np.nan,
    )
    return out


def product_performance(df: pd.DataFrame) -> pd.DataFrame:
    if not _has(df, "product"):
        return pd.DataFrame()
    agg = {"sales": "sum"}
    if _has(df, "quantity"):
        agg["quantity"] = "sum"
    if _has(df, "profit"):
        agg["profit"] = "sum"
    out = df.groupby("product", dropna=True).agg(agg).reset_index()
    return out.sort_values("sales", ascending=False)


def category_performance(df: pd.DataFrame) -> pd.DataFrame:
    if not _has(df, "category"):
        return pd.DataFrame()
    agg = {"sales": "sum"}
    if _has(df, "quantity"):
        agg["quantity"] = "sum"
    if _has(df, "profit"):
        agg["profit"] = "sum"
    out = df.groupby("category", dropna=True).agg(agg).reset_index()
    out["revenue_share_pct"] = out["sales"] / out["sales"].sum() * 100 if out["sales"].sum() else 0
    return out.sort_values("sales", ascending=False)


def regional_performance(df: pd.DataFrame) -> pd.DataFrame:
    if not _has(df, "region"):
        return pd.DataFrame()
    agg = {"sales": "sum"}
    if _has(df, "profit"):
        agg["profit"] = "sum"
    if _has(df, "quantity"):
        agg["quantity"] = "sum"
    return df.groupby("region", dropna=True).agg(agg).reset_index().sort_values("sales", ascending=False)


def descriptive_statistics(df: pd.DataFrame) -> pd.DataFrame:
    numeric = [c for c in ["sales", "quantity", "profit"] if _has(df, c)]
    if not numeric:
        return pd.DataFrame()
    return df[numeric].describe().T.reset_index(names="metric")


def correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    numeric = [c for c in ["sales", "quantity", "profit"] if _has(df, c)]
    if len(numeric) < 2:
        return pd.DataFrame()
    return df[numeric].corr(numeric_only=True)


def generate_findings(df: pd.DataFrame) -> list[str]:
    """Generate deterministic observations from computed data; no invented claims."""
    findings = []
    kpis = calculate_kpis(df)
    findings.append(f"Total recorded revenue is {kpis['total_revenue']:,.2f} across {kpis['total_orders']:,} orders/records.")
    monthly = monthly_revenue(df)
    if not monthly.empty:
        peak = monthly.loc[monthly["revenue"].idxmax()]
        low = monthly.loc[monthly["revenue"].idxmin()]
        findings.append(f"Highest-revenue month: {peak['month']:%B %Y} ({peak['revenue']:,.2f}).")
        findings.append(f"Lowest-revenue month: {low['month']:%B %Y} ({low['revenue']:,.2f}).")
        valid_growth = monthly.dropna(subset=["mom_growth_pct"])
        if not valid_growth.empty:
            latest = valid_growth.iloc[-1]
            direction = "increased" if latest["mom_growth_pct"] >= 0 else "decreased"
            findings.append(f"Revenue {direction} by {abs(latest['mom_growth_pct']):.1f}% in {latest['month']:%B %Y} compared with the previous recorded month.")
    products = product_performance(df)
    if not products.empty:
        p = products.iloc[0]
        findings.append(f"Highest-revenue product: {p['product']} ({p['sales']:,.2f} in sales).")
    categories = category_performance(df)
    if not categories.empty:
        c = categories.iloc[0]
        findings.append(f"Leading category by revenue: {c['category']} ({c['revenue_share_pct']:.1f}% of recorded revenue).")
    regions = regional_performance(df)
    if not regions.empty:
        r = regions.iloc[0]
        findings.append(f"Leading region by revenue: {r['region']} ({r['sales']:,.2f}).")
    if kpis["total_profit"] is not None:
        findings.append(f"Recorded total profit is {kpis['total_profit']:,.2f}.")
    return findings
