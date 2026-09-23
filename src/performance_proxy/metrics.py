from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Metrics:
    requests: int = 0
    hits: int = 0
    misses: int = 0

    @property
    def hit_rate(self) -> float:
        if self.requests == 0:
            return 0.0
        return self.hits / self.requests

    @property
    def miss_rate(self) -> float:
        if self.requests == 0:
            return 0.0
        return self.misses / self.requests

    def update(self, hits: int = 0, misses: int = 0, requests: int = 0) -> None:
        self.hits += hits
        self.misses += misses
        self.requests += requests
