import pandas as pd
from modules.ai_insights import generate_ai_insights


def sample():
    return pd.DataFrame({
        "order_date": pd.to_datetime(["2025-01-04","2025-01-15","2025-02-03","2025-02-20"]),
        "sales": [100, 50, 200, 100],
        "order_id": ["A","B","C","D"],
        "product": ["Pen","Book","Book","Pen"],
        "category": ["Office","Books","Books","Office"],
        "region": ["North","South","North","South"],
        "profit": [10,-5,40,15],
    })


def test_generates_insights_and_recommendations():
    result = generate_ai_insights(sample())
    assert result["insights"]
    assert result["recommendations"]
    assert any("Top product" in x for x in result["insights"])


def test_empty_data_is_handled():
    result = generate_ai_insights(pd.DataFrame())
    assert result["insights"] == []
    assert "No data" in result["summary"]
