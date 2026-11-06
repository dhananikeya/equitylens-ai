import pandas as pd
import streamlit as st

from financial_utils import (
    calc_growth,
    calc_margin,
    format_money,
    pct,
    quarterly_metrics,
)
from market_data import (
    get_company_financial_snapshot,
    get_live_market_data,
)
from ui_components import section


def render_industry_comparison(
    industries,
    company_data,
    subgroups,
    public_market_data_enabled,
    company_quarterly,
    analysis_by_ticker,
    company_analysis,
    remember_choice,
):
    section("Peer Research", "Industry Comparison")

    selected_industry = st.selectbox(
        "Industry",
        industries,
        index=0,
        key="peer_industry",
    )

    industry_companies = [
        name for name, data in company_data.items()
        if data.get("industry", "Unclassified") == selected_industry
    ]

    subgroup_options = ["All current peers"] + [
        name for name, members in subgroups.items()
        if any(member in industry_companies for member in members)
    ]

    if st.session_state.get("peer_subgroup") not in subgroup_options:
        remember_choice("peer_subgroup", "All current peers")
    selected_subgroup = st.selectbox(
        "Sub-group",
        subgroup_options,
        index=0,
        key="peer_subgroup",
    )

    if selected_subgroup == "All current peers":
        available_companies = industry_companies
    else:
        available_companies = [
            company for company in subgroups[selected_subgroup]
            if company in industry_companies
        ]

    defaults = available_companies[:3]
    if "peer_companies" in st.session_state:
        remember_choice("peer_companies", [name for name in st.session_state["peer_companies"] if name in available_companies])
    selected_companies = st.multiselect(
        "Select companies to compare",
        available_companies,
        default=defaults,
        key="peer_companies",
    )

    if selected_subgroup != "All current peers":
        st.caption(
            f"Showing the {selected_subgroup} sub-group. "
            "More companies can be added without changing the comparison workflow."
        )

    peer_financial_cache = {}
    if selected_companies:
        with st.spinner("Loading peer financial statements from Yahoo Finance…"):
            for company in selected_companies:
                ticker = str(company_data[company].get("ticker", "")).upper()
                try:
                    peer_financial_cache[company] = get_company_financial_snapshot(ticker)
                except Exception:
                    peer_financial_cache[company] = {}

        section("Balance Sheet", "Capital Structure Snapshot")

        capital_rows = []
        for company in selected_companies:
            capital = company_data[company].get("capital_structure", {})
            supplemental = peer_financial_cache.get(company, {})
            supplemental_capital = supplemental.get("capital_structure", {})

            shares = (
                capital.get("shares_outstanding")
                if capital.get("shares_outstanding") is not None
                else supplemental_capital.get("shares_outstanding")
            )
            debt = (
                capital.get("total_debt")
                if capital.get("total_debt") is not None
                else supplemental_capital.get("total_debt")
            )
            cash_investments = (
                capital.get("cash_and_investments")
                if capital.get("cash_and_investments") is not None
                else supplemental_capital.get("cash_and_investments")
            )
            balance_date = (
                capital.get("balance_sheet_as_of")
                or supplemental_capital.get("balance_sheet_as_of")
                or "N/A"
            )
            filing_source = capital.get("source_filing", "")
            has_capital_value = any(
                value is not None
                for value in [shares, debt, cash_investments]
            )
            data_source = (
                "SEC filing"
                if filing_source
                else (
                    "Yahoo Finance supplemental"
                    if has_capital_value
                    else "Data unavailable"
                )
            )

            capital_rows.append({
                "Company": company,
                "Shares Outstanding": (
                    f"{int(shares):,}"
                    if shares is not None
                    else "N/A"
                ),
                "Debt": format_money(debt),
                "Cash + Investments": format_money(cash_investments),
                "Balance Sheet Date": balance_date,
                "Data Source": data_source,
                "Source Filing": filing_source,
            })

        st.dataframe(
            pd.DataFrame(capital_rows),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Source Filing": st.column_config.LinkColumn(
                    "Source Filing",
                    display_text="Open filing"
                )
            }
        )

    run_comparison = st.button("Run Peer Comparison", type="primary")
    comparison_signature = tuple(selected_companies)
    if run_comparison and len(selected_companies) >= 2:
        st.session_state["completed_comparison"] = comparison_signature
    if run_comparison or (len(selected_companies) >= 2 and st.session_state.get("completed_comparison") == comparison_signature):
        if len(selected_companies) < 2:
            st.warning("Select at least two companies to compare.")
        else:
            live_market = {}

            if public_market_data_enabled:
                symbols = [
                    company_data[company]["ticker"]
                    for company in selected_companies
                ]
                try:
                    with st.spinner("Loading comparison prices from Yahoo Finance…"):
                        live_market = get_live_market_data(symbols)
                except Exception as exc:
                    st.warning(
                        "Live market data is temporarily unavailable. "
                        "Filing-based research is still available."
                    )
                    st.caption(str(exc))

                section("Market", "Live Market Snapshot")
                price_cols = st.columns(len(selected_companies))
                for idx, company in enumerate(selected_companies):
                    ticker = company_data[company]["ticker"]
                    market = live_market.get(ticker, {})
                    close = market.get("close")
                    change = market.get("percent_change")

                    price = (
                        f"${float(close):,.2f}"
                        if close not in (None, "")
                        else "N/A"
                    )
                    delta = (
                        f"{float(change):.2f}%"
                        if change not in (None, "")
                        else None
                    )

                    price_cols[idx].metric(
                        ticker,
                        price,
                        delta=delta,
                        delta_color="normal"
                    )
            else:
                st.info(
                    "Public market-price data is disabled in this demo. "
                    "SEC filing analysis remains available."
                )

            section("Fundamentals", "Annual Financial Comparison")
            annual_rows = []
            for company in selected_companies:
                data = company_data[company]
                supplemental = peer_financial_cache.get(company, {})
                supplemental_latest = supplemental.get("latest", {})
                supplemental_history = supplemental.get("history", [])
                supplemental_capital = supplemental.get("capital_structure", {})

                revenue = (
                    data.get("revenue")
                    if data.get("revenue") is not None
                    else supplemental_latest.get("revenue")
                )
                gross_profit = (
                    data.get("gross_profit")
                    if data.get("gross_profit") is not None
                    else supplemental_latest.get("gross_profit")
                )
                operating_income = (
                    data.get("operating_income")
                    if data.get("operating_income") is not None
                    else supplemental_latest.get("operating_income")
                )
                net_income = (
                    data.get("net_income")
                    if data.get("net_income") is not None
                    else supplemental_latest.get("net_income")
                )
                history = data.get("history", []) or supplemental_history
                growth = None
                if len(history) >= 2:
                    growth = calc_growth(
                        history[-1].get("revenue"),
                        history[-2].get("revenue")
                    )

                annual_rows.append({
                    "Company": company,
                    "FY": data.get("fiscal_year") or supplemental_latest.get("fiscal_year"),
                    "Revenue": format_money(revenue),
                    "YoY Revenue Growth": pct(growth),
                    "Gross Margin": pct(calc_margin(gross_profit, revenue)),
                    "Operating Margin": pct(calc_margin(operating_income, revenue)),
                    "Net Margin": pct(calc_margin(net_income, revenue)),
                    "Cash + Investments": format_money(
                        data.get("capital_structure", {}).get("cash_and_investments")
                        if data.get("capital_structure", {}).get("cash_and_investments") is not None
                        else supplemental_capital.get("cash_and_investments")
                    ),
                    "Assets": format_money(
                        data.get("assets")
                        if data.get("assets") is not None
                        else supplemental_capital.get("total_assets")
                    ),
                    "Data Source": (
                        "SEC filing"
                        if data.get("filing_url")
                        else "Yahoo Finance supplemental"
                    ),
                    "SEC Filing": data.get("filing_url", "")
                })

            st.dataframe(
                pd.DataFrame(annual_rows),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "SEC Filing": st.column_config.LinkColumn(
                        "SEC Filing",
                        display_text="Open 10-K"
                    )
                }
            )

            section("Earnings", "Quarterly & LTM Analysis")
            quarter_rows = []
            ltm_rows = []

            for company in selected_companies:
                qdata = company_quarterly.get(company, {})
                supplemental_quarters = peer_financial_cache.get(
                    company, {}
                ).get("quarterly_history", [])

                if qdata.get("latest_quarter"):
                    latest = qdata.get("latest_quarter", {})
                    ltm = qdata.get("ltm", {})
                    qm = quarterly_metrics(qdata)
                    quarter_label = qdata.get("quarter_label", "Latest quarter")
                    quarter_source = "SEC filing"
                    quarter_filing = qdata.get("source_filing", "")
                else:
                    latest = supplemental_quarters[-1] if supplemental_quarters else {}
                    prior_q = supplemental_quarters[-2] if len(supplemental_quarters) >= 2 else {}
                    prior_y = supplemental_quarters[-5] if len(supplemental_quarters) >= 5 else {}
                    fallback_qdata = {
                        "latest_quarter": latest,
                        "prior_quarter": prior_q,
                        "prior_year_quarter": prior_y,
                    }
                    qm = quarterly_metrics(fallback_qdata)
                    quarter_label = latest.get("period_end", "N/A")
                    quarter_source = "Yahoo Finance supplemental"
                    quarter_filing = ""

                    trailing = supplemental_quarters[-4:]
                    ltm = {}
                    if trailing:
                        for field in [
                            "revenue",
                            "gross_profit",
                            "operating_income",
                            "net_income",
                        ]:
                            values = [
                                row.get(field)
                                for row in trailing
                                if row.get(field) is not None
                            ]
                            ltm[field] = sum(values) if values else None

                quarter_rows.append({
                    "Company": company,
                    "Quarter": quarter_label,
                    "Revenue": format_money(qm["revenue"]),
                    "YoY Growth": pct(qm["yoy_growth"]),
                    "QoQ Growth": pct(qm["qoq_growth"]),
                    "Gross Margin": pct(qm["gross_margin"]),
                    "Operating Margin": pct(qm["operating_margin"]),
                    "Net Income": format_money(latest.get("net_income")),
                    "Data Source": quarter_source,
                    "SEC Filing": quarter_filing,
                })

                ltm_revenue = ltm.get("revenue")
                ltm_rows.append({
                    "Company": company,
                    "LTM Revenue": format_money(ltm_revenue),
                    "LTM Gross Margin": pct(calc_margin(ltm.get("gross_profit"), ltm_revenue)),
                    "LTM Operating Margin": pct(calc_margin(ltm.get("operating_income"), ltm_revenue)),
                    "LTM Net Income": format_money(ltm.get("net_income")),
                    "LTM Net Margin": pct(calc_margin(ltm.get("net_income"), ltm_revenue)),
                    "Data Source": quarter_source,
                })

            st.markdown("**Latest Quarter**")
            st.dataframe(
                pd.DataFrame(quarter_rows),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "SEC Filing": st.column_config.LinkColumn(
                        "SEC Filing",
                        display_text="Open 10-Q"
                    )
                }
            )

            st.markdown("**Trailing Twelve Months**")
            st.dataframe(
                pd.DataFrame(ltm_rows),
                use_container_width=True,
                hide_index=True
            )

            section("Trend", "Three-Year Revenue")
            st.caption(
                "Use this view to compare the direction and pace of reported revenue growth. "
                "Fiscal years may end on different dates, so the chart is best read as a company-reported annual trend rather than a same-calendar-period comparison."
            )

            revenue_rows = []
            for company in selected_companies:
                history = company_data[company].get("history", [])
                if not history:
                    history = peer_financial_cache.get(company, {}).get("history", [])
                for item in history:
                    revenue_rows.append({
                        "Company": company,
                        "Fiscal Year": str(item.get("fiscal_year")),
                        "Revenue": item.get("revenue")
                    })
            revenue_df = pd.DataFrame(revenue_rows)
            if not revenue_df.empty:
                st.line_chart(
                    revenue_df.pivot(
                        index="Fiscal Year",
                        columns="Company",
                        values="Revenue"
                    )
                )

                st.markdown("**Trend context**")
                trend_rows = []
                for company in selected_companies:
                    history = company_data[company].get("history", [])
                    if not history:
                        history = peer_financial_cache.get(company, {}).get("history", [])
                    if not history:
                        continue

                    first = history[0]
                    latest_hist = history[-1]
                    prior_hist = history[-2] if len(history) >= 2 else None

                    start_revenue = first.get("revenue")
                    latest_revenue = latest_hist.get("revenue")
                    latest_growth = (
                        calc_growth(latest_revenue, prior_hist.get("revenue"))
                        if prior_hist else None
                    )
                    total_change = calc_growth(latest_revenue, start_revenue)

                    periods = max(len(history) - 1, 0)
                    cagr = None
                    if (
                        periods > 0
                        and start_revenue not in (None, 0)
                        and latest_revenue is not None
                        and start_revenue > 0
                        and latest_revenue > 0
                    ):
                        cagr = (
                            (latest_revenue / start_revenue) ** (1 / periods) - 1
                        ) * 100

                    start_margin = calc_margin(
                        first.get("operating_income"),
                        start_revenue
                    )
                    latest_margin = calc_margin(
                        latest_hist.get("operating_income"),
                        latest_revenue
                    )
                    margin_change = (
                        latest_margin - start_margin
                        if latest_margin is not None and start_margin is not None
                        else None
                    )

                    trend_rows.append({
                        "Company": company,
                        "Latest FY": latest_hist.get("fiscal_year"),
                        "Latest Revenue": format_money(latest_revenue),
                        "Latest YoY Growth": pct(latest_growth),
                        "Multi-Year Revenue Change": pct(total_change),
                        "Annualized Growth": pct(cagr),
                        "Operating Margin Change": (
                            f"{margin_change:+.1f} pts"
                            if margin_change is not None else "N/A"
                        )
                    })

                st.dataframe(
                    pd.DataFrame(trend_rows),
                    use_container_width=True,
                    hide_index=True
                )

                st.markdown("**How to read this**")
                st.write(
                    "The chart shows absolute revenue over time, while the table separates growth rate from company size. "
                    "Latest YoY Growth measures the change from the prior reported fiscal year. "
                    "Multi-Year Revenue Change measures the total change from the first year shown to the latest year. "
                    "Annualized Growth converts that multi-year change into an average annual rate. "
                    "Operating Margin Change shows how many percentage points reported operating margin moved over the same period."
                )

            section("Research Context", "Business Model & Risk Comparison")
            st.caption(
                "Company-specific deep dives now live in Company Research. "
                "Industry Comparison keeps only the fields that are useful side by side."
            )

            qualitative_rows = []
            for company in selected_companies:
                ticker = str(
                    company_data.get(company, {}).get("ticker", "")
                ).upper()
                analysis = analysis_by_ticker.get(
                    ticker,
                    company_analysis.get(company, {}),
                )
                themes = analysis.get("key_risk_themes", [])
                qualitative_rows.append({
                    "Company": company.split(" (")[0],
                    "Ticker": ticker,
                    "Business Model": analysis.get(
                        "business_model",
                        "Research pending",
                    ),
                    "Primary Revenue Source": analysis.get(
                        "primary_revenue_source",
                        "Research pending",
                    ),
                    "Competitive Risk": analysis.get(
                        "competitive_risk",
                        "Research pending",
                    ),
                    "Operational Risk": analysis.get(
                        "operational_risk",
                        "Research pending",
                    ),
                    "Key Risk Themes": (
                        ", ".join(themes[:5])
                        if themes
                        else "Research pending"
                    ),
                })

            if qualitative_rows:
                st.dataframe(
                    pd.DataFrame(qualitative_rows),
                    use_container_width=True,
                    hide_index=True,
                )

            st.caption(
                "Use Company Research for the full filing-linked business model, ownership, "
                "financials, analyst context, and source documents for an individual company."
            )

