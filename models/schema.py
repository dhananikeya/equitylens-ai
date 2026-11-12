from typing import NotRequired, TypedDict


class QuoteSnapshot(TypedDict, total=False):
    symbol: str
    close: float
    open: float
    previous_close: float
    percent_change: float
    quote_session: str
    retrieved_at: str
    volume: float


class FilingSummary(TypedDict, total=False):
    form: str
    filing_date: str
    report_date: str
    description: str
    url: str


class CompanySecSummary(TypedDict, total=False):
    ticker: str
    cik: str
    entity_name: str
    has_filings: bool
    has_material_filings: bool
    filing_count: int
    material_filing_count: int
    latest_filing: FilingSummary
    latest_material_filing: FilingSummary
    sec_status: str
    last_checked_utc: str
