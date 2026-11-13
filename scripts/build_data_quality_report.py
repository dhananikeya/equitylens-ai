"""Build a transparent data-quality report for EquityLens research datasets.

The report separates correctness errors from expected coverage gaps. It never
fills missing values or invents metadata; it only describes what is present.
"""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

OUTPUT_PATH = DATA / "data_quality_report.json"

ANNUAL_PATHS = [
    DATA / "generated_company_metrics.json",
    DATA / "company_metrics.json",
]
QUARTERLY_PATHS = [
    DATA / "generated_company_quarterly.json",
    DATA / "company_quarterly.json",
]
ANALYSIS_PATHS = [
    DATA / "generated_company_analysis.json",
    DATA / "company_analysis.json",
]
REGISTRATION_PATHS = [
    DATA / "generated_company_s1.json",
    DATA / "company_s1.json",
]


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    text = path.read_text(
        encoding="utf-8"
    ).strip()
    if not text:
        return {}
    payload = json.loads(text)
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


def merge_index(
    paths: list[Path],
) -> dict[str, dict]:
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
            if not ticker:
                continue
            indexed[ticker] = {
                **indexed.get(
                    ticker,
                    {},
                ),
                **record,
            }
    return indexed


def quarter_ordinal(frame) -> int | None:
    match = re.match(
        r"CY(\d{4})Q([1-4])$",
        str(frame or ""),
    )
    if not match:
        return None
    return (
        int(match.group(1)) * 4
        + int(match.group(2))
    )


def official_sec_url(value) -> bool:
    text = str(value or "").strip()
    return (
        not text
        or text.startswith(
            "https://www.sec.gov/"
        )
        or text.startswith(
            "https://sec.gov/"
        )
    )


def add_issue(
    issues: list[dict],
    *,
    code: str,
    severity: str,
    message: str,
) -> None:
    issues.append({
        "code": code,
        "severity": severity,
        "message": message,
    })


def main() -> None:
    annual = merge_index(
        ANNUAL_PATHS
    )
    quarterly = merge_index(
        QUARTERLY_PATHS
    )
    analysis = merge_index(
        ANALYSIS_PATHS
    )
    registration = merge_index(
        REGISTRATION_PATHS
    )
    sec_summary = read_json(
        DATA / "sec_summary.json"
    )
    coverage = read_json(
        DATA / "research_coverage.json"
    )

    with (
        DATA / "finviz_universe.csv"
    ).open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as handle:
        universe = list(
            csv.DictReader(handle)
        )

    companies = {}
    severity_counts = Counter()
    issue_counts = Counter()

    for row in universe:
        ticker = str(
            row.get(
                "Ticker",
                "",
            )
        ).upper().strip()
        if not ticker:
            continue

        issues: list[dict] = []
        annual_record = (
            annual.get(ticker, {})
            or {}
        )
        quarter_record = (
            quarterly.get(ticker, {})
            or {}
        )
        analysis_record = (
            analysis.get(ticker, {})
            or {}
        )
        registration_record = (
            registration.get(
                ticker,
                {},
            )
            or {}
        )
        sec_record = (
            sec_summary.get(
                "companies",
                {},
            ).get(
                ticker,
                {},
            )
            or {}
        )
        coverage_record = (
            coverage.get(
                "companies",
                {},
            ).get(
                ticker,
                {},
            )
            or {}
        )

        if not annual_record:
            add_issue(
                issues,
                code="annual_missing",
                severity="coverage_gap",
                message=(
                    "No structured annual financial record is available."
                ),
            )
        else:
            fiscal_year_end = str(
                annual_record.get(
                    "fiscal_year_end",
                    "",
                )
                or ""
            )
            fiscal_year = (
                annual_record.get(
                    "fiscal_year"
                )
            )
            if (
                fiscal_year_end[:4].isdigit()
                and fiscal_year
                is not None
                and int(
                    fiscal_year_end[:4]
                )
                != int(
                    fiscal_year
                )
            ):
                add_issue(
                    issues,
                    code=(
                        "annual_year_end_mismatch"
                    ),
                    severity="error",
                    message=(
                        "Fiscal-year label does not match the annual period-end year."
                    ),
                )

            currency = str(
                annual_record.get(
                    "currency",
                    "",
                )
                or ""
            ).upper().strip()
            if not currency:
                add_issue(
                    issues,
                    code=(
                        "annual_currency_missing"
                    ),
                    severity="warning",
                    message=(
                        "Annual reporting currency is not recorded."
                    ),
                )

            history = (
                annual_record.get(
                    "history",
                    [],
                )
                or []
            )
            period_ends = [
                str(
                    item.get(
                        "period_end",
                        "",
                    )
                )
                for item in history
                if isinstance(
                    item,
                    dict,
                )
                and item.get(
                    "period_end"
                )
            ]
            if len(period_ends) != len(
                set(period_ends)
            ):
                add_issue(
                    issues,
                    code=(
                        "annual_duplicate_period"
                    ),
                    severity="error",
                    message=(
                        "Annual history contains a duplicate period end."
                    ),
                )

            if not official_sec_url(
                annual_record.get(
                    "filing_url"
                )
            ):
                add_issue(
                    issues,
                    code=(
                        "annual_source_not_sec"
                    ),
                    severity="error",
                    message=(
                        "Structured annual filing URL is not an official SEC URL."
                    ),
                )

        if not quarter_record:
            add_issue(
                issues,
                code="quarterly_missing",
                severity="coverage_gap",
                message=(
                    "No structured quarterly financial record is available."
                ),
            )
        else:
            latest = (
                quarter_record.get(
                    "latest_quarter",
                    {},
                )
                or {}
            )
            prior = (
                quarter_record.get(
                    "prior_quarter",
                    {},
                )
                or {}
            )
            latest_ordinal = (
                quarter_ordinal(
                    latest.get(
                        "frame"
                    )
                )
            )
            prior_ordinal = (
                quarter_ordinal(
                    prior.get(
                        "frame"
                    )
                )
            )
            if (
                latest.get(
                    "revenue"
                )
                is not None
                and prior.get(
                    "revenue"
                )
                is not None
                and latest_ordinal
                is not None
                and prior_ordinal
                is not None
                and latest_ordinal
                - prior_ordinal
                != 1
            ):
                add_issue(
                    issues,
                    code=(
                        "quarter_nonconsecutive"
                    ),
                    severity="error",
                    message=(
                        "Latest and prior quarters are not consecutive."
                    ),
                )

            if not str(
                quarter_record.get(
                    "currency",
                    "",
                )
                or ""
            ).strip():
                add_issue(
                    issues,
                    code=(
                        "quarter_currency_missing"
                    ),
                    severity="warning",
                    message=(
                        "Quarterly reporting currency is not recorded."
                    ),
                )

            if not official_sec_url(
                quarter_record.get(
                    "source_filing"
                )
            ):
                add_issue(
                    issues,
                    code=(
                        "quarter_source_not_sec"
                    ),
                    severity="error",
                    message=(
                        "Structured quarterly filing URL is not an official SEC URL."
                    ),
                )

        if not analysis_record:
            add_issue(
                issues,
                code=(
                    "qualitative_missing"
                ),
                severity="coverage_gap",
                message=(
                    "No structured qualitative research record is available."
                ),
            )

        if not registration_record:
            add_issue(
                issues,
                code=(
                    "registration_research_missing"
                ),
                severity="coverage_gap",
                message=(
                    "No structured registration-era research is available."
                ),
            )

        if not sec_record.get(
            "has_filings"
        ):
            add_issue(
                issues,
                code="sec_filings_missing",
                severity="warning",
                message=(
                    "SEC filing index does not report filings for this ticker."
                ),
            )

        for issue in issues:
            severity_counts[
                issue["severity"]
            ] += 1
            issue_counts[
                issue["code"]
            ] += 1

        companies[ticker] = {
            "ticker": ticker,
            "company": str(
                row.get(
                    "Company",
                    "",
                )
            ).strip(),
            "issue_count": len(
                issues
            ),
            "errors": sum(
                1
                for issue in issues
                if issue[
                    "severity"
                ]
                == "error"
            ),
            "warnings": sum(
                1
                for issue in issues
                if issue[
                    "severity"
                ]
                == "warning"
            ),
            "coverage_gaps": sum(
                1
                for issue in issues
                if issue[
                    "severity"
                ]
                == "coverage_gap"
            ),
            "research_completeness_percent": int(
                coverage_record.get(
                    "completeness_percent",
                    0,
                )
                or 0
            ),
            "issues": issues,
        }

    error_companies = [
        ticker
        for ticker, record
        in companies.items()
        if record["errors"] > 0
    ]
    warning_companies = [
        ticker
        for ticker, record
        in companies.items()
        if record["warnings"] > 0
    ]

    output = {
        "generated_at_utc": datetime.now(
            timezone.utc
        ).isoformat(
            timespec="seconds"
        ),
        "universe_count": len(
            companies
        ),
        "summary": {
            "companies_with_errors": len(
                error_companies
            ),
            "companies_with_warnings": len(
                warning_companies
            ),
            "issue_counts_by_severity": dict(
                severity_counts
            ),
            "issue_counts_by_code": dict(
                issue_counts
            ),
        },
        "definitions": {
            "error": (
                "A correctness or provenance problem that should be fixed before relying on the affected field."
            ),
            "warning": (
                "A metadata or source-quality limitation that should be visible to users."
            ),
            "coverage_gap": (
                "Research is not yet available; this is not treated as a correctness error."
            ),
        },
        "companies": companies,
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
        "Data quality: "
        f"{len(companies)} companies, "
        f"{len(error_companies)} with errors, "
        f"{len(warning_companies)} with warnings."
    )


if __name__ == "__main__":
    main()
