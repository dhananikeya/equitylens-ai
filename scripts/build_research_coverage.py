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


def has_analysis(record: dict) -> bool:
    return bool(
        record
        and (
            record.get("business_model")
            or record.get("primary_revenue_source")
            or record.get("key_risk_themes")
        )
    )


def has_registration(record: dict) -> bool:
    return bool(
        record
        and (
            record.get("source_url")
            or record.get("filing_details")
            or record.get("historical_context")
        )
    )


def completeness_score(flags: dict[str, bool]) -> int:
    weighted = {
        "sec_filings": 20,
        "annual_financials": 25,
        "quarterly_financials": 20,
        "qualitative_analysis": 25,
        "registration_research": 10,
    }
    return sum(
        weight
        for key, weight in weighted.items()
        if flags.get(key)
    )


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
            "qualitative_analysis": has_analysis(
                datasets["analysis"].get(ticker, {})
            ),
            "registration_research": has_registration(
                datasets["registration"].get(ticker, {})
            ),
        }

        score = completeness_score(flags)
        label = completion_label(score, flags)

        for key, present in flags.items():
            if present:
                totals[key] += 1

        if score >= 90:
            totals["deep_research"] += 1
            deep_tickers.append(ticker)

        analysis_record = datasets["analysis"].get(ticker, {})
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
                "Ticker has SEC filings, annual and quarterly financial coverage, "
                "qualitative analysis, and registration research where represented "
                "by the weighted completeness model."
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
