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
        section(
            "Rates",
            "Treasury, SOFR & Swap Monitor",
        )
        with loading_panel(
            "Loading rates and liquidity data",
            "Retrieving U.S. Treasury, New York Fed SOFR, and swap-curve context."
        ):
            rates_bundle = get_rates_bundle(
                str(
                    st.secrets.get(
                        "SWAP_RATES_JSON_URL",
                        "",
                    )
                ).strip(),
                "rates-v3",
            )

        treasury_curve = rates_bundle[
            "treasury"
        ]
        sofr_reference = rates_bundle["sofr"]
        swap_rates = rates_bundle["swap"]
        rate_errors = set(
            rates_bundle["errors"]
        )

        if "treasury" in rate_errors:
            st.warning(
                "Treasury yield data could not be refreshed from the official feed "
                "or the FRED fallback. Other rate data remains available."
            )
        if "sofr" in rate_errors:
            st.info(
                "New York Fed SOFR reference rates are temporarily unavailable. "
                "Treasury and any available swap context remain separate."
            )

        render_rates_ticker(
            treasury_curve,
            sofr_reference,
        )

        treasury_rates = (
            treasury_curve.get("rates", {})
            if treasury_curve
            else {}
        )
        curve_rows = [
            {
                "Tenor": tenor,
                "Yield (%)": rate,
            }
            for tenor, rate in treasury_rates.items()
            if rate is not None
        ]
        if curve_rows:
            curve_df = pd.DataFrame(curve_rows)
            curve_fig = go.Figure(
                go.Scatter(
                    x=curve_df["Tenor"],
                    y=curve_df["Yield (%)"],
                    mode="lines+markers",
                    name="Treasury",
                    line={
                        "color": "#16C7B2",
                        "width": 2,
                    },
                    marker={"size": 7},
                )
            )
            curve_fig.update_layout(
                height=330,
                margin={
                    "l": 8,
                    "r": 8,
                    "t": 24,
                    "b": 8,
                },
                paper_bgcolor=(
                    "rgba(0,0,0,0)"
                ),
                plot_bgcolor=(
                    "rgba(0,0,0,0)"
                ),
                font={
                    "color": "#8F9CA6",
                    "family": "IBM Plex Sans",
                },
                showlegend=False,
                xaxis={
                    "showgrid": False,
                    "title": "Maturity",
                },
                yaxis={
                    "gridcolor": (
                        "rgba(143,156,166,.12)"
                    ),
                    "title": "Yield (%)",
                    "ticksuffix": "%",
                },
            )
            st.plotly_chart(
                curve_fig,
                use_container_width=True,
                config={"displayModeBar": False},
            )
            st.caption(
                "Daily Treasury par yield curve · U.S. Department of the Treasury"
                + (
                    f" · as of {treasury_curve.get('date')}"
                    if treasury_curve.get("date")
                    else ""
                )
            )

        if swap_rates:
            swap_df = pd.DataFrame(
                swap_rates
            )
            swap_df["Swap Rate"] = (
                swap_df["Swap Rate"].map(
                    lambda value: (
                        f"{value:.3f}%"
                    )
                )
            )
            st.markdown(
                "**USD SOFR OIS Curve**"
            )
            visible_swap_columns = [
                column
                for column in [
                    "Tenor",
                    "Swap Rate",
                    "Curve Date",
                    "Source",
                    "Method",
                ]
                if column
                in swap_df.columns
            ]
            render_crisp_table(
                st,
                swap_df[
                    visible_swap_columns
                ],
            )
            st.caption(
                "Public curve context from CheckMySwap / DTCC-derived transaction data. "
                "These are indicative dated estimates, not executable dealer quotes."
            )
            st.link_button(
                "Open methodology & curve archive",
                "https://checkmyswap.com/rates?ccy=USD",
                use_container_width=True,
            )
        else:
            st.info(
                "USD SOFR OIS curve data is temporarily unavailable. "
                "Official Treasury and New York Fed reference rates remain separate."
            )

    if market_view == "Macro":
        section(
            "Macro",
            "Material U.S. Economic Reports",
        )
        try:
            bls_snapshot = (
                get_bls_macro_snapshot()
            )
        except Exception:
            bls_snapshot = {}
            st.warning(
                "BLS macro data is temporarily unavailable. "
                "No other Market Monitor source is affected."
            )

        macro_order = [
            "CPI",
            "Core CPI",
            "PPI",
            "Unemployment",
            "Payrolls",
            "Hourly Earnings",
            "ECI",
        ]
        available_macro = [
            key
            for key in macro_order
            if key in bls_snapshot
        ]

        for row_start in range(
            0,
            len(available_macro),
            4,
        ):
            row_keys = available_macro[
                row_start:row_start + 4
            ]
            cols = st.columns(
                len(row_keys)
            )
            for col, key in zip(
                cols,
                row_keys,
            ):
                item = bls_snapshot[key]
                col.metric(
                    item.get(
                        "label",
                        key,
                    ),
                    format_bls_display(
                        item
                    ),
                )
                col.caption(
                    f"{item.get('period', '')} · BLS"
                )

        if available_macro:
            source_rows = [
                {
                    "Indicator": (
                        bls_snapshot[key].get(
                            "label",
                            key,
                        )
                    ),
                    "BLS Series": (
                        bls_snapshot[key].get(
                            "series_id",
                            "",
                        )
                    ),
                    "Latest period": (
                        bls_snapshot[key].get(
                            "period",
                            "",
                        )
                    ),
                    "Primary report": (
                        bls_snapshot[key].get(
                            "source",
                            "",
                        )
                    ),
                }
                for key in available_macro
            ]
            with st.expander(
                "Sources & how to read these indicators"
            ):
                st.dataframe(
                    pd.DataFrame(
                        source_rows
                    ),
                    use_container_width=True,
                    hide_index=True,
                )
                st.markdown(
                    "**How to read the panel**\n\n"
                    "- CPI / Core CPI: consumer inflation context.\n"
                    "- PPI: producer selling-price context.\n"
                    "- Payrolls / unemployment: labor-market conditions.\n"
                    "- Hourly earnings / ECI: wage and compensation pressure.\n\n"
                    "Monthly, quarterly, and year-over-year measures answer different questions. "
                    "Always check the period label before comparing releases."
                )
                st.link_button(
                    "Open BLS Public Data API",
                    "https://www.bls.gov/developers/",
                    use_container_width=True,
                )

    if market_view == "Calendar":
        section(
            "Calendar",
            "Economic & Federal Reserve Calendar",
        )

        try:
            bls_calendar = (
                get_bls_release_calendar()
            )
        except Exception:
            bls_calendar = []
            st.caption(
                "The BLS release calendar is temporarily unavailable."
            )

        try:
            fomc_calendar = (
                get_fomc_calendar()
            )
        except Exception:
            fomc_calendar = []
            st.caption(
                "The Federal Reserve meeting calendar is temporarily unavailable."
            )

        calendar_rows = (
            bls_calendar
            + fomc_calendar
        )
        if calendar_rows:
            calendar_df = pd.DataFrame(
                calendar_rows
            ).sort_values(
                ["Date", "Agency"],
                ascending=True,
            ).head(20)
            render_crisp_table(
                st,
                calendar_df,
                link_columns=("Source",),
                link_label="Primary source",
            )
            st.caption(
                "Dates are read from official BLS and Federal Reserve calendars. "
                "Release schedules can change, so the linked primary source remains authoritative."
            )
        else:
            st.info(
                "No calendar rows are available from the official sources right now."
            )

        st.markdown(
            "**Latest Federal Reserve monetary-policy updates**"
        )
        try:
            fed_updates = (
                get_fed_monetary_updates()
            )
        except Exception:
            fed_updates = []

        if fed_updates:
            render_crisp_table(
                st,
                pd.DataFrame(
                    fed_updates
                ),
                link_columns=("Source",),
                link_label="Federal Reserve",
            )
        else:
            st.link_button(
                "Open Federal Reserve monetary-policy updates",
                "https://www.federalreserve.gov/monetarypolicy.htm",
                use_container_width=True,
            )

    st.markdown(
        '<div class="el-market-source">'
        + source_copy[market_view]
        + " · Company-specific fundamentals and filings remain in Company Research."
        + "</div>",
        unsafe_allow_html=True,
    )
