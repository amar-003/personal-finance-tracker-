"""Financial prediction and educational risk-analysis services."""

from __future__ import annotations

import numpy as np
import pandas as pd

from ml.src.data_processing.transactions import preprocess_transactions
from ml.src.models.classifier import train_category_classifier
from ml.src.models.forecasting import forecast_daily_spend


def validate_transactions(transactions: pd.DataFrame) -> pd.DataFrame:
    """Normalize transaction input and reject invalid optional categories."""
    result = preprocess_transactions(transactions)
    if "category" not in result.columns:
        result["category"] = None
    result["category"] = result["category"].replace(r"^\s*$", np.nan, regex=True)
    result["category"] = result["category"].map(
        lambda value: str(value).strip() if pd.notna(value) else np.nan
    )
    return result[
        ["transaction_date", "description", "amount", "category"]
        + [
            column
            for column in result.columns
            if column not in {"transaction_date", "description", "amount", "category"}
        ]
    ]


def predict_categories(
    transactions: pd.DataFrame, descriptions: list[str], amounts: list[float]
) -> list[dict[str, str | float]]:
    labeled = transactions.dropna(subset=["category"])
    model = train_category_classifier(labeled)
    predictions = model.predict(descriptions, amounts)
    return predictions


def forecast_monthly_spend(transactions: pd.DataFrame) -> dict[str, object]:
    """Forecast the next 30 days of spending using an ARIMA time series."""
    forecast = forecast_daily_spend(transactions, days=30)
    lower_total = float(forecast["lower"].sum())
    upper_total = float(forecast["upper"].sum())
    return {
        "method": "ARIMA(1, 1, 1)",
        "period_days": 30,
        "total_forecast": round(float(forecast["forecast"].sum()), 2),
        "range_low": round(lower_total, 2),
        "range_high": round(upper_total, 2),
        "confidence_level": 90,
        "daily_forecast": [
            {
                "date": row.date.date().isoformat(),
                "amount": round(float(row.forecast), 2),
                "lower": round(float(row.lower), 2),
                "upper": round(float(row.upper), 2),
            }
            for row in forecast.itertuples(index=False)
        ],
    }


def analyze_spending(transactions: pd.DataFrame) -> dict[str, object]:
    """Build a concise, explainable month and category spending analysis."""
    if transactions.empty:
        raise ValueError("Import transactions before requesting an analysis.")
    required = {"transaction_date", "amount"}
    missing = required.difference(transactions.columns)
    if missing:
        raise ValueError("Missing analysis columns: " + ", ".join(sorted(missing)))

    frame = transactions.copy()
    frame["transaction_date"] = pd.to_datetime(
        frame["transaction_date"], errors="coerce"
    )
    frame["amount"] = pd.to_numeric(frame["amount"], errors="coerce")
    if frame.isna().any().any() or not np.isfinite(frame["amount"].to_numpy()).all():
        raise ValueError("Analysis data must contain valid dates and finite amounts.")

    frame["spend"] = frame["amount"].abs()
    frame["month"] = frame["transaction_date"].dt.to_period("M").astype(str)
    monthly = (
        frame.groupby("month", sort=True)["spend"]
        .sum()
        .sort_index()
    )
    category_totals = (
        frame.assign(category=frame["category"].fillna("Uncategorized").astype(str).str.strip())
        .groupby("category", sort=False)["spend"]
        .sum()
        .sort_values(ascending=False)
    )
    latest_month = str(monthly.index[-1])
    previous_month = str(monthly.index[-2]) if len(monthly) >= 2 else None
    latest_spend = float(monthly.iloc[-1])
    previous_spend = float(monthly.iloc[-2]) if previous_month else None
    month_change = (
        (latest_spend - previous_spend) / previous_spend * 100
        if previous_spend is not None and previous_spend > 0
        else None
    )
    highest_category = (
        str(category_totals.index[0]) if not category_totals.empty else "Uncategorized"
    )
    highest_category_spend = (
        float(category_totals.iloc[0]) if not category_totals.empty else 0.0
    )
    return {
        "latest_month": latest_month,
        "latest_month_spend": round(latest_spend, 2),
        "average_monthly_spend": round(float(monthly.mean()), 2),
        "month_over_month_change_percent": (
            None if month_change is None else round(month_change, 2)
        ),
        "highest_category": highest_category,
        "highest_category_spend": round(highest_category_spend, 2),
        "monthly_totals": [
            {"month": month, "amount": round(float(amount), 2)}
            for month, amount in monthly.items()
        ],
        "category_totals": [
            {"category": category, "amount": round(float(amount), 2)}
            for category, amount in category_totals.items()
        ],
    }


def calculate_health_score(
    transactions: pd.DataFrame,
    monthly_income: float,
    monthly_debt_payments: float,
    savings_balance: float,
    discretionary_categories: list[str],
) -> dict[str, object]:
    """Compute an explainable heuristic risk score from 0 (lower) to 100."""
    if not np.isfinite([monthly_income, monthly_debt_payments, savings_balance]).all():
        raise ValueError("Income, debt payments, and savings must be finite numbers.")
    if monthly_income <= 0 or monthly_debt_payments < 0 or savings_balance < 0:
        raise ValueError(
            "Monthly income must be positive; debt payments and savings cannot be negative."
        )
    if transactions.empty:
        raise ValueError("Import transaction data before calculating a health score.")

    frame = transactions.copy()
    frame["transaction_date"] = pd.to_datetime(
        frame["transaction_date"], errors="raise"
    )
    frame["spend"] = pd.to_numeric(frame["amount"], errors="raise").abs()
    frame["month"] = frame["transaction_date"].dt.to_period("M")
    latest_month = frame["month"].max()
    recent_months = pd.period_range(end=latest_month, periods=3, freq="M")
    monthly_spend = (
        frame.groupby("month")["spend"].sum().reindex(recent_months, fill_value=0)
    )
    average_monthly_spend = float(monthly_spend.mean())
    debt_to_income = monthly_debt_payments / monthly_income
    savings_rate = (monthly_income - average_monthly_spend) / monthly_income
    emergency_fund_months = (
        savings_balance / average_monthly_spend
        if average_monthly_spend > 0
        else float("inf")
    )

    score = 0
    advice: list[str] = []
    if debt_to_income >= 0.4:
        score += 30
        advice.append("Debt payments are at least 40% of income; consider a repayment plan.")
    elif debt_to_income >= 0.25:
        score += 18
        advice.append("Review debt payments; they use at least 25% of income.")

    if savings_rate < 0:
        score += 30
        advice.append("Recent average spending exceeds income; review expenses or income needs.")
    elif savings_rate < 0.1:
        score += 20
        advice.append("The estimated savings rate is below 10%; consider a sustainable savings target.")
    elif savings_rate < 0.2:
        score += 10
        advice.append("Building savings toward 20% of income may improve resilience.")

    if emergency_fund_months < 1:
        score += 20
        advice.append("Savings cover less than one average month of spending.")
    elif emergency_fund_months < 3:
        score += 12
        advice.append("Consider building an emergency fund toward three months of spending.")
    elif emergency_fund_months < 6:
        score += 5

    categories = {category.casefold() for category in discretionary_categories}
    if categories and frame["category"].notna().any():
        discretionary = frame[
            frame["category"].fillna("").str.casefold().isin(categories)
        ].groupby("month")["spend"].sum()
        discretionary = discretionary.reindex(recent_months, fill_value=0)
        discretionary_mean = float(discretionary.mean())
        if len(discretionary) >= 2 and discretionary_mean > 0:
            discretionary_cv = float(discretionary.std(ddof=0) / discretionary_mean)
            if discretionary_cv >= 0.75:
                score += 20
                advice.append("Discretionary spending varies substantially month to month.")
            elif discretionary_cv >= 0.4:
                score += 10
                advice.append("Consider tracking discretionary spending for more consistency.")
        else:
            discretionary_cv = None
    else:
        discretionary_cv = None

    if not advice:
        advice.append(
            "The supplied figures show no elevated indicators under this simple heuristic."
        )

    return {
        "health_score": 100 - min(score, 100),
        "risk_score": min(score, 100),
        "metrics": {
            "debt_to_income_ratio": round(debt_to_income, 4),
            "estimated_savings_rate": round(savings_rate, 4),
            "average_monthly_spending": round(average_monthly_spend, 2),
            "emergency_fund_months": (
                None if not np.isfinite(emergency_fund_months) else round(emergency_fund_months, 2)
            ),
            "discretionary_spending_coefficient_of_variation": (
                None if discretionary_cv is None else round(discretionary_cv, 4)
            ),
        },
        "advisory_notes": advice,
        "score_note": (
            "Educational heuristic only; not a trained risk model or financial advice."
        ),
    }
