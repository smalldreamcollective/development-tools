# Budgets and Alerts

Set spending limits and receive notifications when thresholds are crossed.

## Classes

### `BudgetManager`

Manages spending limits and enforcement. Source: `src/tokenmeter/budget.py`

```python
from tokenmeter import BudgetManager

# Usually accessed via meter.budget
meter = tokenmeter.Meter()
budget = meter.budget
```

**Methods:**

#### `set_budget(limit, period="total", scope="global", action="warn") -> BudgetConfig`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | `float \| Decimal` | required | Maximum spending in USD |
| `period` | `str` | `"total"` | `"session"`, `"daily"`, `"weekly"`, `"monthly"`, or `"total"` |
| `scope` | `str` | `"global"` | `"global"`, `"user:<id>"`, or `"session:<id>"` |
| `action` | `str` | `"warn"` | `"warn"` (log to stderr) or `"block"` (raise exception) |

```python
meter.set_budget(limit=10.00, period="daily", action="block")
meter.set_budget(limit=100.00, period="monthly", action="warn")
meter.set_budget(limit=5.00, period="total", scope="user:alice", action="block")
```

#### `check(user_id=None) -> list[BudgetStatus]`

Returns current status for all budgets:

```python
statuses = meter.check_budget()
for status in statuses:
    print(f"${status.spent} / ${status.config.limit} ({status.utilization:.0%})")
```

#### `would_exceed(estimated_cost, user_id=None) -> bool`

Check if a pending call would push past any budget:

```python
estimated = meter.estimate("Long prompt...", model="claude-opus-4-6")
if meter.budget.would_exceed(estimated):
    print("Switching to cheaper model")
```

#### `enforce(estimated_cost, user_id=None) -> None`

Raises `BudgetExceededError` if any budget with `action="block"` would be exceeded:

```python
from tokenmeter._types import BudgetExceededError

try:
    meter.budget.enforce(estimated_cost)
except BudgetExceededError as e:
    print(f"Budget exceeded: {e}")
```

#### `remove_budget(budget: BudgetConfig) -> None`

Remove a previously set budget.

#### `list_budgets() -> list[BudgetConfig]`

Return all configured budgets.

### `AlertManager`

Manages threshold-based notifications. Source: `src/tokenmeter/alerts.py`

```python
# Usually accessed via meter.alerts
alerts = meter.alerts
```

**Methods:**

#### `on_alert(callback) -> None`

Register a callback fired when a threshold is crossed:

```python
def handle_alert(status: BudgetStatus, message: str):
    print(f"ALERT: {message}")
    # Send to Slack, log, etc.

meter.on_alert(handle_alert)
```

Callback signature: `(BudgetStatus, str) -> None`

If no callbacks are registered, alerts print to stderr.

#### `set_thresholds(percentages: list[float]) -> None`

Override default thresholds (default: 50%, 80%, 95%, 100%):

```python
meter.alerts.set_thresholds([0.5, 0.8, 0.95])
```

#### `check_and_notify(user_id=None) -> list[str]`

Check budgets and fire callbacks for newly crossed thresholds. Called automatically by `meter.record()`.

#### `reset() -> None`

Reset all threshold triggered states (thresholds can fire again).

## Types

### `BudgetConfig`

| Field | Type | Description |
|-------|------|-------------|
| `limit` | `Decimal` | Maximum spending in USD |
| `period` | `str` | `"session"`, `"daily"`, `"weekly"`, `"monthly"`, `"total"` |
| `scope` | `str` | `"global"` or scoped to user/session |
| `action` | `str` | `"warn"` or `"block"` |

### `BudgetStatus`

| Field | Type | Description |
|-------|------|-------------|
| `config` | `BudgetConfig` | The budget configuration |
| `spent` | `Decimal` | Amount spent in the period |
| `remaining` | `Decimal` | Amount remaining (>= 0) |
| `utilization` | `float` | Fraction used (0.0 to 1.0+) |
| `is_exceeded` | `bool` | Whether the budget is exceeded |

## Example: Full Budget Workflow

```python
import tokenmeter

meter = tokenmeter.Meter(storage="sqlite")

# Set budgets
meter.set_budget(limit=10.00, period="daily", action="block")
meter.set_budget(limit=100.00, period="monthly", action="warn")

# Set up alerts
meter.alerts.set_thresholds([0.5, 0.8, 1.0])
meter.on_alert(lambda status, msg: print(f"[ALERT] {msg}"))

# Before making expensive calls
estimated = meter.estimate("Very long prompt...", model="claude-opus-4-6")
if meter.budget.would_exceed(estimated):
    print("Would exceed budget")
else:
    meter.budget.enforce(estimated)  # raises BudgetExceededError if blocked
    response = call_api(...)
    meter.record(response)  # alerts fire automatically here
```
