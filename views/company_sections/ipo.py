import pandas as pd
import streamlit as st

from ui_components import section


def render_ipo_registration(
    *,
    selected_ticker,
    selected_registrations,
    selected_s1,
):
    section(
        "IPO / Registration",
        "How the Company Described Itself Before or During the Offering",
    )
    st.caption(
        "Registration filings are historical documents. They can explain the company's original "
        "business model, ownership, risks, capitalization, and offering structure, but they should "
        "not be treated as current company facts without checking newer filings."
    )

    if selected_registrations:
        st.markdown(
            "**Registration filing timeline**"
        )
        registration_table = pd.DataFrame([
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
                "SEC Filing": filing.get(
                    "url",
                    "",
                ),
            }
            for filing in selected_registrations
        ])
        st.dataframe(
            registration_table,
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
            "Amendments such as S-1/A or F-1/A can update financials, pricing, share counts, "
            "ownership, risk disclosure, or other offering terms."
        )

    if selected_s1:
        header_cols = st.columns(3)
        header_cols[0].metric(
            "Form",
            selected_s1.get(
                "form",
                "Registration",
            ),
        )
        header_cols[1].metric(
            "Filed",
            selected_s1.get(
                "filed_date",
                "Date unavailable",
            ),
        )
        header_cols[2].metric(
            "Context",
            "Historical",
            help=(
                "This research describes registration-era disclosures, "
                "not necessarily the company's current business."
            ),
        )

        st.markdown("**Historical context**")
        st.write(
            selected_s1.get(
                "historical_context",
                "Historical registration context is available.",
            )
        )
        st.markdown(
            "**What this filing can teach you**"
        )
        st.write(
            selected_s1.get(
                "what_to_learn",
                "Review the original registration filing for business, risk, ownership, and financial context.",
            )
        )

        detail_map = selected_s1.get(
            "filing_details",
            {},
        )
        detail_sections = [
            (
                "Business & Revenue Model",
                "business_revenue_model",
                "How the company described what it sold and how revenue was generated at the time of registration.",
            ),
            (
                "Customers & Go-to-Market",
                "customers_go_to_market",
                "Customer base, sales motion, retention, expansion, and distribution context disclosed before the offering.",
            ),
            (
                "Growth & Market Opportunity",
                "growth_market_opportunity",
                "Management's historical description of expansion opportunities and growth vectors.",
            ),
            (
                "Competition & Differentiation",
                "competition_differentiation",
                "How management positioned the company against alternatives at the time.",
            ),
            (
                "Risk Factors",
                "risk_factors",
                "Major offering-era risks disclosed to prospective investors.",
            ),
            (
                "Financial History",
                "financial_history",
                "Pre-offering revenue, profitability, cash-flow, and other financial context captured in the filing.",
            ),
            (
                "Capitalization & Dilution",
                "ipo_capitalization_dilution",
                "Share classes, voting structure, offering capitalization, and dilution context.",
            ),
            (
                "Proceeds, Management & Ownership",
                "proceeds_management_ownership",
                "Use of proceeds and the management / ownership structure around the offering.",
            ),
        ]

        for label, field, explanation in detail_sections:
            with st.expander(
                label,
                expanded=(
                    label
                    == "Business & Revenue Model"
                ),
            ):
                st.caption(explanation)
                points = detail_map.get(
                    field,
                    [],
                )
                if points:
                    for point in points:
                        st.markdown(f"- {point}")
                else:
                    st.caption(
                        "Structured detail is not available for this part of the registration filing yet."
                    )

        if selected_s1.get("source_url"):
            st.link_button(
                (
                    "Open original "
                    + selected_s1.get(
                        "form",
                        "registration filing",
                    )
                    + " on SEC EDGAR"
                ),
                selected_s1.get("source_url"),
                key=(
                    f"workspace_s1_source_"
                    f"{selected_ticker}"
                ),
            )
    elif selected_registrations:
        st.info(
            "EquityLens has indexed the registration filing history, but the deep structured "
            "registration analysis has not been generated for this company yet."
        )
        first_registration = (
            selected_registrations[0]
        )
        if first_registration.get("url"):
            st.link_button(
                (
                    "Open "
                    + first_registration.get(
                        "form",
                        "registration filing",
                    )
                    + " on SEC EDGAR"
                ),
                first_registration["url"],
                key=(
                    "workspace_registration_direct_"
                    + selected_ticker
                ),
            )
    else:
        st.info(
            "No S-1, F-1, or S-11 registration statement was found in the indexed SEC history. "
            "Some older issuers, foreign issuers, reorganizations, or companies with limited electronic "
            "filing history may not have a registration statement available in the current feed."
        )
