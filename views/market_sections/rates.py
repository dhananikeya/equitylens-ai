import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from macro_data import (
    get_rates_bundle,
    render_rates_ticker,
)
from market_tables import render_crisp_table
from ui_components import loading_panel, section


def render_rates():
    section(
        "Rates",
        "Treasury, SOFR & Swap Monitor",
    )
    with loading_panel(
        "Loading rates and liquidity data",
        "Retrieving U.S. Treasury, New York Fed SOFR, and swap-curve context.",
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

    treasury_curve = rates_bundle["treasury"]
    sofr_reference = rates_bundle["sofr"]
    swap_rates = rates_bundle["swap"]
    rate_errors = set(rates_bundle["errors"])

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
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
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
            config={
                "displayModeBar": False
            },
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
        swap_df = pd.DataFrame(swap_rates)
        swap_df["Swap Rate"] = (
            swap_df["Swap Rate"].map(
                lambda value: f"{value:.3f}%"
            )
        )
        st.markdown("**USD SOFR OIS Curve**")
        visible_columns = [
            column
            for column in [
                "Tenor",
                "Swap Rate",
                "Curve Date",
                "Source",
                "Method",
            ]
            if column in swap_df.columns
        ]
        render_crisp_table(
            st,
            swap_df[visible_columns],
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
