"""Refresh SEC filing coverage for the EquityLens company universe.

The coverage universe comes from data/finviz_universe.csv. Tickers are resolved
to SEC CIKs using the SEC company_tickers.json reference file, then the public
submissions API is used to collect recent filings and registration filings.

No SEC API key is required.
"""

from __future__ import annotations

import csv
import gzip
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UNIVERSE_PATH = ROOT / "data" / "finviz_universe.csv"
LEGACY_OUTPUT_PATH = ROOT / "data" / "sec_filings.json"
ARCHIVE_PATH = ROOT / "data" / "sec_filings.json.gz"
SUMMARY_PATH = ROOT / "data" / "sec_summary.json"
SHARD_DIR = ROOT / "data" / "sec_companies"

USER_AGENT = "EquityLens AI research app dhananikeya@gmail.com"
MAX_FILINGS_PER_COMPANY = 25
# Stable SEC CIK fallback for recently renamed / delisted ticker symbols.
# PSKY: SEC EDGAR filer Paramount Skydance Corp, CIK 0002041610.
CIK_OVERRIDES = {"PSKY": {"cik": "0002041610", "title": "Paramount Skydance Corp"}}
MAX_HISTORY_FILES_FOR_REGISTRATION = 2
REGISTRATION_FORMS = {
    "S-1", "S-1/A",
    "F-1", "F-1/A",
    "S-11", "S-11/A",
}
MATERIAL_HOME_FORMS = {
    "10-K", "10-K/A",
    "10-Q", "10-Q/A",
    "8-K", "8-K/A",
    "20-F", "20-F/A",
    "40-F", "40-F/A",
    "6-K", "6-K/A",
    *REGISTRATION_FORMS,
}


def get_json(url: str) -> dict:
    """Fetch SEC JSON, retrying temporary outages and rate limits."""
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "From": "dhananikeya@gmail.com",
            "Accept": "application/json",
        },
    )
    last_error = None
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            last_error = exc
            # A missing resource is not fixed by retrying, but SEC blocks
            # (403/429), server errors and network hiccups may be temporary.
            if isinstance(exc, urllib.error.HTTPError) and exc.code not in (
                403, 429, 500, 502, 503, 504
            ):
                raise
            if attempt == 3:
                break
            delay = min(24, 3 * 2 ** attempt)
            if isinstance(exc, urllib.error.HTTPError):
                retry_after = exc.headers.get("Retry-After")
                if retry_after:
                    try:
                        delay = max(delay, min(60, int(retry_after)))
                    except ValueError:
                        pass
            print(
                f"SEC request failed ({url}): {exc}; "
                f"retrying in {delay}s (attempt {attempt + 1}/4)",
                file=sys.stderr,
                flush=True,
            )
            time.sleep(delay)
    raise last_error


def load_universe() -> list[dict]:
    with UNIVERSE_PATH.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_company_shards(output: dict[str, dict]) -> tuple[int, int]:
    """Write one compact SEC filing payload per ticker.

    The monolithic archive remains during the migration so the Filing Tracker
    can continue to operate unchanged. Company Research reads these shards
    directly and avoids deserializing the multi-megabyte archive.
    """
    SHARD_DIR.mkdir(parents=True, exist_ok=True)
    expected_files = set()
    changed_files = 0

    for company_data in output.values():
        ticker = str(company_data.get("ticker", "")).upper().strip()
        safe_ticker = "".join(
            char for char in ticker
            if char.isalnum() or char in ".-"
        )
        if not safe_ticker:
            continue

        filename = f"{safe_ticker}.json"
        expected_files.add(filename)
        path = SHARD_DIR / filename
        text = json.dumps(
            company_data,
            indent=2,
            sort_keys=False,
        ) + "\n"
        old_text = (
            path.read_text(encoding="utf-8")
            if path.exists()
            else ""
        )
        if text != old_text:
            path.write_text(text, encoding="utf-8")
            changed_files += 1

    removed_files = 0
    for path in SHARD_DIR.glob("*.json"):
        if path.name not in expected_files:
            path.unlink()
            removed_files += 1

    return changed_files, removed_files


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


def build_summary(output: dict, generated_at_utc: str) -> dict:
    """Build a lightweight SEC index for startup/home/market views."""
    companies = {}
    recent_rows = []
    synced_companies = 0
    companies_with_material_filings = 0
    indexed_filing_count = 0
    indexed_material_filing_count = 0

    def filing_summary(row: dict) -> dict:
        if not row:
            return {}
        return {
            "form": row.get("form", ""),
            "filing_date": row.get("filing_date", ""),
            "report_date": row.get("report_date", ""),
            "description": (
                row.get("description", "")
                or row.get("primary_document", "")
            ),
            "url": row.get("url", ""),
        }

    for key, feed in output.items():
        ticker = str(feed.get("ticker", "")).upper().strip()
        filings = feed.get("filings", []) or []
        registration = feed.get("registration_filings", []) or []
        material_filings = [
            filing for filing in filings
            if filing.get("form") in MATERIAL_HOME_FORMS
        ]

        indexed_filing_count += len(filings)
        indexed_material_filing_count += len(material_filings)

        if feed.get("cik") and filings:
            synced_companies += 1
        if material_filings:
            companies_with_material_filings += 1

        latest = filings[0] if filings else {}
        latest_material = material_filings[0] if material_filings else {}

        form_counts = {}
        for filing in material_filings:
            form = str(filing.get("form", "")).strip()
            if form:
                form_counts[form] = form_counts.get(form, 0) + 1

        companies[ticker or key] = {
            "ticker": ticker,
            "cik": feed.get("cik", ""),
            "entity_name": feed.get(
                "entity_name",
                key.rsplit(" (", 1)[0],
            ),
            "has_filings": bool(filings),
            "has_material_filings": bool(material_filings),
            "filing_count": len(filings),
            "material_filing_count": len(material_filings),
            "material_form_counts": form_counts,
            "latest_filing": filing_summary(latest),
            "latest_material_filing": filing_summary(latest_material),
            "registration_count": len(registration),
            "registration_scan_complete": bool(
                feed.get("registration_scan_complete", False)
            ),
            "sec_status": feed.get("sec_status", ""),
            "last_checked_utc": feed.get("last_checked_utc", ""),
        }

        for filing in material_filings[:5]:
            filing_date = filing.get("filing_date", "")
            if not filing_date:
                continue
            recent_rows.append({
                "ticker": ticker,
                "company": feed.get(
                    "entity_name",
                    key.rsplit(" (", 1)[0],
                ),
                "form": filing.get("form", ""),
                "filing_date": filing_date,
                "report_date": filing.get("report_date", ""),
                "description": (
                    filing.get("description", "")
                    or filing.get("primary_document", "")
                ),
                "url": filing.get("url", ""),
            })

    recent_rows = sorted(
        recent_rows,
        key=lambda row: row.get("filing_date", ""),
        reverse=True,
    )[:25]

    return {
        "generated_at_utc": generated_at_utc,
        "company_count": len(output),
        "synced_companies": synced_companies,
        "companies_with_material_filings": companies_with_material_filings,
        "indexed_filing_count": indexed_filing_count,
        "indexed_material_filing_count": indexed_material_filing_count,
        "companies": companies,
        "recent_filings": recent_rows,
    }


def main() -> None:
    universe = load_universe()
    if ARCHIVE_PATH.exists():
        with gzip.open(
            ARCHIVE_PATH,
            "rt",
            encoding="utf-8",
        ) as archive_file:
            previous_output = json.load(archive_file)
    elif LEGACY_OUTPUT_PATH.exists():
        previous_output = json.loads(
            LEGACY_OUTPUT_PATH.read_text(
                encoding="utf-8"
            )
        )
    else:
        previous_output = {}
    try:
        ticker_map = load_ticker_map()
    except Exception as exc:
        # A transient outage of the ticker reference should not discard
        # existing CIK mappings for the entire company universe.
        ticker_map = {
            record["ticker"]: {
                "cik": record["cik"],
                "title": record.get("entity_name", ""),
            }
            for record in previous_output.values()
            if record.get("ticker") and record.get("cik")
        }
        print(f"WARNING: SEC ticker list unavailable: {exc}", file=sys.stderr)
        if not ticker_map:
            raise RuntimeError(
                "SEC ticker list failed and no cached CIK mappings exist"
            ) from exc

    observed_at_utc = datetime.now(timezone.utc).isoformat(timespec="seconds")
    output = {}
    successful_checks = 0
    failed_checks = 0

    for company in universe:
        ticker = str(company.get("Ticker", "")).upper().strip()
        company_name = str(company.get("Company", "")).strip()
        key = f"{company_name} ({ticker})"

        previous_company = previous_output.get(key, {})
        ticker_record = ticker_map.get(ticker) or CIK_OVERRIDES.get(ticker)
        if not ticker_record and previous_company.get("cik"):
            ticker_record = {
                "cik": previous_company["cik"],
                "title": previous_company.get("entity_name", company_name),
            }
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
        try:
            submissions = get_json(
                f"https://data.sec.gov/submissions/CIK{cik}.json"
            )
        except Exception as exc:
            failed_checks += 1
            print(
                f"WARNING: {ticker} SEC submissions unavailable: {exc}. "
                "Preserving any previously saved filings.",
                file=sys.stderr,
                flush=True,
            )
            if previous_company:
                output[key] = previous_company
            else:
                output[key] = {
                    "ticker": ticker,
                    "cik": cik,
                    "entity_name": ticker_record.get("title") or company_name,
                    "sector": company.get("Sector", ""),
                    "industry": company.get("Industry", ""),
                    "country": company.get("Country", ""),
                    "last_checked_utc": "",
                    "sec_status": "SEC temporarily unavailable; retry pending",
                    "sec_company_url": (
                        "https://www.sec.gov/edgar/browse/"
                        f"?CIK={int(cik)}&owner=exclude&action=getcompany"
                    ),
                    "filings": [],
                    "registration_filings": [],
                    "registration_scan_complete": False,
                }
            continue
        successful_checks += 1
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
            try:
                historical_registration, registration_scan_complete = (
                    scan_historical_registration_filings(
                        submissions,
                        cik,
                    )
                )
                registration.extend(historical_registration)
            except Exception as exc:
                # Historical lookup is best-effort. Recent filings still
                # deserve to be saved, and history is retried next run.
                print(
                    f"WARNING: {ticker} historical S-1 search failed: {exc}",
                    file=sys.stderr,
                    flush=True,
                )
                registration_scan_complete = False

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
        time.sleep(0.20)

    if failed_checks and not successful_checks:
        raise RuntimeError(
            f"All {failed_checks} SEC company lookups failed. "
            "Leaving the published filing feed unchanged."
        )
    if failed_checks:
        print(
            f"WARNING: {failed_checks} company lookups failed; existing "
            "filings were retained where available.",
            file=sys.stderr,
            flush=True,
        )

    # Do not commit a giant JSON file every 15 minutes merely because the
    # check time changed. Preserve the last published check timestamp if
    # the underlying filing data is identical.
    for key, company_data in output.items():
        previous_company = previous_output.get(key)
        if not previous_company:
            continue
        before = {k: v for k, v in previous_company.items()
                  if k != "last_checked_utc"}
        after = {k: v for k, v in company_data.items()
                 if k != "last_checked_utc"}
        if before == after:
            company_data["last_checked_utc"] = previous_company.get(
                "last_checked_utc", observed_at_utc
            )

    new_text = json.dumps(
        output,
        separators=(",", ":"),
        sort_keys=False,
    )

    old_text = ""
    if ARCHIVE_PATH.exists():
        try:
            with gzip.open(
                ARCHIVE_PATH,
                "rt",
                encoding="utf-8",
            ) as archive_file:
                old_text = archive_file.read()
        except (OSError, UnicodeDecodeError):
            old_text = ""

    feed_changed = new_text != old_text
    if feed_changed:
        with gzip.open(
            ARCHIVE_PATH,
            "wt",
            encoding="utf-8",
            compresslevel=9,
        ) as archive_file:
            archive_file.write(new_text)
        print(
            f"Compressed SEC archive updated for {len(output)} covered companies."
        )
    else:
        print("No SEC filing changes detected.")

    # The per-company shards and summary are the runtime fast paths. Once the
    # compressed archive is available, remove the legacy multi-megabyte JSON.
    if ARCHIVE_PATH.exists() and LEGACY_OUTPUT_PATH.exists():
        LEGACY_OUTPUT_PATH.unlink()
        print("Removed legacy uncompressed SEC archive.")

    shard_changes, shard_removals = write_company_shards(output)
    if shard_changes or shard_removals:
        print(
            "SEC company shards updated: "
            f"{shard_changes} written, {shard_removals} removed."
        )
    else:
        print("No SEC company shard changes detected.")

    summary_generated_at = observed_at_utc
    if not feed_changed and SUMMARY_PATH.exists():
        try:
            previous_summary = json.loads(
                SUMMARY_PATH.read_text(encoding="utf-8")
            )
            summary_generated_at = previous_summary.get(
                "generated_at_utc",
                observed_at_utc,
            )
        except Exception:
            pass

    summary = build_summary(output, summary_generated_at)
    summary_text = json.dumps(
        summary,
        indent=2,
        sort_keys=False,
    ) + "\n"
    old_summary_text = (
        SUMMARY_PATH.read_text(encoding="utf-8")
        if SUMMARY_PATH.exists()
        else ""
    )

    if summary_text != old_summary_text:
        SUMMARY_PATH.write_text(summary_text, encoding="utf-8")
        print(
            "SEC summary updated: "
            f"{summary['synced_companies']} synced companies, "
            f"{len(summary['recent_filings'])} recent material filings."
        )
    else:
        print("No SEC summary changes detected.")


if __name__ == "__main__":
    main()
