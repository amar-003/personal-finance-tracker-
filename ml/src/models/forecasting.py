"""ARIMA expenditure forecasting utilities."""

from __future__ import annotations

import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA


def forecast_daily_spend(
    transactions: pd.DataFrame, days: int = 30
) -> pd.DataFrame:
    """Forecast non-negative daily spend from expense-only transaction rows."""
    if days < 1:
        raise ValueError("Forecast horizon must be at least one day.")
    required = {"transaction_date", "amount"}
    missing = required.difference(transactions.columns)
    if missing:
        raise ValueError("Missing forecast columns: " + ", ".join(sorted(missing)))
    if transactions.empty:
        raise ValueError("Import transactions before requesting a forecast.")

    frame = transactions.loc[:, ["transaction_date", "amount"]].copy()
    frame["transaction_date"] = pd.to_datetime(
        frame["transaction_date"], errors="coerce"
    )
    frame["amount"] = pd.to_numeric(frame["amount"], errors="coerce")
    if frame.isna().any().any() or not np.isfinite(frame["amount"].to_numpy()).all():
        raise ValueError("Forecast data must contain valid dates and finite amounts.")

    frame["spend"] = frame["amount"].abs()
    daily = (
        frame.groupby(frame["transaction_date"].dt.normalize())["spend"]
        .sum()
        .sort_index()
    )
    daily = daily.asfreq("D", fill_value=0.0)
    if len(daily) < 14:
        raise ValueError("At least 14 calendar days of transaction history are needed.")
    if daily.nunique() < 2:
        raise ValueError("The spend history has too little variation to fit ARIMA.")

    model = ARIMA(daily.astype(float), order=(1, 1, 1))
    fitted = model.fit()
    forecast_result = fitted.get_forecast(steps=days)
    prediction = np.maximum(
        np.asarray(forecast_result.predicted_mean, dtype=float), 0
    )
    if not np.isfinite(prediction).all():
        raise ValueError("ARIMA could not produce a finite forecast for this history.")
    try:
        interval = forecast_result.conf_int(alpha=0.1)
        lower = np.maximum(np.asarray(interval.iloc[:, 0], dtype=float), 0)
        upper = np.maximum(np.asarray(interval.iloc[:, 1], dtype=float), 0)
    except (AttributeError, IndexError, TypeError, ValueError):
        lower = prediction.copy()
        upper = prediction.copy()
    future_dates = pd.date_range(
        daily.index[-1] + pd.Timedelta(days=1), periods=days, freq="D"
    )
    return pd.DataFrame(
        {
            "date": future_dates,
            "forecast": prediction,
            "lower": lower,
            "upper": upper,
        }
    )
