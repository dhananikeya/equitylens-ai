"""Offline regression tests for SEC annual metrics normalization.

Run: python -m unittest discover -s tests -p 'test_companyfacts_metrics.py'
"""
import importlib.util
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "scripts" / "update_companyfacts_metrics.py"
spec = importlib.util.spec_from_file_location("update_companyfacts_metrics", MODULE)
pipeline = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pipeline)


def item(start, end, val, form="10-K", accn="0000000000-26-000001"):
    row = {"end": end, "val": val, "form": form,
           "filed": "2026-04-01", "accn": accn}
    if start:
        row["start"] = start
    return row


class CompanyFactsTests(unittest.TestCase):
    def facts(self):
        return {"facts": {"us-gaap": {
            "RevenueFromContractWithCustomerExcludingAssessedTax": {"units": {"USD": [
                item("2025-01-01", "2025-12-31", 1000),
                item("2025-10-01", "2025-12-31", 300),  # quarterly exclusion
                item("2024-01-01", "2024-12-31", 900),
            ]}},
            "NetIncomeLoss": {"units": {"USD": [
                item("2025-01-01", "2025-12-31", -50),
            ]}},
            "Assets": {"units": {"USD": [
                item(None, "2025-12-31", 1500),
            ]}},
        }}}

    def test_annual_only(self):
        facts = self.facts()
        rows = pipeline.annual_records(facts, "revenue")
        self.assertEqual(len(rows), 2)
        self.assertEqual({r["val"] for r in rows}, {900, 1000})

    def test_structured_record_and_history(self):
        rec = pipeline.build_record("TEST",
            {"cik": "0000123456", "industry": "Example"}, self.facts())
        self.assertEqual(rec["revenue"], 1000)
        self.assertEqual(rec["net_income"], -50)
        self.assertEqual(rec["assets"], 1500)
        self.assertNotIn("cash", rec)
        self.assertEqual(rec["fiscal_year_end"], "2025-12-31")
        self.assertEqual(len(rec["history"]), 2)
        self.assertIn("/123456/", rec["filing_url"])

    def test_no_annual_facts_returns_none(self):
        self.assertIsNone(pipeline.build_record("T",
            {"cik": "123", "industry": ""}, {"facts": {}}))

    def test_exclude_non_annual_forms(self):
        facts = self.facts()
        rows = facts["facts"]["us-gaap"]["RevenueFromContractWithCustomerExcludingAssessedTax"]["units"]["USD"]
        rows.append(item("2025-01-01", "2025-12-31", 99999, "10-Q"))
        self.assertEqual(pipeline.build_record("TEST",
            {"cik": "123", "industry": ""}, facts)["revenue"], 1000)


if __name__ == "__main__":
    unittest.main()
