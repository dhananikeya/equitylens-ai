import html

import pandas as pd
import streamlit as st

from research_experience import (
    render_home_discovery,
    render_watchlist,
)
from ui_components import (
    format_utc_timestamp,
    render_refresh_indicator,
    section,
)


def render_home(
    company_universe,
    sec_synced_companies,
    sec_summary,
    research_coverage,
    deep_research_tickers,
    company_data,
    open_company_research,
    navigate_to,
    research_link,
    remember_choice,
):
    coverage_totals = (
        research_coverage.get(
            "totals",
            {},
        )
        or {}
    )
    coverage_percentages = (
        research_coverage.get(
            "percentages",
            {},
        )
        or {}
    )
    coverage_by_ticker = (
        research_coverage.get(
            "companies",
            {},
        )
        or {}
    )

    st.markdown(
        f"""
        <div class="el-product-hero el-tool-hero el-home-hero">
            <div class="el-eyebrow">Primary-source public-company research</div>
            <h1 class="el-product-title">
                Understand a company.<br>
                <span>Verify the evidence.</span>
            </h1>
            <p class="el-product-subtitle">
                Search one of {len(company_universe):,} companies, understand the business and numbers,
                then open the original filing behind the research.
            </p>
            <div class="el-badges">
                <span class="el-badge">{len(company_universe):,} companies</span>
                <span class="el-badge">SEC filing links</span>
                <span class="el-badge">No paywall</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_home_discovery(
        st,
        company_universe,
        open_company_research,
        sec_summary,
        research_coverage,
    )

    section(
        "Why EquityLens",
        "Research that keeps the evidence visible",
    )
    differentiators = [
        (
            "01",
            "Primary sources first",
            "SEC filings and official disclosures stay one click away from the summary.",
        ),
        (
            "02",
            "Research depth is visible",
            "A company’s completion status is shown instead of pretending every profile has the same coverage.",
        ),
        (
            "03",
            "Reported and calculated stay separate",
            "EquityLens labels sourced figures, calculated metrics, and qualitative research differently.",
        ),
    ]
    st.markdown(
        '<div class="el-home-card-grid">'
        + "".join(
            (
                '<div class="el-home-card">'
                f'<div class="el-home-card-kicker">{number}</div>'
                f'<div class="el-home-card-title">{html.escape(title)}</div>'
                f'<div class="el-home-card-copy">{html.escape(copy)}</div>'
                '</div>'
            )
            for number, title, copy in differentiators
        )
        + '</div>',
        unsafe_allow_html=True,
    )

    section(
        "Research flow",
        "Search → Understand → Verify",
    )
    workflow = [
        (
            "Search",
            "Find a company by ticker, name, alias, industry context, or close spelling.",
        ),
        (
            "Understand",
            "Read the business model, financial trends, risks, peers, ownership, and filing context.",
        ),
        (
            "Verify",
            "Open the original SEC filing or source behind the conclusion before relying on it.",
        ),
    ]
    st.markdown(
        '<div class="el-home-workflow">'
        + "".join(
            (
                '<div class="el-home-workflow-step">'
                f'<div class="el-home-workflow-num">0{index}</div>'
                f'<div class="el-home-card-title">{html.escape(title)}</div>'
                f'<div class="el-home-card-copy">{html.escape(copy)}</div>'
                '</div>'
            )
            for index, (title, copy) in enumerate(
                workflow,
                start=1,
            )
        )
        + '</div>',
        unsafe_allow_html=True,
    )

    quick_cols = st.columns(3)
    with quick_cols[0]:
        st.button(
            "Open Company Research",
            key="home_open_company_research",
            on_click=navigate_to,
            args=("Company Research",),
            use_container_width=True,
        )
    with quick_cols[1]:
        st.button(
            "Compare companies",
            key="home_open_compare",
            on_click=navigate_to,
            args=("Industry Comparison",),
            use_container_width=True,
        )
    with quick_cols[2]:
        st.button(
            "Open filing tracker",
            key="home_open_filings",
            on_click=navigate_to,
            args=("Filings",),
            use_container_width=True,
        )

    section(
        "Explore",
        "Browse by industry",
    )
    industry_counts = (
        company_universe["Industry"]
        .fillna("Unclassified")
        .astype(str)
        .replace("", "Unclassified")
        .value_counts()
        .head(6)
    )

    def open_industry(industry):
        remember_choice(
            "peer_industry",
            industry,
        )
        remember_choice(
            "peer_subgroup",
            "All current peers",
        )
        navigate_to(
            "Industry Comparison"
        )

    industry_cols = st.columns(3)
    for index, (
        industry,
        count,
    ) in enumerate(industry_counts.items()):
        with industry_cols[index % 3]:
            st.markdown(
                (
                    '<div class="el-home-industry-card">'
                    f'<div class="el-home-card-title">{html.escape(str(industry))}</div>'
                    f'<div class="el-home-card-copy">{int(count):,} companies in the current universe</div>'
                    '</div>'
                ),
                unsafe_allow_html=True,
            )
            st.button(
                "Compare this industry",
                key=(
                    "home_industry_"
                    + str(index)
                ),
                on_click=open_industry,
                args=(str(industry),),
                use_container_width=True,
            )

    recent_tickers = [
        str(ticker).upper().strip()
        for ticker in st.session_state.get(
            "recent_research_tickers",
            [],
        )
        if str(ticker).strip()
    ]

    profile_lookup = {
        str(row.get("Ticker", "")).upper().strip(): {
            "company": str(
                row.get("Company", "")
            ).strip(),
            "industry": str(
                row.get("Industry", "")
            ).strip(),
        }
        for _, row in company_universe.iterrows()
        if str(
            row.get("Ticker", "")
        ).strip()
    }

    section(
        "Continue researching",
        "Recent & most-complete profiles",
    )
    recent_col, complete_col = st.columns(
        2,
        gap="large",
    )

    with recent_col:
        st.markdown(
            "**Recently researched**"
        )
        if recent_tickers:
            for ticker in recent_tickers[:5]:
                meta = profile_lookup.get(
                    ticker,
                    {},
                )
                company = (
                    meta.get("company")
                    or ticker
                )
                coverage = (
                    coverage_by_ticker.get(
                        ticker,
                        {},
                    )
                    or {}
                )
                st.button(
                    f"{ticker} · {company}",
                    key=(
                        "home_recent_"
                        + ticker
                    ),
                    on_click=open_company_research,
                    args=(ticker,),
                    use_container_width=True,
                )
                st.caption(
                    f"{coverage.get('completion_status', 'Research available')} · "
                    f"{int(coverage.get('completeness_percent', 0) or 0)}%"
                )
        else:
            st.caption(
                "Companies you open during this visit will appear here."
            )

    with complete_col:
        st.markdown(
            "**Most-complete profiles**"
        )
        complete_profiles = sorted(
            [
                record
                for ticker, record in coverage_by_ticker.items()
                if (
                    ticker in profile_lookup
                    and int(
                        record.get(
                            "completeness_percent",
                            0,
                        )
                        or 0
                    )
                    > 0
                )
            ],
            key=lambda record: (
                -int(
                    record.get(
                        "completeness_percent",
                        0,
                    )
                    or 0
                ),
                str(
                    record.get(
                        "company",
                        "",
                    )
                ).lower(),
            ),
        )[:5]

        if complete_profiles:
            for record in complete_profiles:
                ticker = str(
                    record.get(
                        "ticker",
                        "",
                    )
                ).upper()
                company = (
                    record.get("company")
                    or profile_lookup.get(
                        ticker,
                        {},
                    ).get(
                        "company",
                        ticker,
                    )
                )
                st.button(
                    f"{ticker} · {company}",
                    key=(
                        "home_complete_"
                        + ticker
                    ),
                    on_click=open_company_research,
                    args=(ticker,),
                    use_container_width=True,
                )
                st.caption(
                    f"{record.get('completion_status', 'Research available')} · "
                    f"{int(record.get('completeness_percent', 0) or 0)}%"
                )
        else:
            st.caption(
                "Completed profiles will appear here as research coverage expands."
            )

    render_watchlist(
        st,
        company_data,
        open_company_research,
    )

    section(
        "What's new",
        "Latest SEC filings detected",
    )
    render_refresh_indicator(
        "SEC coverage refreshed",
        sec_summary.get(
            "generated_at_utc"
        ),
        "automated filing monitor",
    )
    recent_filing_rows = [
        {
            "Company": (
                f"{row.get('ticker', '')} · {row.get('company', '')}"
            ).strip(" ·"),
            "Filed": row.get(
                "filing_date",
                "",
            ),
            "Form": row.get(
                "form",
                "",
            ),
            "Description": row.get(
                "description",
                "",
            ),
            "SEC Filing": row.get(
                "url",
                "",
            ),
            "Research": (
                research_link(
                    row.get(
                        "ticker",
                        "",
                    )
                )
                if row.get("ticker")
                else ""
            ),
        }
        for row in sec_summary.get(
            "recent_filings",
            [],
        )[:6]
        if row.get("filing_date")
    ]

    if recent_filing_rows:
        st.dataframe(
            pd.DataFrame(
                recent_filing_rows
            ),
            use_container_width=True,
            hide_index=True,
            column_config={
                "SEC Filing": (
                    st.column_config.LinkColumn(
                        "SEC Filing",
                        display_text="Open filing",
                    )
                ),
                "Research": (
                    st.column_config.LinkColumn(
                        "Research",
                        display_text="Open research",
                    )
                ),
            },
        )
        st.caption(
            "New filings can appear before every structured research field has been refreshed."
        )
    else:
        st.caption(
            "Recent SEC filing activity will appear here as the filing monitor updates."
        )

    section(
        "Learn",
        "New to filings or financial statements?",
    )
    st.markdown(
        """
        <div class="el-home-learn-card">
            <div class="el-home-card-title">Learn the basics without leaving the research flow.</div>
            <div class="el-home-card-copy">
                Plain-language guides explain revenue, margins, SEC forms, risk factors,
                valuation context, and the terms used throughout EquityLens.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.button(
        "Open Learn",
        key="home_learn_cta",
        on_click=navigate_to,
        args=("Learn",),
        use_container_width=True,
    )

    with st.expander(
        "Coverage & sources"
    ):
        coverage_sec_copy = (
            f"{sec_synced_companies:,} companies with indexed SEC filings"
            if sec_summary.get("_ready")
            else "SEC filing coverage is refreshing"
        )
        st.markdown(
            f"**{len(company_universe):,} companies · "
            f"{company_universe['Industry'].nunique():,} industries · "
            f"{coverage_sec_copy}**"
        )
        st.caption(
            "Universe coverage and research completion are separate. "
            "A company can have SEC filings available before deeper qualitative research is complete."
        )

        coverage_cols = st.columns(4)
        for col, (
            label,
            key,
        ) in zip(
            coverage_cols,
            [
                (
                    "Annual financials",
                    "annual_financials",
                ),
                (
                    "Quarterly financials",
                    "quarterly_financials",
                ),
                (
                    "Qualitative research",
                    "qualitative_analysis",
                ),
                (
                    "Deep research",
                    "deep_research",
                ),
            ],
        ):
            col.metric(
                label,
                f"{coverage_totals.get(key, 0):,}",
                (
                    f"{coverage_percentages.get(key, 0):.1f}%"
                ),
            )

        st.caption(
            "Coverage snapshot: "
            + format_utc_timestamp(
                research_coverage.get(
                    "generated_at_utc"
                ),
                fallback="Unavailable",
            )
            + " · SEC index: "
            + format_utc_timestamp(
                sec_summary.get(
                    "generated_at_utc"
                ),
                fallback="Unavailable",
            )
        )
        st.markdown(
            "**Source policy:** SEC EDGAR and official disclosures are primary. "
            "Reported figures stay separate from EquityLens calculations and qualitative research summaries."
        )
