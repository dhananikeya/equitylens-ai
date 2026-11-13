import html
import json

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from financial_utils import (
    build_change_notes,
    calc_growth,
    calc_margin,
    choose_income_period,
    financial_period_label,
    format_money,
    format_multiple,
    market_return,
    pct,
    quarterly_metrics,
    safe_float,
)
from models.context import CompanyResearchContext
from market_data import (
    finviz_numeric,
    get_company_financial_snapshot,
    get_live_market_data,
)
from research_experience import (
    render_company_evidence,
    render_report_download,
    toggle_watchlist,
)
from sec_data import (
    get_sec_company_research,
    latest_filing_by_forms,
)
from ui_components import (
    loading_panel,
    render_refresh_indicator,
    render_summary_cards,
    section,
)
from views.company_sections.analyst import (
    render_analyst_research,
)
from views.company_sections.business_risks import (
    render_business_and_risks,
)
from views.company_sections.ownership import (
    render_ownership,
)
from views.company_sections.overview import (
    render_overview,
)
from views.company_sections.filings import (
    render_sec_filings,
)
from views.company_sections.financials import (
    render_financials,
)
from views.company_sections.ipo import (
    render_ipo_registration,
)
from views.company_sections.peers import (
    render_peers_and_etfs,
)


def render_company_research(
    context: CompanyResearchContext,
):
    workspace_universe = context.workspace_universe
    company_data = context.company_data
    company_analysis = context.company_analysis
    company_quarterly = context.company_quarterly
    company_s1 = context.company_s1
    research_coverage = context.research_coverage
    _analysis_by_ticker = context.analysis_by_ticker
    _quarterly_by_ticker = context.quarterly_by_ticker
    _s1_by_ticker = context.s1_by_ticker
    industries = context.industries
    load_sec_company = context.load_sec_company
    open_company_research = context.open_company_research
    reset_coverage_selection = context.reset_coverage_selection
    remember_choice = context.remember_choice
    clear_company_filters = context.clear_company_filters
    compare_company = context.compare_company
    retry_company_data = context.retry_company_data
    research_link = context.research_link
    save_rendered_choices = context.save_rendered_choices
    navigate_to = context.navigate_to
    section("Company Research", "Company Research Workspace")

    st.caption(
        "Find a company by name or ticker. Start with its summary, then explore the details below."
    )

    def reopen_recent_company(ticker):
        open_company_research(ticker)

    recent_companies = st.session_state.get("recent_companies", [])
    if recent_companies:
        with st.expander("Recently viewed"):
            for recent_ticker, recent_name in recent_companies:
                st.button(
                    f"{recent_name} ({recent_ticker})",
                    key=f"recent_company_{recent_ticker}",
                    on_click=reopen_recent_company,
                    args=(recent_ticker,),
                )
            st.caption("Recent companies are remembered during this visit.")

    workspace_search = st.text_input(
        "Search company or ticker",
        placeholder="e.g. Amazon, AMZN, MongoDB or MDB",
        key="workspace_company_search",
        on_change=reset_coverage_selection,
    )

    workspace_sectors = sorted(
        [
            value
            for value in workspace_universe["Sector"].dropna().unique().tolist()
            if str(value).strip()
        ]
    )

    workspace_filters = st.columns(2)

    with workspace_filters[0]:
        workspace_sector = st.selectbox(
            "Sector",
            ["All sectors"] + workspace_sectors,
            key="workspace_sector",
        )

    if workspace_sector == "All sectors":
        workspace_sector_df = workspace_universe.copy()
    else:
        workspace_sector_df = workspace_universe[
            workspace_universe["Sector"] == workspace_sector
        ].copy()

    workspace_industries = sorted(
        [
            value
            for value in workspace_sector_df["Industry"].dropna().unique().tolist()
            if str(value).strip()
        ]
    )

    if st.session_state.get("workspace_industry", "All industries") not in ["All industries"] + workspace_industries:
        remember_choice("workspace_industry", "All industries")

    with workspace_filters[1]:
        workspace_industry = st.selectbox(
            "Industry",
            ["All industries"] + workspace_industries,
            key="workspace_industry",
        )

    workspace_filtered = workspace_sector_df.copy()
    if workspace_industry != "All industries":
        workspace_filtered = workspace_filtered[
            workspace_filtered["Industry"] == workspace_industry
        ].copy()

    search_text = workspace_search.strip()
    # Text search always covers the full company universe. Sector/industry
    # filters are browse controls and should never hide an exact ticker match.
    search_pool = workspace_universe.copy()
    st.caption(
        "Company and ticker search checks the full EquityLens universe. "
        "Sector and industry filters only narrow the browse list."
    )
    st.button(
        "Reset filters",
        key="research_reset_filters",
        on_click=clear_company_filters,
    )
    selected_workspace_row = None

    if search_text:
        search_lower = search_text.lower()
        ticker_lower = search_pool["Ticker"].fillna("").astype(str).str.lower()
        company_lower = search_pool["Company"].fillna("").astype(str).str.lower()

        exact_ticker = search_pool[ticker_lower == search_lower]
        exact_company = search_pool[company_lower == search_lower]
        starts_with = search_pool[
            company_lower.str.startswith(search_lower, na=False)
            | ticker_lower.str.startswith(search_lower, na=False)
        ]
        contains = search_pool[
            company_lower.str.contains(search_lower, regex=False, na=False)
            | ticker_lower.str.contains(search_lower, regex=False, na=False)
        ]

        if not exact_ticker.empty:
            search_matches = exact_ticker
        elif not exact_company.empty:
            search_matches = exact_company
        elif not starts_with.empty:
            search_matches = starts_with
        else:
            search_matches = contains

        if not search_matches.empty:
            selected_workspace_row = search_matches.iloc[0]
            if len(search_matches) > 1:
                st.caption(
                    f"{len(search_matches)} matches found. Showing "
                    f"{selected_workspace_row['Company']} "
                    f"({selected_workspace_row['Ticker']}). Keep typing to narrow the result."
                )
        else:
            st.info(
                f'No company or ticker matched "{search_text}" in the current company universe.'
            )
            st.caption(
                "Check the spelling or try the company ticker."
            )
            save_rendered_choices()
            st.stop()

    coverage_pool = search_matches if search_text else workspace_filtered
    coverage_display = coverage_pool[
        [
            column
            for column in [
                "Ticker", "Company", "Sector", "Industry", "Country",
                "Market Cap", "P/E", "Price", "Change",
            ]
            if column in workspace_filtered.columns
        ]
    ].copy().reset_index(drop=True)

    with st.expander(
        f"Matching companies · {len(coverage_pool):,} results",
        expanded=False,
    ):
        st.caption("Select a row to open that company directly in the research workspace.")
        coverage_event = None
        try:
            coverage_event = st.dataframe(
                coverage_display,
                use_container_width=True,
                hide_index=True,
                on_select="rerun",
                selection_mode="single-row",
                key="workspace_coverage_table",
            )
        except TypeError:
            st.dataframe(
                coverage_display,
                use_container_width=True,
                hide_index=True,
            )

    if coverage_event is not None:
        try:
            selected_rows = list(coverage_event.selection.rows)
        except Exception:
            selected_rows = []
        if selected_rows:
            selected_index = selected_rows[0]
            if 0 <= selected_index < len(coverage_display):
                selected_ticker_from_table = str(
                    coverage_display.iloc[selected_index].get("Ticker", "")
                ).upper()
                table_match = workspace_universe[
                    workspace_universe["Ticker"].astype(str).str.upper()
                    == selected_ticker_from_table
                ]
                if not table_match.empty:
                    selected_workspace_row = table_match.iloc[0]

    if selected_workspace_row is None and not search_text:
        previous_ticker = st.session_state.get("last_research_ticker")
        previous_match = workspace_filtered[
            workspace_filtered["Ticker"].astype(str).str.upper() == previous_ticker
        ]
        if not previous_match.empty:
            selected_workspace_row = previous_match.iloc[0]

    if selected_workspace_row is None:
        if not workspace_filtered.empty:
            selected_workspace_row = workspace_filtered.iloc[0]
        else:
            st.info("No companies match these filters. Reset filters to see the full list.")
            save_rendered_choices()
            st.stop()

    selected_ticker = str(selected_workspace_row.get("Ticker", "")).upper().strip()
    st.session_state["last_research_ticker"] = selected_ticker
    selected_name = str(selected_workspace_row.get("Company", "")).strip()
    st.session_state["recent_companies"] = [
        (selected_ticker, selected_name)
    ] + [
        item for item in st.session_state.get("recent_companies", [])
        if item[0] != selected_ticker
    ][:4]
    selected_sector_name = str(selected_workspace_row.get("Sector", "")).strip()
    selected_industry_name = str(selected_workspace_row.get("Industry", "")).strip()
    selected_country = str(selected_workspace_row.get("Country", "")).strip()

    selected_company_key = next(
        (
            company_name
            for company_name, company in company_data.items()
            if str(company.get("ticker", "")).upper() == selected_ticker
        ),
        str(selected_workspace_row.get("Coverage Key", "")).strip(),
    )

    selected_data = company_data.get(selected_company_key, {})
    selected_analysis = _analysis_by_ticker.get(
        selected_ticker,
        company_analysis.get(selected_company_key, {}),
    )
    selected_qdata = _quarterly_by_ticker.get(
        selected_ticker,
        company_quarterly.get(selected_company_key, {}),
    )
    selected_qm = quarterly_metrics(selected_qdata)
    selected_s1 = _s1_by_ticker.get(
        selected_ticker,
        company_s1.get(selected_company_key, {}),
    )
    selected_latest = selected_qdata.get("latest_quarter", {})
    selected_coverage = (
        research_coverage.get(
            "companies",
            {},
        ).get(
            selected_ticker,
            {},
        )
        or {}
    )

    core_snapshot_key = f"company_core_snapshot::{selected_ticker}"
    core_snapshot = st.session_state.get(core_snapshot_key)

    if core_snapshot is None:
        try:
            with loading_panel(
                "Loading financial statements",
                "Retrieving the latest available supplemental company financials."
            ):
                core_financial_fallback = get_company_financial_snapshot(
                    selected_ticker
                )
        except Exception:
            core_financial_fallback = {}

        try:
            with loading_panel(
                "Loading SEC filings",
                "Retrieving recent company filings and registration history from SEC EDGAR."
            ):
                core_sec = get_sec_company_research(selected_ticker)
            core_sec_error = None
        except Exception:
            core_sec = {}
            core_sec_error = (
                "SEC EDGAR is temporarily unavailable for this company. "
                "The rest of the workspace will continue to load."
            )

        # Local SEC fallback is sharded by ticker so a single company lookup
        # never needs to deserialize the full multi-company filing archive.
        core_local_sec = {}
        if not core_sec.get("filings"):
            core_local_sec = load_sec_company(
                selected_ticker,
                selected_company_key,
            )

        try:
            with loading_panel(
                "Retrieving latest market quote",
                "Loading the most recent available daily price snapshot."
            ):
                core_quote = get_live_market_data(
                    [selected_ticker]
                ).get(selected_ticker, {})
        except Exception:
            core_quote = {}

        core_snapshot = {
            "financial_fallback": core_financial_fallback,
            "sec": core_sec,
            "sec_error": core_sec_error,
            "local_sec": core_local_sec,
            "quote": core_quote,
        }
        st.session_state[core_snapshot_key] = core_snapshot

    selected_financial_fallback = core_snapshot.get(
        "financial_fallback",
        {},
    )
    selected_sec = core_snapshot.get("sec", {})
    selected_sec_error = core_snapshot.get("sec_error")
    selected_local_sec = core_snapshot.get("local_sec", {})
    selected_quote = core_snapshot.get("quote", {})

    selected_fallback_latest = selected_financial_fallback.get(
        "latest", {}
    )
    selected_fallback_history = selected_financial_fallback.get(
        "history", []
    )
    selected_fallback_quarters = selected_financial_fallback.get(
        "quarterly_history", []
    )

    selected_filings = (
        selected_sec.get("filings")
        or selected_local_sec.get("filings")
        or []
    )
    selected_registrations = (
        selected_sec.get("registration_filings")
        or selected_local_sec.get("registration_filings")
        or []
    )

    latest_annual = latest_filing_by_forms(
        selected_filings,
        {"10-K", "10-K/A", "20-F", "20-F/A", "40-F", "40-F/A"},
    )
    latest_quarter = latest_filing_by_forms(
        selected_filings,
        {"10-Q", "10-Q/A"},
    )
    latest_current = latest_filing_by_forms(
        selected_filings,
        {"8-K", "8-K/A", "6-K", "6-K/A"},
    )
    primary_registration = selected_registrations[0] if selected_registrations else {}

    selected_price = selected_quote.get("close")
    selected_change = selected_quote.get("percent_change")

    selected_market_cap = finviz_numeric(
        selected_workspace_row.get("Market Cap")
    )
    selected_pe = finviz_numeric(selected_workspace_row.get("P/E"))

    structured_financial_values = [
        selected_data.get("revenue"),
        selected_data.get("gross_profit"),
        selected_data.get("operating_income"),
        selected_data.get("net_income"),
    ]
    has_structured_financials = (
        bool(selected_qdata.get("latest_quarter"))
        or any(value is not None for value in structured_financial_values)
    )
    has_supplemental_financials = bool(
        selected_financial_fallback.get("latest")
        or selected_financial_fallback.get("quarterly_history")
    )

    if has_structured_financials:
        financial_status = (
            "Available",
            "SEC-linked structured financial data",
            "available",
        )
    elif has_supplemental_financials:
        financial_status = (
            "Supplemental",
            "Yahoo Finance statements available",
            "partial",
        )
    else:
        financial_status = (
            "Not found",
            "No financial dataset available yet",
            "missing",
        )

    if selected_filings:
        sec_status = (
            "Available",
            f"{len(selected_filings):,} recent filings loaded",
            "available",
        )
    elif selected_sec_error:
        sec_status = (
            "Refresh unavailable",
            "SEC source could not be reached",
            "partial",
        )
    else:
        sec_status = (
            "Not found",
            "No filing history loaded",
            "missing",
        )

    has_registration = bool(
        selected_s1.get("source_url")
        or selected_registrations
    )
    registration_status = (
        (
            "Available",
            (
                f"{len(selected_registrations):,} registration filing"
                + ("s" if len(selected_registrations) != 1 else "")
                + " indexed"
                if selected_registrations
                else "Structured registration research available"
            ),
            "available",
        )
        if has_registration
        else (
            "Not found",
            "No S-1, F-1, or S-11 found in indexed history",
            "missing",
        )
    )

    qualitative_depth = float(
        selected_coverage.get(
            "qualitative_depth_percent",
            0,
        )
        or 0
    )
    if qualitative_depth >= 80:
        research_status = (
            "Deep",
            f"{qualitative_depth:.0f}% of qualitative research fields populated",
            "available",
        )
    elif qualitative_depth > 0:
        research_status = (
            "Partial",
            f"{qualitative_depth:.0f}% of qualitative research fields populated",
            "partial",
        )
    else:
        research_status = (
            "Not yet available",
            "Primary filings remain accessible",
            "missing",
        )

    business_summary = selected_analysis.get(
        "business_model",
        "Structured company research is being expanded for this company. "
        "SEC filings and market data remain available in the workspace.",
    )

    st.markdown(
        f"""
        <div class="el-company-hero">
            <div class="el-kicker">
                {html.escape(selected_ticker)} · {html.escape(selected_sector_name)} · {html.escape(selected_industry_name)}
            </div>
            <div class="el-company-title">{html.escape(selected_name)}</div>
            <p class="el-subtitle">{html.escape(str(business_summary))}</p>
            <div class="el-badges">
                <span class="el-badge">{html.escape(selected_country or "Global")}</span>
                <span class="el-badge">{html.escape(str(selected_coverage.get("completion_status", "Coverage status unavailable")))}</span>
                <span class="el-badge">{int(selected_coverage.get("completeness_percent", 0) or 0)}% research completeness</span>
                <span class="el-badge">Educational · not investment advice</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    availability_cards = [
        ("SEC filings", *sec_status),
        ("Financials", *financial_status),
        ("Registration filing", *registration_status),
        ("Structured research", *research_status),
    ]
    availability_html = "".join(
        (
            f'<div class="el-availability-card {status_class}">'
            f'<div class="el-availability-label">{html.escape(label)}</div>'
            f'<div class="el-availability-status">{html.escape(status)}</div>'
            f'<div class="el-availability-detail">{html.escape(detail)}</div>'
            '</div>'
        )
        for label, status, detail, status_class in availability_cards
    )
    st.markdown(
        '<div class="el-availability-grid">'
        + availability_html
        + '</div>',
        unsafe_allow_html=True,
    )
    st.caption(
        "Availability reflects the sources currently loaded for this company. "
        "“Not found” is different from a reported value of zero."
    )

    missing_layers = [
        label
        for key, label in [
            ("annual_financials", "annual financials"),
            ("quarterly_financials", "quarterly financials"),
            ("qualitative_analysis", "qualitative analysis"),
            ("registration_research", "registration research"),
        ]
        if not selected_coverage.get(key)
    ]
    if missing_layers:
        st.info(
            "Research still being expanded for this company: "
            + ", ".join(missing_layers)
            + ". SEC filing access remains available where indexed."
        )

    research_actions = st.columns(3)
    with research_actions[0]:
        if selected_company_key in company_data and company_data[selected_company_key].get("industry", "Unclassified") in industries:
            st.button(
                "Compare this company",
                key="research_compare_company",
                on_click=compare_company,
                args=(selected_company_key,),
                use_container_width=True,
            )
        else:
            st.caption("Peer comparison is not available for this company's industry yet.")
    with research_actions[1]:
        with st.expander("Share this research"):
            st.caption("Copy this link to open the same company. Data may change as sources update.")
            st.code(research_link(selected_ticker), language=None)

    with research_actions[2]:
        already_saved = selected_ticker in st.session_state.get(
            "education_watchlist", []
        )
        st.button(
            "Remove from research list" if already_saved else "Save to my research list",
            key="company_watchlist_toggle_%s" % selected_ticker,
            on_click=toggle_watchlist,
            args=(st, selected_ticker),
            use_container_width=True,
        )

    if selected_sec_error or selected_price is None or not selected_financial_fallback:
        st.caption("Some source data is unavailable. You can retry without losing your selected company.")
        st.button(
            "Retry company data",
            key="retry_company_data",
            on_click=retry_company_data,
            args=(selected_ticker,),
        )

    header_metrics = st.columns(5)
    header_metrics[0].metric(
        "Price",
        ("$" + f"{selected_price:,.2f}") if selected_price is not None else "N/A",
        f"{selected_change:+.2f}%" if selected_change is not None else None,
    )
    header_metrics[1].metric("Market Cap", format_money(selected_market_cap), help="Share price multiplied by shares outstanding. Market value differs from revenue or cash.")
    header_metrics[2].metric(
        "P/E",
        f"{selected_pe:.1f}x" if selected_pe is not None else "N/A",
        help="Price-to-earnings ratio: share price relative to earnings per share. An unavailable value does not mean zero.",
    )

    income_selection = choose_income_period(selected_data, selected_qdata, selected_financial_fallback)
    workspace_revenue = income_selection["record"].get("revenue")
    workspace_growth = income_selection["growth"]
    revenue_source_label = income_selection["source"]

    header_metrics[3].metric("Revenue", format_money(workspace_revenue), help="Sales before expenses. Check the period shown below before comparing companies.")
    header_metrics[4].metric("Revenue Growth", pct(workspace_growth), help=income_selection["growth_basis"])

    quote_session = selected_quote.get("quote_session")
    quote_retrieved_at = selected_quote.get("retrieved_at")
    render_refresh_indicator(
        "Market snapshot refreshed",
        quote_retrieved_at,
        "quotes may be delayed",
    )
    render_refresh_indicator(
        "SEC data checked",
        selected_sec.get("last_checked_utc")
        or selected_local_sec.get("last_checked_utc"),
        "SEC EDGAR",
    )
    st.caption(
        "Price source: Yahoo Finance daily price data · "
        f"Trading session: {quote_session or 'Unavailable'} · "
        f"Retrieved (UTC): {quote_retrieved_at or 'Unavailable'}. Quotes may be delayed."
    )
    st.caption(
        f"Revenue source: {revenue_source_label}. "
        "Market cap and P/E: coverage screener dataset; may have a different update time."
    )

    latest_available_filing = max(
        selected_filings,
        key=lambda filing: str(filing.get("filing_date") or ""),
        default={},
    )
    filing_date = latest_available_filing.get("filing_date") or "Date unavailable"
    filing_form = latest_available_filing.get("form") or "Form unavailable"
    financial_period = income_selection["period"]
    st.caption(
        f"Financial period: {financial_period or 'See Financials for source periods'} · "
        "Market quotes may be delayed. Unavailable figures are not zero."
    )

    workspace_section_key = f"workspace_section_{selected_ticker}"
    legacy_section = st.session_state.get(workspace_section_key)
    if legacy_section == "Snapshot":
        st.session_state[workspace_section_key] = "Overview"
    elif legacy_section == "Filings":
        st.session_state[workspace_section_key] = "SEC Filings"

    st.markdown("### Research workspace")
    st.caption(
        "Choose one research area at a time. EquityLens keeps the original "
        "filings and source context available inside each section."
    )
    company_section = st.radio(
        "Company sections",
        [
            "Overview",
            "Financials",
            "Business & Risks",
            "SEC Filings",
            "IPO / Registration",
            "Ownership",
            "Analyst Research",
            "Peers & ETFs",
        ],
        horizontal=True,
        key=workspace_section_key,
        label_visibility="collapsed",
    )
    render_breadcrumbs(
        "Home",
        "Company Research",
        selected_ticker,
        company_section,
    )

    if company_section == "Overview":
        render_overview(
            selected_ticker=selected_ticker,
            selected_name=selected_name,
            selected_industry_name=selected_industry_name,
            selected_sector_name=selected_sector_name,
            selected_analysis=selected_analysis,
            selected_qdata=selected_qdata,
            selected_data=selected_data,
            selected_filings=selected_filings,
            selected_sec_error=selected_sec_error,
            selected_fallback_history=selected_fallback_history,
            selected_price=selected_price,
            income_selection=income_selection,
            workspace_growth=workspace_growth,
            workspace_revenue=workspace_revenue,
            financial_period=financial_period,
            revenue_source_label=revenue_source_label,
            filing_form=filing_form,
            filing_date=filing_date,
            latest_available_filing=latest_available_filing,
            navigate_to=navigate_to,
        )

    if company_section == "Business & Risks":
        render_business_and_risks(
            selected_ticker=selected_ticker,
            selected_analysis=selected_analysis,
            latest_annual=latest_annual,
        )

    if company_section == "Financials":
        render_financials(
            selected_ticker=selected_ticker,
            selected_data=selected_data,
            selected_qdata=selected_qdata,
            selected_financial_fallback=selected_financial_fallback,
            selected_fallback_quarters=selected_fallback_quarters,
            income_selection=income_selection,
            workspace_growth=workspace_growth,
        )

    if company_section == "SEC Filings":
        render_sec_filings(
            selected_ticker=selected_ticker,
            selected_filings=selected_filings,
            selected_sec=selected_sec,
            selected_sec_error=selected_sec_error,
            latest_annual=latest_annual,
            latest_quarter=latest_quarter,
            latest_current=latest_current,
            primary_registration=primary_registration,
        )

    if company_section == "IPO / Registration":
        render_ipo_registration(
            selected_ticker=selected_ticker,
            selected_registrations=selected_registrations,
            selected_s1=selected_s1,
        )

    if company_section == "Ownership":
        render_ownership(
            selected_ticker=selected_ticker,
            selected_data=selected_data,
            selected_s1=selected_s1,
            selected_filings=selected_filings,
        )

    if company_section == "Analyst Research":
        render_analyst_research(
            selected_ticker=selected_ticker,
            selected_price=selected_price,
        )

    if company_section == "Peers & ETFs":
        render_peers_and_etfs(
            workspace_universe=workspace_universe,
            selected_ticker=selected_ticker,
            selected_industry_name=selected_industry_name,
        )

