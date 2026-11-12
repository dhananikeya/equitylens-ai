import pandas as pd
import streamlit as st

from macro_data import (
    format_bls_display,
    get_bls_macro_snapshot,
)
from ui_components import section


def render_macro():
    section(
        "Macro",
        "Material U.S. Economic Reports",
    )
    try:
        snapshot = get_bls_macro_snapshot()
    except Exception:
        snapshot = {}
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
    available = [
        key
        for key in macro_order
        if key in snapshot
    ]

    for row_start in range(
        0,
        len(available),
        4,
    ):
        row_keys = available[
            row_start:row_start + 4
        ]
        cols = st.columns(len(row_keys))
        for col, key in zip(
            cols,
            row_keys,
        ):
            item = snapshot[key]
            col.metric(
                item.get(
                    "label",
                    key,
                ),
                format_bls_display(item),
            )
            col.caption(
                f"{item.get('period', '')} · BLS"
            )

    if available:
        source_rows = [
            {
                "Indicator": snapshot[key].get(
                    "label",
                    key,
                ),
                "BLS Series": snapshot[key].get(
                    "series_id",
                    "",
                ),
                "Latest period": snapshot[key].get(
                    "period",
                    "",
                ),
                "Primary report": snapshot[key].get(
                    "source",
                    "",
                ),
            }
            for key in available
        ]
        with st.expander(
            "Sources & how to read these indicators"
        ):
            st.dataframe(
                pd.DataFrame(source_rows),
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
