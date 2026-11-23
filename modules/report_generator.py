"""PDF and Excel report generation for AI Sales Analytics."""
from __future__ import annotations

from io import BytesIO
from datetime import datetime
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether
)


def build_excel_report(df: pd.DataFrame, kpis: dict, monthly: pd.DataFrame,
                       products: pd.DataFrame, categories: pd.DataFrame,
                       regions: pd.DataFrame, insights: dict | None = None) -> bytes:
    """Return a multi-sheet Excel report as bytes."""
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        pd.DataFrame([kpis]).to_excel(writer, sheet_name="KPI Summary", index=False)
        df.to_excel(writer, sheet_name="Cleaned Data", index=False)
        monthly.to_excel(writer, sheet_name="Monthly Revenue", index=False)
        products.to_excel(writer, sheet_name="Product Performance", index=False)
        categories.to_excel(writer, sheet_name="Category Performance", index=False)
        regions.to_excel(writer, sheet_name="Regional Performance", index=False)
        if insights:
            rows = ([{"Type": "Insight", "Text": x} for x in insights.get("insights", [])] +
                    [{"Type": "Recommendation", "Text": x} for x in insights.get("recommendations", [])])
            pd.DataFrame(rows, columns=["Type", "Text"]).to_excel(writer, sheet_name="AI Insights", index=False)
        # Make each sheet easier to read in Excel.
        for ws in writer.book.worksheets:
            ws.freeze_panes = "A2"
            ws.auto_filter.ref = ws.dimensions
            for column_cells in ws.columns:
                values = [len(str(c.value)) if c.value is not None else 0 for c in column_cells[:200]]
                width = min(max(max(values, default=10) + 2, 12), 42)
                ws.column_dimensions[column_cells[0].column_letter].width = width
    return output.getvalue()


def build_pdf_report(kpis: dict, monthly: pd.DataFrame, products: pd.DataFrame,
                     categories: pd.DataFrame, regions: pd.DataFrame,
                     insights: dict | None = None, title: str = "AI Sales Analytics Report") -> bytes:
    """Return a concise PDF report with KPI, trend and performance tables."""
    output = BytesIO()
    doc = SimpleDocTemplate(
        output, pagesize=A4, rightMargin=17*mm, leftMargin=17*mm,
        topMargin=17*mm, bottomMargin=17*mm, title=title
    )
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="ReportTitle", parent=styles["Title"], fontName="Helvetica-Bold",
                               fontSize=20, leading=25, textColor=colors.HexColor("#17324d"),
                               alignment=TA_LEFT, spaceAfter=5*mm))
    styles.add(ParagraphStyle(name="SectionBlue", parent=styles["Heading2"], fontSize=12,
                               leading=15, textColor=colors.HexColor("#147d92"),
                               spaceBefore=5*mm, spaceAfter=2*mm))
    styles.add(ParagraphStyle(name="SmallNote", parent=styles["BodyText"], fontSize=8,
                               leading=10, textColor=colors.HexColor("#536273")))
    story = [
        Paragraph(title, styles["ReportTitle"]),
        Paragraph(f"Generated on {datetime.now().strftime('%d %B %Y, %I:%M %p')}", styles["SmallNote"]),
        Spacer(1, 5*mm),
        Paragraph("Key performance indicators", styles["SectionBlue"]),
    ]

    def fmt(value):
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return "N/A"
        if isinstance(value, (int, float)):
            return f"{value:,.2f}"
        return str(value)

    kpi_rows = [["Metric", "Value"]]
    labels = [
        ("total_revenue", "Total revenue"),
        ("total_orders", "Total orders"),
        ("units_sold", "Units sold"),
        ("total_profit", "Total profit"),
        ("average_order_value", "Average order value"),
        ("profit_margin_pct", "Profit margin (%)"),
    ]
    for key, label in labels:
        if key in kpis:
            kpi_rows.append([label, fmt(kpis[key])])
    table = Table(kpi_rows, colWidths=[85*mm, 75*mm], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(-1,0), colors.HexColor("#17324d")),
        ("TEXTCOLOR", (0,0),(-1,0), colors.white),
        ("FONTNAME", (0,0),(-1,0), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0,1),(-1,-1), [colors.white, colors.HexColor("#eef3f7")]),
        ("GRID", (0,0),(-1,-1), .35, colors.HexColor("#d2dbe4")),
        ("PADDING", (0,0),(-1,-1), 7),
    ]))
    story.append(table)

    def add_frame(title_text, frame, columns, max_rows=10):
        if frame is None or frame.empty:
            return
        story.append(Paragraph(title_text, styles["SectionBlue"]))
        use = frame.loc[:, [c for c in columns if c in frame.columns]].head(max_rows).copy()
        rows = [list(use.columns)]
        for row in use.itertuples(index=False, name=None):
            rows.append([fmt(v) for v in row])
        widths = [160*mm / max(1, len(rows[0]))] * len(rows[0])
        t = Table(rows, colWidths=widths, repeatRows=1)
        t.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#17324d")),
            ("TEXTCOLOR",(0,0),(-1,0),colors.white),
            ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
            ("FONTSIZE",(0,0),(-1,-1),8),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#eef3f7")]),
            ("GRID",(0,0),(-1,-1),.3,colors.HexColor("#d2dbe4")),
            ("PADDING",(0,0),(-1,-1),5),
        ]))
        story.append(t)

    add_frame("Monthly revenue", monthly, ["month", "sales", "mom_growth_pct"])
    add_frame("Top products", products, ["product", "sales", "profit", "quantity"])
    add_frame("Category performance", categories, ["category", "sales", "revenue_share_pct"])
    add_frame("Regional performance", regions, ["region", "sales", "profit"])
    if insights:
        story.append(Paragraph("AI-generated insights", styles["SectionBlue"]))
        for item in insights.get("insights", []):
            story.append(Paragraph(f"• {item}", styles["BodyText"]))
            story.append(Spacer(1, 1.5*mm))
        story.append(Paragraph("Suggested actions", styles["SectionBlue"]))
        for item in insights.get("recommendations", []):
            story.append(Paragraph(f"• {item}", styles["BodyText"]))
            story.append(Spacer(1, 1.5*mm))
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph(
        "This report is based on the selected and filtered dataset. Forecasts and automated insights are estimates and should be reviewed in business context.",
        styles["SmallNote"]
    ))
    doc.build(story)
    return output.getvalue()
