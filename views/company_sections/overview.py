import html

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from financial_utils import (
    build_change_notes,
    calc_growth,
    calc_margin,
    format_money,
    pct,
)
from market_data import get_market_history
from research_experience import (
    render_company_evidence,
    render_report_download,
)
from ui_components import section


def render_overview(
    *,
    selected_ticker,
    selected_name,
    selected_industry_name,
    selected_sector_name,
    selected_analysis,
    selected_qdata,
    selected_data,
    selected_filings,
    selected_sec_error,
    selected_fallback_history,
    selected_price,
    income_selection,
    workspace_growth,
    workspace_revenue,
    financial_currency,
    financial_period,
    revenue_source_label,
    filing_form,
    filing_date,
    latest_available_filing,
    navigate_to,
):
    section(
        "Overview",
        "Understand the company in 60 seconds",
    )

    overview_record = income_selection[
        "record"
    ]
    overview_revenue = overview_record.get(
        "revenue"
    )
    operating_margin = calc_margin(
        overview_record.get(
            "operating_income"
        ),
        overview_revenue,
    )
    net_margin = calc_margin(
        overview_record.get(
            "net_income"
        ),
        overview_revenue,
    )

    growth_copy = (
        f"Revenue growth: {pct(workspace_growth)} "
        f"({income_selection['growth_basis'].lower()})."
        if workspace_growth is not None
        else (
            "Comparable revenue growth is not available "
            "for the current reporting period."
        )
    )
    profitability_copy = (
        f" Operating margin: {pct(operating_margin)}."
        if operating_margin is not None
        else ""
    )
    net_copy = (
        f" Net margin: {pct(net_margin)}."
        if net_margin is not None
        else ""
    )

    overview_cards = [
        (
            "What does it do?",
            selected_analysis.get(
                "business_model",
                "Structured business-model research is still being added. "
                "Use the Business & Risks section and original filings for source context.",
            ),
        ),
        (
            "How does it make money?",
            selected_analysis.get(
                "primary_revenue_source",
                "The primary revenue source has not been structured yet.",
            ),
        ),
        (
            "Who buys?",
            selected_analysis.get(
                "customer_type",
                "Customer-type research has not been structured yet.",
            ),
        ),
        (
            "Growth & profitability",
            growth_copy
            + profitability_copy
            + net_copy,
        ),
    ]

    overview_html = "".join(
        (
            '<div class="el-overview-card">'
            f'<div class="el-overview-question">{html.escape(label)}</div>'
            f'<div class="el-overview-answer">{html.escape(str(answer))}</div>'
            '</div>'
        )
        for label, answer in overview_cards
    )
    st.markdown(
        '<div class="el-overview-grid">'
        + overview_html
        + '</div>',
        unsafe_allow_html=True,
    )
    st.caption(
        "Financial snapshot period: "
        + str(
            financial_period
            or "period unavailable"
        )
        + " · Financial source: "
        + str(revenue_source_label)
        + "."
    )

    research_path_cols = st.columns(4)
    research_path = [
        (
            "1 · Understand",
            "Business & Risks",
            "Business model, revenue engine, customers, and disclosed risks.",
        ),
        (
            "2 · Measure",
            "Financials",
            "Growth, margins, profitability, cash, debt, and reported periods.",
        ),
        (
            "3 · Verify",
            "SEC Filings",
            "Read the original 10-K, 10-Q, 8-K, and registration documents.",
        ),
        (
            "4 · Compare",
            "Peers & ETFs",
            "Put the company beside others in the same industry.",
        ),
    ]
    for col, (
        step,
        destination,
        description,
    ) in zip(
        research_path_cols,
        research_path,
    ):
        with col:
            st.markdown(
                f"**{step}**"
            )
            st.caption(description)
            st.caption(
                "Workspace section: "
                + destination
            )

    checklist_items = [
        "I understand what the company sells and how it makes money.",
        "I reviewed the latest revenue growth and profitability.",
        "I checked cash, investments, debt, and the balance-sheet date.",
        "I reviewed the latest 10-K or annual filing.",
        "I reviewed the latest 10-Q / interim filing when available.",
        "I reviewed the major disclosed risk themes.",
        "I compared the company with relevant peers.",
        "I verified at least one important conclusion in a primary filing.",
    ]
    checklist_keys = [
        (
            f"research_check_"
            f"{selected_ticker}_"
            f"{index}"
        )
        for index in range(
            len(checklist_items)
        )
    ]

    def clear_research_checklist():
        for key in checklist_keys:
            st.session_state.pop(
                key,
                None,
            )

    with st.expander(
        "Research checklist"
    ):
        completed = sum(
            bool(
                st.session_state.get(
                    key,
                    False,
                )
            )
            for key in checklist_keys
        )
        st.progress(
            completed
            / len(checklist_items)
        )
        st.caption(
            f"{completed} of {len(checklist_items)} research steps completed during this visit."
        )
        for item, key in zip(
            checklist_items,
            checklist_keys,
        ):
            st.checkbox(
                item,
                key=key,
            )
        st.button(
            "Clear research checklist",
            key=(
                "clear_research_checklist_"
                + selected_ticker
            ),
            on_click=(
                clear_research_checklist
            ),
        )
        st.caption(
            "This checklist is a research workflow aid, not a score and not an investment recommendation."
        )

    summary_columns = st.columns(2)
    with summary_columns[0]:
        st.markdown(
            "**Key disclosed risks to investigate**"
        )
        summary_risks = (
            selected_analysis.get(
                "key_risk_themes",
                [],
            )
        )
        if summary_risks:
            for risk in summary_risks[:4]:
                st.write(
                    f"• {risk}"
                )
        else:
            st.caption(
                "Structured risk themes are still being added. "
                "Review Risk Factors in the original filing."
            )

    with summary_columns[1]:
        st.markdown(
            "**Latest source filing**"
        )
        if latest_available_filing:
            st.write(
                f"{filing_form} · Filed {filing_date}"
            )
            description = (
                latest_available_filing.get(
                    "description"
                )
                or latest_available_filing.get(
                    "primary_document"
                )
            )
            if description:
                st.caption(
                    str(description)
                )
            if latest_available_filing.get(
                "url"
            ):
                st.link_button(
                    "Open original SEC filing",
                    latest_available_filing[
                        "url"
                    ],
                    key=(
                        "overview_latest_filing_"
                        + selected_ticker
                    ),
                )
        else:
            st.caption(
                "No filing is available in the current feed yet."
            )

    with st.expander(
        "Need help reading these numbers?"
    ):
        st.markdown(
            "**Revenue:** sales before expenses.\n\n"
            "**Operating margin:** operating profit as a percentage of revenue.\n\n"
            "**Net margin:** final profit or loss as a percentage of revenue.\n\n"
            "**LTM:** the most recent twelve months of results.\n\n"
            "**YoY:** comparison with the same period one year earlier.\n\n"
            "**10-K / 10-Q:** annual / quarterly SEC reports."
        )
        st.button(
            "Open Learn",
            key="summary_open_learn",
            on_click=navigate_to,
            args=("Learn",),
        )

    chart_col, context_col = (
        st.columns([1.65, 1])
    )

    with chart_col:
        st.markdown(
            "**Price Performance**"
        )
        chart_range = st.radio(
            "Range",
            [
                "1M",
                "3M",
                "1Y",
                "2Y",
            ],
            index=2,
            horizontal=True,
            key=(
                "workspace_chart_range_"
                + selected_ticker
            ),
            label_visibility="collapsed",
        )
        history_key = (
            "company_history::"
            + selected_ticker
            + "::"
            + chart_range
        )
        selected_history = (
            st.session_state.get(
                history_key
            )
        )
        if not isinstance(
            selected_history,
            pd.DataFrame,
        ):
            try:
                selected_history = (
                    get_market_history(
                        selected_ticker,
                        interval="1day",
                        outputsize=None,
                        calendar_range=(
                            chart_range
                        ),
                    )
                )
            except Exception:
                selected_history = (
                    pd.DataFrame()
                )
            st.session_state[
                history_key
            ] = selected_history

        if not selected_history.empty:
            price_fig = go.Figure(
                go.Scatter(
                    x=selected_history[
                        "datetime"
                    ],
                    y=selected_history[
                        "close"
                    ],
                    mode="lines",
                    name=selected_ticker,
                    line={
                        "color": "#16C7B2",
                        "width": 2,
                    },
                )
            )
            price_fig.update_layout(
                height=390,
                margin={
                    "l": 8,
                    "r": 8,
                    "t": 22,
                    "b": 8,
                },
                paper_bgcolor=(
                    "rgba(0,0,0,0)"
                ),
                plot_bgcolor=(
                    "rgba(0,0,0,0)"
                ),
                font={
                    "color": "#8F9CA6",
                    "family": (
                        "IBM Plex Sans"
                    ),
                },
                hovermode="x unified",
                showlegend=False,
                xaxis={
                    "showgrid": False,
                    "zeroline": False,
                    "title": None,
                },
                yaxis={
                    "gridcolor": (
                        "rgba(143,156,166,.12)"
                    ),
                    "zeroline": False,
                    "title": None,
                    "tickprefix": "$",
                },
            )
            st.plotly_chart(
                price_fig,
                use_container_width=True,
                config={
                    "displayModeBar": False
                },
            )
        else:
            st.info(
                "Price history is temporarily unavailable."
            )

    with context_col:
        st.markdown(
            "**Company Snapshot**"
        )
        snapshot_items = [
            (
                "Primary revenue source",
                selected_analysis.get(
                    "primary_revenue_source",
                    "Research in progress.",
                ),
            ),
            (
                "Customer type",
                selected_analysis.get(
                    "customer_type",
                    "Research in progress.",
                ),
            ),
            (
                "Platform / operating dependency",
                selected_analysis.get(
                    "platform_dependency",
                    "Research in progress.",
                ),
            ),
        ]
        for label, value in snapshot_items:
            st.markdown(
                f"**{label}**"
            )
            st.write(value)

    st.markdown("---")
    left, right = st.columns(2)

    with left:
        st.markdown(
            "**What changed recently**"
        )
        change_notes = build_change_notes(
            selected_qdata
        )
        if not change_notes:
            annual_history = (
                selected_data.get(
                    "history",
                    [],
                )
                or selected_fallback_history
            )
            if len(annual_history) >= 2:
                latest_year = (
                    annual_history[-1]
                )
                prior_year = (
                    annual_history[-2]
                )
                annual_growth = (
                    calc_growth(
                        latest_year.get(
                            "revenue"
                        ),
                        prior_year.get(
                            "revenue"
                        ),
                    )
                )
                if (
                    annual_growth
                    is not None
                ):
                    change_notes = [(
                        "Annual revenue",
                        (
                            f"Revenue changed {annual_growth:+.1f}% from "
                            f"FY{prior_year.get('fiscal_year')} to "
                            f"FY{latest_year.get('fiscal_year')}."
                        ),
                    )]

        if change_notes:
            for label, copy in (
                change_notes[:4]
            ):
                st.markdown(
                    f"**{label}**"
                )
                st.write(copy)
        else:
            st.caption(
                "Recent standardized period-over-period changes are still being prepared."
            )

    with right:
        st.markdown(
            "**Key disclosed risk themes**"
        )
        risk_themes = (
            selected_analysis.get(
                "key_risk_themes",
                [],
            )
        )
        if risk_themes:
            for risk in risk_themes[:8]:
                st.markdown(
                    f"- {risk}"
                )
        else:
            st.caption(
                "Structured risk themes are being added as deep research coverage expands."
            )

    st.markdown(
        "**Recent SEC activity**"
    )
    if selected_filings:
        rows = [
            {
                "Filed": filing.get(
                    "filing_date",
                    "",
                ),
                "Form": filing.get(
                    "form",
                    "",
                ),
                "Description": (
                    filing.get(
                        "description",
                        "",
                    )
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
            for filing in selected_filings[
                :6
            ]
        ]
        st.dataframe(
            pd.DataFrame(rows),
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
    elif selected_sec_error:
        st.warning(
            selected_sec_error
        )
    else:
        st.caption(
            "Recent filing metadata is not available yet."
        )

    section(
        "Evidence",
        "Verify the research",
    )
    render_company_evidence(
        st,
        selected_ticker,
        selected_analysis,
        selected_filings,
        pct(workspace_growth),
        financial_period,
    )

    with st.expander(
        "Export this research"
    ):
        st.caption(
            "Download a dated EquityLens research summary for offline review. "
            "Primary filings remain the authoritative source."
        )
        render_report_download(
            st,
            selected_name,
            selected_ticker,
            selected_industry_name,
            selected_sector_name,
            selected_analysis,
            selected_filings,
            {
                (
                    "Price (Yahoo Finance, may be delayed)"
                ): (
                    "$"
                    + f"{selected_price:,.2f}"
                    if selected_price
                    is not None
                    else "Not available"
                ),
                "Revenue": (
                    format_money(
                        workspace_revenue,
                        financial_currency,
                    )
                ),
                "Revenue growth": (
                    pct(
                        workspace_growth
                    )
                ),
                "Reporting period": (
                    financial_period
                    or "See Financials"
                ),
                "Data source": (
                    revenue_source_label
                ),
                "Most recent filing": (
                    f"{filing_form} · {filing_date}"
                ),
            },
        )
