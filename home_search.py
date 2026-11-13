from __future__ import annotations

import re
from difflib import SequenceMatcher


COMMON_ALIASES = {
    "GOOG": ("google",),
    "GOOGL": ("google",),
    "META": ("facebook", "instagram", "whatsapp"),
    "AMZN": ("amazon", "aws"),
    "MSFT": ("microsoft",),
    "AAPL": ("apple",),
    "NVDA": ("nvidia",),
    "JPM": ("jp morgan", "jpmorgan", "chase"),
    "BRK-B": ("berkshire hathaway", "berkshire"),
    "BRK.A": ("berkshire hathaway", "berkshire"),
    "BRK.B": ("berkshire hathaway", "berkshire"),
}


CORPORATE_SUFFIXES = {
    "inc",
    "incorporated",
    "corp",
    "corporation",
    "company",
    "co",
    "plc",
    "ltd",
    "limited",
    "holdings",
    "holding",
    "group",
    "class",
    "adr",
}


def normalize_search_text(value):
    text = re.sub(
        r"[^a-z0-9]+",
        " ",
        str(value or "").lower(),
    )
    tokens = [
        token
        for token in text.split()
        if token not in CORPORATE_SUFFIXES
    ]
    return " ".join(tokens).strip()


def company_aliases(ticker, company):
    aliases = {
        normalize_search_text(company),
        normalize_search_text(ticker),
    }
    aliases.update(
        normalize_search_text(alias)
        for alias in COMMON_ALIASES.get(
            str(ticker or "").upper(),
            (),
        )
    )
    return {
        alias
        for alias in aliases
        if alias
    }


def _match_score(query, ticker, company):
    normalized_query = normalize_search_text(
        query
    )
    if not normalized_query:
        return 0

    ticker_text = normalize_search_text(
        ticker
    )
    aliases = company_aliases(
        ticker,
        company,
    )

    if normalized_query == ticker_text:
        return 1000

    best = 0
    for candidate in aliases:
        if normalized_query == candidate:
            best = max(best, 950)
        elif candidate.startswith(
            normalized_query
        ):
            best = max(best, 850)
        elif normalized_query in candidate:
            best = max(best, 700)
        else:
            ratio = SequenceMatcher(
                None,
                normalized_query,
                candidate,
            ).ratio()
            if ratio >= 0.72:
                best = max(
                    best,
                    int(500 * ratio),
                )
    return best


def rank_company_matches(
    universe,
    query,
    research_coverage=None,
    limit=8,
):
    coverage_by_ticker = (
        (research_coverage or {}).get(
            "companies",
            {},
        )
        or {}
    )

    matches = []
    for _, row in universe.iterrows():
        ticker = str(
            row.get("Ticker", "")
        ).upper().strip()
        company = str(
            row.get("Company", "")
        ).strip()
        if not ticker:
            continue

        score = _match_score(
            query,
            ticker,
            company,
        )
        if score <= 0:
            continue

        coverage = (
            coverage_by_ticker.get(
                ticker,
                {},
            )
            or {}
        )
        matches.append({
            "ticker": ticker,
            "company": company or ticker,
            "industry": str(
                row.get(
                    "Industry",
                    "Industry unavailable",
                )
            ).strip()
            or "Industry unavailable",
            "status": str(
                coverage.get(
                    "completion_status",
                    "SEC filings available",
                )
            ),
            "completeness": int(
                coverage.get(
                    "completeness_percent",
                    0,
                )
                or 0
            ),
            "score": score,
        })

    matches.sort(
        key=lambda item: (
            -item["score"],
            -item["completeness"],
            item["company"].lower(),
            item["ticker"],
        )
    )
    return matches[:limit]
