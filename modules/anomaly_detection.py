"""Monthly revenue anomaly detection using Isolation Forest."""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest


def detect_revenue_anomalies(df: pd.DataFrame, contamination: float = 0.10) -> dict:
    """
    Flag unusual monthly revenue observations.
    Requires at least 8 months; results are statistical flags, not proof of business problems.
    """
    if df.empty or not {"order_date", "sales"}.issubset(df.columns):
        raise ValueError("Valid order_date and sales columns are required.")

    monthly = (
        df.set_index(pd.to_datetime(df["order_date"]))["sales"]
        .astype(float).resample("MS").sum().asfreq("MS", fill_value=0.0)
    )
    result = monthly.rename("revenue").reset_index(names="month")
    if len(result) < 8:
        return {
            "data": result.assign(is_anomaly=False, anomaly_label="Insufficient history"),
            "anomaly_count": 0,
            "message": "At least 8 monthly observations are required for anomaly detection.",
            "method": "Isolation Forest",
        }

    # Use revenue plus first difference to capture both unusual levels and abrupt changes.
    features = pd.DataFrame({
        "revenue": monthly,
        "change": monthly.diff().fillna(0),
    })
    model = IsolationForest(
        n_estimators=200,
        contamination=float(contamination),
        random_state=42,
    )
    labels = model.fit_predict(features)
    scores = model.decision_function(features)
    result["is_anomaly"] = labels == -1
    result["anomaly_score"] = scores
    result["anomaly_label"] = np.where(result["is_anomaly"], "Unusual pattern", "Normal")
    result["change_from_previous"] = monthly.diff().to_numpy()
    result["change_pct"] = monthly.pct_change().replace([np.inf, -np.inf], np.nan).to_numpy()
    count = int(result["is_anomaly"].sum())
    return {
        "data": result,
        "anomaly_count": count,
        "message": (
            f"Detected {count} unusual month(s). Review promotions, stock availability, "
            "one-off orders, data quality and other business context before taking action."
            if count else "No unusual monthly revenue patterns were flagged."
        ),
        "method": "Isolation Forest",
    }
