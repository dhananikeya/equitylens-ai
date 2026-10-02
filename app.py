# EquityLens AI
# Copyright © 2026 Keya Dhanani. All rights reserved.
# Independently designed and developed by Keya Dhanani.
# Unauthorized reproduction, redistribution, republication, or creation of a substantially
# similar copy of this original application code is not permitted except where allowed by law
# or applicable platform terms. Third-party libraries, public filings, factual source data,
# company names, and trademarks remain subject to their respective rights and terms.

import json
import requests
import pandas as pd
import streamlit as st
from supabase import create_client

st.set_page_config(
    page_title="EquityLens AI",
    page_icon="📊",
    layout="wide"
)

st.markdown(
    """
    <style>
    :root {
        /* Follow Streamlit's active System / Light / Dark theme automatically. */
        --el-bg: var(--background-color);
        --el-surface: var(--secondary-background-color);
        --el-surface-2: color-mix(
            in srgb,
            var(--secondary-background-color) 82%,
            var(--background-color)
        );
        --el-border: color-mix(in srgb, var(--text-color) 16%, transparent);
        --el-text: var(--text-color);
        --el-muted: color-mix(in srgb, var(--text-color) 62%, transparent);
        --el-teal: #14B8A6;
        --el-blue: #3B82F6;
        --el-gold: #D99A13;
        --el-green: #16A34A;
        --el-red: #DC2626;
    }

    .stApp {
        background:
            radial-gradient(
                circle at 10% 0%,
                color-mix(in srgb, var(--el-teal) 8%, transparent),
                transparent 28%
            ),
            radial-gradient(
                circle at 90% 10%,
                color-mix(in srgb, var(--el-blue) 8%, transparent),
                transparent 30%
            ),
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
        background: linear-gradient(135deg, var(--el-surface), var(--el-surface-2));
        box-shadow: 0 20px 60px rgba(0,0,0,0.22);
        margin-bottom: 1.4rem;
    }

    .el-company-hero {
        padding: 1.6rem 1.8rem;
        border: 1px solid var(--el-border);
        border-radius: 22px;
        background: linear-gradient(135deg, var(--el-surface-2), var(--el-surface));
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
        color: color-mix(in srgb, var(--el-text) 82%, transparent);
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
        background: color-mix(in srgb, var(--el-text) 5%, transparent);
        color: color-mix(in srgb, var(--el-text) 78%, transparent);
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
        background: linear-gradient(180deg, var(--el-surface-2), var(--el-surface));
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
        color: color-mix(in srgb, var(--el-text) 88%, transparent);
        line-height: 1.55;
        margin: 0;
    }

    .el-risk-list {
        margin: 0;
        padding-left: 1.1rem;
        color: color-mix(in srgb, var(--el-text) 88%, transparent);
        line-height: 1.5;
    }

    .el-risk-list li { margin: 0.25rem 0; }

    div[data-testid="stMetric"] {
        background: linear-gradient(180deg, var(--el-surface-2), var(--el-surface));
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
        background: var(--el-surface);
        border-color: var(--el-border);
        border-radius: 14px;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid var(--el-border);
        border-radius: 16px;
        overflow: hidden;
        background: color-mix(in srgb, var(--el-surface) 88%, transparent);
    }

    div[data-testid="stExpander"] {
        border: 1px solid var(--el-border);
        border-radius: 16px;
        background: color-mix(in srgb, var(--el-surface) 82%, transparent);
    }

    div[data-testid="stAlert"] { border-radius: 14px; }

    hr {
        border-color: color-mix(in srgb, var(--el-text) 12%, transparent) !important;
        margin: 1.8rem 0 !important;
    }

    .stCaption, small { color: var(--el-muted) !important; }
    footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True
)


def get_supabase_client():
    url = st.secrets.get("SUPABASE_URL")
    anon_key = st.secrets.get("SUPABASE_ANON_KEY")
    if not url or not anon_key:
        return None
    return create_client(url, anon_key)


def render_auth_sidebar():
    supabase = get_supabase_client()

    with st.sidebar:
        st.markdown("## EquityLens Account")

        if supabase is None:
            st.caption(
                "Account sign-in is being prepared. Public research remains available without an account."
            )
            return

        if "auth_user" not in st.session_state:
            st.session_state.auth_user = None

        if st.session_state.auth_user:
            user = st.session_state.auth_user
            email = getattr(user, "email", "Signed-in user")
            st.success(f"Signed in as {email}")
            st.caption(
                "Accounts are optional. EquityLens does not use account information to provide personalized investment recommendations."
            )
            if st.button("Sign out", use_container_width=True):
                try:
                    supabase.auth.sign_out()
                except Exception:
                    pass
                st.session_state.auth_user = None
                st.rerun()
            return

        auth_mode = st.radio(
            "Account",
            ["Sign in", "Create account"],
            horizontal=True,
            key="auth_mode"
        )

        email = st.text_input(
            "Email",
            key="auth_email",
            placeholder="you@example.com"
        )
        password = st.text_input(
            "Password",
            type="password",
            key="auth_password"
        )

        if auth_mode == "Sign in":
            if st.button("Sign in", use_container_width=True, key="sign_in_button"):
                if not email or not password:
                    st.warning("Enter both an email and password.")
                else:
                    try:
                        response = supabase.auth.sign_in_with_password({
                            "email": email,
                            "password": password
                        })
                        st.session_state.auth_user = response.user
                        st.success("Signed in.")
                        st.rerun()
                    except Exception as exc:
                        st.error("Unable to sign in. Check your email and password.")
                        st.caption(str(exc))
        else:
            if st.button("Create account", use_container_width=True, key="create_account_button"):
                if not email or not password:
                    st.warning("Enter both an email and password.")
                elif len(password) < 8:
                    st.warning("Use a password with at least 8 characters.")
                else:
                    try:
                        response = supabase.auth.sign_up({
                            "email": email,
                            "password": password
                        })
                        if response.user:
                            st.session_state.auth_user = response.user
                        st.success(
                            "Account created. If email confirmation is enabled, check your inbox before signing in."
                        )
                    except Exception as exc:
                        st.error("Unable to create the account.")
                        st.caption(str(exc))

        st.caption(
            "Account creation is optional and is intended for future features such as saved companies, research notes, and preferences."
        )


render_auth_sidebar()


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
company_s1 = load_json("data/company_s1.json")
sec_filings = load_json("data/sec_filings.json")

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
            Learn how public companies work through SEC filings, standardized financials,
            quarterly and LTM performance, capital structure, risk factors, and
            peer comparisons. Built for curious users who want to understand the numbers
            before forming an opinion. EquityLens informs. You decide.
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

st.caption(
    "Public research is available without signing in. Accounts are optional and are intended for future saved research features."
)

st.info(
    "How to read EquityLens: company-reported figures are shown separately from metrics calculated by EquityLens. "
    "Educational explanations define the terms in plain language, and source links point back to the original filing or disclosure. "
    "EquityLens does not provide buy, sell, or hold recommendations."
)

with st.expander("Source standard & information labels"):
    st.markdown(
        """
        **Reported** — taken from a company filing or company-reported disclosure.

        **Calculated by EquityLens** — derived from reported figures, such as revenue growth, margins, or LTM metrics.

        **Educational explanation** — plain-language context that explains a financial concept without recommending an investment action.

        **Source** — the original SEC filing, investor-relations disclosure, or appropriately licensed market-data source used for the underlying information.

        **Source priority:** SEC EDGAR first, company investor-relations disclosures second, and appropriately licensed market-data providers where needed.
        """
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

peer_tab, company_tab, sec_tracker_tab, learn_tab = st.tabs([
    "Peer Comparison",
    "Company Research",
    "SEC Filing Tracker",
    "Learn the Basics"
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
            st.caption(
                "Choose any company in EquityLens to explore how it makes money, "
                "who it serves, what its platform depends on, and the risks disclosed in its filings."
            )

            risk_company = st.selectbox(
                "Choose a company to explore",
                list(company_data.keys()),
                index=(
                    list(company_data.keys()).index(selected_companies[0])
                    if selected_companies and selected_companies[0] in company_data
                    else 0
                ),
                format_func=lambda name: (
                    f"{company_data[name].get('ticker', '')} · {name.split(' (')[0]} "
                    f"— {company_data[name].get('industry', 'Unclassified')}"
                ),
                key="peer_risk_company"
            )

            risk_analysis = company_analysis.get(risk_company, {})
            risk_themes = risk_analysis.get("key_risk_themes", [])
            risk_source = risk_analysis.get(
                "source_filing",
                company_data.get(risk_company, {}).get("filing_url", "")
            )
            risk_name = risk_company.split(" (")[0]
            risk_ticker = company_data.get(risk_company, {}).get("ticker", "")
            risk_industry = company_data.get(risk_company, {}).get(
                "industry", "Unclassified"
            )

            st.markdown(
                f"""
                <div class="el-company-hero">
                    <div class="el-kicker">{risk_ticker} · {risk_industry}</div>
                    <div class="el-company-title">{risk_name}</div>
                    <p class="el-subtitle">{risk_analysis.get('business_model', 'Business model information is not available.')}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            risk_left, risk_right = st.columns(2)

            with risk_left:
                st.markdown(
                    f"""
                    <div class="el-risk-card">
                        <div class="el-risk-title">How the company makes money</div>
                        <p class="el-change-copy">{risk_analysis.get('primary_revenue_source', 'N/A')}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.markdown(
                    f"""
                    <div class="el-risk-card">
                        <div class="el-risk-title">Who it serves</div>
                        <p class="el-change-copy">{risk_analysis.get('customer_type', 'N/A')}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.markdown(
                    f"""
                    <div class="el-risk-card">
                        <div class="el-risk-title">Platform dependency</div>
                        <p class="el-change-copy">{risk_analysis.get('platform_dependency', 'N/A')}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with risk_right:
                st.markdown(
                    f"""
                    <div class="el-risk-card">
                        <div class="el-risk-title">Competitive risk</div>
                        <p class="el-change-copy">{risk_analysis.get('competitive_risk', 'N/A')}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.markdown(
                    f"""
                    <div class="el-risk-card">
                        <div class="el-risk-title">Operational risk</div>
                        <p class="el-change-copy">{risk_analysis.get('operational_risk', 'N/A')}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.markdown(
                    f"""
                    <div class="el-risk-card">
                        <div class="el-risk-title">Profitability history</div>
                        <p class="el-change-copy">{risk_analysis.get('profitability_history', 'N/A')}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            if risk_themes:
                st.markdown("**Key risk themes disclosed or summarized from company filings**")
                theme_cols = st.columns(min(3, len(risk_themes)))
                for idx, theme in enumerate(risk_themes):
                    with theme_cols[idx % len(theme_cols)]:
                        st.markdown(
                            f"""
                            <div class="el-risk-card">
                                <div class="el-risk-title">{theme}</div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

            extra_left, extra_right = st.columns(2)
            with extra_left:
                st.markdown("**Customer concentration**")
                st.write(risk_analysis.get("customer_concentration", "N/A"))
            with extra_right:
                st.markdown("**International exposure**")
                st.write(risk_analysis.get("international_exposure", "N/A"))

            if risk_source:
                st.caption("Source: company SEC filing")
                st.link_button(
                    "Open source filing",
                    risk_source,
                    key=f"risk_source_selected_{risk_ticker}"
                )

            st.caption(
                "This section summarizes publicly disclosed company information for educational research. "
                "It does not rate the company or recommend buying, selling, or holding its securities."
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

    filing_feed = sec_filings.get(research_company, {})
    recent_sec_filings = filing_feed.get("filings", [])
    if recent_sec_filings:
        section("Live SEC Monitor", "Recent SEC Filings")
        st.caption(
            "Automatically refreshed from the SEC submissions API every 15 minutes. "
            "Scheduled GitHub Actions can occasionally run late, so a newly disseminated filing may take a little longer to appear."
        )

        filing_rows = []
        for filing in recent_sec_filings[:8]:
            filing_rows.append({
                "Filed": filing.get("filing_date", ""),
                "Form": filing.get("form", ""),
                "Description": filing.get("description", "") or filing.get("primary_document", ""),
                "SEC Filing": filing.get("url", "")
            })

        st.dataframe(
            pd.DataFrame(filing_rows),
            use_container_width=True,
            hide_index=True,
            column_config={
                "SEC Filing": st.column_config.LinkColumn(
                    "SEC Filing",
                    display_text="Open filing"
                )
            }
        )
        st.caption(
            "This feed surfaces newly posted filings automatically. Financial metrics and qualitative analysis "
            "are updated separately when the filing contains data that can be standardized reliably."
        )


    source_cols = st.columns(2)
    with source_cols[0]:
        st.caption("Primary annual source")
        if data.get("filing_url"):
            st.link_button("Open latest 10-K / annual filing", data.get("filing_url"))
        else:
            st.write("Source not available")
    with source_cols[1]:
        st.caption("Primary quarterly source")
        if qdata.get("source_filing"):
            st.link_button("Open latest quarterly / source filing", qdata.get("source_filing"))
        else:
            st.write("Source not available")

    st.caption(
        "Reported figures come from the linked company filings. Growth rates, margins, and LTM values shown in EquityLens may be calculated from those reported figures."
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

    section("IPO History", "What the S-1 Said")
    s1 = company_s1.get(research_company, {})
    if s1:
        st.caption(
            "An S-1 is the registration statement a company files before an initial public offering. "
            "It is historical, so EquityLens uses it to show how the company originally described its business, strategy, and risks rather than as a source for current financial figures."
        )

        s1_cols = st.columns([1, 3])
        with s1_cols[0]:
            st.markdown("**Filing**")
            st.write(s1.get("form", "S-1"))
            st.markdown("**Filed**")
            st.write(s1.get("filed_date", "N/A"))
        with s1_cols[1]:
            st.markdown("**Historical IPO context**")
            st.write(s1.get("historical_context", "N/A"))
            st.markdown("**What this filing can teach you**")
            st.write(s1.get("what_to_learn", "N/A"))

        if s1.get("source_url"):
            st.caption("Primary source: SEC EDGAR S-1 registration filing")
            st.link_button(
                "Open original S-1 on SEC EDGAR",
                s1.get("source_url"),
                key=f"s1_source_{ticker}"
            )

        st.caption(
            "S-1 information is presented as historical company context. Current company facts and financial performance should be read from the latest 10-K, 10-Q, and other current filings."
        )
    else:
        st.info("No S-1 research has been added for this company yet.")

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

    section("Balanced View", "Bull Case & Bear Case Factors")
    st.caption(
        "These factors summarize reported financial trends and company disclosures. "
        "They are presented for educational research only and do not constitute a buy, sell, or hold recommendation."
    )

    bull_factors = []
    bear_factors = []

    if qm.get("yoy_growth") is not None:
        if qm["yoy_growth"] > 0:
            bull_factors.append({
                "title": "Revenue growth",
                "detail": f"Latest-quarter revenue changed {qm['yoy_growth']:+.1f}% year over year.",
                "source": "Calculated by EquityLens from reported quarterly revenue"
            })
        elif qm["yoy_growth"] < 0:
            bear_factors.append({
                "title": "Revenue growth",
                "detail": f"Latest-quarter revenue changed {qm['yoy_growth']:+.1f}% year over year.",
                "source": "Calculated by EquityLens from reported quarterly revenue"
            })

    if qm.get("operating_margin") is not None and qm.get("prior_q_operating_margin") is not None:
        margin_delta = qm["operating_margin"] - qm["prior_q_operating_margin"]
        factor = {
            "title": "Operating margin trend",
            "detail": (
                f"Operating margin changed {margin_delta:+.1f} percentage points sequentially, "
                f"from {qm['prior_q_operating_margin']:.1f}% to {qm['operating_margin']:.1f}%."
            ),
            "source": "Calculated by EquityLens from reported operating income and revenue"
        }
        if margin_delta > 0:
            bull_factors.append(factor)
        elif margin_delta < 0:
            bear_factors.append(factor)

    latest_net = latest.get("net_income")
    if latest_net is not None:
        if latest_net > 0:
            bull_factors.append({
                "title": "Latest net income",
                "detail": f"The latest reported quarter shows net income of {format_money(latest_net)}.",
                "source": "Reported in the latest quarterly filing"
            })
        elif latest_net < 0:
            bear_factors.append({
                "title": "Latest net income",
                "detail": f"The latest reported quarter shows a net loss of {format_money(latest_net)}.",
                "source": "Reported in the latest quarterly filing"
            })

    cash_value = capital.get("cash_and_investments")
    debt_value = capital.get("total_debt")
    if cash_value is not None and debt_value is not None:
        if cash_value > debt_value:
            bull_factors.append({
                "title": "Cash relative to debt",
                "detail": (
                    f"Reported cash and investments of {format_money(cash_value)} exceed "
                    f"reported debt of {format_money(debt_value)}."
                ),
                "source": "Reported balance-sheet figures"
            })
        elif debt_value > cash_value:
            bear_factors.append({
                "title": "Debt relative to cash",
                "detail": (
                    f"Reported debt of {format_money(debt_value)} exceeds "
                    f"cash and investments of {format_money(cash_value)}."
                ),
                "source": "Reported balance-sheet figures"
            })

    competitive_risk = analysis.get("competitive_risk")
    if competitive_risk:
        bear_factors.append({
            "title": "Competitive risk",
            "detail": competitive_risk,
            "source": "Summarized from company risk disclosures"
        })

    operational_risk = analysis.get("operational_risk")
    if operational_risk:
        bear_factors.append({
            "title": "Operational risk",
            "detail": operational_risk,
            "source": "Summarized from company risk disclosures"
        })

    profitability_history = analysis.get("profitability_history", "")
    if profitability_history:
        lowered = profitability_history.lower()
        if any(term in lowered for term in ["positive", "profitable", "narrowed", "improved"]):
            bull_factors.append({
                "title": "Profitability history",
                "detail": profitability_history,
                "source": "Summarized from company-reported results"
            })
        if any(term in lowered for term in ["loss", "losses", "unprofitable"]):
            bear_factors.append({
                "title": "Profitability history",
                "detail": profitability_history,
                "source": "Summarized from company-reported results"
            })

    factor_cols = st.columns(2)
    with factor_cols[0]:
        st.markdown("### Bull Case Factors")
        if bull_factors:
            for i, factor in enumerate(bull_factors[:5]):
                st.markdown(
                    f"""
                    <div class="el-risk-card">
                        <div class="el-risk-title">{factor['title']}</div>
                        <p class="el-change-copy">{factor['detail']}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.caption(f"Source: {factor['source']}")
        else:
            st.info("No positive factor is being highlighted from the current structured dataset.")

    with factor_cols[1]:
        st.markdown("### Bear Case Factors")
        if bear_factors:
            for i, factor in enumerate(bear_factors[:5]):
                st.markdown(
                    f"""
                    <div class="el-risk-card">
                        <div class="el-risk-title">{factor['title']}</div>
                        <p class="el-change-copy">{factor['detail']}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.caption(f"Source: {factor['source']}")
        else:
            st.info("No risk factor is being highlighted from the current structured dataset.")

    filing_source = qdata.get("source_filing") or data.get("filing_url")
    if filing_source:
        st.link_button(
            "Open supporting SEC filing",
            filing_source,
            key=f"balanced_view_source_{ticker}"
        )

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

with sec_tracker_tab:
    section("SEC Monitor", "Filing Tracker")

    st.write(
        "This tracker combines the recent SEC filings collected for every company covered by EquityLens. "
        "It records the issuer, ticker, form, SEC filing date, SEC acceptance timestamp when available, "
        "the period the filing covers, when EquityLens first detected it, and a direct link to the original filing."
    )

    st.caption(
        "The SEC does not publish an exact future posting time before a filing is submitted. "
        "EquityLens can track actual filings immediately after they appear and can separately add announced "
        "earnings dates or estimated filing windows later."
    )

    tracker_rows = []
    for tracked_company, feed in sec_filings.items():
        entity_name = feed.get("entity_name", tracked_company.split(" (")[0])
        tracked_ticker = feed.get("ticker", "")
        for filing in feed.get("filings", []):
            tracker_rows.append({
                "Company": entity_name,
                "Ticker": tracked_ticker,
                "Form": filing.get("form", ""),
                "SEC Filed Date": filing.get("filing_date", ""),
                "SEC Accepted": filing.get("acceptance_datetime", ""),
                "Report Period": filing.get("report_date", ""),
                "Description": filing.get("description", "") or filing.get("primary_document", ""),
                "Items": filing.get("items", ""),
                "First Seen by EquityLens (UTC)": filing.get("first_seen_utc", ""),
                "Accession Number": filing.get("accession_number", ""),
                "SEC Filing": filing.get("url", "")
            })

    tracker_df = pd.DataFrame(tracker_rows)

    if tracker_df.empty:
        st.info("The filing tracker is waiting for the SEC monitor to populate data.")
    else:
        tracker_df = tracker_df.sort_values(
            by=["SEC Filed Date", "SEC Accepted"],
            ascending=False,
            na_position="last"
        )

        filter_cols = st.columns(2)
        with filter_cols[0]:
            tracker_company = st.selectbox(
                "Company",
                ["All companies"] + sorted(tracker_df["Company"].dropna().unique().tolist()),
                key="sec_tracker_company"
            )
        with filter_cols[1]:
            form_options = sorted(
                [form for form in tracker_df["Form"].dropna().unique().tolist() if form]
            )
            tracker_forms = st.multiselect(
                "Filing type",
                form_options,
                default=[],
                key="sec_tracker_forms"
            )

        filtered_tracker = tracker_df.copy()
        if tracker_company != "All companies":
            filtered_tracker = filtered_tracker[
                filtered_tracker["Company"] == tracker_company
            ]
        if tracker_forms:
            filtered_tracker = filtered_tracker[
                filtered_tracker["Form"].isin(tracker_forms)
            ]

        st.dataframe(
            filtered_tracker,
            use_container_width=True,
            hide_index=True,
            column_config={
                "SEC Filing": st.column_config.LinkColumn(
                    "SEC Filing",
                    display_text="Open filing"
                )
            }
        )

        st.download_button(
            "Download filing tracker as CSV",
            data=filtered_tracker.to_csv(index=False).encode("utf-8"),
            file_name="equitylens_sec_filing_tracker.csv",
            mime="text/csv",
            use_container_width=True
        )

        st.caption(
            f"Showing {len(filtered_tracker):,} filing records from the current monitored set. "
            "The monitor checks for new SEC submissions every 15 minutes."
        )


with learn_tab:
    section("Learning", "Understand the Numbers")
    st.write(
        "EquityLens is designed for users who are still learning how to read public-company information. "
        "The goal is to explain what a metric measures, show the reported or calculated value, and make the original source easy to inspect."
    )

    learning_items = [
        {
            "term": "Revenue",
            "definition": "Revenue is the money a company earns from selling its products or services before expenses are deducted.",
            "why": "Revenue helps show the size of the business and whether customer demand is expanding, slowing, or shrinking over time.",
            "how": "For example, if a company reports $1.0B of revenue this year and $800M last year, sales increased by $200M. Revenue by itself does not tell you whether the company was profitable.",
            "watch": "Look at revenue together with growth rates, margins, customer trends, and whether growth is coming from recurring business or one-time activity."
        },
        {
            "term": "Year-over-Year (YoY) Growth",
            "definition": "YoY growth measures how much a financial metric changed compared with the same period one year earlier.",
            "why": "Comparing the same quarter across years helps reduce seasonal distortions. A retailer's fourth quarter, for example, may naturally be stronger than its third quarter.",
            "how": "Formula: (current-period value - prior-year value) ÷ prior-year value × 100. If quarterly revenue rises from $100M to $120M, YoY growth is 20%.",
            "watch": "A high growth rate can look impressive, but check whether it is accelerating or slowing and whether profitability is improving alongside it."
        },
        {
            "term": "Gross Margin",
            "definition": "Gross margin is the percentage of revenue left after subtracting the direct costs required to deliver a product or service.",
            "why": "It gives a basic view of the economics of what a company sells. Higher gross margins generally mean more revenue remains to pay operating expenses such as research, sales, and administration.",
            "how": "Formula: gross profit ÷ revenue × 100. If revenue is $100M and gross profit is $75M, gross margin is 75%.",
            "watch": "Compare margins with the company's own history and similar businesses. Different industries naturally have very different gross-margin structures."
        },
        {
            "term": "Operating Margin",
            "definition": "Operating margin shows how much operating profit or loss a company produces after core operating expenses such as research and development, sales and marketing, and administration.",
            "why": "It helps show whether the core business is becoming more or less efficient as it grows.",
            "how": "Formula: operating income ÷ revenue × 100. If revenue is $100M and operating income is $10M, operating margin is 10%. If operating income is -$10M, the margin is -10%.",
            "watch": "An improving operating margin may indicate better cost discipline or operating leverage, but one quarter should not be treated as a long-term trend."
        },
        {
            "term": "Net Income",
            "definition": "Net income is the company's final reported profit or loss after operating expenses, interest, taxes, and other reported gains or losses.",
            "why": "It is commonly called the bottom line because it shows what remains after the major expenses and non-operating items recognized during the period.",
            "how": "A company can have positive operating results but lower net income because of interest or taxes, or it can report positive net income because of a one-time gain.",
            "watch": "Read net income alongside operating income and cash flow. Large one-time tax benefits, investment gains, restructuring charges, or other unusual items can make a single period less representative."
        },
        {
            "term": "LTM / Trailing Twelve Months",
            "definition": "LTM combines the most recent twelve months of financial results, usually using the latest four reported quarters.",
            "why": "It gives a more current full-year view than an older annual report when one or more newer quarters have already been released.",
            "how": "If a company's latest 10-K ended six months ago, LTM can combine the newer quarterly results with the remaining quarters needed to create a rolling twelve-month total.",
            "watch": "LTM is calculated rather than a separate SEC reporting period. Always check which quarters are included, especially when comparing companies with different fiscal year-ends."
        },
        {
            "term": "10-K",
            "definition": "A 10-K is the detailed annual report that most U.S. public companies file with the SEC.",
            "why": "It is one of the most important primary sources for understanding a company because it includes audited annual financial statements, the business description, risk factors, management discussion, and other disclosures.",
            "how": "Useful sections include Business, Risk Factors, MD&A, Financial Statements and Notes, and information about debt, stock-based compensation, customers, and accounting policies.",
            "watch": "A 10-K is comprehensive but backward-looking. Pair it with newer 10-Q and 8-K filings so you are not relying on an outdated picture."
        },
        {
            "term": "10-Q",
            "definition": "A 10-Q is the quarterly report that most U.S. public companies file with the SEC for the first three fiscal quarters of the year.",
            "why": "It provides more recent financial statements and management commentary between annual 10-K filings.",
            "how": "A 10-Q can help you compare the newest quarter with the prior quarter and the same quarter a year earlier, while also showing changes in the balance sheet and cash flow.",
            "watch": "Quarterly figures can be seasonal or volatile. Compare them with prior periods and read the accompanying notes rather than judging a company from one number."
        },
        {
            "term": "Cash + Investments",
            "definition": "Cash and investments represent liquid financial resources reported on the balance sheet, although the exact categories included can vary by company.",
            "why": "These resources can help fund operations, acquisitions, debt repayment, share repurchases, or investment during periods when cash generation is weak.",
            "how": "EquityLens combines selected reported cash and investment balances when the underlying filing provides enough information to do so consistently.",
            "watch": "Do not treat every investment as identical to cash. Some securities may have different maturities, restrictions, or liquidity characteristics."
        },
        {
            "term": "Debt",
            "definition": "Debt is borrowed capital that the company is obligated to repay under specified terms.",
            "why": "Debt can finance growth or acquisitions, but it also creates repayment obligations and often interest expense.",
            "how": "When reviewing debt, compare it with cash, operating cash generation, maturity dates, interest rates, and the company's ability to refinance or repay it.",
            "watch": "Debt is not automatically negative, and zero debt is not automatically superior. Its significance depends on the company's business model, cash flow, cost of capital, and financial flexibility."
        }
    ]

    for item in learning_items:
        with st.expander(item["term"]):
            st.markdown("**What it means**")
            st.write(item["definition"])
            st.markdown("**Why it matters**")
            st.write(item["why"])
            st.markdown("**How to think about it**")
            st.write(item["how"])
            st.markdown("**What to watch for**")
            st.write(item["watch"])

    section("Source Guide", "How EquityLens Labels Information")
    st.markdown(
        """
        **Reported** — a figure taken from a company filing or company-reported disclosure.

        **Calculated by EquityLens** — a metric computed from reported figures, such as revenue growth or operating margin.

        **Educational explanation** — plain-language context explaining what a financial term means. It is not a buy, sell, or hold recommendation.

        **Source** — the original filing or disclosure used for the underlying information. When available, EquityLens links directly to the filing so users can verify the data themselves.
        """
    )

    st.info(
        "EquityLens does not rate companies, predict returns, or tell users what securities to buy or sell. "
        "It is designed to help users understand public information and perform their own research."
    )

    section("Learning Resources", "Curated Video Lessons")
    st.write(
        "These external videos are included as supplemental education from established investors, "
        "finance educators, and primary creators. EquityLens links to the original uploader and does "
        "not reproduce or claim ownership of their content. Inclusion is not an endorsement of every "
        "view expressed in a video, and the videos should not be treated as personalized investment advice."
    )

    video_resources = [
        {
            "title": "Valuation: A Preview",
            "creator": "Aswath Damodaran",
            "credit": "Professor of Finance, NYU Stern; original YouTube uploader",
            "url": "https://www.youtube.com/watch?v=LYGYvN5LUbA",
            "why": (
                "A useful introduction to how valuation combines financial numbers with a business story, "
                "and why value and market price are not the same thing."
            ),
            "topics": "Valuation, business fundamentals, price vs. value"
        },
        {
            "title": "Introduction to Valuation Class",
            "creator": "Aswath Damodaran",
            "credit": "Professor of Finance, NYU Stern; original YouTube uploader",
            "url": "https://www.youtube.com/watch?v=oi6M5KBWydg",
            "why": (
                "Introduces the basic logic behind valuing companies and the role of assumptions, "
                "financial statements, and judgment."
            ),
            "topics": "Valuation foundations, financial analysis"
        },
        {
            "title": "Passing Along My Investment and Economic Principles",
            "creator": "Ray Dalio",
            "credit": "Principles by Ray Dalio; original YouTube uploader",
            "url": "https://www.youtube.com/watch?v=y5LyVSQq3Wc",
            "why": (
                "A high-level perspective on how an experienced institutional investor thinks about "
                "investment principles, economics, diversification, and decision-making."
            ),
            "topics": "Investment principles, economics, portfolio thinking"
        },
        {
            "title": "How To Read An Annual Report (10-K)",
            "creator": "Hamish Hodder",
            "credit": "Hamish Hodder; original YouTube uploader",
            "url": "https://www.youtube.com/watch?v=Q0o9S0q0Rr4",
            "why": (
                "Walks through how a long-term investor approaches a 10-K and which sections can help "
                "a reader understand a company's business and financial condition."
            ),
            "topics": "10-Ks, annual reports, fundamental research"
        }
    ]

    for resource in video_resources:
        with st.expander(f"▶ {resource['title']} — {resource['creator']}"):
            st.write(resource["why"])
            st.caption(f"Topics: {resource['topics']}")
            st.caption(f"Credit: {resource['credit']}")
            st.link_button(
                "Watch on the original YouTube channel",
                resource["url"],
                key=f"learning_video_{resource['title']}"
            )

    st.caption(
        "External learning resources remain the property of their respective creators and platforms. "
        "EquityLens provides outbound links and attribution only. Video availability, titles, and content "
        "may change at the creator's discretion."
    )

st.markdown("---")
section("Methodology", "Data Sources")
st.markdown(
    """
    **Source priority**

    1. SEC EDGAR filings, including Forms 10-K, 10-Q, 8-K, and S-1
    2. Company investor-relations materials and company-reported disclosures
    3. Market-data providers only where the relevant licensing and exchange permissions allow use

    EquityLens distinguishes company-reported figures from metrics calculated inside the app. Material figures should include a reporting period and a link to the original source whenever available.
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

st.markdown("---")
st.markdown(
    """
    **© 2026 Keya Dhanani. All rights reserved.**

    EquityLens AI was independently designed and developed by Keya Dhanani. Original
    application code, user-interface design, written explanations, project-specific
    research structure, and documentation are proprietary unless otherwise stated.

    Public SEC filings, company disclosures, trademarks, company names, and third-party
    source materials remain the property of their respective owners. EquityLens cites
    or links to original sources where applicable and does not claim ownership of those
    underlying materials.

    Unauthorized reproduction, redistribution, republishing, or creation of a
    substantially similar copy of the original EquityLens AI application or its
    original written content is not permitted except where allowed by applicable law
    or platform terms.
    """
)

