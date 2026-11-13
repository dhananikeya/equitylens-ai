import io
from datetime import datetime, timezone

import pandas as pd
import streamlit as st

from services.providers.finviz import fetch_screener
import yfinance as yf


def _quote_from_history(symbol, history, retrieved_at):
    """Normalize one symbol's OHLCV history into the EquityLens quote shape."""
    if history is None or history.empty or "Close" not in history.columns:
        return None

    usable = history.dropna(subset=["Close"])
    if usable.empty:
        return None

    latest = usable.iloc[-1]
    previous_close = (
        float(usable.iloc[-2]["Close"])
        if len(usable) >= 2 and pd.notna(usable.iloc[-2]["Close"])
        else None
    )
    close = (
        float(latest["Close"])
        if pd.notna(latest.get("Close"))
        else None
    )
    open_price = (
        float(latest["Open"])
        if pd.notna(latest.get("Open"))
        else None
    )
    volume = (
        float(latest["Volume"])
        if pd.notna(latest.get("Volume"))
        else None
    )

    percent_change = None
    if close is not None and previous_close not in (None, 0):
        percent_change = (
            (close - previous_close) / previous_close
        ) * 100

    return {
        "symbol": symbol,
        "close": close,
        "open": open_price,
        "previous_close": previous_close,
        "percent_change": percent_change,
        "quote_session": pd.Timestamp(
            usable.index[-1]
        ).date().isoformat(),
        "retrieved_at": retrieved_at,
        "volume": volume,
    }


@st.cache_data(ttl=300)
def _get_live_market_data_cached(symbols):
    """Fetch one canonical symbol tuple in a single Yahoo request when possible."""
    symbols = tuple(symbols)
    if not symbols:
        return {}

    retrieved_at = datetime.now(timezone.utc).isoformat()
    quotes = {}

    try:
        downloaded = yf.download(
            tickers=list(symbols),
            period="5d",
            interval="1d",
            auto_adjust=False,
            group_by="ticker",
            threads=True,
            progress=False,
        )

        if isinstance(downloaded, pd.DataFrame) and not downloaded.empty:
            for symbol in symbols:
                history = None
                if isinstance(downloaded.columns, pd.MultiIndex):
                    level_zero = downloaded.columns.get_level_values(0)
                    level_one = downloaded.columns.get_level_values(1)
                    if symbol in level_zero:
                        history = downloaded[symbol].copy()
                    elif symbol in level_one:
                        history = downloaded.xs(
                            symbol,
                            axis=1,
                            level=1,
                        ).copy()
                elif len(symbols) == 1:
                    history = downloaded.copy()

                quote = _quote_from_history(
                    symbol,
                    history,
                    retrieved_at,
                )
                if quote:
                    quotes[symbol] = quote
    except Exception:
        quotes = {}

    missing = [
        symbol for symbol in symbols
        if symbol not in quotes
    ]
    for symbol in missing:
        try:
            history = yf.Ticker(symbol).history(
                period="5d",
                interval="1d",
                auto_adjust=False,
            )
            quote = _quote_from_history(
                symbol,
                history,
                retrieved_at,
            )
            if quote:
                quotes[symbol] = quote
        except Exception:
            continue

    return quotes


def get_live_market_data(symbols):
    """Fetch current-ish quote data using canonicalized, batched Yahoo requests."""
    canonical_symbols = tuple(sorted({
        str(symbol).strip().upper()
        for symbol in symbols
        if str(symbol).strip()
    }))
    return _get_live_market_data_cached(canonical_symbols)


def _clear_live_market_data_cache(*_args, **_kwargs):
    """Preserve the old refresh API while clearing the canonical quote cache."""
    _get_live_market_data_cached.clear()


get_live_market_data.clear = _clear_live_market_data_cache


@st.cache_data(ttl=120)
def get_finviz_screener_data(symbols=None, filters=None):
    export_url = st.secrets.get("FINVIZ_EXPORT_URL")
    api_key = st.secrets.get("FINVIZ_API_KEY")
    configured_api_url = str(
        st.secrets.get("FINVIZ_API_URL", "")
    ).strip()
    api_url = (
        configured_api_url
        if configured_api_url.startswith(("https://", "http://"))
        else "https://elite.finviz.com/export.ashx"
    )

    headers = {"User-Agent": "EquityLens/1.0"}

    if api_key:
        params = {
            "v": "152",
            "auth": str(api_key),
            "ft": "4"
        }

        if symbols:
            params["t"] = ",".join(symbols)

        if filters:
            params["f"] = str(filters)

        response = fetch_screener(
            api_url,
            params=params,
            headers=headers,
        )
    elif export_url:
        response = fetch_screener(
            export_url,
            headers=headers,
        )
    else:
        raise ValueError(
            "The market-data connection has not been configured."
        )

    response.raise_for_status()

    payload = response.text.strip()
    if not payload:
        raise ValueError("Market-data service returned an empty response.")

    payload_start = payload[:200].lower()
    if "<html" in payload_start or "<!doctype" in payload_start:
        raise ValueError(
            "Market-data service returned an unexpected response format."
        )

    data = pd.read_csv(io.StringIO(payload))
    if data.empty:
        raise ValueError("Market-data service returned no screener rows.")

    return data


def find_finviz_column(dataframe, candidates):
    lookup = {
        str(column).strip().lower(): column
        for column in dataframe.columns
    }
    for candidate in candidates:
        match = lookup.get(candidate.strip().lower())
        if match is not None:
            return match
    return None


@st.cache_data(ttl=120, show_spinner=False)
def normalize_finviz_screener(dataframe):
    if dataframe is None or dataframe.empty:
        return pd.DataFrame()

    field_map = {
        "Ticker": ["Ticker", "Symbol"],
        "Company": ["Company", "Company Name"],
        "Sector": ["Sector"],
        "Industry": ["Industry"],
        "Market Cap": ["Market Cap", "Market Cap."],
        "P/E": ["P/E", "PE"],
        "Price": ["Price"],
        "Change": ["Change", "Change %"],
        "Volume": ["Volume", "Current Volume"],
        "Relative Volume": ["Relative Volume", "Rel Volume", "Rel Volume 20D"],
        "Perf Week": ["Perf Week", "Performance Week", "Performance 1 Week"],
        "Perf Month": ["Perf Month", "Performance Month", "Performance 1 Month"],
        "Earnings": ["Earnings", "Earnings Date"]
    }

    normalized = pd.DataFrame(index=dataframe.index)

    for target, candidates in field_map.items():
        source = find_finviz_column(dataframe, candidates)
        if source is not None:
            normalized[target] = dataframe[source]

    if "Ticker" not in normalized.columns:
        raise ValueError(
            "The market-data response does not include a Ticker/Symbol column."
        )

    normalized["Ticker"] = normalized["Ticker"].astype(str).str.upper().str.strip()
    if "Market Cap" in normalized.columns:
        normalized["Market Cap"] = normalized["Market Cap"].apply(finviz_market_cap_dollars)
    return normalized


def finviz_numeric(value):
    if value is None or pd.isna(value):
        return None

    text = str(value).strip().replace(",", "").replace("%", "")
    if not text or text in {"-", "N/A", "nan"}:
        return None

    multiplier = 1.0
    suffix = text[-1:].upper()
    if suffix == "K":
        multiplier = 1_000.0
        text = text[:-1]
    elif suffix == "M":
        multiplier = 1_000_000.0
        text = text[:-1]
    elif suffix == "B":
        multiplier = 1_000_000_000.0
        text = text[:-1]
    elif suffix == "T":
        multiplier = 1_000_000_000_000.0
        text = text[:-1]

    try:
        return float(text) * multiplier
    except ValueError:
        return None


def finviz_market_cap_dollars(value):
    """Market-screener plain market-cap values are in millions unless suffixed."""
    parsed = finviz_numeric(value)
    if parsed is None:
        return None
    text = str(value).strip()
    return parsed if text[-1:].upper() in {"K", "M", "B", "T"} else parsed * 1_000_000


@st.cache_data(ttl=900)
def get_market_history(symbol, interval="1day", outputsize=60, calendar_range=None):
    """Fetch chart history from Yahoo Finance via yfinance."""
    interval_map = {
        "15min": "15m",
        "1h": "1h",
        "1day": "1d"
    }
    yf_interval = interval_map.get(interval, "1d")

    calendar_periods = {"1M": "1mo", "3M": "3mo", "1Y": "1y", "2Y": "2y"}
    if calendar_range in calendar_periods and yf_interval == "1d":
        period = calendar_periods[calendar_range]
    elif yf_interval == "15m":
        period = "5d"
    elif yf_interval == "1h":
        period = "1mo"
    elif outputsize <= 35:
        period = "3mo"
    elif outputsize <= 140:
        period = "1y"
    else:
        period = "2y"

    history = yf.Ticker(symbol).history(
        period=period,
        interval=yf_interval,
        auto_adjust=False
    )

    if history is None or history.empty:
        return pd.DataFrame()

    history = history.reset_index()
    datetime_column = "Datetime" if "Datetime" in history.columns else "Date"
    history = history.rename(columns={
        datetime_column: "datetime",
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Volume": "volume"
    })

    wanted = [
        column for column in
        ["datetime", "open", "high", "low", "close", "volume"]
        if column in history.columns
    ]
    history = history[wanted].copy()

    if "datetime" in history.columns:
        history["datetime"] = pd.to_datetime(history["datetime"], errors="coerce")

    for column in ["open", "high", "low", "close", "volume"]:
        if column in history.columns:
            history[column] = pd.to_numeric(history[column], errors="coerce")

    history = history.dropna(subset=["datetime", "close"]).sort_values("datetime")
    if not calendar_range and outputsize and len(history) > outputsize:
        history = history.tail(outputsize)

    return history


def _yf_table(value):
    """Normalize yfinance table-like responses without failing the page."""
    try:
        if callable(value):
            value = value()
    except Exception:
        return pd.DataFrame()

    if value is None:
        return pd.DataFrame()
    if isinstance(value, pd.DataFrame):
        return value.reset_index()
    if isinstance(value, pd.Series):
        return value.to_frame().reset_index()
    if isinstance(value, dict):
        try:
            return pd.DataFrame([value])
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame()


def _yf_attribute(ticker_obj, *names):
    """Return the first yfinance attribute/method that resolves successfully."""
    for name in names:
        try:
            value = getattr(ticker_obj, name)
            if callable(value):
                value = value()
            if value is not None:
                return value
        except Exception:
            continue
    return None


@st.cache_data(ttl=1800)
def get_company_ownership_data(symbol):
    """Load supplemental public ownership tables from Yahoo Finance."""
    ticker = yf.Ticker(str(symbol).upper())
    return {
        "major": _yf_table(
            _yf_attribute(ticker, "major_holders", "get_major_holders")
        ),
        "institutional": _yf_table(
            _yf_attribute(
                ticker,
                "institutional_holders",
                "get_institutional_holders",
            )
        ),
        "mutual_fund": _yf_table(
            _yf_attribute(
                ticker,
                "mutualfund_holders",
                "get_mutualfund_holders",
            )
        ),
    }


@st.cache_data(ttl=1800)
def get_company_analyst_data(symbol):
    """Load third-party analyst summary data from Yahoo Finance."""
    ticker = yf.Ticker(str(symbol).upper())

    targets = _yf_attribute(
        ticker,
        "analyst_price_targets",
        "get_analyst_price_targets",
    )
    if isinstance(targets, pd.Series):
        targets = targets.to_dict()
    if not isinstance(targets, dict):
        targets = {}

    recommendations = _yf_table(
        _yf_attribute(
            ticker,
            "recommendations_summary",
            "get_recommendations_summary",
            "recommendations",
            "get_recommendations",
        )
    )
    upgrades = _yf_table(
        _yf_attribute(
            ticker,
            "upgrades_downgrades",
            "get_upgrades_downgrades",
        )
    )

    return {
        "targets": targets,
        "recommendations": recommendations,
        "upgrades": upgrades,
    }


def _safe_float(value):
    try:
        if value in (None, ""):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _statement_value(frame, row_names, column=None):
    """Read a numeric value from a yfinance statement using common row labels."""
    if not isinstance(frame, pd.DataFrame) or frame.empty:
        return None

    selected_column = column if column is not None else frame.columns[0]
    lookup = {str(index).strip().lower(): index for index in frame.index}

    for name in row_names:
        match = lookup.get(str(name).strip().lower())
        if match is None:
            continue
        try:
            value = frame.loc[match, selected_column]
            if isinstance(value, pd.Series):
                value = value.iloc[0]
            if pd.isna(value):
                continue
            return float(value)
        except Exception:
            continue

    return None


@st.cache_data(ttl=1800)
def get_company_financial_snapshot(symbol):
    """Supplement missing standardized financials with Yahoo Finance statement data."""
    ticker = yf.Ticker(str(symbol).upper())

    income = _yf_attribute(
        ticker,
        "income_stmt",
        "financials",
        "get_income_stmt",
    )
    quarterly_income = _yf_attribute(
        ticker,
        "quarterly_income_stmt",
        "quarterly_financials",
        "get_income_stmt",
    )
    balance = _yf_attribute(
        ticker,
        "balance_sheet",
        "get_balance_sheet",
    )
    cash_flow = _yf_attribute(
        ticker,
        "cash_flow",
        "cashflow",
        "get_cash_flow",
    )

    if not isinstance(income, pd.DataFrame):
        income = pd.DataFrame()
    if not isinstance(quarterly_income, pd.DataFrame):
        quarterly_income = pd.DataFrame()
    if not isinstance(balance, pd.DataFrame):
        balance = pd.DataFrame()
    if not isinstance(cash_flow, pd.DataFrame):
        cash_flow = pd.DataFrame()

    annual_history = []
    for column in list(income.columns)[:4]:
        try:
            fiscal_year = pd.to_datetime(column).year
        except Exception:
            fiscal_year = str(column)

        annual_history.append({
            "fiscal_year": fiscal_year,
            "revenue": _statement_value(
                income,
                ["Total Revenue", "Operating Revenue"],
                column,
            ),
            "gross_profit": _statement_value(
                income,
                ["Gross Profit"],
                column,
            ),
            "operating_income": _statement_value(
                income,
                ["Operating Income"],
                column,
            ),
            "net_income": _statement_value(
                income,
                ["Net Income", "Net Income Common Stockholders"],
                column,
            ),
        })

    annual_history = [
        row for row in annual_history
        if any(
            row.get(field) is not None
            for field in [
                "revenue",
                "gross_profit",
                "operating_income",
                "net_income",
            ]
        )
    ]
    annual_history = sorted(
        annual_history,
        key=lambda row: str(row.get("fiscal_year", "")),
    )

    quarterly_history = []
    for column in list(quarterly_income.columns)[:5]:
        try:
            period_end = pd.to_datetime(column).date().isoformat()
        except Exception:
            period_end = str(column)

        quarterly_history.append({
            "period_end": period_end,
            "revenue": _statement_value(
                quarterly_income,
                ["Total Revenue", "Operating Revenue"],
                column,
            ),
            "gross_profit": _statement_value(
                quarterly_income,
                ["Gross Profit"],
                column,
            ),
            "operating_income": _statement_value(
                quarterly_income,
                ["Operating Income"],
                column,
            ),
            "net_income": _statement_value(
                quarterly_income,
                ["Net Income", "Net Income Common Stockholders"],
                column,
            ),
        })

    quarterly_history = [
        row for row in quarterly_history
        if any(
            row.get(field) is not None
            for field in [
                "revenue",
                "gross_profit",
                "operating_income",
                "net_income",
            ]
        )
    ]
    quarterly_history = sorted(
        quarterly_history,
        key=lambda row: str(row.get("period_end", "")),
    )

    latest_income = annual_history[-1] if annual_history else {}
    latest_balance_column = balance.columns[0] if not balance.empty else None
    latest_cash_flow_column = (
        cash_flow.columns[0]
        if not cash_flow.empty
        else None
    )

    operating_cash_flow = _statement_value(
        cash_flow,
        [
            "Operating Cash Flow",
            "Total Cash From Operating Activities",
            "Cash Flow From Continuing Operating Activities",
        ],
        latest_cash_flow_column,
    )
    capital_expenditure = _statement_value(
        cash_flow,
        [
            "Capital Expenditure",
            "Capital Expenditures",
        ],
        latest_cash_flow_column,
    )
    free_cash_flow = _statement_value(
        cash_flow,
        [
            "Free Cash Flow",
        ],
        latest_cash_flow_column,
    )
    if (
        free_cash_flow is None
        and operating_cash_flow is not None
        and capital_expenditure is not None
    ):
        free_cash_flow = (
            operating_cash_flow
            + capital_expenditure
            if capital_expenditure < 0
            else operating_cash_flow
            - capital_expenditure
        )

    cash_and_investments = _statement_value(
        balance,
        [
            "Cash Cash Equivalents And Short Term Investments",
            "Cash And Short Term Investments",
            "Cash Financial",
            "Cash And Cash Equivalents",
        ],
        latest_balance_column,
    )

    total_debt = _statement_value(
        balance,
        [
            "Total Debt",
            "Long Term Debt And Capital Lease Obligation",
        ],
        latest_balance_column,
    )

    total_assets = _statement_value(
        balance,
        ["Total Assets"],
        latest_balance_column,
    )

    shares_outstanding = _statement_value(
        balance,
        [
            "Ordinary Shares Number",
            "Share Issued",
        ],
        latest_balance_column,
    )

    balance_date = ""
    if latest_balance_column is not None:
        try:
            balance_date = pd.to_datetime(latest_balance_column).date().isoformat()
        except Exception:
            balance_date = str(latest_balance_column)

    # Statement tables can omit individual rows for otherwise well-covered companies.
    # Use Yahoo summary fields only as a supplemental fallback for missing values.
    info = {}
    try:
        raw_info = ticker.info
        if isinstance(raw_info, dict):
            info = raw_info
    except Exception:
        info = {}

    if shares_outstanding is None:
        shares_outstanding = _safe_float(info.get("sharesOutstanding"))
    if total_debt is None:
        total_debt = _safe_float(info.get("totalDebt"))
    if cash_and_investments is None:
        cash_and_investments = _safe_float(info.get("totalCash"))
    if total_assets is None:
        total_assets = _safe_float(info.get("totalAssets"))

    return {
        "latest": latest_income,
        "history": annual_history,
        "quarterly_history": quarterly_history,
        "capital_structure": {
            "shares_outstanding": shares_outstanding,
            "total_debt": total_debt,
            "cash_and_investments": cash_and_investments,
            "total_assets": total_assets,
            "balance_sheet_as_of": balance_date or "Latest available",
        },
        "cash_flow": {
            "operating_cash_flow": operating_cash_flow,
            "capital_expenditure": capital_expenditure,
            "free_cash_flow": free_cash_flow,
            "cash_flow_as_of": (
                str(latest_cash_flow_column.date())
                if hasattr(
                    latest_cash_flow_column,
                    "date",
                )
                else str(
                    latest_cash_flow_column
                    or ""
                )
            ),
        },
        "source": "Yahoo Finance via yfinance",
    }


MAJOR_ETF_UNIVERSE = {
    "SPY": "SPDR S&P 500 ETF Trust",
    "QQQ": "Invesco QQQ Trust",
    "VTI": "Vanguard Total Stock Market ETF",
    "IWM": "iShares Russell 2000 ETF",
    "XLK": "Technology Select Sector SPDR Fund",
    "XLF": "Financial Select Sector SPDR Fund",
    "XLV": "Health Care Select Sector SPDR Fund",
    "XLY": "Consumer Discretionary Select Sector SPDR Fund",
    "XLP": "Consumer Staples Select Sector SPDR Fund",
    "XLI": "Industrial Select Sector SPDR Fund",
    "XLE": "Energy Select Sector SPDR Fund",
    "XLU": "Utilities Select Sector SPDR Fund",
    "SOXX": "iShares Semiconductor ETF",
    "SMH": "VanEck Semiconductor ETF",
    "IGV": "iShares Expanded Tech-Software Sector ETF",
    "XLC": "Communication Services Select Sector SPDR Fund",
    "VOX": "Vanguard Communication Services ETF",
    "FCOM": "Fidelity MSCI Communication Services Index ETF",
    "VUG": "Vanguard Growth ETF",
    "IWF": "iShares Russell 1000 Growth ETF",
    "MGK": "Vanguard Mega Cap Growth ETF",
    "SCHG": "Schwab U.S. Large-Cap Growth ETF",
    "VGT": "Vanguard Information Technology ETF",
    "ARKK": "ARK Innovation ETF",
}


@st.cache_data(ttl=21600)
def get_major_etf_exposure(symbol):
    """Check a curated set of major ETFs for the selected equity."""
    selected = str(symbol).upper().strip()
    matches = []

    for etf_symbol, etf_name in MAJOR_ETF_UNIVERSE.items():
        try:
            fund = yf.Ticker(etf_symbol).funds_data
            holdings = getattr(fund, "top_holdings", None)
            if callable(holdings):
                holdings = holdings()
            if not isinstance(holdings, pd.DataFrame) or holdings.empty:
                continue

            matched_row = None
            holding_percent = None

            index_lookup = {
                str(index_value).upper(): index_value
                for index_value in holdings.index
            }
            if selected in index_lookup:
                matched_row = holdings.loc[index_lookup[selected]]
            elif "Symbol" in holdings.columns:
                symbol_mask = (
                    holdings["Symbol"]
                    .fillna("")
                    .astype(str)
                    .str.upper()
                    == selected
                )
                if symbol_mask.any():
                    matched_row = holdings.loc[symbol_mask].iloc[0]

            if matched_row is None:
                continue

            if isinstance(matched_row, pd.DataFrame):
                matched_row = matched_row.iloc[0]

            for column in [
                "Holding Percent",
                "HoldingPercent",
                "Weight",
                "% Assets",
            ]:
                try:
                    if column in matched_row.index:
                        holding_percent = matched_row.get(column)
                        break
                except Exception:
                    pass

            matches.append({
                "ETF": etf_symbol,
                "Fund": etf_name,
                "Holding": holding_percent,
            })
        except Exception:
            continue

    return matches


