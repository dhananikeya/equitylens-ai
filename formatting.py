import pandas as pd


def safe_float(value):
    try:
        if value in (None, ""):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def format_market_price(value):
    number = safe_float(value)
    return (
        "$" + f"{number:,.2f}"
        if number is not None
        else "N/A"
    )


def format_market_volume(value):
    number = safe_float(value)
    if number is None:
        return "N/A"
    if number >= 1_000_000_000:
        return f"{number / 1_000_000_000:.2f}B"
    if number >= 1_000_000:
        return f"{number / 1_000_000:.2f}M"
    if number >= 1_000:
        return f"{number / 1_000:.1f}K"
    return f"{number:,.0f}"


def format_money(value):
    number = safe_float(value)
    if number is None:
        return "N/A"
    sign = "-" if number < 0 else ""
    number = abs(number)
    if number >= 1_000_000_000:
        return sign + "$" + f"{number / 1_000_000_000:.2f}B"
    if number >= 1_000_000:
        return sign + "$" + f"{number / 1_000_000:.1f}M"
    return sign + "$" + f"{number:,.0f}"


def pct(value):
    number = safe_float(value)
    return (
        f"{number:.1f}%"
        if number is not None
        else "N/A"
    )


def format_multiple(value):
    number = safe_float(value)
    return (
        f"{number:.2f}x"
        if number is not None
        else "N/A"
    )


def format_utc_timestamp(
    value,
    fallback="Unavailable",
):
    if not value:
        return fallback
    parsed = pd.to_datetime(
        value,
        errors="coerce",
        utc=True,
    )
    if pd.isna(parsed):
        return str(value)
    return parsed.strftime(
        "%Y-%m-%d %H:%M UTC"
    )
