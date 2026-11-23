# Project Facts

## Verified Project Identity
- Project title: Smart Personal Finance Predictor and Analyzer
- Institute: KCC Institute of Technology and Management, Greater Noida
- Department: Computer Science & Engineering
- Program: B.Tech CSE (AI)
- README description: Local, educational personal-expense analysis project
- Deployment mode: Local web application
- Dashboard URL: http://127.0.0.1:8000
- Health URL: http://127.0.0.1:8000/health
- API documentation URL: http://127.0.0.1:8000/docs

## Technology Stack
- Language: Python
- Minimum Python version stated in README: 3.10
- Backend: FastAPI
- Local server: Uvicorn
- Frontend: HTML, CSS, JavaScript
- Persistence: SQLite
- Data processing: Pandas
- Numerical libraries: NumPy, SciPy
- Classification: scikit-learn
- Time-series forecasting: Statsmodels
- Testing: pytest and unittest

## Requirements
- fastapi >=0.115,<1
- numpy >=2.2,<3
- pandas >=2.2,<4
- pytest >=8,<9
- scikit-learn >=1.6,<2
- scipy >=1.15,<2
- statsmodels >=0.14,<1
- uvicorn >=0.34,<1

## Modules and Features
1. CSV import:
   - Input: CSV file with date, description, and amount columns
   - Category: optional
   - Output: normalized transactions stored in SQLite
   - Implementation: frontend and backend header alias mapping
2. CSV parsing and category inference:
   - Input: raw CSV text or Pandas DataFrame
   - Output: transaction_date, description, amount, category
   - Missing categories: keyword-based assignment to Housing, Groceries, Dining, Transport, Utilities, Healthcare, Entertainment, Shopping, Travel, Education, or Other
3. Transaction persistence:
   - Tables: transactions, budgets, savings_goals
   - Supports replace-by-default import and append import
4. Spending dashboard:
   - Input: locally stored transactions
   - Outputs: transaction count, total spend, average spend, top category, daily chart, category chart, transaction table
5. Spending analysis:
   - Input: locally stored transactions
   - Outputs: latest month, latest month spend, average monthly spend, month-over-month change, highest category and monthly/category totals
6. Category prediction:
   - Input: labeled transaction history, merchant description, amount
   - Model: TF-IDF 1-2 word features, StandardScaler amount, balanced logistic regression
   - Training constraints: at least two categories and at least two rows per category
7. 30-day forecasting:
   - Input: absolute daily expense totals
   - Model: Statsmodels ARIMA(1,1,1)
   - Output: 30 daily forecasts plus 90% lower and upper intervals
   - Constraints: at least 14 calendar days and at least two distinct daily totals
8. Financial health estimate:
   - Input: monthly income, debt payments, savings balance, discretionary categories
   - Method: rule-based risk heuristic
   - Outputs: health_score, risk_score, ratios, advisory notes
   - Explicit limitation: not a trained model or financial advice
9. Budget planning:
   - Input: month, optional category, positive amount
   - Output: monthly/category budget records and actual spending progress
10. Savings goal planning:
   - Input: name, target amount, current amount, target date
   - Output: saved goal records and UI progress

## Data Source
- Sample dataset: ml/data/sample_transactions.csv
- Dataset fields: transaction_date, description, amount, category
- Verified sample size: 30 rows
- Verified sample date range: 2026-09-01 to 2026-10-29
- Verified sample total spend: 4,779.88
- Verified sample average spend: 159.33
- Verified sample top category: Housing
- Verified sample Housing spend: 3,800.00
- Runtime storage: database/finance.db
- Verified current SQLite tables: transactions, budgets, savings_goals
- Verified current transaction-table row count: 1500

## ML and Statistical Methods
- Category features:
  - TF-IDF, unigram and bigram, maximum 5000 features
  - Transaction amount standardized with StandardScaler
  - Combined sparse feature matrix
- Category model:
  - LogisticRegression
  - max_iter=1000
  - class_weight=balanced
- Forecast:
  - Daily spend aggregation
  - Missing calendar days filled with zero
  - Absolute expense amounts
  - ARIMA order (1,1,1)
  - 30-day horizon
  - 90% confidence interval requested
  - Non-negative point and interval values
- Preprocessing:
  - Valid date and finite amount validation
  - Day-of-week and day-of-month features
  - Cyclic sine/cosine features
  - Category rolling mean, standard deviation, and spend velocity for 7, 30, and 90 days
  - Rolling values exclude the current transaction
- Health heuristic:
  - Debt-to-income thresholds of 25% and 40%
  - Savings-rate thresholds of 0%, 10%, and 20%
  - Emergency-fund thresholds of 1, 3, and 6 months
  - Discretionary coefficient-of-variation thresholds of 40% and 75%

## Evaluation and Results
- pytest result: 22 tests passed
- pytest warnings: 2 ARIMA EstimationWarning occurrences
- Test areas:
  - CSV header mapping
  - missing required fields
  - category inference
  - temporal and rolling features
  - TF-IDF reuse
  - classifier constraints
  - ARIMA shape and non-negative output
  - spending analysis
  - health score bounds
  - invalid import dates
  - replace/append persistence
  - budget upsert/delete
  - savings goal create/update/delete
- No classifier accuracy, precision, recall, F1, or confusion matrix was found
- No ARIMA backtest, MAE, RMSE, MAPE, or forecast-vs-actual metric was found
- Verified sample ARIMA forecast:
  - total: 2438.02
  - low aggregate: 0.00
  - high aggregate: 14226.88
  - 30 forecast rows
- Forecast output includes confidence level 90 in API

## Screenshots
- presentation/assets/screenshots/dashboard-overview.png
- presentation/assets/screenshots/dashboard-overview-section.png
- presentation/assets/screenshots/category-prediction.png
- presentation/assets/screenshots/category-prediction-section.png
- presentation/assets/screenshots/forecast.png
- presentation/assets/screenshots/forecast-section.png
- presentation/assets/screenshots/health-estimate.png
- presentation/assets/screenshots/health-estimate-section.png
- presentation/assets/screenshots/planning-section.png

## Folder Structure
- backend/src/main.py: FastAPI routes and request models
- backend/src/finance.py: validation, analysis, prediction, forecast, health services
- backend/src/database.py: SQLite initialization and CRUD
- frontend/index.html: dashboard markup
- frontend/app.js: browser UI and API calls
- frontend/csv_parser.py: Python CSV normalization
- frontend/styles.css: dashboard styles
- ml/src/data_processing/transactions.py: preprocessing and rolling features
- ml/src/models/classifier.py: category model
- ml/src/models/forecasting.py: ARIMA forecast
- ml/data/sample_transactions.csv: sample data
- ml/data/raw and ml/data/processed: data folders
- database/finance.db: local SQLite database
- tests/backend: finance and database tests
- tests/frontend: CSV parser tests
- tests/ml: preprocessing tests
- docs/feature-roadmap.md: delivered features and future priorities

## Verified Limitations
- Local use only
- No authentication
- No external cloud synchronization
- No bank/account integration
- No classifier holdout evaluation
- No ARIMA backtesting or error metrics
- No ARIMA confidence interval implementation fallback guarantee
- Health score is an educational heuristic
- README warns transaction data remains local and should not be exposed publicly

## Future Scope in Repository Roadmap
- Forecast backtesting and error metrics
- Uncertainty ranges and sparse-history explanation
- Predicted-versus-actual comparison
- Optional budget warning thresholds
- Recurring goal contributions
- Goal completion history
- Forecast-versus-budget view
- Monthly trend comparison
- Category-level forecast charts
- Export, accessibility, and downloadable reports

## Unresolved Project Fields
- [TO BE FILLED: Four team member names]
- [TO BE FILLED: Four roll numbers]
- [TO BE FILLED: Guide name]
- [TO BE FILLED: Guide designation]
- [TO BE FILLED: Hardware CPU]
- [TO BE FILLED: Hardware RAM]
- [TO BE FILLED: Hardware storage]
- [TO BE FILLED: Available GPU]
- [TO BE FILLED: Operating system name and version]
- [TO BE FILLED: Python version actually used]
- [TO BE FILLED: Project presentation date]

## [VERIFY] Items
- [VERIFY] Exact real-world product limitations and update status for Mint, YNAB, PocketGuard, and Toshl
- [VERIFY] IEEE bibliographic details for cited forecasting, text categorization, and package references
