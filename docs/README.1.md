# 🔥 Prometheus

**Complexity Fitness Analyzer for Codebases**

*Named after the Titan who gave fire to humanity*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Copyright © 2025 Andrew H. Bond <andrew.bond@sjsu.edu>

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
python prometheus.py pallets/flask

# Compare multiple repos with one command
python olympus.py -f repos.txt -o comparison.html
```

**repos.txt:**
```
pallets/flask
psf/requests
django/django
```

That's it. Olympus clones, analyzes, and generates an interactive comparison dashboard.

---

## The Tools

| Tool | Named After | Purpose |
|------|-------------|---------|
| **olympus.py** | Home of the gods | 🆕 **Orchestrator** — one command to analyze everything |
| **prometheus.py** | Titan of forethought | Core analyzer — 2D fitness quadrant |
| **hubris.py** | Greek concept of fatal pride | Resilience theater detector |
| **prometheus_ui.py** | — | Shared UI components & bivariate color palette |
| **shield_analyzer.py** | Aegis (Shield of Zeus) | Resilience pattern detector |
| **entropy_analyzer.py** | Shannon | Complexity metrics |
| **scent_analyzer.py** | Code smells | NIH patterns, staleness, freshness |
| **sentinel.py** | Security guard | Security vulnerability scanner |
| **oracle.py** | Delphi | LLM-assisted analysis |

---

## 🆕 Olympus: One Command to Rule Them All

**New in v2.0**: Olympus is now the orchestrator. One command analyzes multiple repos:

```bash
python olympus.py -f repos.txt -o comparison.html
```

**What it does:**
1. Reads `repos.txt` (one `owner/repo` per line)
2. Clones each repo (shallow, cached in `.olympus_cache/`)
3. Runs **prometheus.py** (complexity + resilience)
4. Runs **hubris.py** (theater detection)
5. Generates interactive HTML comparison dashboard

**Output:**
```
======================================================================
OLYMPUS - Multi-Repository Comparison
======================================================================
  [clone] pallets/flask... OK
  [prometheus] pallets/flask... OK
  [hubris] pallets/flask... OK
  [clone] psf/requests... OK
  [prometheus] psf/requests... OK
  [hubris] psf/requests... OK

  HTML: comparison.html
```

### Features

- **Bivariate color gradient**: 16×16 dithered quadrant chart with distinct colors per quadrant
- **GitHub avatars**: Visual identification of each repo
- **Interactive tooltips**: Hover for details
- **Glossary**: Built-in definitions for all terms (FORTRESS, GLASS HOUSE, Theater Ratio, etc.)
- **Ranked table**: Sortable by health score, complexity, resilience, theater ratio
- **Caching**: Re-runs skip already-analyzed repos

### Flexible Input

```bash
# From file
python olympus.py -f repos.txt -o comparison.html

# Direct arguments
python olympus.py pallets/flask psf/requests -o comparison.html

# Mix remote and local
python olympus.py pallets/flask ./my-local-project -o comparison.html

# Existing JSON reports
python olympus.py prometheus_flask.json prometheus_django.json -o comparison.html
```

---

## The Prometheus Quadrant

```
                    HIGH RESILIENCE
                          │
       💀 DEATHTRAP       │       🏰 FORTRESS
    (Complex AND          │    (Over-engineered
     undefended)          │     but defended)
                          │
    ──────────────────────┼──────────────────────
                          │
       🏠 GLASS HOUSE     │       🏚️ BUNKER
    (Simple but           │    (Ideal: Simple
     fragile)             │     and defended)
                          │
                    LOW RESILIENCE

    ← HIGH COMPLEXITY          LOW COMPLEXITY →
```

**Goal**: Move toward the BUNKER quadrant (bottom-right).

### Quadrant Definitions

| Quadrant | Description | Action |
|----------|-------------|--------|
| 🏚️ **BUNKER** | Low complexity, high resilience. The ideal. | Maintain |
| 🏰 **FORTRESS** | Low complexity, low resilience. Hidden technical debt. | Add error handling |
| 🏠 **GLASS HOUSE** | High complexity, low resilience. Visibly fragile. | Simplify OR add resilience |
| 💀 **DEATHTRAP** | High complexity, high resilience. Over-engineered. | Simplify |

---

## Hubris: Resilience Theater Detector

**Core thesis**: *"The complexity added by reliability patterns can introduce more failure modes than it prevents."*

Hubris detects **cargo cult resilience**—patterns that look defensive but are implemented incorrectly:

| Anti-Pattern | Problem |
|--------------|---------|
| Retry without backoff | Thundering herd |
| Retry without max attempts | Infinite loops |
| Uncoordinated timeouts | Cascading failures |
| Invisible circuit breakers | Silent failures |
| `except Exception: pass` | Swallowed errors |
| Untested fallbacks | False confidence |
| Multiple resilience libraries | Complexity explosion |

### Theater Ratio

```
Theater Ratio = patterns_detected / patterns_correct
```

| Ratio | Meaning |
|-------|---------|
| **1.0** | Perfect — all patterns correctly implemented |
| **1.5** | 50% cargo cult |
| **∞** | All theater, no substance |

### Usage

```bash
# Standalone
python hubris.py pallets/flask --html hubris_report.html

# Integrated (via Olympus)
python olympus.py -f repos.txt  # Hubris runs automatically
```

---

## Installation

### Minimal (Prometheus only)
```bash
pip install radon lizard
```

### Full Suite
```bash
pip install radon lizard bandit
```

### Optional (Go analysis)
```bash
go install github.com/securego/gosec/v2/cmd/gosec@latest
```

---

## Metrics

### Complexity (Entropy Analyzer)

| Metric | Good | Bad |
|--------|------|-----|
| Cyclomatic Complexity | < 5 | > 10 |
| Cognitive Complexity | < 10 | > 20 |
| Maintainability Index | > 65 | < 40 |
| Token Entropy | 4-6 | > 8 |

### Resilience (Shield Analyzer)

| Pattern | Quality Checks |
|---------|----------------|
| Retry | Backoff? Jitter? Max attempts? |
| Timeout | Coordinated? Reasonable values? |
| Circuit Breaker | Metrics? Fallback? Thresholds? |
| Rate Limiting | Per-client? Graceful degradation? |

### Freshness (Scent Analyzer)

| Rating | Criteria |
|--------|----------|
| 🟢 FRESH | Active development, modern patterns |
| 🟡 STALE | < 6 months since last commit |
| 🟠 MOLDY | 6-12 months, outdated deps |
| 🔴 ROTTEN | > 1 year, deprecated patterns |

---

## Output Files

| File | Contents |
|------|----------|
| `comparison.html` | Olympus multi-repo dashboard |
| `prometheus_<repo>.html` | Single-repo quadrant report |
| `prometheus_<repo>.json` | Machine-readable metrics |
| `hubris_<repo>.html` | Resilience theater report |

---

## Example: Compare Famous Repos

**repos.txt:**
```
# Well-maintained
pallets/flask
psf/requests
encode/httpx

# Satirical (for fun)
kelseyhightower/nocode
EnterpriseQualityCoding/FizzBuzzEnterpriseEdition
auchenberg/volkswagen
```

```bash
python olympus.py -f repos.txt -o hall_of_fame.html
```

See where `FizzBuzzEnterpriseEdition` (the world's most over-engineered FizzBuzz) lands on the quadrant! 😄

---

## Philosophy

> "Complexity is the enemy of reliability."

This tool exists because:

1. **Simpler systems have fewer failure modes** (physics)
2. **Simpler systems are easier to understand** (cognition)
3. **Simpler systems are cheaper to maintain** (economics)
4. **We can measure simplicity** (information theory)

Therefore: **we can measure expected reliability.**

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

## Contributing

Contributions welcome. The thesis:

**It doesn't work until you test it. Ground state or it doesn't exist.**

---

## License

MIT

---

## Related Work

- [radon](https://radon.readthedocs.io) — Python complexity metrics
- [lizard](https://github.com/terryyin/lizard) — Multi-language cyclomatic complexity
- [SonarQube](https://www.sonarqube.org) — Enterprise code quality

---

*Built to answer: "Is this codebase more complex than it needs to be?"*
