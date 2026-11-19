import pandas as pd
import streamlit as st

from research_experience import render_home_discovery, render_watchlist
from ui_components import format_utc_timestamp, section
from frontend_components import render_research_actions, supports_research_actions


def render_home(
    company_universe,
    sec_synced_companies,
    sec_summary,
    deep_research_tickers,
    company_data,
    open_company_research,
    navigate_to,
    research_link,
):
    # Presentation-only homepage refresh: no changes to research or data logic.
    st.markdown(
        f"""
        <style>
        .el-home-intro {{
            position: relative; overflow: hidden; padding: clamp(2rem,4.5vw,4.5rem);
            margin: .6rem 0 1.35rem; border: 1px solid #253740;
            border-radius: 14px; background: #091217;
        }}
        .el-home-intro::after {{
            content: ""; position: absolute; width: 36rem; height: 36rem;
            top: -22rem; right: -12rem; border-radius: 50%;
            background: radial-gradient(circle,rgba(22,199,178,.105),transparent 70%);
            pointer-events: none;
        }}
        .el-home-kicker {{ color: #7DD3C7; font-size: .72rem;
            font-weight: 600; letter-spacing: .13em; text-transform: uppercase; }}
        .el-home-title {{ max-width: 830px; margin: 1.1rem 0;
            font-size: clamp(2.6rem,5.6vw,5.3rem); line-height: 1.08;
            letter-spacing: -.055em; font-weight: 600; color: #F1F5F5; }}
        .el-home-title em {{ font-style: normal; color: #91A7AA; }}
        .el-home-description {{ max-width: 640px; color: #A1AFB5;
            font-size: clamp(.96rem,1.2vw,1.09rem); line-height: 1.7; }}
        .el-home-source-line {{ display: flex; flex-wrap: wrap;
            gap: .7rem 1.5rem; margin-top: 2.2rem; padding-top: 1.15rem;
            border-top: 1px solid #263941; font-family: 'IBM Plex Mono',monospace;
            font-size: .72rem; color: #92A4AB; }}
        .el-home-source-line strong {{ font-weight: 600; color: #E3EBEB; }}
        .el-home-section-label {{ color: #83B5AD; font-family: 'IBM Plex Mono',monospace;
            text-transform: uppercase; letter-spacing: .08em; font-size: .7rem; }}
        @media(max-width:640px) {{
            .el-home-intro {{ padding: 1.65rem 1.3rem; }}
            .el-home-title {{ font-size: clamp(2.25rem,9vw,3.1rem); }}
            .el-home-source-line {{ gap: .55rem 1rem; }}
        }}
        </style>
        <section class="el-home-intro" aria-label="EquityLens research introduction">
            <div class="el-home-kicker">Independent financial intelligence</div>
            <h1 class="el-home-title">Understand the business.<br><em>Follow the evidence.</em></h1>
            <p class="el-home-description">
                Research public companies through financial performance, business context,
                market data, and original SEC disclosures, all in one focused workspace.
            </p>
            <div class="el-home-source-line">
                <span><strong>{len(company_universe):,}</strong> companies</span>
                <span><strong>{company_universe['Industry'].nunique():,}</strong> industries</span>
                <span>SEC EDGAR · Primary-source filings</span>
                <span>Independent research · Not investment advice</span>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    # Keep operational coverage transparent, without repeating the hero's counts.
    st.caption(
        f"Filing coverage: {sec_synced_companies:,} companies synced"
        if sec_summary.get("_ready")
        else "Filing coverage index updating"
    )
    st.caption(
        f"Structured research available: {len(deep_research_tickers):,} companies. "
        "The research universe and completed reports are tracked separately."
    )

    render_home_discovery(
        st,
        company_universe,
        open_company_research,
        sec_summary,
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
    # Progressive enhancement: interactive JS cards on modern Streamlit,
    # with native buttons preserved for older deployments.
    v2_available = supports_research_actions()
    if v2_available:
        selected_destination = render_research_actions(quick_actions)
        if selected_destination in {item[1] for item in quick_actions}:
            navigate_to(selected_destination)
            st.rerun()
    else:
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
