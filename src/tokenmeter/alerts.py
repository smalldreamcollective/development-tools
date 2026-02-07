from __future__ import annotations

import sys
from typing import Callable

from tokenmeter._types import AlertThreshold, BudgetStatus
from tokenmeter.budget import BudgetManager

AlertCallback = Callable[[BudgetStatus, str], None]


class AlertManager:
    """Manages alert thresholds and notification callbacks."""

    def __init__(self, budget_manager: BudgetManager) -> None:
        self._budget_manager = budget_manager
        self._callbacks: list[AlertCallback] = []
        self._thresholds: list[AlertThreshold] = [
            AlertThreshold(percentage=0.5),
            AlertThreshold(percentage=0.8),
            AlertThreshold(percentage=0.95),
            AlertThreshold(percentage=1.0),
        ]

    def on_alert(self, callback: AlertCallback) -> None:
        """Register a callback to be called when a threshold is crossed."""
        self._callbacks.append(callback)

    def set_thresholds(self, percentages: list[float]) -> None:
        """Override the default threshold percentages."""
        self._thresholds = [AlertThreshold(percentage=p) for p in sorted(percentages)]

    def check_and_notify(self, user_id: str | None = None) -> list[str]:
        """Check budgets against thresholds and fire callbacks for newly crossed ones.

        Returns list of alert messages generated.
        """
        messages: list[str] = []
        statuses = self._budget_manager.check(user_id)

        for status in statuses:
            for threshold in self._thresholds:
                if threshold.triggered:
                    continue
                if status.utilization >= threshold.percentage:
                    threshold.triggered = True
                    msg = threshold.message or _default_message(status, threshold)
                    messages.append(msg)
                    self._fire(status, msg)

        return messages

    def reset(self) -> None:
        """Reset all threshold triggered states."""
        for t in self._thresholds:
            t.triggered = False

    def _fire(self, status: BudgetStatus, message: str) -> None:
        if self._callbacks:
            for cb in self._callbacks:
                cb(status, message)
        else:
            print(f"[tokenmeter] {message}", file=sys.stderr)


def _default_message(status: BudgetStatus, threshold: AlertThreshold) -> str:
    pct = int(threshold.percentage * 100)
    return (
        f"Budget alert: {pct}% of ${status.config.limit} "
        f"({status.config.period} {status.config.scope}) used. "
        f"Spent: ${status.spent}, Remaining: ${status.remaining}"
    )
