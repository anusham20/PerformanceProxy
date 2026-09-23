import pytest

from performance_proxy.cache import AdaptiveCache, LfuCache, LruCache


def test_lru_cache_get_and_put():
    cache = LruCache(max_size=2)
    cache.put("a", 1)
    cache.put("b", 2)

    assert cache.get("a") == 1
    assert cache.get("b") == 2


def test_lru_cache_evicts_oldest_entry():
    cache = LruCache(max_size=2)
    cache.put("a", 1)
    cache.put("b", 2)
    cache.put("c", 3)

    assert cache.get("a") is None
    assert cache.get("b") == 2
    assert cache.get("c") == 3


def test_lfu_cache_evicts_least_frequently_used_entry():
    cache = LfuCache(max_size=2)
    cache.put("a", 1)
    cache.put("b", 2)
    cache.get("a")
    cache.get("a")
    cache.put("c", 3)

    assert cache.get("b") is None
    assert cache.get("a") == 1
    assert cache.get("c") == 3


def test_adaptive_cache_strategy_changes():
    cache = AdaptiveCache(max_size=3, burst_threshold=2)
    cache.put("a", 1)
    cache.put("b", 2)
    assert cache.strategy_name() in {"lru", "lfu"}


def test_invalid_cache_size_raises():
    with pytest.raises(ValueError):
        LruCache(max_size=0)
