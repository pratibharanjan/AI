import pandas as pd
from modules.report_generator import build_excel_report, build_pdf_report


def frames():
    kpis = {
        "total_revenue": 450.0, "total_orders": 4, "units_sold": 9,
        "total_profit": 60.0, "average_order_value": 112.5,
        "profit_margin_pct": 13.33,
    }
    monthly = pd.DataFrame({"month": ["2025-01", "2025-02"], "sales": [150, 300], "mom_growth_pct": [None, 100]})
    products = pd.DataFrame({"product": ["Book"], "sales": [300]})
    categories = pd.DataFrame({"category": ["Books"], "sales": [300]})
    regions = pd.DataFrame({"region": ["North"], "sales": [450]})
    data = pd.DataFrame({"order_date": pd.to_datetime(["2025-01-01"]), "sales": [450]})
    return data, kpis, monthly, products, categories, regions


def test_excel_report_is_created():
    data, k, m, p, c, r = frames()
    content = build_excel_report(data, k, m, p, c, r)
    assert content[:2] == b"PK"


def test_pdf_report_is_created():
    data, k, m, p, c, r = frames()
    content = build_pdf_report(k, m, p, c, r)
    assert content.startswith(b"%PDF")
