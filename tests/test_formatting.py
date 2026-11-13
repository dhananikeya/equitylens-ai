import unittest

from formatting import format_money


class CurrencyFormattingTests(unittest.TestCase):
    def test_usd_remains_default(self):
        self.assertEqual(
            format_money(
                1_000_000
            ),
            "$1.0M",
        )

    def test_eur_uses_euro_symbol(self):
        self.assertEqual(
            format_money(
                1_000_000,
                "EUR",
            ),
            "€1.0M",
        )

    def test_gbp_uses_pound_symbol(self):
        self.assertEqual(
            format_money(
                -2_000_000,
                "GBP",
            ),
            "-£2.0M",
        )

    def test_unknown_currency_is_labeled_not_converted(self):
        self.assertEqual(
            format_money(
                1_500,
                "SEK",
            ),
            "SEK 1,500",
        )


if __name__ == "__main__":
    unittest.main()
