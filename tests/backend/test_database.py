import tempfile
import unittest
from pathlib import Path

import pandas as pd

from backend.src.database import (
    create_savings_goal,
    delete_budget,
    delete_savings_goal,
    get_budgets,
    get_savings_goals,
    get_transactions,
    replace_transactions,
    set_budget,
    update_savings_goal,
)


class TransactionDatabaseTests(unittest.TestCase):
    def test_import_can_replace_or_append_local_transactions(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            database = Path(temporary_directory) / "finance.db"
            first = pd.DataFrame(
                {
                    "transaction_date": [pd.Timestamp("2026-01-01")],
                    "description": ["Market"],
                    "amount": [25.0],
                    "category": ["Groceries"],
                }
            )
            second = pd.DataFrame(
                {
                    "transaction_date": [pd.Timestamp("2026-01-02")],
                    "description": ["Cafe"],
                    "amount": [7.0],
                    "category": [None],
                }
            )

            replace_transactions(first, database)
            replace_transactions(second, database, replace=False)

            rows = get_transactions(database)
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows["description"].tolist(), ["Market", "Cafe"])

            replace_transactions(second, database)
            self.assertEqual(len(get_transactions(database)), 1)

    def test_monthly_budgets_upsert_by_month_and_category(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            database = Path(temporary_directory) / "finance.db"

            first = set_budget("2026-11", "", 2000, database)
            updated = set_budget("2026-11", "", 2500, database)
            categorized = set_budget("2026-11", "Groceries", 500, database)

            self.assertEqual(first["id"], updated["id"])
            self.assertEqual(updated["amount"], 2500)
            self.assertEqual(len(get_budgets("2026-11", database)), 2)
            self.assertTrue(delete_budget(categorized["id"], database))
            self.assertEqual(len(get_budgets("2026-11", database)), 1)

    def test_savings_goals_create_update_and_delete(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            database = Path(temporary_directory) / "finance.db"
            goal = create_savings_goal(
                "Emergency fund", 5000, 750, "2027-12-31", database
            )

            updated = update_savings_goal(
                goal["id"], "Emergency fund", 6000, 1000, "2028-03-31", database
            )

            self.assertIsNotNone(updated)
            self.assertEqual(updated["target_amount"], 6000)
            self.assertEqual(get_savings_goals(database)[0]["current_amount"], 1000)
            self.assertTrue(delete_savings_goal(goal["id"], database))
            self.assertEqual(get_savings_goals(database), [])


if __name__ == "__main__":
    unittest.main()
