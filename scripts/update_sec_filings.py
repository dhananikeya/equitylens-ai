"""Refresh recent SEC filings for every company covered by EquityLens AI.

Uses the SEC's public submissions API. No API key is required.
The script derives each company's CIK from the existing SEC filing URL in
data/company_metrics.json, so adding a new covered company automatically adds it
to the filing monitor as long as its filing_url is an SEC EDGAR URL.
"""

from __future__ import annotations

import json
import re
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
METRICS_PATH = ROOT / "data" / "company_metrics.json"
OUTPUT_PATH = ROOT / "data" / "sec_filings.json"

USER_AGENT = "EquityLens AI research app dhananikeya@gmail.com"
MAX_FILINGS_PER_COMPANY = 25


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


def cik_from_filing_url(url: str) -> str:
    match = re.search(r"/Archives/edgar/data/(\d+)/", url or "")
    if not match:
        raise ValueError(f"Could not derive CIK from SEC filing URL: {url}")
    return match.group(1).zfill(10)


def filing_url(cik: str, accession: str, primary_document: str) -> str:
    accession_compact = accession.replace("-", "")
    return (
        "https://www.sec.gov/Archives/edgar/data/"
        f"{int(cik)}/{accession_compact}/{primary_document}"
    )


def recent_filings(
    submissions: dict,
    cik: str,
    previous_first_seen: dict[str, str],
    observed_at_utc: str,
) -> list[dict]:
    recent = submissions.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    count = min(len(forms), MAX_FILINGS_PER_COMPANY)
    rows = []

    def value(field: str, index: int, default=""):
        values = recent.get(field, [])
        return values[index] if index < len(values) else default

    for i in range(count):
        accession = value("accessionNumber", i)
        primary_document = value("primaryDocument", i)
        rows.append(
            {
                "form": forms[i],
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


def main() -> None:
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    previous_output = (
        json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
        if OUTPUT_PATH.exists()
        else {}
    )
    observed_at_utc = datetime.now(timezone.utc).isoformat(timespec="seconds")
    output = {}

    for company_name, company in metrics.items():
        cik = cik_from_filing_url(company.get("filing_url", ""))
        submissions = get_json(
            f"https://data.sec.gov/submissions/CIK{cik}.json"
        )

        previous_first_seen = {
            filing.get("accession_number", ""): filing.get("first_seen_utc", "")
            for filing in previous_output.get(company_name, {}).get("filings", [])
            if filing.get("accession_number")
        }

        output[company_name] = {
            "ticker": company.get("ticker", ""),
            "cik": cik,
            "entity_name": submissions.get("name", company_name),
            "last_checked_utc": observed_at_utc,
            "filings": recent_filings(
                submissions,
                cik,
                previous_first_seen,
                observed_at_utc,
            ),
        }

        # Stay comfortably below the SEC's published fair-access ceiling.
        time.sleep(0.2)

    new_text = json.dumps(output, indent=2, sort_keys=False) + "\n"
    old_text = OUTPUT_PATH.read_text(encoding="utf-8") if OUTPUT_PATH.exists() else ""

    if new_text != old_text:
        OUTPUT_PATH.write_text(new_text, encoding="utf-8")
        print("SEC filing feed updated.")
    else:
        print("No SEC filing changes detected.")


if __name__ == "__main__":
    main()
