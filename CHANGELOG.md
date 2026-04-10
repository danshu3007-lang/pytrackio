# Changelog

All notable changes to pytrackio will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

---
## [0.11.0] — 2026-04-10

### Added
- `reset_after=N` parameter on `@track` decorator — automatically clears metrics for that specific function after every N invocations (successful and errored calls both count). Only the decorated function's data is reset; the rest of the registry is untouched. Thread-safe via per-decorator lock.
- `reset_metric(name)` method on `MetricsRegistry` — resets samples and error count for a single named metric without affecting others.


## [0.3.0] — 2026-04-08

### Added
- **Latency Histograms**: Support for tracking execution time distributions using the `histogram_buckets` parameter in the `@track` decorator.
- **Export Utility**: Added `export_histogram()` to print formatted tables to the console and export data to JSON.
- **Global Configuration**: Added `set_buckets()` to define default latency boundaries globally.

### Changed
- **Refactor**: Consolidated tracking logic into a universal decorator in `core.py` to support sync, async, and class methods more efficiently.

## [0.10.1] — 2026-04-08

### Fixed
- Version number now consistent across `pyproject.toml` and `__init__.py`
- Memory leak in `MetricsRegistry` — `_samples` now capped at 1000 entries per metric

## [0.10.0] — 2026-04-08

### Added
- `__qualname__` based metric naming — class methods now report as `ClassName.method_name`
- Full support for `@classmethod`, `@staticmethod`, and instance methods via `@track`
- `all_counters()` method on registry for bulk counter access
- `export_dict()` includes counters in output

### Changed
- `@track` decorator refactored to use `_wrap()` helper for cleaner sync/async dispatch
- `report()` now returns the report string in addition to printing it

## [0.4.0] — 2026-04-07

### Added
- `async with timer()` support via `__aenter__` / `__aexit__`
- `export_jsonlines()` now includes counters as separate JSON lines
- `get_registry()` exported in public API via `__init__.py`
- `MetricsRegistry` and `MetricSummary` exported for type hinting

### Changed
- `timer()` correctly records errors when exceptions occur inside async blocks

## [0.3.0] — 2026-04-07

### Added
- **`export_jsonlines()`** — Added support for exporting metrics in JSON Lines format (one JSON object per line). This is designed for easy integration with log aggregation systems like Datadog, Loki, and Splunk.
- New **`tests/test_export_jsonlines.py`** to ensure format validity and file-writing reliability.
- Full support for tracking Class, Instance, and Static methods using `@track`.
- Automatic namespacing in reports (e.g., `ClassName.method_name`) via `__qualname__`.

### Changed
- Updated `README.md` with usage examples for JSON Lines exporting.
- Updated `CONTRIBUTING.md` to reflect the completion of the structured logging task.
- Refactored core decorator logic from `pytrackio/_track.py` to `pytrackio/core.py`.

## [0.2.0] — 2026-03-31

### Added
- **Async support** — `@track` now works transparently on `async def` functions
- **Async `timer()`** — `async with timer("name")` context manager support
- **p95 and p99 percentile latency** — shown in `report()` and all export formats
- **`export_json()`** — serialize all metrics and counters to JSON string
- **`export_csv()`** — serialize metrics to CSV format (p95/p99 included)
- **`export_dict()`** — return metrics as a plain Python dictionary
- `Summary.percentile(p)` — compute arbitrary percentile from raw durations
- `Summary.p95_ms` and `Summary.p99_ms` properties
- `report(output=False)` — return report as string without printing

### Changed
- `report()` table now includes `p95 ms` and `p99 ms` columns
- `pyproject.toml` updated to v0.2.0 with expanded classifiers
- README fully rewritten with async examples, export docs, comparison table
- Author bio updated to reflect production-grade open source work

### Fixed
- `timer()` now correctly records errors when exceptions occur inside the block

---

## [0.1.0] — 2026-01-01

### Added
- `@track` decorator for sync functions
- `timer()` synchronous context manager
- `counter()` named integer counters
- `report()` formatted terminal output
- `get_registry()` for raw metric access
- Zero external dependencies
- Thread-safe `MetricsRegistry` with `threading.Lock`
- MIT License, CONTRIBUTING, CODE_OF_CONDUCT
- CI/CD via GitHub Actions
- Published to PyPI
