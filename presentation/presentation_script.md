# Presentation Speaking Script

## Slide 1 — Title
Good morning/afternoon. I am presenting Smart Personal Finance Predictor & Analyzer, a local application for importing and understanding personal spending data. The project combines an interactive dashboard with category prediction, expenditure forecasting, and planning tools.

## Slide 2 — Problem
Most people receive their spending information through bank statements or separate apps. The data is present, but they still need to manually organize expenses, identify recurring patterns, set budgets, and estimate future spending. This becomes harder when transactions use different descriptions and categories. Our project addresses this gap without requiring a cloud account.

## Slide 3 — Proposed Solution
The application follows one simple flow: a user imports a CSV file, the system validates and processes the rows, then presents charts and predictions. The same data supports budgets and savings goals. The main benefits are local storage, transparent processing, and a dashboard that turns transactions into visible patterns.

## Slide 4 — Objectives and Features
The implemented objectives are CSV import, spending analysis, category prediction, 30-day forecasting, monthly budgets, and savings targets. The category and forecasting features use machine-learning or statistical methods. Budgets and goals are practical planning modules built on the same stored transactions.

## Slide 5 — System Architecture
The browser provides the HTML, CSS, and JavaScript interface. JavaScript calls FastAPI REST endpoints. FastAPI uses Pandas for validation and analysis, and SQLite stores transactions, budgets, and goals. The ML functions are invoked inside the Python backend rather than through a separate service.

## Slide 6 — Technology Stack
The frontend is plain HTML, CSS, and JavaScript. The backend uses Python, FastAPI, and Uvicorn. Pandas provides data transformation, while SQLite provides local persistence. Scikit-learn and SciPy support text and category classification. Statsmodels provides ARIMA forecasting. Tests use pytest and unittest.

## Slide 7 — System Workflow
The workflow begins when the user selects a CSV. The browser identifies common header variations and sends normalized transactions to the API. FastAPI validates the records and replaces or appends them in SQLite. The dashboard then filters and aggregates the data. For prediction or forecasting, the backend trains or fits from the latest imported history.

## Slide 8 — Core Modules
The overview displays transaction totals, average spend, top category, spending charts, category charts, and recent activity. Separate modules support category prediction, 30-day forecasting, the health estimate, and planning. Budgets can be overall or category-specific, while savings goals track target amount and target date.

## Slide 9 — AI/ML and Analytics
Category prediction uses TF-IDF features from transaction descriptions combined with a scaled amount, passed to a balanced logistic-regression baseline. Forecasting aggregates spending by calendar day and applies an ARIMA(1,1,1) model. The health value is not a trained model. It is an explainable heuristic based on debt-to-income, savings rate, emergency-fund coverage, and discretionary spending variation.

## Slide 10 — Application Demonstration
Here is the actual dashboard using the sample 30-row transaction CSV. The overview shows 30 transactions, a total spend of 4,779.88, an average of 159.33, and Housing as the top category. The forecast tab reports an estimated 30-day total of 2,438.02 for that data. These are demonstration values, not production claims.

## Slide 11 — Results, Limitations and Future Scope
The project successfully implements CSV import, charts, category prediction, ARIMA forecasting, budgets, savings goals, and a health heuristic. It is intentionally local and has no authentication or cloud integration. There is currently no backtest or error metric for forecasting. Future work should add backtesting, uncertainty ranges, budget alerts, authentication, export, and protected storage.

## Slide 12 — Conclusion
In summary, the application converts local transaction data into understandable insights, combines real statistical and ML logic with transparent planning tools, and clearly separates implemented functionality from future scope. It is a suitable educational finance-analysis system, not a certified financial product. Thank you. I am ready for questions.
