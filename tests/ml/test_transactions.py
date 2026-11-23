import unittest

import numpy as np
import pandas as pd

from ml.src.data_processing.transactions import (
    fit_description_tfidf,
    preprocess_transactions,
    transform_description_tfidf,
)

class PreprocessTransactionsTests(unittest.TestCase):
    def test_temporal_features_and_prior_category_rolling_values(self) -> None:
        transactions = pd.DataFrame(
            {
                "transaction_date": ["2026-01-03", "2026-01-04", "2026-01-05"],
                "description": ["Cafe", "Market", "Lunch"],
                "amount": [10.0, 40.0, 20.0],
                "category": ["food", "travel", "food"],
            }
        )

        result = preprocess_transactions(transactions)

        self.assertEqual(result["day_of_week"].tolist(), [5, 6, 0])
        self.assertEqual(result["is_weekend"].tolist(), [True, True, False])
        self.assertTrue(np.isnan(result.loc[0, "rolling_mean_7d"]))
        self.assertEqual(result.loc[2, "rolling_mean_7d"], 10.0)
        self.assertEqual(result.loc[2, "rolling_spend_velocity_7d"], 10.0 / 7)

    def test_missing_category_leaves_rolling_features_unavailable(self) -> None:
        transactions = pd.DataFrame(
            {
                "transaction_date": ["2026-01-03"],
                "description": ["Cafe"],
                "amount": [10.0],
            }
        )

        result = preprocess_transactions(transactions)

        self.assertTrue(np.isnan(result.loc[0, "rolling_mean_7d"]))

    def test_tfidf_reuses_training_vocabulary_for_new_descriptions(self) -> None:
        vectorizer, training_matrix = fit_description_tfidf(
            ["coffee shop", "grocery market"]
        )
        new_matrix = transform_description_tfidf(
            vectorizer, ["coffee shop", "unseen merchant"]
        )

        self.assertEqual(training_matrix.shape[1], new_matrix.shape[1])
        self.assertEqual(training_matrix.shape[0], 2)
        self.assertEqual(new_matrix.shape[0], 2)

    def test_missing_required_column_is_reported(self) -> None:
        with self.assertRaisesRegex(ValueError, "transaction_date"):
            preprocess_transactions(pd.DataFrame({"description": ["Cafe"]}))


if __name__ == "__main__":
    unittest.main()
