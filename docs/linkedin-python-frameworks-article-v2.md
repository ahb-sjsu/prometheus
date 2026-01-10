# Your HTTP Client Is a Liability: A Data-Driven Analysis of Python's Most Popular Libraries

**I analyzed 36 of Python's most popular libraries for resilience patterns. The results reveal a clear divide: database drivers are battle-hardened, HTTP clients are not. And yes, I included my own tool — the results weren't flattering.**

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

I pointed it at 36 popular Python libraries — including Prometheus itself. Here's what I found.

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

Prometheus accounts for this by analyzing **I/O boundary crossings** — network calls, database queries, file operations. Libraries with minimal I/O density are flagged as "resilience not applicable" rather than penalized.

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

---

## Introspection: What About Prometheus Itself?

In the interest of transparency, I ran Prometheus on itself. The results were humbling.

| Metric | Score | Assessment |
|--------|-------|------------|
| Complexity | 21/100 | ⚠️ Very complex |
| Resilience | 34/100 | Just below threshold |
| Quadrant | **DEATHTRAP** | Ouch |

**The tool doesn't give itself a free pass.** Prometheus landed in DEATHTRAP — the same quadrant as `requests` and `httpx`.

Why? The analysis found real problems:

- **Maintainability Index: 28** (healthy is >65)
- **Nesting depth: up to 13 levels** in some files
- **Cyclomatic complexity: 9-17** across core modules
- **Large monolithic files:** hubris.py is 122KB

The resilience score of 34 is actually just one point below the "high resilience" threshold of 35. For a CLI tool that primarily does file processing, that's not terrible. But the complexity score of 21 is an extreme outlier — 18 points below the next-lowest library (urllib3 at 39).

The hotspots tell the story:

| File | Maintainability | Issues |
|------|-----------------|--------|
| prometheus.py | 11.9 | CC 14.3, 6 levels deep |
| benchmark.py | 14.0 | CC 17.2, 5 levels deep |
| hubris.py | 17.9 | 9 levels deep |
| shield_analyzer.py | 18.8 | CC 11.7, 9 levels deep |
| entropy_analyzer.py | 33.5 | **13 levels deep** |

**The honest verdict:** Prometheus has accumulated significant technical debt. The tool accurately identifies its own need for refactoring — smaller functions, less nesting, better modularization. It's complex because analyzing code across six languages is genuinely hard, but that's an explanation, not an excuse.

If I were to improve it, I'd:
1. Break up the large files (especially hubris.py)
2. Reduce nesting depth in the analyzers
3. Extract common patterns into smaller, focused modules

The irony of a code quality tool having code quality issues isn't lost on me. But I'd rather ship an honest tool that identifies its own problems than a polished tool that lies about results.

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

**The five least resilient (I/O-bound libraries):**

1. Starlette (12) — FastAPI's foundation
2. FastAPI (12) — The popular kid
3. httpx (12) — Modern requests alternative
4. requests (14) — The classic, same problems
5. Tornado (15) — Async pioneer

**And in the spirit of honesty:**

- Prometheus (34) — DEATHTRAP, needs refactoring

The gap between the best and worst I/O-heavy libraries is 3x. That's not noise. That's signal.

---

*What resilience patterns do you enforce in your Python projects? Have you been bitten by missing timeouts? And yes — if you want to roast my code quality, the repo is open source. I've already done it myself.*

#Python #SoftwareEngineering #Resilience #OpenSource #Backend #DevOps #SRE #TechnicalDebt
