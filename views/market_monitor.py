import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from financial_utils import (
    format_market_price,
    format_market_volume,
    safe_float,
)
from macro_data import (
    format_bls_display,
    get_bloomberg_market_news,
    get_bls_macro_snapshot,
    get_bls_release_calendar,
    get_fed_monetary_updates,
    get_fomc_calendar,
    get_rates_bundle,
    market_provider_error,
    render_market_news_cards,
    render_rates_ticker,
)
from market_data import (
    finviz_numeric,
    get_finviz_screener_data,
    get_live_market_data,
    get_market_history,
    normalize_finviz_screener,
)
from market_tables import render_crisp_table
from ui_components import (
    format_utc_timestamp,
    loading_panel,
    render_refresh_indicator,
    section,
)
from views.market_sections.overview import (
    render_nyse_market_monitor,
)
from views.market_sections.rates import render_rates
from views.market_sections.macro import render_macro
from views.market_sections.calendar import render_calendar
from views.market_sections.overview_workspace import (
    render_overview_workspace,
)
from views.market_sections.stocks import (
    render_stocks_workspace,
)


def render_market_monitor(
    public_finviz_data_enabled,
    industries,
    company_data,
    sec_summary,
    workspace_known_tickers,
    research_link,
):
    section("Market", "Market Monitor")

    st.markdown(
        """
        <div class="el-market-hero">
            <div class="el-market-hero-label">Market-wide context</div>
            <div class="el-market-hero-title">See what is moving without loading every market feed at once.</div>
            <div class="el-market-hero-copy">
                Explore market breadth, company movement, rates, macro data, and official calendars.
                Each workspace loads only the sources needed for the view you choose.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    market_view = st.radio(
        "Market Monitor sections",
        [
            "Overview",
            "Stocks",
            "Rates",
            "Macro",
            "Calendar",
        ],
        horizontal=True,
        key="market_monitor_section",
        label_visibility="collapsed",
    )

    refresh_col, source_col = st.columns([1, 3])
    with refresh_col:
        if st.button(
            f"Refresh {market_view.lower()} data",
            key=f"refresh_market_monitor_{market_view}",
            type="primary",
            use_container_width=True,
        ):
            if market_view == "Overview":
        render_overview_workspace(
            public_finviz_data_enabled=public_finviz_data_enabled,
            workspace_known_tickers=workspace_known_tickers,
            research_link=research_link,
        )

    if market_view == "Stocks":
        render_stocks_workspace(
            industries=industries,
            company_data=company_data,
            sec_summary=sec_summary,
            public_finviz_data_enabled=public_finviz_data_enabled,
        )

    if market_view == "Rates":
        render_rates()

    if market_view == "Macro":
        render_macro()

    if market_view == "Calendar":
        render_calendar()

    st.markdown(
        '<div class="el-market-source">'
        + source_copy[market_view]
        + " · Company-specific fundamentals and filings remain in Company Research."
        + "</div>",
        unsafe_allow_html=True,
    )
