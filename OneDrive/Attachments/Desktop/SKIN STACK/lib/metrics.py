"""
Metrics collection for Prometheus-style monitoring
"""
import time
from typing import Dict, List
from dataclasses import dataclass, field
from collections import defaultdict

@dataclass
class Metrics:
    """Simple in-memory metrics collector"""

    # Counters
    http_requests_total: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    redirect_cache_hits_total: int = 0
    redirect_cache_misses_total: int = 0

    # Histograms (store raw values for percentile calculation)
    http_request_duration_ms: List[float] = field(default_factory=list)
    redirect_duration_ms: List[float] = field(default_factory=list)

    def increment_request(self, method: str, path: str, status: int):
        """Increment request counter"""
        key = f"{method}_{path}_{status}"
        self.http_requests_total[key] += 1

    def record_duration(self, duration_ms: float, metric_type: str = "http"):
        """Record duration for histogram"""
        if metric_type == "http":
            self.http_request_duration_ms.append(duration_ms)
            # Keep only last 1000 entries to prevent memory growth
            if len(self.http_request_duration_ms) > 1000:
                self.http_request_duration_ms = self.http_request_duration_ms[-1000:]
        elif metric_type == "redirect":
            self.redirect_duration_ms.append(duration_ms)
            if len(self.redirect_duration_ms) > 1000:
                self.redirect_duration_ms = self.redirect_duration_ms[-1000:]

    def increment_cache_hit(self):
        """Increment cache hit counter"""
        self.redirect_cache_hits_total += 1

    def increment_cache_miss(self):
        """Increment cache miss counter"""
        self.redirect_cache_misses_total += 1

    def get_percentile(self, values: List[float], percentile: float) -> float:
        """Calculate percentile from list of values"""
        if not values:
            return 0
        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile / 100)
        return sorted_values[min(index, len(sorted_values) - 1)]

    def export_prometheus(self) -> str:
        """Export metrics in Prometheus format"""
        lines = []

        # Request counters
        lines.append("# HELP http_requests_total Total HTTP requests")
        lines.append("# TYPE http_requests_total counter")
        for key, count in self.http_requests_total.items():
            parts = key.split("_")
            if len(parts) >= 3:
                method = parts[0]
                status = parts[-1]
                path = "_".join(parts[1:-1])
                lines.append(f'http_requests_total{{method="{method}",path="{path}",status="{status}"}} {count}')

        # Cache metrics
        lines.append("# HELP redirect_cache_hits_total Total cache hits")
        lines.append("# TYPE redirect_cache_hits_total counter")
        lines.append(f"redirect_cache_hits_total {self.redirect_cache_hits_total}")

        lines.append("# HELP redirect_cache_misses_total Total cache misses")
        lines.append("# TYPE redirect_cache_misses_total counter")
        lines.append(f"redirect_cache_misses_total {self.redirect_cache_misses_total}")

        # Duration histograms
        if self.http_request_duration_ms:
            lines.append("# HELP http_request_duration_ms Request duration in milliseconds")
            lines.append("# TYPE http_request_duration_ms histogram")
            for percentile in [50, 90, 95, 99]:
                value = self.get_percentile(self.http_request_duration_ms, percentile)
                lines.append(f'http_request_duration_ms{{quantile="{percentile/100}"}} {value:.2f}')

        if self.redirect_duration_ms:
            lines.append("# HELP redirect_duration_ms Redirect duration in milliseconds")
            lines.append("# TYPE redirect_duration_ms histogram")
            for percentile in [50, 90, 95, 99]:
                value = self.get_percentile(self.redirect_duration_ms, percentile)
                lines.append(f'redirect_duration_ms{{quantile="{percentile/100}"}} {value:.2f}')

        return "\n".join(lines)

# Global metrics instance
metrics = Metrics()