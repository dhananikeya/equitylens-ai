import pandas as pd
import streamlit as st

from ui_components import section


def render_sec_filings(
    *,
    selected_ticker,
    selected_filings,
    selected_sec,
    selected_sec_error,
    latest_annual,
    latest_quarter,
    latest_current,
    primary_registration,
):
    section(
        "SEC Filings",
        "Current & Periodic Filing History",
    )
    st.caption(
        "Use this section for ongoing public-company disclosures. "
        "IPO-era registration statements live in the separate IPO / Registration section."
    )

    metric_cols = st.columns(4)
    metric_cols[0].metric(
        "Annual",
        latest_annual.get("form", "N/A"),
        latest_annual.get("filing_date") or None,
    )
    metric_cols[1].metric(
        "Quarterly",
        latest_quarter.get("form", "N/A"),
        latest_quarter.get("filing_date") or None,
    )
    metric_cols[2].metric(
        "Current Report",
        latest_current.get("form", "N/A"),
        latest_current.get("filing_date") or None,
    )
    metric_cols[3].metric(
        "Registration",
        primary_registration.get(
            "form",
            "Not found",
        ),
        primary_registration.get(
            "filing_date"
        ) or None,
        help=(
            "Registration filings are analyzed separately because "
            "they describe IPO-era or offering-era context."
        ),
    )

    if selected_sec_error:
        st.warning(selected_sec_error)

    if selected_filings:
        filing_table = pd.DataFrame([
            {
                "Filed": filing.get(
                    "filing_date",
                    "",
                ),
                "Form": filing.get("form", ""),
                "Report Period": filing.get(
                    "report_date",
                    "",
                ),
                "Description": (
                    filing.get("description", "")
                    or filing.get(
                        "primary_document",
                        "",
                    )
                ),
                "SEC Filing": filing.get(
                    "url",
                    "",
                ),
            }
            for filing in selected_filings[:25]
        ])
        st.dataframe(
            filing_table,
            use_container_width=True,
            hide_index=True,
            column_config={
                "SEC Filing": (
                    st.column_config.LinkColumn(
                        "SEC Filing",
                        display_text="Open filing",
                    )
                )
            },
        )
        st.caption(
            "Showing the 25 most recent filings returned by the current company feed. "
            "Use the complete SEC history link for older documents."
        )
    else:
        st.info(
            "Recent SEC filing metadata is not available for this company right now."
        )

    if selected_sec.get("sec_company_url"):
        st.link_button(
            "Open complete SEC company history",
            selected_sec.get("sec_company_url"),
            key=(
                f"workspace_sec_history_"
                f"{selected_ticker}"
            ),
        )
