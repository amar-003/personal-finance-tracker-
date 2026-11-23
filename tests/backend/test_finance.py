import unittest

import pandas as pd

from backend.src.finance import (
    analyze_spending,
    calculate_health_score,
    validate_transactions,
)
from ml.src.models.classifier import train_category_classifier
from ml.src.models.forecasting import forecast_daily_spend


class FinanceModelTests(unittest.TestCase):
    def test_category_classifier_trains_from_labeled_rows(self) -> None:
        training = pd.DataFrame(
            {
                "description": [
                    "fresh grocery market",
                    "weekly grocery shop",
                    "electric utility bill",
                    "monthly power bill",
                ],
                "amount": [40, 55, 80, 90],
                "category": ["Groceries", "Groceries", "Utilities", "Utilities"],
            }
        )

        model = train_category_classifier(training)
        prediction = model.predict(["grocery market"], [45])

        self.assertEqual(prediction[0]["category"], "Groceries")
        self.assertGreaterEqual(prediction[0]["confidence"], 0)
        self.assertLessEqual(prediction[0]["confidence"], 1)

    def test_classifier_requires_multiple_labeled_categories(self) -> None:
        training = pd.DataFrame(
            {"description": ["market", "shop"], "amount": [10, 20], "category": ["Food", "Food"]}
        )
        with self.assertRaisesRegex(ValueError, "two labeled categories"):
            train_category_classifier(training)

    def test_arima_forecast_returns_nonnegative_future_daily_values(self) -> None:
        dates = pd.date_range("2026-01-01", periods=35, freq="D")
        transactions = pd.DataFrame(
            {
                "transaction_date": dates,
                "amount": [20 + index % 4 for index in range(len(dates))],
            }
        )

        forecast = forecast_daily_spend(transactions, days=30)

        self.assertEqual(len(forecast), 30)
        self.assertEqual(forecast["date"].iloc[0], dates[-1] + pd.Timedelta(days=1))
        self.assertTrue((forecast["forecast"] >= 0).all())
        self.assertTrue((forecast["lower"] <= forecast["forecast"]).all())
        self.assertTrue((forecast["upper"] >= forecast["forecast"]).all())

    def test_spending_analysis_reports_month_and_category_totals(self) -> None:
        transactions = pd.DataFrame(
            {
                "transaction_date": ["2026-02-10", "2026-02-12", "2026-03-10"],
                "description": ["rent", "market", "rent"],
                "amount": [900.0, 200.0, 950.0],
                "category": ["Housing", "Groceries", "Housing"],
            }
        )

        result = analyze_spending(transactions)

        self.assertEqual(result["latest_month"], "2026-03")
        self.assertEqual(result["latest_month_spend"], 950.0)
        self.assertEqual(result["highest_category"], "Housing")
        self.assertEqual(len(result["monthly_totals"]), 2)

    def test_health_score_reports_risk_and_advisory(self) -> None:
        transactions = pd.DataFrame(
            {
                "transaction_date": ["2026-01-10", "2026-02-10", "2026-03-10"],
                "description": ["rent"] * 3,
                "amount": [900.0] * 3,
                "category": ["Rent"] * 3,
            }
        )

        result = calculate_health_score(
            transactions,
            monthly_income=3000,
            monthly_debt_payments=1500,
            savings_balance=500,
            discretionary_categories=["Entertainment"],
        )

        self.assertGreaterEqual(result["risk_score"], 0)
        self.assertLessEqual(result["health_score"], 100)
        self.assertTrue(result["advisory_notes"])
        self.assertIsNone(
            result["metrics"]["discretionary_spending_coefficient_of_variation"]
        )

    def test_import_rejects_invalid_dates(self) -> None:
        transactions = pd.DataFrame(
            {"transaction_date": ["not-a-date"], "description": ["shop"], "amount": [1]}
        )
        with self.assertRaisesRegex(ValueError, "valid dates"):
            validate_transactions(transactions)


if __name__ == "__main__":
    unittest.main()
