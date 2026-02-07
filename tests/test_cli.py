"""Tests for the tokenmeter CLI."""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

import pytest
from click.testing import CliRunner

from tokenmeter.cli import cli
from tokenmeter.config import load_budgets, save_budgets
from tokenmeter._types import BudgetConfig


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def db_path(tmp_path):
    return str(tmp_path / "test.db")


@pytest.fixture
def config_path(tmp_path):
    return str(tmp_path / "config.json")


class TestModels:
    def test_list_all_models(self, runner, db_path):
        result = runner.invoke(cli, ["--db", db_path, "models"])
        assert result.exit_code == 0
        assert "claude-sonnet-4-5" in result.output
        assert "gpt-4o" in result.output

    def test_filter_by_provider(self, runner, db_path):
        result = runner.invoke(cli, ["--db", db_path, "models", "--provider", "anthropic"])
        assert result.exit_code == 0
        assert "claude" in result.output
        assert "gpt" not in result.output

    def test_filter_openai(self, runner, db_path):
        result = runner.invoke(cli, ["--db", db_path, "models", "--provider", "openai"])
        assert result.exit_code == 0
        assert "gpt" in result.output
        assert "claude" not in result.output


class TestEstimate:
    def test_estimate_basic(self, runner, db_path):
        result = runner.invoke(cli, ["--db", db_path, "estimate", "Hello world", "--model", "claude-sonnet-4-5"])
        assert result.exit_code == 0
        assert "Estimated tokens:" in result.output
        assert "Estimated cost:" in result.output
        assert "$" in result.output

    def test_estimate_from_stdin(self, runner, db_path):
        result = runner.invoke(cli, ["--db", db_path, "estimate", "--model", "gpt-4o"], input="Hello world")
        assert result.exit_code == 0
        assert "Estimated cost:" in result.output

    def test_estimate_requires_model(self, runner, db_path):
        result = runner.invoke(cli, ["--db", db_path, "estimate", "Hello"])
        assert result.exit_code != 0


class TestUsage:
    def test_usage_empty(self, runner, db_path):
        result = runner.invoke(cli, ["--db", db_path, "usage"])
        assert result.exit_code == 0
        assert "Total spending: $0.000000" in result.output

    def test_usage_with_records(self, runner, db_path):
        # First record some usage manually via the library
        import tokenmeter
        meter = tokenmeter.Meter(storage="sqlite", db_path=db_path)
        meter.tracker.record_manual(model="claude-sonnet-4-5", input_tokens=1000, output_tokens=500)

        result = runner.invoke(cli, ["--db", db_path, "usage"])
        assert result.exit_code == 0
        assert "Total spending:" in result.output
        assert "Total requests: 1" in result.output

    def test_usage_by_model(self, runner, db_path):
        import tokenmeter
        meter = tokenmeter.Meter(storage="sqlite", db_path=db_path)
        meter.tracker.record_manual(model="claude-sonnet-4-5", input_tokens=1000, output_tokens=500)
        meter.tracker.record_manual(model="gpt-4o", input_tokens=1000, output_tokens=500)

        result = runner.invoke(cli, ["--db", db_path, "usage", "--by", "model"])
        assert result.exit_code == 0
        assert "claude-sonnet-4-5" in result.output
        assert "gpt-4o" in result.output


class TestHistory:
    def test_history_empty(self, runner, db_path):
        result = runner.invoke(cli, ["--db", db_path, "history"])
        assert result.exit_code == 0
        assert "No usage records found." in result.output

    def test_history_with_records(self, runner, db_path):
        import tokenmeter
        meter = tokenmeter.Meter(storage="sqlite", db_path=db_path)
        meter.tracker.record_manual(model="claude-sonnet-4-5", input_tokens=1000, output_tokens=500)

        result = runner.invoke(cli, ["--db", db_path, "history"])
        assert result.exit_code == 0
        assert "claude-sonnet-4-5" in result.output
        assert "1,000" in result.output

    def test_history_limit(self, runner, db_path):
        import tokenmeter
        meter = tokenmeter.Meter(storage="sqlite", db_path=db_path)
        for _ in range(5):
            meter.tracker.record_manual(model="claude-sonnet-4-5", input_tokens=100, output_tokens=50)

        result = runner.invoke(cli, ["--db", db_path, "history", "--limit", "2"])
        assert result.exit_code == 0
        lines = [l for l in result.output.strip().split("\n") if "claude-sonnet" in l]
        assert len(lines) == 2


class TestBudget:
    def test_budget_set(self, runner, db_path, config_path, monkeypatch):
        monkeypatch.setattr("tokenmeter.cli.load_budgets", lambda: load_budgets(config_path))
        monkeypatch.setattr("tokenmeter.cli.save_budgets", lambda b: save_budgets(b, config_path))

        result = runner.invoke(cli, ["--db", db_path, "budget", "set", "10.00", "--period", "daily"])
        assert result.exit_code == 0
        assert "Budget set:" in result.output
        assert "$10.00" in result.output

        # Verify persistence
        budgets = load_budgets(config_path)
        assert len(budgets) == 1
        assert budgets[0].limit == Decimal("10.00")
        assert budgets[0].period == "daily"

    def test_budget_list_empty(self, runner, db_path, config_path, monkeypatch):
        monkeypatch.setattr("tokenmeter.cli.load_budgets", lambda: load_budgets(config_path))

        result = runner.invoke(cli, ["--db", db_path, "budget", "list"])
        assert result.exit_code == 0
        assert "No budgets configured." in result.output

    def test_budget_list_with_budgets(self, runner, db_path, config_path, monkeypatch):
        save_budgets([BudgetConfig(limit=Decimal("10.00"), period="daily", scope="global", action="warn")], config_path)
        monkeypatch.setattr("tokenmeter.cli.load_budgets", lambda: load_budgets(config_path))

        result = runner.invoke(cli, ["--db", db_path, "budget", "list"])
        assert result.exit_code == 0
        assert "10.00" in result.output
        assert "daily" in result.output

    def test_budget_remove(self, runner, db_path, config_path, monkeypatch):
        save_budgets([
            BudgetConfig(limit=Decimal("10.00"), period="daily", scope="global", action="warn"),
            BudgetConfig(limit=Decimal("100.00"), period="monthly", scope="global", action="block"),
        ], config_path)
        monkeypatch.setattr("tokenmeter.cli.load_budgets", lambda: load_budgets(config_path))
        monkeypatch.setattr("tokenmeter.cli.save_budgets", lambda b: save_budgets(b, config_path))

        result = runner.invoke(cli, ["--db", db_path, "budget", "remove", "0"])
        assert result.exit_code == 0
        assert "Removed budget:" in result.output

        budgets = load_budgets(config_path)
        assert len(budgets) == 1
        assert budgets[0].limit == Decimal("100.00")

    def test_budget_remove_invalid_index(self, runner, db_path, config_path, monkeypatch):
        monkeypatch.setattr("tokenmeter.cli.load_budgets", lambda: load_budgets(config_path))

        result = runner.invoke(cli, ["--db", db_path, "budget", "remove", "5"])
        assert result.exit_code != 0


class TestClear:
    def test_clear_with_confirmation(self, runner, db_path):
        import tokenmeter
        meter = tokenmeter.Meter(storage="sqlite", db_path=db_path)
        meter.tracker.record_manual(model="claude-sonnet-4-5", input_tokens=100, output_tokens=50)

        result = runner.invoke(cli, ["--db", db_path, "clear"], input="y\n")
        assert result.exit_code == 0
        assert "All usage data cleared." in result.output

        # Verify data is gone
        records = meter.tracker.get_records()
        assert len(records) == 0

    def test_clear_abort(self, runner, db_path):
        result = runner.invoke(cli, ["--db", db_path, "clear"], input="n\n")
        assert result.exit_code != 0  # Aborted

    def test_clear_with_yes_flag(self, runner, db_path):
        result = runner.invoke(cli, ["--db", db_path, "clear", "--yes"])
        assert result.exit_code == 0


class TestVersion:
    def test_version(self, runner):
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output


class TestConfig:
    def test_load_empty(self, tmp_path):
        path = str(tmp_path / "nonexistent.json")
        budgets = load_budgets(path)
        assert budgets == []

    def test_save_and_load(self, tmp_path):
        path = str(tmp_path / "config.json")
        budgets = [
            BudgetConfig(limit=Decimal("10.00"), period="daily", scope="global", action="warn"),
            BudgetConfig(limit=Decimal("50.00"), period="monthly", scope="user:alice", action="block"),
        ]
        save_budgets(budgets, path)
        loaded = load_budgets(path)
        assert len(loaded) == 2
        assert loaded[0].limit == Decimal("10.00")
        assert loaded[0].period == "daily"
        assert loaded[1].scope == "user:alice"
        assert loaded[1].action == "block"
