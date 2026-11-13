import unittest

from financial_utils import (
    calc_growth,
    calc_margin,
)
from formatting import (
    format_money,
    format_utc_timestamp,
)
from methodology import (
    DATA_TREATMENT_RULES,
)


class FinancialMethodologyTests(unittest.TestCase):
    def test_growth_requires_nonzero_comparable_period(self):
        self.assertEqual(
            calc_growth(120, 100),
            20,
        )
        self.assertIsNone(
            calc_growth(120, 0)
        )
        self.assertIsNone(
            calc_growth(120, None)
        )

    def test_margin_requires_revenue(self):
        self.assertEqual(
            calc_margin(25, 100),
            25,
        )
        self.assertIsNone(
            calc_margin(25, 0)
        )
        self.assertIsNone(
            calc_margin(None, 100)
        )

    def test_missing_money_is_not_zero(self):
        self.assertEqual(
            format_money(None),
            "N/A",
        )
        self.assertNotEqual(
            format_money(None),
            "$0",
        )

    def test_reporting_currency_is_preserved(self):
        self.assertEqual(
            format_money(
                2_500_000,
                "EUR",
            ),
            "€2.5M",
        )
        self.assertEqual(
            format_money(
                2_500_000,
                "GBP",
            ),
            "£2.5M",
        )

    def test_timestamp_normalizes_to_utc_without_pandas(self):
        self.assertEqual(
            format_utc_timestamp(
                "2026-11-13T01:30:00-05:00"
            ),
            "2026-11-13 06:30 UTC",
        )

    def test_methodology_explicitly_forbids_fx_comparison(self):
        self.assertTrue(
            any(
                "does not perform FX conversion"
                in rule
                for rule
                in DATA_TREATMENT_RULES
            )
        )


if __name__ == "__main__":
    unittest.main()
