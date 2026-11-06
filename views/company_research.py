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
from market_data import (
    finviz_numeric,
    get_company_analyst_data,
    get_company_financial_snapshot,
    get_company_ownership_data,
    get_live_market_data,
    get_major_etf_exposure,
    get_market_history,
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
    render_summary_cards,
    section,
)


def render_company_research(
    workspace_universe,
    company_data,
    company_analysis,
    company_quarterly,
    company_s1,
    _analysis_by_ticker,
    _quarterly_by_ticker,
    _s1_by_ticker,
    industries,
    load_sec_filings,
    open_company_research,
    reset_coverage_selection,
    remember_choice,
    clear_company_filters,
    compare_company,
    retry_company_data,
    research_link,
    save_rendered_choices,
    navigate_to,
):
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

    try:
        with st.spinner("Loading financial statements from Yahoo Finance…"):
            selected_financial_fallback = get_company_financial_snapshot(
                selected_ticker
            )
    except Exception:
        selected_financial_fallback = {}

    selected_fallback_latest = selected_financial_fallback.get(
        "latest", {}
    )
    selected_fallback_history = selected_financial_fallback.get(
        "history", []
    )
    selected_fallback_quarters = selected_financial_fallback.get(
        "quarterly_history", []
    )

    try:
        with st.spinner("Loading company filings from SEC EDGAR…"):
            selected_sec = get_sec_company_research(selected_ticker)
        selected_sec_error = None
    except Exception:
        selected_sec = {}
        selected_sec_error = (
            "SEC EDGAR is temporarily unavailable for this company. "
            "The rest of the workspace will continue to load."
        )

    # The full local SEC archive is intentionally lazy-loaded. Most company
    # sessions use the live per-company SEC request and never touch the large file.
    selected_local_sec = {}
    if not selected_sec.get("filings"):
        try:
            selected_local_sec = load_sec_filings().get(
                selected_company_key,
                {},
            )
        except (FileNotFoundError, json.JSONDecodeError):
            selected_local_sec = {}

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

    try:
        with st.spinner("Loading the latest available Yahoo Finance price…"):
            selected_quote = get_live_market_data([selected_ticker]).get(selected_ticker, {})
    except Exception:
        selected_quote = {}

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

    research_fields = [
        selected_analysis.get("business_model"),
        selected_analysis.get("primary_revenue_source"),
        selected_analysis.get("customer_type"),
        selected_analysis.get("competitive_risk"),
        selected_analysis.get("operational_risk"),
        selected_analysis.get("profitability_history"),
        selected_analysis.get("key_risk_themes"),
    ]
    research_field_count = sum(bool(value) for value in research_fields)
    if selected_analysis.get("business_model") and research_field_count >= 4:
        research_status = (
            "Available",
            f"{research_field_count} structured research fields",
            "available",
        )
    elif research_field_count:
        research_status = (
            "Partial",
            f"{research_field_count} structured research fields",
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
                <span class="el-badge">Primary-source research</span>
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

    if company_section == "Overview":
        section("Overview", "Understand the company in 60 seconds")

        overview_record = income_selection["record"]
        overview_revenue = overview_record.get("revenue")
        overview_operating_margin = calc_margin(
            overview_record.get("operating_income"),
            overview_revenue,
        )
        overview_net_margin = calc_margin(
            overview_record.get("net_income"),
            overview_revenue,
        )

        growth_copy = (
            f"Revenue growth: {pct(workspace_growth)} ({income_selection['growth_basis'].lower()})."
            if workspace_growth is not None
            else "Comparable revenue growth is not available for the current reporting period."
        )
        profitability_copy = (
            f" Operating margin: {pct(overview_operating_margin)}."
            if overview_operating_margin is not None
            else ""
        )
        net_copy = (
            f" Net margin: {pct(overview_net_margin)}."
            if overview_net_margin is not None
            else ""
        )

        overview_cards = [
            (
                "What does it do?",
                selected_analysis.get(
                    "business_model",
                    "Structured business-model research is still being added. "
                    "Use the Business & Risks section and original filings for source context.",
                ),
            ),
            (
                "How does it make money?",
                selected_analysis.get(
                    "primary_revenue_source",
                    "The primary revenue source has not been structured yet.",
                ),
            ),
            (
                "Who buys?",
                selected_analysis.get(
                    "customer_type",
                    "Customer-type research has not been structured yet.",
                ),
            ),
            (
                "Growth & profitability",
                growth_copy + profitability_copy + net_copy,
            ),
        ]

        overview_html = "".join(
            (
                '<div class="el-overview-card">'
                f'<div class="el-overview-question">{html.escape(label)}</div>'
                f'<div class="el-overview-answer">{html.escape(str(answer))}</div>'
                '</div>'
            )
            for label, answer in overview_cards
        )
        st.markdown(
            '<div class="el-overview-grid">' + overview_html + '</div>',
            unsafe_allow_html=True,
        )
        st.caption(
            f"Financial snapshot period: {financial_period or 'period unavailable'} · "
            f"Financial source: {revenue_source_label}."
        )

        research_path_cols = st.columns(4)
        research_path = [
            (
                "1 · Understand",
                "Business & Risks",
                "Business model, revenue engine, customers, and disclosed risks.",
            ),
            (
                "2 · Measure",
                "Financials",
                "Growth, margins, profitability, cash, debt, and reported periods.",
            ),
            (
                "3 · Verify",
                "SEC Filings",
                "Read the original 10-K, 10-Q, 8-K, and registration documents.",
            ),
            (
                "4 · Compare",
                "Peers & ETFs",
                "Put the company beside others in the same industry.",
            ),
        ]
        for col, (step, destination, description) in zip(
            research_path_cols,
            research_path,
        ):
            with col:
                st.markdown(f"**{step}**")
                st.caption(description)
                st.caption(f"Workspace section: {destination}")

        summary_columns = st.columns(2)
        with summary_columns[0]:
            st.markdown("**Key disclosed risks to investigate**")
            summary_risks = selected_analysis.get("key_risk_themes", [])
            if summary_risks:
                for risk in summary_risks[:4]:
                    st.write(f"• {risk}")
            else:
                st.caption(
                    "Structured risk themes are still being added. "
                    "Review Risk Factors in the original filing."
                )

        with summary_columns[1]:
            st.markdown("**Latest source filing**")
            if latest_available_filing:
                st.write(f"{filing_form} · Filed {filing_date}")
                filing_description = (
                    latest_available_filing.get("description")
                    or latest_available_filing.get("primary_document")
                )
                if filing_description:
                    st.caption(str(filing_description))
                if latest_available_filing.get("url"):
                    st.link_button(
                        "Open original SEC filing",
                        latest_available_filing["url"],
                        key=f"overview_latest_filing_{selected_ticker}",
                    )
            else:
                st.caption("No filing is available in the current feed yet.")

        with st.expander("Need help reading these numbers?"):
            st.markdown(
                "**Revenue:** sales before expenses.\n\n"
                "**Operating margin:** operating profit as a percentage of revenue.\n\n"
                "**Net margin:** final profit or loss as a percentage of revenue.\n\n"
                "**LTM:** the most recent twelve months of results.\n\n"
                "**YoY:** comparison with the same period one year earlier.\n\n"
                "**10-K / 10-Q:** annual / quarterly SEC reports."
            )
            st.button(
                "Open Learn",
                key="summary_open_learn",
                on_click=navigate_to,
                args=("Learn",),
            )

        snapshot_chart_col, snapshot_context_col = st.columns([1.65, 1])

        with snapshot_chart_col:
            st.markdown("**Price Performance**")
            chart_range = st.radio(
                "Range",
                ["1M", "3M", "1Y", "2Y"],
                index=2,
                horizontal=True,
                key=f"workspace_chart_range_{selected_ticker}",
                label_visibility="collapsed",
            )
            try:
                selected_history = get_market_history(
                    selected_ticker,
                    interval="1day",
                    outputsize=None,
                    calendar_range=chart_range,
                )
            except Exception:
                selected_history = pd.DataFrame()

            if not selected_history.empty:
                price_fig = go.Figure(
                    go.Scatter(
                        x=selected_history["datetime"],
                        y=selected_history["close"],
                        mode="lines",
                        name=selected_ticker,
                        line={"color": "#16C7B2", "width": 2},
                    )
                )
                price_fig.update_layout(
                    height=390,
                    margin={"l": 8, "r": 8, "t": 22, "b": 8},
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font={"color": "#8F9CA6", "family": "IBM Plex Sans"},
                    hovermode="x unified",
                    showlegend=False,
                    xaxis={"showgrid": False, "zeroline": False, "title": None},
                    yaxis={
                        "gridcolor": "rgba(143,156,166,.12)",
                        "zeroline": False,
                        "title": None,
                        "tickprefix": "$",
                    },
                )
                st.plotly_chart(
                    price_fig,
                    use_container_width=True,
                    config={"displayModeBar": False},
                )
            else:
                st.info("Price history is temporarily unavailable.")

        with snapshot_context_col:
            st.markdown("**Company Snapshot**")
            snapshot_items = [
                ("Primary revenue source", selected_analysis.get("primary_revenue_source", "Research in progress.")),
                ("Customer type", selected_analysis.get("customer_type", "Research in progress.")),
                ("Platform / operating dependency", selected_analysis.get("platform_dependency", "Research in progress.")),
            ]
            for label, value in snapshot_items:
                st.markdown(f"**{label}**")
                st.write(value)

        st.markdown("---")
        snapshot_left, snapshot_right = st.columns(2)

        with snapshot_left:
            st.markdown("**What changed recently**")
            change_notes = build_change_notes(selected_qdata)
            if not change_notes:
                annual_history = selected_data.get("history", []) or selected_fallback_history
                if len(annual_history) >= 2:
                    latest_year = annual_history[-1]
                    prior_year = annual_history[-2]
                    annual_growth = calc_growth(
                        latest_year.get("revenue"),
                        prior_year.get("revenue"),
                    )
                    if annual_growth is not None:
                        change_notes = [(
                            "Annual revenue",
                            f"Revenue changed {annual_growth:+.1f}% from "
                            f"FY{prior_year.get('fiscal_year')} to FY{latest_year.get('fiscal_year')}.",
                        )]

            if change_notes:
                for label, copy in change_notes[:4]:
                    st.markdown(f"**{label}**")
                    st.write(copy)
            else:
                st.caption("Recent standardized period-over-period changes are still being prepared.")

        with snapshot_right:
            st.markdown("**Key disclosed risk themes**")
            risk_themes = selected_analysis.get("key_risk_themes", [])
            if risk_themes:
                for risk in risk_themes[:8]:
                    st.markdown(f"- {risk}")
            else:
                st.caption("Structured risk themes are being added as deep research coverage expands.")

        st.markdown("**Recent SEC activity**")
        if selected_filings:
            snapshot_filing_rows = [
                {
                    "Filed": filing.get("filing_date", ""),
                    "Form": filing.get("form", ""),
                    "Description": filing.get("description", "") or filing.get("primary_document", ""),
                    "SEC Filing": filing.get("url", ""),
                }
                for filing in selected_filings[:6]
            ]
            st.dataframe(
                pd.DataFrame(snapshot_filing_rows),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "SEC Filing": st.column_config.LinkColumn("SEC Filing", display_text="Open")
                },
            )
        elif selected_sec_error:
            st.warning(selected_sec_error)
        else:
            st.caption("Recent filing metadata is not available yet.")

        section("Evidence", "Verify the research")
        render_company_evidence(
            st,
            selected_ticker,
            selected_analysis,
            selected_filings,
            pct(workspace_growth),
            financial_period,
        )

        with st.expander("Export this research"):
            st.caption(
                "Download a dated EquityLens research summary for offline review. "
                "Primary filings remain the authoritative source."
            )
            render_report_download(
                st,
                selected_name,
                selected_ticker,
                selected_industry_name,
                selected_sector_name,
                selected_analysis,
                selected_filings,
                {
                    "Price (Yahoo Finance, may be delayed)": (
                        "$" + f"{selected_price:,.2f}"
                        if selected_price is not None
                        else "Not available"
                    ),
                    "Revenue": format_money(workspace_revenue),
                    "Revenue growth": pct(workspace_growth),
                    "Reporting period": financial_period or "See Financials",
                    "Data source": revenue_source_label,
                    "Most recent filing": f"{filing_form} · {filing_date}",
                },
            )

    if company_section == "Business & Risks":
        section(
            "Business & Risks",
            "How the Business Works & What Could Disrupt It",
        )
        st.caption(
            "EquityLens structures qualitative company disclosures into a repeatable research framework. "
            "These are research summaries, not investment ratings. Verify material details in the source filing."
        )

        business_framework = [
            (
                "Business model",
                "What does the company actually sell or provide?",
                selected_analysis.get(
                    "business_model",
                    "Structured business-model research is not available yet.",
                ),
                "Start here. A financial result is difficult to interpret if you do not understand what creates the revenue.",
            ),
            (
                "Revenue engine",
                "How does money enter the business?",
                selected_analysis.get(
                    "primary_revenue_source",
                    "Structured revenue-source research is not available yet.",
                ),
                "Look for recurring subscriptions, transactions, advertising, hardware, services, usage, or other major revenue drivers.",
            ),
            (
                "Customers",
                "Who pays the company?",
                selected_analysis.get(
                    "customer_type",
                    "Structured customer research is not available yet.",
                ),
                "Customer type affects sales cycles, retention, pricing power, concentration risk, and sensitivity to economic conditions.",
            ),
            (
                "Operating dependencies",
                "What does the business rely on to operate?",
                selected_analysis.get(
                    "platform_dependency",
                    "Structured dependency research is not available yet.",
                ),
                "Dependencies can include cloud platforms, suppliers, distribution channels, app stores, partners, data, or third-party infrastructure.",
            ),
            (
                "Profitability history",
                "Has the business historically produced operating profit?",
                selected_analysis.get(
                    "profitability_history",
                    "Structured profitability history is not available yet.",
                ),
                "Growth and profitability should be read together. Fast growth does not automatically mean strong unit economics or durable profit.",
            ),
            (
                "International exposure",
                "How exposed is the company outside its home market?",
                selected_analysis.get(
                    "international_exposure",
                    "Structured international-exposure research is not available yet.",
                ),
                "International operations can add growth opportunities as well as currency, regulatory, tax, geopolitical, and execution risks.",
            ),
        ]

        business_html = "".join(
            (
                '<div class="el-framework-card">'
                f'<div class="el-framework-label">{html.escape(label)}</div>'
                f'<div class="el-framework-question">{html.escape(question)}</div>'
                f'<div class="el-framework-answer">{html.escape(str(answer))}</div>'
                f'<div class="el-framework-why"><strong>Why it matters:</strong> {html.escape(why)}</div>'
                '</div>'
            )
            for label, question, answer, why in business_framework
        )
        st.markdown(
            '<div class="el-framework-grid">' + business_html + '</div>',
            unsafe_allow_html=True,
        )

        section("Risk framework", "What could change the story?")
        st.caption(
            "SEC risk disclosures are intentionally broad. EquityLens groups the available research into themes "
            "so users can investigate the original language rather than treating a long risk list as a prediction."
        )

        risk_framework = [
            (
                "Competition",
                selected_analysis.get(
                    "competitive_risk",
                    "Structured competitive-risk research is not available yet.",
                ),
                "Watch product substitution, pricing pressure, larger incumbents, new entrants, and customer switching behavior.",
            ),
            (
                "Operations",
                selected_analysis.get(
                    "operational_risk",
                    "Structured operational-risk research is not available yet.",
                ),
                "Watch execution, capacity, reliability, supply chain, implementation, sales productivity, and other operating dependencies.",
            ),
            (
                "Customer concentration",
                selected_analysis.get(
                    "customer_concentration",
                    "Structured customer-concentration research is not available yet.",
                ),
                "A small number of important customers can make revenue less diversified and increase renewal or bargaining risk.",
            ),
            (
                "International / regulatory",
                selected_analysis.get(
                    "international_exposure",
                    "Structured international or regulatory risk research is not available yet.",
                ),
                "Cross-border operations can create currency, privacy, tax, sanctions, licensing, and geopolitical exposure.",
            ),
        ]

        risk_html = "".join(
            (
                '<div class="el-framework-card risk">'
                f'<div class="el-framework-label">{html.escape(label)}</div>'
                f'<div class="el-framework-answer">{html.escape(str(answer))}</div>'
                f'<div class="el-framework-why"><strong>Research prompt:</strong> {html.escape(prompt)}</div>'
                '</div>'
            )
            for label, answer, prompt in risk_framework
        )
        st.markdown(
            '<div class="el-framework-grid risk-grid">' + risk_html + '</div>',
            unsafe_allow_html=True,
        )

        st.markdown("**Key disclosed risk themes**")
        risk_themes = selected_analysis.get("key_risk_themes", [])
        if risk_themes:
            risk_theme_cols = st.columns(2)
            for index, risk in enumerate(risk_themes):
                with risk_theme_cols[index % 2]:
                    st.markdown(f"- {risk}")
        else:
            st.caption(
                "Structured risk themes are not available yet. "
                "Review the Risk Factors section in the original SEC filing."
            )

        filing_changes = selected_analysis.get(
            "filing_changes",
            {},
        )
        section(
            "Filing changes",
            "What changed from the prior annual filing?",
        )
        if filing_changes.get("comparison_available"):
            current_label = filing_changes.get(
                "current_filing_label",
                "Current annual filing",
            )
            prior_label = filing_changes.get(
                "prior_filing_label",
                "Prior annual filing",
            )
            st.caption(
                f"Comparison: {prior_label} → {current_label}. "
                "This section summarizes changes in supplied SEC filing evidence; it does not predict their impact."
            )

            change_cols = st.columns(2)
            change_groups = [
                (
                    "Added or more prominent",
                    filing_changes.get(
                        "added_or_increased_themes",
                        [],
                    ),
                ),
                (
                    "Reduced or removed",
                    filing_changes.get(
                        "reduced_or_removed_themes",
                        [],
                    ),
                ),
                (
                    "Notable language changes",
                    filing_changes.get(
                        "notable_language_changes",
                        [],
                    ),
                ),
                (
                    "Core themes that remained",
                    filing_changes.get(
                        "unchanged_core_themes",
                        [],
                    ),
                ),
            ]
            for index, (label, items) in enumerate(change_groups):
                with change_cols[index % 2]:
                    st.markdown(f"**{label}**")
                    if items:
                        for item in items:
                            st.markdown(f"- {item}")
                    else:
                        st.caption(
                            "No supported change was identified in the supplied excerpts."
                        )

            comparison_notes = filing_changes.get(
                "confidence_notes",
                [],
            )
            if comparison_notes:
                with st.expander(
                    "Comparison limitations"
                ):
                    for note in comparison_notes:
                        st.markdown(f"- {note}")
        else:
            st.info(
                "Prior-vs-current annual filing comparison has not been generated for this company yet. "
                "The local deep-research worker now supports this comparison and will add it when the company is refreshed."
            )

        source_filing = selected_analysis.get("source_filing", "")
        if source_filing:
            st.link_button(
                "Open source filing for Business & Risks",
                source_filing,
                key=f"business_risk_source_{selected_ticker}",
            )
        elif latest_annual.get("url"):
            st.link_button(
                "Open latest annual filing",
                latest_annual["url"],
                key=f"business_risk_annual_source_{selected_ticker}",
            )

        st.caption(
            "Research summaries can lag a newly filed report. The original SEC filing is the authoritative disclosure."
        )


    if company_section == "Financials":
        section("Financials", "Income Statement & Balance Sheet")

        latest_financial_period = income_selection["record"]
        financial_period_label = (
            income_selection.get("period")
            or "Reporting period unavailable"
        )
        financial_source_label = (
            income_selection.get("source")
            or "Source unavailable"
        )

        period_revenue = latest_financial_period.get("revenue")
        period_gross_profit = latest_financial_period.get("gross_profit")
        period_operating_income = latest_financial_period.get("operating_income")
        period_net_income = latest_financial_period.get("net_income")

        gross_margin_value = calc_margin(
            period_gross_profit,
            period_revenue,
        )
        operating_margin_value = calc_margin(
            period_operating_income,
            period_revenue,
        )
        net_margin_value = calc_margin(
            period_net_income,
            period_revenue,
        )

        st.caption(
            f"Reporting period: {financial_period_label} · "
            f"Source: {financial_source_label}. "
            "Reported values come from the selected source record; margins and growth are calculated by EquityLens."
        )

        primary_financial_cols = st.columns(4)
        primary_financial_cols[0].metric(
            "Revenue · Reported",
            format_money(period_revenue),
            help=f"Reported revenue for {financial_period_label}.",
        )
        primary_financial_cols[1].metric(
            "Revenue Growth · Calculated",
            pct(workspace_growth),
            help=income_selection.get(
                "growth_basis",
                "Comparable-period revenue growth.",
            ),
        )
        primary_financial_cols[2].metric(
            "Operating Margin · Calculated",
            pct(operating_margin_value),
            help="Operating income divided by revenue for the same reporting period.",
        )
        primary_financial_cols[3].metric(
            "Net Income · Reported",
            format_money(period_net_income),
            help=f"Reported net income or loss for {financial_period_label}.",
        )

        secondary_financial_cols = st.columns(4)
        secondary_financial_cols[0].metric(
            "Gross Profit · Reported",
            format_money(period_gross_profit),
        )
        secondary_financial_cols[1].metric(
            "Gross Margin · Calculated",
            pct(gross_margin_value),
            help="Gross profit divided by revenue for the same reporting period.",
        )
        secondary_financial_cols[2].metric(
            "Operating Income · Reported",
            format_money(period_operating_income),
        )
        secondary_financial_cols[3].metric(
            "Net Margin · Calculated",
            pct(net_margin_value),
            help="Net income divided by revenue for the same reporting period.",
        )

        st.caption(
            "Reported = taken from the selected financial source. "
            "Calculated = derived by EquityLens from reported figures in the same period. "
            "Unavailable values are not treated as zero."
        )

        exact_financial_rows = [
            {
                "Metric": "Revenue",
                "Value": format_money(period_revenue),
                "Type": "Reported",
                "Period": financial_period_label,
                "Source": financial_source_label,
            },
            {
                "Metric": "Gross Profit",
                "Value": format_money(period_gross_profit),
                "Type": "Reported",
                "Period": financial_period_label,
                "Source": financial_source_label,
            },
            {
                "Metric": "Operating Income",
                "Value": format_money(period_operating_income),
                "Type": "Reported",
                "Period": financial_period_label,
                "Source": financial_source_label,
            },
            {
                "Metric": "Net Income",
                "Value": format_money(period_net_income),
                "Type": "Reported",
                "Period": financial_period_label,
                "Source": financial_source_label,
            },
            {
                "Metric": "Revenue Growth",
                "Value": pct(workspace_growth),
                "Type": "Calculated",
                "Period": financial_period_label,
                "Source": income_selection.get("growth_basis", ""),
            },
            {
                "Metric": "Gross Margin",
                "Value": pct(gross_margin_value),
                "Type": "Calculated",
                "Period": financial_period_label,
                "Source": "Gross profit ÷ revenue",
            },
            {
                "Metric": "Operating Margin",
                "Value": pct(operating_margin_value),
                "Type": "Calculated",
                "Period": financial_period_label,
                "Source": "Operating income ÷ revenue",
            },
            {
                "Metric": "Net Margin",
                "Value": pct(net_margin_value),
                "Type": "Calculated",
                "Period": financial_period_label,
                "Source": "Net income ÷ revenue",
            },
        ]
        with st.expander("Show exact values, periods & calculation labels"):
            st.dataframe(
                pd.DataFrame(exact_financial_rows),
                use_container_width=True,
                hide_index=True,
            )

        annual_history = income_selection["annual_history"]
        st.caption(f"Annual trend source: {income_selection['annual_source']}")
        financial_chart_cols = st.columns(2)

        with financial_chart_cols[0]:
            st.markdown("**Annual Revenue Trend**")
            annual_rows = [
                row for row in annual_history
                if row.get("fiscal_year") is not None and row.get("revenue") is not None
            ]
            if annual_rows:
                annual_df = pd.DataFrame(annual_rows)
                annual_fig = go.Figure(
                    go.Bar(
                        x=annual_df["fiscal_year"].astype(str),
                        y=annual_df["revenue"],
                        name="Revenue",
                        marker={"color": "#16C7B2"},
                    )
                )
                annual_fig.update_layout(
                    height=330,
                    margin={"l": 8, "r": 8, "t": 20, "b": 8},
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font={"color": "#8F9CA6", "family": "IBM Plex Sans"},
                    showlegend=False,
                    xaxis={"showgrid": False, "title": None},
                    yaxis={"gridcolor": "rgba(143,156,166,.12)", "title": None},
                )
                st.plotly_chart(annual_fig, use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("Annual revenue history is still being standardized.")

        with financial_chart_cols[1]:
            st.markdown("**Latest P&L Structure**")
            pnl_labels = ["Revenue", "Gross Profit", "Operating Income", "Net Income"]
            pnl_values = [
                latest_financial_period.get("revenue"),
                latest_financial_period.get("gross_profit"),
                latest_financial_period.get("operating_income"),
                latest_financial_period.get("net_income"),
            ]
            if any(value is not None for value in pnl_values):
                pnl_fig = go.Figure(
                    go.Bar(
                        x=pnl_labels,
                        y=pnl_values,
                        marker={"color": "#7DD3FC"},
                    )
                )
                pnl_fig.update_layout(
                    height=330,
                    margin={"l": 8, "r": 8, "t": 20, "b": 8},
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font={"color": "#8F9CA6", "family": "IBM Plex Sans"},
                    showlegend=False,
                    xaxis={"showgrid": False, "title": None},
                    yaxis={"gridcolor": "rgba(143,156,166,.12)", "title": None},
                )
                st.plotly_chart(pnl_fig, use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("P&L data is still being standardized.")

        latest_q = selected_qdata.get("latest_quarter", {})
        prior_q = selected_qdata.get("prior_quarter", {})
        prior_y_q = selected_qdata.get("prior_year_quarter", {})

        if not latest_q and selected_fallback_quarters:
            latest_q = selected_fallback_quarters[-1]
            prior_q = (
                selected_fallback_quarters[-2]
                if len(selected_fallback_quarters) >= 2
                else {}
            )
            prior_y_q = (
                selected_fallback_quarters[-5]
                if len(selected_fallback_quarters) >= 5
                else {}
            )

        if latest_q and (prior_q or prior_y_q):
            st.markdown("**Quarterly Financial Comparison**")
            quarter_series = []
            for label, payload in [
                ("Prior Year Quarter", prior_y_q),
                ("Prior Quarter", prior_q),
                ("Latest Quarter", latest_q),
            ]:
                if payload:
                    quarter_series.append({
                        "Period": label,
                        "Revenue": payload.get("revenue"),
                        "Gross Profit": payload.get("gross_profit"),
                        "Operating Income": payload.get("operating_income"),
                        "Net Income": payload.get("net_income"),
                    })

            quarter_df = pd.DataFrame(quarter_series)
            quarter_fig = go.Figure()
            for metric in ["Revenue", "Gross Profit", "Operating Income", "Net Income"]:
                quarter_fig.add_trace(go.Bar(name=metric, x=quarter_df["Period"], y=quarter_df[metric]))
            quarter_fig.update_layout(
                barmode="group",
                height=380,
                margin={"l": 8, "r": 8, "t": 30, "b": 8},
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font={"color": "#8F9CA6", "family": "IBM Plex Sans"},
                legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "left", "x": 0},
                xaxis={"showgrid": False, "title": None},
                yaxis={"gridcolor": "rgba(143,156,166,.12)", "title": None},
            )
            st.plotly_chart(quarter_fig, use_container_width=True, config={"displayModeBar": False})

        st.markdown("**Balance Sheet Snapshot**")
        capital_structure = selected_data.get("capital_structure", {})
        fallback_capital = selected_financial_fallback.get("capital_structure", {})

        structured_balance_values = [
            capital_structure.get("cash_and_investments"),
            capital_structure.get("total_debt"),
            selected_data.get("cash"),
            selected_data.get("assets"),
        ]
        use_structured_balance = any(
            value is not None
            for value in structured_balance_values
        )
        balance_record = (
            capital_structure
            if use_structured_balance
            else fallback_capital
        )
        balance_source = (
            "Structured company balance sheet"
            if use_structured_balance
            else "Yahoo Finance balance sheet"
        )
        cash_value = (
            selected_data.get("cash")
            if use_structured_balance
            else balance_record.get("cash")
        )
        cash_investments_value = balance_record.get(
            "cash_and_investments"
        )
        debt_value = balance_record.get("total_debt")
        assets_value = (
            selected_data.get("assets")
            if use_structured_balance
            else (
                balance_record.get("total_assets")
                or balance_record.get("assets")
            )
        )
        st.caption(
            f"Balance sheet: {balance_record.get('balance_sheet_as_of') or selected_data.get('fiscal_year_end') or 'Date unavailable'} · {balance_source}. "
            "Its reporting date may differ from the income statement."
        )

        balance_cols = st.columns(4)
        balance_cols[0].metric("Cash", format_money(cash_value))
        balance_cols[1].metric("Cash + Investments", format_money(cash_investments_value))
        balance_cols[2].metric("Total Debt", format_money(debt_value))
        balance_cols[3].metric("Total Assets", format_money(assets_value))

        financial_source = income_selection.get("source_url")
        if financial_source:
            st.link_button(
                "Open source financial filing",
                financial_source,
                key=f"workspace_financial_source_{selected_ticker}",
            )

        with st.expander("Sources & formulas"):
            source_rows = [
                {
                    "Dataset": "Income statement",
                    "Period / date": financial_period_label,
                    "Source": financial_source_label,
                    "Original source": financial_source or "No direct filing link for this fallback source",
                },
                {
                    "Dataset": "Balance sheet",
                    "Period / date": (
                        balance_record.get("balance_sheet_as_of")
                        or selected_data.get("fiscal_year_end")
                        or "Date unavailable"
                    ),
                    "Source": balance_source,
                    "Original source": (
                        capital_structure.get("source_filing")
                        if use_structured_balance
                        else "Supplemental Yahoo Finance statement"
                    ) or "Source link unavailable",
                },
            ]
            source_display = pd.DataFrame(source_rows)
            st.dataframe(
                source_display,
                use_container_width=True,
                hide_index=True,
            )
            balance_source_url = (
                capital_structure.get("source_filing")
                if use_structured_balance
                else ""
            )
            source_link_cols = st.columns(2)
            with source_link_cols[0]:
                if financial_source:
                    st.link_button(
                        "Open income-statement source",
                        financial_source,
                        key=f"financial_provenance_income_{selected_ticker}",
                        use_container_width=True,
                    )
            with source_link_cols[1]:
                if balance_source_url:
                    st.link_button(
                        "Open balance-sheet source",
                        balance_source_url,
                        key=f"financial_provenance_balance_{selected_ticker}",
                        use_container_width=True,
                    )
            st.markdown(
                "**Calculated metrics**\n\n"
                "- Revenue growth = (current revenue − comparable prior revenue) ÷ comparable prior revenue × 100.\n"
                "- Gross margin = gross profit ÷ revenue × 100.\n"
                "- Operating margin = operating income ÷ revenue × 100.\n"
                "- Net margin = net income ÷ revenue × 100."
            )
            st.caption(
                "EquityLens does not replace a missing reported figure with zero. "
                "Calculations are shown only when the required source values exist."
            )

        st.caption(
            "EquityLens uses standardized SEC-reported figures when available. "
             "Income statements and balance sheets each use a single source record; "
            "missing fields remain unavailable. Annual trends can use labeled Yahoo Finance fallback history. "
            "Market values and financial statement periods update on different schedules."
        )

    if company_section == "SEC Filings":
        section("SEC Filings", "Current & Periodic Filing History")
        st.caption(
            "Use this section for ongoing public-company disclosures. "
            "IPO-era registration statements live in the separate IPO / Registration section."
        )

        filing_metric_cols = st.columns(4)
        filing_metric_cols[0].metric(
            "Annual",
            latest_annual.get("form", "N/A"),
            latest_annual.get("filing_date") or None,
        )
        filing_metric_cols[1].metric(
            "Quarterly",
            latest_quarter.get("form", "N/A"),
            latest_quarter.get("filing_date") or None,
        )
        filing_metric_cols[2].metric(
            "Current Report",
            latest_current.get("form", "N/A"),
            latest_current.get("filing_date") or None,
        )
        filing_metric_cols[3].metric(
            "Registration",
            primary_registration.get("form", "Not found"),
            primary_registration.get("filing_date") or None,
            help="Registration filings are analyzed separately because they describe IPO-era or offering-era context.",
        )

        if selected_sec_error:
            st.warning(selected_sec_error)

        if selected_filings:
            filing_table = pd.DataFrame([
                {
                    "Filed": filing.get("filing_date", ""),
                    "Form": filing.get("form", ""),
                    "Report Period": filing.get("report_date", ""),
                    "Description": (
                        filing.get("description", "")
                        or filing.get("primary_document", "")
                    ),
                    "SEC Filing": filing.get("url", ""),
                }
                for filing in selected_filings[:25]
            ])
            st.dataframe(
                filing_table,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "SEC Filing": st.column_config.LinkColumn(
                        "SEC Filing",
                        display_text="Open filing",
                    )
                },
            )
            st.caption(
                "Showing the 25 most recent filings returned by the current company feed. "
                "Use the complete SEC history link for older documents."
            )
        else:
            st.info(
                "Recent SEC filing metadata is not available for this company right now."
            )

        if selected_sec.get("sec_company_url"):
            st.link_button(
                "Open complete SEC company history",
                selected_sec.get("sec_company_url"),
                key=f"workspace_sec_history_{selected_ticker}",
            )

    if company_section == "IPO / Registration":
        section(
            "IPO / Registration",
            "How the Company Described Itself Before or During the Offering",
        )
        st.caption(
            "Registration filings are historical documents. They can explain the company's original "
            "business model, ownership, risks, capitalization, and offering structure, but they should "
            "not be treated as current company facts without checking newer filings."
        )

        if selected_registrations:
            st.markdown("**Registration filing timeline**")
            registration_table = pd.DataFrame([
                {
                    "Filed": filing.get("filing_date", ""),
                    "Form": filing.get("form", ""),
                    "Description": (
                        filing.get("description", "")
                        or filing.get("primary_document", "")
                    ),
                    "SEC Filing": filing.get("url", ""),
                }
                for filing in selected_registrations
            ])
            st.dataframe(
                registration_table,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "SEC Filing": st.column_config.LinkColumn(
                        "SEC Filing",
                        display_text="Open filing",
                    )
                },
            )
            st.caption(
                "Amendments such as S-1/A or F-1/A can update financials, pricing, share counts, "
                "ownership, risk disclosure, or other offering terms."
            )

        if selected_s1:
            ipo_header_cols = st.columns(3)
            ipo_header_cols[0].metric(
                "Form",
                selected_s1.get("form", "Registration"),
            )
            ipo_header_cols[1].metric(
                "Filed",
                selected_s1.get("filed_date", "Date unavailable"),
            )
            ipo_header_cols[2].metric(
                "Context",
                "Historical",
                help="This research describes registration-era disclosures, not necessarily the company's current business.",
            )

            st.markdown("**Historical context**")
            st.write(
                selected_s1.get(
                    "historical_context",
                    "Historical registration context is available.",
                )
            )
            st.markdown("**What this filing can teach you**")
            st.write(
                selected_s1.get(
                    "what_to_learn",
                    "Review the original registration filing for business, risk, ownership, and financial context.",
                )
            )

            detail_map = selected_s1.get("filing_details", {})
            detail_sections = [
                (
                    "Business & Revenue Model",
                    "business_revenue_model",
                    "How the company described what it sold and how revenue was generated at the time of registration.",
                ),
                (
                    "Customers & Go-to-Market",
                    "customers_go_to_market",
                    "Customer base, sales motion, retention, expansion, and distribution context disclosed before the offering.",
                ),
                (
                    "Growth & Market Opportunity",
                    "growth_market_opportunity",
                    "Management's historical description of expansion opportunities and growth vectors.",
                ),
                (
                    "Competition & Differentiation",
                    "competition_differentiation",
                    "How management positioned the company against alternatives at the time.",
                ),
                (
                    "Risk Factors",
                    "risk_factors",
                    "Major offering-era risks disclosed to prospective investors.",
                ),
                (
                    "Financial History",
                    "financial_history",
                    "Pre-offering revenue, profitability, cash-flow, and other financial context captured in the filing.",
                ),
                (
                    "Capitalization & Dilution",
                    "ipo_capitalization_dilution",
                    "Share classes, voting structure, offering capitalization, and dilution context.",
                ),
                (
                    "Proceeds, Management & Ownership",
                    "proceeds_management_ownership",
                    "Use of proceeds and the management / ownership structure around the offering.",
                ),
            ]

            for label, field, explanation in detail_sections:
                with st.expander(label, expanded=(label == "Business & Revenue Model")):
                    st.caption(explanation)
                    points = detail_map.get(field, [])
                    if points:
                        for point in points:
                            st.markdown(f"- {point}")
                    else:
                        st.caption(
                            "Structured detail is not available for this part of the registration filing yet."
                        )

            if selected_s1.get("source_url"):
                st.link_button(
                    f"Open original {selected_s1.get('form', 'registration filing')} on SEC EDGAR",
                    selected_s1.get("source_url"),
                    key=f"workspace_s1_source_{selected_ticker}",
                )
        elif selected_registrations:
            st.info(
                "EquityLens has indexed the registration filing history, but the deep structured "
                "registration analysis has not been generated for this company yet."
            )
            first_registration = selected_registrations[0]
            if first_registration.get("url"):
                st.link_button(
                    f"Open {first_registration.get('form', 'registration filing')} on SEC EDGAR",
                    first_registration["url"],
                    key=f"workspace_registration_direct_{selected_ticker}",
                )
        else:
            st.info(
                "No S-1, F-1, or S-11 registration statement was found in the indexed SEC history. "
                "Some older issuers, foreign issuers, reorganizations, or companies with limited electronic filing history "
                "may not have a registration statement available in the current feed."
            )

    if company_section == "Ownership":
        section("Ownership", "Ownership & Major Holders")
        st.caption(
            "Ownership combines SEC beneficial-ownership filings with supplemental institutional and fund-holder data. "
            "Percentages and holder tables can update on a different schedule from company filings."
        )

        try:
            ownership_data = get_company_ownership_data(selected_ticker)
        except Exception:
            ownership_data = {
                "major": pd.DataFrame(),
                "institutional": pd.DataFrame(),
                "mutual_fund": pd.DataFrame(),
            }

        major_table = ownership_data.get("major", pd.DataFrame())
        major_lookup = {}
        if isinstance(major_table, pd.DataFrame) and not major_table.empty:
            major_copy = major_table.copy()
            key_column = next(
                (
                    column
                    for column in ["index", "Breakdown", "Metric"]
                    if column in major_copy.columns
                ),
                major_copy.columns[0],
            )
            value_column = next(
                (
                    column
                    for column in ["Value", "value"]
                    if column in major_copy.columns
                ),
                major_copy.columns[-1],
            )
            for _, row in major_copy.iterrows():
                major_lookup[str(row.get(key_column, ""))] = row.get(value_column)

        def _ownership_pct(value):
            number = safe_float(value)
            if number is None:
                return "N/A"
            if abs(number) <= 1:
                number *= 100
            return f"{number:.1f}%"

        def _ownership_count(value):
            number = safe_float(value)
            return f"{int(number):,}" if number is not None else "N/A"

        ownership_summary_cols = st.columns(4)
        ownership_summary_cols[0].metric(
            "Insider ownership",
            _ownership_pct(
                major_lookup.get(
                    "insidersPercentHeld",
                    major_lookup.get("% of Shares Held by All Insider", None),
                )
            ),
        )
        ownership_summary_cols[1].metric(
            "Institutional ownership",
            _ownership_pct(
                major_lookup.get(
                    "institutionsPercentHeld",
                    major_lookup.get("% of Shares Held by Institutions", None),
                )
            ),
        )
        ownership_summary_cols[2].metric(
            "Institutional float",
            _ownership_pct(
                major_lookup.get(
                    "institutionsFloatPercentHeld",
                    major_lookup.get("% of Float Held by Institutions", None),
                )
            ),
        )
        ownership_summary_cols[3].metric(
            "Institutional holders",
            _ownership_count(
                major_lookup.get(
                    "institutionsCount",
                    major_lookup.get("Number of Institutions Holding Shares", None),
                )
            ),
        )

        st.markdown("**SEC beneficial-ownership filings**")
        ownership_forms = {
            "DEF 14A",
            "DEFA14A",
            "SC 13D",
            "SC 13D/A",
            "SC 13G",
            "SC 13G/A",
        }
        sec_ownership_rows = [
            {
                "Filed": filing.get("filing_date", ""),
                "Form": filing.get("form", ""),
                "Description": (
                    filing.get("description", "")
                    or filing.get("primary_document", "")
                ),
                "SEC Filing": filing.get("url", ""),
            }
            for filing in selected_filings
            if filing.get("form") in ownership_forms
        ][:20]

        if sec_ownership_rows:
            st.dataframe(
                pd.DataFrame(sec_ownership_rows),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "SEC Filing": st.column_config.LinkColumn(
                        "SEC Filing",
                        display_text="Open",
                    )
                },
            )
        else:
            st.caption(
                "No proxy or Schedule 13D/13G filing appeared in the currently loaded SEC history."
            )

        def _clean_holder_table(table):
            if not isinstance(table, pd.DataFrame) or table.empty:
                return pd.DataFrame()

            cleaned = table.copy()
            cleaned = cleaned.drop(
                columns=[column for column in ["index"] if column in cleaned.columns],
                errors="ignore",
            )
            cleaned = cleaned.rename(
                columns={
                    "Date Reported": "Reported",
                    "pctHeld": "% Held",
                    "pctChange": "% Change",
                    "Value": "Position Value",
                }
            )

            if "Reported" in cleaned.columns:
                cleaned["Reported"] = pd.to_datetime(
                    cleaned["Reported"],
                    errors="coerce",
                ).dt.date.astype(str)

            if "% Held" in cleaned.columns:
                cleaned["% Held"] = cleaned["% Held"].apply(
                    lambda value: _ownership_pct(value)
                )

            if "% Change" in cleaned.columns:
                cleaned["% Change"] = cleaned["% Change"].apply(
                    lambda value: _ownership_pct(value)
                )

            if "Shares" in cleaned.columns:
                cleaned["Shares"] = cleaned["Shares"].apply(
                    lambda value: (
                        f"{int(safe_float(value)):,}"
                        if safe_float(value) is not None
                        else "N/A"
                    )
                )

            if "Position Value" in cleaned.columns:
                cleaned["Position Value"] = cleaned["Position Value"].apply(
                    lambda value: format_money(safe_float(value))
                )

            preferred = [
                column
                for column in [
                    "Holder",
                    "Reported",
                    "% Held",
                    "Shares",
                    "Position Value",
                    "% Change",
                ]
                if column in cleaned.columns
            ]
            remaining = [
                column for column in cleaned.columns
                if column not in preferred
            ]
            return cleaned[preferred + remaining]

        st.markdown("**Largest institutional holders**")
        institutional_table = _clean_holder_table(
            ownership_data.get("institutional", pd.DataFrame())
        )
        if not institutional_table.empty:
            st.dataframe(
                institutional_table.head(15),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.caption(
                "Institutional-holder detail is unavailable from the supplemental feed."
            )

        st.markdown("**Largest mutual-fund holders**")
        mutual_table = _clean_holder_table(
            ownership_data.get("mutual_fund", pd.DataFrame())
        )
        if not mutual_table.empty:
            st.dataframe(
                mutual_table.head(15),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.caption(
                "Mutual-fund holder detail is unavailable from the supplemental feed."
            )

        st.caption(
            "SEC filings are the primary ownership source. Institutional and fund-holder tables are supplemental Yahoo Finance data via yfinance."
        )

    if company_section == "Analyst Research":
        section("Analyst Research", "Consensus, Price Targets & Rating Changes")
        st.caption(
            "These are third-party analyst opinions and market-data aggregates. "
            "They are not EquityLens ratings, recommendations, or price forecasts."
        )

        try:
            analyst_data = get_company_analyst_data(selected_ticker)
        except Exception:
            analyst_data = {
                "targets": {},
                "recommendations": pd.DataFrame(),
                "upgrades": pd.DataFrame(),
            }

        targets = analyst_data.get("targets", {}) or {}

        def target_value(*keys):
            for key in keys:
                if key in targets and targets.get(key) is not None:
                    return safe_float(targets.get(key))
            return None

        current_target_price = target_value("current", "currentPrice", "Current")
        mean_target = target_value("mean", "meanPriceTarget", "targetMeanPrice")
        median_target = target_value("median", "medianPriceTarget", "targetMedianPrice")
        low_target = target_value("low", "lowPriceTarget", "targetLowPrice")
        high_target = target_value("high", "highPriceTarget", "targetHighPrice")

        analyst_metric_cols = st.columns(5)
        analyst_metric_cols[0].metric(
            "Current Price",
            ("$" + f"{(current_target_price or selected_price):,.2f}")
            if (current_target_price or selected_price) is not None
            else "N/A",
        )
        analyst_metric_cols[1].metric(
            "Mean Target",
            ("$" + f"{mean_target:,.2f}") if mean_target is not None else "N/A",
        )
        analyst_metric_cols[2].metric(
            "Median Target",
            ("$" + f"{median_target:,.2f}") if median_target is not None else "N/A",
        )
        analyst_metric_cols[3].metric(
            "Low Target",
            ("$" + f"{low_target:,.2f}") if low_target is not None else "N/A",
        )
        analyst_metric_cols[4].metric(
            "High Target",
            ("$" + f"{high_target:,.2f}") if high_target is not None else "N/A",
        )

        recommendations_table = analyst_data.get("recommendations", pd.DataFrame())
        st.markdown("**Recommendation summary**")
        if isinstance(recommendations_table, pd.DataFrame) and not recommendations_table.empty:
            st.dataframe(recommendations_table, use_container_width=True, hide_index=True)
        else:
            st.caption("Consensus recommendation data is unavailable from the supplemental feed.")

        upgrades_table = analyst_data.get("upgrades", pd.DataFrame())
        st.markdown("**Recent upgrades / downgrades**")
        if isinstance(upgrades_table, pd.DataFrame) and not upgrades_table.empty:
            st.dataframe(
                upgrades_table.tail(25).iloc[::-1],
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.caption("Recent analyst rating-change data is unavailable from the supplemental feed.")

        st.caption(
            "Supplemental analyst data: Yahoo Finance via yfinance. "
            "EquityLens does not convert third-party opinions into its own buy, sell, or hold rating."
        )

    if company_section == "Peers & ETFs":
        section("Peers", "Related Companies & Major ETF Exposure")

        peer_rows = workspace_universe[
            (workspace_universe["Industry"] == selected_industry_name)
            & (workspace_universe["Ticker"].astype(str).str.upper() != selected_ticker)
        ].copy()

        if "Market Cap" in peer_rows.columns:
            peer_rows["_market_cap_sort"] = peer_rows["Market Cap"].apply(finviz_numeric)
            peer_rows = peer_rows.sort_values("_market_cap_sort", ascending=False)

        peer_columns = [
            column
            for column in [
                "Ticker", "Company", "Sector", "Industry",
                "Market Cap", "P/E", "Price", "Change",
            ]
            if column in peer_rows.columns
        ]

        st.markdown("**Industry peers**")
        if not peer_rows.empty:
            st.dataframe(
                peer_rows[peer_columns].head(20),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.caption("No additional companies share this exact industry label in the current universe.")

        st.markdown("**Major ETF exposure**")
        st.caption(
            "This scanner checks the published top-holdings lists for a curated set of major broad-market, growth, sector, semiconductor, communication-services, and software ETFs. "
            "It is useful context, not an exhaustive ETF-ownership database."
        )

        etf_state_key = f"workspace_etf_scan_{selected_ticker}"
        if st.button("Scan major ETFs", key=f"workspace_etf_button_{selected_ticker}"):
            st.session_state[etf_state_key] = True

        if st.session_state.get(etf_state_key, False):
            try:
                etf_matches = get_major_etf_exposure(selected_ticker)
            except Exception:
                etf_matches = []

            if etf_matches:
                etf_df = pd.DataFrame(etf_matches)
                if "Holding" in etf_df.columns:
                    etf_df["Holding"] = etf_df["Holding"].apply(
                        lambda value: (
                            f"{safe_float(value) * 100:.2f}%"
                            if safe_float(value) is not None and abs(safe_float(value)) <= 1
                            else (
                                f"{safe_float(value):.2f}%"
                                if safe_float(value) is not None
                                else "N/A"
                            )
                        )
                    )
                st.dataframe(etf_df, use_container_width=True, hide_index=True)
            else:
                st.info(
                    "No match was found in the published top-holdings sample for the ETFs scanned. "
                    "This does not mean no ETF owns the stock; free fund feeds do not expose every holding for every ETF."
                )

        st.caption(
            "Peer groups use the EquityLens industry classification. "
            "ETF holdings are supplemental market data and may be delayed."
        )


