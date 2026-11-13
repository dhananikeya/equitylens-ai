from datetime import datetime, timezone

import pandas as pd
import streamlit as st

from financial_utils import (
    format_market_price,
    format_market_volume,
    safe_float,
)
from market_data import (
    finviz_numeric,
    get_finviz_screener_data,
    get_live_market_data,
    normalize_finviz_screener,
)
from market_tables import render_crisp_table
from ui_components import (
    format_utc_timestamp,
    render_refresh_indicator,
    section,
)


def render_stocks_workspace(
    *,
    industries,
    company_data,
    sec_summary,
    public_finviz_data_enabled,
    research_link,
):
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
                "Research": (
                    research_link(
                        ticker
                    )
                    if ticker
                    else ""
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
                link_columns=(
                    "Research",
                ),
                link_label="Open research",
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
                screener_retrieved_at = (
                    datetime.now(
                        timezone.utc
                    ).isoformat()
                )
                screener_cols = st.columns(3)
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
                with screener_cols[2]:
                    screener_sort = st.selectbox(
                        "Sort by",
                        [
                            "Absolute daily move",
                            "Relative volume",
                            "Market cap",
                        ],
                        key="market_screener_sort",
                    )
    
                covered = finviz_market[
                    finviz_market["Ticker"].isin(
                        industry_symbols
                    )
                ].copy()
                covered[
                    "Research"
                ] = covered[
                    "Ticker"
                ].astype(str).map(
                    lambda ticker: (
                        research_link(
                            ticker
                        )
                    )
                )
    
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

                if (
                    screener_sort
                    == "Absolute daily move"
                    and "Change"
                    in covered.columns
                ):
                    covered["_sort_value"] = (
                        covered["Change"]
                        .apply(finviz_numeric)
                        .abs()
                    )
                elif (
                    screener_sort
                    == "Relative volume"
                    and "Relative Volume"
                    in covered.columns
                ):
                    covered["_sort_value"] = (
                        covered[
                            "Relative Volume"
                        ].apply(
                            finviz_numeric
                        )
                    )
                elif (
                    "Market Cap"
                    in covered.columns
                ):
                    covered["_sort_value"] = (
                        covered[
                            "Market Cap"
                        ].apply(
                            finviz_numeric
                        )
                    )

                if (
                    "_sort_value"
                    in covered.columns
                ):
                    covered = (
                        covered.sort_values(
                            "_sort_value",
                            ascending=False,
                            na_position="last",
                        )
                        .drop(
                            columns=[
                                "_sort_value"
                            ]
                        )
                    )
    
                preferred = [
                    "Ticker",
                    "Company",
                    "Exchange",
                    "Price",
                    "Change",
                    "Volume",
                    "Relative Volume",
                    "Market Cap",
                    "P/E",
                    "Perf Week",
                    "Perf Month",
                    "Earnings",
                    "Research",
                ]
                visible = [
                    column
                    for column in preferred
                    if column in covered.columns
                ]
                if not covered.empty:
                    st.caption(
                        f"{len(covered):,} companies match the current screener filters · "
                        "snapshot retrieved "
                        + format_utc_timestamp(
                            screener_retrieved_at,
                            fallback="Unavailable",
                        )
                    )
                    render_crisp_table(
                        st,
                        covered[visible],
                        link_columns=(
                            "Research",
                        ),
                        link_label=(
                            "Open research"
                        ),
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
                        <a class="el-move-research" href="{research_link(row['Ticker'])}">
                            Open company research ↗
                        </a>
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
    