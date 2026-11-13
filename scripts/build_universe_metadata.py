"""Build source-conscious metadata for the EquityLens company universe.

The universe CSV remains the market/screener source of truth. This companion
file adds metadata that can be derived safely from existing EquityLens/SEC data
without pretending unknown exchange, index-membership, or IPO facts are known.
"""

from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

UNIVERSE_PATH = DATA / "finviz_universe.csv"
METRICS_PATHS = [
    DATA / "generated_company_metrics.json",
    DATA / "company_metrics.json",
]
S1_PATHS = [
    DATA / "generated_company_s1.json",
    DATA / "company_s1.json",
]
OUTPUT_PATH = DATA / "company_universe_metadata.json"

# Historical or alternate symbols that materially improve discovery.
# This is deliberately small and curated rather than an unsourced ticker-history feed.
LEGACY_TICKER_ALIASES = {
    "META": ["FB"],
    "XYZ": ["SQ"],
    "GOOGL": ["GOOG"],
    "GOOG": ["GOOGL"],
    "BRK-B": ["BRK.B", "BRKB"],
}

SHARE_CLASS_PATTERN = re.compile(
    r"\bclass\s+([abc])\b",
    re.IGNORECASE,
)


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    payload = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )
    return payload if isinstance(
        payload,
        dict,
    ) else {}


def ticker_from_record(
    key: str,
    record: dict,
) -> str:
    ticker = str(
        (record or {}).get(
            "ticker",
            "",
        )
    ).upper().strip()
    if ticker:
        return ticker

    match = re.search(
        r"\(([^()]+)\)\s*$",
        str(key),
    )
    return (
        match.group(1).upper().strip()
        if match
        else ""
    )


def index_by_ticker(paths: list[Path]) -> dict[str, dict]:
    indexed: dict[str, dict] = {}
    for path in paths:
        for key, record in read_json(
            path
        ).items():
            if not isinstance(
                record,
                dict,
            ):
                continue
            ticker = ticker_from_record(
                key,
                record,
            )
            if ticker:
                indexed[ticker] = {
                    **indexed.get(
                        ticker,
                        {},
                    ),
                    **record,
                }
    return indexed


def market_cap_band(value) -> str:
    try:
        market_cap_millions = float(
            value
        )
    except (
        TypeError,
        ValueError,
    ):
        return "Unknown"

    if market_cap_millions >= 200_000:
        return "Mega cap"
    if market_cap_millions >= 10_000:
        return "Large cap"
    if market_cap_millions >= 2_000:
        return "Mid cap"
    if market_cap_millions >= 300:
        return "Small cap"
    return "Micro cap"


def share_class(
    ticker: str,
    company: str,
) -> str:
    match = SHARE_CLASS_PATTERN.search(
        company
    )
    if match:
        return (
            "Class "
            + match.group(1).upper()
        )

    normalized = ticker.upper()
    if normalized.endswith(
        (".A", "-A")
    ):
        return "Class A"
    if normalized.endswith(
        (".B", "-B")
    ):
        return "Class B"
    if normalized.endswith(
        (".C", "-C")
    ):
        return "Class C"
    return ""


def issuer_type(
    country: str,
    company: str,
) -> str:
    company_lower = company.lower()
    if (
        " adr" in company_lower
        or company_lower.endswith("adr")
        or "depositary receipt"
        in company_lower
    ):
        return "ADR"

    if (
        str(country).strip().upper()
        not in {
            "USA",
            "UNITED STATES",
            "UNITED STATES OF AMERICA",
        }
    ):
        return "Foreign issuer"

    return "U.S. issuer"


def reporting_regime(
    metrics_record: dict,
) -> str:
    source = str(
        metrics_record.get(
            "source",
            "",
        )
    ).upper().strip()

    if source.startswith("20-F"):
        return "20-F foreign private issuer"
    if source.startswith("40-F"):
        return "40-F Canadian issuer"
    if source.startswith("10-K"):
        return "10-K domestic reporting"
    return "Periodic form not classified"


def registration_year(
    registration_record: dict,
):
    filed = str(
        registration_record.get(
            "filed_date",
            "",
        )
    ).strip()
    if (
        len(filed) >= 4
        and filed[:4].isdigit()
    ):
        return int(filed[:4])
    return None


def main() -> None:
    metrics = index_by_ticker(
        METRICS_PATHS
    )
    registrations = index_by_ticker(
        S1_PATHS
    )

    with UNIVERSE_PATH.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as handle:
        rows = list(
            csv.DictReader(handle)
        )

    companies = {}
    for row in rows:
        ticker = str(
            row.get(
                "Ticker",
                "",
            )
        ).upper().strip()
        if not ticker:
            continue

        company = str(
            row.get(
                "Company",
                "",
            )
        ).strip()
        country = str(
            row.get(
                "Country",
                "",
            )
        ).strip()
        metrics_record = (
            metrics.get(
                ticker,
                {},
            )
            or {}
        )
        registration_record = (
            registrations.get(
                ticker,
                {},
            )
            or {}
        )

        companies[ticker] = {
            "ticker": ticker,
            "company": company,
            "listing_status": "Active universe",
            "aliases": sorted(
                set(
                    LEGACY_TICKER_ALIASES.get(
                        ticker,
                        [],
                    )
                )
            ),
            "share_class": share_class(
                ticker,
                company,
            ),
            "country": country,
            "issuer_type": issuer_type(
                country,
                company,
            ),
            "reporting_regime": (
                reporting_regime(
                    metrics_record
                )
            ),
            "market_cap_band": (
                market_cap_band(
                    row.get(
                        "Market Cap"
                    )
                )
            ),
            "registration_year": (
                registration_year(
                    registration_record
                )
            ),
            "ipo_year": None,
            "exchange": None,
            "index_memberships": [],
            "metadata_notes": [
                (
                    "Registration year is shown separately from IPO year; "
                    "a registration filing does not prove the offering completed that year."
                )
            ],
        }

    output = {
        "generated_at_utc": datetime.now(
            timezone.utc
        ).isoformat(
            timespec="seconds"
        ),
        "companies": companies,
        "field_policy": {
            "exchange": (
                "Unknown until a reliable listing source is connected."
            ),
            "index_memberships": (
                "Unknown until a reliable index-membership source is connected."
            ),
            "ipo_year": (
                "Unknown unless a completed IPO/listing year is explicitly sourced."
            ),
            "registration_year": (
                "Derived only from structured S-1/F-1/S-11 research and is not treated as IPO year."
            ),
            "reporting_regime": (
                "Derived from the annual financial source form when available."
            ),
        },
    }

    OUTPUT_PATH.write_text(
        json.dumps(
            output,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    print(
        f"Wrote metadata for {len(companies)} companies."
    )


if __name__ == "__main__":
    main()
