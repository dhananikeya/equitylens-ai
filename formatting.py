from datetime import datetime, timezone


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


CURRENCY_PREFIXES = {
    "USD": "$",
    "EUR": "€",
    "GBP": "£",
    "JPY": "¥",
    "CAD": "C$",
    "AUD": "A$",
    "CHF": "CHF ",
    "CNY": "CN¥",
    "HKD": "HK$",
    "INR": "₹",
    "KRW": "₩",
}


def format_money(
    value,
    currency="USD",
):
    number = safe_float(value)
    if number is None:
        return "N/A"

    currency_code = str(
        currency or "USD"
    ).upper().strip()
    prefix = CURRENCY_PREFIXES.get(
        currency_code,
        currency_code + " ",
    )

    sign = "-" if number < 0 else ""
    number = abs(number)
    if number >= 1_000_000_000:
        return (
            sign
            + prefix
            + f"{number / 1_000_000_000:.2f}B"
        )
    if number >= 1_000_000:
        return (
            sign
            + prefix
            + f"{number / 1_000_000:.1f}M"
        )
    return (
        sign
        + prefix
        + f"{number:,.0f}"
    )


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

    try:
        if isinstance(
            value,
            datetime,
        ):
            parsed = value
        else:
            text = str(
                value
            ).strip()
            if text.endswith("Z"):
                text = (
                    text[:-1]
                    + "+00:00"
                )
            parsed = datetime.fromisoformat(
                text
            )

        if parsed.tzinfo is None:
            parsed = parsed.replace(
                tzinfo=timezone.utc
            )
        else:
            parsed = parsed.astimezone(
                timezone.utc
            )

        return parsed.strftime(
            "%Y-%m-%d %H:%M UTC"
        )
    except (
        TypeError,
        ValueError,
        OverflowError,
    ):
        return str(value)
