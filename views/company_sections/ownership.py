import pandas as pd
import streamlit as st

from financial_utils import format_money, safe_float
from market_data import get_company_ownership_data
from sources import source_label
from ui_components import section


def _ownership_pct(value):
    number = safe_float(value)
    if number is None:
        return "N/A"
    if abs(number) <= 1:
        number *= 100
    return f"{number:.1f}%"


def _ownership_count(value):
    number = safe_float(value)
    return (
        f"{int(number):,}"
        if number is not None
        else "N/A"
    )


def _clean_holder_table(table):
    if (
        not isinstance(table, pd.DataFrame)
        or table.empty
    ):
        return pd.DataFrame()

    cleaned = table.copy()
    cleaned = cleaned.drop(
        columns=[
            column
            for column in ["index"]
            if column in cleaned.columns
        ],
        errors="ignore",
    )
    cleaned = cleaned.rename(
        columns={
            "Date Reported": "Reported",
            "pctHeld": "% Held",
            "pctChange": "% Change",
            "Value": "Position Value",
        }
    )

    if "Reported" in cleaned.columns:
        cleaned["Reported"] = pd.to_datetime(
            cleaned["Reported"],
            errors="coerce",
        ).dt.date.astype(str)

    if "% Held" in cleaned.columns:
        cleaned["% Held"] = cleaned["% Held"].apply(
            _ownership_pct
        )

    if "% Change" in cleaned.columns:
        cleaned["% Change"] = cleaned[
            "% Change"
        ].apply(_ownership_pct)

    if "Shares" in cleaned.columns:
        cleaned["Shares"] = cleaned["Shares"].apply(
            lambda value: (
                f"{int(safe_float(value)):,}"
                if safe_float(value) is not None
                else "N/A"
            )
        )

    if "Position Value" in cleaned.columns:
        cleaned["Position Value"] = cleaned[
            "Position Value"
        ].apply(
            lambda value: format_money(
                safe_float(value)
            )
        )

    preferred = [
        column
        for column in [
            "Holder",
            "Reported",
            "% Held",
            "Shares",
            "Position Value",
            "% Change",
        ]
        if column in cleaned.columns
    ]
    remaining = [
        column
        for column in cleaned.columns
        if column not in preferred
    ]
    return cleaned[preferred + remaining]


def render_ownership(
    selected_ticker,
    selected_data,
    selected_s1,
    selected_filings,
):
    section(
        "Ownership",
        "Capital Structure, Control & Major Holders",
    )
    st.caption(
        "Start with issuer-reported capital structure and SEC ownership disclosures. "
        "Institutional and mutual-fund holder tables are supplemental market data and can update on a different schedule."
    )

    capital = selected_data.get(
        "capital_structure",
        {},
    )
    shares = capital.get("shares_outstanding")
    debt = capital.get("total_debt")
    cash_investments = capital.get(
        "cash_and_investments"
    )
    balance_date = (
        capital.get("balance_sheet_as_of")
        or selected_data.get("fiscal_year_end")
        or "Date unavailable"
    )
    share_date = (
        capital.get("shares_as_of")
        or "Date unavailable"
    )

    capital_cols = st.columns(4)
    capital_cols[0].metric(
        "Shares Outstanding · Reported",
        (
            f"{int(shares):,}"
            if shares is not None
            else "N/A"
        ),
        share_date if shares is not None else None,
    )
    capital_cols[1].metric(
        "Total Debt · Reported",
        format_money(debt),
    )
    capital_cols[2].metric(
        "Cash + Investments · Reported",
        format_money(cash_investments),
    )
    capital_cols[3].metric(
        "Balance Sheet Date",
        balance_date,
    )

    source = capital.get("source_filing", "")
    if source:
        st.link_button(
            "Open capital-structure source filing",
            source,
            key=(
                f"ownership_capital_source_"
                f"{selected_ticker}"
            ),
        )

    ipo_ownership_points = (
        selected_s1.get("filing_details", {})
        .get("ipo_capitalization_dilution", [])
    )
    ipo_control_points = (
        selected_s1.get("filing_details", {})
        .get("proceeds_management_ownership", [])
    )
    if ipo_ownership_points or ipo_control_points:
        with st.expander(
            "Historical IPO-era control & dilution context"
        ):
            st.caption(
                "Historical registration context only. Voting rights, ownership, share classes, "
                "and capitalization may have changed since the offering."
            )
            if ipo_ownership_points:
                st.markdown(
                    "**Capitalization & dilution disclosed at registration**"
                )
                for point in ipo_ownership_points:
                    st.markdown(f"- {point}")
            if ipo_control_points:
                st.markdown(
                    "**Management / ownership context disclosed at registration**"
                )
                for point in ipo_control_points:
                    st.markdown(f"- {point}")

    st.markdown("**Supplemental ownership snapshot**")
    snapshot_key = (
        f"company_ownership::{selected_ticker}"
    )
    ownership_data = st.session_state.get(
        snapshot_key
    )
    if not isinstance(ownership_data, dict):
        try:
            ownership_data = (
                get_company_ownership_data(
                    selected_ticker
                )
            )
        except Exception:
            ownership_data = {
                "major": pd.DataFrame(),
                "institutional": pd.DataFrame(),
                "mutual_fund": pd.DataFrame(),
            }
        st.session_state[snapshot_key] = (
            ownership_data
        )

    major_table = ownership_data.get(
        "major",
        pd.DataFrame(),
    )
    major_lookup = {}
    if (
        isinstance(major_table, pd.DataFrame)
        and not major_table.empty
    ):
        major_copy = major_table.copy()
        key_column = next(
            (
                column
                for column in [
                    "index",
                    "Breakdown",
                    "Metric",
                ]
                if column in major_copy.columns
            ),
            major_copy.columns[0],
        )
        value_column = next(
            (
                column
                for column in ["Value", "value"]
                if column in major_copy.columns
            ),
            major_copy.columns[-1],
        )
        for _, row in major_copy.iterrows():
            major_lookup[
                str(row.get(key_column, ""))
            ] = row.get(value_column)

    summary_cols = st.columns(4)
    summary_cols[0].metric(
        "Insider ownership",
        _ownership_pct(
            major_lookup.get(
                "insidersPercentHeld",
                major_lookup.get(
                    "% of Shares Held by All Insider",
                    None,
                ),
            )
        ),
    )
    summary_cols[1].metric(
        "Institutional ownership",
        _ownership_pct(
            major_lookup.get(
                "institutionsPercentHeld",
                major_lookup.get(
                    "% of Shares Held by Institutions",
                    None,
                ),
            )
        ),
    )
    summary_cols[2].metric(
        "Institutional float",
        _ownership_pct(
            major_lookup.get(
                "institutionsFloatPercentHeld",
                major_lookup.get(
                    "% of Float Held by Institutions",
                    None,
                ),
            )
        ),
    )
    summary_cols[3].metric(
        "Institutional holders",
        _ownership_count(
            major_lookup.get(
                "institutionsCount",
                major_lookup.get(
                    "Number of Institutions Holding Shares",
                    None,
                ),
            )
        ),
    )

    st.markdown(
        "**SEC beneficial-ownership filings**"
    )
    ownership_forms = {
        "DEF 14A",
        "DEFA14A",
        "SC 13D",
        "SC 13D/A",
        "SC 13G",
        "SC 13G/A",
    }
    sec_rows = [
        {
            "Filed": filing.get(
                "filing_date",
                "",
            ),
            "Form": filing.get("form", ""),
            "Description": (
                filing.get("description", "")
                or filing.get(
                    "primary_document",
                    "",
                )
            ),
            "SEC Filing": filing.get("url", ""),
        }
        for filing in selected_filings
        if filing.get("form") in ownership_forms
    ][:20]

    if sec_rows:
        st.dataframe(
            pd.DataFrame(sec_rows),
            use_container_width=True,
            hide_index=True,
            column_config={
                "SEC Filing": (
                    st.column_config.LinkColumn(
                        "SEC Filing",
                        display_text="Open",
                    )
                )
            },
        )
    else:
        st.caption(
            "No proxy or Schedule 13D/13G filing appeared in the currently loaded SEC history."
        )

    st.markdown(
        "**Largest institutional holders**"
    )
    institutional = _clean_holder_table(
        ownership_data.get(
            "institutional",
            pd.DataFrame(),
        )
    )
    if not institutional.empty:
        st.dataframe(
            institutional.head(15),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.caption(
            "Institutional-holder detail is unavailable from the supplemental feed."
        )

    st.markdown(
        "**Largest mutual-fund holders**"
    )
    mutual = _clean_holder_table(
        ownership_data.get(
            "mutual_fund",
            pd.DataFrame(),
        )
    )
    if not mutual.empty:
        st.dataframe(
            mutual.head(15),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.caption(
            "Mutual-fund holder detail is unavailable from the supplemental feed."
        )

    st.caption(
        "Source hierarchy: "
        + source_label("SEC")
        + " for capital structure and beneficial-ownership disclosures; "
        + source_label("Yahoo")
        + " for supplemental institutional and fund-holder tables. "
        "A 13D/13G, proxy filing, and third-party holder table can represent different dates and ownership concepts."
    )
