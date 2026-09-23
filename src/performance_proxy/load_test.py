from __future__ import annotations

import random
import statistics
import time
from collections import defaultdict

from .cache import LruCache, LfuCache


def generate_workload(size: int = 1000, hot_keys: int = 20) -> list[str]:
    keys = [f"k{i}" for i in range(hot_keys)]
    workload = []
    for _ in range(size):
        if random.random() < 0.7:
            workload.append(random.choice(keys))
        else:
            workload.append(f"k{random.randint(0, 200)}")
    return workload


def benchmark_policy(policy_name: str, workload: list[str], max_size: int = 64) -> dict:
    cache = LruCache(max_size=max_size) if policy_name == "lru" else LfuCache(max_size=max_size)

    start = time.perf_counter()
    for key in workload:
        value = cache.get(key)
        if value is None:
            cache.put(key, 1)
    elapsed = time.perf_counter() - start

    return {
        "policy": policy_name,
        "hit_rate": round(cache.hit_rate(), 4),
        "elapsed_seconds": round(elapsed, 6),
        "hits": cache.hits,
        "misses": cache.misses,
    }


def run_load_test() -> dict:
    workloads = [generate_workload(size=1000, hot_keys=20) for _ in range(5)]
    results = []
    for workload in workloads:
        for policy in ["lru", "lfu"]:
            results.append(benchmark_policy(policy, workload))

    grouped = defaultdict(list)
    for row in results:
        grouped[row["policy"]].append(row["hit_rate"])

    return {
        "average_hit_rates": {
            policy: round(statistics.mean(values), 4)
            for policy, values in grouped.items()
        },
        "samples": results,
    }


if __name__ == "__main__":
    print(run_load_test())
