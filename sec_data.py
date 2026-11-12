import requests
import streamlit as st

from models.context import CompanyIdentifier


SEC_REQUEST_HEADERS = {
    "User-Agent": "EquityLens AI research app dhananikeya@gmail.com",
    "From": "dhananikeya@gmail.com",
    "Accept": "application/json",
}

# Backwards-compatible alias for the existing company-facts helper.
HEADERS = SEC_REQUEST_HEADERS


@st.cache_data(ttl=3600)
def get_company_facts(cik):
    cik = str(cik).zfill(10)
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"

    response = requests.get(
        url,
        headers=SEC_REQUEST_HEADERS,
        timeout=20,
    )
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=86400)
def get_sec_ticker_directory():
    response = requests.get(
        "https://www.sec.gov/files/company_tickers.json",
        headers=SEC_REQUEST_HEADERS,
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()

    directory = {}
    for row in payload.values():
        ticker = str(row.get("ticker", "")).upper().strip()
        if ticker:
            directory[ticker] = {
                "cik": str(row.get("cik_str", "")).zfill(10),
                "title": row.get("title", ""),
            }
    return directory


def sec_filing_url(cik, accession, primary_document):
    if not cik or not accession or not primary_document:
        return ""
    return (
        "https://www.sec.gov/Archives/edgar/data/"
        + str(int(cik))
        + "/"
        + str(accession).replace("-", "")
        + "/"
        + str(primary_document)
    )


def sec_rows_from_recent(recent, cik):
    forms = recent.get("form", []) if isinstance(recent, dict) else []
    rows = []

    def value(field, index, default=""):
        values = recent.get(field, []) if isinstance(recent, dict) else []
        return values[index] if index < len(values) else default

    for index, form in enumerate(forms):
        accession = value("accessionNumber", index)
        primary_document = value("primaryDocument", index)
        rows.append({
            "form": form,
            "filing_date": value("filingDate", index),
            "report_date": value("reportDate", index),
            "accession_number": accession,
            "primary_document": primary_document,
            "description": value("primaryDocDescription", index),
            "items": value("items", index),
            "url": sec_filing_url(cik, accession, primary_document),
        })

    return rows


@st.cache_data(ttl=900)
def get_sec_company_research(ticker):
    ticker = str(ticker).upper().strip()
    directory = get_sec_ticker_directory()
    ticker_record = directory.get(ticker)

    if not ticker_record:
        return {
            "ticker": ticker,
            "cik": "",
            "entity_name": "",
            "filings": [],
            "registration_filings": [],
            "sec_company_url": "",
            "status": "Ticker not resolved in SEC directory",
        }

    cik = ticker_record["cik"]
    response = requests.get(
        f"https://data.sec.gov/submissions/CIK{cik}.json",
        headers=SEC_REQUEST_HEADERS,
        timeout=30,
    )
    response.raise_for_status()
    submissions = response.json()

    recent = submissions.get("filings", {}).get("recent", {})
    recent_rows = sec_rows_from_recent(recent, cik)

    registration_forms = {
        "S-1", "S-1/A",
        "F-1", "F-1/A",
        "S-11", "S-11/A",
    }
    registration_rows = [
        row for row in recent_rows
        if row.get("form") in registration_forms
    ]

    if not registration_rows:
        history_files = submissions.get("filings", {}).get("files", []) or []
        for history_file in history_files:
            history_name = history_file.get("name")
            if not history_name:
                continue
            history_response = requests.get(
                "https://data.sec.gov/submissions/" + history_name,
                headers=SEC_REQUEST_HEADERS,
                timeout=30,
            )
            history_response.raise_for_status()
            historical_rows = sec_rows_from_recent(
                history_response.json(),
                cik,
            )
            registration_rows.extend(
                row for row in historical_rows
                if row.get("form") in registration_forms
            )
            if registration_rows:
                break

    seen_accessions = set()
    registration_unique = []
    for row in registration_rows:
        accession = row.get("accession_number")
        if accession and accession in seen_accessions:
            continue
        if accession:
            seen_accessions.add(accession)
        registration_unique.append(row)

    return {
        "ticker": ticker,
        "cik": cik,
        "entity_name": submissions.get(
            "name",
            ticker_record.get("title", ""),
        ),
        "filings": recent_rows[:200],
        "registration_filings": registration_unique,
        "sec_company_url": (
            "https://www.sec.gov/edgar/browse/"
            + f"?CIK={int(cik)}&owner=exclude&action=getcompany"
        ),
        "status": "available",
    }


def latest_filing_by_forms(filings, forms):
    wanted_forms = set(forms)
    for filing in filings:
        if filing.get("form") in wanted_forms:
            return filing
    return {}
