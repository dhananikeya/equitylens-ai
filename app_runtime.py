import gzip
import json
import re

import pandas as pd
import streamlit as st

from market_units import market_cap_dollars

from research_data import (
    index_dataset_by_ticker,
    merge_research_records,
)


@st.cache_data(show_spinner=False)
def load_json(path):
    """Load repository-backed JSON once per app process."""
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


@st.cache_data(show_spinner=False)
def load_sec_filings():
    """Load the full SEC filing archive only on pages that truly need it."""
    try:
        with gzip.open(
            "data/sec_filings.json.gz",
            "rt",
            encoding="utf-8",
        ) as archive_file:
            return json.load(archive_file)
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return load_json("data/sec_filings.json")


@st.cache_data(show_spinner=False)
def load_sec_company(ticker, company_key=""):
    """Load one company's SEC shard, with legacy archive fallback."""
    safe_ticker = re.sub(
        r"[^A-Z0-9.\-]",
        "",
        str(ticker or "").upper().strip(),
    )
    if safe_ticker:
        try:
            return load_json(
                f"data/sec_companies/{safe_ticker}.json"
            )
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    if company_key:
        try:
            return load_sec_filings().get(company_key, {})
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    return {}


@st.cache_data(show_spinner=False)
def load_research_datasets():
    """Load narrative, quarterly, and S-1 datasets only when needed."""
    hand_analysis = load_json("data/company_analysis.json")
    hand_quarterly = load_json("data/company_quarterly.json")
    hand_s1 = load_json("data/company_s1.json")
    generated_analysis = load_json(
        "data/generated_company_analysis.json"
    )
    generated_quarterly = load_json(
        "data/generated_company_quarterly.json"
    )
    generated_s1 = load_json(
        "data/generated_company_s1.json"
    )

    def merge_keyed(generated, curated):
        merged = {
            key: (
                dict(value)
                if isinstance(value, dict)
                else value
            )
            for key, value in generated.items()
        }
        for key, value in curated.items():
            if (
                key in merged
                and isinstance(merged[key], dict)
                and isinstance(value, dict)
            ):
                merged[key] = (
                    merge_research_records(
                        merged[key],
                        value,
                    )
                )
            else:
                merged[key] = value
        return merged

    analysis = merge_keyed(
        generated_analysis,
        hand_analysis,
    )
    quarterly = merge_keyed(
        generated_quarterly,
        hand_quarterly,
    )
    s1 = merge_keyed(
        generated_s1,
        hand_s1,
    )

    return {
        "analysis": analysis,
        "quarterly": quarterly,
        "s1": s1,
        "analysis_by_ticker": index_dataset_by_ticker(
            analysis
        ),
        "quarterly_by_ticker": index_dataset_by_ticker(
            quarterly
        ),
        "s1_by_ticker": index_dataset_by_ticker(s1),
    }


@st.cache_data(show_spinner=False)
def load_startup_company_data():
    """Load only the small company-metrics datasets required at startup."""
    hand = load_json("data/company_metrics.json")
    generated = load_json(
        "data/generated_company_metrics.json"
    )
    merged = dict(generated)
    for key, value in hand.items():
        if (
            key in merged
            and isinstance(merged[key], dict)
            and isinstance(value, dict)
        ):
            merged[key] = (
                merge_research_records(
                    merged[key],
                    value,
                )
            )
        else:
            merged[key] = value
    return merged


@st.cache_data(show_spinner=False)
def load_research_coverage():
    try:
        return load_json(
            "data/research_coverage.json"
        )
    except (
        FileNotFoundError,
        json.JSONDecodeError,
    ):
        return {
            "generated_at_utc": "",
            "totals": {},
            "percentages": {},
            "companies": {},
        }


@st.cache_data(show_spinner=False)
def load_research_index():
    try:
        return load_json("data/research_index.json")
    except (FileNotFoundError, json.JSONDecodeError):
        return {"deep_research_tickers": []}


@st.cache_data(show_spinner=False)
def load_sec_summary():
    try:
        summary = dict(load_json("data/sec_summary.json"))
        summary["_ready"] = True
        return summary
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "_ready": False,
            "company_count": 0,
            "synced_companies": 0,
            "companies": {},
            "recent_filings": [],
        }


def _market_cap_dollars(value):
    return market_cap_dollars(
        value,
        plain_numbers_are_millions=True,
    )


@st.cache_data(show_spinner=False)
def load_data_quality_report():
    try:
        return load_json(
            "data/data_quality_report.json"
        )
    except (
        FileNotFoundError,
        json.JSONDecodeError,
    ):
        return {
            "generated_at_utc": "",
            "universe_count": 0,
            "summary": {},
            "companies": {},
        }


@st.cache_data(show_spinner=False)
def load_company_universe_metadata():
    try:
        return load_json(
            "data/company_universe_metadata.json"
        )
    except (
        FileNotFoundError,
        json.JSONDecodeError,
    ):
        return {
            "generated_at_utc": "",
            "companies": {},
            "field_policy": {},
        }


@st.cache_data(show_spinner=False)
def load_company_universe():
    try:
        universe = pd.read_csv(
            "data/finviz_universe.csv"
        )
    except pd.errors.ParserError:
        universe = pd.read_csv(
            "data/finviz_universe.csv",
            engine="python",
            on_bad_lines="skip",
        )

    for column in [
        "Ticker",
        "Company",
        "Sector",
        "Industry",
        "Country",
    ]:
        if column in universe.columns:
            universe[column] = (
                universe[column]
                .fillna("")
                .astype(str)
                .str.strip()
            )

    if "Market Cap" in universe.columns:
        universe["Market Cap"] = universe[
            "Market Cap"
        ].apply(_market_cap_dollars)

    if "Ticker" in universe.columns:
        universe["Ticker"] = (
            universe["Ticker"].str.upper()
        )

    if {
        "Company",
        "Ticker",
    }.issubset(universe.columns):
        universe["Coverage Key"] = (
            universe["Company"]
            + " ("
            + universe["Ticker"]
            + ")"
        )

    return universe
