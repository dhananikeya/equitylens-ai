import json
import requests
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="EquityLens AI",
    page_icon="📊",
    layout="wide"
)

st.markdown(
    """
    <style>
    :root {
        --el-bg: #07111F;
        --el-surface: #0D1B2A;
        --el-surface-2: #112338;
        --el-border: rgba(148, 163, 184, 0.18);
        --el-text: #EAF2F8;
        --el-muted: #94A3B8;
        --el-teal: #2DD4BF;
        --el-blue: #60A5FA;
        --el-gold: #F6C453;
        --el-green: #22C55E;
        --el-red: #EF4444;
    }

    .stApp {
        background:
            radial-gradient(circle at 10% 0%, rgba(45, 212, 191, 0.08), transparent 28%),
            radial-gradient(circle at 90% 10%, rgba(96, 165, 250, 0.08), transparent 30%),
            var(--el-bg);
        color: var(--el-text);
    }

    .block-container {
        max-width: 1450px;
        padding-top: 1.8rem;
        padding-bottom: 4rem;
    }

    .el-hero {
        padding: 2rem 2.2rem;
        border: 1px solid var(--el-border);
        border-radius: 24px;
        background: linear-gradient(135deg, rgba(13,27,42,0.98), rgba(17,35,56,0.94));
        box-shadow: 0 20px 60px rgba(0,0,0,0.22);
        margin-bottom: 1.4rem;
    }

    .el-company-hero {
        padding: 1.6rem 1.8rem;
        border: 1px solid var(--el-border);
        border-radius: 22px;
        background: linear-gradient(135deg, rgba(17,35,56,0.98), rgba(13,27,42,0.96));
        margin: 0.8rem 0 1.3rem 0;
    }

    .el-kicker {
        color: var(--el-teal);
        font-size: 0.78rem;
        font-weight: 800;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        margin-bottom: 0.45rem;
    }

    .el-title {
        font-size: clamp(2.2rem, 5vw, 4.2rem);
        line-height: 0.98;
        font-weight: 800;
        letter-spacing: -0.04em;
        color: var(--el-text);
        margin: 0 0 0.8rem 0;
    }

    .el-title span { color: var(--el-teal); }

    .el-company-title {
        font-size: clamp(1.8rem, 4vw, 3rem);
        line-height: 1.05;
        font-weight: 800;
        letter-spacing: -0.035em;
        color: var(--el-text);
        margin-bottom: 0.5rem;
    }

    .el-subtitle {
        max-width: 900px;
        font-size: 1.02rem;
        line-height: 1.65;
        color: #C7D2E1;
        margin: 0;
    }

    .el-badges {
        display: flex;
        flex-wrap: wrap;
        gap: 0.55rem;
        margin-top: 1.1rem;
    }

    .el-badge {
        padding: 0.42rem 0.7rem;
        border-radius: 999px;
        border: 1px solid var(--el-border);
        background: rgba(255,255,255,0.035);
        color: #CBD5E1;
        font-size: 0.78rem;
        font-weight: 650;
    }

    .el-section {
        margin-top: 1.65rem;
        margin-bottom: 0.55rem;
    }

    .el-section-label {
        color: var(--el-teal);
        text-transform: uppercase;
        letter-spacing: 0.12em;
        font-size: 0.74rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }

    .el-section-title {
        font-size: 1.65rem;
        font-weight: 750;
        color: var(--el-text);
        letter-spacing: -0.02em;
        margin: 0;
    }

    .el-summary-card, .el-change-card, .el-risk-card {
        border: 1px solid var(--el-border);
        border-radius: 18px;
        background: linear-gradient(180deg, rgba(17,35,56,0.92), rgba(13,27,42,0.92));
        box-shadow: 0 10px 30px rgba(0,0,0,0.12);
    }

    .el-summary-card {
        min-height: 145px;
        padding: 1.2rem 1.3rem;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .el-summary-label {
        color: var(--el-muted);
        font-size: 0.88rem;
        font-weight: 650;
        margin-bottom: 0.55rem;
    }

    .el-summary-value {
        color: var(--el-text);
        font-size: 1.7rem;
        line-height: 1.2;
        font-weight: 800;
        letter-spacing: -0.03em;
        overflow-wrap: anywhere;
    }

    .el-change-card, .el-risk-card {
        padding: 1rem 1.1rem;
        margin: 0.6rem 0;
    }

    .el-change-title, .el-risk-title {
        color: var(--el-text);
        font-size: 1rem;
        font-weight: 800;
        margin-bottom: 0.35rem;
    }

    .el-change-copy {
        color: #D8E2EE;
        line-height: 1.55;
        margin: 0;
    }

    .el-risk-list {
        margin: 0;
        padding-left: 1.1rem;
        color: #D8E2EE;
        line-height: 1.5;
    }

    .el-risk-list li { margin: 0.25rem 0; }

    div[data-testid="stMetric"] {
        background: linear-gradient(180deg, rgba(17,35,56,0.96), rgba(13,27,42,0.96));
        border: 1px solid var(--el-border);
        border-radius: 18px;
        padding: 1rem 1.1rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.14);
    }

    div[data-testid="stMetricLabel"] { color: var(--el-muted); }
    div[data-testid="stMetricValue"] { color: var(--el-text); font-weight: 750; }

    .stButton > button {
        min-height: 3rem;
        border-radius: 14px;
        border: 1px solid rgba(45, 212, 191, 0.35);
        background: linear-gradient(135deg, #13B8A6, #2F7FEA);
        color: white;
        font-weight: 750;
        padding: 0.7rem 1.35rem;
        box-shadow: 0 10px 28px rgba(47,127,234,0.18);
    }

    .stButton > button:hover {
        border-color: rgba(45, 212, 191, 0.75);
        filter: brightness(1.05);
        color: white;
    }

    div[data-baseweb="select"] > div {
        background: rgba(13,27,42,0.92);
        border-color: var(--el-border);
        border-radius: 14px;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid var(--el-border);
        border-radius: 16px;
        overflow: hidden;
        background: rgba(13,27,42,0.72);
    }

    div[data-testid="stExpander"] {
        border: 1px solid var(--el-border);
        border-radius: 16px;
        background: rgba(13,27,42,0.64);
    }

    div[data-testid="stAlert"] { border-radius: 14px; }

    hr {
        border-color: rgba(148, 163, 184, 0.12) !important;
        margin: 1.8rem 0 !important;
    }

    .stCaption, small { color: var(--el-muted) !important; }
    footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True
)


@st.cache_data(ttl=60)
def load_json(path):
    with open(path, "r") as file:
        return json.load(file)


@st.cache_data(ttl=300)
def get_live_market_data(symbols):
    api_key = st.secrets.get(
        "TWELVE_DATA_API_KEY",
        st.secrets.get("FINIMPULSE_API_KEY")
    )

    if not api_key:
        raise ValueError("Missing Twelve Data API key in Streamlit Secrets.")

    response = requests.get(
        "https://api.twelvedata.com/quote",
        params={"symbol": ",".join(symbols), "apikey": api_key},
        timeout=20
    )
    response.raise_for_status()
    body = response.json()

    if isinstance(body, dict) and body.get("status") == "error":
        raise ValueError(body.get("message", "Twelve Data API error"))

    if len(symbols) == 1 and isinstance(body, dict) and body.get("symbol"):
        body = {symbols[0]: body}

    return {
        symbol: body.get(symbol, {})
        for symbol in symbols
        if isinstance(body, dict)
    }


def format_money(value):
    if value is None:
        return "N/A"
    sign = "-" if value < 0 else ""
    value = abs(value)
    if value >= 1_000_000_000:
        return f"{sign}${value / 1_000_000_000:.2f}B"
    if value >= 1_000_000:
        return f"{sign}${value / 1_000_000:.1f}M"
    return f"{sign}${value:,.0f}"


def pct(value):
    return f"{value:.1f}%" if value is not None else "N/A"


def format_multiple(value):
    return f"{value:.2f}x" if value is not None else "N/A"


def calc_growth(current, prior):
    if current is None or prior in (None, 0):
        return None
    return ((current - prior) / prior) * 100


def calc_margin(profit, revenue):
    if profit is None or revenue in (None, 0):
        return None
    return (profit / revenue) * 100


def section(label, title):
    st.markdown(
        f"""
        <div class="el-section">
            <div class="el-section-label">{label}</div>
            <div class="el-section-title">{title}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_summary_cards(cards):
    cols = st.columns(len(cards))
    for col, (label, value) in zip(cols, cards):
        with col:
            st.markdown(
                f"""
                <div class="el-summary-card">
                    <div class="el-summary-label">{label}</div>
                    <div class="el-summary-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True
            )


def quarterly_metrics(qdata):
    latest = qdata.get("latest_quarter", {})
    prior_q = qdata.get("prior_quarter", {})
    prior_y = qdata.get("prior_year_quarter", {})

    revenue = latest.get("revenue")
    prior_q_revenue = prior_q.get("revenue")
    prior_y_revenue = prior_y.get("revenue")

    return {
        "revenue": revenue,
        "yoy_growth": calc_growth(revenue, prior_y_revenue),
        "qoq_growth": calc_growth(revenue, prior_q_revenue),
        "gross_margin": calc_margin(latest.get("gross_profit"), revenue),
        "operating_margin": calc_margin(latest.get("operating_income"), revenue),
        "net_margin": calc_margin(latest.get("net_income"), revenue),
        "prior_q_operating_margin": calc_margin(
            prior_q.get("operating_income"), prior_q_revenue
        ),
        "prior_y_operating_margin": calc_margin(
            prior_y.get("operating_income"), prior_y_revenue
        )
    }


def build_change_notes(qdata):
    latest = qdata.get("latest_quarter", {})
    prior_q = qdata.get("prior_quarter", {})
    prior_y = qdata.get("prior_year_quarter", {})
    m = quarterly_metrics(qdata)

    notes = []

    if m["qoq_growth"] is not None:
        notes.append((
            "Sequential revenue",
            f"Revenue changed {m['qoq_growth']:+.1f}% from the prior quarter, "
            f"from {format_money(prior_q.get('revenue'))} to {format_money(latest.get('revenue'))}."
        ))

    if m["yoy_growth"] is not None:
        notes.append((
            "Year-over-year revenue",
            f"Revenue changed {m['yoy_growth']:+.1f}% from the same quarter a year earlier, "
            f"from {format_money(prior_y.get('revenue'))} to {format_money(latest.get('revenue'))}."
        ))

    if m["operating_margin"] is not None and m["prior_q_operating_margin"] is not None:
        delta = m["operating_margin"] - m["prior_q_operating_margin"]
        notes.append((
            "Operating margin",
            f"Operating margin changed {delta:+.1f} percentage points sequentially, "
            f"from {m['prior_q_operating_margin']:.1f}% to {m['operating_margin']:.1f}%."
        ))

    current_net = latest.get("net_income")
    prior_net = prior_q.get("net_income")
    if current_net is not None and prior_net is not None:
        if prior_net < 0 <= current_net:
            copy = (
                f"Net income moved from a loss of {format_money(prior_net)} "
                f"to profit of {format_money(current_net)}."
            )
        elif prior_net >= 0 > current_net:
            copy = (
                f"Net income moved from profit of {format_money(prior_net)} "
                f"to a loss of {format_money(current_net)}."
            )
        else:
            copy = (
                f"Net income changed from {format_money(prior_net)} "
                f"to {format_money(current_net)}."
            )
        notes.append(("Net income", copy))

    return notes


company_data = load_json("data/company_metrics.json")
company_analysis = load_json("data/company_analysis.json")
company_quarterly = load_json("data/company_quarterly.json")

public_market_data_enabled = bool(
    st.secrets.get("PUBLIC_MARKET_DATA_ENABLED", False)
)

industries = sorted({
    item.get("industry", "Unclassified")
    for item in company_data.values()
})


SUBGROUPS = {
    "Data Platforms": [
        "Snowflake (SNOW)",
        "MongoDB (MDB)",
        "Datadog (DDOG)",
        "Elastic (ESTC)",
        "Dynatrace (DT)"
    ],
    "Cloud / Network Infrastructure": [
        "Cloudflare (NET)",
        "Akamai (AKAM)"
    ],
    "Cybersecurity": [
        "Rubrik (RBRK)",
        "Palo Alto Networks (PANW)",
        "Zscaler (ZS)"
    ],
    "Enterprise / AI Platforms": [],
    "AI / Compute Infrastructure": [],
    "Endpoint / XDR": [
        "CrowdStrike (CRWD)",
        "SentinelOne (S)"
    ],
    "Identity Security": [
        "Okta (OKTA)"
    ],
    "Network Security": [
        "Palo Alto Networks (PANW)",
        "Fortinet (FTNT)",
        "Zscaler (ZS)"
    ],
    "Exposure Management": [
        "Tenable (TENB)"
    ]
}

st.markdown(
    """
    <div class="el-hero">
        <div class="el-kicker">Public Markets Research Platform</div>
        <div class="el-title">EquityLens <span>AI</span></div>
        <p class="el-subtitle">
            Compare public companies through SEC filings, standardized financials,
            quarterly and LTM performance, capital structure, risk factors, and
            market-data integrations. EquityLens informs. You decide.
        </p>
        <div class="el-badges">
            <span class="el-badge">SEC-sourced</span>
            <span class="el-badge">Quarterly + LTM</span>
            <span class="el-badge">Company research</span>
            <span class="el-badge">Peer comparison</span>
            <span class="el-badge">Neutral research</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

latest_period = max(
    [q.get("period_end", "") for q in company_quarterly.values()] or [""]
)

render_summary_cards([
    ("Companies Covered", str(len(company_data))),
    ("Industries", str(len(industries))),
    ("Latest Filing Period", latest_period or "N/A"),
    (
        "Market Data",
        "Private Live" if public_market_data_enabled else "Public Filing Mode"
    )
])

peer_tab, company_tab = st.tabs([
    "Peer Comparison",
    "Company Research"
])

with peer_tab:
    section("Peer Research", "Industry Comparison")

    selected_industry = st.selectbox(
        "Industry",
        industries,
        index=0
    )

    industry_companies = [
        name for name, data in company_data.items()
        if data.get("industry", "Unclassified") == selected_industry
    ]

    subgroup_options = ["All current peers"] + [
        name for name, members in SUBGROUPS.items()
        if any(member in industry_companies for member in members)
    ]

    selected_subgroup = st.selectbox(
        "Sub-group",
        subgroup_options,
        index=0
    )

    if selected_subgroup == "All current peers":
        available_companies = industry_companies
    else:
        available_companies = [
            company for company in SUBGROUPS[selected_subgroup]
            if company in industry_companies
        ]

    defaults = available_companies[:3]
    selected_companies = st.multiselect(
        "Select companies to compare",
        available_companies,
        default=defaults
    )

    if selected_subgroup != "All current peers":
        st.caption(
            f"Showing the {selected_subgroup} sub-group. "
            "More companies can be added without changing the comparison workflow."
        )

    if selected_companies:
        section("Balance Sheet", "Capital Structure Snapshot")

        capital_rows = []
        for company in selected_companies:
            capital = company_data[company].get("capital_structure", {})
            capital_rows.append({
                "Company": company,
                "Shares Outstanding": (
                    f"{capital.get('shares_outstanding'):,}"
                    if capital.get("shares_outstanding") is not None
                    else "N/A"
                ),
                "Debt": format_money(capital.get("total_debt")),
                "Cash + Investments": format_money(
                    capital.get("cash_and_investments")
                ),
                "Balance Sheet Date": capital.get(
                    "balance_sheet_as_of", "N/A"
                ),
                "Source": capital.get("source_filing", "")
            })

        st.dataframe(
            pd.DataFrame(capital_rows),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Source": st.column_config.LinkColumn(
                    "Source",
                    display_text="Open filing"
                )
            }
        )

    if st.button("Run Peer Comparison", type="primary"):
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
                revenue = data.get("revenue")
                history = data.get("history", [])
                growth = None
                if len(history) >= 2:
                    growth = calc_growth(
                        history[-1].get("revenue"),
                        history[-2].get("revenue")
                    )

                annual_rows.append({
                    "Company": company,
                    "FY": data.get("fiscal_year"),
                    "Revenue": format_money(revenue),
                    "YoY Revenue Growth": pct(growth),
                    "Gross Margin": pct(
                        calc_margin(data.get("gross_profit"), revenue)
                    ),
                    "Operating Margin": pct(
                        calc_margin(data.get("operating_income"), revenue)
                    ),
                    "Net Margin": pct(
                        calc_margin(data.get("net_income"), revenue)
                    ),
                    "Cash": format_money(data.get("cash")),
                    "Assets": format_money(data.get("assets")),
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
                latest = qdata.get("latest_quarter", {})
                ltm = qdata.get("ltm", {})
                qm = quarterly_metrics(qdata)

                quarter_rows.append({
                    "Company": company,
                    "Quarter": qdata.get("quarter_label", "N/A"),
                    "Revenue": format_money(qm["revenue"]),
                    "YoY Growth": pct(qm["yoy_growth"]),
                    "QoQ Growth": pct(qm["qoq_growth"]),
                    "Gross Margin": pct(qm["gross_margin"]),
                    "Operating Margin": pct(qm["operating_margin"]),
                    "Net Income": format_money(latest.get("net_income")),
                    "SEC Filing": qdata.get("source_filing", "")
                })

                ltm_revenue = ltm.get("revenue")
                ltm_rows.append({
                    "Company": company,
                    "LTM Revenue": format_money(ltm_revenue),
                    "LTM Gross Margin": pct(
                        calc_margin(ltm.get("gross_profit"), ltm_revenue)
                    ),
                    "LTM Operating Margin": pct(
                        calc_margin(ltm.get("operating_income"), ltm_revenue)
                    ),
                    "LTM Net Income": format_money(ltm.get("net_income")),
                    "LTM Net Margin": pct(
                        calc_margin(ltm.get("net_income"), ltm_revenue)
                    )
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
                for item in company_data[company].get("history", []):
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

            section("Qualitative Research", "Risk & Business Model")
            risk_rows = []
            for company in selected_companies:
                analysis = company_analysis.get(company, {})
                risk_rows.append({
                    "Company": company,
                    "Business Model": analysis.get("business_model", ""),
                    "Revenue Source": analysis.get(
                        "primary_revenue_source", ""
                    ),
                    "Platform Dependency": analysis.get(
                        "platform_dependency", ""
                    ),
                    "Competitive Risk": analysis.get(
                        "competitive_risk", ""
                    ),
                    "Operational Risk": analysis.get(
                        "operational_risk", ""
                    )
                })

            st.dataframe(
                pd.DataFrame(risk_rows),
                use_container_width=True,
                hide_index=True
            )

with company_tab:
    section("Deep Dive", "Company Research View")

    research_company = st.selectbox(
        "Search company or ticker",
        list(company_data.keys()),
        format_func=lambda name: (
            f"{company_data[name].get('ticker', '')} · "
            f"{name.split(' (')[0]}"
        ),
        key="research_company"
    )

    data = company_data[research_company]
    analysis = company_analysis.get(research_company, {})
    qdata = company_quarterly.get(research_company, {})
    latest = qdata.get("latest_quarter", {})
    ltm = qdata.get("ltm", {})
    capital = data.get("capital_structure", {})
    qm = quarterly_metrics(qdata)

    ticker = data.get("ticker", "")
    company_name = research_company.split(" (")[0]

    st.markdown(
        f"""
        <div class="el-company-hero">
            <div class="el-kicker">{ticker} · {data.get('industry', '')}</div>
            <div class="el-company-title">{company_name}</div>
            <p class="el-subtitle">{analysis.get('business_model', '')}</p>
            <div class="el-badges">
                <span class="el-badge">{qdata.get('quarter_label', 'Latest quarter')}</span>
                <span class="el-badge">10-K + 10-Q sourced</span>
                <span class="el-badge">Neutral research</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if public_market_data_enabled:
        try:
            market = get_live_market_data([ticker]).get(ticker, {})
        except Exception:
            market = {}

        if market:
            close = market.get("close")
            change = market.get("percent_change")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric(
                "Market Price",
                f"${float(close):,.2f}" if close not in (None, "") else "N/A",
                delta=(
                    f"{float(change):.2f}%"
                    if change not in (None, "")
                    else None
                )
            )
            m2.metric("Latest Quarter", qdata.get("quarter_label", "N/A"))
            m3.metric("Quarter Revenue", format_money(qm["revenue"]))
            m4.metric("YoY Revenue Growth", pct(qm["yoy_growth"]))
    else:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Latest Quarter", qdata.get("quarter_label", "N/A"))
        m2.metric("Quarter Revenue", format_money(qm["revenue"]))
        m3.metric("YoY Revenue Growth", pct(qm["yoy_growth"]))
        m4.metric("Operating Margin", pct(qm["operating_margin"]))

    section("Earnings", "What Changed This Quarter?")
    change_notes = build_change_notes(qdata)
    if change_notes:
        for title, copy in change_notes:
            st.markdown(
                f"""
                <div class="el-change-card">
                    <div class="el-change-title">{title}</div>
                    <p class="el-change-copy">{copy}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        st.caption(
            "These statements are calculated from reported SEC filing figures. "
            "They describe changes and do not rate the company or make an investment recommendation."
        )
    else:
        st.info(
            "Quarter-over-quarter change analysis will appear here when a newer quarterly filing "
            "is added to the structured dataset. The latest annual filing is available below."
        )

    section("Financial Snapshot", "Latest Quarter + LTM")
    quarter_cols = st.columns(4)
    quarter_cols[0].metric("Quarter Revenue", format_money(latest.get("revenue")))
    quarter_cols[1].metric("Gross Margin", pct(qm["gross_margin"]))
    quarter_cols[2].metric("Operating Margin", pct(qm["operating_margin"]))
    quarter_cols[3].metric("Net Income", format_money(latest.get("net_income")))

    ltm_revenue = ltm.get("revenue")
    ltm_cols = st.columns(4)
    ltm_cols[0].metric("LTM Revenue", format_money(ltm_revenue))
    ltm_cols[1].metric(
        "LTM Gross Margin",
        pct(calc_margin(ltm.get("gross_profit"), ltm_revenue))
    )
    ltm_cols[2].metric(
        "LTM Operating Margin",
        pct(calc_margin(ltm.get("operating_income"), ltm_revenue))
    )
    ltm_cols[3].metric("LTM Net Income", format_money(ltm.get("net_income")))

    section("Balance Sheet", "Capital Structure")
    render_summary_cards([
        (
            "Shares Outstanding",
            f"{capital.get('shares_outstanding'):,}"
            if capital.get("shares_outstanding") is not None else "N/A"
        ),
        ("Debt", format_money(capital.get("total_debt"))),
        (
            "Cash + Investments",
            format_money(capital.get("cash_and_investments"))
        ),
        ("Balance Sheet Date", capital.get("balance_sheet_as_of", "N/A"))
    ])

    section("Trend", "Historical Financials")
    history = data.get("history", [])
    history_df = pd.DataFrame(history)
    if not history_df.empty:
        display_history = history_df.copy()
        display_history["Operating Margin"] = (
            display_history["operating_income"]
            / display_history["revenue"] * 100
        )
        st.line_chart(
            display_history.set_index(
                display_history["fiscal_year"].astype(str)
            )[["revenue"]].rename(columns={"revenue": "Revenue"})
        )
        st.line_chart(
            display_history.set_index(
                display_history["fiscal_year"].astype(str)
            )[["Operating Margin"]]
        )

    section("Filings", "10-K vs Latest 10-Q Snapshot")
    annual_revenue = data.get("revenue")
    filing_rows = [
        {
            "Filing": "Latest 10-K",
            "Period": data.get("fiscal_year_end", "N/A"),
            "Revenue": format_money(annual_revenue),
            "Operating Margin": pct(
                calc_margin(data.get("operating_income"), annual_revenue)
            ),
            "Net Income": format_money(data.get("net_income")),
            "Source": data.get("filing_url", "")
        },
        {
            "Filing": "Latest 10-Q",
            "Period": qdata.get("period_end", "N/A"),
            "Revenue": format_money(latest.get("revenue")),
            "Operating Margin": pct(qm["operating_margin"]),
            "Net Income": format_money(latest.get("net_income")),
            "Source": qdata.get("source_filing", "")
        }
    ]

    st.dataframe(
        pd.DataFrame(filing_rows),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Source": st.column_config.LinkColumn(
                "Source",
                display_text="Open filing"
            )
        }
    )
    st.caption(
        "Annual and quarterly periods are different lengths, so the table is a filing snapshot, "
        "not a direct period-for-period comparison."
    )

    section("Timeline", "Recent Filing Timeline")
    timeline = pd.DataFrame([
        {
            "Date / Period End": data.get("fiscal_year_end", "N/A"),
            "Form": "10-K",
            "What it covers": "Annual financials, business model, and risk disclosures",
            "Source": data.get("filing_url", "")
        },
        {
            "Date / Period End": qdata.get("period_end", "N/A"),
            "Form": "10-Q",
            "What it covers": "Latest quarterly financial performance",
            "Source": qdata.get("source_filing", "")
        }
    ])

    st.dataframe(
        timeline,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Source": st.column_config.LinkColumn(
                "Source",
                display_text="Open filing"
            )
        }
    )

    section("Qualitative Research", "Business Model & Risk Themes")
    detail_cols = st.columns(2)

    with detail_cols[0]:
        st.markdown("**Business model**")
        st.write(analysis.get("business_model", "N/A"))
        st.markdown("**Primary revenue source**")
        st.write(analysis.get("primary_revenue_source", "N/A"))
        st.markdown("**Customer type**")
        st.write(analysis.get("customer_type", "N/A"))
        st.markdown("**Platform dependency**")
        st.write(analysis.get("platform_dependency", "N/A"))

    with detail_cols[1]:
        themes = analysis.get("key_risk_themes", [])
        items = "".join(f"<li>{theme}</li>" for theme in themes)
        st.markdown(
            f"""
            <div class="el-risk-card">
                <div class="el-risk-title">Key risk themes</div>
                <ul class="el-risk-list">{items}</ul>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown("**Competitive risk**")
        st.write(analysis.get("competitive_risk", "N/A"))
        st.markdown("**Operational risk**")
        st.write(analysis.get("operational_risk", "N/A"))

    section("Grounded Research", "Quick Questions")
    research_question = st.selectbox(
        "Choose a question",
        [
            "How fast is revenue growing?",
            "Is operating profitability improving sequentially?",
            "What does the company primarily sell?",
            "What are the main disclosed risk themes?",
            "How much cash and debt does it report?"
        ]
    )

    if research_question == "How fast is revenue growing?":
        st.info(
            f"Latest-quarter revenue was {format_money(qm['revenue'])}. "
            f"That represents {pct(qm['yoy_growth'])} year-over-year growth "
            f"and {pct(qm['qoq_growth'])} sequential growth."
        )
    elif research_question == "Is operating profitability improving sequentially?":
        current_margin = qm["operating_margin"]
        prior_margin = qm["prior_q_operating_margin"]
        if current_margin is not None and prior_margin is not None:
            delta = current_margin - prior_margin
            st.info(
                f"Operating margin changed from {prior_margin:.1f}% in the prior quarter "
                f"to {current_margin:.1f}% in the latest quarter, a change of {delta:+.1f} percentage points."
            )
        else:
            st.info("The current structured dataset is insufficient to calculate that comparison.")
    elif research_question == "What does the company primarily sell?":
        st.info(analysis.get("primary_revenue_source", "Not available."))
    elif research_question == "What are the main disclosed risk themes?":
        st.info("; ".join(analysis.get("key_risk_themes", [])) or "Not available.")
    elif research_question == "How much cash and debt does it report?":
        st.info(
            f"Latest structured capital data shows "
            f"{format_money(capital.get('cash_and_investments'))} of cash and investments "
            f"and {format_money(capital.get('total_debt'))} of debt."
        )

st.markdown("---")
section("Methodology", "Data Sources")
st.write(
    """
    - SEC EDGAR filings, including Forms 10-K, 10-Q, 8-K, and S-1
    - Company-reported financial statements and disclosures
    - Market-data integrations in private environments when permitted by provider licensing
    """
)

section("Disclosure", "Important Disclosures")
st.caption(
    """
    EquityLens AI is an educational and research tool that analyzes publicly
    available financial information. It does not provide personalized investment
    advice, investment recommendations, rankings, or guarantees of future performance.

    EquityLens AI is an independent personal research project and is not affiliated
    with, sponsored by, or endorsed by any similarly named company, product, service,
    financial institution, broker, exchange, or data provider.

    Financial information may be delayed, incomplete, or affected by later filings
    and restatements. Users should verify material information against the original
    SEC filings and company disclosures before making financial decisions.
    """
)
