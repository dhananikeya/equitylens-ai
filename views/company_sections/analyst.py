import pandas as pd
import streamlit as st

from financial_utils import safe_float
from market_data import get_company_analyst_data
from sources import source_label
from ui_components import section


def render_analyst_research(selected_ticker, selected_price):
    section(
        "Analyst Research",
        "Consensus, Price Targets & Rating Changes",
    )
    st.caption(
        "These are third-party analyst opinions and market-data aggregates. "
        "They are not EquityLens ratings, recommendations, or price forecasts."
    )

    snapshot_key = f"company_analyst::{selected_ticker}"
    analyst_data = st.session_state.get(snapshot_key)
    if not isinstance(analyst_data, dict):
        try:
            analyst_data = get_company_analyst_data(
                selected_ticker
            )
        except Exception:
            analyst_data = {
                "targets": {},
                "recommendations": pd.DataFrame(),
                "upgrades": pd.DataFrame(),
            }
        st.session_state[snapshot_key] = analyst_data

    targets = analyst_data.get("targets", {}) or {}

    def target_value(*keys):
        for key in keys:
            if (
                key in targets
                and targets.get(key) is not None
            ):
                return safe_float(targets.get(key))
        return None

    current_target_price = target_value(
        "current",
        "currentPrice",
        "Current",
    )
    mean_target = target_value(
        "mean",
        "meanPriceTarget",
        "targetMeanPrice",
    )
    median_target = target_value(
        "median",
        "medianPriceTarget",
        "targetMedianPrice",
    )
    low_target = target_value(
        "low",
        "lowPriceTarget",
        "targetLowPrice",
    )
    high_target = target_value(
        "high",
        "highPriceTarget",
        "targetHighPrice",
    )

    metric_cols = st.columns(5)
    metric_cols[0].metric(
        "Current Price",
        (
            "$" + f"{(current_target_price or selected_price):,.2f}"
            if (current_target_price or selected_price) is not None
            else "N/A"
        ),
    )
    metric_cols[1].metric(
        "Mean Target",
        "$" + f"{mean_target:,.2f}"
        if mean_target is not None
        else "N/A",
    )
    metric_cols[2].metric(
        "Median Target",
        "$" + f"{median_target:,.2f}"
        if median_target is not None
        else "N/A",
    )
    metric_cols[3].metric(
        "Low Target",
        "$" + f"{low_target:,.2f}"
        if low_target is not None
        else "N/A",
    )
    metric_cols[4].metric(
        "High Target",
        "$" + f"{high_target:,.2f}"
        if high_target is not None
        else "N/A",
    )

    recommendations = analyst_data.get(
        "recommendations",
        pd.DataFrame(),
    )
    st.markdown("**Recommendation summary**")
    if (
        isinstance(recommendations, pd.DataFrame)
        and not recommendations.empty
    ):
        st.dataframe(
            recommendations,
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.caption(
            "Consensus recommendation data is unavailable from the supplemental feed."
        )

    upgrades = analyst_data.get(
        "upgrades",
        pd.DataFrame(),
    )
    st.markdown("**Recent upgrades / downgrades**")
    if (
        isinstance(upgrades, pd.DataFrame)
        and not upgrades.empty
    ):
        st.dataframe(
            upgrades.tail(25).iloc[::-1],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.caption(
            "Recent analyst rating-change data is unavailable from the supplemental feed."
        )

    st.caption(
        "Supplemental analyst data: "
        + source_label("Yahoo")
        + ". EquityLens does not convert third-party opinions into its own buy, sell, or hold rating."
    )
