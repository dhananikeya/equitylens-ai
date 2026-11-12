APP_TITLE = "EquityLens AI"
APP_PAGE_ICON = "📊"
APP_LAYOUT = "wide"
PUBLIC_APP_URL = (
    "https://equitylens-ai-2h7rd8qluv3bc8sdqf5cu3."
    "streamlit.app/"
)

PERFORMANCE_BUDGET_MS = {
    "Home": 2000,
    "Company Research": 3000,
}
NAVIGATION_RERUN_BUDGET_MS = 1000

CACHE_TTLS = {
    "market_quotes": 300,
    "finviz_raw": 120,
    "finviz_normalized": 120,
    "market_history": 900,
    "ownership": 1800,
    "analyst": 1800,
    "financials": 1800,
    "etf_exposure": 21600,
    "sec_company": 900,
    "sec_ticker_directory": 86400,
    "macro_default": 3600,
    "rates": 3600,
    "news": 900,
}

PROVIDERS = {
    "SEC": {
        "label": "SEC EDGAR",
        "authority": "primary",
    },
    "Yahoo": {
        "label": "Yahoo Finance via yfinance",
        "authority": "supplemental",
    },
    "Treasury": {
        "label": "U.S. Treasury",
        "authority": "primary",
    },
    "NYFed": {
        "label": "Federal Reserve Bank of New York",
        "authority": "primary",
    },
    "BLS": {
        "label": "U.S. Bureau of Labor Statistics",
        "authority": "primary",
    },
    "FederalReserve": {
        "label": "Federal Reserve",
        "authority": "primary",
    },
    "Bloomberg": {
        "label": "Bloomberg linked headlines",
        "authority": "supplemental",
    },
}
