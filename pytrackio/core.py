from __future__ import annotations
import functools
import time
import inspect
from ._registry import _REGISTRY
from functools import wraps
from typing import List, Optional, Dict, Any
import json
import threading

DEFAULT_BUCKETS = [1, 5, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000]
_HISTOGRAM__REGISTRY: Dict[str, Dict[float, int]] = {}

def set_buckets(buckets: List[float]):
    """Global configuration for default buckets."""
    global DEFAULT_BUCKETS
    DEFAULT_BUCKETS = sorted(buckets)

def _record_histogram(metric_name: str, duration_ms: float, buckets: List[float]):
    """Finds the correct bucket and increments the count."""
    if metric_name not in _HISTOGRAM__REGISTRY:
        _HISTOGRAM__REGISTRY[metric_name] = {b: 0 for b in buckets}
        _HISTOGRAM__REGISTRY[metric_name][float("inf")] = 0
    
    for b in buckets:
        if duration_ms <= b:
            _HISTOGRAM__REGISTRY[metric_name][b] += 1
            return
    
    _HISTOGRAM__REGISTRY[metric_name][float("inf")] += 1

def track(func=None, *, name: str | None = None, histogram_buckets: List[float] | None = None, reset_after: int | None = None):
    def decorator(fn):
        metric_name = name or getattr(fn, "__qualname__", fn.__name__)
        active_buckets = sorted(histogram_buckets) if histogram_buckets else DEFAULT_BUCKETS
        _call_count = 0
        _call_lock = threading.Lock()
        if inspect.iscoroutinefunction(fn):
            @functools.wraps(fn)
            async def async_wrapper(*args, **kwargs):
                start = time.perf_counter()
                err = False  
                try:
                    return await fn(*args, **kwargs)
                except Exception as e:
                    err = True 
                    raise e
                finally:
                    nonlocal _call_count
                    duration = (time.perf_counter() - start) * 1000
                    _REGISTRY.record(metric_name, duration, err)
                    _record_histogram(metric_name, duration, active_buckets)
                    if reset_after is not None:
                        with _call_lock:
                            _call_count += 1
                            if _call_count >= reset_after:
                                _REGISTRY.reset_metric(metric_name)
                                _call_count = 0
            return async_wrapper

        @functools.wraps(fn)
        def sync_wrapper(*args, **kwargs):
            start = time.perf_counter()
            err = False 
            try:
                return fn(*args, **kwargs)
            except Exception as e:
                err = True
                raise e
            finally:
                nonlocal _call_count
                duration = (time.perf_counter() - start) * 1000
                _REGISTRY.record(metric_name, duration, err)
                _record_histogram(metric_name, duration, active_buckets)
                if reset_after is not None:
                    with _call_lock:
                        _call_count += 1
                        if _call_count >= reset_after:
                            _REGISTRY.reset_metric(metric_name)
                            _call_count = 0
        return sync_wrapper

    if func is None:
        return decorator
    return decorator(func)

def export_histogram(filepath: str | None = None):
    """
    Prints a formatted table of latency distributions and 
    optionally exports to a JSON file.
    """
    if not _HISTOGRAM__REGISTRY :
        print("No Histogram data recorded yet.")
        return
    for metric_name, buckets in _HISTOGRAM__REGISTRY.items():

        print(f"\nLatency Histogram for {metric_name}:")
        print("┌─────────────┬──────────┐")
        print("│ Bucket      │ Count    │")
        print("├─────────────┼──────────┤")

        prev_limit = 0
        for limit, count in buckets.items():
            if limit == float("inf"):
                label = f"{prev_limit}ms+"
            else:
                label = f"{prev_limit}-{limit}ms"
            
            print(f"| {label:<11} | {count:<8} |")
            if limit != float("inf"):
                prev_limit = limit
            
        print("└─────────────┴──────────┘")
    
    if filepath:
        export_data = {
            name: {str(k): v for k, v in b.items()} 
            for name, b in _HISTOGRAM__REGISTRY.items()
        }
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=4)
        print(f"Histogram exported to {filepath}")

            