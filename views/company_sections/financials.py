import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from market_data import get_company_financial_snapshot
from financial_utils import (
    calc_margin,
    format_money,
    pct,
)
from ui_components import section


def render_financials(
    *,
    selected_ticker,
    selected_data,
    selected_qdata,
    selected_financial_fallback,
    selected_fallback_quarters,
    income_selection,
    workspace_growth,
    financial_currency,
):
    section(
        "Financials",
        "Income Statement & Balance Sheet",
    )

    supplemental_financials = (
        selected_financial_fallback
        if isinstance(
            selected_financial_fallback,
            dict,
        )
        else {}
    )
    supplemental_key = (
        "company_financial_section::"
        + selected_ticker
    )
    if not supplemental_financials.get(
        "cash_flow"
    ):
        cached_supplemental = (
            st.session_state.get(
                supplemental_key
            )
        )
        if not isinstance(
            cached_supplemental,
            dict,
        ):
            try:
                cached_supplemental = (
                    get_company_financial_snapshot(
                        selected_ticker
                    )
                )
            except Exception:
                cached_supplemental = {}
            st.session_state[
                supplemental_key
            ] = cached_supplemental

        if cached_supplemental:
            supplemental_financials = (
                cached_supplemental
            )

    latest_financial_period = income_selection[
        "record"
    ]
    financial_period_label = (
        income_selection.get("period")
        or "Reporting period unavailable"
    )
    financial_source_label = (
        income_selection.get("source")
        or "Source unavailable"
    )

    period_revenue = latest_financial_period.get(
        "revenue"
    )
    period_gross_profit = (
        latest_financial_period.get(
            "gross_profit"
        )
    )
    period_operating_income = (
        latest_financial_period.get(
            "operating_income"
        )
    )
    period_net_income = (
        latest_financial_period.get(
            "net_income"
        )
    )

    gross_margin_value = calc_margin(
        period_gross_profit,
        period_revenue,
    )
    operating_margin_value = calc_margin(
        period_operating_income,
        period_revenue,
    )
    net_margin_value = calc_margin(
        period_net_income,
        period_revenue,
    )

    st.caption(
        f"Reporting period: {financial_period_label} · "
        f"Reporting currency: {financial_currency} · "
        f"Source: {financial_source_label}. "
        "Reported values come from the selected source record; margins and growth are calculated by EquityLens."
    )

    primary_cols = st.columns(4)
    primary_cols[0].metric(
        "Revenue · Reported",
        format_money(period_revenue, financial_currency),
        help=(
            "Reported revenue for "
            + financial_period_label
            + "."
        ),
    )
    primary_cols[1].metric(
        "Revenue Growth · Calculated",
        pct(workspace_growth),
        help=income_selection.get(
            "growth_basis",
            "Comparable-period revenue growth.",
        ),
    )
    primary_cols[2].metric(
        "Operating Margin · Calculated",
        pct(operating_margin_value),
        help=(
            "Operating income divided by revenue "
            "for the same reporting period."
        ),
    )
    primary_cols[3].metric(
        "Net Income · Reported",
        format_money(period_net_income, financial_currency),
        help=(
            "Reported net income or loss for "
            + financial_period_label
            + "."
        ),
    )

    secondary_cols = st.columns(4)
    secondary_cols[0].metric(
        "Gross Profit · Reported",
        format_money(period_gross_profit, financial_currency),
    )
    secondary_cols[1].metric(
        "Gross Margin · Calculated",
        pct(gross_margin_value),
        help=(
            "Gross profit divided by revenue "
            "for the same reporting period."
        ),
    )
    secondary_cols[2].metric(
        "Operating Income · Reported",
        format_money(
            period_operating_income,
            financial_currency,
        ),
    )
    secondary_cols[3].metric(
        "Net Margin · Calculated",
        pct(net_margin_value),
        help=(
            "Net income divided by revenue "
            "for the same reporting period."
        ),
    )

    st.caption(
        "Reported = taken from the selected financial source. "
        "Calculated = derived by EquityLens from reported figures in the same period. "
        "Unavailable values are not treated as zero."
    )

    exact_rows = [
        {
            "Metric": "Revenue",
            "Value": format_money(
                period_revenue,
                financial_currency,
            ),
            "Type": "Reported",
            "Period": financial_period_label,
            "Source": financial_source_label,
        },
        {
            "Metric": "Gross Profit",
            "Value": format_money(
                period_gross_profit,
                financial_currency,
            ),
            "Type": "Reported",
            "Period": financial_period_label,
            "Source": financial_source_label,
        },
        {
            "Metric": "Operating Income",
            "Value": format_money(
                period_operating_income,
                financial_currency,
            ),
            "Type": "Reported",
            "Period": financial_period_label,
            "Source": financial_source_label,
        },
        {
            "Metric": "Net Income",
            "Value": format_money(
                period_net_income,
                financial_currency,
            ),
            "Type": "Reported",
            "Period": financial_period_label,
            "Source": financial_source_label,
        },
        {
            "Metric": "Revenue Growth",
            "Value": pct(workspace_growth),
            "Type": "Calculated",
            "Period": financial_period_label,
            "Source": income_selection.get(
                "growth_basis",
                "",
            ),
        },
        {
            "Metric": "Gross Margin",
            "Value": pct(
                gross_margin_value
            ),
            "Type": "Calculated",
            "Period": financial_period_label,
            "Source": (
                "Gross profit ÷ revenue"
            ),
        },
        {
            "Metric": "Operating Margin",
            "Value": pct(
                operating_margin_value
            ),
            "Type": "Calculated",
            "Period": financial_period_label,
            "Source": (
                "Operating income ÷ revenue"
            ),
        },
        {
            "Metric": "Net Margin",
            "Value": pct(
                net_margin_value
            ),
            "Type": "Calculated",
            "Period": financial_period_label,
            "Source": (
                "Net income ÷ revenue"
            ),
        },
    ]
    with st.expander(
        "Show exact values, periods & calculation labels"
    ):
        st.dataframe(
            pd.DataFrame(exact_rows),
            use_container_width=True,
            hide_index=True,
        )

    annual_history = income_selection[
        "annual_history"
    ]
    st.caption(
        "Annual trend source: "
        + str(
            income_selection[
                "annual_source"
            ]
        )
        + " · reporting currency: "
        + str(financial_currency)
    )
    chart_cols = st.columns(2)

    with chart_cols[0]:
        st.markdown(
            "**Annual Revenue Trend**"
        )
        annual_rows = [
            row
            for row in annual_history
            if (
                row.get("fiscal_year")
                is not None
                and row.get("revenue")
                is not None
            )
        ]
        if annual_rows:
            annual_df = pd.DataFrame(
                annual_rows
            )
            annual_fig = go.Figure(
                go.Bar(
                    x=annual_df[
                        "fiscal_year"
                    ].astype(str),
                    y=annual_df["revenue"],
                    name="Revenue",
                    marker={
                        "color": "#16C7B2"
                    },
                )
            )
            annual_fig.update_layout(
                height=330,
                margin={
                    "l": 8,
                    "r": 8,
                    "t": 20,
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
                showlegend=False,
                xaxis={
                    "showgrid": False,
                    "title": None,
                },
                yaxis={
                    "gridcolor": (
                        "rgba(143,156,166,.12)"
                    ),
                    "title": None,
                },
            )
            st.plotly_chart(
                annual_fig,
                use_container_width=True,
                config={
                    "displayModeBar": False
                },
            )
        else:
            st.info(
                "Annual revenue history is still being standardized."
            )

    with chart_cols[1]:
        st.markdown(
            "**Latest P&L Structure**"
        )
        pnl_labels = [
            "Revenue",
            "Gross Profit",
            "Operating Income",
            "Net Income",
        ]
        pnl_values = [
            latest_financial_period.get(
                "revenue"
            ),
            latest_financial_period.get(
                "gross_profit"
            ),
            latest_financial_period.get(
                "operating_income"
            ),
            latest_financial_period.get(
                "net_income"
            ),
        ]
        if any(
            value is not None
            for value in pnl_values
        ):
            pnl_fig = go.Figure(
                go.Bar(
                    x=pnl_labels,
                    y=pnl_values,
                    marker={
                        "color": "#7DD3FC"
                    },
                )
            )
            pnl_fig.update_layout(
                height=330,
                margin={
                    "l": 8,
                    "r": 8,
                    "t": 20,
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
                showlegend=False,
                xaxis={
                    "showgrid": False,
                    "title": None,
                },
                yaxis={
                    "gridcolor": (
                        "rgba(143,156,166,.12)"
                    ),
                    "title": None,
                },
            )
            st.plotly_chart(
                pnl_fig,
                use_container_width=True,
                config={
                    "displayModeBar": False
                },
            )
        else:
            st.info(
                "P&L data is still being standardized."
            )

    latest_q = selected_qdata.get(
        "latest_quarter",
        {},
    )
    prior_q = selected_qdata.get(
        "prior_quarter",
        {},
    )
    prior_y_q = selected_qdata.get(
        "prior_year_quarter",
        {},
    )

    if (
        not latest_q
        and selected_fallback_quarters
    ):
        latest_q = (
            selected_fallback_quarters[-1]
        )
        prior_q = (
            selected_fallback_quarters[-2]
            if len(
                selected_fallback_quarters
            )
            >= 2
            else {}
        )
        prior_y_q = (
            selected_fallback_quarters[-5]
            if len(
                selected_fallback_quarters
            )
            >= 5
            else {}
        )

    if latest_q and (
        prior_q or prior_y_q
    ):
        st.markdown(
            "**Quarterly Financial Comparison**"
        )
        quarter_series = []
        for label, payload in [
            (
                "Prior Year Quarter",
                prior_y_q,
            ),
            (
                "Prior Quarter",
                prior_q,
            ),
            (
                "Latest Quarter",
                latest_q,
            ),
        ]:
            if payload:
                quarter_series.append({
                    "Period": label,
                    "Revenue": payload.get(
                        "revenue"
                    ),
                    "Gross Profit": (
                        payload.get(
                            "gross_profit"
                        )
                    ),
                    "Operating Income": (
                        payload.get(
                            "operating_income"
                        )
                    ),
                    "Net Income": (
                        payload.get(
                            "net_income"
                        )
                    ),
                })

        quarter_df = pd.DataFrame(
            quarter_series
        )
        quarter_fig = go.Figure()
        for metric in [
            "Revenue",
            "Gross Profit",
            "Operating Income",
            "Net Income",
        ]:
            quarter_fig.add_trace(
                go.Bar(
                    name=metric,
                    x=quarter_df["Period"],
                    y=quarter_df[metric],
                )
            )
        quarter_fig.update_layout(
            barmode="group",
            height=380,
            margin={
                "l": 8,
                "r": 8,
                "t": 30,
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
                "family": "IBM Plex Sans",
            },
            legend={
                "orientation": "h",
                "yanchor": "bottom",
                "y": 1.02,
                "xanchor": "left",
                "x": 0,
            },
            xaxis={
                "showgrid": False,
                "title": None,
            },
            yaxis={
                "gridcolor": (
                    "rgba(143,156,166,.12)"
                ),
                "title": None,
            },
        )
        st.plotly_chart(
            quarter_fig,
            use_container_width=True,
            config={
                "displayModeBar": False
            },
        )

    st.markdown(
        "**Cash Flow Snapshot**"
    )
    fallback_cash_flow = (
        supplemental_financials.get(
            "cash_flow",
            {},
        )
        or {}
    )
    operating_cash_flow = (
        fallback_cash_flow.get(
            "operating_cash_flow"
        )
    )
    capital_expenditure = (
        fallback_cash_flow.get(
            "capital_expenditure"
        )
    )
    free_cash_flow = (
        fallback_cash_flow.get(
            "free_cash_flow"
        )
    )
    free_cash_flow_method = (
        fallback_cash_flow.get(
            "free_cash_flow_method",
            "unavailable",
        )
    )
    cash_flow_date = (
        fallback_cash_flow.get(
            "cash_flow_as_of"
        )
        or "Latest available"
    )

    cash_flow_cols = st.columns(3)
    cash_flow_cols[0].metric(
        "Operating Cash Flow · Reported",
        format_money(
            operating_cash_flow,
            financial_currency,
        ),
    )
    cash_flow_cols[1].metric(
        "Capital Expenditure · Reported",
        format_money(
            capital_expenditure,
            financial_currency,
        ),
    )
    cash_flow_cols[2].metric(
        (
            "Free Cash Flow · Reported"
            if free_cash_flow_method
            == "reported"
            else (
                "Free Cash Flow · Calculated"
                if free_cash_flow_method
                == "calculated"
                else "Free Cash Flow"
            )
        ),
        format_money(
            free_cash_flow,
            financial_currency,
        ),
        help=(
            "Reported when Yahoo exposes a direct free-cash-flow row; "
            "otherwise calculated as operating cash flow minus capital expenditures."
        ),
    )
    st.caption(
        "Cash-flow source: Yahoo Finance statement data · "
        f"Period: {cash_flow_date}. "
        "Unavailable values remain unavailable rather than being treated as zero."
    )

    st.markdown(
        "**Balance Sheet Snapshot**"
    )
    capital_structure = (
        selected_data.get(
            "capital_structure",
            {},
        )
    )
    fallback_capital = (
        supplemental_financials.get(
            "capital_structure",
            {},
        )
    )

    structured_balance_values = [
        capital_structure.get(
            "cash_and_investments"
        ),
        capital_structure.get(
            "total_debt"
        ),
        selected_data.get("cash"),
        selected_data.get("assets"),
    ]
    use_structured_balance = any(
        value is not None
        for value in structured_balance_values
    )
    balance_record = (
        capital_structure
        if use_structured_balance
        else fallback_capital
    )
    balance_source = (
        "Structured company balance sheet"
        if use_structured_balance
        else "Yahoo Finance balance sheet"
    )
    cash_value = (
        selected_data.get("cash")
        if use_structured_balance
        else balance_record.get("cash")
    )
    cash_investments_value = (
        balance_record.get(
            "cash_and_investments"
        )
    )
    debt_value = balance_record.get(
        "total_debt"
    )
    assets_value = (
        selected_data.get("assets")
        if use_structured_balance
        else (
            balance_record.get(
                "total_assets"
            )
            or balance_record.get(
                "assets"
            )
        )
    )

    st.caption(
        "Balance sheet: "
        + str(
            balance_record.get(
                "balance_sheet_as_of"
            )
            or selected_data.get(
                "fiscal_year_end"
            )
            or "Date unavailable"
        )
        + " · "
        + balance_source
        + ". Its reporting date may differ from the income statement."
    )

    balance_cols = st.columns(4)
    balance_cols[0].metric(
        "Cash",
        format_money(cash_value, financial_currency),
    )
    balance_cols[1].metric(
        "Cash + Investments",
        format_money(
            cash_investments_value,
            financial_currency,
        ),
    )
    balance_cols[2].metric(
        "Total Debt",
        format_money(debt_value, financial_currency),
    )
    balance_cols[3].metric(
        "Total Assets",
        format_money(assets_value, financial_currency),
    )

    financial_source = (
        income_selection.get(
            "source_url"
        )
    )
    if financial_source:
        st.link_button(
            "Open source financial filing",
            financial_source,
            key=(
                "workspace_financial_source_"
                + selected_ticker
            ),
        )

    with st.expander(
        "Sources & formulas"
    ):
        source_rows = [
            {
                "Dataset": (
                    "Income statement"
                ),
                "Period / date": (
                    financial_period_label
                ),
                "Source": (
                    financial_source_label
                ),
                "Original source": (
                    financial_source
                    or "No direct filing link for this fallback source"
                ),
            },
            {
                "Dataset": (
                    "Cash flow"
                ),
                "Period / date": (
                    cash_flow_date
                ),
                "Source": (
                    "Yahoo Finance cash-flow statement"
                ),
                "Original source": (
                    "Supplemental Yahoo Finance statement"
                ),
            },
            {
                "Dataset": (
                    "Balance sheet"
                ),
                "Period / date": (
                    balance_record.get(
                        "balance_sheet_as_of"
                    )
                    or selected_data.get(
                        "fiscal_year_end"
                    )
                    or "Date unavailable"
                ),
                "Source": balance_source,
                "Original source": (
                    capital_structure.get(
                        "source_filing"
                    )
                    if use_structured_balance
                    else (
                        "Supplemental Yahoo Finance statement"
                    )
                )
                or "Source link unavailable",
            },
        ]
        st.dataframe(
            pd.DataFrame(source_rows),
            use_container_width=True,
            hide_index=True,
        )

        balance_source_url = (
            capital_structure.get(
                "source_filing"
            )
            if use_structured_balance
            else ""
        )
        source_cols = st.columns(2)
        with source_cols[0]:
            if financial_source:
                st.link_button(
                    "Open income-statement source",
                    financial_source,
                    key=(
                        "financial_provenance_income_"
                        + selected_ticker
                    ),
                    use_container_width=True,
                )
        with source_cols[1]:
            if balance_source_url:
                st.link_button(
                    "Open balance-sheet source",
                    balance_source_url,
                    key=(
                        "financial_provenance_balance_"
                        + selected_ticker
                    ),
                    use_container_width=True,
                )

        st.markdown(
            "**Calculated metrics**\n\n"
            "- Revenue growth = (current revenue − comparable prior revenue) ÷ comparable prior revenue × 100.\n"
            "- Gross margin = gross profit ÷ revenue × 100.\n"
            "- Operating margin = operating income ÷ revenue × 100.\n"
            "- Net margin = net income ÷ revenue × 100.\n"
            "- Free cash flow = operating cash flow − capital expenditures when a direct FCF row is unavailable."
        )
        st.caption(
            "EquityLens does not replace a missing reported figure with zero. "
            "Calculations are shown only when the required source values exist."
        )

    st.caption(
        "EquityLens uses standardized SEC-reported figures when available. "
        "Income statements and balance sheets each use a single source record; "
        "missing fields remain unavailable. Annual trends can use labeled Yahoo Finance fallback history. "
        "Market values and financial statement periods update on different schedules."
    )
