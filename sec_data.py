import requests
import streamlit as st


HEADERS = {
    "User-Agent": "EquityLens AI research app dhananikeya@gmail.com"
}


@st.cache_data(ttl=3600)
def get_company_facts(cik):
    cik = str(cik).zfill(10)

    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=20
    )

    response.raise_for_status()

    return response.json()
