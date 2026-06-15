"""Tiny thread-safe TTL cache (reused from mcp-factory).

Used to memoize the embedding model handle and repeated identical queries within
a short window so an agent calling several tools in one turn doesn't recompute.
"""
from __future__ import annotations

import threading
import time
from typing import Any, Callable

_lock = threading.Lock()
_store: dict[str, tuple[float, Any]] = {}


def get_or_fetch(key: str, ttl_s: float, fetch: Callable[[], Any]) -> Any:
    """Return a cached value if fresh, otherwise call `fetch()` and store it."""
    now = time.monotonic()
    with _lock:
        hit = _store.get(key)
        if hit is not None and (now - hit[0]) < ttl_s:
            return hit[1]
    value = fetch()
    with _lock:
        _store[key] = (time.monotonic(), value)
    return value


def clear() -> None:
    """Drop all cached entries (used by tests)."""
    with _lock:
        _store.clear()
