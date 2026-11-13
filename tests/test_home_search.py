import unittest

import pandas as pd

from home_search import (
    normalize_search_text,
    rank_company_matches,
)


class HomeSearchTests(unittest.TestCase):
    def setUp(self):
        self.universe = pd.DataFrame([
            {
                "Ticker": "AAPL",
                "Company": "Apple Inc",
                "Industry": "Consumer Electronics",
            },
            {
                "Ticker": "GOOGL",
                "Company": "Alphabet Inc",
                "Industry": "Internet Content & Information",
            },
            {
                "Ticker": "MSFT",
                "Company": "Microsoft Corp",
                "Industry": "Software - Infrastructure",
            },
        ])
        self.coverage = {
            "companies": {
                "AAPL": {
                    "completion_status": "Structured research available",
                    "completeness_percent": 80,
                },
                "GOOGL": {
                    "completion_status": "Financial research available",
                    "completeness_percent": 65,
                },
            }
        }

    def test_normalization_removes_corporate_suffixes(self):
        self.assertEqual(
            normalize_search_text("Apple, Inc."),
            "apple",
        )

    def test_exact_ticker_ranks_first(self):
        matches = rank_company_matches(
            self.universe,
            "AAPL",
            self.coverage,
        )
        self.assertEqual(
            matches[0]["ticker"],
            "AAPL",
        )

    def test_alias_finds_alphabet_from_google(self):
        matches = rank_company_matches(
            self.universe,
            "Google",
            self.coverage,
        )
        self.assertEqual(
            matches[0]["ticker"],
            "GOOGL",
        )

    def test_close_misspelling_finds_company(self):
        matches = rank_company_matches(
            self.universe,
            "aple",
            self.coverage,
        )
        self.assertEqual(
            matches[0]["ticker"],
            "AAPL",
        )

    def test_search_result_includes_research_status(self):
        match = rank_company_matches(
            self.universe,
            "Apple",
            self.coverage,
        )[0]
        self.assertEqual(
            match["status"],
            "Structured research available",
        )
        self.assertEqual(
            match["completeness"],
            80,
        )


if __name__ == "__main__":
    unittest.main()
