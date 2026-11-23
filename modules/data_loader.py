"""File loading and column detection for the AI Sales Analytics project."""
from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Any

import pandas as pd


SUPPORTED_EXTENSIONS = {".xlsx", ".xls", ".csv"}

COLUMN_ALIASES = {
    "order_id": ["order id", "order_id", "invoice", "invoice no", "transaction id", "order number"],
    "order_date": ["order date", "order_date", "date", "transaction date", "invoice date"],
    "product": ["product name", "product", "item", "description", "product_name"],
    "category": ["category", "product category", "sub-category", "subcategory"],
    "quantity": ["quantity", "qty", "units", "units sold"],
    "sales": ["sales", "revenue", "amount", "total sales", "net sales", "line total"],
    "profit": ["profit", "gross profit", "net profit"],
    "region": ["region", "area", "territory", "state", "market"],
    "unit_price": ["unit price", "unit_price", "price", "selling price"],
    "cost_price": ["cost price", "cost_price", "unit cost", "cost"],
}


def _normalise_header(value: Any) -> str:
    return " ".join(str(value).strip().lower().replace("_", " ").replace("-", " ").split())


def detect_columns(columns: list[Any]) -> dict[str, str | None]:
    """Return best-effort semantic-to-original column mapping."""
    normalized = {_normalise_header(col): str(col) for col in columns}
    result: dict[str, str | None] = {}
    for semantic, aliases in COLUMN_ALIASES.items():
        result[semantic] = next(
            (normalized[alias] for alias in aliases if alias in normalized),
            None,
        )
    return result


def load_uploaded_file(uploaded_file: Any) -> tuple[pd.DataFrame, str]:
    """Load an uploaded CSV/XLS/XLSX file. Excel workbooks use the first sheet."""
    name = getattr(uploaded_file, "name", "uploaded_file")
    suffix = Path(name).suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError("Unsupported file type. Please upload an .xlsx, .xls, or .csv file.")

    raw = uploaded_file.getvalue() if hasattr(uploaded_file, "getvalue") else uploaded_file.read()
    if not raw:
        raise ValueError("The uploaded file is empty.")

    try:
        if suffix == ".csv":
            frame = pd.read_csv(BytesIO(raw))
            sheet = "CSV"
        else:
            workbook = pd.ExcelFile(BytesIO(raw))
            if not workbook.sheet_names:
                raise ValueError("The Excel workbook does not contain any worksheets.")
            sheet = workbook.sheet_names[0]
            frame = pd.read_excel(workbook, sheet_name=sheet)
    except Exception as exc:
        raise ValueError(f"Could not read the uploaded file: {exc}") from exc

    if frame.empty:
        raise ValueError("The selected worksheet contains no data rows.")
    frame.columns = [str(c).strip() for c in frame.columns]
    if frame.columns.duplicated().any():
        duplicates = frame.columns[frame.columns.duplicated()].tolist()
        raise ValueError(f"Duplicate column names found: {duplicates}. Rename them and upload again.")
    return frame, sheet
