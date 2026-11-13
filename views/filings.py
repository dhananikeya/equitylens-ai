import json

import pandas as pd
import streamlit as st

from ui_components import (
    render_breadcrumbs,
    render_refresh_indicator,
    section,
)


FINANCIAL_FORMS = {
    "10-K", "10-K/A", "10-Q", "10-Q/A",
    "20-F", "20-F/A", "40-F", "40-F/A",
}
CURRENT_FORMS = {"8-K", "8-K/A", "6-K", "6-K/A"}
REGISTRATION_FORMS = {
    "S-1", "S-1/A", "F-1", "F-1/A", "S-11", "S-11/A",
}
INSIDER_FORMS = {
    "3", "3/A", "4", "4/A",
    "5", "5/A", "144", "144/A",
}
BENEFICIAL_OWNERSHIP_FORMS = {
    "SC 13D", "SC 13D/A",
    "SC 13G", "SC 13G/A",
    "SCHEDULE 13D", "SCHEDULE 13D/A",
    "SCHEDULE 13G", "SCHEDULE 13G/A",
}
PROXY_FORMS = {
    "DEF 14A",
    "DEFA14A",
    "PRE 14A",
    "DEFM14A",
}
OWNERSHIP_FORMS = (
    INSIDER_FORMS
    | BENEFICIAL_OWNERSHIP_FORMS
)
MATERIAL_FORMS = (
    FINANCIAL_FORMS
    | CURRENT_FORMS
    | REGISTRATION_FORMS
)

FORM_CATEGORIES = {
    "Material reports": MATERIAL_FORMS,
    "Financial reports": FINANCIAL_FORMS,
    "Current events": CURRENT_FORMS,
    "Registration": REGISTRATION_FORMS,
    "Ownership / insiders": OWNERSHIP_FORMS,
    "Proxy / governance": PROXY_FORMS,
    "All filings": None,
}


def render_filings(
    company_universe,
    load_sec_filings,
    get_sec_company_research,
    sec_summary=None,
    research_link=None,
):
    render_breadcrumbs(
        "Home",
        "Filings",
        "Filing Tracker",
    )
    section("SEC Monitor", "Filing Tracker")
    render_refresh_indicator(
        "SEC archive refreshed",
        (sec_summary or {}).get("generated_at_utc"),
        "automated filing monitor",
    )

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
                "Research": (
                    research_link(
                        tracked_ticker
                    )
                    if (
                        research_link
                        and tracked_ticker
                    )
                    else ""
                ),
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

        detection_seconds = (
            first_seen_dt
            - accepted_dt
        ).dt.total_seconds()

        def format_detection_lag(value):
            if pd.isna(value) or value < 0:
                return "N/A"
            seconds = int(value)
            if seconds < 60:
                return f"{seconds}s"
            minutes, remaining = divmod(
                seconds,
                60,
            )
            if minutes < 60:
                return (
                    f"{minutes}m {remaining}s"
                )
            hours, minutes = divmod(
                minutes,
                60,
            )
            return f"{hours}h {minutes}m"

        tracker_df[
            "Detection Lag"
        ] = detection_seconds.map(
            format_detection_lag
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

        filed_dt = pd.to_datetime(
            tracker_df["SEC Filed Date"],
            errors="coerce",
        )
        tracker_df["_FiledDate"] = filed_dt

        valid_dates = filed_dt.dropna()
        if not valid_dates.empty:
            latest_date = valid_dates.max().date()
            earliest_date = valid_dates.min().date()
            default_start = max(
                earliest_date,
                (
                    valid_dates.max()
                    - pd.Timedelta(days=90)
                ).date(),
            )
        else:
            latest_date = pd.Timestamp.today().date()
            earliest_date = latest_date
            default_start = latest_date

        seven_day_cutoff = pd.Timestamp(
            latest_date
        ) - pd.Timedelta(days=6)
        recent_material_mask = (
            tracker_df["Form"].isin(
                MATERIAL_FORMS
            )
            & tracker_df[
                "_FiledDate"
            ].ge(
                seven_day_cutoff
            )
        )
        filing_pulse = st.columns(4)
        filing_pulse[0].metric(
            "Indexed filings",
            f"{len(tracker_df):,}",
        )
        filing_pulse[1].metric(
            "Issuers",
            f"{tracker_df['Ticker'].nunique():,}",
        )
        filing_pulse[2].metric(
            "Material · last 7 days",
            f"{int(recent_material_mask.sum()):,}",
        )
        filing_pulse[3].metric(
            "Newest filing",
            str(latest_date),
        )

        primary_filters = st.columns([1.6, 1, .75])
        with primary_filters[0]:
            tracker_search = st.text_input(
                "Search company or ticker",
                placeholder="e.g. Amazon or AMZN",
                key="sec_tracker_search",
            ).strip()
        with primary_filters[1]:
            tracker_category = st.selectbox(
                "Filing category",
                list(FORM_CATEGORIES),
                index=0,
                key="sec_tracker_category",
                help=(
                    "Material reports emphasizes periodic financial reports, current reports, "
                    "and registration statements. All other SEC forms remain available."
                ),
            )
        with primary_filters[2]:
            display_limit = st.selectbox(
                "Rows shown",
                [100, 250, 500],
                index=0,
                key="sec_tracker_display_limit",
            )

        date_cols = st.columns(2)
        with date_cols[0]:
            tracker_start_date = st.date_input(
                "Filed on or after",
                value=default_start,
                min_value=earliest_date,
                max_value=latest_date,
                key="sec_tracker_start_date",
            )
        with date_cols[1]:
            tracker_end_date = st.date_input(
                "Filed on or before",
                value=latest_date,
                min_value=earliest_date,
                max_value=latest_date,
                key="sec_tracker_end_date",
            )

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
        company_options = [
            "All companies"
        ] + sorted(
            tracker_df["Company"]
            .dropna()
            .unique()
            .tolist()
        )

        with st.expander("Advanced filing filters"):
            tracker_company = st.selectbox(
                "Exact company",
                company_options,
                key="sec_tracker_company",
            )
            tracker_forms = st.multiselect(
                "Exact SEC forms",
                form_options,
                default=[],
                key="sec_tracker_forms",
                help=(
                    "Exact-form selections are applied in addition to the filing category above."
                ),
            )

        filtered_tracker = tracker_df.copy()

        category_forms = FORM_CATEGORIES.get(
            tracker_category
        )
        if category_forms is not None:
            filtered_tracker = filtered_tracker[
                filtered_tracker["Form"].isin(
                    category_forms
                )
            ]

        if tracker_search:
            search_lower = tracker_search.lower()
            search_mask = (
                filtered_tracker["Company"]
                .fillna("")
                .astype(str)
                .str.lower()
                .str.contains(
                    search_lower,
                    regex=False,
                )
                |
                filtered_tracker["Ticker"]
                .fillna("")
                .astype(str)
                .str.lower()
                .str.contains(
                    search_lower,
                    regex=False,
                )
            )
            filtered_tracker = (
                filtered_tracker[
                    search_mask
                ]
            )

        if tracker_company != "All companies":
            filtered_tracker = filtered_tracker[
                filtered_tracker["Company"]
                == tracker_company
            ]

        if tracker_forms:
            filtered_tracker = filtered_tracker[
                filtered_tracker["Form"].isin(
                    tracker_forms
                )
            ]

        if tracker_start_date > tracker_end_date:
            st.warning(
                "The start date is after the end date. Adjust the filing date range."
            )
            filtered_tracker = filtered_tracker.iloc[0:0]
        else:
            filtered_tracker = filtered_tracker[
                filtered_tracker["_FiledDate"].between(
                    pd.Timestamp(
                        tracker_start_date
                    ),
                    pd.Timestamp(
                        tracker_end_date
                    )
                    + pd.Timedelta(
                        days=1
                    )
                    - pd.Timedelta(
                        microseconds=1
                    ),
                    inclusive="both",
                )
            ]

        filtered_tracker = (
            filtered_tracker.sort_values(
                by=[
                    "SEC Filed Date",
                    "SEC Accepted (ET)",
                ],
                ascending=False,
                na_position="last",
            )
        )

        display_columns = [
            "Company",
            "Ticker",
            "Form",
            "SEC Filed Date",
            "SEC Accepted (ET)",
            "First Seen by EquityLens (ET)",
            "Detection Lag",
            "Report Period",
            "Description",
            "SEC Filing",
            "Research",
        ]
        visible_tracker = (
            filtered_tracker[
                display_columns
            ].head(display_limit)
        )

        if visible_tracker.empty:
            st.info(
                "No filings match the current filters."
            )
        else:
            st.dataframe(
                visible_tracker,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "SEC Filing": st.column_config.LinkColumn(
                        "SEC Filing",
                        display_text="Open filing",
                    ),
                    "Research": st.column_config.LinkColumn(
                        "Research",
                        display_text="Open research",
                    ),
                },
            )

        st.caption(
            f"Showing {min(len(filtered_tracker), display_limit):,} of "
            f"{len(filtered_tracker):,} matching records · "
            f"category: {tracker_category} · automated monitor checks approximately every 15 minutes."
        )

        download_df = filtered_tracker.drop(
            columns=["_FiledDate"],
            errors="ignore",
        )
        st.download_button(
            "Download all filtered filings as CSV",
            data=download_df.to_csv(
                index=False
            ).encode("utf-8"),
            file_name=(
                "equitylens_sec_filing_tracker.csv"
            ),
            mime="text/csv",
            use_container_width=True,
        )

        with st.expander("What do these SEC forms mean?"):
            form_guide = pd.DataFrame([
                {
                    "Form": "10-K",
                    "Meaning": "Annual report",
                    "Use it for": "Business, risks, audited annual financials, MD&A",
                },
                {
                    "Form": "10-Q",
                    "Meaning": "Quarterly report",
                    "Use it for": "Quarterly financials, updates, MD&A, changing risks",
                },
                {
                    "Form": "8-K",
                    "Meaning": "Current report",
                    "Use it for": "Specified material events and attached exhibits",
                },
                {
                    "Form": "20-F / 6-K",
                    "Meaning": "Foreign private issuer annual / current reporting",
                    "Use it for": "Comparable foreign-issuer disclosure context",
                },
                {
                    "Form": "S-1 / F-1 / S-11",
                    "Meaning": "Registration statement",
                    "Use it for": "IPO/offering business, risks, financials, ownership, dilution",
                },
                {
                    "Form": "3 / 4 / 5",
                    "Meaning": "Insider ownership / transaction filings",
                    "Use it for": "Reported insider positions and transactions",
                },
                {
                    "Form": "13D / 13G",
                    "Meaning": "Beneficial ownership disclosure",
                    "Use it for": "Certain holders crossing reporting thresholds",
                },
                {
                    "Form": "DEF 14A",
                    "Meaning": "Definitive proxy statement",
                    "Use it for": "Board matters, executive compensation, shareholder votes, and governance",
                },
            ])
            st.dataframe(
                form_guide,
                use_container_width=True,
                hide_index=True,
            )
            st.caption(
                "Form descriptions are educational summaries. The SEC form and the filed document are authoritative."
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

    archived_registration_feed = next(
        (
            feed
            for feed in sec_filings.values()
            if str(
                feed.get(
                    "ticker",
                    "",
                )
            ).upper()
            == registration_ticker.upper()
        ),
        {},
    )

    registration_feed = (
        archived_registration_feed
        if archived_registration_feed.get(
            "registration_filings"
        )
        else {}
    )
    registration_error = None

    if not registration_feed:
        try:
            registration_feed = (
                get_sec_company_research(
                    registration_ticker
                )
            )
        except Exception:
            registration_feed = (
                archived_registration_feed
            )
            registration_error = (
                "Live SEC refresh is temporarily unavailable. "
                "Showing the latest registration history from the synced archive."
            )

    if registration_error:
        st.info(registration_error)

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
