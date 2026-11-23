# Smart Personal Finance Predictor & Analyzer

A local, educational B.Tech CSE (AI) portfolio project for exploring personal
expense analysis. The current MVP imports a user's labeled transaction CSV,
stores it in SQLite, predicts expense categories, forecasts spending, and
computes an explainable financial-health estimate.

## Features

- CSV import, transaction history, daily spend chart, and category breakdown.
- Category prediction using TF-IDF text features, scaled transaction amount,
  and a scikit-learn logistic regression baseline.
- 30-day expenditure forecast using ARIMA(1, 1, 1), with a daily forecast
  chart.
- Monthly overall/category budgets and savings goals with progress tracking.
- A transparent health/risk heuristic using debt-to-income, estimated savings
  rate, emergency-fund coverage, and (when enough labeled history exists)
  discretionary-spending variation.
- FastAPI endpoints and a responsive HTML, CSS, and JavaScript dashboard, backed by a local SQLite file.
- Transaction preprocessing with temporal, cyclical, and category-level rolling
  features.

This is a learning project, not financial advice or a validated financial
product. The risk estimate is a rule-based heuristic, not a trained risk model.

## Requirements and setup

Use Python 3.10 or later. From the project root, create a virtual environment
and install dependencies:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Run the dashboard and API from the project root with the virtual environment
activated:

```powershell
python -m frontend.app
```

Open the dashboard at <http://127.0.0.1:8000>. The API health check and
interactive API documentation are at <http://127.0.0.1:8000/health> and
<http://127.0.0.1:8000/docs>.

Run the test suite from the project root:

```powershell
python -m pytest
```

## CSV format

The dashboard recognizes common variations in CSV header names and converts
them to the fields below. Matching ignores capitalization, spaces, and
punctuation. For example, `Date`, `Posted Date`, or `Transaction Date` map to
`transaction_date`; `Payee` or `Merchant Name` map to `description`; and
`Debit Amount` or `Spend` map to `amount`.

| Column | Required | Meaning |
| --- | --- | --- |
| `transaction_date` | Yes | Date parseable by Pandas, such as `2026-01-31` |
| `description` | Yes | Merchant or transaction text |
| `amount` | Yes | Numeric expense amount |
| `category` | No | Existing expense label used to train the category classifier |

Use expense transactions, not income rows; spend totals use the absolute value
of each amount. Category prediction needs at least two labeled categories and
at least two transactions per category. Forecasting needs at least 14 calendar
days of history with some variation. Replace-history is enabled by default when
importing; uncheck it to append rows.

The CSV is stored locally in `database/finance.db`, which is ignored by Git.
Do not upload or commit financial information you are not comfortable storing
locally. The API is intended for local development and has no authentication;
do not expose it to a public network.

## API

- `GET /health` — service status.
- `POST /transactions/import` — validate and save transaction rows; pass
  `replace: false` to append instead of replacing existing rows.
- `GET /transactions` — list locally stored transactions.
- `POST /predict-category` — predict categories for one or more descriptions
  using labeled rows currently stored in SQLite.
- `GET /forecast-monthly` — forecast daily spend for the next 30 days and return
  the 30-day total.
- `GET /budgets?month=YYYY-MM` and `PUT /budgets` — list or upsert a monthly
  overall/category budget. `DELETE /budgets/{budget_id}` removes one.
- `GET /savings-goals`, `POST /savings-goals`, and
  `PUT`/`DELETE /savings-goals/{goal_id}` — manage savings targets and progress.
- `POST /health-score` — compute a health/risk estimate from stored transactions
  and user-supplied monthly income, debt payments, savings, and discretionary
  categories.

## Project structure

- `frontend/` — browser dashboard and CSV import helpers.
- `backend/` — FastAPI endpoints, finance services, and SQLite persistence.
- `ml/src/data_processing/` — input validation and transaction feature
  engineering.
- `ml/src/models/` — category classifier and ARIMA forecasting model.
- `ml/data/` — local datasets; raw and processed data are git-ignored.
- `database/` — local SQLite database and future schema migrations.
- `tests/` — focused tests for preprocessing, models, finance calculations,
  and persistence.
- `docs/` — project documentation.

See [docs/feature-roadmap.md](docs/feature-roadmap.md) for delivered features
and next priorities.
