import json

import pandas as pd
import streamlit as st

from ui_components import section


def render_filings(
    company_universe,
    load_sec_filings,
    get_sec_company_research,
):
    section("SEC Monitor", "Filing Tracker")

    try:
        sec_filings = load_sec_filings()
    except (FileNotFoundError, json.JSONDecodeError):
        sec_filings = {}

    st.write(
        "This tracker combines the recent SEC filings collected for every company covered by EquityLens. "
        "It records the issuer, ticker, form, SEC filing date, SEC acceptance timestamp when available, "
        "the period the filing covers, when EquityLens first detected it, and a direct link to the original filing."
    )

    st.caption(
        "The SEC does not publish an exact future posting time before a filing is submitted. "
        "EquityLens can track actual filings immediately after they appear and can separately add announced "
        "earnings dates or estimated filing windows later."
    )

    tracker_rows = []
    for tracked_company, feed in sec_filings.items():
        entity_name = feed.get(
            "entity_name",
            tracked_company.split(" (")[0],
        )
        tracked_ticker = feed.get("ticker", "")
        for filing in feed.get("filings", []):
            tracker_rows.append({
                "Company": entity_name,
                "Ticker": tracked_ticker,
                "Form": filing.get("form", ""),
                "SEC Filed Date": filing.get("filing_date", ""),
                "SEC Accepted": filing.get("acceptance_datetime", ""),
                "Report Period": filing.get("report_date", ""),
                "Description": (
                    filing.get("description", "")
                    or filing.get("primary_document", "")
                ),
                "Items": filing.get("items", ""),
                "First Seen by EquityLens (UTC)": filing.get(
                    "first_seen_utc",
                    "",
                ),
                "Accession Number": filing.get(
                    "accession_number",
                    "",
                ),
                "SEC Filing": filing.get("url", ""),
            })

    tracker_df = pd.DataFrame(tracker_rows)

    if tracker_df.empty:
        st.info(
            "The filing tracker is waiting for the SEC monitor to populate data."
        )
    else:
        accepted_dt = pd.to_datetime(
            tracker_df["SEC Accepted"],
            errors="coerce",
            utc=True,
        )
        first_seen_dt = pd.to_datetime(
            tracker_df["First Seen by EquityLens (UTC)"],
            errors="coerce",
            utc=True,
        )

        tracker_df["SEC Accepted (ET)"] = (
            accepted_dt.dt.tz_convert("America/New_York")
            .dt.strftime("%Y-%m-%d %I:%M:%S %p %Z")
        )
        tracker_df["First Seen by EquityLens (ET)"] = (
            first_seen_dt.dt.tz_convert("America/New_York")
            .dt.strftime("%Y-%m-%d %I:%M:%S %p %Z")
        )

        tracker_df = tracker_df.drop(
            columns=[
                "SEC Accepted",
                "First Seen by EquityLens (UTC)",
            ]
        )

        tracker_df = tracker_df.sort_values(
            by=["SEC Filed Date", "SEC Accepted (ET)"],
            ascending=False,
            na_position="last",
        )

        filter_cols = st.columns(2)
        with filter_cols[0]:
            tracker_company = st.selectbox(
                "Company",
                ["All companies"]
                + sorted(
                    tracker_df["Company"]
                    .dropna()
                    .unique()
                    .tolist()
                ),
                key="sec_tracker_company",
            )
        with filter_cols[1]:
            form_options = sorted(
                [
                    form
                    for form in tracker_df["Form"]
                    .dropna()
                    .unique()
                    .tolist()
                    if form
                ]
            )
            tracker_forms = st.multiselect(
                "Filing type",
                form_options,
                default=[],
                key="sec_tracker_forms",
            )

        filtered_tracker = tracker_df.copy()
        if tracker_company != "All companies":
            filtered_tracker = filtered_tracker[
                filtered_tracker["Company"] == tracker_company
            ]
        if tracker_forms:
            filtered_tracker = filtered_tracker[
                filtered_tracker["Form"].isin(tracker_forms)
            ]

        st.dataframe(
            filtered_tracker,
            use_container_width=True,
            hide_index=True,
            column_config={
                "SEC Filing": st.column_config.LinkColumn(
                    "SEC Filing",
                    display_text="Open filing",
                )
            },
        )

        st.download_button(
            "Download filing tracker as CSV",
            data=filtered_tracker.to_csv(index=False).encode("utf-8"),
            file_name="equitylens_sec_filing_tracker.csv",
            mime="text/csv",
            use_container_width=True,
        )

        st.caption(
            f"Showing {len(filtered_tracker):,} filing records from the current monitored set. "
            "The monitor checks for new SEC submissions every 15 minutes."
        )

    section(
        "Registration Filings",
        "S-1 / F-1 / S-11 History",
    )

    registration_company = st.selectbox(
        "Company registration history",
        company_universe["Coverage Key"].tolist(),
        format_func=lambda key: (
            key.split(" (")[-1].rstrip(")")
            + " · "
            + key.rsplit(" (", 1)[0]
        ),
        key="sec_registration_company",
    )

    registration_row = company_universe[
        company_universe["Coverage Key"] == registration_company
    ].iloc[0]
    registration_ticker = str(
        registration_row.get("Ticker", "")
    )

    try:
        registration_feed = get_sec_company_research(
            registration_ticker
        )
        registration_error = None
    except Exception:
        registration_feed = {}
        registration_error = (
            "SEC EDGAR is temporarily unavailable for this company."
        )

    if registration_error:
        st.warning(registration_error)
        return

    registration_rows = registration_feed.get(
        "registration_filings",
        [],
    )

    if registration_rows:
        registration_table = pd.DataFrame(
            [
                {
                    "Filed": filing.get(
                        "filing_date",
                        "",
                    ),
                    "Form": filing.get("form", ""),
                    "Description": (
                        filing.get("description", "")
                        or filing.get("primary_document", "")
                    ),
                    "SEC Filing": filing.get("url", ""),
                }
                for filing in registration_rows
            ]
        )

        st.dataframe(
            registration_table,
            use_container_width=True,
            hide_index=True,
            column_config={
                "SEC Filing": st.column_config.LinkColumn(
                    "SEC Filing",
                    display_text="Open filing",
                )
            },
        )
    else:
        st.caption(
            "No S-1, S-1/A, F-1, F-1/A, S-11, or S-11/A was found in "
            "the SEC history available for this issuer."
        )

    registration_sec_url = registration_feed.get(
        "sec_company_url",
        "",
    )
    if registration_sec_url:
        st.link_button(
            "Open complete SEC filing history",
            registration_sec_url,
            key="registration_sec_history",
            use_container_width=True,
        )
