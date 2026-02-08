# Spec: Storage Backends

## Motivation

Usage records need to persist across sessions for long-term tracking, but in-memory storage is appropriate for testing and short-lived scripts. A pluggable storage abstraction lets users choose the right tradeoff without changing application code.

## API Design

### `StorageBackend` (ABC)

- `save(record: UsageRecord) -> None`
- `query(provider=None, model=None, user_id=None, session_id=None, since=None, until=None, tags=None) -> list[UsageRecord]`
- `clear() -> None`

### `create_storage(backend, **kwargs) -> StorageBackend`

Factory function. Accepts `"memory"`, `"sqlite"`, `"jsonl"`, or a `StorageBackend` instance.

### Backends

**MemoryStorage:** Python list. No persistence, no dependencies.

**SQLiteStorage(db_path="~/.tokenmeter/usage.db"):**
- Uses Python built-in `sqlite3`
- Thread-safe (`threading.Lock`)
- Indexed on timestamp, provider, session_id, user_id
- Decimal values as TEXT, tags as JSON
- Auto-creates parent directories
- Schema migration: checks `PRAGMA table_info` and adds missing columns (e.g., `water_ml`)

**JsonFileStorage(path="~/.tokenmeter/usage.jsonl"):**
- JSON Lines format (one JSON object per line)
- Thread-safe (`threading.Lock`)
- Decimal values as strings
- Backward-compatible reads (missing fields get defaults)

## Data Model

All backends store/return `UsageRecord` objects with identical fields:
`id`, `timestamp`, `provider`, `model`, `input_tokens`, `output_tokens`, `cache_read_tokens`, `cache_write_tokens`, `input_cost`, `output_cost`, `total_cost`, `session_id`, `user_id`, `tags`, `is_estimate`, `water_ml`.

## Edge Cases

- Tag filtering: SQLite does tag filtering in Python (JSON field not easily queryable in SQL); JSON and memory backends also filter in Python.
- Empty database/file: `query()` returns `[]`.
- Missing columns in SQLite (schema migration): added via `ALTER TABLE ADD COLUMN` on init.
- Missing fields in JSON Lines (backward compat): `dict.get()` with defaults.

## Files

- `src/tokenmeter/storage/__init__.py`
- `src/tokenmeter/storage/_base.py`
- `src/tokenmeter/storage/memory.py`
- `src/tokenmeter/storage/sqlite.py`
- `src/tokenmeter/storage/json_file.py`
