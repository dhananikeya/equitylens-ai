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
                get_live_market_data.clear()
                get_finviz_screener_data.clear()
                get_bloomberg_market_news.clear()
                st.session_state.pop(
                    "market_monitor_snapshot::Overview",
                    None,
                )
            elif market_view == "Stocks":
                get_live_market_data.clear()
                get_finviz_screener_data.clear()
            elif market_view == "Rates":
                get_rates_bundle.clear()
            elif market_view == "Macro":
                get_bls_macro_snapshot.clear()
            elif market_view == "Calendar":
                get_bls_release_calendar.clear()
                get_fomc_calendar.clear()
                get_fed_monetary_updates.clear()
            st.rerun()

    with source_col:
        source_copy = {
            "Overview": "NYSE feed + Yahoo Finance market proxies + linked Bloomberg headlines",
            "Stocks": "Yahoo Finance quotes + market-data screener + SEC filing context",
            "Rates": "U.S. Treasury + Federal Reserve Bank of New York + public swap context",
            "Macro": "U.S. Bureau of Labor Statistics",
            "Calendar": "BLS + Federal Reserve official calendars and releases",
        }
        st.caption(source_copy[market_view])

    if market_view == "Overview":
        section("Market Overview", "NYSE Tape, Heat Map & Broad-Market Context")

        overview_snapshot_key = "market_monitor_snapshot::Overview"
        overview_snapshot = st.session_state.get(
            overview_snapshot_key
        )

        if overview_snapshot is None:
            nyse_finviz = pd.DataFrame()
            nyse_error = ""
            if public_finviz_data_enabled:
                try:
                    nyse_finviz = normalize_finviz_screener(
                        get_finviz_screener_data(
                            filters="exch_nyse"
                        )
                    )
                except Exception as exc:
                    nyse_error = (
                        market_provider_error(
                            "NYSE market feed",
                            exc,
                        )
                        + " Broad-market proxies and linked news remain available."
                    )
            else:
                nyse_error = (
                    "The NYSE market-data feed is not configured. "
                    "Broad-market proxies and news remain available."
                )

            try:
                overview_quotes = get_live_market_data(
                    ["SPY", "QQQ", "GLD", "USO", "UUP"]
                )
            except Exception:
                overview_quotes = {}

            try:
                bloomberg_news = get_bloomberg_market_news()
            except Exception:
                bloomberg_news = []

            overview_snapshot = {
                "nyse_finviz": nyse_finviz,
                "nyse_error": nyse_error,
                "overview_quotes": overview_quotes,
                "bloomberg_news": bloomberg_news,
            }
            st.session_state[
                overview_snapshot_key
            ] = overview_snapshot
        else:
            nyse_finviz = overview_snapshot.get(
                "nyse_finviz",
                pd.DataFrame(),
            )
            nyse_error = overview_snapshot.get(
                "nyse_error",
                "",
            )
            overview_quotes = overview_snapshot.get(
                "overview_quotes",
                {},
            )
            bloomberg_news = overview_snapshot.get(
                "bloomberg_news",
                [],
            )

        if nyse_error:
            st.info(nyse_error)

        render_nyse_market_monitor(
            nyse_finviz,
            workspace_known_tickers,
            research_link,
        )

        st.markdown("**Broad-market proxies · may be delayed**")

        proxy_labels = {
            "SPY": "S&P 500 proxy",
            "QQQ": "Nasdaq-100 proxy",
            "GLD": "Gold proxy",
            "USO": "Oil proxy",
            "UUP": "U.S. dollar proxy",
        }
        overview_retrieval_times = [
            quote.get("retrieved_at")
            for quote in overview_quotes.values()
            if quote.get("retrieved_at")
        ]
        overview_latest_retrieval = (
            max(overview_retrieval_times)
            if overview_retrieval_times
            else ""
        )
        render_refresh_indicator(
            "Market overview refreshed",
            overview_latest_retrieval,
            "Yahoo Finance proxy snapshot",
        )

        proxy_cols = st.columns(len(proxy_labels))
        for col, (symbol, label) in zip(
            proxy_cols,
            proxy_labels.items(),
        ):
            quote = overview_quotes.get(symbol, {})
            change = safe_float(
                quote.get("percent_change")
            )
            col.metric(
                label,
                format_market_price(
                    quote.get("close")
                ),
                (
                    f"{change:+.2f}%"
                    if change is not None
                    else None
                ),
            )
            session = quote.get("quote_session")
            if session:
                col.caption(str(session))

        st.caption(
            "Quote snapshot retrieved: "
            + format_utc_timestamp(
                overview_latest_retrieval,
                fallback="Unavailable",
            )
            + ". Individual proxy cards show the trading session represented."
        )

        section("News", "Linked Market Headlines")

        if bloomberg_news:
            news_context = {
                symbol: safe_float(
                    overview_quotes.get(
                        symbol,
                        {},
                    ).get("percent_change")
                )
                for symbol in proxy_labels
            }
            render_market_news_cards(
                bloomberg_news,
                market_context=news_context,
            )
            st.caption(
                "Bloomberg supplies the linked headlines. EquityLens does not copy article text "
                "or infer that a headline caused a market move."
            )
        else:
            st.info(
                "The linked market-news feed is temporarily unavailable. "
                "Market data above remains independent of the news feed."
            )
            st.link_button(
                "Open Bloomberg Markets",
                "https://www.bloomberg.com/markets",
                use_container_width=True,
            )

    if market_view == "Stocks":
        section("Stocks", "Industry Market Board & Movement")

        controls = st.columns([2, 1])
        with controls[0]:
            market_industry = st.selectbox(
                "Industry",
                industries,
                key="market_monitor_industry",
            )
        with controls[1]:
            movement_threshold = st.number_input(
                "Notable move threshold (%)",
                min_value=0.5,
                max_value=25.0,
                value=3.0,
                step=0.5,
                key="market_movement_threshold",
            )

        market_companies = [
            name
            for name, company in company_data.items()
            if company.get(
                "industry",
                "Unclassified",
            ) == market_industry
        ]
        industry_symbols = [
            str(
                company_data[name].get(
                    "ticker",
                    "",
                )
            ).upper()
            for name in market_companies
            if company_data[name].get("ticker")
        ]

        try:
            stock_quotes = get_live_market_data(
                ["SPY", "QQQ"] + industry_symbols
            )
        except Exception:
            stock_quotes = {}

        benchmark_market = {
            symbol: stock_quotes.get(symbol, {})
            for symbol in ["SPY", "QQQ"]
        }
        industry_market = {
            symbol: stock_quotes.get(symbol, {})
            for symbol in industry_symbols
        }

        pulse_cols = st.columns(4)
        spy = benchmark_market.get("SPY", {})
        qqq = benchmark_market.get("QQQ", {})
        spy_change = safe_float(
            spy.get("percent_change")
        )
        qqq_change = safe_float(
            qqq.get("percent_change")
        )

        pulse_cols[0].metric(
            "SPY",
            format_market_price(
                spy.get("close")
            ),
            (
                f"{spy_change:+.2f}%"
                if spy_change is not None
                else None
            ),
        )
        pulse_cols[1].metric(
            "QQQ",
            format_market_price(
                qqq.get("close")
            ),
            (
                f"{qqq_change:+.2f}%"
                if qqq_change is not None
                else None
            ),
        )

        industry_changes = [
            safe_float(
                industry_market.get(
                    symbol,
                    {},
                ).get("percent_change")
            )
            for symbol in industry_symbols
        ]
        industry_changes = [
            value
            for value in industry_changes
            if value is not None
        ]
        positive_count = sum(
            1
            for value in industry_changes
            if value > 0
        )
        median_change = (
            float(
                pd.Series(
                    industry_changes
                ).median()
            )
            if industry_changes
            else None
        )
        pulse_cols[2].metric(
            "Names positive",
            (
                f"{positive_count} / "
                f"{len(industry_changes)}"
                if industry_changes
                else "N/A"
            ),
        )
        pulse_cols[3].metric(
            "Industry median",
            (
                f"{median_change:+.2f}%"
                if median_change is not None
                else "N/A"
            ),
        )

        stock_retrieval_times = [
            quote.get("retrieved_at")
            for quote in stock_quotes.values()
            if quote.get("retrieved_at")
        ]
        stock_latest_retrieval = (
            max(stock_retrieval_times)
            if stock_retrieval_times
            else ""
        )
        render_refresh_indicator(
            "Stock snapshot refreshed",
            stock_latest_retrieval,
            "quotes may be delayed",
        )
        st.caption(
            "Stock quote snapshot retrieved: "
            + format_utc_timestamp(
                stock_latest_retrieval,
                fallback="Unavailable",
            )
            + ". Quotes may be delayed."
        )

        market_rows = []
        for company in market_companies:
            data = company_data[company]
            ticker = data.get("ticker", "")
            quote = industry_market.get(
                ticker,
                {},
            )
            price = safe_float(
                quote.get("close")
            )
            change = safe_float(
                quote.get("percent_change")
            )
            volume = safe_float(
                quote.get("volume")
            )
            open_price = safe_float(
                quote.get("open")
            )
            previous_close = safe_float(
                quote.get("previous_close")
            )
            market_rows.append({
                "Ticker": ticker,
                "Company": company.split(" (")[0],
                "Price": (
                    "$" + f"{price:,.2f}"
                    if price is not None
                    else "N/A"
                ),
                "Today": (
                    f"{change:+.2f}%"
                    if change is not None
                    else "N/A"
                ),
                "Volume": format_market_volume(
                    volume
                ),
                "Open": (
                    "$" + f"{open_price:,.2f}"
                    if open_price is not None
                    else "N/A"
                ),
                "Previous Close": (
                    "$"
                    + f"{previous_close:,.2f}"
                    if previous_close is not None
                    else "N/A"
                ),
                "_change": change,
            })

        board_df = pd.DataFrame(market_rows)
        if not board_df.empty:
            render_crisp_table(
                st,
                board_df.drop(
                    columns=["_change"]
                ),
            )
        else:
            st.info(
                "No quote rows are available for the selected industry."
            )

        if (
            public_finviz_data_enabled
            and industry_symbols
        ):
            section(
                "Screener",
                "Price, Volume & Market Activity",
            )
            try:
                finviz_market = (
                    normalize_finviz_screener(
                        get_finviz_screener_data(
                            symbols=industry_symbols
                        )
                    )
                )
            except Exception:
                finviz_market = pd.DataFrame()

            if not finviz_market.empty:
                screener_cols = st.columns(2)
                with screener_cols[0]:
                    min_relative_volume = (
                        st.number_input(
                            "Minimum relative volume",
                            min_value=0.0,
                            value=0.0,
                            step=0.1,
                            key=(
                                "finviz_min_relative_volume"
                            ),
                        )
                    )
                with screener_cols[1]:
                    min_abs_change = (
                        st.number_input(
                            "Minimum absolute daily move (%)",
                            min_value=0.0,
                            value=0.0,
                            step=0.5,
                            key="finviz_min_abs_change",
                        )
                    )

                covered = finviz_market[
                    finviz_market["Ticker"].isin(
                        industry_symbols
                    )
                ].copy()

                if (
                    "Relative Volume"
                    in covered.columns
                    and min_relative_volume > 0
                ):
                    values = covered[
                        "Relative Volume"
                    ].apply(finviz_numeric)
                    covered = covered[
                        values.fillna(-1)
                        >= min_relative_volume
                    ]

                if (
                    "Change" in covered.columns
                    and min_abs_change > 0
                ):
                    values = covered[
                        "Change"
                    ].apply(finviz_numeric)
                    covered = covered[
                        values.abs().fillna(-1)
                        >= min_abs_change
                    ]

                preferred = [
                    "Ticker",
                    "Company",
                    "Price",
                    "Change",
                    "Volume",
                    "Relative Volume",
                    "Market Cap",
                    "P/E",
                    "Perf Week",
                    "Perf Month",
                    "Earnings",
                ]
                visible = [
                    column
                    for column in preferred
                    if column in covered.columns
                ]
                if not covered.empty:
                    render_crisp_table(
                        st,
                        covered[visible],
                    )
                else:
                    st.caption(
                        "No companies match the current screener filters."
                    )
            else:
                st.caption(
                    "The market-data connection returned no usable screener rows."
                )

        notable_rows = sorted(
            [
                row
                for row in market_rows
                if (
                    row["_change"] is not None
                    and abs(row["_change"])
                    >= movement_threshold
                )
            ],
            key=lambda row: abs(
                row["_change"]
            ),
            reverse=True,
        )[:6]

        section(
            "Movement",
            (
                "Moves Beyond ±"
                + f"{movement_threshold:.1f}%"
            ),
        )

        if notable_rows:
            movement_cards = []
            for row in notable_rows:
                summary_company = (
                    sec_summary.get(
                        "companies",
                        {},
                    ).get(
                        row["Ticker"],
                        {},
                    )
                )
                latest_filing = (
                    summary_company.get(
                        "latest_material_filing",
                        {},
                    )
                    or summary_company.get(
                        "latest_filing",
                        {},
                    )
                    or {}
                )
                filing_label = (
                    (
                        f"{latest_filing.get('form', 'SEC filing')} · "
                        f"{latest_filing.get('filing_date', 'date unavailable')}"
                    )
                    if latest_filing
                    else "No recent filing loaded"
                )
                direction_class = (
                    "positive"
                    if row["_change"] >= 0
                    else "negative"
                )
                movement_cards.append(
                    f"""
                    <div class="el-move-card">
                        <div class="el-move-top">
                            <div class="el-move-ticker">{row['Ticker']}</div>
                            <div class="el-move-change {direction_class}">{row['_change']:+.2f}%</div>
                        </div>
                        <div class="el-move-name">{row['Company']}</div>
                        <div class="el-move-filing">
                            Recent SEC context: {filing_label}<br>
                            Market movement shown without attributing a cause.
                        </div>
                    </div>
                    """
                )
            st.markdown(
                '<div class="el-move-grid">'
                + "".join(movement_cards)
                + "</div>",
                unsafe_allow_html=True,
            )
        else:
            st.caption(
                f"No covered {market_industry} company currently exceeds "
                f"the selected ±{movement_threshold:.1f}% threshold."
            )

        st.caption(
            "Market movement is descriptive. A nearby SEC filing is shown as context only; "
            "EquityLens does not claim that the filing caused the price move."
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
