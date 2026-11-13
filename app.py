# EquityLens AI
# Copyright © 2026 Keya Dhanani. All rights reserved.
# Independently designed and developed by Keya Dhanani.
# Unauthorized reproduction, redistribution, republication, or creation of a substantially
# similar copy of this original application code is not permitted except where allowed by law
# or applicable platform terms. Third-party libraries, public filings, factual source data,
# company names, and trademarks remain subject to their respective rights and terms.

import json
import time

import pandas as pd
import streamlit as st

from app_runtime import (
    load_company_universe,
    load_company_universe_metadata,
    load_json,
    load_research_datasets,
    load_research_coverage,
    load_research_index,
    load_sec_company,
    load_sec_filings,
    load_sec_summary,
    load_startup_company_data,
)
from config import (
    APP_LAYOUT,
    APP_PAGE_ICON,
    APP_TITLE,
    NAVIGATION_RERUN_BUDGET_MS,
    PERFORMANCE_BUDGET_MS,
    PUBLIC_APP_URL,
)
from models.context import (
    CompanyResearchContext,
    IndustryComparisonContext,
)
from navigation import (
    NAVIGATION_LABELS,
    build_global_company_lookup,
    clear_company_filters as clear_company_filters_state,
    format_global_search_option as format_global_search_option_value,
    global_search_options as build_global_search_options,
    initialize_saved_choices,
    navigate_to as navigate_to_state,
    remember_choice as remember_choice_state,
    research_link,
    reset_coverage_selection as reset_coverage_selection_state,
    save_rendered_choices as save_rendered_choices_state,
)
from services.refresh import retry_company_data as retry_company_data_state
from ui_components import section
from views.home import render_home
from research_experience import inject_readability_styles
from styles import inject_global_styles

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_PAGE_ICON,
    layout=APP_LAYOUT,
)

_app_run_started = time.perf_counter()


def _timed_render(page_name, render_callable):
    """Record server-side render duration for one top-level destination."""
    started = time.perf_counter()
    try:
        return render_callable()
    finally:
        elapsed_ms = (time.perf_counter() - started) * 1000
        timings = st.session_state.setdefault(
            "equitylens_page_timings",
            {},
        )
        history = list(timings.get(page_name, []))
        history.append(round(elapsed_ms, 1))
        timings[page_name] = history[-20:]
        st.session_state["equitylens_page_timings"] = timings
        st.session_state["equitylens_last_page_timing"] = {
            "page": page_name,
            "milliseconds": round(elapsed_ms, 1),
        }

inject_global_styles(st)



company_data = load_startup_company_data()
research_index = load_research_index()
research_coverage = load_research_coverage()
sec_summary = load_sec_summary()
company_universe = load_company_universe()
company_universe_metadata = (
    load_company_universe_metadata()
)

required_universe_columns = {
    "Ticker", "Company", "Sector", "Industry", "Country"
}

_metadata_by_ticker = (
    company_universe_metadata.get(
        "companies",
        {},
    )
    or {}
)
if _metadata_by_ticker:
    metadata_columns = {
        "Listing Status": "listing_status",
        "Ticker Aliases": "aliases",
        "Share Class": "share_class",
        "Issuer Type": "issuer_type",
        "Reporting Regime": "reporting_regime",
        "Market Cap Band": "market_cap_band",
        "Registration Year": "registration_year",
        "IPO Year": "ipo_year",
        "Exchange": "exchange",
        "Index Memberships": "index_memberships",
    }
    for display_column, metadata_key in (
        metadata_columns.items()
    ):
        company_universe[
            display_column
        ] = company_universe[
            "Ticker"
        ].astype(str).str.upper().map(
            lambda ticker: (
                _metadata_by_ticker.get(
                    ticker,
                    {},
                ).get(
                    metadata_key
                )
            )
        )
if not required_universe_columns.issubset(company_universe.columns):
    missing_columns = sorted(
        required_universe_columns - set(company_universe.columns)
    )
    st.error(
        "The expanded company-universe file is missing required columns: "
        + ", ".join(missing_columns)
    )
    st.stop()

coverage_sectors = sorted(
    [
        value
        for value in company_universe["Sector"]
        .dropna()
        .unique()
        .tolist()
        if value
    ]
)

# Make all 517 companies available throughout the app immediately.
# Generated SEC research fills these stubs over time.
_company_key_by_ticker = {
    str(record.get("ticker", "")).upper(): key
    for key, record in company_data.items()
    if record.get("ticker")
}
for _, _row in company_universe.iterrows():
    _ticker = str(_row.get("Ticker", "")).upper().strip()
    if not _ticker or _ticker in _company_key_by_ticker:
        continue

    _key = str(_row.get("Coverage Key", "")).strip()
    company_data[_key] = {
        "ticker": _ticker,
        "industry": str(_row.get("Industry", "Unclassified")),
        "sector": str(_row.get("Sector", "")),
        "country": str(_row.get("Country", "")),
        "fiscal_year": None,
        "fiscal_year_end": None,
        "source": "SEC research pending",
        "filing_url": "",
        "revenue": None,
        "gross_profit": None,
        "operating_income": None,
        "net_income": None,
        "cash": None,
        "assets": None,
        "history": [],
        "capital_structure": {
            "shares_outstanding": None,
            "shares_as_of": None,
            "total_debt": None,
            "cash_and_investments": None,
            "balance_sheet_as_of": None,
            "source_filing": ""
        }
    }
    _company_key_by_ticker[_ticker] = _key

public_market_data_enabled = True

public_finviz_data_enabled = bool(
    st.secrets.get("PUBLIC_FINVIZ_DATA_ENABLED", False)
    or st.secrets.get("FINVIZ_API_KEY")
    or st.secrets.get("FINVIZ_EXPORT_URL")
)

industries = sorted({
    item.get("industry", "Unclassified")
    for item in company_data.values()
})


SUBGROUPS = {
    "Data Platforms": [
        "Snowflake (SNOW)",
        "MongoDB (MDB)",
        "Datadog (DDOG)",
        "Elastic (ESTC)",
        "Dynatrace (DT)"
    ],
    "Cloud / Network Infrastructure": [
        "Cloudflare (NET)",
        "Akamai (AKAM)"
    ],
    "Cybersecurity": [
        "Rubrik (RBRK)",
        "Palo Alto Networks (PANW)",
        "Zscaler (ZS)"
    ],
    "Enterprise / AI Platforms": [],
    "AI / Compute Infrastructure": [],
    "Endpoint / XDR": [
        "CrowdStrike (CRWD)",
        "SentinelOne (S)"
    ],
    "Identity Security": [
        "Okta (OKTA)"
    ],
    "Network Security": [
        "Palo Alto Networks (PANW)",
        "Fortinet (FTNT)",
        "Zscaler (ZS)"
    ],
    "Exposure Management": [
        "Tenable (TENB)"
    ],
    "Consumer Financial Platforms": [
        "Coinbase (COIN)",
        "Robinhood (HOOD)",
        "Affirm (AFRM)"
    ],
    "Payments / Commerce Infrastructure": [
        "Block (XYZ)",
        "Toast (TOST)",
        "BILL Holdings (BILL)",
        "Marqeta (MQ)"
    ]
}

# Build a unified searchable universe from the 517-company market universe plus
# curated legacy research profiles that are not present in that CSV.
workspace_universe = company_universe.copy()
workspace_known_tickers = set(
    workspace_universe["Ticker"].astype(str).str.upper().tolist()
)
workspace_extra_rows = []

for workspace_key, workspace_record in company_data.items():
    extra_ticker = str(workspace_record.get("ticker", "")).upper().strip()
    if not extra_ticker or extra_ticker in workspace_known_tickers:
        continue

    extra_industry = str(
        workspace_record.get("industry", "Other")
    ).strip() or "Other"
    extra_sector = str(workspace_record.get("sector", "")).strip()

    if not extra_sector:
        if extra_industry in {
            "Cloud & Data Infrastructure Software",
            "Cybersecurity",
        }:
            extra_sector = "Technology"
        elif extra_industry == "Fintech & Digital Finance":
            extra_sector = "Financial"
        else:
            extra_sector = "Other"

    workspace_extra_rows.append({
        "Ticker": extra_ticker,
        "Company": workspace_key.rsplit(" (", 1)[0],
        "Sector": extra_sector,
        "Industry": extra_industry,
        "Country": str(workspace_record.get("country", "")).strip(),
        "Listing Status": "Historical / outside active universe",
        "Ticker Aliases": [],
        "Share Class": "",
        "Issuer Type": "Historical profile",
        "Reporting Regime": "Unknown",
        "Market Cap Band": "Unknown",
        "Registration Year": None,
        "IPO Year": None,
        "Exchange": None,
        "Index Memberships": [],
        "Coverage Key": workspace_key,
    })
    workspace_known_tickers.add(extra_ticker)

if workspace_extra_rows:
    workspace_universe = pd.concat(
        [workspace_universe, pd.DataFrame(workspace_extra_rows)],
        ignore_index=True,
        sort=False,
    )


initialize_saved_choices(st)
navigation_labels = NAVIGATION_LABELS


def remember_choice(key, value):
    remember_choice_state(
        st,
        key,
        value,
    )


def save_rendered_choices():
    save_rendered_choices_state(st)


def reset_coverage_selection():
    reset_coverage_selection_state(st)


def clear_company_filters():
    clear_company_filters_state(st)


def _sync_url(
    destination,
    ticker=None,
):
    current_section = str(
        st.query_params.get(
            "section",
            "",
        )
    )
    if current_section != destination:
        st.query_params[
            "section"
        ] = destination

    normalized_ticker = str(
        ticker or ""
    ).upper().strip()
    current_ticker = str(
        st.query_params.get(
            "ticker",
            "",
        )
    ).upper().strip()

    if normalized_ticker:
        if current_ticker != normalized_ticker:
            st.query_params[
                "ticker"
            ] = normalized_ticker
    elif (
        destination
        != "Company Research"
        and "ticker" in st.query_params
    ):
        del st.query_params[
            "ticker"
        ]

    if (
        destination
        != "Company Research"
        and "view" in st.query_params
    ):
        del st.query_params[
            "view"
        ]


def navigate_to(destination):
    navigate_to_state(
        st,
        destination,
    )
    _sync_url(destination)


def open_company_research(ticker):
    clear_company_filters()
    remember_choice(
        "workspace_company_search",
        ticker,
    )
    normalized_ticker = str(
        ticker
    ).upper().strip()
    st.session_state[
        "last_research_ticker"
    ] = normalized_ticker

    recent = [
        item
        for item in st.session_state.get(
            "recent_research_tickers",
            [],
        )
        if item != normalized_ticker
    ]
    st.session_state[
        "recent_research_tickers"
    ] = [
        normalized_ticker,
        *recent,
    ][:6]

    reset_coverage_selection()
    if "view" in st.query_params:
        del st.query_params["view"]
    _sync_url(
        "Company Research",
        normalized_ticker,
    )
    navigate_to_state(
        st,
        "Company Research",
    )


def compare_company(company_key):
    comparison_industry = (
        company_data[company_key].get(
            "industry",
            "Unclassified",
        )
    )
    peers = [
        name
        for name, data in company_data.items()
        if data.get(
            "industry",
            "Unclassified",
        )
        == comparison_industry
        and name != company_key
    ]
    remember_choice(
        "peer_industry",
        comparison_industry,
    )
    remember_choice(
        "peer_subgroup",
        "All current peers",
    )
    remember_choice(
        "peer_companies",
        [company_key] + peers[:2],
    )
    navigate_to(
        "Industry Comparison"
    )


def retry_company_data(ticker):
    retry_company_data_state(
        st,
        ticker,
    )


global_company_lookup = (
    build_global_company_lookup(
        workspace_universe
    )
)
global_search_options = (
    build_global_search_options(
        global_company_lookup
    )
)


def format_global_search_option(option):
    return format_global_search_option_value(
        option,
        global_company_lookup,
    )


def navigate_from_global_search():
    selected = st.session_state.get(
        "global_search_choice"
    )

    if selected in navigation_labels:
        navigate_to(selected)
        return

    selected_text = str(
        selected or ""
    )
    if selected_text.startswith(
        "filing::"
    ):
        form = selected_text.split(
            "::",
            1,
        )[1]
        remember_choice(
            "sec_tracker_category",
            "All forms",
        )
        remember_choice(
            "sec_tracker_forms",
            [form],
        )
        navigate_to("Filings")
        return

    if selected_text.startswith(
        "learn::"
    ):
        term = selected_text.split(
            "::",
            1,
        )[1]
        remember_choice(
            "learning_path",
            "All Concepts",
        )
        st.session_state[
            "learn_focus_term"
        ] = term
        navigate_to("Learn")
        return

    company = global_company_lookup.get(
        selected,
        {},
    )
    ticker = company.get("ticker")
    if ticker:
        open_company_research(ticker)


query_destination = str(
    st.query_params.get(
        "section",
        "",
    )
)
query_ticker = str(
    st.query_params.get(
        "ticker",
        "",
    )
).upper().strip()
query_signature = (
    query_destination,
    query_ticker,
)

if (
    st.session_state.get(
        "_last_query_signature"
    )
    != query_signature
):
    if (
        query_destination
        in navigation_labels
    ):
        navigate_to_state(
            st,
            query_destination,
        )

    if (
        query_ticker
        and query_ticker
        in workspace_known_tickers
    ):
        clear_company_filters()
        remember_choice(
            "workspace_company_search",
            query_ticker,
        )
        st.session_state[
            "last_research_ticker"
        ] = query_ticker
        navigate_to_state(
            st,
            "Company Research",
        )

    st.session_state[
        "_last_query_signature"
    ] = query_signature


st.session_state.setdefault("main_navigation", "Home")
inject_readability_styles(st)

with st.container(key="top_command_bar"):
    st.markdown(
        '<div class="el-kicker">EquityLens AI · Search and navigate</div>',
        unsafe_allow_html=True,
    )
    st.selectbox(
        "Search EquityLens",
        options=global_search_options,
        index=None,
        format_func=format_global_search_option,
        placeholder="Search a company, ticker, filing area, market view, or section…",
        key="global_search_choice",
        on_change=navigate_from_global_search,
        label_visibility="collapsed",
    )
    def sync_main_navigation_url():
        destination = st.session_state.get(
            "main_navigation",
            "Home",
        )
        ticker = (
            st.session_state.get(
                "last_research_ticker",
                "",
            )
            if destination
            == "Company Research"
            else ""
        )
        _sync_url(
            destination,
            ticker,
        )

    active_destination = st.radio(
        "Explore EquityLens",
        options=list(navigation_labels),
        horizontal=True,
        key="main_navigation",
        on_change=sync_main_navigation_url,
        label_visibility="collapsed",
    )

workspace_search = ""



sec_synced_companies = int(
    sec_summary.get("synced_companies", 0) or 0
)

deep_research_tickers = {
    str(ticker).upper().strip()
    for ticker in research_index.get(
        "deep_research_tickers",
        [],
    )
    if str(ticker).strip()
}

if active_destination == "Home":
    _timed_render(
        "Home",
        lambda: render_home(
        company_universe=company_universe,
        sec_synced_companies=sec_synced_companies,
        sec_summary=sec_summary,
        research_coverage=research_coverage,
        deep_research_tickers=deep_research_tickers,
        company_data=company_data,
        open_company_research=open_company_research,
        navigate_to=navigate_to,
        research_link=research_link,
        remember_choice=remember_choice,
        ),
    )


if active_destination == "Industry Comparison":
    from views.industry_comparison import render_industry_comparison

    _research = load_research_datasets()
    company_analysis = _research["analysis"]
    company_quarterly = _research["quarterly"]
    _analysis_by_ticker = _research["analysis_by_ticker"]

    comparison_context = IndustryComparisonContext(
        industries=industries,
        company_data=company_data,
        subgroups=SUBGROUPS,
        public_market_data_enabled=public_market_data_enabled,
        company_quarterly=company_quarterly,
        analysis_by_ticker=_analysis_by_ticker,
        company_analysis=company_analysis,
        research_coverage=research_coverage,
        remember_choice=remember_choice,
        company_universe=company_universe,
        research_link=research_link,
    )
    _timed_render(
        "Industry Comparison",
        lambda: render_industry_comparison(
            comparison_context
        ),
    )


if active_destination == "Company Research":
    from views.company_research import render_company_research

    _research = load_research_datasets()
    company_analysis = _research["analysis"]
    company_quarterly = _research["quarterly"]
    company_s1 = _research["s1"]
    _analysis_by_ticker = _research["analysis_by_ticker"]
    _quarterly_by_ticker = _research["quarterly_by_ticker"]
    _s1_by_ticker = _research["s1_by_ticker"]

    # Fill lightweight universe stubs with the matching lazy-loaded records.
    for _key, _record in company_data.items():
        _ticker = str(_record.get("ticker", "")).upper()
        if _ticker in _analysis_by_ticker:
            company_analysis[_key] = _analysis_by_ticker[_ticker]
        if _ticker in _quarterly_by_ticker:
            company_quarterly[_key] = _quarterly_by_ticker[_ticker]
        if _ticker in _s1_by_ticker:
            company_s1[_key] = _s1_by_ticker[_ticker]

    research_context = CompanyResearchContext(
        workspace_universe=workspace_universe,
        company_data=company_data,
        company_analysis=company_analysis,
        company_quarterly=company_quarterly,
        company_s1=company_s1,
        research_coverage=research_coverage,
        analysis_by_ticker=_analysis_by_ticker,
        quarterly_by_ticker=_quarterly_by_ticker,
        s1_by_ticker=_s1_by_ticker,
        industries=industries,
        load_sec_company=load_sec_company,
        open_company_research=open_company_research,
        reset_coverage_selection=reset_coverage_selection,
        remember_choice=remember_choice,
        clear_company_filters=clear_company_filters,
        compare_company=compare_company,
        retry_company_data=retry_company_data,
        research_link=research_link,
        save_rendered_choices=save_rendered_choices,
        navigate_to=navigate_to,
    )
    _timed_render(
        "Company Research",
        lambda: render_company_research(
            research_context
        ),
    )


if active_destination == "Market Monitor":
    from views.market_monitor import render_market_monitor

    _timed_render(
        "Market Monitor",
        lambda: render_market_monitor(
        public_finviz_data_enabled=public_finviz_data_enabled,
        industries=industries,
        company_data=company_data,
        sec_summary=sec_summary,
        workspace_known_tickers=workspace_known_tickers,
        research_link=research_link,
        ),
    )


if active_destination == "Filings":
    from sec_data import get_sec_company_research
    from views.filings import render_filings

    _timed_render(
        "Filings",
        lambda: render_filings(
        company_universe=company_universe,
        load_sec_filings=load_sec_filings,
        get_sec_company_research=get_sec_company_research,
        sec_summary=sec_summary,
        research_link=research_link,
        ),
    )


if active_destination == "Learn":
    from views.learn import render_learn

    render_learn(
        navigate_to=navigate_to
    )


save_rendered_choices()

_app_run_elapsed_ms = round(
    (time.perf_counter() - _app_run_started) * 1000,
    1,
)
st.session_state["equitylens_last_rerun_ms"] = _app_run_elapsed_ms

_debug_flag = str(
    st.query_params.get("debug", "")
).strip().lower()
if _debug_flag in {"1", "true", "yes"}:
    with st.expander("Developer performance diagnostics"):
        timings = st.session_state.get(
            "equitylens_page_timings",
            {},
        )
        rows = []
        for page_name, samples in sorted(timings.items()):
            if not samples:
                continue
            budget = PERFORMANCE_BUDGET_MS.get(
                page_name
            )
            average_ms = round(
                sum(samples) / len(samples),
                1,
            )
            rows.append({
                "Page": page_name,
                "Last render (ms)": samples[-1],
                "Average (ms)": average_ms,
                "Budget (ms)": budget or "—",
                "Budget status": (
                    "Within budget"
                    if budget and samples[-1] <= budget
                    else (
                        "Over budget"
                        if budget
                        else "Monitor"
                    )
                ),
                "Fastest (ms)": min(samples),
                "Slowest (ms)": max(samples),
                "Samples": len(samples),
            })
        if rows:
            st.dataframe(
                pd.DataFrame(rows),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.caption(
                "Navigate to a page to collect timing samples."
            )

        coverage_totals = research_coverage.get(
            "totals",
            {},
        )
        coverage_percentages = research_coverage.get(
            "percentages",
            {},
        )
        st.markdown("**Research coverage**")
        coverage_rows = [
            {
                "Layer": "SEC filing coverage",
                "Companies": coverage_totals.get(
                    "sec_filings",
                    0,
                ),
                "Coverage": (
                    f"{coverage_percentages.get('sec_filings', 0):.1f}%"
                ),
            },
            {
                "Layer": "Annual financials",
                "Companies": coverage_totals.get(
                    "annual_financials",
                    0,
                ),
                "Coverage": (
                    f"{coverage_percentages.get('annual_financials', 0):.1f}%"
                ),
            },
            {
                "Layer": "Quarterly financials",
                "Companies": coverage_totals.get(
                    "quarterly_financials",
                    0,
                ),
                "Coverage": (
                    f"{coverage_percentages.get('quarterly_financials', 0):.1f}%"
                ),
            },
            {
                "Layer": "Qualitative analysis",
                "Companies": coverage_totals.get(
                    "qualitative_analysis",
                    0,
                ),
                "Coverage": (
                    f"{coverage_percentages.get('qualitative_analysis', 0):.1f}%"
                ),
            },
            {
                "Layer": "Deep research",
                "Companies": coverage_totals.get(
                    "deep_research",
                    0,
                ),
                "Coverage": (
                    f"{coverage_percentages.get('deep_research', 0):.1f}%"
                ),
            },
        ]
        st.dataframe(
            pd.DataFrame(coverage_rows),
            use_container_width=True,
            hide_index=True,
        )

        navigation_status = (
            "within target"
            if _app_run_elapsed_ms <= NAVIGATION_RERUN_BUDGET_MS
            else "over target"
        )
        st.caption(
            f"Current full Streamlit rerun: {_app_run_elapsed_ms:,.1f} ms "
            f"({navigation_status}; target < {NAVIGATION_RERUN_BUDGET_MS:,} ms) · "
            "Server-side timing only; browser/network paint time is not included."
        )


with st.expander(
    "Methodology, sources & disclosure"
):
    st.markdown(
        """
        **Source policy**

        EquityLens prioritizes SEC EDGAR filings and official company disclosures for company research.
        BLS, U.S. Treasury, the Federal Reserve, and the New York Fed are used for macro and rates context.
        Supplemental market/news providers are labeled where used.

        **How values are treated**

        - **Reported:** taken from a disclosed source record.
        - **Calculated:** computed by EquityLens from reported source values.
        - **Research summary:** structured context based on available disclosures.
        - **Supplemental data:** third-party or market context with its own update schedule.

        Local-LLM research is used only for qualitative filing summaries. Reported financial facts are not generated by the model.

        **Educational disclosure**

        EquityLens AI is an independent educational research project. It does not provide personalized investment advice,
        security recommendations, rankings, or guarantees of future performance. Verify material information against the
        original filing or official source.
        """
    )

st.markdown(
    """
    <div class="el-site-footer">
        <div>
            <strong>EquityLens AI</strong> · Created by Keya Dhanani · Primary-source research first
        </div>
        <div class="el-site-footer-links">
            <a href="https://github.com/dhananikeya/equitylens-ai" target="_blank" rel="noopener noreferrer">GitHub</a>
            <span>·</span>
            <span>Educational research, not investment advice</span>
            <span>·</span>
            <span>© 2026 Keya Dhanani</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
