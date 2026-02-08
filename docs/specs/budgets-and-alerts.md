# Spec: Budgets and Alerts

## Motivation

AI API spending can grow unexpectedly. Developers need configurable spending limits with two enforcement levels: soft warnings (logged to stderr) and hard blocks (raise exceptions). Alert thresholds provide early warning as budgets approach their limits.

## API Design

### `BudgetManager`

- `set_budget(limit, period="total", scope="global", action="warn") -> BudgetConfig`
- `check(user_id=None) -> list[BudgetStatus]` — current status for all budgets
- `would_exceed(estimated_cost, user_id=None) -> bool` — pre-call check
- `enforce(estimated_cost, user_id=None) -> None` — raises `BudgetExceededError` if any `action="block"` budget would be exceeded
- `remove_budget(budget) -> None`
- `list_budgets() -> list[BudgetConfig]`

### `AlertManager`

- `on_alert(callback) -> None` — register `(BudgetStatus, str) -> None` callback
- `set_thresholds(percentages) -> None` — override defaults (50%, 80%, 95%, 100%)
- `check_and_notify(user_id=None) -> list[str]` — fire callbacks for newly crossed thresholds
- `reset() -> None` — allow thresholds to fire again

### Types

**BudgetConfig:** `limit` (Decimal), `period` (session/daily/weekly/monthly/total), `scope` (global/user:\<id\>/session:\<id\>), `action` (warn/block).

**BudgetStatus:** `config`, `spent`, `remaining`, `utilization` (float 0-1+), `is_exceeded` (bool).

**BudgetExceededError:** Raised with the offending `BudgetStatus`.

**AlertThreshold:** `percentage` (float), `message` (optional), `triggered` (bool).

## Data Model

- Budgets are in-memory only on the `BudgetManager` instance.
- Persistent budget config stored in `~/.tokenmeter/config.json` via `config.py`.
- Period start calculation: daily=midnight, weekly=Monday midnight, monthly=1st of month, total=no filter.
- Scope `"global"` queries all records; `"user:<id>"` and `"session:<id>"` filter accordingly.
- Spending is computed live from the tracker's storage (not cached).

## Edge Cases

- Zero limit -> 0% utilization, immediately exceeded
- `would_exceed` checks ALL budgets; `enforce` only checks `action="block"` budgets
- Alerts fire once per threshold (tracked via `triggered` flag); call `reset()` to re-arm
- No callbacks registered -> alerts print to stderr

## Files

- `src/tokenmeter/budget.py`
- `src/tokenmeter/alerts.py`
- `src/tokenmeter/config.py`
- `src/tokenmeter/_types.py` (BudgetConfig, BudgetStatus, BudgetExceededError, AlertThreshold)
