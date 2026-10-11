"""Regression checks for native mobile tables and provider-neutral UI."""
import unittest
from pathlib import Path

from market_tables import _safe_link, table_markup


class FakeTable:
    columns = ["Ticker", "Company", "Source"]

    def itertuples(self, index=False, name=None):
        assert index is False and name is None
        return iter([
            ("ACME", "<b>Example</b>", "https://www.federalreserve.gov/example"),
            ("TEST", "Test & Co.", "javascript:alert(1)"),
        ])


class MarketTableTests(unittest.TestCase):
    def test_table_uses_real_text_and_escapes_user_data(self):
        html = table_markup(FakeTable(), link_columns=("Source",))
        self.assertIn("ACME", html)
        self.assertIn("data-label=", html)
        self.assertIn("&lt;b&gt;Example&lt;/b&gt;", html)
        self.assertIn("Test &amp; Co.", html)
        self.assertNotIn("<b>Example</b>", html)
        self.assertNotIn('href="javascript:', html)

    def test_links_are_validated(self):
        self.assertEqual(_safe_link("javascript:alert(1)"), "")
        self.assertEqual(_safe_link("https://evil.example/"), "https://evil.example/")
        self.assertEqual(_safe_link("//example.com/path"), "")

    def test_empty_table_has_message(self):
        class EmptyTable:
            columns = ["Ticker"]
            def itertuples(self, index=False, name=None):
                return iter([])
        self.assertIn("No table entries available", table_markup(EmptyTable()))

    def test_market_monitor_retains_features_without_provider_brand_text(self):
        app = Path("app.py").read_text(encoding="utf-8")
        self.assertIn('section("Screener", "Market Intelligence")', app)
        self.assertIn("render_crisp_table(st, covered_finviz[visible_columns])", app)
        self.assertIn("render_crisp_table(", app)
        self.assertIn("get_rates_bundle(", app)
        self.assertIn("ThreadPoolExecutor(max_workers=3)", app)
        self.assertIn("section(\"Rates\", \"Treasury, SOFR & Swap Monitor\")", app)
        self.assertNotIn("Finviz Market Intelligence", app)
        self.assertNotIn("Finviz supplies the screener", app)
        self.assertNotIn("Finviz Elite · market timing", app)


if __name__ == "__main__":
    unittest.main()
