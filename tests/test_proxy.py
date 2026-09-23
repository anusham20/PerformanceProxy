from performance_proxy.proxy import CacheProxy, ProxyRequest, ProxyResponse


def test_proxy_returns_fallback_response_for_cache_miss():
    proxy = CacheProxy(max_size=2)
    response = proxy.process(ProxyRequest(method="GET", path="/index.html"))

    assert response.status_code == 200
    assert response.body == "fallback response"
    assert response.cached is False


def test_proxy_returns_cached_response_for_hit():
    proxy = CacheProxy(max_size=2)
    proxy.process(ProxyRequest(method="GET", path="/home"))
    cached = proxy.process(ProxyRequest(method="GET", path="/home"))

    assert cached.cached is True
    assert proxy.metrics["hits"] >= 1


def test_proxy_store_retains_response_payload():
    proxy = CacheProxy(max_size=3)
    payload = ProxyResponse(status_code=201, body="created", headers={"X-Test": "true"})
    proxy.store("/resource", payload)

    loaded = proxy.process(ProxyRequest(method="GET", path="/resource"))
    assert loaded.status_code == 201
    assert loaded.headers["X-Test"] == "true"
