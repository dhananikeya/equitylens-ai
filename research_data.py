import re


def _ticker_from_key_or_record(key, record):
    """Resolve a ticker from a dataset record or a '(TICKER)' key suffix."""
    if isinstance(record, dict):
        ticker = str(record.get("ticker", "")).upper().strip()
        if ticker:
            return ticker

    match = re.search(r"\(([^()]+)\)\s*$", str(key))
    return match.group(1).upper().strip() if match else ""


def index_dataset_by_ticker(dataset):
    """Index any EquityLens JSON dataset by ticker, independent of company-name spelling."""
    indexed = {}
    for key, record in (dataset or {}).items():
        ticker = _ticker_from_key_or_record(key, record)
        if ticker:
            indexed[ticker] = record
    return indexed


