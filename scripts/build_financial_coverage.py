"""Incrementally build SEC XBRL financial coverage without any LLM.

This pipeline is intentionally separate from qualitative research. It reads the
existing SEC filing shards for filing metadata and calls SEC Company Facts for
reported financial values. Hand-curated records remain authoritative in the app.
"""

from __future__ import annotations

import csv
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from build_deep_research import (
    ANNUAL_FORMS,
    QUARTERLY_FORMS,
    build_financial_records,
    get_json,
    latest_filing,
    read_json,
    rows_from_submission_arrays,
    write_json,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

UNIVERSE_PATH = DATA / "finviz_universe.csv"
SEC_SUMMARY_PATH = DATA / "sec_summary.json"
METRICS_PATH = DATA / "generated_company_metrics.json"
QUARTERLY_PATH = DATA / "generated_company_quarterly.json"
HAND_METRICS_PATH = DATA / "company_metrics.json"
STATE_PATH = DATA / "financial_pipeline_state.json"

BATCH_SIZE = max(
    1,
    int(os.getenv("FINANCIAL_BATCH_SIZE", "50")),
)

FINANCIAL_PIPELINE_VERSION = (
    "sec-period-end-v2"
)


def load_universe() -> list[dict]:
    with UNIVERSE_PATH.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as handle:
        return list(csv.DictReader(handle))


def ticker_index(payload: dict) -> dict[str, str]:
    output = {}
    for key, record in payload.items():
        if not isinstance(record, dict):
            continue
        ticker = str(
            record.get("ticker", "")
        ).upper().strip()
        if ticker:
            output[ticker] = key
    return output


def canonical_key(
    company: dict,
    hand_key_by_ticker: dict[str, str],
) -> str:
    ticker = str(
        company.get("Ticker", "")
    ).upper().strip()
    return hand_key_by_ticker.get(
        ticker,
        (
            str(company.get("Company", "")).strip()
            + " ("
            + ticker
            + ")"
        ),
    )


def main() -> None:
    universe = load_universe()
    generated_metrics = read_json(
        METRICS_PATH,
        {},
    )
    generated_quarterly = read_json(
        QUARTERLY_PATH,
        {},
    )
    hand_metrics = read_json(
        HAND_METRICS_PATH,
        {},
    )
    state = read_json(STATE_PATH, {})
    sec_summary = read_json(
        SEC_SUMMARY_PATH,
        {},
    )
    sec_companies = (
        sec_summary.get("companies", {})
        or {}
    )

    hand_key_by_ticker = ticker_index(
        hand_metrics
    )
    generated_metric_tickers = set(
        ticker_index(generated_metrics)
    )
    generated_quarterly_tickers = set(
        ticker_index(generated_quarterly)
    )

    candidates = []
    for company in universe:
        ticker = str(
            company.get("Ticker", "")
        ).upper().strip()
        if not ticker:
            continue

        # Curated financial records already provide authoritative coverage.
        if ticker in hand_key_by_ticker:
            continue

        existing_state = (
            state.get(
                ticker,
                {},
            )
            or {}
        )
        if (
            ticker in generated_metric_tickers
            and ticker
            in generated_quarterly_tickers
            and existing_state.get(
                "pipeline_version"
            )
            == FINANCIAL_PIPELINE_VERSION
        ):
            continue

        sec_company = (
            sec_companies.get(ticker, {})
            or {}
        )
        if not sec_company.get("cik"):
            continue

        candidates.append(
            (company, sec_company)
        )
        if len(candidates) >= BATCH_SIZE:
            break

    if not candidates:
        print(
            "No missing deterministic financial coverage remains."
        )
        return

    print(
        f"Building deterministic financial coverage for "
        f"{len(candidates)} companies."
    )

    for index, (company, sec_company) in enumerate(
        candidates,
        start=1,
    ):
        ticker = str(
            company.get("Ticker", "")
        ).upper().strip()
        key = canonical_key(
            company,
            hand_key_by_ticker,
        )
        cik = str(
            sec_company.get("cik", "")
        ).zfill(10)

        print(
            f"[{index}/{len(candidates)}] "
            f"{ticker} · "
            f"{company.get('Company', '')}"
        )

        try:
            submissions = get_json(
                "https://data.sec.gov/submissions/"
                f"CIK{cik}.json"
            )
            filings = rows_from_submission_arrays(
                submissions,
                cik,
            )
            annual_filing = latest_filing(
                filings,
                ANNUAL_FORMS,
            )
            quarterly_filing = latest_filing(
                filings,
                QUARTERLY_FORMS,
            )

            if (
                not annual_filing
                and not quarterly_filing
            ):
                raise ValueError(
                    "No supported annual or quarterly filing in SEC shard."
                )

            companyfacts = get_json(
                "https://data.sec.gov/api/xbrl/"
                f"companyfacts/CIK{cik}.json"
            )

            (
                metrics_record,
                quarterly_record,
                _,
            ) = build_financial_records(
                key,
                company,
                companyfacts,
                annual_filing,
                quarterly_filing,
            )

            generated_metrics[key] = (
                metrics_record
            )
            generated_quarterly[key] = (
                quarterly_record
            )
            state[ticker] = {
                "status": "complete",
                "pipeline_version": (
                    FINANCIAL_PIPELINE_VERSION
                ),
                "cik": cik,
                "key": key,
                "annual_source": (
                    annual_filing.get(
                        "url",
                        "",
                    )
                ),
                "quarterly_source": (
                    quarterly_filing.get(
                        "url",
                        "",
                    )
                ),
                "completed_utc": (
                    datetime.now(
                        timezone.utc
                    ).isoformat(
                        timespec="seconds"
                    )
                ),
                "error": "",
            }
            print("  complete")
        except Exception as exc:
            state[ticker] = {
                "status": "error",
                "pipeline_version": (
                    FINANCIAL_PIPELINE_VERSION
                ),
                "cik": cik,
                "key": key,
                "last_attempt_utc": (
                    datetime.now(
                        timezone.utc
                    ).isoformat(
                        timespec="seconds"
                    )
                ),
                "error": str(exc)[:1000],
            }
            print(
                "  ERROR: "
                + str(exc)
            )

        write_json(
            METRICS_PATH,
            generated_metrics,
        )
        write_json(
            QUARTERLY_PATH,
            generated_quarterly,
        )
        write_json(
            STATE_PATH,
            state,
        )

    print(
        "Deterministic financial batch complete."
    )


if __name__ == "__main__":
    main()
