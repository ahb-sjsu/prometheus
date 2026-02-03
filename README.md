# Prometheus - Complexity Fitness Analyzer

[![CI](https://github.com/ahb-sjsu/prometheus/actions/workflows/ci.yml/badge.svg)](https://github.com/ahb-sjsu/prometheus/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/prometheus-analyzer.svg)](https://pypi.org/project/prometheus-analyzer/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A pragmatic tool for measuring whether a codebase is too complex for its task.

## Quick Start

```bash
pip install prometheus-analyzer

# Analyze a GitHub repo directly
prometheus https://github.com/pallets/flask

# Or use short form
prometheus pallets/flask

# Analyze local codebase
prometheus /path/to/your/code

# Outputs: prometheus_pallets_flask.html, prometheus_pallets_flask.json
```

## The Tools

| Tool | Named After | Purpose |
|------|-------------|---------|
| **prometheus.py** | Titan who gave fire to humanity | Combined orchestrator — 2D fitness quadrant |
| **shield_analyzer.py** (Aegis) | Shield of Zeus/Athena | Resilience pattern detector |
| **entropy_analyzer.py** | Shannon | Complexity metrics |
| **hubris.py** | Greek for "excessive pride" | Resilience theater detector — finds cargo-cult patterns |
| **olympus.py** | Home of the gods | Multi-repository comparison tool |

## Theoretical Basis

This tool implements a **pragmatic proof** that simpler systems are more reliable:

### Shannon's Information Theory
- Channel capacity limits how much information can be transmitted error-free
- Code is an information channel between intent and execution
- Higher complexity → more bits → higher error probability

### Thermodynamics (Landauer's Principle)  
- Maintaining information requires energy: `E = kT ln(2)` per bit
- Complex systems require more energy to maintain
- Complex systems have more failure modes and decay faster

### Reliability Engineering
- System reliability: `R = r₁ × r₂ × ... × rₙ`
- Each component with reliability `r < 1` reduces total reliability
- More components = exponentially lower reliability

### Kolmogorov Complexity
- The complexity of an object is the length of its shortest description
- Simpler descriptions are more compressible
- High compression ratio → redundancy → potential simplification

## Metrics Collected

### Per-File Metrics
- **Cyclomatic Complexity**: Number of independent paths through code
- **Cognitive Complexity**: Weighted by nesting depth (SonarQube-style)
- **Halstead Metrics**: Volume, difficulty, effort, estimated bugs
- **Maintainability Index**: Composite score (0-100)
- **Token Entropy**: Shannon entropy of token distribution
- **Compression Ratio**: `original_size / gzip_size`
- **Nesting Depth**: Maximum control flow nesting
- **Coupling**: Import count and dependencies

### Task Metrics (Estimated)
- Test file count and test case count
- Assertion density
- API endpoint count
- Function point estimate

### Fitness Ratios (The Key Outputs)
- **Complexity per Feature**: Is the code over-engineered?
- **LOC per Function Point**: Industry standard ~50
- **Bits per Feature**: Information-theoretic complexity density
- **Redundancy Ratio**: How much could be DRY'd out?

## Installation

```bash
pip install radon lizard
```

## Usage

### Analyze GitHub Repos

```bash
# Full URL
python prometheus.py https://github.com/django/django

# Short form (owner/repo)
python prometheus.py fastapi/fastapi

# Keep the cloned repo after analysis
python prometheus.py pallets/flask --keep
```

### Analyze Local Code

```bash
# Full analysis with HTML quadrant chart
python prometheus.py /your/codebase

# Just resilience (Aegis)
python shield_analyzer.py /your/codebase

# Just complexity (Shannon metrics)
python entropy_analyzer.py /your/codebase
```

### Output Files

Files are automatically named after the repo:
- `prometheus_<owner>_<repo>.html` — Visual quadrant report
- `prometheus_<owner>_<repo>.json` — Machine-readable data

Override with:
```bash
python prometheus.py owner/repo --html custom.html -o custom.json
```

## Thresholds

| Metric | Good | Medium | Poor |
|--------|------|--------|------|
| Cyclomatic Complexity (avg) | < 5 | 5-10 | > 10 |
| Maintainability Index | > 65 | 40-65 | < 40 |
| LOC per Function Point | < 50 | 50-150 | > 150 |
| Token Entropy | 4-6 | 6-8 | < 4 or > 8 |

## Interpreting Results

### Risk Levels

- **LOW**: Complexity well-matched to task. Reliable.
- **MEDIUM**: Trending toward excess. Monitor.
- **HIGH**: Over-complex. Elevated error rates expected.
- **CRITICAL**: Significantly over-engineered. Refactor before adding features.

### The Pragmatic Verdict

### From PyPI (Recommended)

```bash
# Basic installation
pip install prometheus-analyzer

# With security scanning (bandit)
pip install prometheus-analyzer[security]

# Full suite with all optional dependencies
pip install prometheus-analyzer[full]
```

After installation, use the commands:
```bash
prometheus pallets/flask
olympus -f repos.txt -o comparison.html
hubris pallets/flask --html hubris_report.html
```

### From Source

```bash
git clone https://github.com/yourusername/prometheus.git
cd prometheus
pip install -e .
```

### Manual Installation (Legacy)

If installing manually without the package:

```bash
# Minimal (Prometheus only)
pip install radon lizard

# Full Suite
pip install radon lizard bandit
```
This tool doesn't claim to measure "truth" — it measures **fitness**.

Per the pragmatist framework:
- We don't ask "is this codebase correct?"
- We ask "will this codebase reliably do its job?"

Physics and information theory tell us: **simpler systems win**.

## Limitations

- Task complexity estimation is heuristic (based on tests, endpoints, imports)
- Some metrics only available for Python (uses `radon`)
- Doesn't measure semantic complexity (bad names, confusing logic)
- Can't detect "essential" vs "accidental" complexity

## Extending

To add new languages or metrics:

1. Add extension mapping in `Extractor.LANGUAGE_EXTENSIONS`
2. Implement `_analyze_<language>()` method
3. Integrate additional static analysis tools

## Hubris: Resilience Theater Detector

Hubris analyzes codebases for **cargo-cult resilience patterns** — code that looks like it handles failures but doesn't actually work.

### Quadrant Classification

| Quadrant | Description |
|----------|-------------|
| **SIMPLE** | Few patterns, low complexity — appropriate for simple tasks |
| **BATTLE_HARDENED** | Many patterns, correctly implemented — production-ready |
| **OVERENGINEERED** | Too many patterns for the task — unnecessary complexity |
| **CARGO_CULT** | Many patterns, poorly implemented — false sense of security |

### What It Detects

- **Retry without backoff**: Retries that hammer services without delay
- **Missing timeouts**: Network calls without timeout configuration
- **Empty exception handlers**: `except: pass` and similar anti-patterns
- **Circuit breakers without metrics**: Breakers that can't report state
- **Library soup**: Too many resilience libraries without coherent strategy

### Architecture

```
hubris.py        # Main orchestrator
├── models.py    # Data classes (HubrisReport, etc.)
├── patterns.py  # Regex patterns for detection
├── detectors.py # Detection logic (RetryDetector, TimeoutDetector, etc.)
├── fp_filter.py # False positive filtering
├── design_patterns.py  # Design pattern anti-pattern detection
└── report.py    # HTML report generation
```

### Usage

```bash
# Analyze a codebase
python hubris.py /path/to/code

# Generate HTML report
python hubris.py /path/to/code --html report.html

# Export JSON
python hubris.py /path/to/code -o report.json
```

## Philosophy

> "Complexity is the enemy of reliability."

This tool exists because:
1. Simpler systems have fewer failure modes (physics)
2. Simpler systems are easier to understand (cognition)
3. Simpler systems are cheaper to maintain (economics)
4. We can *measure* simplicity (information theory)

Therefore: we can *measure* expected reliability.

That's the pragmatic proof.

---

*Built to answer: "Can you provide something I can measure?"*
