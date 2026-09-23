from __future__ import annotations

import json
from pathlib import Path


def percent_improvement(baseline: float, optimized: float) -> float:
    if baseline == 0:
        raise ValueError("baseline value must be non-zero")
    return ((optimized - baseline) / baseline) * 100.0


def main() -> None:
    result_path = Path("results") / "cache_policy_comparison.json"
    if not result_path.exists():
        print("No benchmark JSON found. Run: python -m performance_proxy.benchmark")
        return

    with result_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    baseline = None
    best = None
    for item in data:
        if item.get("scenario") == "random" and item.get("policy") == "lru":
            baseline = float(item.get("hit_rate", 0.0))
        if item.get("scenario") == "random" and item.get("policy") == "lfu":
            best = float(item.get("hit_rate", 0.0))

    if baseline is not None and best is not None:
        gain = percent_improvement(baseline, best)
        print(f"LRU baseline hit rate: {baseline:.3f}")
        print(f"LFU optimized hit rate: {best:.3f}")
        print(f"Improvement: {gain:.2f}%")

    baseline_t = 550.0
    optimized_t = 740.0
    throughput_gain = percent_improvement(baseline_t, optimized_t)
    print(f"Example throughput improvement: {throughput_gain:.2f}%")


if __name__ == "__main__":
    main()
