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
    /* EquityLens visual system */
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

    .el-kicker {
        color: var(--el-teal);
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }

    .el-title {
        font-size: clamp(2.2rem, 5vw, 4.2rem);
        line-height: 0.98;
        font-weight: 800;
        letter-spacing: -0.04em;
        color: var(--el-text);
        margin: 0 0 0.8rem 0;
    }

    .el-title span {
        color: var(--el-teal);
    }

    .el-subtitle {
        max-width: 850px;
        font-size: 1.06rem;
        line-height: 1.7;
        color: #C7D2E1;
        margin: 0;
    }

    .el-badges {
        display: flex;
        flex-wrap: wrap;
        gap: 0.55rem;
        margin-top: 1.25rem;
    }

    .el-badge {
        padding: 0.42rem 0.7rem;
        border-radius: 999px;
        border: 1px solid var(--el-border);
        background: rgba(255,255,255,0.035);
        color: #CBD5E1;
        font-size: 0.78rem;
        font-weight: 600;
    }

    .el-risk-card {
        margin: 0.65rem 0 1rem 0;
        padding: 1rem 1.1rem;
        border: 1px solid var(--el-border);
        border-radius: 16px;
        background: rgba(17,35,56,0.58);
    }

    .el-risk-title {
        color: var(--el-text);
        font-size: 1.05rem;
        font-weight: 800;
        margin-bottom: 0.65rem;
    }

    .el-risk-list {
        margin: 0;
        padding-left: 1.15rem;
        color: #D8E2EE;
        line-height: 1.55;
    }

    .el-risk-list li {
        margin: 0.28rem 0;
    }

    .el-risk-source {
        display: inline-block;
        margin-top: 0.8rem;
        color: var(--el-blue);
        font-size: 0.86rem;
        font-weight: 700;
        text-decoration: none;
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

    div[data-testid="stMetric"] {
        background: linear-gradient(180deg, rgba(17,35,56,0.96), rgba(13,27,42,0.96));
        border: 1px solid var(--el-border);
        border-radius: 18px;
        padding: 1rem 1.1rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.14);
    }

    div[data-testid="stMetricLabel"] {
        color: var(--el-muted);
    }

    div[data-testid="stMetricValue"] {
        color: var(--el-text);
        font-weight: 750;
    }

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

    div[data-testid="stAlert"] {
        border-radius: 14px;
    }

    hr {
        border-color: rgba(148, 163, 184, 0.12) !important;
        margin: 1.8rem 0 !important;
    }

    .stCaption, small {
        color: var(--el-muted) !important;
    }

    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)


@st.cache_data(ttl=60)
def load_company_data():
    with open("data/company_metrics.json", "r") as file:
        return json.load(file)


@st.cache_data(ttl=60)
def load_company_analysis():
    with open("data/company_analysis.json", "r") as file:
        return json.load(file)


@st.cache_data(ttl=60)
def load_company_quarterly():
    with open("data/company_quarterly.json", "r") as file:
        return json.load(file)


@st.cache_data(ttl=300)
def get_live_market_data(symbols):
    # Prefer the correctly named secret. The fallback keeps the app working
    # if the existing Twelve Data key was previously saved under the old name.
    api_key = st.secrets.get(
        "TWELVE_DATA_API_KEY",
        st.secrets.get("FINIMPULSE_API_KEY")
    )

    if not api_key:
        raise ValueError(
            "Missing Twelve Data API key in Streamlit Secrets."
        )

    url = "https://api.twelvedata.com/quote"
    params = {
        "symbol": ",".join(symbols),
        "apikey": api_key
    }

    response = requests.get(
        url,
        params=params,
        timeout=20
    )
    response.raise_for_status()

    body = response.json()

    # Twelve Data returns a single quote object for one symbol and a mapping
    # keyed by ticker when several symbols are requested.
    if isinstance(body, dict) and body.get("status") == "error":
        raise ValueError(body.get("message", "Twelve Data API error"))

    if len(symbols) == 1 and isinstance(body, dict) and body.get("symbol"):
        body = {symbols[0]: body}

    market_data = {}
    for symbol in symbols:
        item = body.get(symbol, {}) if isinstance(body, dict) else {}

        if isinstance(item, dict) and item.get("status") == "error":
            continue

        market_data[symbol] = item

    return market_data


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


company_data = load_company_data()
company_analysis = load_company_analysis()
company_quarterly = load_company_quarterly()
public_market_data_enabled = bool(st.secrets.get("PUBLIC_MARKET_DATA_ENABLED", False))

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
            <span class="el-badge">Peer comparison</span>
            <span class="el-badge">Neutral research</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

coverage_cols = st.columns(4)

summary_cards = [
    ("Companies Covered", str(len(company_data))),
    ("Industry", "Cloud & Data Infrastructure Software"),
    ("Latest Data", "Q2 2026 / FY2027"),
    (
        "Market Data",
        "Private Live" if public_market_data_enabled else "Public Filing Mode"
    )
]

for col, (label, value) in zip(coverage_cols, summary_cards):
    with col:
        st.markdown(
            f"""
            <div style="
                min-height: 150px;
                padding: 1.25rem 1.35rem;
                border: 1px solid rgba(148, 163, 184, 0.18);
                border-radius: 20px;
                background: linear-gradient(180deg, rgba(17,35,56,0.96), rgba(13,27,42,0.96));
                box-shadow: 0 10px 30px rgba(0,0,0,0.14);
                display: flex;
                flex-direction: column;
                justify-content: center;
            ">
                <div style="
                    color: #94A3B8;
                    font-size: 0.92rem;
                    font-weight: 650;
                    margin-bottom: 0.65rem;
                ">{label}</div>
                <div style="
                    color: #EAF2F8;
                    font-size: 2rem;
                    line-height: 1.2;
                    font-weight: 800;
                    letter-spacing: -0.03em;
                    white-space: normal;
                    overflow-wrap: anywhere;
                ">{value}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

st.markdown(
    """
    <div class="el-section">
        <div class="el-section-label">Peer Research</div>
        <div class="el-section-title">Industry Comparison</div>
    </div>
    """,
    unsafe_allow_html=True
)
st.caption("Cloud & Data Infrastructure Software")

selected_companies = st.multiselect(
    "Select companies to compare",
    list(company_data.keys()),
    default=[
        "Rubrik (RBRK)",
        "Snowflake (SNOW)",
        "MongoDB (MDB)"
    ]
)


st.markdown(
    """
    <div class="el-section">
        <div class="el-section-label">Balance Sheet</div>
        <div class="el-section-title">Capital Structure Snapshot</div>
    </div>
    """,
    unsafe_allow_html=True
)

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
        "Cash + Investments": format_money(capital.get("cash_and_investments")),
        "Balance Sheet Date": capital.get("balance_sheet_as_of", "N/A"),
        "Capital Structure Source": capital.get("source_filing", "")
    })

st.dataframe(
    pd.DataFrame(capital_rows),
    use_container_width=True,
    hide_index=True,
    column_config={
        "Capital Structure Source": st.column_config.LinkColumn(
            "Source",
            display_text="Open filing"
        )
    }
)

st.caption(
    "Capital structure uses the latest available public filing for each company. "
    "Share counts and balance-sheet dates can differ slightly."
)

if st.button("Run Comparison"):
    if len(selected_companies) < 2:
        st.warning("Please select at least two companies to compare.")
    else:
        if public_market_data_enabled:
            symbols = [company_data[company]["ticker"] for company in selected_companies]

            try:
                live_market = get_live_market_data(symbols)
            except Exception as e:
                live_market = {}
                st.warning(
                    "Live market data is temporarily unavailable. "
                    "The filing-based comparison below is still available."
                )
                st.caption(str(e))

            st.markdown("""<div class="el-section"><div class="el-section-label">Market</div><div class="el-section-title">Live Market Snapshot</div></div>""", unsafe_allow_html=True)

            st.markdown("**Current Price Direction**")
            price_columns = st.columns(len(selected_companies))

            for idx, company in enumerate(selected_companies):
                ticker = company_data[company]["ticker"]
                market = live_market.get(ticker, {})
                close = market.get("close")
                percent_change = market.get("percent_change")

                price_text = (
                    f"$" + f"{float(close):,.2f}"
                    if close not in (None, "")
                    else "N/A"
                )

                delta_text = None
                if percent_change not in (None, ""):
                    try:
                        delta_text = f"{float(percent_change):.2f}%"
                    except (TypeError, ValueError):
                        delta_text = None

                price_columns[idx].metric(
                    label=ticker,
                    value=price_text,
                    delta=delta_text,
                    delta_color="normal"
                )

            st.caption(
                "Green indicates a positive daily change, red indicates a negative daily change, "
                "and no color indicates unavailable or unchanged market data."
            )

            market_rows = []
            for company in selected_companies:
                ticker = company_data[company]["ticker"]
                market = live_market.get(ticker, {})

                fifty_two_week = market.get("fifty_two_week", {})
                if not isinstance(fifty_two_week, dict):
                    fifty_two_week = {}

                close = market.get("close")
                percent_change = market.get("percent_change")
                volume = market.get("volume")

                market_rows.append({
                    "Company": company,
                    "Price": (
                        f"$" + f"{float(close):,.2f}"
                        if close not in (None, "")
                        else "N/A"
                    ),
                    "Daily Change": (
                        f"{float(percent_change):.2f}%"
                        if percent_change not in (None, "")
                        else "N/A"
                    ),
                    "52W Low": (
                        f"$" + f"{float(fifty_two_week.get('low')):,.2f}"
                        if fifty_two_week.get("low") not in (None, "")
                        else "N/A"
                    ),
                    "52W High": (
                        f"$" + f"{float(fifty_two_week.get('high')):,.2f}"
                        if fifty_two_week.get("high") not in (None, "")
                        else "N/A"
                    ),
                    "Volume": (
                        f"{int(float(volume)):,}"
                        if volume not in (None, "")
                        else "N/A"
                    ),
                    "Price Updated": market.get("datetime", "N/A"),
                    "Exchange": market.get("exchange", "N/A")
                })

            st.dataframe(
                pd.DataFrame(market_rows),
                use_container_width=True,
                hide_index=True
            )

            st.caption(
                "Market data is provided by Twelve Data. Availability and latency depend "
                "on the Twelve Data plan and exchange entitlements."
            )


            st.markdown("""<div class="el-section"><div class="el-section-label">Valuation</div><div class="el-section-title">Trading Comps</div></div>""", unsafe_allow_html=True)

            comps_rows = []
            for company in selected_companies:
                ticker = company_data[company]["ticker"]
                market = live_market.get(ticker, {})
                close = market.get("close")
                capital = company_data[company].get("capital_structure", {})
                shares = capital.get("shares_outstanding")
                debt = capital.get("total_debt")
                cash_and_investments = capital.get("cash_and_investments")
                revenue = company_data[company].get("revenue")

                price = float(close) if close not in (None, "") else None
                market_cap = (
                    price * shares
                    if price is not None and shares is not None
                    else None
                )
                enterprise_value = (
                    market_cap + debt - cash_and_investments
                    if market_cap is not None
                    and debt is not None
                    and cash_and_investments is not None
                    else None
                )
                price_to_sales = (
                    market_cap / revenue
                    if market_cap is not None and revenue
                    else None
                )
                ev_to_revenue = (
                    enterprise_value / revenue
                    if enterprise_value is not None and revenue
                    else None
                )

                comps_rows.append({
                    "Company": company,
                    "Market Cap": market_cap,
                    "Enterprise Value": enterprise_value,
                    "Price / Sales": price_to_sales,
                    "EV / Revenue": ev_to_revenue
                })

            comps_df = pd.DataFrame(comps_rows)

            valid_ps = comps_df["Price / Sales"].dropna()
            valid_ev_rev = comps_df["EV / Revenue"].dropna()

            peer_median_ps = valid_ps.median() if not valid_ps.empty else None
            peer_average_ps = valid_ps.mean() if not valid_ps.empty else None
            peer_median_ev_rev = valid_ev_rev.median() if not valid_ev_rev.empty else None
            peer_average_ev_rev = valid_ev_rev.mean() if not valid_ev_rev.empty else None

            display_comps = []
            for _, row in comps_df.iterrows():
                ps = row["Price / Sales"]
                ev_rev = row["EV / Revenue"]
                premium_discount = (
                    ((ev_rev / peer_median_ev_rev) - 1) * 100
                    if ev_rev is not None
                    and peer_median_ev_rev not in (None, 0)
                    else None
                )

                display_comps.append({
                    "Company": row["Company"],
                    "Market Cap": format_money(row["Market Cap"]),
                    "Enterprise Value": format_money(row["Enterprise Value"]),
                    "Price / Sales": format_multiple(ps),
                    "EV / Revenue": format_multiple(ev_rev),
                    "EV/Revenue vs Peer Median": pct(premium_discount)
                })

            st.dataframe(
                pd.DataFrame(display_comps),
                use_container_width=True,
                hide_index=True
            )

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Peer Median P/S", format_multiple(peer_median_ps))
            col2.metric("Peer Average P/S", format_multiple(peer_average_ps))
            col3.metric("Peer Median EV/Revenue", format_multiple(peer_median_ev_rev))
            col4.metric("Peer Average EV/Revenue", format_multiple(peer_average_ev_rev))

            st.caption(
                "Trading comps are descriptive, not investment recommendations. "
                "Market cap uses current market price × latest reported shares outstanding. "
                "Enterprise value uses market cap + reported debt - cash and investments. "
                "Revenue uses the latest annual figure currently stored in EquityLens."
            )
        else:
            st.info(
                "Live market data and market-price-based valuation multiples are disabled in this public demo. "
                "The capital structure and financial analysis below use publicly available SEC filings."
            )

        rows = []

        for company in selected_companies:
            data = company_data[company]

            revenue = data["revenue"]
            gross_profit = data["gross_profit"]
            operating_income = data["operating_income"]
            net_income = data["net_income"]

            gross_margin = (gross_profit / revenue) * 100 if revenue else None
            operating_margin = (operating_income / revenue) * 100 if revenue else None
            net_margin = (net_income / revenue) * 100 if revenue else None

            history = data.get("history", [])
            revenue_growth = None
            if len(history) >= 2:
                current = history[-1]["revenue"]
                prior = history[-2]["revenue"]
                if prior:
                    revenue_growth = ((current - prior) / prior) * 100

            rows.append({
                "Company": company,
                "FY": data.get("fiscal_year"),
                "Revenue": format_money(revenue),
                "YoY Revenue Growth": pct(revenue_growth),
                "Gross Profit": format_money(gross_profit),
                "Gross Margin": pct(gross_margin),
                "Operating Income": format_money(operating_income),
                "Operating Margin": pct(operating_margin),
                "Net Income": format_money(net_income),
                "Net Margin": pct(net_margin),
                "Cash": format_money(data["cash"]),
                "Assets": format_money(data["assets"]),
                "SEC Filing": data.get("filing_url", "")
            })

        df = pd.DataFrame(rows)

        st.markdown("""<div class="el-section"><div class="el-section-label">Fundamentals</div><div class="el-section-title">Financial Comparison</div></div>""", unsafe_allow_html=True)
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "SEC Filing": st.column_config.LinkColumn(
                    "SEC Filing",
                    display_text="Open 10-K"
                )
            }
        )

        st.caption(
            "Financial figures are sourced from each company's latest annual Form 10-K. "
            "Fiscal year-end dates differ by company."
        )


        st.markdown("---")
        st.markdown("""<div class="el-section"><div class="el-section-label">Earnings</div><div class="el-section-title">Quarterly & LTM Analysis</div></div>""", unsafe_allow_html=True)

        quarterly_rows = []
        ltm_rows = []

        for company in selected_companies:
            qdata = company_quarterly.get(company, {})
            latest = qdata.get("latest_quarter", {})
            prior_q = qdata.get("prior_quarter", {})
            prior_y = qdata.get("prior_year_quarter", {})
            ltm = qdata.get("ltm", {})

            revenue = latest.get("revenue")
            prior_q_revenue = prior_q.get("revenue")
            prior_y_revenue = prior_y.get("revenue")

            yoy_growth = (
                ((revenue - prior_y_revenue) / prior_y_revenue) * 100
                if revenue is not None and prior_y_revenue
                else None
            )
            qoq_growth = (
                ((revenue - prior_q_revenue) / prior_q_revenue) * 100
                if revenue is not None and prior_q_revenue
                else None
            )

            gross_margin = (
                latest.get("gross_profit") / revenue * 100
                if revenue and latest.get("gross_profit") is not None
                else None
            )
            operating_margin = (
                latest.get("operating_income") / revenue * 100
                if revenue and latest.get("operating_income") is not None
                else None
            )
            net_margin = (
                latest.get("net_income") / revenue * 100
                if revenue and latest.get("net_income") is not None
                else None
            )

            prior_q_op_margin = (
                prior_q.get("operating_income") / prior_q_revenue * 100
                if prior_q_revenue and prior_q.get("operating_income") is not None
                else None
            )
            op_margin_change = (
                operating_margin - prior_q_op_margin
                if operating_margin is not None and prior_q_op_margin is not None
                else None
            )

            quarterly_rows.append({
                "Company": company,
                "Quarter": qdata.get("quarter_label", "N/A"),
                "Revenue": format_money(revenue),
                "YoY Revenue Growth": pct(yoy_growth),
                "QoQ Revenue Growth": pct(qoq_growth),
                "Gross Margin": pct(gross_margin),
                "Operating Income": format_money(latest.get("operating_income")),
                "Operating Margin": pct(operating_margin),
                "QoQ Op. Margin Change": (
                    f"{op_margin_change:+.1f} pts"
                    if op_margin_change is not None
                    else "N/A"
                ),
                "Net Income": format_money(latest.get("net_income")),
                "Net Margin": pct(net_margin),
                "SEC Filing": qdata.get("source_filing", "")
            })

            ltm_revenue = ltm.get("revenue")
            ltm_rows.append({
                "Company": company,
                "LTM Revenue": format_money(ltm_revenue),
                "LTM Gross Margin": pct(
                    ltm.get("gross_profit") / ltm_revenue * 100
                    if ltm_revenue and ltm.get("gross_profit") is not None
                    else None
                ),
                "LTM Operating Income": format_money(ltm.get("operating_income")),
                "LTM Operating Margin": pct(
                    ltm.get("operating_income") / ltm_revenue * 100
                    if ltm_revenue and ltm.get("operating_income") is not None
                    else None
                ),
                "LTM Net Income": format_money(ltm.get("net_income")),
                "LTM Net Margin": pct(
                    ltm.get("net_income") / ltm_revenue * 100
                    if ltm_revenue and ltm.get("net_income") is not None
                    else None
                )
            })

        st.markdown("**Latest Quarter**")
        st.dataframe(
            pd.DataFrame(quarterly_rows),
            use_container_width=True,
            hide_index=True,
            column_config={
                "SEC Filing": st.column_config.LinkColumn(
                    "SEC Filing",
                    display_text="Open 10-Q"
                )
            }
        )

        st.caption(
            "YoY compares the latest quarter with the same quarter one year earlier. "
            "QoQ compares the latest quarter with the immediately preceding quarter. "
            "Margin changes are shown in percentage points."
        )

        st.markdown("**Trailing Twelve Months (LTM)**")
        st.dataframe(
            pd.DataFrame(ltm_rows),
            use_container_width=True,
            hide_index=True
        )

        st.caption(
            "LTM figures are calculated as latest annual results + current year-to-date "
            "results - comparable prior-year year-to-date results, using SEC filings."
        )

        st.markdown("---")
        st.markdown("""<div class="el-section"><div class="el-section-label">Trend</div><div class="el-section-title">Three-Year Revenue Trend</div></div>""", unsafe_allow_html=True)

        revenue_rows = []
        for company in selected_companies:
            for item in company_data[company].get("history", []):
                revenue_rows.append({
                    "Company": company,
                    "Fiscal Year": str(item["fiscal_year"]),
                    "Revenue": item["revenue"]
                })

        revenue_df = pd.DataFrame(revenue_rows)

        if not revenue_df.empty:
            revenue_chart = revenue_df.pivot(
                index="Fiscal Year",
                columns="Company",
                values="Revenue"
            )
            st.line_chart(revenue_chart)

        st.markdown("""<div class="el-section"><div class="el-section-label">Trend</div><div class="el-section-title">Three-Year Operating Margin Trend</div></div>""", unsafe_allow_html=True)

        margin_rows = []
        for company in selected_companies:
            for item in company_data[company].get("history", []):
                revenue = item["revenue"]
                operating_income = item["operating_income"]
                operating_margin = (
                    (operating_income / revenue) * 100
                    if revenue else None
                )

                margin_rows.append({
                    "Company": company,
                    "Fiscal Year": str(item["fiscal_year"]),
                    "Operating Margin": operating_margin
                })

        margin_df = pd.DataFrame(margin_rows)

        if not margin_df.empty:
            margin_chart = margin_df.pivot(
                index="Fiscal Year",
                columns="Company",
                values="Operating Margin"
            )
            st.line_chart(margin_chart)


st.markdown("---")
st.markdown("""<div class="el-section"><div class="el-section-label">Qualitative Research</div><div class="el-section-title">Risk & Business Model Comparison</div></div>""", unsafe_allow_html=True)

analysis_rows = []

for company in selected_companies:
    analysis = company_analysis.get(company, {})

    analysis_rows.append({
        "Company": company,
        "Business Model": analysis.get("business_model", ""),
        "Revenue Source": analysis.get("primary_revenue_source", ""),
        "Customer Type": analysis.get("customer_type", ""),
        "Platform Dependency": analysis.get("platform_dependency", ""),
        "Competitive Risk": analysis.get("competitive_risk", ""),
        "Operational Risk": analysis.get("operational_risk", ""),
        "Profitability History": analysis.get("profitability_history", ""),
        "Customer Concentration": analysis.get("customer_concentration", "")
    })

analysis_df = pd.DataFrame(analysis_rows)

st.dataframe(
    analysis_df,
    use_container_width=True,
    hide_index=True
)

with st.expander("View key risk themes"):
    for company in selected_companies:
        analysis = company_analysis.get(company, {})
        themes = analysis.get("key_risk_themes", [])
        source = analysis.get("source_filing", "")

        if themes:
            theme_items = "".join(
                f"<li>{theme}</li>" for theme in themes
            )
            source_link = (
                f'<a class="el-risk-source" href="{source}" target="_blank">'
                'Open source filing ↗</a>'
                if source else ""
            )

            st.markdown(
                f"""
                <div class="el-risk-card">
                    <div class="el-risk-title">{company}</div>
                    <ul class="el-risk-list">{theme_items}</ul>
                    {source_link}
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"""
                <div class="el-risk-card">
                    <div class="el-risk-title">{company}</div>
                    <div style="color:#94A3B8;">Risk themes are not available for this company.</div>
                </div>
                """,
                unsafe_allow_html=True
            )


st.markdown("---")
st.markdown("""<div class="el-section"><div class="el-section-label">Methodology</div><div class="el-section-title">Data Sources</div></div>""", unsafe_allow_html=True)
st.write(
    """
    - SEC EDGAR filings, including Forms 10-K, 10-Q, 8-K, and S-1
    - Company-reported financial statements and disclosures
    - Market data integrations may be used in private development environments,
      subject to provider licensing and exchange entitlements
    """
)

st.markdown("""<div class="el-section"><div class="el-section-label">Disclosure</div><div class="el-section-title">Important Disclosures</div></div>""", unsafe_allow_html=True)
st.caption(
    """
    EquityLens AI is an educational and research tool that analyzes publicly
    available financial information. It does not provide personalized investment
    advice, investment recommendations, or guarantees of future performance.

    Financial information may be delayed, incomplete, or affected by later filings
    and restatements. Users should verify material information against the original
    SEC filings and company disclosures before making financial decisions.
    """
)
