"""Plotly charts for Phase 3."""
import plotly.express as px


def monthly_revenue_chart(monthly):
    return px.line(monthly, x="month", y="revenue", markers=True,
                   title="Monthly Revenue Trend", template="plotly_dark",
                   labels={"month": "Month", "revenue": "Revenue"})


def product_chart(products, top_n=10):
    data = products.head(top_n).sort_values("sales", ascending=True)
    return px.bar(data, x="sales", y="product", orientation="h",
                  title=f"Top {top_n} Products by Revenue", template="plotly_dark",
                  labels={"sales": "Revenue", "product": "Product"})


def category_chart(categories):
    return px.bar(categories, x="category", y="sales", color="category",
                  title="Revenue by Category", template="plotly_dark",
                  labels={"sales": "Revenue", "category": "Category"})


def region_chart(regions):
    return px.bar(regions, x="region", y="sales", color="region",
                  title="Revenue by Region", template="plotly_dark",
                  labels={"sales": "Revenue", "region": "Region"})
