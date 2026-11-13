import pandas as pd
import streamlit as st

from financial_utils import safe_float
from market_data import finviz_numeric, get_major_etf_exposure
from ui_components import section


def render_peers_and_etfs(
    workspace_universe,
    selected_ticker,
    selected_industry_name,
):
    section("Peers", "Related Companies & Major ETF Exposure")

    peer_rows = workspace_universe[
        (
            workspace_universe["Industry"]
            == selected_industry_name
        )
        & (
            workspace_universe["Ticker"]
            .astype(str)
            .str.upper()
            != selected_ticker
        )
    ].copy()

    if "Market Cap" in peer_rows.columns:
        peer_rows["_market_cap_sort"] = peer_rows[
            "Market Cap"
        ].apply(finviz_numeric)
        peer_rows = peer_rows.sort_values(
            "_market_cap_sort",
            ascending=False,
        )

    peer_columns = [
        column
        for column in [
            "Ticker",
            "Company",
            "Sector",
            "Industry",
            "Market Cap",
            "P/E",
            "Price",
            "Change",
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
        st.caption(
            "No additional companies share this exact industry label in the current universe."
        )

    st.markdown("**Major ETF exposure**")
    st.caption(
        "This scanner checks the published top-holdings lists for a curated set of major "
        "broad-market, growth, sector, semiconductor, communication-services, and software ETFs. "
        "It is useful context, not an exhaustive ETF-ownership database."
    )

    state_key = f"workspace_etf_scan_{selected_ticker}"
    snapshot_key = (
        f"company_etf_exposure::{selected_ticker}"
    )
    if st.button(
        "Scan major ETFs",
        key=f"workspace_etf_button_{selected_ticker}",
    ):
        st.session_state[state_key] = True
        st.session_state.pop(snapshot_key, None)

    if st.session_state.get(state_key, False):
        etf_matches = st.session_state.get(
            snapshot_key
        )
        if not isinstance(etf_matches, list):
            try:
                etf_matches = get_major_etf_exposure(
                    selected_ticker
                )
            except Exception:
                etf_matches = []
            st.session_state[snapshot_key] = (
                etf_matches
            )

        if etf_matches:
            etf_df = pd.DataFrame(etf_matches)
            if "Holding" in etf_df.columns:
                etf_df["Holding"] = etf_df[
                    "Holding"
                ].apply(
                    lambda value: (
                        f"{safe_float(value) * 100:.2f}%"
                        if (
                            safe_float(value) is not None
                            and abs(safe_float(value)) <= 1
                        )
                        else (
                            f"{safe_float(value):.2f}%"
                            if safe_float(value) is not None
                            else "N/A"
                        )
                    )
                )
            st.dataframe(
                etf_df,
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info(
                "No match was found in the published top-holdings sample for the ETFs scanned. "
                "This does not mean no ETF owns the stock; free fund feeds do not expose every holding for every ETF."
            )

    st.caption(
        "Peer groups use the EquityLens industry classification. "
        "ETF holdings are supplemental market data and may be delayed."
    )
