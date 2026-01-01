# Prometheus

**Complexity Fitness Analyzer for Codebases**

*Named after the Titan who gave fire to humanity*

---

## The Thesis

**Simpler systems are more reliable.** This isn't opinion—it's physics:

- **Shannon's Information Theory**: More bits = more error probability
- **Thermodynamics (Landauer)**: Complex systems require more energy to maintain
- **Reliability Engineering**: R = r₁ × r₂ × ... × rₙ (more components = exponentially lower reliability)

Prometheus measures whether your codebase is more complex than it needs to be.

---

## Quick Start

```bash
pip install radon lizard

# Analyze a GitHub repo
python prometheus.py https://github.com/pallets/flask

# Short form
python prometheus.py pallets/flask

# Local codebase
python prometheus.py /path/to/your/code

# Full analysis with all tools
python prometheus.py pallets/flask --smells --security
```

---

## The Tools

| Tool | Named After | Purpose |
|------|-------------|---------|
| **prometheus.py** | Titan of forethought | Main orchestrator — 2D fitness quadrant |
| **hubris.py** | Greek concept of fatal pride | Resilience theater detector |
| **olympus.py** | Home of the gods | Multi-repo comparison dashboard |
| **shield_analyzer.py** (Aegis) | Shield of Zeus/Athena | Resilience pattern detector |
| **entropy_analyzer.py** | Shannon | Complexity metrics |
| **scent_analyzer.py** | Code smells | NIH patterns, staleness, freshness |
| **sentinel.py** | Security guard | Security vulnerability scanner |
| **oracle.py** | Delphi | LLM-assisted analysis |
| **benchmark.py** | — | Prediction accuracy testing |

---

## The Prometheus Quadrant

```
                    HIGH RESILIENCE
                          │
         FORTRESS         │         BUNKER
    (Over-engineered     │    (Ideal: Simple
     but defended)       │     and defended)
                         │
    ─────────────────────┼─────────────────────
                         │
         DEATHTRAP       │         GLASS HOUSE
    (Complex AND        │    (Simple but
     undefended)        │     fragile)
                         │
                    LOW RESILIENCE

Goal: Move toward BUNKER quadrant.
```

---

## Hubris: Resilience Theater Detector

**Core thesis**: "The complexity added by reliability patterns can introduce more failure modes than it prevents."

Hubris detects **cargo cult resilience**—patterns that look defensive but are implemented incorrectly:

- Retry without backoff (causes thundering herd)
- Retry without max attempts (infinite loops)
- Uncoordinated timeouts (retry_count × timeout > caller_timeout)
- Invisible circuit breakers (no metrics/logging)
- Broad exception swallowing (`except Exception: pass`)
- Untested fallbacks
- Library soup (multiple resilience libraries = complexity explosion)

### The Hubris Quadrant

```
                    HIGH QUALITY
                    (backoff, jitter, 
                    metrics, tested)
                         │
       OVERENGINEERED    │    BATTLE-HARDENED
       Complex but       │    Complex and
       probably works    │    correctly implemented
                         │
    ─────────────────────┼─────────────────────
                         │
       SIMPLE            │    CARGO CULT
       Crashes cleanly,  │    Has patterns but
       easy to fix       │    implemented wrong
                         │
                    LOW QUALITY
                    (naive retry, no 
                    metrics, untested)
```

### Usage

```bash
# Analyze resilience patterns
python hubris.py /path/to/codebase

# Generate HTML report
python hubris.py pallets/flask --html hubris_flask.html

# Output JSON for integration
python hubris.py . -o hubris_report.json
```

### Key Metric: Theater Ratio

```
Theater Ratio = patterns_detected / patterns_correct
```

- **1.0** = Perfect (all patterns correctly implemented)
- **1.5** = 50% cargo cult (half your resilience is theater)
- **∞** = All theater, no substance

---

## Olympus: Multi-Repo Comparison

Compare multiple repositories on a single Gartner-style quadrant chart.

### Usage

```bash
# Analyze several repos first
python prometheus.py pallets/flask -o flask.json
python prometheus.py django/django -o django.json
python prometheus.py fastapi/fastapi -o fastapi.json

# Run hubris on each (optional, enriches comparison)
python hubris.py pallets/flask -o hubris_flask.json
python hubris.py django/django -o hubris_django.json

# Generate comparison
python olympus.py flask.json django.json fastapi.json hubris_*.json -o comparison.html
```

### Output

Interactive HTML dashboard showing:
- All repos plotted on complexity vs. resilience quadrant
- Bubble size = theater ratio (larger = more cargo cult)
- Bubble color = Hubris assessment
- Ranked table with health scores
- Cargo cult warnings

---

## Full Analysis Pipeline

```bash
# Complete analysis of a repo
python prometheus.py owner/repo \
  --smells \           # Run scent analysis (freshness, NIH patterns)
  --security \         # Run sentinel (security vulnerabilities)
  --report \           # Generate detailed markdown report
  --dump               # Dump all raw data for further analysis
```

### Output Files

| File | Contents |
|------|----------|
| `prometheus_<repo>.html` | Visual quadrant report |
| `prometheus_<repo>.json` | Machine-readable data |
| `prometheus_<repo>_report.md` | Detailed technical report |
| `hubris_<repo>.html` | Resilience theater report |
| `scent_<repo>.json` | Code smell analysis |
| `sentinel_<repo>.json` | Security findings |
| `olympus_comparison.html` | Multi-repo dashboard |

---

## Metrics Collected

### Complexity (Entropy Analyzer)

| Metric | Description | Good | Bad |
|--------|-------------|------|-----|
| Cyclomatic Complexity | Independent paths through code | < 5 | > 10 |
| Cognitive Complexity | Weighted by nesting depth | < 10 | > 20 |
| Halstead Volume | Algorithmic complexity | < 1000 | > 5000 |
| Maintainability Index | Composite score | > 65 | < 40 |
| Token Entropy | Shannon entropy of tokens | 4-6 | > 8 |
| Compression Ratio | original / gzipped | > 3 | < 2 |

### Resilience (Shield Analyzer / Aegis)

| Pattern | Detection | Quality Check |
|---------|-----------|---------------|
| Retry | Loops, decorators, library usage | Backoff? Jitter? Max attempts? |
| Timeout | Socket, HTTP, DB timeouts | Coordinated? Reasonable values? |
| Circuit Breaker | Library patterns, state machines | Metrics? Fallback? Thresholds? |
| Rate Limiting | Token bucket, sliding window | Per-client? Graceful degradation? |
| Bulkhead | Thread pools, connection limits | Sized correctly? Monitored? |

### Freshness (Scent Analyzer)

| Rating | Criteria |
|--------|----------|
| 🟢 FRESH | Active development, modern patterns |
| 🟡 STALE | < 6 months since last commit |
| 🟠 MOLDY | 6-12 months, some outdated deps |
| 🔴 ROTTEN | > 1 year, deprecated patterns |

---

## Interpreting Results

### Risk Levels

| Level | Meaning | Action |
|-------|---------|--------|
| **LOW** | Complexity well-matched to task | Maintain |
| **MEDIUM** | Trending toward excess | Monitor |
| **HIGH** | Over-complex for requirements | Refactor |
| **CRITICAL** | Significantly over-engineered | Stop adding features, simplify |

### Quadrant Actions

| Quadrant | Situation | Priority Action |
|----------|-----------|-----------------|
| **BUNKER** | Simple and defended | Maintain. Maybe reduce redundant defenses. |
| **FORTRESS** | Complex but defended | Simplify. Resilience may be compensating for accidental complexity. |
| **GLASS HOUSE** | Simple but fragile | Add defenses: error handling, timeouts, retries. |
| **DEATHTRAP** | Complex and fragile | 🚨 Critical. Simplify OR add resilience immediately. |

---

## Library Mode

For analyzing libraries (vs applications), use `--library` flag:

```bash
python prometheus.py owner/lib --library
```

Adjusts scoring:
- Less penalty for missing timeouts/retries (libraries don't control caller context)
- More focus on API surface complexity
- Different test coverage expectations

---

## Benchmark Results

From `benchmark.py` testing against 10 diverse repositories:

```
Overall Prediction Accuracy: 69.8%

High confidence (≥70%): 75% accuracy
Correct quadrant calls: 7/10

Top learnings:
- Overconfident on very small repos (chalk/chalk)
- Rust Result<T,E> patterns not fully detected
- Test fixtures add noise (bat's jquery.js)
```

---

## Installation

### Core (Prometheus only)
```bash
pip install radon lizard
```

### Full Suite
```bash
pip install radon lizard bandit semgrep
```

### Optional (for Go analysis)
```bash
go install github.com/securego/gosec/v2/cmd/gosec@latest
```

---

## Philosophy

> "Complexity is the enemy of reliability."

This tool exists because:

1. **Simpler systems have fewer failure modes** (physics)
2. **Simpler systems are easier to understand** (cognition)
3. **Simpler systems are cheaper to maintain** (economics)
4. **We can measure simplicity** (information theory)

Therefore: **we can measure expected reliability.**

That's the pragmatic proof.

---

## The Hubris Insight

Most "reliability engineering" is theater. Teams add:
- Retries (without backoff → thundering herd)
- Circuit breakers (without metrics → invisible failures)
- Timeouts (uncoordinated → cascading failures)
- Multiple resilience libraries (→ complexity explosion)

**The patterns look defensive. The implementation adds failure modes.**

Hubris detects this. A high theater ratio means your resilience is performance, not protection.

---

## Extending

### Add Language Support

1. Add extension mapping in `Extractor.LANGUAGE_EXTENSIONS`
2. Implement `_analyze_<language>()` method
3. Add patterns to `RetryDetector.RETRY_PATTERNS`

### Add New Analyzers

Follow the pattern:
- `@dataclass` for report structure
- `analyze()` method returning report
- `save_report()` for JSON output
- `generate_*_html()` for visualization

---

## Related Work

- [Prometheus (monitoring)](https://prometheus.io) — Different project, same name, same spirit
- [radon](https://radon.readthedocs.io) — Python complexity metrics
- [lizard](https://github.com/terryyin/lizard) — Multi-language cyclomatic complexity
- [SonarQube](https://www.sonarqube.org) — Enterprise code quality (heavier weight)

---

## License

MIT

---

## Contributing

This is part of the Engineerism project. The thesis:

**It doesn't work until you test it. Ground state or it doesn't exist.**

Contributions that add measurable, testable improvements welcome.

---

*Built to answer: "Is this codebase more complex than it needs to be?"*
