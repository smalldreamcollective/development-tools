# Spec: CLI

## Motivation

Developers need a way to interact with tokenmeter from the terminal — send prompts with cost tracking, estimate costs, view spending history, and manage budgets — without writing Python code.

## Commands

### `tokenmeter prompt`

Send a prompt to an AI model, display the response, and record cost/water.

- Accepts text as argument or from stdin
- `--model` (required), `--provider`, `--max-tokens` (default 1024), `--system`, `--tag key=value`, `--user-id`
- Output: response text, then `[model] in/out | Cost: $X.XX | Water: ~X.X mL`

### `tokenmeter estimate`

Estimate input cost and water without sending a request.

- Accepts text as argument or from stdin
- `--model` (required)
- Output: model, estimated tokens, estimated cost, estimated water

### `tokenmeter usage`

Show spending summary.

- `--by` (group by model/provider/user_id/session_id)
- `--provider`, `--model`, `--since`, `--until` filters
- Output: total spending, total water, total requests, total tokens

### `tokenmeter history`

Show individual usage records (most recent first).

- `--limit` (default 20), `--provider`, `--model`, `--user-id`, `--since`, `--until`
- Output: table with Timestamp, Model, In, Out, Cost, Water columns

### `tokenmeter budget set|list|remove`

- `set <limit>` with `--period`, `--scope`, `--action`
- `list` shows all budgets with current status
- `remove <index>` removes by index from list

### `tokenmeter models`

List supported models with pricing. `--provider` filter.

### `tokenmeter clear`

Delete all stored usage data. `--yes` skips confirmation.

## Global Options

- `--db` — path to SQLite database (default `~/.tokenmeter/usage.db`)
- `--version` — show version

## Data Model

- CLI uses SQLite storage exclusively.
- Budget config persisted in `~/.tokenmeter/config.json`.
- Provider inferred from model name; `--provider` overrides.

## Dependencies

Requires the `cli` extra (`click >= 8.1.0`). API calls require the respective provider SDK (`anthropic` or `openai`).

## Edge Cases

- No text argument and not piped -> `UsageError`
- Empty text -> `UsageError`
- Unknown provider from model name and no `--provider` -> `ClickException`
- Invalid date format -> `BadParameter`
- Invalid tag format (no `=`) -> `BadParameter`
- Budget remove with out-of-range index -> `ClickException`

## Files

- `src/tokenmeter/cli.py`
- `src/tokenmeter/config.py`
