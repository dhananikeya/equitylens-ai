"""Refresh sourced annual financial metrics from SEC Company Facts.

This is deliberately separate from the filings monitor: filing discovery does not
automatically populate standardized company financials.

Run: python scripts/update_companyfacts_metrics.py [--limit 20]
No external packages or paid API keys required.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import random
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SEC_SUMMARY = DATA / "sec_summary.json"
UNIVERSE = DATA / "finviz_universe.csv"
OUTPUT = DATA / "generated_company_metrics.json"
STATUS = DATA / "companyfacts_refresh_status.json"
USER_AGENT = "EquityLens AI research app dhananikeya@gmail.com"
BASE_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{}.json"

# US-GAAP taxonomy values in USD. A missing tag remains missing, never zero.
METRICS = {
    "revenue": ["RevenueFromContractWithCustomerExcludingAssessedTax",
                "Revenues", "SalesRevenueNet", "RevenueFromContractWithCustomerIncludingAssessedTax"],
    "gross_profit": ["GrossProfit"],
    "operating_income": ["OperatingIncomeLoss"],
    "net_income": ["NetIncomeLoss", "ProfitLoss"],
    "cash": ["CashAndCashEquivalentsAtCarryingValue"],
    "assets": ["Assets"],
}
FLOW_FIELDS = {"revenue", "gross_profit", "operating_income", "net_income"}


def fetch_companyfacts(cik: str) -> dict:
    req = Request(BASE_URL.format(str(cik).zfill(10)),
                  headers={"User-Agent": USER_AGENT,
                           "From": "dhananikeya@gmail.com",
                           "Accept": "application/json"})
    for attempt in range(4):
        try:
            with urlopen(req, timeout=25) as response:
                return json.load(response)
        except HTTPError as exc:
            if exc.code in (400, 404):
                raise
            if exc.code not in (403, 429, 500, 502, 503, 504):
                raise
            if attempt == 3:
                raise
            time.sleep(min(20, 3 * (2 ** attempt)))
        except (URLError, TimeoutError, OSError):
            if attempt == 3:
                raise
            time.sleep(min(20, 3 * (2 ** attempt)))
    raise RuntimeError("SEC API exhausted retries")


def annual_records(facts: dict, field: str) -> list[dict]:
    namespace = facts.get("facts", {}).get("us-gaap", {})
    candidates = []
    for priority, tag in enumerate(METRICS[field]):
        values = namespace.get(tag, {}).get("units", {}).get("USD", [])
        for row in values:
            if row.get("form") not in ("10-K", "10-K/A"):
                continue
            end = row.get("end", "")
            start = row.get("start")
            if not end or row.get("val") is None:
                continue
            if field in FLOW_FIELDS:
                if not start:
                    continue
                try:
                    days = (date.fromisoformat(end) -
                            date.fromisoformat(start)).days
                except ValueError:
                    continue
                if not 300 <= days <= 380:
                    continue
            elif start:  # Snapshot balances must not use period flows.
                continue
            candidates.append({**row, "_tag_priority": priority})
    return candidates


def choose(records: list[dict], end: str) -> dict | None:
    matching = [r for r in records if r.get("end") == end]
    if not matching:
        return None
    # Prefer first-choice taxonomy, then the most recently filed annual report.
    return sorted(matching, key=lambda r: (
        -r["_tag_priority"], r.get("filed", ""), r.get("accn", "")
    ), reverse=True)[0]


def filing_link(cik: str, record: dict) -> str:
    accession = record.get("accn", "").replace("-", "")
    if not accession:
        return "https://www.sec.gov/edgar/browse/?CIK=" + str(int(cik))
    return ("https://www.sec.gov/Archives/edgar/data/" +
            str(int(cik)) + "/" + accession + "/")


def build_record(ticker: str, company: dict, facts: dict) -> dict | None:
    rows = {key: annual_records(facts, key) for key in METRICS}
    # A financial year needs a dated annual revenue record or comparable
    # annual earnings period. Do not mislabel a quarterly or YTD number as FY.
    annual_ends = sorted(
        {r["end"] for k in FLOW_FIELDS for r in rows[k]},
        reverse=True,
    )
    if not annual_ends:
        return None
    selected_end = annual_ends[0]
    chosen = {key: choose(value, selected_end) for key, value in rows.items()}
    anchor = next((chosen[k] for k in
                   ("revenue", "net_income", "operating_income", "gross_profit")
                   if chosen[k]), None)
    if not anchor:
        return None
    history = []
    for period_end in annual_ends[:5]:
        entry = {"fiscal_year": int(period_end[:4])}
        for field in ("revenue", "operating_income"):
            rec = choose(rows[field], period_end)
            if rec:
                entry[field] = rec["val"]
        if len(entry) > 1:
            history.append(entry)
    history.reverse()
    # SEC FY values are useful, but the actual fiscal year label can differ
    # from the end calendar year. Mark period end as authoritative.
    result = {
        "ticker": ticker,
        "industry": company.get("industry", ""),
        "fiscal_year": int(selected_end[:4]),
        "fiscal_year_end": selected_end,
        "source": "SEC Company Facts / 10-K",
        "filing_url": filing_link(company["cik"], anchor),
        "history": history,
        "data_source": "SEC XBRL companyfacts",
        "last_refreshed_utc": datetime.now(timezone.utc).isoformat(),
    }
    for field, value in chosen.items():
        if value:
            result[field] = value["val"]
    return result


def atomic_json(path: Path, data: dict) -> None:
    temp = path.with_name(path.name + ".tmp")
    temp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8")
    os.replace(temp, path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=50,
                        help="Maximum companies to try per run (default 50)")
    parser.add_argument("--all", action="store_true",
                        help="Try all companies; requires sufficient runtime")
    parser.add_argument("--dry-run", action="store_true",
                        help="Inspect without writing generated files")
    args = parser.parse_args()
    summary = json.loads(SEC_SUMMARY.read_text(encoding="utf-8"))
    companies = summary.get("companies", {})
    if not companies:
        raise RuntimeError("SEC CIK summary is empty; refusing to erase data")
    universe = list(csv.DictReader(UNIVERSE.open(encoding="utf-8-sig",
                                                newline="")))
    names = {str(row["Ticker"]).upper(): row for row in universe}
    existing = json.loads(OUTPUT.read_text(encoding="utf-8")) if OUTPUT.exists() else {}
    if not isinstance(existing, dict):
        raise RuntimeError("Existing generated metrics are not a dictionary")
    prior = json.loads(STATUS.read_text(encoding="utf-8")) if STATUS.exists() else {}
    # Rotate through companies across runs, rather than repeatedly refreshing
    # only the first alphabetical 50. Failures are eligible for later retries.
    cursor = int(prior.get("next_index", 0))
    tickers = sorted(t for t in companies if t in names)
    if not tickers:
        raise RuntimeError("No overlap between SEC CIKs and market universe")
    ordered = tickers[cursor:] + tickers[:cursor]
    selected = ordered if args.all else ordered[:max(1, args.limit)]
    updated = dict(existing)
    successes, empty, failures = 0, 0, {}
    for ticker in selected:
        company = companies[ticker]
        cik = company.get("cik")
        if not cik:
            empty += 1
            continue
        row = names[ticker]
        key = f"{row.get('Company', '').strip()} ({ticker})"
        try:
            payload = fetch_companyfacts(cik)
            record = build_record(ticker, {
                "cik": cik, "industry": row.get("Industry", "")
            }, payload)
            if record:
                updated[key] = record
                successes += 1
            else:
                empty += 1
        except Exception as exc:
            failures[ticker] = str(exc)[:180]
            print(f"WARNING {ticker}: {exc}", file=sys.stderr, flush=True)
        time.sleep(0.18)  # Stay below SEC fair-access request threshold.
    next_index = (cursor + len(selected)) % len(tickers)
    status = {
        "last_attempt_utc": datetime.now(timezone.utc).isoformat(),
        "company_universe": len(tickers),
        "attempted": len(selected),
        "updated": successes,
        "without_annual_us_gaap": empty,
        "failed": len(failures),
        "failure_examples": dict(list(failures.items())[:15]),
        "next_index": next_index,
        "generated_metric_records": len(updated),
    }
    print(json.dumps(status, indent=2))
    if args.dry_run:
        return
    # If the SEC API is completely blocked, never publish an empty update.
    if failures and not successes and not empty:
        raise RuntimeError("All SEC API requests failed; existing data unchanged")
    if updated != existing:
        atomic_json(OUTPUT, updated)
    atomic_json(STATUS, status)


if __name__ == "__main__":
    main()
