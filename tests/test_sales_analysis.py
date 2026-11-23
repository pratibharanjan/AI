import pandas as pd
from modules.sales_analysis import (
    calculate_kpis, monthly_revenue, product_performance,
    category_performance, generate_findings,
)


def sample():
    d = pd.DataFrame({
        "order_date": pd.to_datetime(["2025-01-01", "2025-01-10", "2025-02-01"]),
        "month": pd.to_datetime(["2025-01-01", "2025-01-01", "2025-02-01"]),
        "sales": [100.0, 200.0, 300.0],
        "order_id": ["A", "B", "C"],
        "product": ["Mouse", "Keyboard", "Mouse"],
        "category": ["Accessories", "Accessories", "Electronics"],
        "quantity": [1, 2, 3],
        "profit": [10.0, 20.0, 60.0],
        "region": ["North", "South", "North"],
    })
    return d


def test_kpis():
    k = calculate_kpis(sample())
    assert k["total_revenue"] == 600
    assert k["total_orders"] == 3
    assert k["units_sold"] == 6
    assert k["total_profit"] == 90


def test_monthly_growth():
    m = monthly_revenue(sample())
    assert len(m) == 2
    assert round(m.iloc[1]["mom_growth_pct"], 2) == 0.0


def test_product_and_category_aggregation():
    p = product_performance(sample())
    assert p.iloc[0]["product"] == "Mouse"
    c = category_performance(sample())
    assert round(c["revenue_share_pct"].sum(), 5) == 100.0


def test_findings_are_generated():
    assert len(generate_findings(sample())) >= 4
