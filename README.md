# ⚡ pytrackio

<div align="center">

### 🌐 Live Showcase & Docs

[![Showcase](https://img.shields.io/badge/showcase-live-7c6af7?style=flat-square)](https://danshu3007-lang.github.io/pytrackio/)

**[👉 View the full interactive showcase →](https://danshu3007-lang.github.io/pytrackio/)**

<br>

### 🎬 Demo Video

https://github.com/danshu3007-lang/pytrackio/raw/main/docs/demo.mp4

<br>

### 📸 Showcase Preview

<a href="https://danshu3007-lang.github.io/pytrackio/">
  <img src="https://danshu3007-lang.github.io/pytrackio/preview.png"
       alt="pytrackio showcase"
       onerror="this.style.display='none'"
       width="100%">
</a>

</div>

---



**The fastest way to add performance tracking to any Python project.**
One decorator. Zero dependencies. No servers. No config. Just answers.

[![Tests](https://github.com/danshu3007-lang/pytrackio/actions/workflows/tests.yml/badge.svg)](https://github.com/danshu3007-lang/pytrackio/actions)
[![PyPI version](https://img.shields.io/pypi/v/pytrackio?style=flat-square&color=blue)](https://pypi.org/project/pytrackio/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-zero-brightgreen?style=flat-square)](pyproject.toml)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square)](CONTRIBUTING.md)

---
```python
pip install pytrackio
```
```python
from pytrackio import track, timer, counter, report

@track
def process_order(order_id):
    ...

with timer("db_query"):
    results = db.execute(query)

counter("api_calls").increment()
report()
```
```
================================================================================
  pytrackio - Performance Report         uptime: 4.21s
================================================================================
  Name                         Calls      Avg      Min      Max      p95      p99  Errors
--------------------------------------------------------------------------------
  process_order                   42   120.34    98.10   310.50   290.10   308.40       -
  db_query                        18    45.20    40.10    89.30    87.20    89.10       -
--------------------------------------------------------------------------------
  Counters
--------------------------------------------------------------------------------
  api_calls: 42
================================================================================
```
#### Auto-reset after N calls

```python
@track(reset_after=100)
def process_order(order_id: int):
    ...
```

When `process_order` has been called 100 times, its metrics (call count, latency, errors) are automatically cleared and the counter starts fresh. Only that function's data is reset — all other tracked functions are unaffected. Both successful and errored calls count toward N. Thread-safe.

---

## Why pytrackio?

Sometimes you just need to know how fast your code runs, without setting up
servers, installing agents, or managing infrastructure.

pytrackio runs inside your process, requires zero setup, and gives you
real answers in seconds.

| Feature | pytrackio |
|---|---|
| Setup time | 30 seconds |
| External server required | None |
| Dependencies | 0 |
| Works in scripts and notebooks | Yes |
| p95 and p99 percentiles | Yes |
| Async support | Yes |
| Thread-safe | Yes |

---

## Installation
```bash
pip install pytrackio
```

Requirements: Python 3.10+ and zero external dependencies.

---

## Usage

### @track - decorate any function
```python
from pytrackio import track

@track
def fetch_user(user_id: int):
    ...

@track
async def send_notification(user_id: int):
    await mailer.send(...)

@track(name="payment_gateway")
def charge_card(amount: float):
    ...
```

Tracks call count, avg, min, max, p95, p99 latency, error count, and error rate.

---

### timer() - track any code block
```python
from pytrackio import timer

with timer("image_resize"):
    resized = resize_image(img, width=800)

async with timer("external_api"):
    result = await fetch_data()
```

---
## Tracking Methods
`@track` works out-of-the-box for instance, class, and static methods.

```python
class PaymentProcessor:
    @track
    def process(self, amount):  # Instance method
        ...

    @classmethod
    @track
    def get_supported_currencies(cls):  # Class method
        ...

    @staticmethod
    @track
    def validate_card(card_number):  # Static method
        ...
```


---
### counter() - named event counters
```python
from pytrackio import counter

counter("cache_hits").increment()
counter("retries").increment(3)
counter("queue_size").decrement()
counter("requests").reset()

print(counter("cache_hits").value)
```

---

### report() - print everything
```python
from pytrackio import report

report()
report(show_counters=False)
report(colour=False)
```

Returns the report as a string for logging or alerting.

---

### Latency Histograms
Track execution time distributions with customizable buckets:

```python
from pytrackio import track, export_histogram

@track(histogram_buckets=[10, 100, 500])
def my_function():
    ...

export_histogram() # Prints table to console
export_histogram("metrics.json") # Saves to JSON
```
---

### Export data
```python
from pytrackio import export_json, export_csv, export_dict

export_json("metrics.json")
export_csv("metrics.csv")
data = export_dict()
```

---

### Raw registry access
```python
from pytrackio import get_registry

registry = get_registry()

for s in registry.all_summaries():
    if s.error_rate > 5.0:
        print(f"{s.name} error rate: {s.error_rate:.1f}%")

registry.reset()
```

---

## Real-world example
```python
from pytrackio import track, timer, counter, report

@track
def get_product(product_id: int) -> dict:
    counter("db_reads").increment()
    return db.query(Product).get(product_id)

@track
async def checkout(cart_id: int) -> str:
    with timer("payment"):
        result = await payment_gateway.charge(cart_id)
    counter("orders_placed").increment()
    return result["order_id"]

report()
```

---

## Contributing

See CONTRIBUTING.md - PRs welcome.

---

## Changelog

See CHANGELOG.md for version history.

---

## Author

**Deepanshu** - Python Developer and Open Source Author.
Creator of pytrackio. Building tools that solve real problems for real developers.

---

## License

MIT - free to use, modify, and distribute.
