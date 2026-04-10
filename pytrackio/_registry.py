from __future__ import annotations
import threading, time
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class MetricSummary:
    name: str
    calls: int
    errors: int
    avg_ms: float
    min_ms: float
    max_ms: float
    p95_ms: float
    p99_ms: float
    error_rate: float

class Counter:
    def __init__(self, name):
        self.name = name; self._v = 0; self._lock = threading.Lock()
    @property
    def value(self):
        with self._lock: return self._v
    def increment(self, n=1):
        with self._lock: self._v += n
    def decrement(self, n=1):
        with self._lock: self._v -= n
    def reset(self):
        with self._lock: self._v = 0

def _pct(s, p):
    if not s: return 0.0
    n = len(s)
    if n == 1: return s[0]
    i = (p/100.0)*(n-1); lo = int(i); hi = lo+1
    return s[-1] if hi >= n else s[lo]+(i-lo)*(s[hi]-s[lo])

class MetricsRegistry:
    def __init__(self):
        self._lock = threading.Lock()
        self._samples: Dict[str, List[float]] = {}
        self._errors: Dict[str, int] = {}
        self._counters: Dict[str, Counter] = {}
        self._start = time.monotonic()
    def record(self, name, ms, error=False):
        with self._lock:
            bucket = self._samples.setdefault(name, [])
            if len(bucket) >= 1000:
                bucket.pop(0)
            bucket.append(ms)
            self._errors.setdefault(name, 0)
            if error: self._errors[name] += 1
    def counter(self, name):
        with self._lock:
            if name not in self._counters: self._counters[name] = Counter(name)
            return self._counters[name]
    def summary(self, name):
        with self._lock:
            s = self._samples.get(name)
            return None if not s else self._build(name, list(s), self._errors.get(name,0))
    def all_summaries(self):
        with self._lock:
            return [self._build(n,list(s),self._errors.get(n,0)) for n,s in self._samples.items()]
    def all_counters(self):
        with self._lock: return {n:c.value for n,c in self._counters.items()}
    def _build(self, name, samples, errors):
        s=sorted(samples); c=len(s)
        return MetricSummary(name=name,calls=c,errors=errors,
            avg_ms=sum(s)/c,min_ms=s[0],max_ms=s[-1],
            p95_ms=_pct(s,95),p99_ms=_pct(s,99),
            error_rate=100.0*errors/c if c else 0.0)
    def reset(self):
        with self._lock:
            self._samples.clear(); self._errors.clear()
            self._counters.clear(); self._start=time.monotonic()
    def reset_metric(self, name: str):
        with self._lock:
            self._samples.pop(name, None)
            self._errors.pop(name, None)
    def uptime_seconds(self): return time.monotonic()-self._start

_REGISTRY = MetricsRegistry()
