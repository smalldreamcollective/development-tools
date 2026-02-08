# References: Budgets and Alerts

Sources consulted during design and implementation of the budgets and alerts feature.

## Design Inspiration

- **Cloud provider billing alerts (AWS Budgets, GCP Budget Alerts)**
  https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-managing-costs.html
  https://cloud.google.com/billing/docs/how-to/budgets
  Used for: the concept of configurable spending limits with threshold-based alerts. Informed the period/scope/action model and the percentage-based alert thresholds (50%, 80%, 95%, 100%).

- **Circuit breaker pattern**
  General resilience pattern. Used for: the `action="block"` enforcement that raises `BudgetExceededError` to prevent further spending, analogous to a circuit breaker tripping.

## Language References

- **Python `datetime` module — timedelta and date arithmetic**
  https://docs.python.org/3/library/datetime.html
  Used for: computing period start times (daily=midnight, weekly=Monday, monthly=1st of month).

## Design Decisions

| Decision | Source |
|----------|--------|
| Two enforcement levels: warn vs block | AWS Budgets offers similar "notify" vs "stop" actions |
| Percentage-based alert thresholds | GCP/AWS budget alerts use percentage thresholds |
| Alerts fire once per threshold (require reset) | Prevents alert spam; matches cloud billing alert behavior |
| No callbacks registered -> print to stderr | Sensible default so alerts aren't silently lost |
| Spending computed live from storage (not cached) | Ensures accuracy; avoids stale cache invalidation complexity |
| Budget config persisted in JSON file | Simple, human-readable, no database dependency for config |
