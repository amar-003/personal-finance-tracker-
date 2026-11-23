# One-Minute Project Summary

Smart Personal Finance Predictor & Analyzer is a local educational personal-finance application built with a Python FastAPI backend and a responsive HTML, CSS, and JavaScript frontend. It accepts a transaction CSV, recognizes common column names, validates and stores expense records in SQLite, and presents filtering, transaction history, daily spending charts, and category breakdowns.

The implemented prediction module trains a logistic-regression classifier on labeled transaction descriptions and transaction amounts using TF-IDF text features. The forecasting module aggregates daily spending and applies an ARIMA(1,1,1) model to estimate 30 future days. The health estimate is a transparent rule-based heuristic using debt-to-income, savings rate, emergency-fund coverage, and discretionary-spending variation; it is not a trained risk model.

The application also provides monthly overall or category budgets and savings goals with progress updates. Verified runtime validation used a 30-row sample CSV: the dashboard showed 30 transactions, 4,779.88 total spend, 159.33 average spend, and Housing as the top category. The 30-day forecast produced an estimated 2,438.02 total. The project test suite contains 21 passing tests.

Its main limitations are local-only operation, no authentication or cloud integration, no classifier holdout evaluation or ARIMA backtest, and no confidence intervals. Realistic future work is forecast backtesting with MAE/RMSE, uncertainty ranges, budget alerts, protected storage, report export, and improved accessibility.
