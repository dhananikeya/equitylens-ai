import json
import unittest
from pathlib import Path


class UniverseMetadataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(
            Path(
                "data/company_universe_metadata.json"
            ).read_text(
                encoding="utf-8"
            )
        )

    def test_active_universe_has_metadata_for_all_companies(self):
        self.assertEqual(
            len(
                self.payload.get(
                    "companies",
                    {},
                )
            ),
            517,
        )

    def test_reporting_regime_distinguishes_20f_reporters(self):
        companies = self.payload[
            "companies"
        ]
        self.assertEqual(
            companies["ASML"][
                "reporting_regime"
            ],
            "20-F foreign private issuer",
        )
        self.assertEqual(
            companies["AAPL"][
                "reporting_regime"
            ],
            "10-K domestic reporting",
        )

    def test_unknown_metadata_is_not_fabricated(self):
        apple = self.payload[
            "companies"
        ]["AAPL"]
        self.assertIsNone(
            apple["ipo_year"]
        )
        self.assertIsNone(
            apple["exchange"]
        )
        self.assertEqual(
            apple[
                "index_memberships"
            ],
            [],
        )


if __name__ == "__main__":
    unittest.main()
