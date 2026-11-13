import pandas as pd
import streamlit as st

from macro_data import (
    get_bls_release_calendar,
    get_fed_monetary_updates,
    get_fomc_calendar,
)
from market_tables import render_crisp_table
from ui_components import section


def render_calendar():
    section(
        "Calendar",
        "Economic & Federal Reserve Calendar",
    )

    try:
        bls_calendar = get_bls_release_calendar()
    except Exception:
        bls_calendar = []
        st.caption(
            "The BLS release calendar is temporarily unavailable."
        )

    try:
        fomc_calendar = get_fomc_calendar()
    except Exception:
        fomc_calendar = []
        st.caption(
            "The Federal Reserve meeting calendar is temporarily unavailable."
        )

    calendar_rows = bls_calendar + fomc_calendar
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
        fed_updates = get_fed_monetary_updates()
    except Exception:
        fed_updates = []

    if fed_updates:
        render_crisp_table(
            st,
            pd.DataFrame(fed_updates),
            link_columns=("Source",),
            link_label="Federal Reserve",
        )
    else:
        st.link_button(
            "Open Federal Reserve monetary-policy updates",
            "https://www.federalreserve.gov/monetarypolicy.htm",
            use_container_width=True,
        )
