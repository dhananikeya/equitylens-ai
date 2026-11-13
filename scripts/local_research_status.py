"""Report local qualitative-research progress without calling an LLM."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def read_json(name: str) -> dict:
    path = DATA / name
    if not path.exists():
        return {}
    payload = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )
    return (
        payload
        if isinstance(payload, dict)
        else {}
    )


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

    if "(" in key and key.endswith(")"):
        return (
            key.rsplit("(", 1)[1][:-1]
            .upper()
            .strip()
        )
    return ""


def ticker_set(payload: dict) -> set[str]:
    output = set()
    for key, record in payload.items():
        if not isinstance(
            record,
            dict,
        ):
            continue
        ticker = ticker_from_record(
            key,
            record,
        )
        if ticker:
            output.add(ticker)
    return output


def main() -> None:
    with (
        DATA
        / "finviz_universe.csv"
    ).open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as handle:
        universe = list(
            csv.DictReader(handle)
        )

    generated_analysis = read_json(
        "generated_company_analysis.json"
    )
    generated_s1 = read_json(
        "generated_company_s1.json"
    )
    hand_analysis = read_json(
        "company_analysis.json"
    )
    coverage = read_json(
        "research_coverage.json"
    )
    state = read_json(
        "research_pipeline_state.json"
    )

    generated_tickers = ticker_set(
        generated_analysis
    )
    hand_tickers = ticker_set(
        hand_analysis
    )
    registration_tickers = ticker_set(
        generated_s1
    )

    complete_states = sum(
        1
        for value in state.values()
        if (
            isinstance(value, dict)
            and value.get("status")
            == "complete"
        )
    )
    error_states = sum(
        1
        for value in state.values()
        if (
            isinstance(value, dict)
            and value.get("status")
            == "error"
        )
    )

    total = len(universe)
    qualitative_union = (
        generated_tickers
        | hand_tickers
    )

    print(
        f"Universe: {total}"
    )
    print(
        "Generated qualitative records: "
        f"{len(generated_tickers)}"
    )
    print(
        "Curated qualitative records: "
        f"{len(hand_tickers)}"
    )
    print(
        "Total qualitative ticker coverage: "
        f"{len(qualitative_union)}"
    )
    print(
        "Generated registration records: "
        f"{len(registration_tickers)}"
    )
    print(
        "Worker states: "
        f"{complete_states} complete, "
        f"{error_states} errors"
    )

    totals = coverage.get(
        "totals",
        {},
    )
    if totals:
        print(
            "Coverage index: "
            f"{totals.get('annual_financials', 0)} annual, "
            f"{totals.get('quarterly_financials', 0)} quarterly, "
            f"{totals.get('qualitative_analysis', 0)} qualitative, "
            f"{totals.get('deep_research', 0)} deep"
        )

    remaining = [
        str(
            row.get(
                "Ticker",
                "",
            )
        ).upper().strip()
        for row in universe
        if str(
            row.get(
                "Ticker",
                "",
            )
        ).upper().strip()
        not in generated_tickers
    ]
    print(
        "Next ungenerated tickers: "
        + ", ".join(
            remaining[:20]
        )
    )


if __name__ == "__main__":
    main()
