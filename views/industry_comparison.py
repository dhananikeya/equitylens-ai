from datetime import datetime, timezone

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from financial_utils import (
    calc_growth,
    calc_margin,
    format_money,
    pct,
    quarterly_metrics,
    safe_float,
)
from models.context import IndustryComparisonContext
from market_data import (
    get_company_financial_snapshot,
    get_live_market_data,
)
from ui_components import loading_panel, render_refresh_indicator, section


def _annual_snapshot(company, company_data, supplemental):
    data = company_data[company]
    fallback_latest = supplemental.get("latest", {})
    fallback_history = supplemental.get("history", [])

    revenue = (
        data.get("revenue")
        if data.get("revenue") is not None
        else fallback_latest.get("revenue")
    )
    gross_profit = (
        data.get("gross_profit")
        if data.get("gross_profit") is not None
        else fallback_latest.get("gross_profit")
    )
    operating_income = (
        data.get("operating_income")
        if data.get("operating_income") is not None
        else fallback_latest.get("operating_income")
    )
    net_income = (
        data.get("net_income")
        if data.get("net_income") is not None
        else fallback_latest.get("net_income")
    )
    history = data.get("history", []) or fallback_history

    growth = None
    if len(history) >= 2:
        growth = calc_growth(
            history[-1].get("revenue"),
            history[-2].get("revenue"),
        )

    return {
        "revenue": revenue,
        "gross_profit": gross_profit,
        "operating_income": operating_income,
        "net_income": net_income,
        "growth": growth,
        "gross_margin": calc_margin(gross_profit, revenue),
        "operating_margin": calc_margin(operating_income, revenue),
        "net_margin": calc_margin(net_income, revenue),
        "fiscal_year": (
            data.get("fiscal_year")
            or fallback_latest.get("fiscal_year")
        ),
        "history": history,
        "source": (
            str(
                data.get(
                    "source",
                    "SEC filing",
                )
            )
            if data.get("filing_url")
            else "Yahoo Finance supplemental"
        ),
        "source_url": data.get("filing_url", ""),
    }


def _quarter_snapshot(company, company_quarterly, supplemental):
    qdata = company_quarterly.get(company, {})
    fallback_quarters = supplemental.get("quarterly_history", [])

    if qdata.get("latest_quarter"):
        latest = qdata.get("latest_quarter", {})
        metrics = quarterly_metrics(qdata)
        return {
            "period": (
                qdata.get("quarter_label")
                or qdata.get("period_end")
                or "Latest quarter"
            ),
            "revenue": metrics.get("revenue"),
            "yoy_growth": metrics.get("yoy_growth"),
            "qoq_growth": metrics.get("qoq_growth"),
            "gross_margin": metrics.get("gross_margin"),
            "operating_margin": metrics.get("operating_margin"),
            "net_income": latest.get("net_income"),
            "source": "SEC filing",
            "source_url": qdata.get("source_filing", ""),
        }

    latest = fallback_quarters[-1] if fallback_quarters else {}
    prior_q = (
        fallback_quarters[-2]
        if len(fallback_quarters) >= 2
        else {}
    )
    prior_y = (
        fallback_quarters[-5]
        if len(fallback_quarters) >= 5
        else {}
    )
    metrics = quarterly_metrics({
        "latest_quarter": latest,
        "prior_quarter": prior_q,
        "prior_year_quarter": prior_y,
    })
    return {
        "period": latest.get("period_end", "N/A"),
        "revenue": metrics.get("revenue"),
        "yoy_growth": metrics.get("yoy_growth"),
        "qoq_growth": metrics.get("qoq_growth"),
        "gross_margin": metrics.get("gross_margin"),
        "operating_margin": metrics.get("operating_margin"),
        "net_income": latest.get("net_income"),
        "source": (
            "Yahoo Finance supplemental"
            if latest
            else "Data unavailable"
        ),
        "source_url": "",
    }


def _needs_peer_supplemental(
    company,
    company_data,
    company_quarterly,
):
    data = company_data.get(
        company,
        {},
    )
    qdata = company_quarterly.get(
        company,
        {},
    )
    structured = (
        data.get(
            "capital_structure",
            {},
        )
        or {}
    )

    annual_missing = (
        data.get("revenue") is None
        or data.get("operating_income")
        is None
        or not data.get("history")
    )
    quarterly_missing = not bool(
        qdata.get(
            "latest_quarter"
        )
    )
    balance_missing = any(
        value is None
        for value in [
            structured.get(
                "shares_outstanding"
            ),
            structured.get(
                "total_debt"
            ),
            structured.get(
                "cash_and_investments"
            ),
            data.get("assets"),
        ]
    )
    return (
        annual_missing
        or quarterly_missing
        or balance_missing
    )


def render_industry_comparison(
    context: IndustryComparisonContext,
):
    industries = context.industries
    company_data = context.company_data
    subgroups = context.subgroups
    public_market_data_enabled = (
        context.public_market_data_enabled
    )
    company_quarterly = context.company_quarterly
    analysis_by_ticker = context.analysis_by_ticker
    company_analysis = context.company_analysis
    research_coverage = context.research_coverage
    remember_choice = context.remember_choice
    company_universe = context.company_universe
    research_link = context.research_link
    section("Peer Research", "Industry Comparison")
    st.caption(
        "Compare 2–6 companies using clearly labeled periods and sources. "
        "Fiscal calendars can differ, so EquityLens shows the reported period instead of pretending every row is perfectly synchronized."
    )

    industry_cols = st.columns(2)
    with industry_cols[0]:
        selected_industry = st.selectbox(
            "Primary industry",
            industries,
            index=0,
            key="peer_industry",
        )

    secondary_options = [
        "No second industry"
    ] + [
        industry
        for industry in industries
        if industry != selected_industry
    ]
    current_secondary = (
        st.session_state.get(
            "peer_secondary_industry",
            "No second industry",
        )
    )
    if current_secondary not in secondary_options:
        remember_choice(
            "peer_secondary_industry",
            "No second industry",
        )

    with industry_cols[1]:
        secondary_industry = st.selectbox(
            "Optional second industry",
            secondary_options,
            key="peer_secondary_industry",
            help=(
                "Use this for cross-industry comparisons. "
                "Curated subgroups are available only for a single industry."
            ),
        )

    selected_industries = [
        selected_industry
    ]
    if (
        secondary_industry
        != "No second industry"
    ):
        selected_industries.append(
            secondary_industry
        )

    industry_companies = sorted([
        name
        for name, data in company_data.items()
        if data.get(
            "industry",
            "Unclassified",
        )
        in selected_industries
    ])

    curated_sets = {
        name: [
            company
            for company in members
            if company in industry_companies
        ]
        for name, members in subgroups.items()
    }
    curated_sets = {
        name: members
        for name, members in curated_sets.items()
        if len(members) >= 2
    }

    peer_set_options = (
        ["Full industry selection"]
        if len(
            selected_industries
        )
        > 1
        else (
            ["Full industry"]
            + [
                f"Curated · {name}"
                for name in sorted(
                    curated_sets
                )
            ]
        )
    )
    current_peer_set = st.session_state.get(
        "peer_subgroup",
        peer_set_options[0],
    )
    if current_peer_set not in peer_set_options:
        remember_choice(
            "peer_subgroup",
            peer_set_options[0],
        )

    selected_peer_set = st.selectbox(
        "Peer set",
        peer_set_options,
        key="peer_subgroup",
        help=(
            "Full industry uses the EquityLens industry classification. "
            "Curated sets are optional legacy research groups and are labeled explicitly."
        ),
    )

    if selected_peer_set in {
        "Full industry",
        "Full industry selection",
    }:
        available_companies = industry_companies
    else:
        curated_name = selected_peer_set.replace(
            "Curated · ",
            "",
            1,
        )
        available_companies = curated_sets.get(
            curated_name,
            industry_companies,
        )

    universe_market_cap = {
        str(
            row.get(
                "Ticker",
                "",
            )
        ).upper(): (
            safe_float(
                row.get(
                    "Market Cap"
                )
            )
            or 0
        )
        for _, row in (
            company_universe.iterrows()
        )
    }
    available_companies = sorted(
        available_companies,
        key=lambda company: (
            -universe_market_cap.get(
                str(
                    company_data[
                        company
                    ].get(
                        "ticker",
                        "",
                    )
                ).upper(),
                0,
            ),
            company.lower(),
        ),
    )

    candidate_rows = []
    for company in (
        available_companies[:20]
    ):
        ticker = str(
            company_data[
                company
            ].get(
                "ticker",
                "",
            )
        ).upper()
        coverage = (
            research_coverage.get(
                "companies",
                {},
            ).get(
                ticker,
                {},
            )
            or {}
        )
        candidate_rows.append({
            "Company": (
                company.split(
                    " ("
                )[0]
            ),
            "Ticker": ticker,
            "Industry": (
                company_data[
                    company
                ].get(
                    "industry",
                    "Unclassified",
                )
            ),
            "Market Cap": (
                universe_market_cap.get(
                    ticker
                )
            ),
            "Research %": int(
                coverage.get(
                    "completeness_percent",
                    0,
                )
                or 0
            ),
        })

    with st.expander(
        "Top peer candidates · by market cap",
        expanded=False,
    ):
        st.dataframe(
            pd.DataFrame(
                candidate_rows
            ),
            use_container_width=True,
            hide_index=True,
        )
        st.caption(
            "Candidate ranking is a navigation aid, not an investment ranking."
        )

    existing_selection = st.session_state.get(
        "peer_companies",
        [],
    )
    valid_existing = [
        company
        for company in existing_selection
        if company in available_companies
    ]
    if existing_selection != valid_existing:
        remember_choice(
            "peer_companies",
            valid_existing,
        )

    defaults = available_companies[:3]
    selected_companies = st.multiselect(
        "Companies to compare",
        available_companies,
        default=(
            valid_existing
            if valid_existing
            else defaults
        ),
        key="peer_companies",
        help="Use 2–6 companies for a readable comparison.",
    )

    if len(selected_companies) > 6:
        st.warning(
            "Select no more than six companies so the comparison remains readable."
        )
        return

    if len(selected_companies) < 2:
        st.info(
            "Select at least two companies to start a peer comparison."
        )
        return

    selection_summary = " · ".join(
        str(company_data[name].get("ticker", "")).upper()
        for name in selected_companies
    )
    st.caption(
        "Industries: "
        + " + ".join(
            selected_industries
        )
        + f" · Selected: {selection_summary} · {len(selected_companies)} companies"
    )

    compare_button = st.button(
        "Load comparison",
        type="primary",
        use_container_width=True,
    )
    signature = (
        tuple(
            selected_industries
        ),
        selected_peer_set,
        tuple(selected_companies),
    )
    comparison_snapshot_key = "peer_financial_snapshot"
    if compare_button:
        st.session_state["completed_comparison"] = signature
        st.session_state.pop(comparison_snapshot_key, None)

    if st.session_state.get("completed_comparison") != signature:
        st.info(
            "Load the comparison when your peer set is ready. "
            "This prevents supplemental market requests from running while you are still changing selections."
        )
        return

    comparison_snapshot = st.session_state.get(comparison_snapshot_key)
    if (
        not isinstance(comparison_snapshot, dict)
        or comparison_snapshot.get("signature") != signature
    ):
        peer_financial_cache = {}
        with loading_panel(
            "Loading peer financial statements",
            "Retrieving supplemental statements for the selected comparison set."
        ):
            for company in selected_companies:
                if not _needs_peer_supplemental(
                    company,
                    company_data,
                    company_quarterly,
                ):
                    peer_financial_cache[
                        company
                    ] = {}
                    continue

                ticker = str(
                    company_data[company].get("ticker", "")
                ).upper()
                try:
                    peer_financial_cache[company] = (
                        get_company_financial_snapshot(ticker)
                    )
                except Exception:
                    peer_financial_cache[company] = {}

        annual_by_company = {
            company: _annual_snapshot(
                company,
                company_data,
                peer_financial_cache.get(company, {}),
            )
            for company in selected_companies
        }
        quarter_by_company = {
            company: _quarter_snapshot(
                company,
                company_quarterly,
                peer_financial_cache.get(company, {}),
            )
            for company in selected_companies
        }
        comparison_snapshot = {
            "signature": signature,
            "financials": peer_financial_cache,
            "annual": annual_by_company,
            "quarterly": quarter_by_company,
            "loaded_at_utc": datetime.now(timezone.utc).isoformat(),
        }
        st.session_state[comparison_snapshot_key] = comparison_snapshot
    else:
        peer_financial_cache = comparison_snapshot.get(
            "financials",
            {},
        )
        annual_by_company = comparison_snapshot.get(
            "annual",
            {},
        )
        quarter_by_company = comparison_snapshot.get(
            "quarterly",
            {},
        )

    if not annual_by_company:
        annual_by_company = {
            company: _annual_snapshot(
                company,
                company_data,
                peer_financial_cache.get(company, {}),
            )
            for company in selected_companies
        }
    if not quarter_by_company:
        quarter_by_company = {
            company: _quarter_snapshot(
                company,
                company_quarterly,
                peer_financial_cache.get(company, {}),
            )
            for company in selected_companies
        }

    render_refresh_indicator(
        "Comparison loaded",
        comparison_snapshot.get("loaded_at_utc"),
        "supplemental peer data",
    )

    fiscal_years = {
        str(
            annual_by_company[
                company
            ].get(
                "fiscal_year",
                "",
            )
        )
        for company in selected_companies
        if annual_by_company[
            company
        ].get(
            "fiscal_year"
        )
        is not None
    }
    if len(fiscal_years) > 1:
        st.warning(
            "Selected peers report different fiscal years. "
            "Use the Reported FY and source columns when comparing annual figures."
        )

    comparison_focus = st.radio(
        "Comparison view",
        [
            "Overview",
            "Growth & Margins",
            "Quarterly",
            "Balance Sheet",
            "Business & Risks",
        ],
        horizontal=True,
        key="peer_comparison_focus",
    )

    universe_by_ticker = {
        str(row.get("Ticker", "")).upper(): row
        for _, row in company_universe.iterrows()
    }

    export_rows = []
    for company in selected_companies:
        ticker = str(
            company_data[
                company
            ].get(
                "ticker",
                "",
            )
        ).upper()
        annual = annual_by_company[
            company
        ]
        quarter = quarter_by_company[
            company
        ]
        universe_row = (
            universe_by_ticker.get(
                ticker,
                {},
            )
        )
        coverage = (
            research_coverage.get(
                "companies",
                {},
            ).get(
                ticker,
                {},
            )
            or {}
        )
        export_rows.append({
            "Company": (
                company.split(
                    " ("
                )[0]
            ),
            "Ticker": ticker,
            "Industry": (
                company_data[
                    company
                ].get(
                    "industry",
                    "",
                )
            ),
            "Fiscal Year": annual.get(
                "fiscal_year"
            ),
            "Annual Revenue": annual.get(
                "revenue"
            ),
            "Annual Revenue Growth %": annual.get(
                "growth"
            ),
            "Gross Margin %": annual.get(
                "gross_margin"
            ),
            "Operating Margin %": annual.get(
                "operating_margin"
            ),
            "Net Margin %": annual.get(
                "net_margin"
            ),
            "Quarter": quarter.get(
                "period"
            ),
            "Quarter Revenue": quarter.get(
                "revenue"
            ),
            "Quarter YoY Growth %": quarter.get(
                "yoy_growth"
            ),
            "Quarter QoQ Growth %": quarter.get(
                "qoq_growth"
            ),
            "Market Cap": safe_float(
                universe_row.get(
                    "Market Cap"
                )
            ),
            "SEC Reporting": (
                universe_row.get(
                    "Reporting Regime",
                    "",
                )
            ),
            "Research Completeness %": int(
                coverage.get(
                    "completeness_percent",
                    0,
                )
                or 0
            ),
            "Annual Source": annual.get(
                "source"
            ),
            "Annual Filing": annual.get(
                "source_url"
            ),
            "Quarter Source": quarter.get(
                "source"
            ),
            "Quarter Filing": quarter.get(
                "source_url"
            ),
        })

    export_df = pd.DataFrame(
        export_rows
    )
    st.download_button(
        "Download comparison data (CSV)",
        data=export_df.to_csv(
            index=False
        ).encode("utf-8"),
        file_name=(
            "EquityLens_peer_comparison_"
            + "_".join(
                str(
                    company_data[
                        company
                    ].get(
                        "ticker",
                        "",
                    )
                ).upper()
                for company
                in selected_companies
            )
            + ".csv"
        ),
        mime="text/csv",
        key=(
            "peer_comparison_csv_"
            + str(
                abs(
                    hash(signature)
                )
            )
        ),
        use_container_width=True,
    )

    if comparison_focus == "Overview":
        section(
            "Overview",
            "Who Is Growing, Profitable & Large?",
        )

        overview_rows = []
        for company in selected_companies:
            ticker = str(
                company_data[company].get("ticker", "")
            ).upper()
            annual = annual_by_company[company]
            universe_row = universe_by_ticker.get(ticker, {})
            overview_rows.append({
                "Company": company.split(" (")[0],
                "Ticker": ticker,
                "Reported FY": annual.get("fiscal_year"),
                "Revenue": annual.get("revenue"),
                "YoY Revenue Growth": annual.get("growth"),
                "Operating Margin": annual.get(
                    "operating_margin"
                ),
                "Net Margin": annual.get("net_margin"),
                "Market Cap": safe_float(
                    universe_row.get("Market Cap")
                ),
                "SEC Reporting": (
                    universe_row.get(
                        "Reporting Regime",
                        "",
                    )
                ),
                "Research %": int(
                    (
                        research_coverage.get(
                            "companies",
                            {},
                        ).get(
                            ticker,
                            {},
                        )
                        or {}
                    ).get(
                        "completeness_percent",
                        0,
                    )
                    or 0
                ),
                "Research Status": (
                    (
                        research_coverage.get(
                            "companies",
                            {},
                        ).get(
                            ticker,
                            {},
                        )
                        or {}
                    ).get(
                        "completion_status",
                        "Coverage unavailable",
                    )
                ),
                "Data Source": annual.get("source"),
                "SEC Filing": annual.get("source_url"),
            })

        overview_df = pd.DataFrame(overview_rows)

        question_cols = st.columns(4)
        ranking_specs = [
            ("Fastest growth", "YoY Revenue Growth", "percent"),
            ("Highest op. margin", "Operating Margin", "percent"),
            ("Largest revenue", "Revenue", "money"),
            ("Largest market cap", "Market Cap", "money"),
        ]
        for col, (label, field, mode) in zip(
            question_cols,
            ranking_specs,
        ):
            valid = overview_df.dropna(subset=[field])
            if valid.empty:
                col.metric(label, "N/A")
                continue
            winner = valid.sort_values(
                field,
                ascending=False,
            ).iloc[0]
            value = winner[field]
            display_value = (
                pct(value)
                if mode == "percent"
                else format_money(value)
            )
            col.metric(
                label,
                str(winner["Ticker"]),
                display_value,
                delta_color="off",
            )

        display_overview = overview_df.copy()
        display_overview["Revenue"] = (
            display_overview["Revenue"].map(format_money)
        )
        display_overview["YoY Revenue Growth"] = (
            display_overview["YoY Revenue Growth"].map(pct)
        )
        display_overview["Operating Margin"] = (
            display_overview["Operating Margin"].map(pct)
        )
        display_overview["Net Margin"] = (
            display_overview["Net Margin"].map(pct)
        )
        display_overview["Market Cap"] = (
            display_overview["Market Cap"].map(format_money)
        )

        st.dataframe(
            display_overview,
            use_container_width=True,
            hide_index=True,
            column_config={
                "SEC Filing": st.column_config.LinkColumn(
                    "SEC Filing",
                    display_text="Open source",
                )
            },
        )
        st.caption(
            "Rankings above use only the displayed metric. EquityLens does not combine these metrics into an investment score."
        )

        if public_market_data_enabled:
            tickers = [
                str(
                    company_data[name].get(
                        "ticker",
                        "",
                    )
                ).upper()
                for name in selected_companies
            ]
            try:
                live_market = get_live_market_data(
                    tickers
                )
            except Exception:
                live_market = {}

            if live_market:
                st.markdown(
                    "**Market snapshot · may be delayed**"
                )
                market_cols = st.columns(
                    len(selected_companies)
                )
                for col, company in zip(
                    market_cols,
                    selected_companies,
                ):
                    ticker = str(
                        company_data[company].get(
                            "ticker",
                            "",
                        )
                    ).upper()
                    quote = live_market.get(ticker, {})
                    close = quote.get("close")
                    change = quote.get(
                        "percent_change"
                    )
                    col.metric(
                        ticker,
                        (
                            "$" + f"{close:,.2f}"
                            if close is not None
                            else "N/A"
                        ),
                        (
                            f"{change:+.2f}%"
                            if change is not None
                            else None
                        ),
                    )

    if comparison_focus == "Growth & Margins":
        section(
            "Growth & Margins",
            "Compare Pace of Growth & Operating Economics",
        )

        metric_rows = []
        for company in selected_companies:
            ticker = str(
                company_data[company].get(
                    "ticker",
                    "",
                )
            ).upper()
            annual = annual_by_company[company]
            metric_rows.append({
                "Company": company.split(" (")[0],
                "Ticker": ticker,
                "Fiscal Year": annual.get(
                    "fiscal_year"
                ),
                "Revenue": annual.get("revenue"),
                "Revenue Growth": annual.get(
                    "growth"
                ),
                "Gross Margin": annual.get(
                    "gross_margin"
                ),
                "Operating Margin": annual.get(
                    "operating_margin"
                ),
                "Net Margin": annual.get(
                    "net_margin"
                ),
                "Source": annual.get("source"),
                "SEC Filing": annual.get(
                    "source_url"
                ),
            })

        metric_df = pd.DataFrame(metric_rows)
        chart_cols = st.columns(2)

        with chart_cols[0]:
            growth_chart = metric_df.dropna(
                subset=["Revenue Growth"]
            )
            if not growth_chart.empty:
                fig = go.Figure(
                    go.Bar(
                        x=growth_chart["Ticker"],
                        y=growth_chart[
                            "Revenue Growth"
                        ],
                        text=[
                            pct(value)
                            for value in growth_chart[
                                "Revenue Growth"
                            ]
                        ],
                        textposition="auto",
                    )
                )
                fig.update_layout(
                    title="Latest reported annual revenue growth",
                    height=360,
                    margin={
                        "l": 10,
                        "r": 10,
                        "t": 55,
                        "b": 10,
                    },
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font={"color": "#8F9CA6"},
                    yaxis_title="Percent",
                )
                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    config={"displayModeBar": False},
                )
            else:
                st.info(
                    "Comparable annual revenue growth is unavailable for this peer set."
                )

        with chart_cols[1]:
            margin_chart = metric_df.dropna(
                subset=["Operating Margin"]
            )
            if not margin_chart.empty:
                fig = go.Figure(
                    go.Bar(
                        x=margin_chart["Ticker"],
                        y=margin_chart[
                            "Operating Margin"
                        ],
                        text=[
                            pct(value)
                            for value in margin_chart[
                                "Operating Margin"
                            ]
                        ],
                        textposition="auto",
                    )
                )
                fig.update_layout(
                    title="Latest reported operating margin",
                    height=360,
                    margin={
                        "l": 10,
                        "r": 10,
                        "t": 55,
                        "b": 10,
                    },
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font={"color": "#8F9CA6"},
                    yaxis_title="Percent",
                )
                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    config={"displayModeBar": False},
                )
            else:
                st.info(
                    "Comparable operating margin is unavailable for this peer set."
                )

        display_metrics = metric_df.copy()
        for field in [
            "Revenue Growth",
            "Gross Margin",
            "Operating Margin",
            "Net Margin",
        ]:
            display_metrics[field] = (
                display_metrics[field].map(pct)
            )
        display_metrics["Revenue"] = (
            display_metrics["Revenue"].map(
                format_money
            )
        )
        st.dataframe(
            display_metrics,
            use_container_width=True,
            hide_index=True,
            column_config={
                "SEC Filing": st.column_config.LinkColumn(
                    "SEC Filing",
                    display_text="Open source",
                )
            },
        )
        st.caption(
            "Fiscal years can end on different dates. Compare the displayed fiscal-year labels before drawing conclusions."
        )

    if comparison_focus == "Quarterly":
        section(
            "Quarterly",
            "Latest Quarter & Comparable Growth",
        )
        rows = []
        for company in selected_companies:
            ticker = str(
                company_data[company].get(
                    "ticker",
                    "",
                )
            ).upper()
            q = quarter_by_company[company]
            rows.append({
                "Company": company.split(" (")[0],
                "Ticker": ticker,
                "Quarter / Period": q.get("period"),
                "Revenue": format_money(
                    q.get("revenue")
                ),
                "YoY Growth": pct(
                    q.get("yoy_growth")
                ),
                "QoQ Growth": pct(
                    q.get("qoq_growth")
                ),
                "Gross Margin": pct(
                    q.get("gross_margin")
                ),
                "Operating Margin": pct(
                    q.get("operating_margin")
                ),
                "Net Income": format_money(
                    q.get("net_income")
                ),
                "Data Source": q.get("source"),
                "SEC Filing": q.get("source_url"),
            })

        st.dataframe(
            pd.DataFrame(rows),
            use_container_width=True,
            hide_index=True,
            column_config={
                "SEC Filing": st.column_config.LinkColumn(
                    "SEC Filing",
                    display_text="Open source",
                )
            },
        )
        st.caption(
            "Quarterly YoY compares with the same quarter one year earlier when available. "
            "QoQ compares with the immediately prior quarter."
        )

    if comparison_focus == "Balance Sheet":
        section(
            "Balance Sheet",
            "Liquidity & Capital Structure",
        )
        rows = []
        for company in selected_companies:
            data = company_data[company]
            structured = data.get(
                "capital_structure",
                {},
            )
            supplemental = peer_financial_cache.get(
                company,
                {},
            ).get("capital_structure", {})

            structured_values = {
                "shares_outstanding": (
                    structured.get(
                        "shares_outstanding"
                    )
                ),
                "total_debt": (
                    structured.get(
                        "total_debt"
                    )
                ),
                "cash_and_investments": (
                    structured.get(
                        "cash_and_investments"
                    )
                ),
                "assets": data.get(
                    "assets"
                ),
            }
            supplemental_values = {
                "shares_outstanding": (
                    supplemental.get(
                        "shares_outstanding"
                    )
                ),
                "total_debt": (
                    supplemental.get(
                        "total_debt"
                    )
                ),
                "cash_and_investments": (
                    supplemental.get(
                        "cash_and_investments"
                    )
                ),
                "assets": (
                    supplemental.get(
                        "total_assets"
                    )
                    or supplemental.get(
                        "assets"
                    )
                ),
            }

            merged_values = {
                key: (
                    value
                    if value is not None
                    else supplemental_values.get(
                        key
                    )
                )
                for key, value in (
                    structured_values.items()
                )
            }
            used_structured = any(
                value is not None
                for value in (
                    structured_values.values()
                )
            )
            used_supplemental = any(
                (
                    structured_values.get(
                        key
                    )
                    is None
                    and supplemental_values.get(
                        key
                    )
                    is not None
                )
                for key in merged_values
            )

            shares = merged_values[
                "shares_outstanding"
            ]
            debt = merged_values[
                "total_debt"
            ]
            cash_investments = (
                merged_values[
                    "cash_and_investments"
                ]
            )
            assets = merged_values[
                "assets"
            ]
            rows.append({
                "Company": company.split(" (")[0],
                "Ticker": str(
                    data.get("ticker", "")
                ).upper(),
                "Shares Outstanding": (
                    f"{int(shares):,}"
                    if shares is not None
                    else "N/A"
                ),
                "Debt": format_money(debt),
                "Cash + Investments": (
                    format_money(
                        cash_investments
                    )
                ),
                "Assets": format_money(assets),
                "Balance Sheet Date": (
                    structured.get(
                        "balance_sheet_as_of"
                    )
                    or supplemental.get(
                        "balance_sheet_as_of"
                    )
                    or data.get(
                        "fiscal_year_end"
                    )
                    or "N/A"
                ),
                "Source": (
                    "SEC filing + Yahoo supplemental"
                    if (
                        used_structured
                        and used_supplemental
                    )
                    else (
                        "SEC filing"
                        if used_structured
                        else "Yahoo Finance supplemental"
                    )
                ),
                "SEC Filing": (
                    structured.get(
                        "source_filing",
                        "",
                    )
                ),
            })

        st.dataframe(
            pd.DataFrame(rows),
            use_container_width=True,
            hide_index=True,
            column_config={
                "SEC Filing": st.column_config.LinkColumn(
                    "SEC Filing",
                    display_text="Open source",
                )
            },
        )

    if comparison_focus == "Business & Risks":
        section(
            "Business & Risks",
            "Compare How the Companies Make Money & What They Disclose",
        )
        st.caption(
            "Qualitative fields are EquityLens research summaries based on available disclosures. "
            "They are not scores or recommendations."
        )

        qualitative_rows = []
        for company in selected_companies:
            ticker = str(
                company_data.get(
                    company,
                    {},
                ).get("ticker", "")
            ).upper()
            analysis = analysis_by_ticker.get(
                ticker,
                company_analysis.get(
                    company,
                    {},
                ),
            )
            themes = analysis.get(
                "key_risk_themes",
                [],
            )
            qualitative_rows.append({
                "Company": company.split(" (")[0],
                "Ticker": ticker,
                "Business Model": analysis.get(
                    "business_model",
                    "Research pending",
                ),
                "Revenue Source": analysis.get(
                    "primary_revenue_source",
                    "Research pending",
                ),
                "Customer Type": analysis.get(
                    "customer_type",
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
                "Source Filing": analysis.get(
                    "source_filing",
                    "",
                ),
            })

        st.dataframe(
            pd.DataFrame(qualitative_rows),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Source Filing": st.column_config.LinkColumn(
                    "Source Filing",
                    display_text="Open source",
                )
            },
        )

        st.markdown("**Continue the research**")
        link_cols = st.columns(
            min(len(selected_companies), 3)
        )
        for index, company in enumerate(
            selected_companies
        ):
            ticker = str(
                company_data[company].get(
                    "ticker",
                    "",
                )
            ).upper()
            with link_cols[index % len(link_cols)]:
                st.link_button(
                    f"Open {ticker} research",
                    research_link(ticker),
                    use_container_width=True,
                )

    st.caption(
        "EquityLens peer comparisons are descriptive research tools. "
        "No composite score, buy/sell ranking, or investment recommendation is produced."
    )
