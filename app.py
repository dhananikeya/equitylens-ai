import requests
import streamlit as st

st.set_page_config(
    page_title="EquityLens AI",
    page_icon="📊",
    layout="wide"
)

SEC_HEADERS = {
    "User-Agent": "EquityLens AI research app https://github.com/dhananikeya/equitylens-ai"
}

COMPANIES = {
    "Rubrik (RBRK)": {
        "ticker": "RBRK",
        "cik": "1943896"
    },
    "Snowflake (SNOW)": {
        "ticker": "SNOW",
        "cik": "1640147"
    },
    "MongoDB (MDB)": {
        "ticker": "MDB",
        "cik": "1441816"
    },
    "Datadog (DDOG)": {
        "ticker": "DDOG",
        "cik": "1561550"
    },
    "Cloudflare (NET)": {
        "ticker": "NET",
        "cik": "1477333"
    }
}


@st.cache_data(ttl=3600)
def get_company_facts(cik):
    cik = str(cik).zfill(10)
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"

    response = requests.get(
        url,
        headers=SEC_HEADERS,
        timeout=20
    )
    response.raise_for_status()

    return response.json()


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
    list(COMPANIES.keys()),
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
        st.subheader("SEC Data Connection Test")

        for company in selected_companies:
            cik = COMPANIES[company]["cik"]

            try:
                data = get_company_facts(cik)

                st.success(
                    f"{company}: SEC connection successful"
                )

                st.write(
                    "SEC company name:",
                    data.get("entityName", "Not available")
                )

            except Exception as e:
                st.error(
                    f"Could not retrieve SEC data for {company}"
                )
                st.write(e)
