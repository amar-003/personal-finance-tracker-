# Likely Viva Questions and Answers

1. **What is the project?**  
   A local personal-finance dashboard that imports CSV transactions, analyzes spending, predicts categories, forecasts the next 30 days, estimates an educational health score, and tracks budgets and savings goals.

2. **Why did you choose FastAPI?**  
   FastAPI provides typed Python request models, fast local REST APIs, and generated documentation. It is suitable for the small local backend.

3. **How is the frontend connected to the backend?**  
   Plain JavaScript uses the Fetch API to call endpoints such as `/transactions/import`, `/predict-category`, `/forecast-monthly`, and `/health-score`.

4. **What database is used?**  
   SQLite, stored locally at `database/finance.db`.

5. **What tables are stored?**  
   `transactions`, `budgets`, and `savings_goals`.

6. **What CSV fields are required?**  
   `transaction_date`, `description`, and `amount`. Category is optional.

7. **How are CSV headers normalized?**  
   The frontend and backend recognize common aliases and also infer fields from normalized header names.

8. **How does category assignment work during import?**  
   A supplied category is retained. If absent, a keyword heuristic assigns categories such as Groceries, Dining, Transport, or Other.

9. **What is the category prediction model?**  
   TF-IDF with 1–2 word features, scaled transaction amount, and logistic regression.

10. **Why combine text and amount?**  
    The description identifies the merchant or service, while amount may help distinguish categories when useful.

11. **What training requirements exist?**  
    At least two labeled categories and at least two transactions in every labeled category.

12. **Is the category model hyperparameter-tuned or evaluated?**  
    No. It is a baseline and no holdout accuracy metric is implemented.

13. **What is the forecasting model?**  
    Statsmodels ARIMA with order `(1,1,1)`.

14. **What data does ARIMA receive?**  
    Absolute daily expense totals, with missing calendar days filled with zero.

15. **How much history is required?**  
    At least 14 calendar days and at least two distinct daily totals.

16. **What forecast horizon is returned?**  
    30 future calendar days.

17. **Is forecasting guaranteed?**  
    No. It is an educational estimate and output is explicitly presented as a disclaimer.

18. **What accuracy metric is reported?**  
    None. The roadmap identifies backtesting and MAE/RMSE as future work.

19. **What is the financial health score?**  
    A rule-based heuristic that returns a health score and a risk score.

20. **How is the health score calculated?**  
    Debt-to-income and savings-rate thresholds add risk points; emergency-fund coverage and discretionary-spending variation can add more. The score is `100 - risk`, capped at zero to 100.

21. **Is the health score a trained AI model?**  
    No. It uses fixed educational rules and is not financial advice.

22. **How are budgets implemented?**  
    Budgets have month, optional category, and amount. SQLite enforces a unique month/category pair and positive amount.

23. **How are savings goals implemented?**  
    SQLite stores name, target amount, current amount, target date, and creation date. The UI calculates progress and remaining contribution timing.

24. **Does the app support append and replace import?**  
    Yes. Replace is the default; append is available with `replace: false`.

25. **What testing is present?**  
    Focused tests cover preprocessing, classifier constraints, ARIMA output shape, health calculation, invalid imports, CSV parser behavior, and database operations.

26. **How many tests pass?**  
    The current suite reported 21 passing tests. Two tests emit ARIMA estimation warnings.

27. **What are the main limitations?**  
    Local-only use, no authentication, no cloud sync, no model backtest or uncertainty intervals, and no bank-account integration.

28. **What future improvements are planned?**  
    Forecast backtesting and error metrics, confidence or uncertainty ranges, budget warnings, recurring goals, report export, authentication, and improved accessibility.

29. **Is transaction data sent outside the system?**  
    No external service is used for the core application. The HTML loads Google Fonts, but transaction processing remains local.

30. **Is this production financial software?**  
    No. It is an educational B.Tech project and should not be used as verified financial advice.
