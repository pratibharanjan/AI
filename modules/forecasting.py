"""Monthly revenue forecasting using Holt-Winters Exponential Smoothing."""
from __future__ import annotations

import warnings
import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing


def monthly_series(df: pd.DataFrame) -> pd.Series:
    """Aggregate sales by calendar month and fill missing months within observed range with zero."""
    if df.empty or "order_date" not in df or "sales" not in df:
        raise ValueError("Valid order_date and sales columns are required.")
    series = (
        df.set_index(pd.to_datetime(df["order_date"]))["sales"]
        .astype(float)
        .resample("MS")
        .sum()
    )
    if series.empty:
        raise ValueError("No monthly revenue observations are available.")
    return series.asfreq("MS", fill_value=0.0)


def _fit_model(train: pd.Series):
    """Use additive seasonality only when at least two full annual cycles are available."""
    if len(train) >= 24:
        return ExponentialSmoothing(
            train, trend="add", seasonal="add", seasonal_periods=12,
            initialization_method="estimated"
        ).fit(optimized=True)
    if len(train) >= 3:
        return ExponentialSmoothing(
            train, trend="add", seasonal=None, initialization_method="estimated"
        ).fit(optimized=True)
    raise ValueError("At least 3 monthly observations are required for forecasting.")


def evaluate_forecast(series: pd.Series, holdout: int = 3) -> dict:
    """Chronological holdout evaluation; never randomly shuffles time-series data."""
    n = min(holdout, max(1, len(series) // 4))
    if len(series) < 6 or len(series) - n < 3:
        return {"mae": None, "rmse": None, "test_periods": 0,
                "message": "Not enough history for a reliable holdout evaluation."}
    train, actual = series.iloc[:-n], series.iloc[-n:]
    try:
        fitted = _fit_model(train)
        predicted = fitted.forecast(n)
        errors = actual.to_numpy() - predicted.to_numpy()
        return {
            "mae": float(np.mean(np.abs(errors))),
            "rmse": float(np.sqrt(np.mean(errors ** 2))),
            "test_periods": int(n),
            "message": "Metrics calculated on the most recent held-out months.",
        }
    except Exception as exc:
        return {"mae": None, "rmse": None, "test_periods": 0,
                "message": f"Evaluation unavailable: {exc}"}


def forecast_revenue(df: pd.DataFrame, horizon: int = 3) -> dict:
    """Fit an appropriate Holt-Winters model and forecast future monthly revenue."""
    if horizon not in (3, 6):
        raise ValueError("Forecast horizon must be 3 or 6 months.")
    series = monthly_series(df)
    if len(series) < 3:
        raise ValueError("At least 3 months of data are required. Upload more historical data.")

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        fitted = _fit_model(series)
        prediction = fitted.forecast(horizon)

    future_index = pd.date_range(
        series.index[-1] + pd.offsets.MonthBegin(1), periods=horizon, freq="MS"
    )
    forecast_df = pd.DataFrame({
        "month": future_index,
        "predicted_revenue": np.maximum(prediction.to_numpy(dtype=float), 0),
    })
    evaluation = evaluate_forecast(series)
    seasonal = len(series) >= 24
    return {
        "history": series.rename("actual_revenue").reset_index(names="month"),
        "forecast": forecast_df,
        "evaluation": evaluation,
        "model_name": "Holt-Winters additive trend and seasonality" if seasonal
                      else "Holt linear trend (seasonality unavailable)",
        "seasonality_used": seasonal,
        "observations": int(len(series)),
        "horizon": horizon,
    }
