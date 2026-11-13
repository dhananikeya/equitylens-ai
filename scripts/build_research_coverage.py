"""Build an honest research-coverage index for the full EquityLens universe.

This script does not generate narrative research. It measures which structured
datasets and SEC sources are actually available for each ticker so the UI can
separate universe coverage from deep-research coverage.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

UNIVERSE_PATH = DATA / "finviz_universe.csv"
OUTPUT_PATH = DATA / "research_coverage.json"
INDEX_PATH = DATA / "research_index.json"

DATASETS = {
    "metrics": (
        DATA / "generated_company_metrics.json",
        DATA / "company_metrics.json",
    ),
    "quarterly": (
        DATA / "generated_company_quarterly.json",
        DATA / "company_quarterly.json",
    ),
    "analysis": (
        DATA / "generated_company_analysis.json",
        DATA / "company_analysis.json",
    ),
    "registration": (
        DATA / "generated_company_s1.json",
        DATA / "company_s1.json",
    ),
}

QUALITATIVE_FIELDS = [
    "business_model",
    "primary_revenue_source",
    "customer_type",
    "platform_dependency",
    "competitive_risk",
    "operational_risk",
    "profitability_history",
    "customer_concentration",
    "international_exposure",
    "business_segments",
    "geographic_exposure",
    "competitive_positioning",
    "capital_allocation",
    "dilution_stock_comp",
    "debt_liquidity",
    "profitability_cash_flow",
    "key_risk_themes",
]


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return {}
    payload = json.loads(text)
    return payload if isinstance(payload, dict) else {}


def ticker_from_entry(key: str, value: dict) -> str:
    ticker = str((value or {}).get("ticker", "")).upper().strip()
    if ticker:
        return ticker

    key = str(key)
    if "(" in key and key.endswith(")"):
        return key.rsplit("(", 1)[1][:-1].upper().strip()
    return ""


def index_dataset(payload: dict) -> dict[str, dict]:
    indexed = {}
    for key, value in payload.items():
        if not isinstance(value, dict):
            continue
        ticker = ticker_from_entry(key, value)
        if ticker:
            indexed[ticker] = value
    return indexed


def merge_generated_and_curated(
    generated_path: Path,
    curated_path: Path,
) -> dict[str, dict]:
    generated = index_dataset(read_json(generated_path))
    curated = index_dataset(read_json(curated_path))
    return {**generated, **curated}


def has_annual(record: dict) -> bool:
    return bool(
        record
        and (
            record.get("revenue") is not None
            or record.get("history")
        )
    )


def has_quarterly(record: dict) -> bool:
    return bool(
        record
        and (
            record.get("latest_quarter")
            or record.get("quarterly_history")
        )
    )


def qualitative_depth(record: dict) -> float:
    if not record:
        return 0.0

    populated = 0
    for field in QUALITATIVE_FIELDS:
        value = record.get(field)
        if isinstance(value, list):
            present = any(
                str(item).strip()
                for item in value
            )
        else:
            present = bool(
                str(value or "").strip()
            )
        if present:
            populated += 1

    return round(
        (populated / len(QUALITATIVE_FIELDS)) * 100,
        1,
    )


def has_analysis(record: dict) -> bool:
    return qualitative_depth(record) > 0


def has_registration(record: dict) -> bool:
    return bool(
        record
        and (
            record.get("source_url")
            or record.get("filing_details")
            or record.get("historical_context")
        )
    )


def completeness_score(
    flags: dict[str, bool],
    qualitative_depth_percent: float,
) -> int:
    score = 0
    if flags.get("sec_filings"):
        score += 20
    if flags.get("annual_financials"):
        score += 25
    if flags.get("quarterly_financials"):
        score += 20
    if flags.get("registration_research"):
        score += 10

    score += round(
        25
        * max(
            0.0,
            min(
                100.0,
                qualitative_depth_percent,
            ),
        )
        / 100
    )
    return int(score)


def completion_label(score: int, flags: dict[str, bool]) -> str:
    if score >= 90:
        return "Deep research available"
    if flags.get("qualitative_analysis") and flags.get("annual_financials"):
        return "Structured research available"
    if flags.get("annual_financials") or flags.get("quarterly_financials"):
        return "Financial research available"
    if flags.get("sec_filings"):
        return "SEC filings available"
    return "Universe listing only"


def main() -> None:
    datasets = {
        name: merge_generated_and_curated(*paths)
        for name, paths in DATASETS.items()
    }

    sec_summary = read_json(DATA / "sec_summary.json")
    sec_companies = sec_summary.get("companies", {}) or {}

    with UNIVERSE_PATH.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as handle:
        universe = list(csv.DictReader(handle))

    companies = {}
    totals = {
        "universe": len(universe),
        "sec_filings": 0,
        "annual_financials": 0,
        "quarterly_financials": 0,
        "qualitative_analysis": 0,
        "registration_research": 0,
        "deep_research": 0,
    }
    deep_tickers = []

    for row in universe:
        ticker = str(row.get("Ticker", "")).upper().strip()
        if not ticker:
            continue

        sec = sec_companies.get(ticker, {}) or {}
        analysis_record = datasets[
            "analysis"
        ].get(ticker, {})
        qualitative_depth_percent = (
            qualitative_depth(
                analysis_record
            )
        )

        flags = {
            "sec_filings": bool(
                sec.get("has_filings")
                or sec.get("has_material_filings")
            ),
            "annual_financials": has_annual(
                datasets["metrics"].get(ticker, {})
            ),
            "quarterly_financials": has_quarterly(
                datasets["quarterly"].get(ticker, {})
            ),
            "qualitative_analysis": (
                qualitative_depth_percent > 0
            ),
            "registration_research": has_registration(
                datasets["registration"].get(ticker, {})
            ),
        }

        score = completeness_score(
            flags,
            qualitative_depth_percent,
        )
        label = completion_label(score, flags)

        for key, present in flags.items():
            if present:
                totals[key] += 1

        if score >= 90:
            totals["deep_research"] += 1
            deep_tickers.append(ticker)

        metrics_record = datasets["metrics"].get(ticker, {})
        quarterly_record = datasets["quarterly"].get(ticker, {})
        registration_record = datasets["registration"].get(ticker, {})

        source_urls = sorted({
            str(url).strip()
            for url in [
                analysis_record.get("source_filing"),
                metrics_record.get("filing_url"),
                quarterly_record.get("source_filing"),
                registration_record.get("source_url"),
                (
                    sec.get("latest_material_filing", {})
                    or {}
                ).get("url"),
            ]
            if str(url or "").strip()
        })

        companies[ticker] = {
            "ticker": ticker,
            "company": str(row.get("Company", "")).strip(),
            "sector": str(row.get("Sector", "")).strip(),
            "industry": str(row.get("Industry", "")).strip(),
            "country": str(row.get("Country", "")).strip(),
            **flags,
            "qualitative_depth_percent": (
                qualitative_depth_percent
            ),
            "completeness_percent": score,
            "completion_status": label,
            "source_urls": source_urls,
        }

    percentages = {
        key: round(
            (value / totals["universe"]) * 100,
            1,
        )
        for key, value in totals.items()
        if key != "universe"
    }

    generated_at = datetime.now(
        timezone.utc
    ).isoformat(timespec="seconds")

    output = {
        "generated_at_utc": generated_at,
        "totals": totals,
        "percentages": percentages,
        "companies": companies,
        "definition": {
            "universe": (
                "Company appears in the 517-company EquityLens universe."
            ),
            "deep_research": (
                "Ticker reaches at least 90% weighted completeness across SEC filing coverage, "
                "annual and quarterly financials, qualitative research depth, and registration research."
            ),
            "qualitative_depth": (
                "Percentage of the required structured qualitative fields that are populated."
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

    INDEX_PATH.write_text(
        json.dumps(
            {
                "generated_at_utc": generated_at,
                "deep_research_tickers": sorted(
                    deep_tickers
                ),
                "structured_research_tickers": sorted(
                    ticker
                    for ticker, record in companies.items()
                    if (
                        record["qualitative_analysis"]
                        and record["annual_financials"]
                    )
                ),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    print(
        "Research coverage: "
        + ", ".join(
            f"{key}={value}"
            for key, value in totals.items()
        )
    )


if __name__ == "__main__":
    main()
