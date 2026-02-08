# References: Storage Backends

Sources consulted during design and implementation of the storage backends.

## Language & Library References

- **Python `sqlite3` module documentation**
  https://docs.python.org/3/library/sqlite3.html
  Used for: SQLite backend implementation. Informed connection management, `Row` factory for dict-like access, `executescript` for schema creation, `PRAGMA table_info` for migration checks, and TEXT storage for Decimal precision.

- **JSON Lines format specification**
  https://jsonlines.org/
  Used for: the JSON Lines storage backend design. One JSON object per line enables append-only writes and line-by-line reads without loading the entire file.

- **Python `threading` module documentation**
  https://docs.python.org/3/library/threading.html
  Used for: thread safety in SQLite and JSON Lines backends via `threading.Lock`.

- **Python `json` module documentation**
  https://docs.python.org/3/library/json.html
  Used for: serializing tags dicts and JSON Lines records.

- **Python `pathlib` module documentation**
  https://docs.python.org/3/library/pathlib.html
  Used for: path handling, `expanduser()` for `~` expansion, `mkdir(parents=True)` for directory creation.

## Design Patterns

- **Strategy Pattern / Abstract Factory**
  General software architecture pattern. Used for: the `StorageBackend` ABC with `create_storage()` factory function, allowing runtime selection of backend via a string identifier.

- **SQLite ALTER TABLE ADD COLUMN for schema migration**
  https://www.sqlite.org/lang_altertable.html
  Used for: the migration strategy that adds new columns (like `water_ml`) to existing databases without requiring a full migration framework.

## Design Decisions

| Decision | Source |
|----------|--------|
| Decimal values stored as TEXT/string (not REAL/float) | Python decimal docs — avoids floating-point representation errors |
| Tags stored as JSON string in SQLite | sqlite3 has no native dict type; JSON is queryable enough with Python-side filtering |
| Tag filtering done in Python (not SQL) | JSON fields not easily queryable in SQLite WHERE clauses |
| `CREATE TABLE IF NOT EXISTS` + `ALTER TABLE ADD COLUMN` | SQLite ALTER TABLE docs — simple, no migration framework needed |
| Thread-safe via `threading.Lock` | Required for multi-threaded applications; sqlite3 connections aren't fully thread-safe |
| JSON Lines (not plain JSON array) | jsonlines.org — append-friendly, doesn't require reading entire file to add a record |
| Default paths under `~/.tokenmeter/` | Convention for user-level application data |
