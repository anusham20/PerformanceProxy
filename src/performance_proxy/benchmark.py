from __future__ import annotations

import json
from pathlib import Path

from .cache import build_workload_sequence, evaluate_policy


def run_policy_comparison(max_size: int = 32) -> list[dict]:
    scenarios = [
        ("temporal", build_workload_sequence("temporal", 200)),
        ("hotset", build_workload_sequence("hotset", 200)),
        ("random", build_workload_sequence("random", 200)),
    ]

    results: list[dict] = []
    for name, workload in scenarios:
        for policy in ["lru", "lfu"]:
            hit_rate, hits, misses = evaluate_policy(policy, workload, max_size=max_size)
            results.append({
                "scenario": name,
                "policy": policy,
                "hit_rate": round(hit_rate, 4),
                "hits": hits,
                "misses": misses,
            })

    output_path = Path("results") / "cache_policy_comparison.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    return results


def write_policy_plot(results: list[dict], output_path: str | Path = "results/cache_policy_comparison.png") -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    scenarios = sorted({x["scenario"] for x in results})
    policies = ["lru", "lfu"]
    fig, ax = plt.subplots(figsize=(8, 5))

    for policy in policies:
        values = [
            next(item["hit_rate"] for item in results if item["scenario"] == scenario and item["policy"] == policy)
            for scenario in scenarios
        ]
        ax.plot(scenarios, values, marker="o", label=policy.upper())

    ax.set_title("LRU vs LFU Cache Hit Rate by Workload")
    ax.set_xlabel("Workload")
    ax.set_ylabel("Hit Rate")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)
    return out_path


if __name__ == "__main__":
    results = run_policy_comparison()
    plot_path = write_policy_plot(results)
    print({"results": results, "plot": str(plot_path)})
