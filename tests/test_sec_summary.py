import importlib.util
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "update_sec_filings.py"
SPEC = importlib.util.spec_from_file_location("update_sec_filings", MODULE_PATH)
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


def test_build_summary_prefers_material_filings_and_counts():
    output = {
        "Example Corp (EXM)": {
            "ticker": "EXM",
            "cik": "0000000001",
            "entity_name": "Example Corp",
            "sec_status": "available",
            "last_checked_utc": "2026-11-12T00:00:00+00:00",
            "registration_filings": [],
            "registration_scan_complete": True,
            "filings": [
                {
                    "form": "4",
                    "filing_date": "2026-11-12",
                    "report_date": "2026-11-11",
                    "description": "Insider transaction",
                    "url": "https://example.com/form4",
                },
                {
                    "form": "10-Q",
                    "filing_date": "2026-11-10",
                    "report_date": "2026-09-30",
                    "description": "Quarterly report",
                    "url": "https://example.com/10q",
                },
                {
                    "form": "8-K",
                    "filing_date": "2026-11-08",
                    "report_date": "2026-11-08",
                    "description": "Current report",
                    "url": "https://example.com/8k",
                },
            ],
        }
    }

    summary = module.build_summary(output, "2026-11-12T01:00:00+00:00")
    company = summary["companies"]["EXM"]

    assert company["latest_filing"]["form"] == "4"
    assert company["latest_material_filing"]["form"] == "10-Q"
    assert company["filing_count"] == 3
    assert company["material_filing_count"] == 2
    assert company["material_form_counts"] == {"10-Q": 1, "8-K": 1}
    assert summary["indexed_filing_count"] == 3
    assert summary["indexed_material_filing_count"] == 2
    assert summary["companies_with_material_filings"] == 1
    assert summary["recent_filings"][0]["form"] == "10-Q"
