"""Refresh SEC filing coverage for the EquityLens company universe.

The coverage universe comes from data/finviz_universe.csv. Tickers are resolved
to SEC CIKs using the SEC company_tickers.json reference file, then the public
submissions API is used to collect recent filings and registration filings.

No SEC API key is required.
"""

from __future__ import annotations

import csv
import json
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UNIVERSE_PATH = ROOT / "data" / "finviz_universe.csv"
OUTPUT_PATH = ROOT / "data" / "sec_filings.json"

USER_AGENT = "EquityLens AI research app dhananikeya@gmail.com"
MAX_FILINGS_PER_COMPANY = 25
MAX_HISTORY_FILES_FOR_REGISTRATION = 2
REGISTRATION_FORMS = {
    "S-1", "S-1/A",
    "F-1", "F-1/A",
    "S-11", "S-11/A",
}


def get_json(url: str) -> dict:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "From": "dhananikeya@gmail.com",
            "Accept": "application/json",
        },
    )
    last_error = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            last_error = exc
            if attempt < 2:
                time.sleep(2 ** attempt)
    raise last_error


def load_universe() -> list[dict]:
    with UNIVERSE_PATH.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def load_ticker_map() -> dict[str, dict]:
    payload = get_json("https://www.sec.gov/files/company_tickers.json")
    ticker_map = {}

    for row in payload.values():
        ticker = str(row.get("ticker", "")).upper().strip()
        if not ticker:
            continue
        ticker_map[ticker] = {
            "cik": str(row.get("cik_str", "")).zfill(10),
            "title": row.get("title", ""),
        }

    return ticker_map


def filing_url(cik: str, accession: str, primary_document: str) -> str:
    accession_compact = accession.replace("-", "")
    return (
        "https://www.sec.gov/Archives/edgar/data/"
        f"{int(cik)}/{accession_compact}/{primary_document}"
    )


def filing_rows_from_recent(
    recent: dict,
    cik: str,
    previous_first_seen: dict[str, str],
    observed_at_utc: str,
    limit: int | None = None,
) -> list[dict]:
    forms = recent.get("form", [])
    count = len(forms) if limit is None else min(len(forms), limit)
    rows = []

    def value(field: str, index: int, default=""):
        values = recent.get(field, [])
        return values[index] if index < len(values) else default

    for i in range(count):
        accession = value("accessionNumber", i)
        primary_document = value("primaryDocument", i)
        form = value("form", i)

        rows.append(
            {
                "form": form,
                "filing_date": value("filingDate", i),
                "acceptance_datetime": value("acceptanceDateTime", i),
                "report_date": value("reportDate", i),
                "accession_number": accession,
                "primary_document": primary_document,
                "description": value("primaryDocDescription", i),
                "items": value("items", i),
                "is_xbrl": value("isXBRL", i, 0),
                "is_inline_xbrl": value("isInlineXBRL", i, 0),
                "first_seen_utc": previous_first_seen.get(
                    accession, observed_at_utc
                ),
                "url": filing_url(cik, accession, primary_document)
                if accession and primary_document
                else "",
            }
        )

    return rows


def registration_rows(recent: dict, cik: str) -> list[dict]:
    rows = filing_rows_from_recent(
        recent,
        cik,
        previous_first_seen={},
        observed_at_utc="",
        limit=None,
    )
    return [
        row for row in rows
        if row.get("form") in REGISTRATION_FORMS
    ]


def scan_historical_registration_filings(
    submissions: dict,
    cik: str,
) -> tuple[list[dict], bool]:
    registration = []
    history_files = submissions.get("filings", {}).get("files", []) or []
    scanned = 0

    for history in history_files:
        if scanned >= MAX_HISTORY_FILES_FOR_REGISTRATION:
            break

        name = history.get("name")
        if not name:
            continue

        scanned += 1
        payload = get_json(
            "https://data.sec.gov/submissions/" + name
        )
        registration.extend(registration_rows(payload, cik))
        time.sleep(0.12)

        if registration:
            break

    return registration, scanned >= min(
        MAX_HISTORY_FILES_FOR_REGISTRATION,
        len(history_files),
    )


def dedupe_filings(rows: list[dict]) -> list[dict]:
    seen = set()
    output = []

    for row in rows:
        key = row.get("accession_number") or (
            row.get("form"),
            row.get("filing_date"),
            row.get("url"),
        )
        if key in seen:
            continue
        seen.add(key)
        output.append(row)

    return sorted(
        output,
        key=lambda row: row.get("filing_date", ""),
        reverse=True,
    )


def main() -> None:
    universe = load_universe()
    ticker_map = load_ticker_map()

    previous_output = (
        json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
        if OUTPUT_PATH.exists()
        else {}
    )

    observed_at_utc = datetime.now(timezone.utc).isoformat(timespec="seconds")
    output = {}

    for company in universe:
        ticker = str(company.get("Ticker", "")).upper().strip()
        company_name = str(company.get("Company", "")).strip()
        key = f"{company_name} ({ticker})"

        ticker_record = ticker_map.get(ticker)
        if not ticker_record:
            output[key] = {
                "ticker": ticker,
                "cik": "",
                "entity_name": company_name,
                "sector": company.get("Sector", ""),
                "industry": company.get("Industry", ""),
                "country": company.get("Country", ""),
                "last_checked_utc": observed_at_utc,
                "sec_status": "CIK not resolved from SEC ticker reference",
                "sec_company_url": "",
                "filings": [],
                "registration_filings": [],
                "registration_scan_complete": False,
            }
            continue

        cik = ticker_record["cik"]
        submissions = get_json(
            f"https://data.sec.gov/submissions/CIK{cik}.json"
        )

        previous_company = previous_output.get(key, {})
        previous_first_seen = {
            filing.get("accession_number", ""): filing.get("first_seen_utc")
            for filing in previous_company.get("filings", [])
            if filing.get("accession_number") and filing.get("first_seen_utc")
        }

        recent = submissions.get("filings", {}).get("recent", {})
        filings = filing_rows_from_recent(
            recent,
            cik,
            previous_first_seen,
            observed_at_utc,
            limit=MAX_FILINGS_PER_COMPANY,
        )

        registration = registration_rows(recent, cik)
        registration_scan_complete = bool(
            previous_company.get("registration_scan_complete", False)
        )

        if not registration:
            previous_registration = previous_company.get(
                "registration_filings", []
            )
            if previous_registration:
                registration = previous_registration

        if not registration and not registration_scan_complete:
            historical_registration, registration_scan_complete = (
                scan_historical_registration_filings(
                    submissions,
                    cik,
                )
            )
            registration.extend(historical_registration)

        registration = dedupe_filings(registration)

        output[key] = {
            "ticker": ticker,
            "cik": cik,
            "entity_name": submissions.get(
                "name",
                ticker_record.get("title") or company_name,
            ),
            "sector": company.get("Sector", ""),
            "industry": company.get("Industry", ""),
            "country": company.get("Country", ""),
            "last_checked_utc": observed_at_utc,
            "sec_status": "available",
            "sec_company_url": (
                "https://www.sec.gov/edgar/browse/"
                f"?CIK={int(cik)}&owner=exclude&action=getcompany"
            ),
            "filings": filings,
            "registration_filings": registration,
            "registration_scan_complete": registration_scan_complete,
        }

        # Keep requests comfortably below the SEC fair-access ceiling.
        time.sleep(0.12)

    new_text = json.dumps(output, indent=2, sort_keys=False) + "\n"
    old_text = (
        OUTPUT_PATH.read_text(encoding="utf-8")
        if OUTPUT_PATH.exists()
        else ""
    )

    if new_text != old_text:
        OUTPUT_PATH.write_text(new_text, encoding="utf-8")
        print(
            f"SEC filing feed updated for {len(output)} covered companies."
        )
    else:
        print("No SEC filing changes detected.")


if __name__ == "__main__":
    main()
