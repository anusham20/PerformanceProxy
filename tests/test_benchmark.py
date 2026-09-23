from performance_proxy.benchmark import run_policy_comparison


def test_policy_comparison_runs_and_returns_results():
    results = run_policy_comparison(max_size=8)

    assert len(results) >= 6
    for entry in results:
        assert "scenario" in entry
        assert "policy" in entry
        assert 0.0 <= entry["hit_rate"] <= 1.0
