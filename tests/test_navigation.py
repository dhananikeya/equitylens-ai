import unittest
from pathlib import Path

import pandas as pd

from navigation import (
    format_global_search_option,
    global_search_options,
)


class NavigationSearchTests(unittest.TestCase):
    def setUp(self):
        self.lookup = {
            "ticker::AAPL": {
                "ticker": "AAPL",
                "company": "Apple Inc",
                "industry": "Consumer Electronics",
            }
        }

    def test_global_search_indexes_company_filing_and_learn_content(self):
        options = global_search_options(
            self.lookup
        )
        self.assertIn(
            "ticker::AAPL",
            options,
        )
        self.assertIn(
            "filing::10-K",
            options,
        )
        self.assertIn(
            "learn::Revenue",
            options,
        )

    def test_global_search_labels_are_descriptive(self):
        self.assertIn(
            "Consumer Electronics",
            format_global_search_option(
                "ticker::AAPL",
                self.lookup,
            ),
        )
        self.assertEqual(
            format_global_search_option(
                "filing::10-Q",
                self.lookup,
            ),
            "SEC filing · 10-Q",
        )
        self.assertEqual(
            format_global_search_option(
                "learn::SOFR",
                self.lookup,
            ),
            "Learn · SOFR",
        )

    def test_mobile_sticky_navigation_has_compact_overflow_rules(self):
        css = Path(
            "assets/equitylens.css"
        ).read_text(
            encoding="utf-8"
        )
        self.assertIn(
            ".st-key-top_command_bar",
            css,
        )
        self.assertIn(
            "position: sticky",
            css,
        )
        self.assertIn(
            "overflow-x: auto",
            css,
        )
        self.assertIn(
            "label:has(input:checked)",
            css,
        )


if __name__ == "__main__":
    unittest.main()
