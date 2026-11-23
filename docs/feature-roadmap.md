# Personal Finance Feature Roadmap

## Delivered

- Local CSV import with automatic transaction column mapping and category
  defaults.
- Daily spending and category charts with transaction filters.
- Category prediction and a 30-day ARIMA spending forecast, now shown as a
  trend chart with an explicit estimate disclaimer.
- Monthly overall and category budgets, with actual spending progress.
- Savings goals with target dates, progress updates, and estimated monthly
  contributions.

## Next priorities

### Forecast quality and transparency

- Backtest forecasts against historical months and report error metrics.
- Show uncertainty ranges and explain when transaction history is too sparse
  for a useful estimate.
- Compare predicted totals with actual spending after each forecast period.

### More planning controls

- Add optional budget warning thresholds and in-app notices.
- Support recurring goal contributions and goal-completion history.
- Provide an optional forecast-versus-budget view for the selected month.

### Dashboard improvements

- Add monthly trend comparisons and category-level forecast charts.
- Allow users to export a filtered report without sending data to a service.
- Improve chart keyboard accessibility and downloadable image/report formats.

Forecasts and goal timelines are estimates for educational planning, not
guaranteed outcomes or financial advice. Transaction, budget, and goal records
remain in the local SQLite database.
