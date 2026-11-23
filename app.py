from __future__ import annotations

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from modules.data_loader import detect_columns, load_uploaded_file
from modules.preprocessing import clean_sales_data
from modules.sales_analysis import (
    calculate_kpis, monthly_revenue, product_performance,
    category_performance, regional_performance,
    descriptive_statistics, correlation_matrix, generate_findings,
)
from modules.visualizations import (
    monthly_revenue_chart, product_chart, category_chart, region_chart,
)
from modules.forecasting import forecast_revenue
from modules.anomaly_detection import detect_revenue_anomalies
from modules.ai_insights import generate_ai_insights
from modules.report_generator import build_excel_report, build_pdf_report
from modules.project_health import build_health_report

st.set_page_config(page_title="AI Sales Intelligence", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
:root { color-scheme: dark; }
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: radial-gradient(ellipse at 15% 0%, #15223a 0%, #0a1020 46%); color: #edf2fa; }
[data-testid="stHeader"] { background: rgba(10,16,32,.82); }
[data-testid="stSidebar"] { background: #0d1729; border-right: 1px solid #263650; }
.block-container { max-width: 1500px; padding-top: 2rem; padding-bottom: 3rem; }
h1,h2,h3 { font-family: 'Space Grotesk', sans-serif !important; color: #f4f7fc !important; }
[data-testid="stMetric"] { background: linear-gradient(145deg,#17263e,#111b2e); border: 1px solid #2a3b56; border-radius: 15px; padding: 17px; }
[data-testid="stMetricLabel"] { color: #9eafc5 !important; }
[data-testid="stMetricValue"] { color: #f3f7fc !important; }
.stButton > button,.stDownloadButton > button { border-radius: 10px; border: 1px solid #31506d; background: #18314a; color: #eaf6fb; font-weight: 600; }
[data-testid="stFileUploader"] { background: #111d31; border: 1px dashed #3a536f; border-radius: 14px; padding: 15px; }
[data-testid="stDataFrame"] { border: 1px solid #263650; border-radius: 12px; }
div[data-testid="stExpander"] { background: rgba(17,27,46,.72); border: 1px solid #263650; border-radius: 12px; }
.hero { background: linear-gradient(110deg,rgba(27,58,82,.92),rgba(19,34,57,.92) 58%,rgba(28,49,71,.88)); border:1px solid #31506a; border-radius:18px; padding:23px 26px; margin-bottom:22px; }
.hero-kicker { color:#77d5df; text-transform:uppercase; letter-spacing:.15em; font-size:.69rem; font-weight:700; }
.hero-title { font-family:'Space Grotesk',sans-serif; font-size:1.7rem; color:#f6fbff; font-weight:700; margin-top:6px; }
.hero-sub { color:#b7c8d9; margin-top:5px; font-size:.92rem; }
.section-kicker { color:#70c9d8; text-transform:uppercase; letter-spacing:.13em; font-size:.68rem; font-weight:700; margin-bottom:4px; }
.insight { background:#121f33; border:1px solid #293d59; border-left:3px solid #55c2d8; border-radius:10px; padding:13px 15px; margin:8px 0; color:#dce7f4; }
</style>
""", unsafe_allow_html=True)


def money(value):
    return "N/A" if value is None else f"{value:,.2f}"


def hero(title, subtitle, kicker="SALES INTELLIGENCE"):
    st.markdown(f'<div class="hero"><div class="hero-kicker">{kicker}</div><div class="hero-title">{title}</div><div class="hero-sub">{subtitle}</div></div>', unsafe_allow_html=True)


def section(title, subtitle=None):
    st.markdown(f'<div class="section-kicker">ANALYTICS</div><h2>{title}</h2>', unsafe_allow_html=True)
    if subtitle:
        st.caption(subtitle)


with st.sidebar:
    st.markdown("## ◈ SALES INTELLIGENCE")
    st.caption("AI-powered business analytics")
    st.divider()
    page = st.radio("WORKSPACE", ["Overview", "Revenue Analysis", "Product Performance", "Category & Region", "Statistical Analysis", "Forecasting", "Anomaly Detection", "AI Insights", "Reports & Export", "Project Health", "Upload Dataset"], label_visibility="collapsed")
    st.divider()
    if "clean_sales_df" in st.session_state:
        st.success(f"{len(st.session_state['clean_sales_df']):,} prepared records")
    else:
        st.info("No dataset loaded")
    st.caption("PHASE 8 · FINAL PROJECT CHECK")

st.markdown('<div class="section-kicker">BUSINESS INTELLIGENCE WORKSPACE</div>', unsafe_allow_html=True)
st.title("AI Sales Analytics")
st.caption("Explore performance, forecast revenue and identify unusual patterns.")

if "clean_sales_df" not in st.session_state:
    hero("Your sales story starts here", "Upload a sales workbook to explore business performance and machine learning.")
    st.info("Open Upload Dataset in the sidebar to get started.")
    page = "Upload Dataset"

if page == "Upload Dataset":
    hero("Import your sales data", "Upload Excel or CSV, confirm columns and prepare the dataset.", "DATA MANAGEMENT")
    uploaded = st.file_uploader("Choose a sales dataset", type=["xlsx", "xls", "csv"])
    if uploaded:
        try:
            raw, sheet = load_uploaded_file(uploaded)
            st.success(f"Loaded {uploaded.name} · {sheet} · {len(raw):,} rows")
            st.dataframe(raw.head(12), use_container_width=True, hide_index=True)
            detected = detect_columns(list(raw.columns))
            choices = ["(Not available)"] + list(raw.columns)
            labels = [("order_date","Order date *"),("sales","Sales / revenue *"),("order_id","Order ID"),("product","Product name"),("category","Category"),("quantity","Quantity"),("profit","Profit"),("region","Region"),("unit_price","Unit price"),("cost_price","Cost price")]
            mapping = {}
            cols = st.columns(2)
            for i,(key,label) in enumerate(labels):
                default = detected.get(key) if detected.get(key) in raw.columns else "(Not available)"
                with cols[i%2]:
                    selected = st.selectbox(label, choices, index=choices.index(default), key=f"phase5_{key}")
                mapping[key] = None if selected == "(Not available)" else selected
            if st.button("Validate and prepare dataset", type="primary"):
                cleaned, quality = clean_sales_data(raw, mapping)
                st.session_state["clean_sales_df"] = cleaned
                st.session_state["cleaning_report"] = quality
                st.success("Dataset prepared.")
                st.rerun()
        except Exception as exc:
            st.error(f"Could not process dataset: {exc}")
    st.stop()

df = st.session_state["clean_sales_df"].copy()
with st.expander("⌕ Refine dashboard data", expanded=True):
    a,b,c = st.columns([1.2,1,1])
    min_date,max_date = df["order_date"].min().date(),df["order_date"].max().date()
    with a:
        date_range = st.date_input("Order date range",value=(min_date,max_date),min_value=min_date,max_value=max_date)
    filtered = df.copy()
    if isinstance(date_range,tuple) and len(date_range)==2:
        start,end=date_range
        filtered=filtered[(filtered["order_date"].dt.date>=start)&(filtered["order_date"].dt.date<=end)]
    with b:
        if "category" in filtered and filtered["category"].notna().any():
            vals=sorted(filtered["category"].dropna().unique().tolist())
            selected=st.multiselect("Category",vals,default=vals)
            filtered=filtered[filtered["category"].isin(selected)]
    with c:
        if "region" in filtered and filtered["region"].notna().any():
            vals=sorted(filtered["region"].dropna().unique().tolist())
            selected=st.multiselect("Region",vals,default=vals)
            filtered=filtered[filtered["region"].isin(selected)]

if filtered.empty:
    st.warning("No records match the selected filters.")
    st.stop()

k=calculate_kpis(filtered)
monthly=monthly_revenue(filtered)
products=product_performance(filtered)
categories=category_performance(filtered)
regions=regional_performance(filtered)

if page=="Overview":
    hero("Business overview","Monitor key sales metrics and discover what is driving performance.")
    cols=st.columns(4)
    cols[0].metric("Total revenue",money(k["total_revenue"]))
    cols[1].metric("Total orders",f'{k["total_orders"]:,}')
    cols[2].metric("Units sold",f'{k["units_sold"]:,.0f}' if k["units_sold"] is not None else "N/A")
    cols[3].metric("Total profit",money(k["total_profit"]))
    x,y=st.columns(2)
    x.metric("Average order value",money(k["average_order_value"]))
    y.metric("Profit margin",f'{k["profit_margin_pct"]:.2f}%' if k["profit_margin_pct"] is not None else "N/A")
    st.divider()
    x,y=st.columns([1.5,1])
    with x:
        section("Revenue performance")
        st.plotly_chart(monthly_revenue_chart(monthly),use_container_width=True)
    with y:
        section("Revenue by category")
        if not categories.empty:
            fig=px.pie(categories,names="category",values="sales",hole=.65,template="plotly_dark")
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",margin=dict(t=15,b=5,l=0,r=0))
            st.plotly_chart(fig,use_container_width=True)
        else: st.info("Category data unavailable.")
    section("Business highlights")
    from modules.sales_analysis import generate_findings
    for item in generate_findings(filtered):
        st.markdown(f'<div class="insight">✦ &nbsp; {item}</div>',unsafe_allow_html=True)

elif page=="Revenue Analysis":
    hero("Revenue analysis","Understand monthly performance and changes in revenue.")
    st.plotly_chart(monthly_revenue_chart(monthly),use_container_width=True)
    growth=monthly.dropna(subset=["mom_growth_pct"])
    if not growth.empty:
        st.plotly_chart(px.bar(growth,x="month",y="mom_growth_pct",title="Month-over-month growth (%)",template="plotly_dark"),use_container_width=True)
    st.dataframe(monthly,use_container_width=True,hide_index=True)

elif page=="Product Performance":
    hero("Product performance","Find products contributing most to revenue.")
    if products.empty: st.warning("No product column is mapped.")
    else:
        n=st.slider("Products to display",5,min(20,max(5,len(products))),min(10,len(products)))
        st.plotly_chart(product_chart(products,n),use_container_width=True)
        x,y=st.columns(2)
        x.dataframe(products.head(n),use_container_width=True,hide_index=True)
        y.dataframe(products.tail(n).sort_values("sales"),use_container_width=True,hide_index=True)

elif page=="Category & Region":
    hero("Category and regional performance","Compare revenue contribution across business segments.")
    x,y=st.columns(2)
    with x:
        section("Category revenue")
        if not categories.empty:
            st.plotly_chart(category_chart(categories),use_container_width=True)
            st.dataframe(categories,use_container_width=True,hide_index=True)
        else: st.info("Category data unavailable.")
    with y:
        section("Regional revenue")
        if not regions.empty:
            st.plotly_chart(region_chart(regions),use_container_width=True)
            st.dataframe(regions,use_container_width=True,hide_index=True)
        else: st.info("Region data unavailable.")

elif page=="Statistical Analysis":
    hero("Statistical analysis","Explore the distribution and relationships between numeric measures.")
    stats=descriptive_statistics(filtered)
    if not stats.empty: st.dataframe(stats,use_container_width=True,hide_index=True)
    else: st.info("No numeric measures available.")
    corr=correlation_matrix(filtered)
    if not corr.empty:
        st.plotly_chart(px.imshow(corr,text_auto=".2f",color_continuous_scale="RdBu",zmin=-1,zmax=1,template="plotly_dark"),use_container_width=True)
    else: st.info("At least two numeric measures are needed for correlation analysis.")

elif page=="Project Health":
    hero("Project health check","Check your Python environment, required project files and currently loaded dataset.","FINAL VALIDATION")
    report = build_health_report(".", filtered)
    st.caption(f"Python {report['python_version']} · Project folder: {report['project_root']}")
    a,b,c=st.columns(3)
    a.metric("Checks ready",report["ready_count"])
    b.metric("Missing items",report["missing_count"])
    c.metric("Warnings",report["warning_count"])
    if report["overall_status"]=="Ready":
        st.success("All detected checks are ready.")
    else:
        st.warning("Some checks need attention. Review the details below.")
    checks_df = pd.DataFrame(report["checks"])
    if not checks_df.empty:
        st.dataframe(checks_df,use_container_width=True,hide_index=True)
    diagnostic = pd.DataFrame([
        {"item":"Python version","value":report["python_version"]},
        {"item":"Python executable","value":report["python_executable"]},
        {"item":"Project root","value":report["project_root"]},
        {"item":"Overall status","value":report["overall_status"]},
    ])
    st.download_button("Download diagnostic report",
                       diagnostic.to_csv(index=False).encode("utf-8"),
                       "project_health_report.csv","text/csv")
    st.info("A Ready status means these checks passed. It does not replace testing the complete app with your actual dataset.")
    st.divider()
    section("Final demo checklist")
    checklist = [
        "Upload the sample sales dataset and verify the preview.",
        "Check that date, sales and optional columns are mapped correctly.",
        "Open each dashboard page and confirm charts render.",
        "Try forecasting with enough monthly history.",
        "Generate AI insights and review the recommendations.",
        "Export both PDF and Excel reports and open the files.",
        "Run the automated tests from the VS Code terminal.",
        "Remove private or confidential datasets before pushing to GitHub.",
    ]
    for item in checklist:
        st.checkbox(item,key="phase8_"+str(checklist.index(item)))

elif page=="Reports & Export":
    hero("Reports and export centre","Create downloadable PDF and Excel reports from the currently filtered dataset.","REPORTING")
    st.caption("Reports use the active date, category and region filters shown above.")
    insight_result = st.session_state.get("phase6_insights")
    if st.button("Generate latest AI insights for report"):
        insight_result = generate_ai_insights(filtered)
        st.session_state["phase6_insights"] = insight_result
    st.divider()
    st.subheader("Excel workbook")
    st.write("Includes KPI summary, cleaned data, monthly revenue, product, category and regional performance, plus AI insights when available.")
    if st.button("Prepare Excel workbook", type="primary"):
        try:
            xlsx_bytes = build_excel_report(filtered, k, monthly, products, categories, regions, insight_result)
            st.session_state["phase7_excel"] = xlsx_bytes
            st.success("Excel workbook prepared.")
        except Exception as exc:
            st.error(f"Could not create Excel workbook: {exc}")
    if st.session_state.get("phase7_excel"):
        st.download_button("Download Excel report", st.session_state["phase7_excel"],
                           "ai_sales_analytics_report.xlsx",
                           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    st.divider()
    st.subheader("PDF summary report")
    st.write("Includes KPI metrics, monthly revenue, product/category/region tables and AI insights when available.")
    if st.button("Prepare PDF report"):
        try:
            pdf_bytes = build_pdf_report(k, monthly, products, categories, regions, insight_result)
            st.session_state["phase7_pdf"] = pdf_bytes
            st.success("PDF report prepared.")
        except Exception as exc:
            st.error(f"Could not create PDF report: {exc}")
    if st.session_state.get("phase7_pdf"):
        st.download_button("Download PDF report", st.session_state["phase7_pdf"],
                           "ai_sales_analytics_report.pdf", "application/pdf")
    st.divider()
    st.subheader("Quick data export")
    st.download_button("Download filtered cleaned data (CSV)",
                       filtered.to_csv(index=False).encode("utf-8"),
                       "cleaned_sales_data.csv", "text/csv")

elif page=="AI Insights":
    hero("AI sales assistant","Turn your selected sales data into clear observations and practical next steps.","AI INSIGHTS")
    st.caption("Insights are generated locally using transparent data-driven rules. No external AI service is called and your dataset is not sent anywhere.")
    if st.button("Generate business insights",type="primary"):
        st.session_state["phase6_insights"]=generate_ai_insights(filtered)
    result=st.session_state.get("phase6_insights")
    if result:
        st.markdown(f'<div class="insight">✦ &nbsp; {result["summary"]}</div>',unsafe_allow_html=True)
        left,right=st.columns(2)
        with left:
            section("What the data says")
            for item in result["insights"]:
                st.markdown(f'<div class="insight">📈 &nbsp; {item}</div>',unsafe_allow_html=True)
        with right:
            section("Recommended actions")
            for item in result["recommendations"]:
                st.markdown(f'<div class="insight">💡 &nbsp; {item}</div>',unsafe_allow_html=True)
        export_rows=[{"type":"Insight","text":x} for x in result["insights"]]+[{"type":"Recommendation","text":x} for x in result["recommendations"]]
        import pandas as pd
        report=pd.DataFrame(export_rows)
        st.download_button("Download insights report (CSV)",report.to_csv(index=False).encode("utf-8"),"ai_sales_insights.csv","text/csv")
        st.caption("These are decision-support suggestions, not guaranteed causes or business instructions. Validate them against business context.")
    else:
        st.info("Click Generate business insights to analyse the currently selected data.")

elif page=="Forecasting":
    hero("Revenue forecasting","Use historical monthly revenue to estimate the next 3 or 6 months.","MACHINE LEARNING")
    section("Forecast configuration","The model uses the selected dataset and filters.")
    horizon=st.radio("Forecast horizon", [3,6], horizontal=True, format_func=lambda x:f"Next {x} months")
    if st.button("Generate revenue forecast",type="primary"):
        try:
            result=forecast_revenue(filtered,horizon)
            st.session_state["phase5_forecast"]=result
        except Exception as exc:
            st.session_state.pop("phase5_forecast",None)
            st.error(str(exc))
    result=st.session_state.get("phase5_forecast")
    if result:
        st.caption(f"Model: {result['model_name']} · Historical monthly observations: {result['observations']}")
        hist=result["history"].copy()
        pred=result["forecast"].copy()
        fig=go.Figure()
        fig.add_trace(go.Scatter(x=hist["month"],y=hist["actual_revenue"],mode="lines+markers",name="Actual revenue",line=dict(color="#55c2d8",width=3)))
        fig.add_trace(go.Scatter(x=pred["month"],y=pred["predicted_revenue"],mode="lines+markers",name="Forecast",line=dict(color="#a78bfa",width=3,dash="dash")))
        fig.update_layout(title="Actual vs predicted monthly revenue",template="plotly_dark",paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",legend=dict(orientation="h"))
        st.plotly_chart(fig,use_container_width=True)
        p1,p2=st.columns(2)
        p1.metric("Forecast total",money(float(pred["predicted_revenue"].sum())))
        p2.metric("Average forecast / month",money(float(pred["predicted_revenue"].mean())))
        ev=result["evaluation"]
        st.subheader("Model evaluation")
        e1,e2=st.columns(2)
        e1.metric("MAE",money(ev["mae"]))
        e2.metric("RMSE",money(ev["rmse"]))
        st.caption(ev["message"])
        if result["seasonality_used"]:
            st.success("Seasonal component enabled: at least 24 monthly observations were available.")
        else:
            st.info("Seasonality was not enabled. At least 24 monthly observations are needed for two annual cycles.")
        st.dataframe(pred,use_container_width=True,hide_index=True)
        st.download_button("Download forecast CSV",pred.to_csv(index=False).encode("utf-8"),"revenue_forecast.csv","text/csv")
    else:
        st.info("Choose a forecast horizon and click Generate revenue forecast.")

elif page=="Anomaly Detection":
    hero("Anomaly detection","Find unusual monthly revenue patterns that deserve further investigation.","MACHINE LEARNING")
    contamination=st.slider("Expected proportion of unusual months",0.05,0.25,0.10,0.05,help="Controls how many observations Isolation Forest is expected to flag. This is a modelling setting, not a measured business rate.")
    if st.button("Detect unusual revenue patterns",type="primary"):
        try:
            st.session_state["phase5_anomalies"]=detect_revenue_anomalies(filtered,contamination)
        except Exception as exc:
            st.session_state.pop("phase5_anomalies",None)
            st.error(str(exc))
    result=st.session_state.get("phase5_anomalies")
    if result:
        data=result["data"]
        st.metric("Unusual months flagged",result["anomaly_count"])
        st.info(result["message"])
        fig=go.Figure()
        normal=data[~data["is_anomaly"]]
        unusual=data[data["is_anomaly"]]
        fig.add_trace(go.Scatter(x=normal["month"],y=normal["revenue"],mode="lines+markers",name="Typical months",line=dict(color="#55c2d8",width=2)))
        fig.add_trace(go.Scatter(x=unusual["month"],y=unusual["revenue"],mode="markers",name="Flagged months",marker=dict(color="#fb7185",size=12,symbol="x")))
        fig.update_layout(title="Monthly revenue with unusual observations",template="plotly_dark",paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",legend=dict(orientation="h"))
        st.plotly_chart(fig,use_container_width=True)
        st.dataframe(data[data["is_anomaly"]],use_container_width=True,hide_index=True)
        st.download_button("Download anomaly results",data.to_csv(index=False).encode("utf-8"),"sales_anomalies.csv","text/csv")
        st.caption("Anomaly flags are statistical alerts, not proof of fraud, error or poor performance. Investigate business context.")
    else:
        st.info("Choose the expected anomaly proportion and click Detect unusual revenue patterns.")

st.divider()
st.caption("AI Sales Intelligence · Phase 8 · Final validation and anomaly flags are estimates derived from the selected data.")
