"""Runtime and project diagnostics for AI Sales Analytics."""
from __future__ import annotations

import importlib.util
import platform
from pathlib import Path
import sys
import pandas as pd


REQUIRED_PACKAGES = [
    "streamlit", "pandas", "numpy", "plotly", "openpyxl",
    "sklearn", "statsmodels", "reportlab",
]
REQUIRED_FILES = [
    "app.py",
    "modules/data_loader.py",
    "modules/preprocessing.py",
    "modules/sales_analysis.py",
    "modules/visualizations.py",
    "modules/forecasting.py",
    "modules/anomaly_detection.py",
    "modules/ai_insights.py",
    "modules/report_generator.py",
]


def build_health_report(project_root: str | Path = ".",
                        dataframe: pd.DataFrame | None = None) -> dict:
    """Check Python packages, expected project files and an optional dataset."""
    root = Path(project_root).resolve()
    package_checks = []
    for package in REQUIRED_PACKAGES:
        available = importlib.util.find_spec(package) is not None
        package_checks.append({
            "check": f"Package: {package}",
            "status": "Ready" if available else "Missing",
            "details": "Importable in this Python environment" if available else "Install project requirements",
        })

    file_checks = []
    for relative in REQUIRED_FILES:
        exists = (root / relative).is_file()
        file_checks.append({
            "check": f"File: {relative}",
            "status": "Ready" if exists else "Missing",
            "details": "Found" if exists else "Expected project file was not found",
        })

    dataset_checks = []
    if dataframe is not None:
        required_columns = ["order_date", "sales"]
        for column in required_columns:
            ok = column in dataframe.columns
            dataset_checks.append({
                "check": f"Dataset column: {column}",
                "status": "Ready" if ok else "Missing",
                "details": f"{len(dataframe):,} rows currently loaded" if ok else "Required for core sales analysis",
            })
        if "order_date" in dataframe.columns:
            valid_dates = pd.to_datetime(dataframe["order_date"], errors="coerce").notna().sum()
            dataset_checks.append({
                "check": "Valid order dates",
                "status": "Ready" if valid_dates else "Warning",
                "details": f"{valid_dates:,} valid dates out of {len(dataframe):,} rows",
            })
        if "sales" in dataframe.columns:
            numeric_sales = pd.to_numeric(dataframe["sales"], errors="coerce").notna().sum()
            dataset_checks.append({
                "check": "Numeric sales values",
                "status": "Ready" if numeric_sales else "Warning",
                "details": f"{numeric_sales:,} numeric values out of {len(dataframe):,} rows",
            })

    checks = package_checks + file_checks + dataset_checks
    ready = sum(item["status"] == "Ready" for item in checks)
    missing = sum(item["status"] == "Missing" for item in checks)
    warnings = sum(item["status"] == "Warning" for item in checks)
    return {
        "python_version": platform.python_version(),
        "python_executable": sys.executable,
        "project_root": str(root),
        "checks": checks,
        "ready_count": ready,
        "missing_count": missing,
        "warning_count": warnings,
        "overall_status": "Ready" if missing == 0 and warnings == 0 else "Needs attention",
    }
