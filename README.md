# AI-Powered Sales Analytics and Revenue Forecasting System

A Python and Streamlit dashboard for exploring sales performance, understanding monthly revenue patterns, forecasting revenue, detecting unusual trends, and exporting reports.

## Features

- Upload sales data in CSV or Excel format.
- Map dataset columns and clean invalid dates, sales values and duplicate records.
- Review KPIs such as revenue, orders, units sold, profit, average order value and profit margin (when source columns support them).
- Analyse monthly revenue, product performance, categories and regions.
- View descriptive statistics and correlations.
- Forecast monthly revenue with statistical time-series models when enough history is available.
- Flag unusual monthly revenue patterns using Isolation Forest.
- Generate local, rule-based business insights and recommendations.
- Export filtered data as CSV and reports as PDF or multi-sheet Excel.
- Run a project health check and automated tests.

## Technology

Python, Streamlit, Pandas, NumPy, Plotly, scikit-learn, Statsmodels, ReportLab, OpenPyXL and pytest.

## Requirements

- Python 3.10 or newer recommended.
- VS Code or another Python editor.
- Internet connection for the initial package installation.

## Setup on Windows

Open this folder in VS Code. In the terminal, run:

```powershell
py -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Start the dashboard:

```powershell
streamlit run app.py
```

Stop the server with `Ctrl + C`.

## Dataset

Use a CSV or Excel file with at least:
- `Order Date` (date of transaction)
- `Sales` (numeric revenue value)

Optional columns improve the analysis:
- Order ID
- Product name
- Category
- Quantity
- Profit
- Region
- Unit price and cost price

The upload page supports manual column mapping when the source headers differ. Forecast quality depends on the number and consistency of monthly observations. The seasonal forecasting path requires at least 24 months of data.

## Run tests

From the project root with the virtual environment activated:

```powershell
python -m pytest -q
```

## Project structure

```text
AI_Sales_Analytics/
├── app.py
├── requirements.txt
├── README.md
├── data/
├── modules/
│   ├── data_loader.py
│   ├── preprocessing.py
│   ├── sales_analysis.py
│   ├── visualizations.py
│   ├── forecasting.py
│   ├── anomaly_detection.py
│   ├── ai_insights.py
│   ├── report_generator.py
│   └── project_health.py
├── tests/
└── .streamlit/
    └── config.toml
```

## Important limitations

- The AI Insights feature is a transparent, rule-based analysis module. It does not call a hosted LLM.
- Forecasts are estimates based on historical data, not guarantees.
- Anomaly detection flags unusual patterns for investigation; it does not prove fraud or data errors.
- Missing calendar months in the forecasting series are filled with zero revenue by the current implementation. Confirm whether that assumption fits your dataset.
- The dashboard's results depend on the selected filters and the quality of the uploaded data.

## GitHub safety

Do not commit passwords, API keys, private customer data, or confidential business files. Keep uploaded datasets out of version control unless you have permission to share them. Review the files staged for commit before pushing.

## Team

Add the confirmed team member names, roles, course and institution details here before submission.
