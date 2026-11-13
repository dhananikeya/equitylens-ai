import pandas as pd
import streamlit as st

from research_experience import render_home_discovery, render_watchlist
from ui_components import format_utc_timestamp, render_refresh_indicator, section


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
):
    st.markdown(
        f"""
        <div class="el-product-hero el-tool-hero">
            <div class="el-eyebrow">Public-company research, made easier to navigate</div>
            <h1 class="el-product-title">
                Research public companies.<br>
                <span>Without digging through hundreds of pages.</span>
            </h1>
            <p class="el-product-subtitle">
                EquityLens brings SEC filings, financial performance, business context,
                market data, and source-linked research into one workspace so you can
                understand a company faster and verify the original evidence yourself.
            </p>
            <div class="el-badges">
                <span class="el-badge">{len(company_universe):,}-company universe</span>
                <span class="el-badge">{company_universe['Industry'].nunique():,} industries</span>
                <span class="el-badge">SEC EDGAR sourced</span>
                <span class="el-badge">Direct filing links</span>
            </div>
            <div style="margin-top:1rem;color:#8F9CA6;font-size:.88rem;">
                Independently created by Keya Dhanani · Educational research, not investment advice.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    coverage_totals = research_coverage.get(
        "totals",
        {},
    )
    coverage_percentages = research_coverage.get(
        "percentages",
        {},
    )

    render_home_discovery(
        st,
        company_universe,
        open_company_research,
        sec_summary,
        research_coverage,
    )
    render_watchlist(
        st,
        company_data,
        open_company_research,
    )

    section("Start here", "What would you like to explore?")
    quick_actions = [
        (
            "Research a company",
            "Company Research",
            "Financials, business context, risks, and original filings.",
        ),
        (
            "Compare companies",
            "Industry Comparison",
            "Compare growth, margins, and business models across peers.",
        ),
        (
            "Explore markets",
            "Market Monitor",
            "Market movement, heat maps, rates, and economic releases.",
        ),
        (
            "Learn the basics",
            "Learn",
            "Plain-language explanations of financial terms and concepts.",
        ),
    ]
    action_columns = st.columns(2)
    for action_index, (label, destination, description) in enumerate(quick_actions):
        with action_columns[action_index % 2]:
            st.button(
                label,
                key=f"home_action_{action_index}",
                on_click=navigate_to,
                args=(destination,),
                use_container_width=True,
            )
            st.caption(description)

    with st.expander("Coverage & sources"):
        coverage_sec_copy = (
            f"{sec_synced_companies:,} companies with synced SEC filings"
            if sec_summary.get("_ready")
            else "SEC filing coverage index refreshing"
        )
        sec_index_updated = format_utc_timestamp(
            sec_summary.get("generated_at_utc"),
            fallback="Refresh in progress",
        )
        st.caption(
            f"{len(company_universe):,} companies · "
            f"{company_universe['Industry'].nunique():,} industries · "
            f"{coverage_sec_copy} · SEC index: {sec_index_updated}"
        )
        st.write(
            "Company coverage and completed research are different. "
            "Some companies have market data and filings while structured analysis is still being added."
        )
        coverage_cols = st.columns(4)
        coverage_cols[0].metric(
            "Annual financials",
            f"{coverage_totals.get('annual_financials', 0):,}",
            f"{coverage_percentages.get('annual_financials', 0):.1f}%",
        )
        coverage_cols[1].metric(
            "Quarterly financials",
            f"{coverage_totals.get('quarterly_financials', 0):,}",
            f"{coverage_percentages.get('quarterly_financials', 0):.1f}%",
        )
        coverage_cols[2].metric(
            "Qualitative analysis",
            f"{coverage_totals.get('qualitative_analysis', 0):,}",
            f"{coverage_percentages.get('qualitative_analysis', 0):.1f}%",
        )
        coverage_cols[3].metric(
            "Deep research",
            f"{coverage_totals.get('deep_research', 0):,}",
            f"{coverage_percentages.get('deep_research', 0):.1f}%",
        )
        st.caption(
            "Coverage snapshot generated: "
            + format_utc_timestamp(
                research_coverage.get(
                    "generated_at_utc"
                ),
                fallback="Unavailable",
            )
        )
        st.markdown(
            "**Reported:** taken from a company disclosure. "
            "**Calculated:** derived from reported figures. "
            "**Research summary:** context based on available disclosures."
        )
        st.caption(
            "Primary sources: SEC EDGAR and company disclosures. "
            "Market-data sources are identified in each view."
        )

    section("Recently updated", "Latest SEC filings detected")
    render_refresh_indicator(
        "SEC coverage refreshed",
        sec_summary.get("generated_at_utc"),
        "automated filing monitor",
    )
    recent_filing_rows = [
        {
            "Company": (
                f"{row.get('ticker', '')} · {row.get('company', '')}"
            ).strip(" ·"),
            "Filed": row.get("filing_date", ""),
            "Form": row.get("form", ""),
            "Description": row.get("description", ""),
            "SEC Filing": row.get("url", ""),
            "Research": (
                research_link(row.get("ticker", ""))
                if row.get("ticker")
                else ""
            ),
        }
        for row in sec_summary.get("recent_filings", [])[:5]
        if row.get("filing_date")
    ]

    if recent_filing_rows:
        st.dataframe(
            pd.DataFrame(recent_filing_rows),
            use_container_width=True,
            hide_index=True,
            column_config={
                "SEC Filing": st.column_config.LinkColumn(
                    "SEC Filing",
                    display_text="Open filing",
                ),
                "Research": st.column_config.LinkColumn(
                    "Research",
                    display_text="Open company research",
                )
            },
        )
        st.caption(
            "The filing monitor checks covered companies automatically. "
            f"Coverage index generated: {format_utc_timestamp(sec_summary.get('generated_at_utc'))}. "
            "Newly detected filings may appear before EquityLens has standardized every financial or qualitative field."
        )
    else:
        st.caption(
            "Recent SEC filing activity will appear here as the automated filing monitor populates."
        )
