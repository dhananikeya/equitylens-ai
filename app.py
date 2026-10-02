import json
import requests
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="EquityLens AI",
    page_icon="📊",
    layout="wide"
)


@st.cache_data
def load_company_data():
    with open("data/company_metrics.json", "r") as file:
        return json.load(file)


@st.cache_data
def load_company_analysis():
    with open("data/company_analysis.json", "r") as file:
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
public_market_data_enabled = bool(st.secrets.get("PUBLIC_MARKET_DATA_ENABLED", False))

st.title("EquityLens AI")

st.subheader(
    "AI-powered capital markets research using SEC filings, financial data, and market-data integrations"
)

st.write(
    """
    EquityLens AI helps users compare public companies using financial metrics,
    SEC filings, risk factors, capital-structure data, and market-data integrations.
    """
)

st.markdown("---")
st.header("Industry Comparison")
st.markdown("**Industry:** Cloud & Data Infrastructure Software")

selected_companies = st.multiselect(
    "Select companies to compare",
    list(company_data.keys()),
    default=[
        "Rubrik (RBRK)",
        "Snowflake (SNOW)",
        "MongoDB (MDB)"
    ]
)


st.subheader("Capital Structure Snapshot")

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

            st.subheader("Live Market Snapshot")

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


            st.subheader("Trading Comps")

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

        st.subheader("Financial Comparison")
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
        st.subheader("Three-Year Revenue Trend")

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

        st.subheader("Three-Year Operating Margin Trend")

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
st.subheader("Risk & Business Model Comparison")

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
        st.markdown(f"**{company}**")
        if themes:
            for theme in themes:
                st.write(f"• {theme}")
        else:
            st.write("Qualitative analysis not added yet.")

        source = analysis.get("source_filing")
        if source:
            st.markdown(f"[Open source filing]({source})")


st.markdown("---")
st.subheader("Data Sources")
st.write(
    """
    - SEC EDGAR filings, including Forms 10-K, 10-Q, 8-K, and S-1
    - Company-reported financial statements and disclosures
    - Market data integrations may be used in private development environments,
      subject to provider licensing and exchange entitlements
    """
)

st.subheader("Important Disclosures")
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
