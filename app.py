import streamlit as st

st.set_page_config(
    page_title="EquityLens AI",
    page_icon="📊",
    layout="wide"
)

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

industry = st.selectbox(
    "Select industry",
    ["Cloud & Data Infrastructure Software"]
)

companies = [
    "Rubrik (RBRK)",
    "Snowflake (SNOW)",
    "MongoDB (MDB)",
    "Datadog (DDOG)",
    "Cloudflare (NET)"
]

selected_companies = st.multiselect(
    "Select companies to compare",
    companies,
    default=["Rubrik (RBRK)", "Snowflake (SNOW)", "MongoDB (MDB)"]
)

if st.button("Run Comparison"):
    if len(selected_companies) < 2:
        st.warning("Please select at least two companies to compare.")
    else:
        st.success(
            "Preparing comparison for: " + ", ".join(selected_companies)
        )
