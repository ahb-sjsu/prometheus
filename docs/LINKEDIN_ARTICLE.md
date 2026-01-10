# 🔥 Announcing Prometheus v2.0: One Command to Analyze Any Codebase

**TL;DR**: I built a tool that measures whether your code is more complex than it needs to be. Now with one command, you can compare multiple GitHub repos on an interactive dashboard.

```bash
python olympus.py -f repos.txt -o comparison.html
```

---

## The Problem

Every engineer has inherited a codebase and thought: *"Why is this so complicated?"*

But "complicated" is subjective. What if we could **measure** it?

Turns out, we can. Physics and information theory give us the tools:

- **Shannon**: More bits = more error probability
- **Landauer**: Complex systems require more energy to maintain  
- **Reliability Engineering**: More components = exponentially lower reliability

**Simpler systems are more reliable. This isn't opinion—it's physics.**

---

## The Solution: Prometheus

Prometheus analyzes codebases and places them on a 2D fitness quadrant:

```
                    HIGH RESILIENCE
                          │
       💀 DEATHTRAP       │       🏰 FORTRESS
       (Complex +         │       (Over-engineered)
        Undefended)       │
    ──────────────────────┼──────────────────────
                          │
       🏠 GLASS HOUSE     │       🏚️ BUNKER
       (Fragile)          │       (Ideal ✓)
                          │
                    LOW RESILIENCE
```

**Goal**: Get to the BUNKER quadrant—simple AND resilient.

---

## What's New in v2.0

### 🆕 Olympus: The Orchestrator

One command to rule them all:

```bash
python olympus.py -f repos.txt -o comparison.html
```

**repos.txt:**
```
pallets/flask
psf/requests  
django/django
kelseyhightower/nocode
```

Olympus will:
1. Clone each repo
2. Run full analysis (complexity + resilience + theater detection)
3. Generate an interactive comparison dashboard

No manual steps. No JSON wrangling. Just results.

### 🆕 Hubris Integration

**Hubris** detects "resilience theater"—patterns that *look* defensive but are implemented wrong:

- Retry without backoff → thundering herd
- Circuit breakers without metrics → silent failures
- `except Exception: pass` → swallowed errors

The **Theater Ratio** tells you how much of your resilience is real vs. performance.

### 🆕 Beautiful Dashboards

- Bivariate color gradient (16×16 dithered)
- GitHub avatars for visual identification
- Interactive tooltips
- Built-in glossary
- Ranked comparison table

---

## Try It Yourself

**Compare some famous repos:**

```bash
# Clone the tool
git clone https://github.com/ahb-sjsu/prometheus.git
cd prometheus
pip install radon lizard

# Create a list
echo "pallets/flask
psf/requests
EnterpriseQualityCoding/FizzBuzzEnterpriseEdition" > repos.txt

# Run it
python olympus.py -f repos.txt -o comparison.html
```

See where **FizzBuzzEnterpriseEdition** (the world's most over-engineered FizzBuzz) lands on the quadrant! 😄

---

## The Philosophy

> "Complexity is the enemy of reliability."

Most "reliability engineering" is theater. Teams add retries, circuit breakers, and timeouts—but implement them wrong.

**The patterns look defensive. The implementation adds failure modes.**

Prometheus measures this. Hubris detects it.

---

## Links

📖 **README**: https://github.com/ahb-sjsu/prometheus/blob/main/README.md

💻 **GitHub**: https://github.com/ahb-sjsu/prometheus

---

## What's Next?

- CI/CD integration (fail builds if complexity exceeds threshold)
- Historical tracking (watch repos improve or decay over time)
- More language support

**Questions? Ideas? Let me know in the comments.**

---

*Built to answer: "Is this codebase more complex than it needs to be?"*

#SoftwareEngineering #CodeQuality #DevTools #Python #OpenSource #TechnicalDebt #Reliability
