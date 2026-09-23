from __future__ import annotations

import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Dict, Iterable, List


@dataclass
class ProxyRequest:
    method: str
    path: str


@dataclass
class ProxyResponse:
    status_code: int
    body: str
    headers: Dict[str, str] = field(default_factory=dict)
    cached: bool = False


class CacheProxy:
    """A simplified HTTP proxy model for cache and request-tracing experiments."""

    def __init__(self, max_size: int = 8):
        self.max_size = max_size
        self._store: Dict[str, ProxyResponse] = {}
        self._lock = threading.Lock()
        self.metrics = {"requests": 0, "hits": 0, "misses": 0}

    def store(self, path: str, response: ProxyResponse) -> None:
        with self._lock:
            if len(self._store) >= self.max_size:
                self._store.pop(next(iter(self._store)))
            self._store[path] = response

    def process(self, request: ProxyRequest) -> ProxyResponse:
        with self._lock:
            self.metrics["requests"] += 1
            if request.path in self._store:
                self.metrics["hits"] += 1
                resp = self._store[request.path]
                resp.cached = True
                return resp

            self.metrics["misses"] += 1
            response = ProxyResponse(
                status_code=200,
                body="fallback response",
                headers={"X-Proxy": "default"},
                cached=False,
            )
            self._store[request.path] = response
            return response

    def simulate_parallel_load(self, requests: Iterable[ProxyRequest], workers: int = 4) -> List[ProxyResponse]:
        with ThreadPoolExecutor(max_workers=workers) as executor:
            return list(executor.map(self.process, requests))
