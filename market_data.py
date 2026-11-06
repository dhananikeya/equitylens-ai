import io
from datetime import datetime, timezone

import pandas as pd
import requests
import streamlit as st
import yfinance as yf


@st.cache_data(ttl=300)
def get_live_market_data(symbols):
    """Fetch current-ish quote data from Yahoo Finance via yfinance."""
    symbols = [str(symbol).strip().upper() for symbol in symbols if symbol]
    if not symbols:
        return {}

    quotes = {}
    for symbol in symbols:
        try:
            history = yf.Ticker(symbol).history(
                period="5d",
                interval="1d",
                auto_adjust=False
            )
        except Exception:
            continue

        if history is None or history.empty:
            continue

        history = history.dropna(subset=["Close"])
        if history.empty:
            continue

        latest = history.iloc[-1]
        previous_close = (
            float(history.iloc[-2]["Close"])
            if len(history) >= 2 and pd.notna(history.iloc[-2]["Close"])
            else None
        )
        close = float(latest["Close"]) if pd.notna(latest.get("Close")) else None
        open_price = float(latest["Open"]) if pd.notna(latest.get("Open")) else None
        volume = float(latest["Volume"]) if pd.notna(latest.get("Volume")) else None

        percent_change = None
        if close is not None and previous_close not in (None, 0):
            percent_change = ((close - previous_close) / previous_close) * 100

        quotes[symbol] = {
            "symbol": symbol,
            "close": close,
            "open": open_price,
            "previous_close": previous_close,
            "percent_change": percent_change,
            "quote_session": pd.Timestamp(history.index[-1]).date().isoformat(),
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "volume": volume
        }

    return quotes


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

        response = requests.get(
            str(api_url),
            params=params,
            headers=headers,
            timeout=30
        )
    elif export_url:
        response = requests.get(
            str(export_url),
            headers=headers,
            timeout=30
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


