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
    api_key = st.secrets["FINIMPULSE_API_KEY"]

    url = "https://api.finimpulse.com/v1/search-lite"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "symbols": symbols,
        "quote_types": ["stock"],
        "select_identifiers": [
            "display_name",
            "current_price",
            "current_price_update_time",
            "regular_market_price_change_percent",
            "regular_market_volume",
            "amount_usd",
            "fifty_two_week_low",
            "fifty_two_week_high"
        ],
        "limit": len(symbols)
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=20
    )
    response.raise_for_status()

    body = response.json()
    result = body.get("result", [])

    if isinstance(result, dict):
        if "items" in result and isinstance(result["items"], list):
            result = result["items"]
        else:
            result = [result]

    market_data = {}
    for item in result:
        symbol = item.get("symbol")
        if symbol:
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


company_data = load_company_data()
company_analysis = load_company_analysis()

st.title("EquityLens AI")

st.subheader(
    "AI-powered capital markets research using SEC filings and live market data"
)

st.write(
    """
    EquityLens AI helps users compare public companies using financial metrics,
    SEC filings, live market data, risk factors, and AI-powered research insights.
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

if st.button("Run Comparison"):
    if len(selected_companies) < 2:
        st.warning("Please select at least two companies to compare.")
    else:
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

        market_rows = []
        for company in selected_companies:
            ticker = company_data[company]["ticker"]
            market = live_market.get(ticker, {})

            market_cap = market.get("amount_usd")
            cash = company_data[company].get("cash")

            enterprise_value = None
            if market_cap is not None and cash is not None:
                # Debt will be added to the model next. Until then, this is a
                # simplified net-cash EV estimate rather than full enterprise value.
                enterprise_value = market_cap - cash

            market_rows.append({
                "Company": company,
                "Price": (
                    f"${market.get('current_price'):,.2f}"
                    if market.get("current_price") is not None
                    else "N/A"
                ),
                "Daily Change": (
                    pct(market.get("regular_market_price_change_percent"))
                    if market.get("regular_market_price_change_percent") is not None
                    else "N/A"
                ),
                "Market Cap": format_money(market_cap),
                "52W Low": (
                    f"${market.get('fifty_two_week_low'):,.2f}"
                    if market.get("fifty_two_week_low") is not None
                    else "N/A"
                ),
                "52W High": (
                    f"${market.get('fifty_two_week_high'):,.2f}"
                    if market.get("fifty_two_week_high") is not None
                    else "N/A"
                ),
                "Volume": (
                    f"{market.get('regular_market_volume'):,}"
                    if market.get("regular_market_volume") is not None
                    else "N/A"
                ),
                "Price Updated": market.get("current_price_update_time", "N/A"),
                "Simplified EV": format_money(enterprise_value)
            })

        st.dataframe(
            pd.DataFrame(market_rows),
            use_container_width=True,
            hide_index=True
        )

        st.caption(
            "FinImpulse market prices may be delayed. Simplified EV currently equals "
            "market cap minus cash; debt will be incorporated in the next valuation upgrade."
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
