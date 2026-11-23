import pandas as pd
import pytest
from modules.forecasting import monthly_series, forecast_revenue
from modules.anomaly_detection import detect_revenue_anomalies


def make_data(n=30):
    dates = pd.date_range("2023-01-01", periods=n, freq="MS")
    vals = [1000 + i * 30 + (100 if i % 12 in [10, 11] else 0) for i in range(n)]
    return pd.DataFrame({"order_date": dates, "sales": vals})


def test_monthly_series_aggregates():
    df = pd.DataFrame({
        "order_date": pd.to_datetime(["2025-01-02", "2025-01-20", "2025-03-01"]),
        "sales": [100, 200, 50],
    })
    s = monthly_series(df)
    assert len(s) == 3
    assert s.iloc[0] == 300
    assert s.iloc[1] == 0


def test_forecast_horizon():
    result = forecast_revenue(make_data(), 3)
    assert len(result["forecast"]) == 3
    assert (result["forecast"]["predicted_revenue"] >= 0).all()


def test_forecast_requires_enough_months():
    with pytest.raises(ValueError):
        forecast_revenue(make_data(2), 3)


def test_anomaly_detector_handles_short_history():
    result = detect_revenue_anomalies(make_data(5))
    assert result["anomaly_count"] == 0
    assert "At least 8" in result["message"]


def test_anomaly_detector_returns_month_flags():
    result = detect_revenue_anomalies(make_data(18))
    assert len(result["data"]) == 18
    assert "is_anomaly" in result["data"].columns
