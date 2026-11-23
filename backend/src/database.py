"""Small SQLite persistence layer for locally stored transactions."""

from __future__ import annotations

import sqlite3
from contextlib import closing
from pathlib import Path

import pandas as pd

DEFAULT_DATABASE = Path(__file__).resolve().parents[2] / "database" / "finance.db"


def _connect(database_path: str | Path = DEFAULT_DATABASE) -> sqlite3.Connection:
    path = Path(database_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database(database_path: str | Path = DEFAULT_DATABASE) -> None:
    with closing(_connect(database_path)) as connection, connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY,
                transaction_date TEXT NOT NULL,
                description TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY,
                month TEXT NOT NULL,
                category TEXT NOT NULL DEFAULT '',
                amount REAL NOT NULL CHECK (amount > 0),
                UNIQUE (month, category)
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS savings_goals (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                target_amount REAL NOT NULL CHECK (target_amount > 0),
                current_amount REAL NOT NULL DEFAULT 0 CHECK (current_amount >= 0),
                target_date TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def replace_transactions(
    transactions: pd.DataFrame,
    database_path: str | Path = DEFAULT_DATABASE,
    replace: bool = True,
) -> int:
    """Persist transactions atomically and return the imported row count."""
    initialize_database(database_path)
    records = [
        (
            row.transaction_date.date().isoformat(),
            row.description,
            float(row.amount),
            row.category if pd.notna(row.category) and row.category else None,
        )
        for row in transactions.itertuples(index=False)
    ]
    with closing(_connect(database_path)) as connection, connection:
        if replace:
            connection.execute("DELETE FROM transactions")
        connection.executemany(
            """
            INSERT INTO transactions (transaction_date, description, amount, category)
            VALUES (?, ?, ?, ?)
            """,
            records,
        )
    return len(records)


def get_transactions(database_path: str | Path = DEFAULT_DATABASE) -> pd.DataFrame:
    initialize_database(database_path)
    with closing(_connect(database_path)) as connection, connection:
        rows = connection.execute(
            """
            SELECT transaction_date, description, amount, category
            FROM transactions
            ORDER BY transaction_date, id
            """
        ).fetchall()
    return pd.DataFrame(
        [dict(row) for row in rows],
        columns=["transaction_date", "description", "amount", "category"],
    )


def get_budgets(
    month: str, database_path: str | Path = DEFAULT_DATABASE
) -> list[dict[str, object]]:
    initialize_database(database_path)
    with closing(_connect(database_path)) as connection, connection:
        rows = connection.execute(
            """
            SELECT id, month, category, amount
            FROM budgets
            WHERE month = ?
            ORDER BY category, id
            """,
            (month,),
        ).fetchall()
    return [dict(row) for row in rows]


def set_budget(
    month: str,
    category: str,
    amount: float,
    database_path: str | Path = DEFAULT_DATABASE,
) -> dict[str, object]:
    initialize_database(database_path)
    with closing(_connect(database_path)) as connection, connection:
        connection.execute(
            """
            INSERT INTO budgets (month, category, amount)
            VALUES (?, ?, ?)
            ON CONFLICT (month, category)
            DO UPDATE SET amount = excluded.amount
            """,
            (month, category, amount),
        )
        row = connection.execute(
            """
            SELECT id, month, category, amount
            FROM budgets
            WHERE month = ? AND category = ?
            """,
            (month, category),
        ).fetchone()
    return dict(row)


def delete_budget(budget_id: int, database_path: str | Path = DEFAULT_DATABASE) -> bool:
    initialize_database(database_path)
    with closing(_connect(database_path)) as connection, connection:
        cursor = connection.execute("DELETE FROM budgets WHERE id = ?", (budget_id,))
    return cursor.rowcount > 0


def get_savings_goals(
    database_path: str | Path = DEFAULT_DATABASE,
) -> list[dict[str, object]]:
    initialize_database(database_path)
    with closing(_connect(database_path)) as connection, connection:
        rows = connection.execute(
            """
            SELECT id, name, target_amount, current_amount, target_date
            FROM savings_goals
            ORDER BY target_date, id
            """
        ).fetchall()
    return [dict(row) for row in rows]


def create_savings_goal(
    name: str,
    target_amount: float,
    current_amount: float,
    target_date: str,
    database_path: str | Path = DEFAULT_DATABASE,
) -> dict[str, object]:
    initialize_database(database_path)
    with closing(_connect(database_path)) as connection, connection:
        cursor = connection.execute(
            """
            INSERT INTO savings_goals
                (name, target_amount, current_amount, target_date)
            VALUES (?, ?, ?, ?)
            """,
            (name, target_amount, current_amount, target_date),
        )
        row = connection.execute(
            """
            SELECT id, name, target_amount, current_amount, target_date
            FROM savings_goals
            WHERE id = ?
            """,
            (cursor.lastrowid,),
        ).fetchone()
    return dict(row)


def update_savings_goal(
    goal_id: int,
    name: str,
    target_amount: float,
    current_amount: float,
    target_date: str,
    database_path: str | Path = DEFAULT_DATABASE,
) -> dict[str, object] | None:
    initialize_database(database_path)
    with closing(_connect(database_path)) as connection, connection:
        cursor = connection.execute(
            """
            UPDATE savings_goals
            SET name = ?, target_amount = ?, current_amount = ?, target_date = ?
            WHERE id = ?
            """,
            (name, target_amount, current_amount, target_date, goal_id),
        )
        if cursor.rowcount == 0:
            return None
        row = connection.execute(
            """
            SELECT id, name, target_amount, current_amount, target_date
            FROM savings_goals
            WHERE id = ?
            """,
            (goal_id,),
        ).fetchone()
    return dict(row)


def delete_savings_goal(
    goal_id: int, database_path: str | Path = DEFAULT_DATABASE
) -> bool:
    initialize_database(database_path)
    with closing(_connect(database_path)) as connection, connection:
        cursor = connection.execute(
            "DELETE FROM savings_goals WHERE id = ?", (goal_id,)
        )
    return cursor.rowcount > 0
