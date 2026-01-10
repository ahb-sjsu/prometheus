# Your HTTP Client Is a Liability: A Data-Driven Analysis of Python's Most Popular Libraries

**I analyzed 35 of Python's most popular libraries for resilience patterns. The results reveal a clear divide: database drivers are battle-hardened, HTTP clients are not.**

---

We all have opinions about which Python libraries are "production-ready." But opinions aren't data. So I built a tool to find out.

Prometheus analyzes codebases for two dimensions:

1. **Complexity Score** (0-100) — Higher means simpler, more maintainable code
2. **Resilience Score** (0-100) — Higher means better error handling, timeouts, retries, and failure recovery

These map to four quadrants:

- **BUNKER** — Simple and well-defended (the goal)
- **FORTRESS** — Complex but well-defended
- **GLASS HOUSE** — Simple but fragile
- **DEATHTRAP** — Complex AND fragile

I pointed it at 35 popular Python libraries. Here's what I found.

---

## The Good News: Database Drivers Get It Right

If you're connecting to a database, the Python ecosystem has your back:

| Library | Quadrant | Resilience |
|---------|----------|------------|
| redis-py | BUNKER | 45/100 |
| peewee | FORTRESS | 39/100 |
| pymongo | BUNKER | 39/100 |
| SQLAlchemy | BUNKER | 35/100 |

These libraries handle connection pooling, timeouts, retries, and error recovery. They've learned from years of production incidents that database connections fail, and they're prepared for it.

**redis-py scored the second-highest resilience of any library tested** (45/100). When your library's job is to talk to an external service over a network, this is exactly what you want to see.

---

## The Bad News: HTTP Clients Are a Different Story

Now look at how we make HTTP calls:

| Library | Quadrant | Resilience |
|---------|----------|------------|
| urllib3 | DEATHTRAP | 25/100 |
| aiohttp | GLASS HOUSE | 20/100 |
| requests | DEATHTRAP | 14/100 |
| httpx | DEATHTRAP | 12/100 |

**Three of the four most popular HTTP clients landed in DEATHTRAP** — the worst possible quadrant.

The `requests` library — with 52,000 GitHub stars, downloaded millions of times per day — has a resilience score of 14. It famously has no default timeout. Every `requests.get()` call without an explicit timeout is a production incident waiting to happen.

`httpx`, the modern async alternative that was supposed to fix these problems? Resilience score: 12. Same quadrant: DEATHTRAP.

This isn't an indictment of the maintainers. These are excellent, well-maintained libraries. But their design philosophy prioritizes simplicity and flexibility over safety defaults. That's a choice — and it pushes the resilience burden onto every application developer.

---

## Web Frameworks: A Tale of Two Philosophies

The results for web frameworks were revealing:

| Framework | Quadrant | Resilience |
|-----------|----------|------------|
| Flask | BUNKER | 41/100 |
| Sanic | BUNKER | 41/100 |
| Bottle | BUNKER | 36/100 |
| Tornado | GLASS HOUSE | 15/100 |
| Django | GLASS HOUSE | 13/100 |
| Falcon | GLASS HOUSE | 13/100 |
| FastAPI | GLASS HOUSE | 12/100 |
| Starlette | DEATHTRAP | 12/100 |

**Flask scored over 3x higher than Django on resilience.**

Why? Flask is deliberately minimal. It delegates I/O handling to the WSGI server and lets you choose your own database libraries. Django does more internally — ORM, caching, sessions, email — which means more code that needs defensive patterns.

The Starlette result is notable because **FastAPI is built on Starlette**. Starlette landed in DEATHTRAP (C:41, R:12) while FastAPI landed in GLASS HOUSE (C:73, R:12). Same resilience, but FastAPI's cleaner architecture pushed it out of the danger zone on complexity.

---

## The Standout: Trio

One library stood above all others:

| Library | Quadrant | Resilience |
|---------|----------|------------|
| **Trio** | FORTRESS | **46/100** |

Trio scored the **highest resilience of any library tested**. This isn't surprising to anyone who knows the project — Trio was designed from the ground up around structured concurrency and explicit error handling. Its creator, Nathaniel J. Smith, has written extensively about why async Python needs better primitives for managing failure.

The data validates the philosophy: when you design for correctness first, resilience follows.

---

## What About Libraries That Don't Need Resilience?

Fair question. A JSON parser doesn't need retry logic. A progress bar doesn't need circuit breakers.

Prometheus accounts for this by analyzing **I/O boundary crossings** — network calls, database queries, file operations. Libraries with minimal I/O are flagged as "resilience not applicable" rather than penalized.

But here's the thing: **HTTP clients and web frameworks DO cross I/O boundaries. That's their entire job.** When these libraries score poorly on resilience, it's not a measurement error — it's a finding.

---

## The Uncomfortable Question

Why do database drivers handle failure gracefully while HTTP clients don't?

My theory: **database connections fail constantly**, and the pain is immediate. A dropped Postgres connection crashes your web request right now. So database libraries evolved timeout handling, connection pooling, and retry logic.

HTTP calls fail differently. A missing timeout doesn't crash — it hangs. The request might eventually complete, or the process might get killed by a load balancer 30 seconds later. The failure mode is silent, and silent failures don't drive library design decisions.

---

## What This Means For You

**1. Always set timeouts on HTTP calls.** Always. Every time. No exceptions.

```python
# Not this
response = requests.get(url)

# This
response = requests.get(url, timeout=(3.05, 27))
```

**2. Wrap external calls.** Don't trust library defaults. Add your own retry logic, circuit breakers, and timeout handling at the application layer.

**3. Consider your framework's I/O surface.** If you're using Django, you're trusting Django's ORM, cache backend, session store, and email handling to fail gracefully. If you're using Flask, you're choosing those components yourself — which means you're responsible for their resilience.

**4. Look at Trio.** If you're doing async Python and resilience matters, Trio's design philosophy is worth understanding — even if you don't adopt it wholesale.

---

## The Methodology

Prometheus measures resilience patterns including:

- Error handling coverage (try/except density, specific vs. bare exceptions)
- Timeout configurations on network and database calls
- Retry patterns (decorators, exponential backoff, jitter)
- Circuit breaker implementations
- Observability hooks (logging, metrics, tracing)

The complexity score combines cyclomatic complexity, maintainability index, and hotspot analysis.

Libraries are classified based on thresholds calibrated against industry benchmarks:
- Resilience ≥ 35 = "high resilience"
- Complexity ≥ 50 = "low complexity" (simpler code)

Full analysis available at the Prometheus repository.

---

## Introspection: What About Prometheus Itself?

In the interest of transparency, I ran Prometheus on itself.

| Metric | Score |
|--------|-------|
| Complexity | 21/100 |
| Resilience | N/A |
| Quadrant | **FORTRESS** |

The tool doesn't give itself a free pass. A complexity score of 21 means Prometheus is genuinely complex code — and it is. Parsing ASTs across six languages, running pattern detection, calculating entropy metrics... that's inherently complicated work.

The resilience score shows N/A because Prometheus is primarily a file-processing tool with minimal network I/O. It reads source files, analyzes them, and writes reports. The resilience patterns we measure (timeouts, retries, circuit breakers) apply to network-bound code, not local file processing.

**The honest verdict:** Prometheus lands in FORTRESS — complex but functional. Not the BUNKER I'd aim for, but at least it's not a GLASS HOUSE analyzing other people's glass houses.

If I were to improve it, I'd focus on reducing complexity through better modularization. The resilience score is appropriately N/A for a CLI analysis tool.

---

## The Bottom Line

The Python ecosystem has a resilience gap. Database drivers learned from decades of connection failures. HTTP clients haven't caught up.

This isn't about blame. The maintainers of `requests` and `httpx` have made reasonable design choices. But those choices push resilience responsibility onto every developer who uses the library.

The data is clear: if you're making HTTP calls in production, the library won't save you. You need to save yourself.

---

**The five most resilient Python libraries tested:**

1. Trio (46) — Async done right
2. redis-py (45) — Battle-tested database driver  
3. Flask (41) — Minimal by design
4. Sanic (41) — Async web framework
5. NumPy (41) — Surprisingly defensive

**The five least resilient:**

1. cryptography (1) — CPU-bound, low I/O (expected)
2. orjson (3) — Pure parsing (expected)
3. Pydantic (10) — Validation library
4. Starlette (12) — FastAPI's foundation
5. FastAPI (12) — The popular kid

The gap between the best and worst I/O-heavy libraries is 3x. That's not noise. That's signal.

---

*What resilience patterns do you enforce in your Python projects? Have you been bitten by missing timeouts? I'd love to hear your war stories in the comments.*

#Python #SoftwareEngineering #Resilience #OpenSource #Backend #DevOps #SRE
