from performance_proxy.metrics import Metrics


def test_metrics_hit_rate_and_miss_rate():
    metrics = Metrics(requests=10, hits=7, misses=3)
    assert metrics.hit_rate == 0.7
    assert metrics.miss_rate == 0.3


def test_metrics_update_adds_values():
    metrics = Metrics()
    metrics.update(hits=2, misses=3, requests=5)
    assert metrics.hits == 2
    assert metrics.misses == 3
    assert metrics.requests == 5
