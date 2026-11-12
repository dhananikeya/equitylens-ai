import re


def _ticker_from_key_or_record(key, record):
    """Resolve a ticker from a dataset record or a '(TICKER)' key suffix."""
    if isinstance(record, dict):
        ticker = str(
            record.get("ticker", "")
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


def _has_value(value):
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(
        value,
        (list, tuple, set, dict),
    ):
        return bool(value)
    return True


def merge_research_records(
    base,
    override,
):
    """Merge research records while preserving authoritative non-empty overrides.

    Generated data can fill gaps in a curated record, but a populated curated
    value remains authoritative. Nested dictionaries are merged recursively.
    """
    if not isinstance(base, dict):
        base = {}
    if not isinstance(override, dict):
        return dict(base)

    merged = dict(base)
    for key, value in override.items():
        existing = merged.get(key)

        if (
            isinstance(existing, dict)
            and isinstance(value, dict)
        ):
            merged[key] = (
                merge_research_records(
                    existing,
                    value,
                )
            )
        elif _has_value(value):
            merged[key] = value
        elif key not in merged:
            merged[key] = value

    return merged


def index_dataset_by_ticker(dataset):
    """Index an EquityLens dataset by ticker and fill gaps across duplicate records."""
    indexed = {}
    for key, record in (
        dataset or {}
    ).items():
        ticker = (
            _ticker_from_key_or_record(
                key,
                record,
            )
        )
        if not ticker:
            continue

        if ticker in indexed:
            indexed[ticker] = (
                merge_research_records(
                    indexed[ticker],
                    record,
                )
            )
        else:
            indexed[ticker] = (
                dict(record)
                if isinstance(record, dict)
                else record
            )

    return indexed
