from __future__ import annotations

from tokenmeter.storage._base import StorageBackend
from tokenmeter.storage.json_file import JsonFileStorage
from tokenmeter.storage.memory import MemoryStorage
from tokenmeter.storage.sqlite import SQLiteStorage


def create_storage(backend: str | StorageBackend = "memory", **kwargs: str) -> StorageBackend:
    """Factory for creating storage backends.

    Args:
        backend: "memory", "sqlite", "jsonl", or a StorageBackend instance.
        **kwargs: Passed to the storage backend constructor (e.g., db_path, path).
    """
    if isinstance(backend, StorageBackend):
        return backend
    if backend == "memory":
        return MemoryStorage()
    if backend == "sqlite":
        return SQLiteStorage(**kwargs)
    if backend == "jsonl":
        return JsonFileStorage(**kwargs)
    raise ValueError(f"Unknown storage backend: {backend!r}. Use 'memory', 'sqlite', or 'jsonl'.")
