"""Transparent, rule-based sales insights from the selected dataset."""
from __future__ import annotations

import pandas as pd


def generate_ai_insights(df: pd.DataFrame) -> dict:
    """Generate readable observations and practical recommendations.

    This is a local, rule-based insight engine. It does not call an external
    generative-AI API or send the user's dataset anywhere.
    """
    if df is None or df.empty:
        return {"summary": "No data is available for analysis.", "insights": [], "recommendations": []}

    data = df.copy()
    data["order_date"] = pd.to_datetime(data["order_date"], errors="coerce")
    data["sales"] = pd.to_numeric(data["sales"], errors="coerce")
    data = data.dropna(subset=["order_date", "sales"])
    if data.empty:
        return {"summary": "No valid date and sales values were found.", "insights": [], "recommendations": []}

    total = float(data["sales"].sum())
    orders = int(data["order_id"].nunique()) if "order_id" in data.columns else int(len(data))
    monthly = data.assign(month=data["order_date"].dt.to_period("M")).groupby("month")["sales"].sum().sort_index()
    insights, recommendations = [], []

    insights.append(f"The selected records contain {len(data):,} valid transactions/rows and {total:,.2f} in total revenue across {orders:,} distinct orders or rows.")

    if len(monthly) >= 2:
        first, last = float(monthly.iloc[0]), float(monthly.iloc[-1])
        if first > 0:
            change = (last - first) / first * 100
            direction = "increased" if change > 0 else "decreased" if change < 0 else "stayed level"
            insights.append(f"Revenue {direction} by {abs(change):.1f}% from the first observed month to the latest observed month.")
        peak_month = str(monthly.idxmax())
        low_month = str(monthly.idxmin())
        insights.append(f"Highest-revenue month: {peak_month} ({float(monthly.max()):,.2f}). Lowest-revenue month: {low_month} ({float(monthly.min()):,.2f}).")
        if len(monthly) >= 3:
            recent = float(monthly.iloc[-1])
            previous = float(monthly.iloc[-2])
            if previous > 0:
                mom = (recent - previous) / previous * 100
                insights.append(f"Latest month changed {mom:+.1f}% compared with the previous month.")
                if mom < -10:
                    recommendations.append("Review the latest month's product mix, order volume, discounts and regional results to understand the revenue decline.")
                elif mom > 10:
                    recommendations.append("Check which products and regions drove the recent increase, then assess whether the improvement is repeatable.")

    if "product" in data.columns and data["product"].notna().any():
        product_sales = data.groupby("product")["sales"].sum().sort_values(ascending=False)
        best_name, best_value = str(product_sales.index[0]), float(product_sales.iloc[0])
        insights.append(f"Top product by revenue: {best_name} ({best_value:,.2f}).")
        if total > 0 and best_value / total >= 0.5:
            recommendations.append(f"Revenue is highly concentrated in {best_name}. Monitor its stock and consider reducing dependence on a single product.")
        if len(product_sales) > 1:
            weak_name, weak_value = str(product_sales.index[-1]), float(product_sales.iloc[-1])
            insights.append(f"Lowest-revenue product in the selected data: {weak_name} ({weak_value:,.2f}).")
            recommendations.append(f"Review demand, pricing and promotion history for {weak_name} before deciding whether to improve, reposition or discontinue it.")

    if "category" in data.columns and data["category"].notna().any():
        cat = data.groupby("category")["sales"].sum().sort_values(ascending=False)
        if len(cat):
            share = float(cat.iloc[0] / total * 100) if total > 0 else 0
            insights.append(f"Leading category: {cat.index[0]} ({share:.1f}% of revenue).")
            if share >= 60:
                recommendations.append("The leading category contributes a large share of revenue. Track its performance separately and look for opportunities to grow other categories.")

    if "region" in data.columns and data["region"].notna().any():
        reg = data.groupby("region")["sales"].sum().sort_values(ascending=False)
        if len(reg) > 1:
            insights.append(f"Highest-revenue region: {reg.index[0]} ({float(reg.iloc[0]):,.2f}); lowest: {reg.index[-1]} ({float(reg.iloc[-1]):,.2f}).")
            recommendations.append(f"Compare customer demand, product availability and marketing activity in {reg.index[-1]} with stronger regions.")

    if "profit" in data.columns:
        profit = pd.to_numeric(data["profit"], errors="coerce").dropna()
        if not profit.empty:
            loss_rows = int((profit < 0).sum())
            insights.append(f"Profit is available for {len(profit):,} rows; {loss_rows:,} rows have negative profit.")
            if loss_rows:
                recommendations.append("Inspect loss-making transactions for discount levels, shipping costs, pricing and product costs.")

    if not recommendations:
        recommendations.append("Continue monitoring monthly revenue and compare product, category and regional performance as more data becomes available.")

    return {
        "summary": f"Analysis of {len(data):,} valid rows across {len(monthly):,} observed months.",
        "insights": insights,
        "recommendations": recommendations,
    }
