import pandas as pd
import streamlit as st

from financial_utils import (
    format_market_price,
    safe_float,
)
from macro_data import (
    get_bloomberg_market_news,
    market_provider_error,
    render_market_news_cards,
)
from market_data import (
    get_finviz_screener_data,
    get_live_market_data,
    normalize_finviz_screener,
)
from ui_components import (
    format_utc_timestamp,
    render_refresh_indicator,
    section,
)
from views.market_sections.overview import (
    render_nyse_market_monitor,
)


def render_overview_workspace(
    *,
    public_finviz_data_enabled,
    workspace_known_tickers,
    research_link,
):
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
