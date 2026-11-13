"""Unit normalization helpers for market-data fields."""

from __future__ import annotations

import math


_SUFFIX_MULTIPLIERS = {
    "K": 1_000.0,
    "M": 1_000_000.0,
    "B": 1_000_000_000.0,
    "T": 1_000_000_000_000.0,
}


def market_cap_dollars(
    value,
    *,
    plain_numbers_are_millions=True,
):
    """Normalize market-cap text to dollars.

    Finviz-style plain numeric market-cap fields are expressed in millions.
    Suffixed values (K/M/B/T) are interpreted literally.
    """
    if value is None:
        return None

    if isinstance(
        value,
        float,
    ) and math.isnan(value):
        return None

    text = (
        str(value)
        .strip()
        .replace(",", "")
        .replace("%", "")
    )
    if (
        not text
        or text.lower()
        in {
            "-",
            "n/a",
            "nan",
            "none",
        }
    ):
        return None

    suffix = text[-1:].upper()
    multiplier = (
        _SUFFIX_MULTIPLIERS.get(
            suffix,
            1.0,
        )
    )
    if suffix in _SUFFIX_MULTIPLIERS:
        text = text[:-1]

    try:
        parsed = (
            float(text)
            * multiplier
        )
    except ValueError:
        return None

    if (
        suffix
        not in _SUFFIX_MULTIPLIERS
        and plain_numbers_are_millions
    ):
        return parsed * 1_000_000

    return parsed
