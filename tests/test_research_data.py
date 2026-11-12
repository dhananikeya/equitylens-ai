import unittest

from research_data import (
    index_dataset_by_ticker,
    merge_research_records,
)


class ResearchDataMergeTests(unittest.TestCase):
    def test_curated_values_override_generated_but_missing_fields_survive(self):
        generated = {
            "ticker": "TEST",
            "business_model": "Generated model",
            "capital_allocation": "Generated capital allocation",
            "nested": {
                "generated_only": "keep",
                "shared": "generated",
            },
        }
        curated = {
            "ticker": "TEST",
            "business_model": "Curated model",
            "capital_allocation": "",
            "nested": {
                "shared": "curated",
            },
        }

        merged = merge_research_records(
            generated,
            curated,
        )

        self.assertEqual(
            merged["business_model"],
            "Curated model",
        )
        self.assertEqual(
            merged["capital_allocation"],
            "Generated capital allocation",
        )
        self.assertEqual(
            merged["nested"]["generated_only"],
            "keep",
        )
        self.assertEqual(
            merged["nested"]["shared"],
            "curated",
        )

    def test_duplicate_ticker_records_merge_across_different_keys(self):
        dataset = {
            "Generated Example (TEST)": {
                "ticker": "TEST",
                "business_model": "Generated model",
                "debt_liquidity": "Generated liquidity context",
            },
            "Curated Example (TEST)": {
                "ticker": "TEST",
                "business_model": "Curated model",
                "debt_liquidity": "",
            },
        }

        indexed = index_dataset_by_ticker(
            dataset
        )

        self.assertEqual(
            indexed["TEST"]["business_model"],
            "Curated model",
        )
        self.assertEqual(
            indexed["TEST"]["debt_liquidity"],
            "Generated liquidity context",
        )


if __name__ == "__main__":
    unittest.main()
