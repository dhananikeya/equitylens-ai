import html

import streamlit as st

from ui_components import section


def render_business_and_risks(
    *,
    selected_ticker,
    selected_analysis,
    latest_annual,
):
    section(
        "Business & Risks",
        "How the Business Works & What Could Disrupt It",
    )
    st.caption(
        "EquityLens structures qualitative company disclosures into a repeatable research framework. "
        "These are research summaries, not investment ratings. Verify material details in the source filing."
    )

    business_framework = [
        (
            "Business model",
            "What does the company actually sell or provide?",
            selected_analysis.get(
                "business_model",
                "Structured business-model research is not available yet.",
            ),
            "Start here. A financial result is difficult to interpret if you do not understand what creates the revenue.",
        ),
        (
            "Revenue engine",
            "How does money enter the business?",
            selected_analysis.get(
                "primary_revenue_source",
                "Structured revenue-source research is not available yet.",
            ),
            "Look for recurring subscriptions, transactions, advertising, hardware, services, usage, or other major revenue drivers.",
        ),
        (
            "Customers",
            "Who pays the company?",
            selected_analysis.get(
                "customer_type",
                "Structured customer research is not available yet.",
            ),
            "Customer type affects sales cycles, retention, pricing power, concentration risk, and sensitivity to economic conditions.",
        ),
        (
            "Operating dependencies",
            "What does the business rely on to operate?",
            selected_analysis.get(
                "platform_dependency",
                "Structured dependency research is not available yet.",
            ),
            "Dependencies can include cloud platforms, suppliers, distribution channels, app stores, partners, data, or third-party infrastructure.",
        ),
        (
            "Profitability history",
            "Has the business historically produced operating profit?",
            selected_analysis.get(
                "profitability_history",
                "Structured profitability history is not available yet.",
            ),
            "Growth and profitability should be read together. Fast growth does not automatically mean strong unit economics or durable profit.",
        ),
        (
            "International exposure",
            "How exposed is the company outside its home market?",
            selected_analysis.get(
                "international_exposure",
                "Structured international-exposure research is not available yet.",
            ),
            "International operations can add growth opportunities as well as currency, regulatory, tax, geopolitical, and execution risks.",
        ),
    ]

    business_html = "".join(
        (
            '<div class="el-framework-card">'
            f'<div class="el-framework-label">{html.escape(label)}</div>'
            f'<div class="el-framework-question">{html.escape(question)}</div>'
            f'<div class="el-framework-answer">{html.escape(str(answer))}</div>'
            f'<div class="el-framework-why"><strong>Why it matters:</strong> {html.escape(why)}</div>'
            '</div>'
        )
        for label, question, answer, why in business_framework
    )
    st.markdown(
        '<div class="el-framework-grid">'
        + business_html
        + '</div>',
        unsafe_allow_html=True,
    )

    section(
        "Risk framework",
        "What could change the story?",
    )
    st.caption(
        "SEC risk disclosures are intentionally broad. EquityLens groups the available research into themes "
        "so users can investigate the original language rather than treating a long risk list as a prediction."
    )

    risk_framework = [
        (
            "Competition",
            selected_analysis.get(
                "competitive_risk",
                "Structured competitive-risk research is not available yet.",
            ),
            "Watch product substitution, pricing pressure, larger incumbents, new entrants, and customer switching behavior.",
        ),
        (
            "Operations",
            selected_analysis.get(
                "operational_risk",
                "Structured operational-risk research is not available yet.",
            ),
            "Watch execution, capacity, reliability, supply chain, implementation, sales productivity, and other operating dependencies.",
        ),
        (
            "Customer concentration",
            selected_analysis.get(
                "customer_concentration",
                "Structured customer-concentration research is not available yet.",
            ),
            "A small number of important customers can make revenue less diversified and increase renewal or bargaining risk.",
        ),
        (
            "International / regulatory",
            selected_analysis.get(
                "international_exposure",
                "Structured international or regulatory risk research is not available yet.",
            ),
            "Cross-border operations can create currency, privacy, tax, sanctions, licensing, and geopolitical exposure.",
        ),
    ]

    risk_html = "".join(
        (
            '<div class="el-framework-card risk">'
            f'<div class="el-framework-label">{html.escape(label)}</div>'
            f'<div class="el-framework-answer">{html.escape(str(answer))}</div>'
            f'<div class="el-framework-why"><strong>Research prompt:</strong> {html.escape(prompt)}</div>'
            '</div>'
        )
        for label, answer, prompt in risk_framework
    )
    st.markdown(
        '<div class="el-framework-grid risk-grid">'
        + risk_html
        + '</div>',
        unsafe_allow_html=True,
    )

    st.markdown("**Key disclosed risk themes**")
    risk_themes = selected_analysis.get(
        "key_risk_themes",
        [],
    )
    if risk_themes:
        cols = st.columns(2)
        for index, risk in enumerate(
            risk_themes
        ):
            with cols[index % 2]:
                st.markdown(f"- {risk}")
    else:
        st.caption(
            "Structured risk themes are not available yet. "
            "Review the Risk Factors section in the original SEC filing."
        )

    filing_changes = selected_analysis.get(
        "filing_changes",
        {},
    )
    section(
        "Filing changes",
        "What changed from the prior annual filing?",
    )
    if filing_changes.get(
        "comparison_available"
    ):
        current_label = filing_changes.get(
            "current_filing_label",
            "Current annual filing",
        )
        prior_label = filing_changes.get(
            "prior_filing_label",
            "Prior annual filing",
        )
        st.caption(
            f"Comparison: {prior_label} → {current_label}. "
            "This section summarizes changes in supplied SEC filing evidence; it does not predict their impact."
        )

        change_cols = st.columns(2)
        change_groups = [
            (
                "Added or more prominent",
                filing_changes.get(
                    "added_or_increased_themes",
                    [],
                ),
            ),
            (
                "Reduced or removed",
                filing_changes.get(
                    "reduced_or_removed_themes",
                    [],
                ),
            ),
            (
                "Notable language changes",
                filing_changes.get(
                    "notable_language_changes",
                    [],
                ),
            ),
            (
                "Core themes that remained",
                filing_changes.get(
                    "unchanged_core_themes",
                    [],
                ),
            ),
        ]

        for index, (
            label,
            items,
        ) in enumerate(change_groups):
            with change_cols[
                index % 2
            ]:
                st.markdown(
                    f"**{label}**"
                )
                if items:
                    for item in items:
                        st.markdown(
                            f"- {item}"
                        )
                else:
                    st.caption(
                        "No supported change was identified in the supplied excerpts."
                    )

        comparison_notes = (
            filing_changes.get(
                "confidence_notes",
                [],
            )
        )
        if comparison_notes:
            with st.expander(
                "Comparison limitations"
            ):
                for note in comparison_notes:
                    st.markdown(
                        f"- {note}"
                    )
    else:
        st.info(
            "Prior-vs-current annual filing comparison has not been generated for this company yet. "
            "The local deep-research worker now supports this comparison and will add it when the company is refreshed."
        )

    source_filing = selected_analysis.get(
        "source_filing",
        "",
    )
    if source_filing:
        st.link_button(
            "Open source filing for Business & Risks",
            source_filing,
            key=(
                "business_risk_source_"
                + selected_ticker
            ),
        )
    elif latest_annual.get("url"):
        st.link_button(
            "Open latest annual filing",
            latest_annual["url"],
            key=(
                "business_risk_annual_source_"
                + selected_ticker
            ),
        )

    st.caption(
        "Research summaries can lag a newly filed report. The original SEC filing is the authoritative disclosure."
    )
