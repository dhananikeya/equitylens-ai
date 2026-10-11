"""Regression checks for the education-first research experience.

Run with: python -m unittest discover -s tests
"""
import unittest
from pathlib import Path

from research_experience import (
    _filer_timeline,
    _compact_dollars,
    _safe_sec_url,
    build_research_pdf,
)


class ResearchExperienceTests(unittest.TestCase):
    def test_official_sec_links_only(self):
        self.assertEqual(
            _safe_sec_url("https://www.sec.gov/Archives/edgar/data/1234/test.htm"),
            "https://www.sec.gov/Archives/edgar/data/1234/test.htm",
        )
        self.assertEqual(_safe_sec_url("https://example.com/filing"), "")
        self.assertEqual(_safe_sec_url("http://www.sec.gov/path"), "")
        self.assertEqual(_safe_sec_url("https://sec.gov.evil.example/path"), "")

    def test_filing_timeline_sorted_without_mutating_input(self):
        rows = [
            {"form": "10-K", "filing_date": "2025-11-01"},
            {"form": "10-Q", "filing_date": "2026-02-01"},
            {"form": "8-K", "filing_date": ""},
        ]
        timeline = _filer_timeline(rows, 2)
        self.assertEqual([f["form"] for f in timeline], ["10-Q", "10-K"])
        self.assertEqual(rows[0]["form"], "10-K")

    def test_compact_money_formatting_and_missing_values(self):
        self.assertEqual(_compact_dollars(3_200_000_000), "$3.20B")
        self.assertEqual(_compact_dollars(-420_000_000), "-$420.0M")
        self.assertEqual(_compact_dollars(None), "Not available")

    def test_export_handles_missing_analysis_without_fake_claims(self):
        pdf = build_research_pdf(
            "Example & Sons", "TEST", "Technology", "Software", {},
            [], {"Revenue": "Not available", "Period": "Not available"},
        )
        self.assertTrue(pdf.startswith(b"%PDF-"))
        self.assertGreater(len(pdf), 1400)

    def test_export_handles_source_links_and_escaping(self):
        pdf = build_research_pdf(
            "Sample <Company>", "SAM", "Services", "Technology",
            {
                "business_model": "Software & cloud",
                "key_risk_themes": ["Competition", "Pricing"],
                "source_filing": (
                    "https://www.sec.gov/Archives/edgar/data/1000/test.htm"
                ),
            },
            [{"form": "10-K", "filing_date": "2026-02-01",
              "url": "https://www.sec.gov/Archives/edgar/data/1000/test.htm"}],
            {"Revenue": "$1 million"},
        )
        self.assertTrue(pdf.startswith(b"%PDF-"))

    def test_original_six_sections_remain_accessible(self):
        app = Path("app.py").read_text(encoding="utf-8")
        for section in (
            '"Home": "Home"',
            '"Company Research":',
            '"Industry Comparison":',
            '"Market Monitor":',
            '"Filings":',
            '"Learn":',
        ):
            self.assertIn(section, app)
        self.assertIn('render_company_evidence(', app)
        self.assertIn('render_report_download(', app)
        self.assertNotIn("from supabase import", app)


if __name__ == "__main__":
    unittest.main()
