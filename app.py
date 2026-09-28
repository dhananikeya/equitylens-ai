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

            rows.append({
                "Company": company,
                "Revenue": data["revenue"],
                "Gross Profit": data["gross_profit"],
                "Operating Income": data["operating_income"],
                "Net Income": data["net_income"],
                "Cash": data["cash"],
                "Assets": data["assets"]
            })

        df = pd.DataFrame(rows)

        st.subheader("Financial Comparison")
        st.dataframe(df, use_container_width=True)

        st.caption(
            "Current values are placeholders until verified filing data is loaded into company_metrics.json."
        )
