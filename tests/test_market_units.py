import unittest

from market_units import (
    market_cap_dollars,
)


class MarketUnitTests(unittest.TestCase):
    def test_plain_finviz_market_cap_is_millions(self):
        self.assertEqual(
            market_cap_dollars(
                4585200
            ),
            4_585_200_000_000,
        )

    def test_billion_suffix_is_literal_dollars(self):
        self.assertEqual(
            market_cap_dollars(
                "150B"
            ),
            150_000_000_000,
        )

    def test_trillion_suffix_is_literal_dollars(self):
        self.assertEqual(
            market_cap_dollars(
                "4.5T"
            ),
            4_500_000_000_000,
        )

    def test_missing_market_cap_remains_missing(self):
        self.assertIsNone(
            market_cap_dollars(
                "N/A"
            )
        )


if __name__ == "__main__":
    unittest.main()
