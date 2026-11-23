"""FastAPI endpoints for the personal finance predictor."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Annotated

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, field_validator

from backend.src.database import (
    DEFAULT_DATABASE,
    create_savings_goal,
    delete_budget,
    delete_savings_goal,
    get_budgets,
    get_savings_goals,
    get_transactions,
    initialize_database,
    replace_transactions,
    set_budget,
    update_savings_goal,
)
from backend.src.finance import (
    analyze_spending,
    calculate_health_score,
    forecast_monthly_spend,
    predict_categories,
    validate_transactions,
)

app = FastAPI(
    title="Smart Personal Finance Predictor & Analyzer",
    description="Local educational tools for analyzing personal expense transactions.",
    version="0.1.0",
)
FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"


@app.get("/", include_in_schema=False)
def dashboard() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/styles.css", include_in_schema=False)
def dashboard_styles() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "styles.css", media_type="text/css")


@app.get("/app.js", include_in_schema=False)
def dashboard_script() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "app.js", media_type="text/javascript")


class TransactionInput(BaseModel):
    transaction_date: date
    description: str = Field(max_length=500)
    amount: float
    category: str | None = Field(default=None, max_length=100)


class TransactionImport(BaseModel):
    transactions: Annotated[list[TransactionInput], Field(min_length=1, max_length=100000)]
    replace: bool = True


class CategoryPredictionInput(BaseModel):
    description: str = Field(min_length=1, max_length=500)
    amount: float


class CategoryPredictionRequest(BaseModel):
    transactions: Annotated[
        list[CategoryPredictionInput], Field(min_length=1, max_length=1000)
    ]


class HealthScoreRequest(BaseModel):
    monthly_income: float = Field(gt=0)
    monthly_debt_payments: float = Field(ge=0)
    savings_balance: float = Field(ge=0)
    discretionary_categories: list[str] = Field(
        default_factory=lambda: ["dining", "entertainment", "shopping", "travel"],
        max_length=100,
    )


class BudgetInput(BaseModel):
    month: str = Field(pattern=r"^\d{4}-(0[1-9]|1[0-2])$")
    category: str = Field(default="", max_length=100)
    amount: float = Field(gt=0)


class SavingsGoalInput(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    target_amount: float = Field(gt=0)
    current_amount: float = Field(ge=0)
    target_date: date

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Goal name cannot be blank.")
        return normalized


@app.on_event("startup")
def startup() -> None:
    initialize_database()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/transactions/import")
def import_transactions(payload: TransactionImport) -> dict[str, int | str]:
    frame = pd.DataFrame([transaction.model_dump() for transaction in payload.transactions])
    try:
        normalized = validate_transactions(frame)
        count = replace_transactions(normalized, replace=payload.replace)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return {"imported": count, "storage": str(DEFAULT_DATABASE.name)}


@app.get("/transactions")
def transactions() -> dict[str, list[dict[str, object]]]:
    frame = get_transactions()
    frame["transaction_date"] = frame["transaction_date"].astype(str)
    frame = frame.astype(object).where(pd.notna(frame), None)
    return {"transactions": frame.to_dict(orient="records")}


@app.get("/budgets")
def budgets(
    month: Annotated[str, Query(pattern=r"^\d{4}-(0[1-9]|1[0-2])$")],
) -> dict[str, list[dict[str, object]]]:
    return {"budgets": get_budgets(month)}


@app.put("/budgets")
def save_budget(payload: BudgetInput) -> dict[str, object]:
    return {
        "budget": set_budget(
            month=payload.month,
            category=payload.category.strip(),
            amount=payload.amount,
        )
    }


@app.delete("/budgets/{budget_id}")
def remove_budget(budget_id: int) -> dict[str, bool]:
    if not delete_budget(budget_id):
        raise HTTPException(status_code=404, detail="Budget not found.")
    return {"deleted": True}


@app.get("/savings-goals")
def savings_goals() -> dict[str, list[dict[str, object]]]:
    return {"goals": get_savings_goals()}


@app.post("/savings-goals")
def add_savings_goal(payload: SavingsGoalInput) -> dict[str, object]:
    return {
        "goal": create_savings_goal(
            name=payload.name.strip(),
            target_amount=payload.target_amount,
            current_amount=payload.current_amount,
            target_date=payload.target_date.isoformat(),
        )
    }


@app.put("/savings-goals/{goal_id}")
def save_savings_goal(
    goal_id: int, payload: SavingsGoalInput
) -> dict[str, object]:
    goal = update_savings_goal(
        goal_id=goal_id,
        name=payload.name.strip(),
        target_amount=payload.target_amount,
        current_amount=payload.current_amount,
        target_date=payload.target_date.isoformat(),
    )
    if goal is None:
        raise HTTPException(status_code=404, detail="Savings goal not found.")
    return {"goal": goal}


@app.delete("/savings-goals/{goal_id}")
def remove_savings_goal(goal_id: int) -> dict[str, bool]:
    if not delete_savings_goal(goal_id):
        raise HTTPException(status_code=404, detail="Savings goal not found.")
    return {"deleted": True}


@app.post("/predict-category")
def predict_category(
    payload: CategoryPredictionRequest,
) -> dict[str, list[dict[str, str | float]]]:
    frame = get_transactions()
    if frame.empty:
        raise HTTPException(
            status_code=422,
            detail="Import labeled transactions before requesting predictions.",
        )
    try:
        predictions = predict_categories(
            frame,
            [transaction.description for transaction in payload.transactions],
            [transaction.amount for transaction in payload.transactions],
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return {"predictions": predictions}


@app.get("/forecast-monthly")
def forecast_monthly() -> dict[str, object]:
    try:
        return forecast_monthly_spend(get_transactions())
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@app.get("/analysis")
def spending_analysis() -> dict[str, object]:
    try:
        return analyze_spending(get_transactions())
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@app.post("/health-score")
def health_score(payload: HealthScoreRequest) -> dict[str, object]:
    try:
        return calculate_health_score(
            get_transactions(),
            monthly_income=payload.monthly_income,
            monthly_debt_payments=payload.monthly_debt_payments,
            savings_balance=payload.savings_balance,
            discretionary_categories=payload.discretionary_categories,
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
