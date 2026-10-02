import json
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="EquityLens AI",
    page_icon="📊",
    layout="wide"
)


@st.cache_data
def load_company_data():
    with open("data/company_metrics.json", "r") as file:
        return json.load(file)


def format_money(value):
    if value is None:
        return "N/A"

    sign = "-" if value < 0 else ""
    value = abs(value)

    if value >= 1_000_000_000:
        return f"{sign}${value / 1_000_000_000:.2f}B"
    if value >= 1_000_000:
        return f"{sign}${value / 1_000_000:.1f}M"

    return f"{sign}${value:,.0f}"


def pct(value):
    return f"{value:.1f}%" if value is not None else "N/A"


company_data = load_company_data()

st.title("EquityLens AI")

st.subheader(
    "AI-powered capital markets research using SEC filings and financial data"
)

st.write(
    """
    EquityLens AI helps users compare public companies using financial metrics,
    SEC filings, risk factors, and AI-powered research insights.
    """
)

st.markdown("---")
st.header("Industry Comparison")
st.markdown("**Industry:** Cloud & Data Infrastructure Software")

selected_companies = st.multiselect(
    "Select companies to compare",
    list(company_data.keys()),
    default=[
        "Rubrik (RBRK)",
        "Snowflake (SNOW)",
        "MongoDB (MDB)"
    ]
)

if st.button("Run Comparison"):
    if len(selected_companies) < 2:
        st.warning("Please select at least two companies to compare.")
    else:
        rows = []

        for company in selected_companies:
            data = company_data[company]

            revenue = data["revenue"]
            gross_profit = data["gross_profit"]
            operating_income = data["operating_income"]
            net_income = data["net_income"]

            gross_margin = (gross_profit / revenue) * 100 if revenue else None
            operating_margin = (operating_income / revenue) * 100 if revenue else None
            net_margin = (net_income / revenue) * 100 if revenue else None

            history = data.get("history", [])
            revenue_growth = None
            if len(history) >= 2:
                current = history[-1]["revenue"]
                prior = history[-2]["revenue"]
                if prior:
                    revenue_growth = ((current - prior) / prior) * 100

            rows.append({
                "Company": company,
                "FY": data.get("fiscal_year"),
                "Revenue": format_money(revenue),
                "YoY Revenue Growth": pct(revenue_growth),
                "Gross Profit": format_money(gross_profit),
                "Gross Margin": pct(gross_margin),
                "Operating Income": format_money(operating_income),
                "Operating Margin": pct(operating_margin),
                "Net Income": format_money(net_income),
                "Net Margin": pct(net_margin),
                "Cash": format_money(data["cash"]),
                "Assets": format_money(data["assets"]),
                "SEC Filing": data.get("filing_url", "")
            })

        df = pd.DataFrame(rows)

        st.subheader("Financial Comparison")
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "SEC Filing": st.column_config.LinkColumn(
                    "SEC Filing",
                    display_text="Open 10-K"
                )
            }
        )

        st.caption(
            "Financial figures are sourced from each company's latest annual Form 10-K. "
            "Fiscal year-end dates differ by company."
        )

        st.markdown("---")
        st.subheader("Three-Year Revenue Trend")

        revenue_rows = []
        for company in selected_companies:
            for item in company_data[company].get("history", []):
                revenue_rows.append({
                    "Company": company,
                    "Fiscal Year": str(item["fiscal_year"]),
                    "Revenue": item["revenue"]
                })

        revenue_df = pd.DataFrame(revenue_rows)

        if not revenue_df.empty:
            revenue_chart = revenue_df.pivot(
                index="Fiscal Year",
                columns="Company",
                values="Revenue"
            )
            st.line_chart(revenue_chart)

        st.subheader("Three-Year Operating Margin Trend")

        margin_rows = []
        for company in selected_companies:
            for item in company_data[company].get("history", []):
                revenue = item["revenue"]
                operating_income = item["operating_income"]
                operating_margin = (
                    (operating_income / revenue) * 100
                    if revenue else None
                )

                margin_rows.append({
                    "Company": company,
                    "Fiscal Year": str(item["fiscal_year"]),
                    "Operating Margin": operating_margin
                })

        margin_df = pd.DataFrame(margin_rows)

        if not margin_df.empty:
            margin_chart = margin_df.pivot(
                index="Fiscal Year",
                columns="Company",
                values="Operating Margin"
            )
            st.line_chart(margin_chart)
