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

st.header("Company Comparison")

company_1 = st.selectbox(
    "Select first company",
    ["AvePoint", "Rubrik", "Box"]
)

company_2 = st.selectbox(
    "Select second company",
    ["Rubrik", "AvePoint", "Box"]
)

if st.button("Compare Companies"):
    st.success(
        f"Preparing comparison between {company_1} and {company_2}"
    )
