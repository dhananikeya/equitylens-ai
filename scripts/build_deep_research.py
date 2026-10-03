"""Build schema-compatible deep research for the full EquityLens universe.

This worker:
1. Reads the 517-company Finviz universe.
2. Resolves each ticker to an SEC CIK.
3. Pulls current SEC submissions and company facts.
4. Finds annual, quarterly, current-report, and registration filings.
5. Extracts structured financial metrics from SEC XBRL facts.
6. Uses OpenAI Structured Outputs to turn primary-source filing text into the
   same research schema already used by EquityLens' hand-curated companies.
7. Writes incremental generated JSON files so the website can merge generated
   coverage with the hand-curated research set.

Hand-curated records remain authoritative in app.py and override generated
records for the same ticker.
"""

from __future__ import annotations

import csv
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
UNIVERSE_PATH = ROOT / "data" / "finviz_universe.csv"
HAND_METRICS_PATH = ROOT / "data" / "company_metrics.json"
METRICS_PATH = ROOT / "data" / "generated_company_metrics.json"
QUARTERLY_PATH = ROOT / "data" / "generated_company_quarterly.json"
ANALYSIS_PATH = ROOT / "data" / "generated_company_analysis.json"
S1_PATH = ROOT / "data" / "generated_company_s1.json"
STATE_PATH = ROOT / "data" / "research_pipeline_state.json"

LOCAL_LLM_PROVIDER = os.getenv("LOCAL_LLM_PROVIDER", "ollama").strip().lower()
LOCAL_LLM_URL = os.getenv("LOCAL_LLM_URL", "").strip()
LOCAL_LLM_MODEL = os.getenv("LOCAL_LLM_MODEL", "").strip()
BATCH_SIZE = max(1, int(os.getenv("RESEARCH_BATCH_SIZE", "40")))
MAX_ATTEMPTS = max(1, int(os.getenv("RESEARCH_MAX_ATTEMPTS", "3")))
SEC_DELAY_SECONDS = float(os.getenv("SEC_REQUEST_DELAY_SECONDS", "0.12"))

SEC_HEADERS = {
    "User-Agent": "EquityLens AI research app dhananikeya@gmail.com",
    "From": "dhananikeya@gmail.com",
    "Accept": "application/json,text/html,*/*",
}

ANNUAL_FORMS = {"10-K", "10-K/A", "20-F", "20-F/A", "40-F", "40-F/A"}
QUARTERLY_FORMS = {"10-Q", "10-Q/A"}
CURRENT_FORMS = {"8-K", "8-K/A", "6-K", "6-K/A"}
REGISTRATION_FORMS = {
    "S-1", "S-1/A",
    "F-1", "F-1/A",
    "S-11", "S-11/A",
}

RESEARCH_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "business_model": {"type": "string"},
        "primary_revenue_source": {"type": "string"},
        "customer_type": {"type": "string"},
        "platform_dependency": {"type": "string"},
        "competitive_risk": {"type": "string"},
        "operational_risk": {"type": "string"},
        "profitability_history": {"type": "string"},
        "customer_concentration": {"type": "string"},
        "international_exposure": {"type": "string"},
        "key_risk_themes": {
            "type": "array",
            "items": {"type": "string"},
            "maxItems": 10,
        },
        "recent_performance_summary": {"type": "string"},
        "historical_context": {"type": "string"},
        "what_to_learn": {"type": "string"},
        "filing_details": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "business_revenue_model": {
                    "type": "array",
                    "items": {"type": "string"},
                    "maxItems": 6,
                },
                "customers_go_to_market": {
                    "type": "array",
                    "items": {"type": "string"},
                    "maxItems": 6,
                },
                "growth_market_opportunity": {
                    "type": "array",
                    "items": {"type": "string"},
                    "maxItems": 6,
                },
                "competition_differentiation": {
                    "type": "array",
                    "items": {"type": "string"},
                    "maxItems": 6,
                },
                "risk_factors": {
                    "type": "array",
                    "items": {"type": "string"},
                    "maxItems": 8,
                },
                "financial_history": {
                    "type": "array",
                    "items": {"type": "string"},
                    "maxItems": 6,
                },
                "ipo_capitalization_dilution": {
                    "type": "array",
                    "items": {"type": "string"},
                    "maxItems": 6,
                },
                "proceeds_management_ownership": {
                    "type": "array",
                    "items": {"type": "string"},
                    "maxItems": 6,
                },
            },
            "required": [
                "business_revenue_model",
                "customers_go_to_market",
                "growth_market_opportunity",
                "competition_differentiation",
                "risk_factors",
                "financial_history",
                "ipo_capitalization_dilution",
                "proceeds_management_ownership",
            ],
        },
        "confidence_notes": {
            "type": "array",
            "items": {"type": "string"},
            "maxItems": 6,
        },
    },
    "required": [
        "business_model",
        "primary_revenue_source",
        "customer_type",
        "platform_dependency",
        "competitive_risk",
        "operational_risk",
        "profitability_history",
        "customer_concentration",
        "international_exposure",
        "key_risk_themes",
        "recent_performance_summary",
        "historical_context",
        "what_to_learn",
        "filing_details",
        "confidence_notes",
    ],
}


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return default
    return json.loads(text)


def write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def get(url: str, accept: str = "application/json") -> requests.Response:
    headers = dict(SEC_HEADERS)
    headers["Accept"] = accept
    last_error = None
    for attempt in range(4):
        try:
            response = requests.get(url, headers=headers, timeout=45)
            response.raise_for_status()
            time.sleep(SEC_DELAY_SECONDS)
            return response
        except Exception as exc:
            last_error = exc
            if attempt < 3:
                time.sleep(2 ** attempt)
    raise last_error


def get_json(url: str) -> dict:
    return get(url, "application/json").json()


def load_universe() -> list[dict]:
    with UNIVERSE_PATH.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def load_ticker_directory() -> dict[str, dict]:
    payload = get_json("https://www.sec.gov/files/company_tickers.json")
    output = {}
    for row in payload.values():
        ticker = str(row.get("ticker", "")).upper().strip()
        if ticker:
            output[ticker] = {
                "cik": str(row.get("cik_str", "")).zfill(10),
                "title": row.get("title", ""),
            }
    return output


def filing_url(cik: str, accession: str, primary_document: str) -> str:
    if not cik or not accession or not primary_document:
        return ""
    return (
        "https://www.sec.gov/Archives/edgar/data/"
        + str(int(cik))
        + "/"
        + accession.replace("-", "")
        + "/"
        + primary_document
    )


def rows_from_submission_arrays(payload: dict, cik: str) -> list[dict]:
    if "filings" in payload:
        data = payload.get("filings", {}).get("recent", {})
    else:
        data = payload

    forms = data.get("form", []) if isinstance(data, dict) else []
    rows = []

    def value(field: str, index: int, default=""):
        values = data.get(field, []) if isinstance(data, dict) else []
        return values[index] if index < len(values) else default

    for index, form in enumerate(forms):
        accession = value("accessionNumber", index)
        primary_document = value("primaryDocument", index)
        rows.append({
            "form": form,
            "filing_date": value("filingDate", index),
            "report_date": value("reportDate", index),
            "acceptance_datetime": value("acceptanceDateTime", index),
            "accession_number": accession,
            "primary_document": primary_document,
            "description": value("primaryDocDescription", index),
            "items": value("items", index),
            "url": filing_url(cik, accession, primary_document),
        })

    return rows


def latest_filing(rows: list[dict], forms: set[str]) -> dict:
    for row in rows:
        if row.get("form") in forms:
            return row
    return {}


def registration_filings(submissions: dict, cik: str) -> list[dict]:
    rows = rows_from_submission_arrays(submissions, cik)
    found = [
        row for row in rows
        if row.get("form") in REGISTRATION_FORMS
    ]

    if not found:
        history_files = submissions.get("filings", {}).get("files", []) or []
        for history in history_files:
            name = history.get("name")
            if not name:
                continue
            try:
                payload = get_json(
                    "https://data.sec.gov/submissions/" + name
                )
            except Exception:
                continue
            historical_rows = rows_from_submission_arrays(payload, cik)
            found.extend(
                row for row in historical_rows
                if row.get("form") in REGISTRATION_FORMS
            )
            if found:
                break

    seen = set()
    unique = []
    for row in sorted(
        found,
        key=lambda item: item.get("filing_date", ""),
        reverse=True,
    ):
        accession = row.get("accession_number")
        if accession and accession in seen:
            continue
        if accession:
            seen.add(accession)
        unique.append(row)
    return unique


def normalize_document_text(raw_html: str) -> str:
    soup = BeautifulSoup(raw_html, "html.parser")
    for node in soup(["script", "style", "noscript"]):
        node.decompose()

    text = soup.get_text("\n")
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text)
    return text.strip()


def filing_text(filing: dict) -> str:
    url = filing.get("url", "")
    if not url:
        return ""
    response = get(url, "text/html,application/xhtml+xml,*/*")
    return normalize_document_text(response.text)


def focused_excerpt(text: str, max_chars: int = 150_000) -> str:
    if not text:
        return ""
    if len(text) <= max_chars:
        return text

    keywords = [
        "business",
        "risk factors",
        "competition",
        "customers",
        "management's discussion",
        "management’s discussion",
        "results of operations",
        "use of proceeds",
        "dilution",
        "principal stockholders",
        "market opportunity",
        "revenue",
    ]

    lower = text.lower()
    windows: list[tuple[int, int]] = [(0, min(25_000, len(text)))]

    for keyword in keywords:
        start = 0
        matches = 0
        while matches < 2:
            pos = lower.find(keyword, start)
            if pos < 0:
                break
            windows.append((
                max(0, pos - 5_000),
                min(len(text), pos + 18_000),
            ))
            start = pos + len(keyword)
            matches += 1

    windows.sort()
    merged = []
    for start, end in windows:
        if not merged or start > merged[-1][1]:
            merged.append([start, end])
        else:
            merged[-1][1] = max(merged[-1][1], end)

    chunks = []
    used = 0
    for start, end in merged:
        chunk = text[start:end]
        remaining = max_chars - used
        if remaining <= 0:
            break
        chunks.append(chunk[:remaining])
        used += min(len(chunk), remaining)

    return "\n\n--- EXCERPT BREAK ---\n\n".join(chunks)


FACT_TAGS = {
    "revenue": [
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "Revenues",
        "SalesRevenueNet",
        "Revenue",
    ],
    "gross_profit": ["GrossProfit"],
    "operating_income": [
        "OperatingIncomeLoss",
        "ProfitLossFromOperatingActivities",
    ],
    "net_income": [
        "NetIncomeLoss",
        "ProfitLoss",
        "ProfitLossAttributableToOwnersOfParent",
    ],
    "assets": ["Assets"],
    "cash": [
        "CashAndCashEquivalentsAtCarryingValue",
        "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",
        "CashAndCashEquivalents",
    ],
    "short_term_investments": [
        "ShortTermInvestments",
        "MarketableSecuritiesCurrent",
        "ShorttermInvestments",
    ],
    "shares_outstanding": [
        "EntityCommonStockSharesOutstanding",
        "CommonStocksIncludingAdditionalPaidInCapitalMember",
    ],
    "debt_current": [
        "LongTermDebtCurrent",
        "LongTermDebtAndFinanceLeaseObligationsCurrent",
        "CurrentDebt",
    ],
    "debt_noncurrent": [
        "LongTermDebtNoncurrent",
        "LongTermDebtAndFinanceLeaseObligationsNoncurrent",
        "NoncurrentDebt",
    ],
    "debt_total": [
        "LongTermDebt",
        "LongTermDebtAndFinanceLeaseObligations",
        "DebtAndFinanceLeaseObligations",
    ],
}


def fact_object(companyfacts: dict, tag: str) -> dict | None:
    for namespace in ("us-gaap", "ifrs-full", "dei"):
        obj = companyfacts.get("facts", {}).get(namespace, {}).get(tag)
        if obj:
            return obj
    return None


def fact_points(
    companyfacts: dict,
    tags: list[str],
    preferred_units: tuple[str, ...] = ("USD",),
) -> list[dict]:
    for tag in tags:
        obj = fact_object(companyfacts, tag)
        if not obj:
            continue
        units = obj.get("units", {})
        for unit in preferred_units:
            points = units.get(unit)
            if points:
                return [point for point in points if point.get("val") is not None]
        for points in units.values():
            if points:
                return [point for point in points if point.get("val") is not None]
    return []


def dedupe_period_points(points: list[dict]) -> list[dict]:
    output = {}
    for point in points:
        key = (
            point.get("frame")
            or point.get("end")
            or point.get("filed")
            or str(point.get("val"))
        )
        previous = output.get(key)
        if previous is None or point.get("filed", "") > previous.get("filed", ""):
            output[key] = point
    return sorted(
        output.values(),
        key=lambda item: (
            item.get("end", ""),
            item.get("filed", ""),
        ),
        reverse=True,
    )


def annual_points(companyfacts: dict, metric: str) -> list[dict]:
    points = fact_points(companyfacts, FACT_TAGS[metric])
    filtered = [
        point for point in points
        if point.get("form") in ANNUAL_FORMS
        and (
            point.get("fp") == "FY"
            or str(point.get("frame", "")).endswith("CY")
            or not point.get("fp")
        )
    ]
    return dedupe_period_points(filtered)


def quarterly_points(companyfacts: dict, metric: str) -> list[dict]:
    points = fact_points(companyfacts, FACT_TAGS[metric])
    filtered = [
        point for point in points
        if point.get("form") in QUARTERLY_FORMS
        and re.search(r"Q[1-4]$", str(point.get("frame", "")))
    ]
    return dedupe_period_points(filtered)


def latest_balance_point(
    companyfacts: dict,
    metric: str,
    preferred_units: tuple[str, ...] = ("USD",),
) -> dict:
    points = fact_points(
        companyfacts,
        FACT_TAGS[metric],
        preferred_units=preferred_units,
    )
    points = [
        point for point in points
        if point.get("form") in ANNUAL_FORMS | QUARTERLY_FORMS
    ]
    ordered = dedupe_period_points(points)
    return ordered[0] if ordered else {}


def numeric(point: dict) -> float | int | None:
    value = point.get("val") if point else None
    if isinstance(value, (int, float)):
        return value
    return None


def metric_value_for_period(
    points: list[dict],
    end: str | None = None,
    fy: int | None = None,
) -> float | int | None:
    for point in points:
        if end and point.get("end") == end:
            return numeric(point)
        if fy is not None and point.get("fy") == fy:
            return numeric(point)
    return None


def build_financial_records(
    key: str,
    company: dict,
    companyfacts: dict,
    annual_filing: dict,
    quarterly_filing: dict,
) -> tuple[dict, dict, dict]:
    annual = {
        metric: annual_points(companyfacts, metric)
        for metric in [
            "revenue",
            "gross_profit",
            "operating_income",
            "net_income",
        ]
    }

    revenue_annual = annual["revenue"]
    latest_revenue_point = revenue_annual[0] if revenue_annual else {}
    latest_end = latest_revenue_point.get("end")
    latest_fy = latest_revenue_point.get("fy")

    history = []
    for point in revenue_annual[:3]:
        fy = point.get("fy")
        end = point.get("end")
        history.append({
            "fiscal_year": fy or (
                int(end[:4]) if isinstance(end, str) and len(end) >= 4 else None
            ),
            "revenue": numeric(point),
            "operating_income": metric_value_for_period(
                annual["operating_income"],
                end=end,
                fy=fy,
            ),
        })
    history = list(reversed(history))

    cash_point = latest_balance_point(companyfacts, "cash")
    investments_point = latest_balance_point(
        companyfacts,
        "short_term_investments",
    )
    assets_point = latest_balance_point(companyfacts, "assets")
    shares_point = latest_balance_point(
        companyfacts,
        "shares_outstanding",
        preferred_units=("shares",),
    )

    debt_current = numeric(
        latest_balance_point(companyfacts, "debt_current")
    )
    debt_noncurrent = numeric(
        latest_balance_point(companyfacts, "debt_noncurrent")
    )
    debt_total_point = latest_balance_point(companyfacts, "debt_total")

    if debt_current is not None or debt_noncurrent is not None:
        total_debt = (debt_current or 0) + (debt_noncurrent or 0)
    else:
        total_debt = numeric(debt_total_point)

    cash = numeric(cash_point)
    investments = numeric(investments_point)
    cash_and_investments = None
    if cash is not None or investments is not None:
        cash_and_investments = (cash or 0) + (investments or 0)

    metrics_record = {
        "ticker": company.get("Ticker", ""),
        "industry": company.get("Industry", "Unclassified"),
        "sector": company.get("Sector", ""),
        "country": company.get("Country", ""),
        "fiscal_year": latest_fy or (
            int(latest_end[:4])
            if isinstance(latest_end, str) and len(latest_end) >= 4
            else None
        ),
        "fiscal_year_end": latest_end,
        "source": annual_filing.get("form", "SEC annual filing"),
        "filing_url": annual_filing.get("url", ""),
        "revenue": numeric(latest_revenue_point),
        "gross_profit": metric_value_for_period(
            annual["gross_profit"],
            end=latest_end,
            fy=latest_fy,
        ),
        "operating_income": metric_value_for_period(
            annual["operating_income"],
            end=latest_end,
            fy=latest_fy,
        ),
        "net_income": metric_value_for_period(
            annual["net_income"],
            end=latest_end,
            fy=latest_fy,
        ),
        "cash": cash,
        "assets": numeric(assets_point),
        "history": history,
        "capital_structure": {
            "shares_outstanding": numeric(shares_point),
            "shares_as_of": shares_point.get("end") if shares_point else None,
            "total_debt": total_debt,
            "cash_and_investments": cash_and_investments,
            "balance_sheet_as_of": (
                assets_point.get("end")
                if assets_point
                else cash_point.get("end") if cash_point else None
            ),
            "source_filing": (
                quarterly_filing.get("url")
                or annual_filing.get("url", "")
            ),
        },
    }

    quarter_metrics = {
        metric: quarterly_points(companyfacts, metric)
        for metric in [
            "revenue",
            "gross_profit",
            "operating_income",
            "net_income",
        ]
    }

    latest_quarter_point = (
        quarter_metrics["revenue"][0]
        if quarter_metrics["revenue"]
        else {}
    )
    quarter_end = latest_quarter_point.get("end")
    quarter_frame = latest_quarter_point.get("frame")

    def quarter_record(index: int) -> dict:
        revenue_points = quarter_metrics["revenue"]
        if index >= len(revenue_points):
            return {
                "revenue": None,
                "gross_profit": None,
                "operating_income": None,
                "net_income": None,
            }
        point = revenue_points[index]
        end = point.get("end")
        return {
            "revenue": numeric(point),
            "gross_profit": metric_value_for_period(
                quarter_metrics["gross_profit"],
                end=end,
            ),
            "operating_income": metric_value_for_period(
                quarter_metrics["operating_income"],
                end=end,
            ),
            "net_income": metric_value_for_period(
                quarter_metrics["net_income"],
                end=end,
            ),
        }

    latest_quarter = quarter_record(0)
    prior_quarter = quarter_record(1)

    prior_year_quarter = {
        "revenue": None,
        "gross_profit": None,
        "operating_income": None,
        "net_income": None,
    }
    if quarter_frame:
        match = re.match(r"CY(\d{4})Q([1-4])$", str(quarter_frame))
        if match:
            prior_frame = "CY" + str(int(match.group(1)) - 1) + "Q" + match.group(2)
            for point in quarter_metrics["revenue"]:
                if point.get("frame") == prior_frame:
                    end = point.get("end")
                    prior_year_quarter = {
                        "revenue": numeric(point),
                        "gross_profit": metric_value_for_period(
                            quarter_metrics["gross_profit"],
                            end=end,
                        ),
                        "operating_income": metric_value_for_period(
                            quarter_metrics["operating_income"],
                            end=end,
                        ),
                        "net_income": metric_value_for_period(
                            quarter_metrics["net_income"],
                            end=end,
                        ),
                    }
                    break

    def ltm_value(metric: str) -> float | int | None:
        points = quarter_metrics[metric][:4]
        values = [numeric(point) for point in points]
        if len(values) < 4 or any(value is None for value in values):
            return None
        return sum(values)

    quarterly_record = {
        "quarter_label": quarter_frame or (
            "Latest quarter" if quarter_end else "Quarterly data unavailable"
        ),
        "period_end": quarter_end,
        "source_filing": quarterly_filing.get("url", ""),
        "latest_quarter": latest_quarter,
        "prior_quarter": prior_quarter,
        "prior_year_quarter": prior_year_quarter,
        "current_ytd": {
            "revenue": None,
            "gross_profit": None,
            "operating_income": None,
            "net_income": None,
        },
        "prior_year_ytd": {
            "revenue": None,
            "gross_profit": None,
            "operating_income": None,
            "net_income": None,
        },
        "ltm": {
            "revenue": ltm_value("revenue"),
            "gross_profit": ltm_value("gross_profit"),
            "operating_income": ltm_value("operating_income"),
            "net_income": ltm_value("net_income"),
        },
    }

    financial_context = {
        "annual": {
            "fiscal_year": metrics_record["fiscal_year"],
            "period_end": metrics_record["fiscal_year_end"],
            "revenue": metrics_record["revenue"],
            "gross_profit": metrics_record["gross_profit"],
            "operating_income": metrics_record["operating_income"],
            "net_income": metrics_record["net_income"],
            "cash": metrics_record["cash"],
            "assets": metrics_record["assets"],
        },
        "quarterly": {
            "period": quarterly_record["quarter_label"],
            "period_end": quarterly_record["period_end"],
            **latest_quarter,
        },
        "ltm": quarterly_record["ltm"],
        "capital_structure": metrics_record["capital_structure"],
    }

    return metrics_record, quarterly_record, financial_context


def research_prompt(
    company: dict,
    financial_context: dict,
    annual_filing: dict,
    quarterly_filing: dict,
    registration_filing: dict,
    annual_excerpt: str,
    quarterly_excerpt: str,
    registration_excerpt: str,
) -> str:
    evidence = {
        "company": {
            "ticker": company.get("Ticker", ""),
            "name": company.get("Company", ""),
            "sector": company.get("Sector", ""),
            "industry": company.get("Industry", ""),
            "country": company.get("Country", ""),
        },
        "financial_context_from_sec_xbrl": financial_context,
        "annual_filing": {
            "form": annual_filing.get("form", ""),
            "filed": annual_filing.get("filing_date", ""),
            "report_date": annual_filing.get("report_date", ""),
            "url": annual_filing.get("url", ""),
        },
        "quarterly_filing": {
            "form": quarterly_filing.get("form", ""),
            "filed": quarterly_filing.get("filing_date", ""),
            "report_date": quarterly_filing.get("report_date", ""),
            "url": quarterly_filing.get("url", ""),
        },
        "registration_filing": {
            "form": registration_filing.get("form", ""),
            "filed": registration_filing.get("filing_date", ""),
            "url": registration_filing.get("url", ""),
        },
    }

    return (
        "Build a structured public-company research record using ONLY the supplied "
        "SEC-derived evidence. Do not make investment recommendations, price targets, "
        "rankings, or predictions. Do not invent facts. If a requested detail is not "
        "supported by the supplied evidence, write 'Not disclosed in the supplied filing.' "
        "Treat risk factors as company disclosures, not predictions. Distinguish current "
        "annual/quarterly context from IPO-era registration context. Keep each field concise "
        "but substantive enough to be useful to a research user.\n\n"
        "SEC/XBRL CONTEXT:\n"
        + json.dumps(evidence, indent=2)
        + "\n\nANNUAL FILING EXCERPT:\n"
        + (annual_excerpt or "[not available]")
        + "\n\nLATEST QUARTERLY FILING EXCERPT:\n"
        + (quarterly_excerpt or "[not available]")
        + "\n\nREGISTRATION FILING EXCERPT:\n"
        + (registration_excerpt or "[not available]")
    )


def local_llm_base_url() -> str:
    if LOCAL_LLM_URL:
        return LOCAL_LLM_URL.rstrip("/")

    if LOCAL_LLM_PROVIDER == "ollama":
        return "http://127.0.0.1:11434"

    if LOCAL_LLM_PROVIDER in {"openai_compatible", "lmstudio", "lm_studio"}:
        return "http://127.0.0.1:1234/v1"

    raise ValueError(
        "Unsupported LOCAL_LLM_PROVIDER. Use 'ollama' or 'openai_compatible'."
    )


def detect_local_model() -> str:
    if LOCAL_LLM_MODEL:
        return LOCAL_LLM_MODEL

    base_url = local_llm_base_url()

    if LOCAL_LLM_PROVIDER == "ollama":
        response = requests.get(
            base_url + "/api/tags",
            timeout=15,
        )
        response.raise_for_status()
        models = response.json().get("models", [])
        if not models:
            raise RuntimeError(
                "Ollama is reachable, but no local models are installed."
            )
        return str(models[0].get("name", "")).strip()

    response = requests.get(
        base_url + "/models",
        timeout=15,
    )
    response.raise_for_status()
    models = response.json().get("data", [])
    if not models:
        raise RuntimeError(
            "The local OpenAI-compatible server is reachable, but it exposes no models."
        )
    return str(models[0].get("id", "")).strip()


def extract_json_object(text: str) -> dict:
    cleaned = (text or "").strip()

    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.I)
        cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        payload = json.loads(cleaned)
        if isinstance(payload, dict):
            return payload
    except json.JSONDecodeError:
        pass

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start >= 0 and end > start:
        payload = json.loads(cleaned[start:end + 1])
        if isinstance(payload, dict):
            return payload

    raise ValueError("Local LLM did not return a valid JSON object.")


def validate_research_payload(payload: dict) -> dict:
    required = set(RESEARCH_SCHEMA["required"])
    missing = sorted(required - set(payload.keys()))
    if missing:
        raise ValueError(
            "Local LLM response is missing required research fields: "
            + ", ".join(missing)
        )

    filing_details = payload.get("filing_details", {})
    required_details = set(
        RESEARCH_SCHEMA["properties"]["filing_details"]["required"]
    )
    missing_details = sorted(required_details - set(filing_details.keys()))
    if missing_details:
        raise ValueError(
            "Local LLM response is missing filing-detail fields: "
            + ", ".join(missing_details)
        )

    return payload


def generate_research(
    prompt: str,
    model: str,
) -> dict:
    base_url = local_llm_base_url()

    system_prompt = (
        "You are EquityLens' SEC filing research extraction engine. "
        "Use only the supplied SEC-derived evidence. "
        "Return one JSON object matching the requested schema exactly. "
        "Do not include markdown fences, commentary, investment recommendations, "
        "price targets, rankings, or unsupported facts."
    )

    if LOCAL_LLM_PROVIDER == "ollama":
        response = requests.post(
            base_url + "/api/chat",
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                "stream": False,
                "format": RESEARCH_SCHEMA,
                "options": {
                    "temperature": 0.1,
                },
            },
            timeout=900,
        )
        response.raise_for_status()
        content = (
            response.json()
            .get("message", {})
            .get("content", "")
        )
        return validate_research_payload(
            extract_json_object(content)
        )

    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.1,
        "response_format": {"type": "json_object"},
    }

    response = requests.post(
        base_url + "/chat/completions",
        json=body,
        timeout=900,
    )

    # Some local OpenAI-compatible servers do not implement response_format.
    if response.status_code >= 400:
        body.pop("response_format", None)
        response = requests.post(
            base_url + "/chat/completions",
            json=body,
            timeout=900,
        )

    response.raise_for_status()
    payload = response.json()
    content = (
        payload.get("choices", [{}])[0]
        .get("message", {})
        .get("content", "")
    )
    return validate_research_payload(
        extract_json_object(content)
    )



def main() -> None:
    model = detect_local_model()
    print(
        "Using local LLM provider "
        + LOCAL_LLM_PROVIDER
        + " with model "
        + model
        + " at "
        + local_llm_base_url()
    )

    universe = load_universe()
    ticker_directory = load_ticker_directory()

    hand_metrics = read_json(HAND_METRICS_PATH, {})
    hand_key_by_ticker = {
        str(record.get("ticker", "")).upper(): key
        for key, record in hand_metrics.items()
        if record.get("ticker")
    }

    generated_metrics = read_json(METRICS_PATH, {})
    generated_quarterly = read_json(QUARTERLY_PATH, {})
    generated_analysis = read_json(ANALYSIS_PATH, {})
    generated_s1 = read_json(S1_PATH, {})
    state = read_json(STATE_PATH, {})

    def canonical_key(company: dict) -> str:
        ticker = str(company.get("Ticker", "")).upper().strip()
        return hand_key_by_ticker.get(
            ticker,
            f"{company.get('Company', '').strip()} ({ticker})",
        )

    candidates = []
    for company in universe:
        ticker = str(company.get("Ticker", "")).upper().strip()
        key = canonical_key(company)
        ticker_state = state.get(ticker, {})
        if key in generated_analysis:
            continue
        if int(ticker_state.get("attempts", 0)) >= MAX_ATTEMPTS:
            continue
        candidates.append((key, company))
        if len(candidates) >= BATCH_SIZE:
            break

    if not candidates:
        print("No missing companies remain in the current deep-research queue.")
        return

    print(
        f"Processing {len(candidates)} companies with local model {model}. "
        f"Current generated coverage: {len(generated_analysis)}/{len(universe)}."
    )

    for index, (key, company) in enumerate(candidates, start=1):
        ticker = str(company.get("Ticker", "")).upper().strip()
        print(f"[{index}/{len(candidates)}] {ticker} · {company.get('Company', '')}")

        ticker_state = state.get(ticker, {})
        ticker_state["attempts"] = int(ticker_state.get("attempts", 0)) + 1
        ticker_state["last_attempt_utc"] = datetime.now(
            timezone.utc
        ).isoformat(timespec="seconds")

        try:
            ticker_record = ticker_directory.get(ticker)
            if not ticker_record:
                raise ValueError("Ticker could not be resolved to an SEC CIK.")

            cik = ticker_record["cik"]
            submissions = get_json(
                f"https://data.sec.gov/submissions/CIK{cik}.json"
            )
            recent_rows = rows_from_submission_arrays(submissions, cik)

            annual_filing = latest_filing(recent_rows, ANNUAL_FORMS)
            quarterly_filing = latest_filing(recent_rows, QUARTERLY_FORMS)
            current_filing = latest_filing(recent_rows, CURRENT_FORMS)
            registrations = registration_filings(submissions, cik)
            registration_filing = registrations[0] if registrations else {}

            if not annual_filing and not quarterly_filing:
                raise ValueError(
                    "No supported annual or quarterly SEC filing was found."
                )

            companyfacts = get_json(
                f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
            )

            metrics_record, quarterly_record, financial_context = (
                build_financial_records(
                    key,
                    company,
                    companyfacts,
                    annual_filing,
                    quarterly_filing,
                )
            )

            annual_excerpt = ""
            quarterly_excerpt = ""
            registration_excerpt = ""

            if annual_filing:
                try:
                    annual_excerpt = focused_excerpt(
                        filing_text(annual_filing),
                        max_chars=150_000,
                    )
                except Exception as exc:
                    print(f"  annual filing text unavailable: {exc}")

            if quarterly_filing:
                try:
                    quarterly_excerpt = focused_excerpt(
                        filing_text(quarterly_filing),
                        max_chars=80_000,
                    )
                except Exception as exc:
                    print(f"  quarterly filing text unavailable: {exc}")

            if registration_filing:
                try:
                    registration_excerpt = focused_excerpt(
                        filing_text(registration_filing),
                        max_chars=150_000,
                    )
                except Exception as exc:
                    print(f"  registration filing text unavailable: {exc}")

            prompt = research_prompt(
                company,
                financial_context,
                annual_filing,
                quarterly_filing,
                registration_filing,
                annual_excerpt,
                quarterly_excerpt,
                registration_excerpt,
            )
            research = generate_research(prompt, model)

            generated_metrics[key] = metrics_record
            generated_quarterly[key] = quarterly_record
            generated_analysis[key] = {
                "business_model": research["business_model"],
                "primary_revenue_source": research["primary_revenue_source"],
                "customer_type": research["customer_type"],
                "platform_dependency": research["platform_dependency"],
                "competitive_risk": research["competitive_risk"],
                "operational_risk": research["operational_risk"],
                "profitability_history": research["profitability_history"],
                "customer_concentration": research["customer_concentration"],
                "international_exposure": research["international_exposure"],
                "key_risk_themes": research["key_risk_themes"],
                "recent_performance_summary": research[
                    "recent_performance_summary"
                ],
                "confidence_notes": research["confidence_notes"],
                "source_filing": (
                    annual_filing.get("url")
                    or quarterly_filing.get("url", "")
                ),
                "latest_current_filing": current_filing.get("url", ""),
                "generated_by": (
                    "local:"
                    + LOCAL_LLM_PROVIDER
                    + ":"
                    + model
                ),
                "generated_at_utc": datetime.now(
                    timezone.utc
                ).isoformat(timespec="seconds"),
            }

            if registration_filing:
                generated_s1[key] = {
                    "filed_date": registration_filing.get("filing_date", ""),
                    "form": registration_filing.get("form", ""),
                    "source_url": registration_filing.get("url", ""),
                    "historical_context": research["historical_context"],
                    "what_to_learn": research["what_to_learn"],
                    "filing_details": research["filing_details"],
                    "generated_by": (
                        "local:"
                        + LOCAL_LLM_PROVIDER
                        + ":"
                        + model
                    ),
                    "generated_at_utc": datetime.now(
                        timezone.utc
                    ).isoformat(timespec="seconds"),
                }

            ticker_state.update({
                "status": "complete",
                "key": key,
                "cik": cik,
                "annual_accession": annual_filing.get(
                    "accession_number", ""
                ),
                "quarterly_accession": quarterly_filing.get(
                    "accession_number", ""
                ),
                "registration_accession": registration_filing.get(
                    "accession_number", ""
                ),
                "completed_utc": datetime.now(
                    timezone.utc
                ).isoformat(timespec="seconds"),
                "error": "",
            })

            print("  complete")

        except Exception as exc:
            ticker_state.update({
                "status": "error",
                "key": key,
                "error": str(exc)[:1000],
            })
            print(f"  ERROR: {exc}")

        state[ticker] = ticker_state

        # Persist after every company so a cancelled workflow loses almost no work.
        write_json(METRICS_PATH, generated_metrics)
        write_json(QUARTERLY_PATH, generated_quarterly)
        write_json(ANALYSIS_PATH, generated_analysis)
        write_json(S1_PATH, generated_s1)
        write_json(STATE_PATH, state)

    print(
        "Deep-research batch finished. "
        f"Generated analysis coverage: {len(generated_analysis)}/{len(universe)}."
    )


if __name__ == "__main__":
    main()
