from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Tuple


class LruCache:
    """Least-recently-used cache implementation."""

    def __init__(self, max_size: int = 16):
        if max_size <= 0:
            raise ValueError("max_size must be positive")
        self.max_size = max_size
        self._store: OrderedDict[str, Any] = OrderedDict()
        self.hits = 0
        self.misses = 0

    def get(self, key: str):
        if key not in self._store:
            self.misses += 1
            return None
        self.hits += 1
        value = self._store.pop(key)
        self._store[key] = value
        return value

    def put(self, key: str, value: Any) -> None:
        if key in self._store:
            self._store.pop(key)
        self._store[key] = value
        if len(self._store) > self.max_size:
            self._store.popitem(last=False)

    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return 0.0 if total == 0 else self.hits / total


class LfuCache:
    """Least-frequently-used cache implementation."""

    def __init__(self, max_size: int = 16):
        if max_size <= 0:
            raise ValueError("max_size must be positive")
        self.max_size = max_size
        self._store: Dict[str, Dict[str, Any]] = {}
        self.hits = 0
        self.misses = 0

    def get(self, key: str):
        entry = self._store.get(key)
        if entry is None:
            self.misses += 1
            return None
        self.hits += 1
        entry["freq"] += 1
        return entry["value"]

    def put(self, key: str, value: Any) -> None:
        if key in self._store:
            self._store[key]["value"] = value
            return
        if len(self._store) >= self.max_size:
            evict_key = min(self._store, key=lambda k: self._store[k]["freq"])
            self._store.pop(evict_key)
        self._store[key] = {"value": value, "freq": 1}

    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return 0.0 if total == 0 else self.hits / total


@dataclass
class AdaptiveCache:
    max_size: int = 16
    burst_threshold: int = 3
    access_count: int = 0
    _lru: LruCache = field(init=False)
    _lfu: LfuCache = field(init=False)

    def __post_init__(self):
        self._lru = LruCache(self.max_size)
        self._lfu = LfuCache(self.max_size)

    def _policy(self) -> str:
        return "lru" if self.access_count <= self.burst_threshold else "lfu"

    def get(self, key: str):
        self.access_count += 1
        policy = self._policy()
        if policy == "lru":
            return self._lru.get(key)
        return self._lfu.get(key)

    def put(self, key: str, value: Any) -> None:
        policy = self._policy()
        if policy == "lru":
            self._lru.put(key, value)
        else:
            self._lfu.put(key, value)

    def strategy_name(self) -> str:
        return self._policy()


def build_workload_sequence(pattern: str, size: int) -> List[str]:
    """Generate a synthetic workload pattern for benchmark analysis."""
    if pattern == "temporal":
        return [f"k{i % 8}" for i in range(size)]
    if pattern == "hotset":
        hot = [f"k{i}" for i in range(5)]
        return [hot[i % len(hot)] for i in range(size)] + [f"k{(i % 7) + 10}" for i in range(size // 3)]
    if pattern == "random":
        import random

        random.seed(42)
        return [f"k{random.randrange(0, 20)}" for _ in range(size)]
    return [f"k{i % 10}" for i in range(size)]


def evaluate_policy(policy_name: str, workload: Iterable[str], max_size: int = 16) -> Tuple[float, int, int]:
    cache = LruCache(max_size=max_size) if policy_name == "lru" else LfuCache(max_size=max_size)
    for key in workload:
        value = cache.get(key)
        if value is None:
            cache.put(key, 1)
    return cache.hit_rate(), cache.hits, cache.misses
