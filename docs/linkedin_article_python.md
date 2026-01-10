# I Analyzed 36 Python Frameworks for Resilience. Django Landed in Glass House.

**The follow-up analysis that made me question everything I thought I knew about "battle-tested" code.**

---

Last week, I shared an analysis of 18 open-source repositories that revealed [Netflix Hystrix scoring low on resilience](link-to-previous-article). The response was overwhelming — and the most common question was: *"What about the Python ecosystem?"*

So I ran Prometheus against 36 of Python's most popular frameworks and libraries. The results challenged my assumptions even more than the first batch.

---

## The Results at a Glance

| Quadrant | Count | What It Means |
|----------|-------|---------------|
| 🏰 BUNKER | 7 | Simple AND resilient (ideal) |
| 🏯 FORTRESS | 11 | Complex but defended |
| 🏠 GLASS HOUSE | 12 | Simple but fragile |
| ☠️ DEATHTRAP | 6 | Complex AND fragile |

---

## The Biggest Surprises

### 1. Django is a Glass House

**Django** — the 20-year-old "batteries included" framework trusted by Instagram, Spotify, and Mozilla — scored as **GLASS HOUSE**.

- Complexity Score: 55 (moderate)
- Resilience Score: 13 (low)
- Theater Ratio: 30.55 (high)

Before you close this tab: this doesn't mean Django is bad. It means Django delegates resilience to *you*.

Django handles routing, ORM, authentication, and admin brilliantly. But timeout handling? Retry logic? Circuit breakers for your database connections? That's your job.

The theater ratio of 30.55 is notable — it means for every correctly-implemented defensive pattern, there are ~30 that are incomplete or missing quality indicators like backoff and jitter.

### 2. FastAPI and Starlette: The Modern Stack's Blind Spot

**FastAPI** (GLASS HOUSE) and **Starlette** (DEATHTRAP) power a huge portion of modern Python APIs.

| Framework | Quadrant | Resilience | Theater |
|-----------|----------|------------|---------|
| FastAPI | GLASS HOUSE | 12 | 4.50 |
| Starlette | DEATHTRAP | 12 | ∞ |

Starlette's infinity theater ratio means it has defensive patterns, but *none* are fully correct by the analyzer's criteria.

The async Python ecosystem is young. These frameworks optimize for developer experience and performance. Resilience patterns are expected to come from your infrastructure layer — Kubernetes health checks, service meshes, or libraries like `tenacity`.

### 3. The HTTP Client Story Gets Worse

Remember how `requests` landed in DEATHTRAP last time? I tested its alternatives:

| Library | Quadrant | Resilience | Theater |
|---------|----------|------------|---------|
| requests | DEATHTRAP | 14 | 4.50 |
| httpx | DEATHTRAP | 12 | 23.50 |
| urllib3 | DEATHTRAP | 25 | 7.78 |
| aiohttp | GLASS HOUSE | 20 | 19.20 |

**Every major Python HTTP client is in DEATHTRAP or GLASS HOUSE.**

`httpx` was supposed to be the modern, "batteries included" replacement for requests. It has slightly *worse* resilience than `requests`, with a much higher theater ratio (23.50 vs 4.50).

`urllib3` — which underlies `requests` — actually scores better on resilience (25), possibly because it's closer to the metal and handles more edge cases directly.

### 4. cryptography: The Security Library with 1% Resilience

**pyca/cryptography** — the library that secures half of Python's TLS connections:

- Quadrant: GLASS HOUSE
- Resilience Score: **1**
- Theater Ratio: 40.00

A resilience score of 1 out of 100.

This makes sense when you think about it: cryptography is a *cryptographic primitive* library. It does one thing — encrypt and decrypt — and does it correctly. It's not trying to handle network failures or retry logic.

But it's a reminder: security ≠ resilience. A perfectly secure library can still be part of a fragile system.

### 5. The Winners: Who Actually Got It Right?

**BUNKER (Simple + Resilient):**
- **redis-py** (45 resilience) — database clients need to handle connection failures
- **SQLAlchemy** (35 resilience) — connection pooling forces you to think about failure
- **NumPy** (41 resilience) — surprising! perhaps because array operations are bounded
- **MongoDB driver** (39 resilience) — distributed database = must handle partitions
- **Sanic** (41 resilience) — async framework that took resilience seriously

**FORTRESS (Complex but Defended):**
- **Trio** (46 resilience) — structured concurrency done right
- **Flask** (41 resilience) — mature, battle-tested
- **Peewee** (39 resilience) — lightweight ORM with solid error handling
- **Click** (39 resilience) — CLI tools need graceful degradation
- **Typer** (41 resilience) — built on Click's solid foundation
- **RQ** (40 resilience) — job queues must handle worker failures

---

## The Pattern That Emerged

Looking across all 36 projects, a clear pattern emerges:

> **Libraries that handle I/O boundaries score higher on resilience.**

- Database drivers (redis-py, MongoDB, SQLAlchemy) — must handle connection failures
- Job queues (RQ, Celery sort-of) — must handle worker crashes
- CLI tools (Click, Typer) — must handle user interrupts gracefully

Meanwhile:

> **Libraries that focus on computation or API surface score lower.**

- Web frameworks (Django, FastAPI) — delegate I/O resilience to layers below
- HTTP clients (requests, httpx) — provide the mechanism, not the policy
- Data science (pandas, scikit-learn) — assume data is already loaded

This isn't a flaw. It's a **design boundary**.

---

## What This Means for Your Stack

### 1. Your Framework Won't Save You

Django, FastAPI, and Flask are excellent at what they do. But none of them will:
- Retry your failed database queries
- Circuit-break a failing microservice
- Timeout a hanging HTTP call

That's your application code's job.

### 2. The "Modern" Stack Isn't More Resilient

httpx and FastAPI are newer than requests and Django. They have better async support, type hints, and developer ergonomics.

They don't have better resilience defaults.

Don't assume new = improved in this dimension.

### 3. Database Clients Are Your Best Teachers

Want to see resilience done right? Read the source code of `redis-py` or the MongoDB driver. These libraries *must* handle:
- Connection timeouts
- Retry with backoff
- Connection pooling
- Failover to replicas

They're masterclasses in defensive programming because distributed databases punish you immediately when you get it wrong.

### 4. Add Resilience at the Boundaries

Since frameworks don't provide resilience, add it where your code touches external systems:

```python
# Instead of this:
response = httpx.get(url)

# Do this:
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, max=10))
def fetch_with_resilience(url):
    return httpx.get(url, timeout=30.0)
```

---

## Methodology Note

This analysis used static code pattern detection to identify:
- Retry implementations (with/without backoff, jitter, max attempts)
- Timeout configurations
- Exception handling quality
- Circuit breaker patterns

A low resilience score doesn't mean "buggy code." It means the codebase handles failures implicitly (letting exceptions propagate) rather than explicitly (catching, retrying, falling back).

Many libraries *intentionally* design this way — they provide building blocks, not policies.

---

## The Uncomfortable Truth

The Python ecosystem is built on a foundation of libraries that assume the happy path.

This is fine — until it isn't.

The question isn't whether your dependencies are "good" or "bad." The question is: **who owns resilience in your system?**

If it's not your framework, and it's not your HTTP client, and it's not your ORM...

It's you.

---

*What surprised you most about these results? Have you been burned by a "reliable" library that didn't handle failures the way you expected?*

---

**#Python #SoftwareEngineering #Resilience #Django #FastAPI #CodeQuality**
