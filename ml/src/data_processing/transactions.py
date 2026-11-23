"""Preprocessing and feature engineering for transaction records."""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer

_REQUIRED_COLUMNS = {"transaction_date", "description", "amount"}
_ROLLING_WINDOWS = (7, 30, 90)


def preprocess_transactions(transactions: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with normalized inputs and temporal/rolling features.

    Required columns are ``transaction_date``, ``description``, and ``amount``.
    If ``category`` is present, rolling statistics are computed per category.
    Rolling values only use transactions strictly earlier than the current
    transaction, so the current amount is not included in its own features.
    """
    missing_columns = _REQUIRED_COLUMNS.difference(transactions.columns)
    if missing_columns:
        raise ValueError(
            "Missing required transaction columns: "
            + ", ".join(sorted(missing_columns))
        )

    result = transactions.copy().reset_index(drop=True)
    result["transaction_date"] = pd.to_datetime(
        result["transaction_date"], errors="coerce"
    )
    if result["transaction_date"].isna().any():
        raise ValueError("'transaction_date' must contain valid dates.")

    result["description"] = result["description"].fillna("").astype(str).str.strip()
    result["amount"] = pd.to_numeric(result["amount"], errors="coerce")
    amounts = result["amount"].to_numpy(dtype=float, na_value=np.nan)
    if not np.isfinite(amounts).all():
        raise ValueError("'amount' must contain finite numeric values.")

    dates = result["transaction_date"]
    result["day_of_week"] = dates.dt.day_of_week
    result["is_weekend"] = dates.dt.day_of_week >= 5
    result["day_of_month"] = dates.dt.day
    weekday_angle = 2 * np.pi * dates.dt.day_of_week / 7
    monthday_angle = 2 * np.pi * (dates.dt.day - 1) / dates.dt.days_in_month
    result["day_of_week_sin"] = np.sin(weekday_angle)
    result["day_of_week_cos"] = np.cos(weekday_angle)
    result["day_of_month_sin"] = np.sin(monthday_angle)
    result["day_of_month_cos"] = np.cos(monthday_angle)

    rolling_columns = [
        f"rolling_{stat}_{days}d"
        for days in _ROLLING_WINDOWS
        for stat in ("mean", "std", "spend_velocity")
    ]
    for column in rolling_columns:
        result[column] = np.nan

    if "category" not in result.columns:
        return result

    category_groups: Iterable[np.ndarray] = result.groupby(
        "category", dropna=False, sort=False
    ).indices.values()
    for row_indices in category_groups:
        group = result.iloc[row_indices].sort_values(
            "transaction_date", kind="mergesort"
        )
        spend = pd.Series(
            np.abs(group["amount"].to_numpy(dtype=float, na_value=np.nan)),
            index=pd.DatetimeIndex(group["transaction_date"]),
        )
        for days in _ROLLING_WINDOWS:
            rolling = spend.rolling(f"{days}D", closed="left", min_periods=1)
            result.loc[group.index, f"rolling_mean_{days}d"] = (
                rolling.mean().to_numpy()
            )
            result.loc[group.index, f"rolling_std_{days}d"] = (
                rolling.std().to_numpy()
            )
            result.loc[group.index, f"rolling_spend_velocity_{days}d"] = (
                rolling.sum().to_numpy() / days
            )

    return result


def _clean_descriptions(descriptions: Iterable[object]) -> list[str]:
    return ["" if pd.isna(text) else str(text).strip() for text in descriptions]


def fit_description_tfidf(
    descriptions: Iterable[object], max_features: int | None = None
) -> tuple[TfidfVectorizer, csr_matrix]:
    """Fit a TF-IDF vectorizer on training descriptions and return its matrix."""
    vectorizer = TfidfVectorizer(max_features=max_features)
    matrix = vectorizer.fit_transform(_clean_descriptions(descriptions))
    return vectorizer, matrix


def transform_description_tfidf(
    vectorizer: TfidfVectorizer, descriptions: Iterable[object]
) -> csr_matrix:
    """Transform descriptions using a vectorizer already fitted on training data."""
    return vectorizer.transform(_clean_descriptions(descriptions))
