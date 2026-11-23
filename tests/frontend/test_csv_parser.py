import unittest

import pandas as pd

from frontend.csv_parser import (
    assign_basic_categories,
    normalize_transaction_columns,
)


class CsvParserTests(unittest.TestCase):
    def test_maps_common_headers_and_ignores_unrelated_columns(self) -> None:
        transactions = pd.DataFrame(
            {
                "Posted Date": ["2026-01-03"],
                "Merchant Name": ["Cafe"],
                "Debit Amount": [10.0],
                "Expense Category": ["Food"],
                "Account": ["Checking"],
            }
        )

        result = normalize_transaction_columns(transactions)

        self.assertEqual(
            result.iloc[0].to_dict(),
            {
                "transaction_date": "2026-01-03",
                "description": "Cafe",
                "amount": 10.0,
                "category": "Food",
            },
        )

    def test_category_is_optional(self) -> None:
        transactions = pd.DataFrame(
            {"DATE": ["2026-01-03"], "Payee": ["Cafe"], "Amount": [10.0]}
        )

        result = normalize_transaction_columns(transactions)

        self.assertEqual(result.loc[0, "category"], "Dining")

    def test_detects_variant_headers_and_assigns_missing_categories(self) -> None:
        transactions = pd.DataFrame(
            {
                "Effective Date": ["2026-02-01"],
                "Merchant / Payee": ["Neighborhood supermarket"],
                "Net Debit": [42.25],
                "Expense Classification": [None],
            }
        )

        result = normalize_transaction_columns(transactions)

        self.assertEqual(result.loc[0, "transaction_date"], "2026-02-01")
        self.assertEqual(result.loc[0, "description"], "Neighborhood supermarket")
        self.assertEqual(result.loc[0, "amount"], 42.25)
        self.assertEqual(result.loc[0, "category"], "Groceries")

    def test_maps_more_common_header_variations(self) -> None:
        transactions = pd.DataFrame(
            {
                "Purchase Date": ["2026-03-01"],
                "Vendor Name": ["City bus operator"],
                "Net Amount": [18.50],
                "Transaction Type": [None],
            }
        )

        result = normalize_transaction_columns(transactions)

        self.assertEqual(result.loc[0, "transaction_date"], "2026-03-01")
        self.assertEqual(result.loc[0, "description"], "City bus operator")
        self.assertEqual(result.loc[0, "amount"], 18.50)
        self.assertEqual(result.loc[0, "category"], "Transport")

    def test_maps_transaction_specific_headers(self) -> None:
        transactions = pd.DataFrame(
            {
                "Transaction Date and Time": ["2026-04-04"],
                "Transaction Name": ["Monthly apartment rent"],
                "Withdrawal Amount": [875.0],
                "Transaction Category": ["Housing"],
            }
        )

        result = normalize_transaction_columns(transactions)

        self.assertEqual(result.loc[0, "transaction_date"], "2026-04-04")
        self.assertEqual(result.loc[0, "description"], "Monthly apartment rent")
        self.assertEqual(result.loc[0, "amount"], 875.0)
        self.assertEqual(result.loc[0, "category"], "Housing")

    def test_maps_bank_export_money_out_amount_header(self) -> None:
        transactions = pd.DataFrame(
            {
                "Transaction Date": ["2026-04-12"],
                "Payee": ["Coffee shop"],
                "Money Out": ["6.75"],
            }
        )

        result = normalize_transaction_columns(transactions)

        self.assertEqual(result.loc[0, "amount"], "6.75")
        self.assertEqual(result.loc[0, "category"], "Dining")

    def test_prefers_explicit_category_over_generic_type_column(self) -> None:
        transactions = pd.DataFrame(
            {
                "Date": ["2026-05-01", "2026-05-02"],
                "Merchant": ["Coffee shop", "Unlisted service"],
                "Amount": [4.5, None],
                "Debit": [99.0, 7.25],
                "Category": ["Dining", None],
                "Type": ["Debit", "Credit"],
            }
        )

        result = normalize_transaction_columns(transactions)

        self.assertEqual(result.loc[0, "category"], "Dining")
        self.assertEqual(result.loc[1, "category"], "Other")
        self.assertEqual(result.loc[0, "amount"], 4.5)
        self.assertEqual(result.loc[1, "amount"], 7.25)

    def test_auto_category_assignment_preserves_existing_categories(self) -> None:
        transactions = pd.DataFrame(
            {
                "description": ["Monthly apartment rent", "Coffee shop", "Unknown service"],
                "category": ["Custom Housing", None, ""],
            }
        )

        result = assign_basic_categories(transactions)

        self.assertEqual(result.loc[0, "category"], "Custom Housing")
        self.assertEqual(result.loc[1, "category"], "Dining")
        self.assertEqual(result.loc[2, "category"], "Other")

    def test_reports_missing_required_fields(self) -> None:
        with self.assertRaisesRegex(ValueError, "amount"):
            normalize_transaction_columns(
                pd.DataFrame({"Date": ["2026-01-03"], "Payee": ["Cafe"]})
            )


if __name__ == "__main__":
    unittest.main()
