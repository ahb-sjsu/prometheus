#!/usr/bin/env python3
"""
Prometheus - Combined Complexity & Resilience Fitness Analyzer
===============================================================

Named after the Titan who gave fire (technology) to humanity.

Combines:
- Entropy analysis (from Shannon/thermodynamics)
- Resilience patterns (from SRE principles)

Produces a 2D fitness map:

    HIGH COMPLEXITY
          │
          │   DEATHTRAP        │        FORTRESS
          │   (Complex AND     │   (Over-engineered
          │    undefended)     │    but defended)
          │                    │
          ├────────────────────┼────────────────────
          │                    │
          │   GLASS HOUSE      │        BUNKER
          │   (Simple but      │   (Ideal: Simple
          │    fragile)        │    and defended)
          │                    │
    LOW COMPLEXITY ────────────┴──────────────────→
                          LOW              HIGH
                            RESILIENCE

The goal: Move toward BUNKER quadrant (bottom-right).
"""

import json
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

# Import our analyzers
from .entropy_analyzer import ComplexityFitnessPipeline
from .shield_analyzer import Aegis


def clone_github_repo(url: str, target_dir: str = None) -> tuple[str, str]:
    """
    Clone a GitHub repository and return (local_path, repo_name).

    Accepts formats:
    - https://github.com/owner/repo
    - https://github.com/owner/repo.git
    - git@github.com:owner/repo.git
    - owner/repo (assumes GitHub)
    """
    # Handle short form: owner/repo
    if re.match(r"^[\w\-]+/[\w\-\.]+$", url):
        url = f"https://github.com/{url}"

    # Handle SSH format
    if url.startswith("git@"):
        # git@github.com:owner/repo.git -> https://github.com/owner/repo
        match = re.match(r"git@github\.com:(.+?)(?:\.git)?$", url)
        if match:
            url = f"https://github.com/{match.group(1)}"

    # Extract repo name
    parsed = urlparse(url)
    path_parts = parsed.path.strip("/").replace(".git", "").split("/")

    if len(path_parts) >= 2:
        owner = path_parts[-2]
        repo = path_parts[-1]
        repo_name = f"{owner}_{repo}"
    else:
        repo_name = path_parts[-1] if path_parts else "unknown_repo"

    # Create target directory
    if target_dir is None:
        target_dir = tempfile.mkdtemp(prefix=f"prometheus_{repo_name}_")

    clone_path = Path(target_dir) / repo_name

    print(f"[CLONE] Cloning {url}...")
    print(f"        Target: {clone_path}")

    # Clone with depth 1 for speed
    try:
        result = subprocess.run(
            ["git", "clone", "--depth", "1", url, str(clone_path)],
            capture_output=True,
            text=True,
            timeout=120,
        )

        if result.returncode != 0:
            error_msg = result.stderr.strip()
            if "unable to access" in error_msg or "CONNECT tunnel" in error_msg:
                raise RuntimeError(
                    "Cannot access GitHub. Network may be restricted.\n"
                    "Try cloning the repo locally first, then run:\n"
                    "  python prometheus.py /path/to/local/clone"
                )
            raise RuntimeError(f"Git clone failed: {error_msg}")

        print("        Done!")
        return str(clone_path), repo_name

    except subprocess.TimeoutExpired:
        raise RuntimeError("Git clone timed out after 120 seconds")
    except FileNotFoundError:
        raise RuntimeError("Git is not installed or not in PATH")


def is_github_url(path: str) -> bool:
    """Check if the path looks like a GitHub URL."""
    github_patterns = [
        r"^https?://github\.com/",
        r"^git@github\.com:",
        r"^[\w\-]+/[\w\-\.]+$",  # owner/repo format
    ]
    return any(re.match(p, path) for p in github_patterns)


@dataclass
class GitHubMetadata:
    """Metadata fetched from GitHub API."""

    name: str = ""
    full_name: str = ""
    description: str = ""
    stars: int = 0
    forks: int = 0
    language: str = ""
    topics: list = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""
    open_issues: int = 0
    license: str = ""
    url: str = ""


def fetch_github_metadata(repo_path: str) -> GitHubMetadata:
    """Fetch metadata from GitHub API for a repo."""
    import urllib.request

    # Extract owner/repo from various formats
    if "github.com" in repo_path:
        match = re.search(r"github\.com[/:]([^/]+)/([^/\.]+)", repo_path)
        if match:
            owner, repo = match.groups()
        else:
            return GitHubMetadata()
    elif "/" in repo_path and not repo_path.startswith("/"):
        parts = repo_path.split("/")
        owner, repo = parts[0], parts[1].replace(".git", "")
    else:
        return GitHubMetadata()

    try:
        api_url = f"https://api.github.com/repos/{owner}/{repo}"
        req = urllib.request.Request(api_url, headers={"User-Agent": "Prometheus/1.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())

            return GitHubMetadata(
                name=data.get("name", ""),
                full_name=data.get("full_name", ""),
                description=data.get("description", "") or "",
                stars=data.get("stargazers_count", 0),
                forks=data.get("forks_count", 0),
                language=data.get("language", "") or "",
                topics=data.get("topics", []),
                created_at=data.get("created_at", ""),
                updated_at=data.get("updated_at", ""),
                open_issues=data.get("open_issues_count", 0),
                license=(data.get("license", {}).get("spdx_id", "") if data.get("license") else ""),
                url=data.get("html_url", ""),
            )
    except Exception:
        return GitHubMetadata(name=repo, full_name=f"{owner}/{repo}")


@dataclass
class PrometheusReport:
    """Combined fitness report."""

    codebase_path: str
    timestamp: str

    # GitHub metadata (optional)
    github: GitHubMetadata = field(default_factory=GitHubMetadata)

    # Complexity metrics (from pipeline)
    complexity_risk: str = ""
    complexity_score: float = 0.0  # Lower is better (inverted for quadrant)
    loc_per_function_point: float = 0.0
    avg_cyclomatic: float = 0.0
    entropy: float = 0.0

    # Resilience metrics (from aegis)
    shield_rating: str = ""
    resilience_score: float = 0.0  # Higher is better

    # Combined assessment
    quadrant: str = ""
    quadrant_description: str = ""
    fitness_verdict: str = ""

    # Action items
    priorities: list = field(default_factory=list)

    # Raw reports
    complexity_report: dict = None
    resilience_report: dict = None


class Prometheus:
    """
    The Fire-Bringer - Combined fitness analyzer.

    Measures both complexity (liability) and resilience (defense)
    to produce actionable guidance.

    Accepts local paths or GitHub URLs:
    - /path/to/codebase
    - https://github.com/owner/repo
    - owner/repo
    """

    QUADRANTS = {
        "BUNKER": {
            "name": "BUNKER",
            "description": "Low complexity, high resilience. The ideal state.",
            "emoji": "🏰",
            "action": "Maintain current practices. Consider if any resilience measures are redundant.",
        },
        "FORTRESS": {
            "name": "FORTRESS",
            "description": "High complexity, high resilience. Defended but over-engineered.",
            "emoji": "🏯",
            "action": "Simplify where possible. The resilience may be compensating for accidental complexity.",
        },
        "GLASS_HOUSE": {
            "name": "GLASS HOUSE",
            "description": "Low complexity, low resilience. Simple but fragile.",
            "emoji": "🏠",
            "action": "Add defensive patterns: error handling, timeouts, retries. Complexity will increase but reliability will improve.",
        },
        "DEATHTRAP": {
            "name": "DEATHTRAP",
            "description": "High complexity, low resilience. The worst state.",
            "emoji": "💀",
            "action": "Critical: Either simplify dramatically or add resilience immediately. Failures are likely and debugging will be difficult.",
        },
    }

    def __init__(self, codebase_path: str, library_mode: bool = False):
        self.original_path = codebase_path
        self.cloned = False
        self.temp_dir = None
        self.library_mode = library_mode

        # Check if it's a GitHub URL
        if is_github_url(codebase_path):
            local_path, self.repo_name = clone_github_repo(codebase_path)
            self.codebase_path = Path(local_path)
            self.cloned = True
            self.temp_dir = self.codebase_path.parent
        else:
            self.codebase_path = Path(codebase_path).resolve()
            # Handle . and get actual directory name
            self.repo_name = self.codebase_path.name or "local_repo"

    def cleanup(self):
        """Remove cloned repository if we created one."""
        if self.cloned and self.temp_dir and self.temp_dir.exists():
            print(f"[CLEANUP] Removing {self.temp_dir}")
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def analyze(self) -> PrometheusReport:
        """Run combined analysis."""
        print("=" * 70)
        print("PROMETHEUS - Combined Fitness Analysis")
        print("=" * 70)

        report = PrometheusReport(
            codebase_path=str(self.codebase_path), timestamp=datetime.now().isoformat()
        )

        # Run complexity analysis
        print("\n[1/2] Running complexity analysis...")
        complexity_pipeline = ComplexityFitnessPipeline(str(self.codebase_path))
        complexity_result = complexity_pipeline.run()

        report.complexity_risk = complexity_result.risk_level
        report.loc_per_function_point = complexity_result.loc_per_function_point
        report.avg_cyclomatic = complexity_result.codebase_metrics.avg_cyclomatic
        report.entropy = complexity_result.codebase_metrics.codebase_entropy

        # =================================================================
        # INDUSTRY-CALIBRATED COMPLEXITY SCORING
        # =================================================================
        # Normalized against industry benchmarks:
        # - Small focused library (<20k LOC): Can score 85-100
        # - Medium project (20-100k LOC): Typically 60-85
        # - Large framework (100-300k LOC): Typically 45-70
        # - Massive codebase (300k+ LOC): Typically 30-55
        #
        # Factors weighted by industry importance:
        # 1. Size penalty (larger = harder to maintain) - 25%
        # 2. Cyclomatic complexity (cognitive load) - 25%
        # 3. Maintainability index (code quality) - 25%
        # 4. Hotspot density (problem areas) - 25%

        total_loc = complexity_result.codebase_metrics.total_loc
        avg_cyclo = complexity_result.codebase_metrics.avg_cyclomatic
        maint = complexity_result.codebase_metrics.avg_maintainability
        num_hotspots = len(complexity_result.hotspots)

        # 1. SIZE SCORE (0-25 points)
        # Industry baseline: 50k LOC is "normal", scales logarithmically
        # <10k = 25, 50k = 20, 100k = 15, 300k = 10, 500k+ = 5
        import math

        if total_loc < 5000:
            size_score = 25
        else:
            # Logarithmic decay: every 3x increase in LOC = -5 points
            size_score = max(5, 25 - (math.log10(total_loc / 5000) / math.log10(3)) * 5)

        # 2. CYCLOMATIC SCORE (0-25 points)
        # Industry baseline: 2.0-2.5 is typical for well-maintained code
        # <1.5 = 25, 2.0 = 22, 2.5 = 18, 3.0 = 14, 4.0 = 8, 5.0+ = 2
        if avg_cyclo <= 1.5:
            cyclo_score = 25
        elif avg_cyclo <= 3.0:
            cyclo_score = 25 - (avg_cyclo - 1.5) * 7  # Linear decrease
        elif avg_cyclo <= 5.0:
            cyclo_score = 14 - (avg_cyclo - 3.0) * 6  # Steeper decrease
        else:
            cyclo_score = max(0, 2 - (avg_cyclo - 5.0))
        cyclo_score = max(0, min(25, cyclo_score))

        # 3. MAINTAINABILITY SCORE (0-25 points)
        # Industry baseline: 65-75 is typical, >80 is excellent
        # MI > 80 = 25, 70 = 20, 60 = 15, 50 = 10, 40 = 5, <30 = 0
        if maint >= 80:
            maint_score = 25
        elif maint >= 40:
            maint_score = (maint - 40) / 40 * 25  # Linear scale 40-80 -> 0-25
        else:
            maint_score = 0
        maint_score = max(0, min(25, maint_score))

        # 4. HOTSPOT SCORE (0-25 points)
        # Hotspots per 10k LOC - industry baseline: <1 is good, >3 is concerning
        hotspots_per_10k = (num_hotspots / max(1, total_loc)) * 10000
        if hotspots_per_10k <= 0.5:
            hotspot_score = 25
        elif hotspots_per_10k <= 3.0:
            hotspot_score = 25 - (hotspots_per_10k - 0.5) * 8  # Linear decrease
        else:
            hotspot_score = max(0, 5 - (hotspots_per_10k - 3.0) * 2)
        hotspot_score = max(0, min(25, hotspot_score))

        # FINAL COMPLEXITY SCORE (0-100)
        # Higher score = SIMPLER code (better maintainability)
        # Lower score = MORE COMPLEX code (harder to maintain)
        # This is counter-intuitive naming but consistent with the original design
        report.complexity_score = size_score + cyclo_score + maint_score + hotspot_score

        # Store breakdown for transparency
        report.complexity_breakdown = {
            "size_score": round(size_score, 1),
            "cyclo_score": round(cyclo_score, 1),
            "maint_score": round(maint_score, 1),
            "hotspot_score": round(hotspot_score, 1),
            "total_loc": total_loc,
            "avg_cyclomatic": round(avg_cyclo, 2),
            "maintainability": round(maint, 1),
            "num_hotspots": num_hotspots,
            "hotspots_per_10k": round(hotspots_per_10k, 2),
        }

        # Run resilience analysis
        print("\n[2/2] Running resilience analysis...")
        mode_str = " (library mode)" if self.library_mode else ""
        print(f"[AEGIS] Scanning {self.codebase_path}{mode_str}...")
        aegis = Aegis(str(self.codebase_path), library_mode=self.library_mode)
        resilience_result = aegis.analyze()

        report.shield_rating = resilience_result.shield_rating
        report.resilience_score = resilience_result.overall_resilience_score

        # Store raw reports
        report.complexity_report = {
            "risk_level": complexity_result.risk_level,
            "verdict": complexity_result.overall_verdict,
            "recommendations": complexity_result.recommendations,
            "hotspots": complexity_result.hotspots,
            "metrics": {
                "total_loc": complexity_result.codebase_metrics.total_loc,
                "avg_cyclomatic": complexity_result.codebase_metrics.avg_cyclomatic,
                "maintainability": complexity_result.codebase_metrics.avg_maintainability,
                "entropy": complexity_result.codebase_metrics.codebase_entropy,
            },
        }

        report.resilience_report = {
            "shield_rating": resilience_result.shield_rating,
            "overall_score": resilience_result.overall_resilience_score,
            "category_scores": {
                "error_handling": resilience_result.error_handling_score,
                "timeouts": resilience_result.timeout_score,
                "retries": resilience_result.retry_score,
                "circuit_breakers": resilience_result.circuit_breaker_score,
                "observability": resilience_result.observability_score,
            },
            "vulnerabilities": resilience_result.vulnerabilities[:10],
            "recommendations": resilience_result.recommendations,
            "too_small_to_score": getattr(resilience_result, "too_small_to_score", False),
            "total_loc": getattr(resilience_result, "total_loc", 0),
            # I/O boundary analysis
            "io_boundary_analysis": {
                "total_io_operations": getattr(resilience_result, "total_io_operations", 0),
                "network_io_operations": getattr(resilience_result, "network_io_operations", 0),
                "io_density": getattr(resilience_result, "io_density", 0),
                "network_io_density": getattr(resilience_result, "network_io_density", 0),
                "has_io_boundaries": getattr(resilience_result, "has_io_boundaries", True),
                "has_network_boundaries": getattr(resilience_result, "has_network_boundaries", True),
                "resilience_applicable": getattr(resilience_result, "resilience_applicable", True),
                "io_boundary_reason": getattr(resilience_result, "io_boundary_reason", ""),
            },
        }

        # Determine quadrant
        self._determine_quadrant(report, resilience_result)

        # Generate priorities
        self._generate_priorities(report, complexity_result, resilience_result)

        return report

    def _determine_quadrant(self, report: PrometheusReport, resilience_result):
        """Determine which quadrant the codebase falls into.

        Industry-calibrated thresholds:
        - Complexity >= 50: Low complexity (well-structured, simpler code)
        - Complexity < 50: High complexity (needs work)
        - Resilience >= 35: Adequate resilience for frameworks
        
        Note: Complexity score uses INVERTED semantics - higher = simpler
        """
        # Thresholds - calibrated to industry benchmarks
        complexity_threshold = 50  # >= 50 = low complexity (simpler code)
        resilience_threshold = 35  # >= 35 = adequate resilience for frameworks

        # Check if resilience patterns are applicable (code crosses NETWORK I/O boundaries)
        if not getattr(resilience_result, "resilience_applicable", True):
            # Code doesn't cross network I/O boundaries - resilience patterns not expected
            total_loc = getattr(resilience_result, "total_loc", 0)
            total_io = getattr(resilience_result, "total_io_operations", 0)
            network_io = getattr(resilience_result, "network_io_operations", 0)
            file_io = total_io - network_io
            low_complexity = report.complexity_score >= complexity_threshold

            if low_complexity:
                # Simple computational/library code
                report.quadrant = "BUNKER"
                report.quadrant_description = "Simple computational/CLI code (no network I/O)."
                report.fitness_verdict = (
                    f"🏰 BUNKER (CLI/Library): Simple code without network dependencies.\n\n"
                    f"I/O Analysis: {network_io} network ops, {file_io} file ops in {total_loc:,} LOC.\n"
                    f"Resilience patterns (retries, timeouts, circuit breakers) are for network-bound code. "
                    f"This codebase primarily does local file I/O which doesn't need these patterns."
                )
            else:
                # Complex computational code
                report.quadrant = "FORTRESS"
                report.quadrant_description = "Complex computational/CLI code (no network I/O)."
                report.fitness_verdict = (
                    f"🏯 FORTRESS (CLI/Library): Complex code without network dependencies.\n\n"
                    f"I/O Analysis: {network_io} network ops, {file_io} file ops in {total_loc:,} LOC.\n"
                    f"Resilience patterns aren't needed for file-based code. "
                    f"Consider simplifying the algorithms or structure."
                )

            report.resilience_score = -1  # Mark as N/A
            report.shield_rating = "NO_IO"
            return

        # Check if codebase is too small to score resilience
        if getattr(resilience_result, "too_small_to_score", False):
            # For tiny codebases, we can't determine resilience
            # Classify based on complexity only, but mark as "MICRO" variant
            total_loc = getattr(resilience_result, "total_loc", 0)
            low_complexity = report.complexity_score >= complexity_threshold
            
            # Use special micro-variants that don't imply resilience assessment
            if low_complexity:
                # Small and simple - not a concern
                report.quadrant = "BUNKER"
                report.quadrant_description = "Small, simple codebase (micro-project)."
                report.fitness_verdict = (
                    f"🏰 BUNKER (Micro): Small, simple codebase.\n\n"
                    f"Note: Codebase has {total_loc:,} LOC - too small for resilience pattern analysis.\n"
                    f"This is not a problem - small codebases don't need complex resilience patterns."
                )
            else:
                # Small but complex - concerning
                report.quadrant = "GLASS HOUSE"
                report.quadrant_description = "Small but complex codebase (micro-project)."
                report.fitness_verdict = (
                    f"🏠 GLASS HOUSE (Micro): Small but complex codebase.\n\n"
                    f"Note: Codebase has {total_loc:,} LOC - too small for resilience pattern analysis.\n"
                    f"Consider simplifying the code structure."
                )

            report.resilience_score = -1  # Mark as not scored (will display as N/A)
            report.shield_rating = "TOO_SMALL"
            return

        low_complexity = report.complexity_score >= complexity_threshold
        high_resilience = report.resilience_score >= resilience_threshold

        if low_complexity and high_resilience:
            quadrant = "BUNKER"
        elif not low_complexity and high_resilience:
            quadrant = "FORTRESS"
        elif low_complexity and not high_resilience:
            quadrant = "GLASS_HOUSE"
        else:
            quadrant = "DEATHTRAP"

        q = self.QUADRANTS[quadrant]
        report.quadrant = q["name"]
        report.quadrant_description = q["description"]

        report.fitness_verdict = (
            f"{q['emoji']} {q['name']}: {q['description']}\n\n" f"Recommended Action: {q['action']}"
        )

    def _generate_priorities(self, report: PrometheusReport, complexity, resilience):
        """Generate prioritized action items."""
        priorities = []

        # Critical: DEATHTRAP needs immediate action
        if report.quadrant == "DEATHTRAP":
            priorities.append(
                {
                    "priority": 0,
                    "category": "CRITICAL",
                    "action": "This codebase is at high risk. Every deployment is a gamble.",
                    "first_steps": [
                        "Add timeouts to ALL network calls immediately",
                        "Add basic error handling around I/O operations",
                        "Set up centralized logging before the next incident",
                    ],
                }
            )

        # Resilience priorities (if low)
        if report.resilience_score < 50:
            if resilience.timeout_score < 30:
                priorities.append(
                    {
                        "priority": 1,
                        "category": "Timeouts",
                        "action": "Missing timeouts are the #1 cause of cascading failures",
                        "first_steps": [
                            "Audit all HTTP client instantiations",
                            "Add connect_timeout and read_timeout to each",
                            "Default: 5s connect, 30s read (adjust per use case)",
                        ],
                    }
                )

            if resilience.error_handling_score < 40:
                priorities.append(
                    {
                        "priority": 2,
                        "category": "Error Handling",
                        "action": "Unhandled exceptions crash processes and lose context",
                        "first_steps": [
                            "Wrap external calls in try/except",
                            "Create domain-specific exception classes",
                            "Log errors with context before re-raising",
                        ],
                    }
                )

            if resilience.observability_score < 40:
                priorities.append(
                    {
                        "priority": 3,
                        "category": "Observability",
                        "action": "You cannot fix what you cannot see",
                        "first_steps": [
                            "Add structured logging (structlog, pino)",
                            "Log at function entry/exit for critical paths",
                            "Include correlation IDs for request tracing",
                        ],
                    }
                )

        # Complexity priorities (if high)
        if report.complexity_score < 50:
            if complexity.codebase_metrics.avg_cyclomatic > 15:
                priorities.append(
                    {
                        "priority": 4,
                        "category": "Cyclomatic Complexity",
                        "action": "Functions with many branches are hard to test and reason about",
                        "first_steps": [
                            "Identify functions with complexity > 10",
                            "Extract helper functions for each logical branch",
                            "Consider strategy pattern for complex conditionals",
                        ],
                    }
                )

            if complexity.loc_per_function_point > 100:
                priorities.append(
                    {
                        "priority": 5,
                        "category": "Over-Engineering",
                        "action": f"{complexity.loc_per_function_point:.0f} LOC per feature is excessive",
                        "first_steps": [
                            "Look for abstraction layers that add no value",
                            "Remove speculative generality (YAGNI)",
                            "Inline trivial wrapper functions",
                        ],
                    }
                )

        # Sort by priority
        priorities.sort(key=lambda x: x["priority"])
        report.priorities = priorities

    def save_report(self, report: PrometheusReport, output_path: str = None) -> str:
        """Save combined report to JSON."""
        if output_path is None:
            output_path = f"prometheus_{self.repo_name}.json"

        report_dict = {
            "codebase_path": report.codebase_path,
            "timestamp": report.timestamp,
            "quadrant": report.quadrant,
            "fitness_verdict": report.fitness_verdict,
            "scores": {
                "complexity_risk": report.complexity_risk,
                "complexity_score": report.complexity_score,
                "resilience_score": report.resilience_score,
                "shield_rating": report.shield_rating,
            },
            "priorities": report.priorities,
            "complexity_analysis": report.complexity_report,
            "resilience_analysis": report.resilience_report,
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report_dict, f, indent=2, ensure_ascii=False)

        return output_path


def generate_technical_report(report: PrometheusReport, output_path: str) -> str:
    """
    Generate detailed technical report in Markdown format.

    Includes:
    - Executive summary
    - Methodology explanation
    - Detailed metrics breakdown
    - File-by-file analysis
    - Actionable recommendations with code examples
    """

    cr = report.complexity_report or {}
    rr = report.resilience_report or {}
    cm = cr.get("metrics", {})
    cs = rr.get("category_scores", {})

    md = f"""# Prometheus Technical Report
## Codebase: {report.codebase_path}
**Generated:** {report.timestamp}

---

# Executive Summary

| Dimension | Rating | Score |
|-----------|--------|-------|
| **Complexity Risk** | {report.complexity_risk} | {report.complexity_score:.0f}/100 |
| **Resilience Shield** | {report.shield_rating} | {report.resilience_score:.0f}/100 |
| **Fitness Quadrant** | {report.quadrant} | — |

**Verdict:** {report.quadrant_description}

---

# Methodology

This analysis combines two measurement frameworks:

## 1. Complexity Analysis (Shannon-Inspired)

Based on information theory and thermodynamics:

- **Shannon Entropy**: Measures information density of token distribution
- **Kolmogorov Complexity Proxy**: Compression ratio indicates redundancy
- **Cyclomatic Complexity**: Graph-theoretic count of independent paths
- **Halstead Metrics**: Operator/operand analysis predicting bug density

**Theoretical basis**: Systems with higher complexity have more failure modes.
Reliability of a series system: `R = r₁ × r₂ × ... × rₙ` — each component
with reliability `r < 1` multiplicatively reduces total reliability.

## 2. Resilience Analysis (SRE Principles)

Detection of defensive programming patterns:

- **Error Handling**: try/catch coverage and exception specificity
- **Timeouts**: Network and database timeout configurations
- **Retries**: Exponential backoff, jitter, max attempt limits
- **Circuit Breakers**: Failure threshold configs, fallback methods
- **Observability**: Logging density, metrics emission, trace spans
- **Health Checks**: Liveness/readiness probes, dependency checks

**Theoretical basis**: Defense in depth. Each resilience pattern
reduces the probability that a failure becomes an outage.

---

# Complexity Metrics Detail

## Overview

| Metric | Value | Assessment |
|--------|-------|------------|
| Total Lines of Code | {cm.get('total_loc', 'N/A'):,} | — |
| Average Cyclomatic Complexity | {cm.get('avg_cyclomatic', 0):.2f} | {'🟢 Good' if cm.get('avg_cyclomatic', 0) < 5 else '🟡 Elevated' if cm.get('avg_cyclomatic', 0) < 10 else '🔴 High'} |
| Maintainability Index | {cm.get('maintainability', 0):.1f}/100 | {'🟢 Good' if cm.get('maintainability', 0) > 65 else '🟡 Fair' if cm.get('maintainability', 0) > 40 else '🔴 Poor'} |
| Code Entropy | {cm.get('entropy', 0):.2f} bits/token | {'🟡 Low (repetitive)' if cm.get('entropy', 0) < 4 else '🟢 Normal' if cm.get('entropy', 0) < 8 else '🟡 High (chaotic)'} |
| LOC per Function Point | {report.loc_per_function_point:.0f} | {'🟢 Efficient' if report.loc_per_function_point < 50 else '🟡 Acceptable' if report.loc_per_function_point < 150 else '🔴 Over-engineered'} |

## Cyclomatic Complexity Thresholds

| Range | Risk Level | Recommendation |
|-------|------------|----------------|
| 1-5 | Low | Simple, easy to test |
| 6-10 | Moderate | Consider simplifying |
| 11-20 | High | Refactoring recommended |
| 21+ | Very High | Split into smaller functions |

## Hotspots (Files Needing Attention)

"""

    hotspots = cr.get("hotspots", [])
    if hotspots:
        for hs in hotspots[:10]:
            md += f"### `{hs.get('file', 'unknown')}`\n\n"
            for issue in hs.get("issues", []):
                md += f"- ⚠️ {issue}\n"
            md += "\n"
    else:
        md += "_No critical hotspots identified._\n\n"

    md += f"""---

# Resilience Metrics Detail

## Category Scores

| Pattern | Score | Status |
|---------|-------|--------|
| Error Handling | {cs.get('error_handling', 0):.0f}/100 | {'🟢' if cs.get('error_handling', 0) >= 60 else '🟡' if cs.get('error_handling', 0) >= 40 else '🔴'} |
| Timeouts | {cs.get('timeouts', 0):.0f}/100 | {'🟢' if cs.get('timeouts', 0) >= 60 else '🟡' if cs.get('timeouts', 0) >= 40 else '🔴'} |
| Retries | {cs.get('retries', 0):.0f}/100 | {'🟢' if cs.get('retries', 0) >= 60 else '🟡' if cs.get('retries', 0) >= 40 else '🔴'} |
| Circuit Breakers | {cs.get('circuit_breakers', 0):.0f}/100 | {'🟢' if cs.get('circuit_breakers', 0) >= 60 else '🟡' if cs.get('circuit_breakers', 0) >= 40 else '🔴'} |
| Observability | {cs.get('observability', 0):.0f}/100 | {'🟢' if cs.get('observability', 0) >= 60 else '🟡' if cs.get('observability', 0) >= 40 else '🔴'} |

## Vulnerabilities Detected

"""

    vulns = rr.get("vulnerabilities", [])
    if vulns:
        for v in vulns[:15]:
            severity_icon = (
                "🔴"
                if v.get("severity") == "HIGH"
                else "🟡" if v.get("severity") == "MEDIUM" else "🟢"
            )
            md += f"- {severity_icon} **[{v.get('severity', 'UNKNOWN')}]** `{v.get('file', 'unknown')}`: {v.get('message', '')}\n"
    else:
        md += "_No critical vulnerabilities detected._\n"

    md += """

---

# Recommendations

"""

    # Detailed recommendations with code examples
    for i, rec in enumerate(rr.get("recommendations", [])[:8], 1):
        priority_icon = (
            "🚨"
            if rec.get("priority") == "CRITICAL"
            else "⚠️" if rec.get("priority") == "HIGH" else "ℹ️"
        )
        md += f"""## {i}. {rec.get('category', 'General')} {priority_icon}

**Priority:** {rec.get('priority', 'MEDIUM')}

{rec.get('message', '')}

**Suggested Libraries:**
"""
        for lib in rec.get("libraries", []):
            md += f"- `{lib}`\n"
        md += "\n"

    # Add code examples for common patterns
    md += """---

# Appendix: Pattern Examples

## A. Timeout Configuration (Python)

```python
import httpx

# ✅ Good: Explicit timeouts
client = httpx.Client(
    timeout=httpx.Timeout(
        connect=5.0,    # Connection timeout
        read=30.0,      # Read timeout
        write=10.0,     # Write timeout
        pool=5.0        # Pool acquisition timeout
    )
)

# ❌ Bad: No timeout (can hang forever)
client = httpx.Client()
```

## B. Retry with Exponential Backoff (Python)

```python
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((ConnectionError, TimeoutError))
)
def call_external_service():
    response = client.get("/api/data")
    response.raise_for_status()
    return response.json()
```

## C. Circuit Breaker (Python)

```python
import pybreaker

# Create breaker: opens after 5 failures, resets after 30s
db_breaker = pybreaker.CircuitBreaker(
    fail_max=5,
    reset_timeout=30,
    exclude=[ValueError]  # Don't count these as failures
)

@db_breaker
def query_database(query):
    return db.execute(query)

# Usage with fallback
try:
    result = query_database("SELECT * FROM users")
except pybreaker.CircuitBreakerError:
    result = get_cached_users()  # Fallback
```

## D. Structured Logging (Python)

```python
import structlog

logger = structlog.get_logger()

def process_order(order_id: str, user_id: str):
    log = logger.bind(order_id=order_id, user_id=user_id)

    log.info("processing_started")

    try:
        result = do_processing()
        log.info("processing_complete", items=len(result))
        return result
    except Exception as e:
        log.error("processing_failed", error=str(e), exc_info=True)
        raise
```

---

# Quadrant Movement Strategy

Current position: **{report.quadrant}**

"""

    if report.quadrant == "DEATHTRAP":
        md += """## Escaping the Deathtrap

**Immediate actions (this sprint):**
1. Add timeouts to ALL network calls
2. Wrap external calls in try/except
3. Set up centralized error logging

**Short-term (next 2-4 weeks):**
1. Add retry logic for transient failures
2. Implement health check endpoints
3. Add metrics for error rates

**Medium-term (1-3 months):**
1. Refactor high-complexity functions
2. Add circuit breakers for external dependencies
3. Implement feature flags for graceful degradation

**Goal:** Move to GLASS HOUSE first (reduce complexity), then to BUNKER (add resilience).
"""
    elif report.quadrant == "GLASS HOUSE":
        md += """## Fortifying the Glass House

Your code is simple — that's good! Now add defense:

**Immediate actions:**
1. Audit all I/O operations for error handling
2. Add timeouts to network calls
3. Implement basic retry logic

**Short-term:**
1. Add structured logging
2. Implement health checks
3. Add circuit breakers for critical paths

**Goal:** Move to BUNKER (add resilience while maintaining simplicity).
"""
    elif report.quadrant == "FORTRESS":
        md += """## Streamlining the Fortress

Your code is well-defended but over-engineered:

**Questions to ask:**
1. Are all abstractions earning their keep?
2. Can any defensive layers be consolidated?
3. Is there speculative generality (YAGNI violations)?

**Actions:**
1. Identify and remove unused code paths
2. Consolidate redundant error handling
3. Simplify overly abstract interfaces

**Goal:** Move to BUNKER (reduce complexity while maintaining resilience).
"""
    else:  # BUNKER
        md += """## Maintaining the Bunker

You're in the ideal state. Maintain it:

**Ongoing practices:**
1. Monitor complexity metrics in CI/CD
2. Review new code for unnecessary complexity
3. Keep resilience patterns up to date
4. Regular dependency updates

**Warning signs to watch:**
1. Cyclomatic complexity creeping up
2. New code without error handling
3. Network calls without timeouts
"""

    md += """

---

*Report generated by Prometheus Fitness Analyzer*
*Complexity × Resilience = Reliability*
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md)

    return output_path


def dump_raw_data(report: PrometheusReport, output_path: str) -> str:
    """
    Dump all analysis data to a text file for further processing.

    Format designed for:
    - Grep/awk/sed analysis
    - Import into spreadsheets
    - Feeding to other tools or LLMs
    """

    lines = []

    lines.append("=" * 80)
    lines.append("PROMETHEUS RAW DATA DUMP")
    lines.append("=" * 80)
    lines.append("")
    lines.append(f"CODEBASE_PATH={report.codebase_path}")
    lines.append(f"TIMESTAMP={report.timestamp}")
    lines.append(f"QUADRANT={report.quadrant}")
    lines.append(f"COMPLEXITY_RISK={report.complexity_risk}")
    lines.append(f"COMPLEXITY_SCORE={report.complexity_score}")
    lines.append(f"SHIELD_RATING={report.shield_rating}")
    lines.append(f"RESILIENCE_SCORE={report.resilience_score}")
    lines.append(f"AVG_CYCLOMATIC={report.avg_cyclomatic}")
    lines.append(f"LOC_PER_FP={report.loc_per_function_point}")
    lines.append(f"ENTROPY={report.entropy}")
    lines.append("")

    # Complexity metrics
    lines.append("-" * 80)
    lines.append("COMPLEXITY_METRICS")
    lines.append("-" * 80)
    if report.complexity_report:
        cm = report.complexity_report.get("metrics", {})
        for key, value in cm.items():
            lines.append(f"COMPLEXITY.{key.upper()}={value}")
    lines.append("")

    # Resilience category scores
    lines.append("-" * 80)
    lines.append("RESILIENCE_CATEGORY_SCORES")
    lines.append("-" * 80)
    if report.resilience_report:
        cs = report.resilience_report.get("category_scores", {})
        for key, value in cs.items():
            lines.append(f"RESILIENCE.{key.upper()}={value}")
    lines.append("")

    # Hotspots
    lines.append("-" * 80)
    lines.append("HOTSPOTS")
    lines.append("-" * 80)
    if report.complexity_report:
        for hs in report.complexity_report.get("hotspots", []):
            for issue in hs.get("issues", []):
                lines.append(f"HOTSPOT|{hs.get('file', 'unknown')}|{issue}")
    lines.append("")

    # Vulnerabilities
    lines.append("-" * 80)
    lines.append("VULNERABILITIES")
    lines.append("-" * 80)
    if report.resilience_report:
        for v in report.resilience_report.get("vulnerabilities", []):
            lines.append(
                f"VULN|{v.get('severity', 'UNKNOWN')}|{v.get('file', 'unknown')}|{v.get('message', '')}"
            )
    lines.append("")

    # Recommendations
    lines.append("-" * 80)
    lines.append("RECOMMENDATIONS")
    lines.append("-" * 80)
    if report.resilience_report:
        for rec in report.resilience_report.get("recommendations", []):
            libs = ",".join(rec.get("libraries", []))
            lines.append(
                f"REC|{rec.get('priority', 'MEDIUM')}|{rec.get('category', '')}|{rec.get('message', '')}|{libs}"
            )
    lines.append("")

    # Priorities
    lines.append("-" * 80)
    lines.append("PRIORITIES")
    lines.append("-" * 80)
    for p in report.priorities:
        steps = "; ".join(p.get("first_steps", []))
        lines.append(
            f"PRIORITY|{p.get('priority', 99)}|{p.get('category', '')}|{p.get('action', '')}|{steps}"
        )
    lines.append("")

    # File-level metrics (TSV format for easy parsing)
    lines.append("-" * 80)
    lines.append("FILE_METRICS_TSV")
    lines.append("-" * 80)
    lines.append(
        "FILE\tLOC\tCYCLOMATIC\tMAINTAINABILITY\tTRY_BLOCKS\tBARE_EXCEPTS\tTIMEOUTS\tLOG_DENSITY\tRESILIENCE_SCORE"
    )

    # Get file metrics from complexity report if available
    if report.complexity_report and "file_details" in report.complexity_report:
        for fm in report.complexity_report.get("file_details", []):
            if isinstance(fm, dict):
                lines.append(
                    f"{fm.get('path', 'unknown')}\t"
                    f"{fm.get('lines_of_code', 0)}\t"
                    f"{fm.get('cyclomatic_complexity', 0):.2f}\t"
                    f"{fm.get('maintainability_index', 0):.1f}\t"
                    f"N/A\tN/A\tN/A\tN/A\tN/A"
                )

    # If we have resilience file metrics, add those
    if report.resilience_report and "file_metrics" in report.resilience_report:
        for fm in report.resilience_report.get("file_metrics", []):
            if isinstance(fm, dict):
                eh = fm.get("error_handling", {})
                to = fm.get("timeouts", {})
                ob = fm.get("observability", {})
                lines.append(
                    f"{fm.get('path', 'unknown')}\t"
                    f"{fm.get('lines_of_code', 0)}\t"
                    f"N/A\tN/A\t"
                    f"{eh.get('try_blocks', 0)}\t"
                    f"{eh.get('bare_excepts', 0)}\t"
                    f"{to.get('generic_timeouts', 0)}\t"
                    f"{ob.get('logs_per_100_loc', 0):.2f}\t"
                    f"{fm.get('resilience_score', 0):.1f}"
                )

    lines.append("")
    lines.append("=" * 80)
    lines.append("END DUMP")
    lines.append("=" * 80)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return output_path


def _build_comparison_item(r):
    """Build HTML for a single comparison item in the quadrant report."""
    from pathlib import Path
    color = '#22c55e' if r.quadrant == 'BUNKER' else '#3b82f6' if r.quadrant == 'FORTRESS' else '#eab308' if r.quadrant == 'GLASS HOUSE' else '#ef4444'
    name = r.github.full_name if r.github.full_name else Path(r.codebase_path).name
    desc = r.github.description[:40] + '...' if r.github.description and len(r.github.description) > 40 else r.github.description or ''
    quadrant_short = r.quadrant.split()[0]
    resilience_display = "N/A" if r.resilience_score < 0 else f"{r.resilience_score:.0f}"
    return f'''
                    <div style="display: flex; align-items: center; gap: 1rem; padding: 0.75rem; background: rgba(15, 23, 42, 0.5); border-radius: 0.5rem; border-left: 4px solid {color};">
                        <div style="flex: 1;">
                            <div style="font-weight: bold; color: #f8fafc;">{name}</div>
                            <div style="font-size: 0.8rem; color: #94a3b8;">{desc}</div>
                        </div>
                        <div style="text-align: center; min-width: 80px;">
                            <div style="font-size: 1.25rem; font-weight: bold; color: {color};">{quadrant_short}</div>
                            <div style="font-size: 0.7rem; color: #64748b;">QUADRANT</div>
                        </div>
                        <div style="text-align: center; min-width: 60px;">
                            <div style="font-size: 1.25rem; font-weight: bold; color: #f8fafc;">{resilience_display}</div>
                            <div style="font-size: 0.7rem; color: #64748b;">RESILIENCE</div>
                        </div>
                    </div>'''


def generate_quadrant_html(
    report: PrometheusReport,
    output_path: str = None,
    repo_name: str = "Codebase",
    comparison_reports: list = None,
) -> str:
    """Generate visual HTML report with quadrant chart."""

    if output_path is None:
        output_path = "prometheus_report.html"

    reports_data = comparison_reports if comparison_reports else [report]

    # Generate points for all reports
    points_html = ""
    legend_html = ""
    colors = [
        "#3b82f6",
        "#22c55e",
        "#f59e0b",
        "#ef4444",
        "#8b5cf6",
        "#ec4899",
        "#06b6d4",
        "#84cc16",
    ]

    for idx, r in enumerate(reports_data):
        x = r.complexity_score
        y = r.resilience_score

        name = r.github.full_name if r.github.full_name else Path(r.codebase_path).name
        short_name = name.split("/")[-1][:10] if "/" in name else name[:10]

        if len(reports_data) == 1:
            quadrant_colors = {
                "BUNKER": "#22c55e",
                "FORTRESS": "#3b82f6",
                "GLASS HOUSE": "#eab308",
                "DEATHTRAP": "#ef4444",
            }
            color = quadrant_colors.get(r.quadrant, "#666")
        else:
            color = colors[idx % len(colors)]

        points_html += f"""
            <div class="point" style="left: {x}%; bottom: {y}%; background: {color};" title="{name}: {r.quadrant}">
                {'<span class="point-label">' + short_name + '</span>' if len(reports_data) > 1 else ''}
            </div>"""

        if len(reports_data) > 1:
            stars_str = f" ⭐{r.github.stars:,}" if r.github.stars else ""
            legend_html += f"""
                <div class="legend-item">
                    <span class="legend-dot" style="background: {color};"></span>
                    <span class="legend-name">{name}{stars_str}</span>
                    <span class="legend-quadrant" style="color: {color};">{r.quadrant}</span>
                </div>"""

    # Build title with GitHub metadata
    gh = report.github
    if gh.full_name:
        display_name = gh.full_name
        meta_parts = []
        if gh.stars:
            meta_parts.append(f"⭐ {gh.stars:,}")
        if gh.language:
            meta_parts.append(gh.language)
        if gh.license:
            meta_parts.append(gh.license)
        subtitle = " • ".join(meta_parts) if meta_parts else ""
        description = gh.description or ""
    else:
        display_name = repo_name.replace("_", "/") if "_" in repo_name else repo_name
        subtitle = ""
        description = ""

    if len(reports_data) > 1:
        display_name = "Comparison"
        subtitle = f"{len(reports_data)} repositories analyzed"
        description = ""

    # Comparison table if multiple reports
    comparison_table = ""
    if len(reports_data) > 1:
        comparison_rows = ""
        for r in sorted(
            reports_data,
            key=lambda x: (
                -x.github.stars if x.github.stars else 0,
                -x.resilience_score,
            ),
        ):
            quadrant_colors = {
                "BUNKER": "#22c55e",
                "FORTRESS": "#3b82f6",
                "GLASS HOUSE": "#eab308",
                "DEATHTRAP": "#ef4444",
            }
            q_color = quadrant_colors.get(r.quadrant, "#6b7280")
            name = r.github.full_name if r.github.full_name else Path(r.codebase_path).name
            stars = f"⭐ {r.github.stars:,}" if r.github.stars else "-"
            lang = r.github.language or "-"
            comparison_rows += f"""
            <tr>
                <td>
                    <strong>{name}</strong>
                    {f'<br/><small style="color: #64748b;">{r.github.description[:50]}...</small>' if r.github.description else ''}
                </td>
                <td>{stars}</td>
                <td>{lang}</td>
                <td><span style="color: {q_color}; font-weight: bold;">{r.quadrant}</span></td>
                <td>{r.complexity_score:.0f}</td>
                <td>{r.resilience_score:.0f}</td>
            </tr>"""
        comparison_table = f"""
        <div class="section">
            <h2>Comparison ({len(reports_data)} repositories)</h2>
            <table style="width: 100%; border-collapse: collapse; background: #1e293b; border-radius: 8px;">
                <thead>
                    <tr style="background: #0f172a;">
                        <th style="padding: 0.75rem; text-align: left; color: #94a3b8;">Repository</th>
                        <th style="padding: 0.75rem; text-align: left; color: #94a3b8;">Stars</th>
                        <th style="padding: 0.75rem; text-align: left; color: #94a3b8;">Language</th>
                        <th style="padding: 0.75rem; text-align: left; color: #94a3b8;">Quadrant</th>
                        <th style="padding: 0.75rem; text-align: left; color: #94a3b8;">Complexity</th>
                        <th style="padding: 0.75rem; text-align: left; color: #94a3b8;">Resilience</th>
                    </tr>
                </thead>
                <tbody>{comparison_rows}</tbody>
            </table>
        </div>"""

    # Calculate position on quadrant (0-100 scale)
    x = report.complexity_score  # Higher = less complex (right side)
    y = report.resilience_score  # Higher = more resilient (top)

    # Quadrant colors
    quadrant_colors = {
        "BUNKER": "#22c55e",
        "FORTRESS": "#3b82f6",
        "GLASS HOUSE": "#eab308",
        "DEATHTRAP": "#ef4444",
    }
    color = quadrant_colors.get(report.quadrant, "#666")

    # Generate priority HTML
    priorities_html = ""
    for p in report.priorities[:5]:
        steps_html = "".join(f"<li>{s}</li>" for s in p.get("first_steps", []))
        priorities_html += f"""
        <div class="priority priority-{p['priority']}">
            <div class="priority-header">
                <span class="priority-badge">{p['category']}</span>
            </div>
            <p>{p['action']}</p>
            <ul class="steps">{steps_html}</ul>
        </div>
        """

    comparison_items_html = "".join(_build_comparison_item(r) for r in sorted(reports_data, key=lambda x: -x.resilience_score))
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Prometheus: {display_name}</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
            color: #e2e8f0;
            min-height: 100vh;
            padding: 2rem;
        }}

        .container {{ max-width: 1200px; margin: 0 auto; }}

        h1 {{
            font-size: 2.5rem;
            background: linear-gradient(90deg, #f97316, #eab308);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.5rem;
        }}

        .repo-name {{
            font-size: 1.5rem;
            color: #e2e8f0;
            font-weight: 300;
            margin-bottom: 0.25rem;
        }}

        .subtitle {{ color: #94a3b8; margin-bottom: 2rem; }}

        .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-bottom: 2rem; }}

        @media (max-width: 900px) {{ .grid {{ grid-template-columns: 1fr; }} }}

        .card {{
            background: rgba(30, 41, 59, 0.8);
            border-radius: 1rem;
            padding: 1.5rem;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(148, 163, 184, 0.1);
        }}

        .quadrant-container {{
            position: relative;
            width: 100%;
            aspect-ratio: 1;
            background: linear-gradient(135deg,
                rgba(239, 68, 68, 0.15) 0%,
                rgba(239, 68, 68, 0.15) 50%,
                rgba(234, 179, 8, 0.15) 50%,
                rgba(234, 179, 8, 0.15) 100%
            );
            border-radius: 0.5rem;
            overflow: hidden;
        }}

        .quadrant-container::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 50%;
            right: 0;
            bottom: 50%;
            background: linear-gradient(135deg,
                rgba(59, 130, 246, 0.15) 0%,
                rgba(34, 197, 94, 0.15) 100%
            );
        }}

        .quadrant-container::after {{
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            right: 0;
            bottom: 0;
            background: rgba(34, 197, 94, 0.15);
        }}

        .axis {{
            position: absolute;
            background: rgba(148, 163, 184, 0.3);
        }}

        .axis-x {{ left: 0; right: 0; top: 50%; height: 2px; }}
        .axis-y {{ top: 0; bottom: 0; left: 50%; width: 2px; }}

        .quadrant-label {{
            position: absolute;
            font-size: 0.75rem;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.1em;
        }}

        .label-bunker {{ bottom: 10%; right: 10%; color: #22c55e; }}
        .label-fortress {{ top: 10%; right: 10%; color: #3b82f6; }}
        .label-glass {{ bottom: 10%; left: 10%; color: #eab308; }}
        .label-death {{ top: 10%; left: 10%; color: #ef4444; }}

        .position-dot {{
            position: absolute;
            width: 24px;
            height: 24px;
            background: {color};
            border-radius: 50%;
            transform: translate(-50%, -50%);
            box-shadow: 0 0 20px {color}, 0 0 40px {color}66;
            z-index: 10;
            animation: pulse 2s infinite;
        }}

        @keyframes pulse {{
            0%, 100% {{ transform: translate(-50%, -50%) scale(1); }}
            50% {{ transform: translate(-50%, -50%) scale(1.2); }}
        }}

        .axis-label {{
            position: absolute;
            font-size: 0.7rem;
            color: #94a3b8;
        }}

        .label-top {{ top: 5px; left: 50%; transform: translateX(-50%); }}
        .label-bottom {{ bottom: 5px; left: 50%; transform: translateX(-50%); }}
        .label-left {{ left: 5px; top: 50%; transform: translateY(-50%) rotate(-90deg); transform-origin: left center; }}
        .label-right {{ right: 5px; top: 50%; transform: translateY(-50%) rotate(90deg); transform-origin: right center; }}

        .verdict {{
            text-align: center;
            padding: 1.5rem;
        }}

        .verdict-quadrant {{
            font-size: 3rem;
            margin-bottom: 0.5rem;
        }}

        .verdict-name {{
            font-size: 1.5rem;
            font-weight: bold;
            color: {color};
            margin-bottom: 0.5rem;
        }}

        .verdict-desc {{
            color: #94a3b8;
            margin-bottom: 1rem;
        }}

        .scores {{
            display: flex;
            justify-content: center;
            gap: 2rem;
            margin-top: 1rem;
        }}

        .score {{
            text-align: center;
        }}

        .score-value {{
            font-size: 2rem;
            font-weight: bold;
        }}

        .score-label {{
            font-size: 0.75rem;
            color: #64748b;
            text-transform: uppercase;
        }}

        h2 {{
            font-size: 1.25rem;
            margin-bottom: 1rem;
            color: #f8fafc;
        }}

        .priority {{
            background: rgba(15, 23, 42, 0.5);
            border-radius: 0.5rem;
            padding: 1rem;
            margin-bottom: 1rem;
            border-left: 4px solid #64748b;
        }}

        .priority-0 {{ border-color: #ef4444; }}
        .priority-1 {{ border-color: #f97316; }}
        .priority-2 {{ border-color: #eab308; }}
        .priority-3 {{ border-color: #3b82f6; }}
        .priority-4, .priority-5 {{ border-color: #64748b; }}

        .priority-header {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 0.5rem;
        }}

        .priority-badge {{
            font-size: 0.75rem;
            font-weight: bold;
            text-transform: uppercase;
            color: #f8fafc;
        }}

        .priority p {{
            color: #cbd5e1;
            margin-bottom: 0.75rem;
        }}

        .steps {{
            margin-left: 1.25rem;
            color: #94a3b8;
            font-size: 0.9rem;
        }}

        .steps li {{
            margin-bottom: 0.25rem;
        }}

        .formula {{
            text-align: center;
            padding: 1rem;
            background: rgba(15, 23, 42, 0.5);
            border-radius: 0.5rem;
            margin-top: 1rem;
        }}

        .formula-text {{
            font-family: 'Times New Roman', serif;
            font-style: italic;
            font-size: 1.1rem;
            color: #94a3b8;
        }}

        footer {{
            text-align: center;
            margin-top: 2rem;
            padding-top: 1rem;
            border-top: 1px solid rgba(148, 163, 184, 0.1);
            color: #64748b;
            font-size: 0.875rem;
        }}

        .point {{
            position: absolute;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            border: 3px solid white;
            box-shadow: 0 0 20px currentColor;
            transform: translate(-50%, 50%);
            z-index: 10;
            cursor: pointer;
            transition: transform 0.2s;
        }}
        .point:hover {{ transform: translate(-50%, 50%) scale(1.3); }}
        .point-label {{
            position: absolute;
            top: -20px;
            left: 50%;
            transform: translateX(-50%);
            font-size: 0.6rem;
            color: white;
            white-space: nowrap;
            background: #0f172a;
            padding: 2px 6px;
            border-radius: 4px;
        }}

        .legend {{
            margin-top: 1rem;
            display: flex;
            flex-wrap: wrap;
            gap: 0.75rem;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.8rem;
        }}
        .legend-dot {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
        }}
        .legend-name {{ color: #e2e8f0; }}
        .legend-quadrant {{ font-size: 0.7rem; }}

        .repo-meta {{
            color: #94a3b8;
            font-size: 0.9rem;
            margin-bottom: 0.5rem;
        }}
        .repo-description {{
            color: #64748b;
            font-size: 0.85rem;
            margin-bottom: 1rem;
        }}
        .repo-name a {{
            color: #e2e8f0;
            text-decoration: none;
        }}
        .repo-name a:hover {{
            color: #7dd3fc;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔥 Prometheus</h1>
        <p class="repo-name">{f'<a href="{report.github.url}" target="_blank">{display_name}</a>' if report.github.url else display_name}</p>
        {f'<p class="repo-meta">{subtitle}</p>' if subtitle else ''}
        {f'<p class="repo-description">{description}</p>' if description else ''}
        <p class="subtitle">Combined Fitness Analysis • {report.timestamp[:10]}</p>

        {comparison_table}

        <div class="grid">
            <div class="card">
                <h2>Fitness Quadrant</h2>
                <div class="quadrant-container">
                    <div class="axis axis-x"></div>
                    <div class="axis axis-y"></div>

                    <span class="quadrant-label label-bunker">🏰 Bunker</span>
                    <span class="quadrant-label label-fortress">🏯 Fortress</span>
                    <span class="quadrant-label label-glass">🏠 Glass House</span>
                    <span class="quadrant-label label-death">💀 Deathtrap</span>

                    <span class="axis-label label-top">High Resilience</span>
                    <span class="axis-label label-bottom">Low Resilience</span>
                    <span class="axis-label label-left">High Complexity</span>
                    <span class="axis-label label-right">Low Complexity</span>

                    {points_html if len(reports_data) > 1 else f'<div class="position-dot" style="left: {x}%; bottom: {y}%;"></div>'}
                </div>
                {f'<div class="legend">{legend_html}</div>' if legend_html else ''}
            </div>

            <div class="card verdict">
                {"" if len(reports_data) > 1 else f'''
                <div class="verdict-quadrant">
                    {"🏰" if report.quadrant == "BUNKER" else "🏯" if report.quadrant == "FORTRESS" else "🏠" if report.quadrant == "GLASS HOUSE" else "💀"}
                </div>
                <div class="verdict-name">{report.quadrant}</div>
                <div class="verdict-desc">{report.quadrant_description}</div>

                <div class="scores">
                    <div class="score">
                        <div class="score-value" style="color: {"#22c55e" if report.complexity_score >= 60 else "#eab308" if report.complexity_score >= 40 else "#ef4444"}">
                            {report.complexity_risk}
                        </div>
                        <div class="score-label">Complexity Risk</div>
                    </div>
                    <div class="score">
                        <div class="score-value" style="color: {"#22c55e" if report.resilience_score >= 60 else "#eab308" if report.resilience_score >= 40 else "#ef4444"}">
                            {report.shield_rating}
                        </div>
                        <div class="score-label">Shield Rating</div>
                    </div>
                </div>

                <div class="scores">
                    <div class="score">
                        <div class="score-value">{f"{report.avg_cyclomatic:.1f}" if report.avg_cyclomatic > 0 else "N/A"}</div>
                        <div class="score-label">Avg Cyclomatic</div>
                    </div>
                    <div class="score">
                        <div class="score-value">{"N/A" if report.resilience_score < 0 else f"{report.resilience_score:.0f}"}</div>
                        <div class="score-label">Resilience Score</div>
                    </div>
                </div>

                <div class="formula">
                    <div class="formula-text">
                        Fitness = f(1/Complexity, Resilience)
                    </div>
                </div>
                '''}

                {f'''
                <h2 style="margin-bottom: 1rem;">Comparison Summary</h2>
                <div style="display: flex; flex-direction: column; gap: 1rem;">
                    {comparison_items_html}
                </div>
                <div class="formula" style="margin-top: 1rem;">
                    <div class="formula-text">
                        Higher resilience = better defended
                    </div>
                </div>
                ''' if len(reports_data) > 1 else ''}
            </div>
        </div>

        <div class="card">
            <h2>Priority Actions</h2>
            {priorities_html if priorities_html else '<p style="color: #64748b;">No critical actions required. Maintain current practices.</p>'}
        </div>

        <footer>
            <p>Prometheus Fitness Analyzer</p>
            <p>Complexity × Resilience = Reliability</p>
        </footer>
    </div>
</body>
</html>
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    return output_path


def safe_print(text):
    """Print function that handles Unicode errors on Windows."""
    try:
        print(text)
    except UnicodeEncodeError:
        # Strip non-ASCII for Windows console
        import re

        clean = re.sub(r"[^\x00-\x7F]+", "", str(text))
        print(clean)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Prometheus - Combined complexity and resilience analysis",
        epilog="""
Examples:
  python prometheus.py /path/to/local/repo
  python prometheus.py https://github.com/owner/repo
  python prometheus.py owner/repo
  python prometheus.py pallets/flask --report --dump
  python prometheus.py repo1 repo2 repo3 --compare
        """,
    )
    parser.add_argument("paths", nargs="+", help="Path(s) to codebase or GitHub URL(s)")
    parser.add_argument("-o", "--output", help="Output JSON path (default: prometheus_<repo>.json)")
    parser.add_argument("--html", help="Output HTML report path (default: prometheus_<repo>.html)")
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate detailed technical report in Markdown",
    )
    parser.add_argument(
        "--report-path",
        help="Path for Markdown report (default: prometheus_<repo>_report.md)",
    )
    parser.add_argument(
        "--dump",
        action="store_true",
        help="Dump all raw data to text file for analysis",
    )
    parser.add_argument(
        "--dump-path", help="Path for data dump (default: prometheus_<repo>_data.txt)"
    )
    parser.add_argument(
        "--library",
        action="store_true",
        help="Library mode: adjusts scoring for libraries (less penalty for missing timeouts/retries)",
    )
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Generate comparison chart for multiple repos",
    )
    parser.add_argument(
        "--security",
        action="store_true",
        help="Run security analysis (requires bandit, semgrep, or gosec)",
    )
    parser.add_argument(
        "--smells",
        action="store_true",
        help="Run code smell analysis (NIH patterns, long functions, outdated code)",
    )
    parser.add_argument("--keep", action="store_true", help="Keep cloned repo after analysis")

    args = parser.parse_args()

    # Multi-repo comparison mode
    if len(args.paths) > 1 or args.compare:
        reports = []
        prometheus_instances = []

        for path in args.paths:
            safe_print(f"\n[ANALYZE] {path}")
            prometheus = Prometheus(path, library_mode=args.library)
            prometheus_instances.append(prometheus)

            try:
                report = prometheus.analyze()

                # Fetch GitHub metadata
                if is_github_url(path):
                    safe_print("[META] Fetching GitHub metadata...")
                    report.github = fetch_github_metadata(path)
                    if report.github.stars:
                        safe_print(f"       ⭐ {report.github.stars:,} | {report.github.language}")

                reports.append((report, prometheus))

                # Save individual JSON
                json_path = f"prometheus_{prometheus.repo_name}.json"
                prometheus.save_report(report, json_path)

            except Exception as e:
                safe_print(f"  ERROR: {e}")
                continue

        if reports:
            # Print summary
            safe_print("\n" + "=" * 70)
            safe_print("PROMETHEUS COMPARISON REPORT")
            safe_print("=" * 70)

            for report, prometheus in reports:
                name = report.github.full_name if report.github.full_name else prometheus.repo_name
                stars = f" ⭐{report.github.stars:,}" if report.github.stars else ""
                safe_print(
                    f"\n  {name}{stars}: {report.quadrant} (C:{report.complexity_score:.0f} R:{report.resilience_score:.0f})"
                )

            # Generate comparison HTML
            html_path = args.html or "prometheus_comparison.html"
            all_reports = [r[0] for r in reports]
            generate_quadrant_html(
                reports[0][0],
                html_path,
                repo_name="Comparison",
                comparison_reports=all_reports,
            )
            safe_print(f"\n  HTML: {html_path}")

        # Cleanup
        if not args.keep:
            for prometheus in prometheus_instances:
                prometheus.cleanup()

        return

    # Single repo mode
    prometheus = Prometheus(args.paths[0], library_mode=args.library)

    try:
        report = prometheus.analyze()

        # Fetch GitHub metadata
        if is_github_url(args.paths[0]):
            safe_print("[META] Fetching GitHub metadata...")
            report.github = fetch_github_metadata(args.paths[0])
            if report.github.stars:
                safe_print(
                    f"       ⭐ {report.github.stars:,} stars | {report.github.language} | {report.github.description[:60] if report.github.description else ''}..."
                )

        # Save JSON FIRST (before any emoji printing that might fail on Windows)
        json_path = args.output or f"prometheus_{prometheus.repo_name}.json"
        prometheus.save_report(report, json_path)

        safe_print("\n" + "=" * 70)
        safe_print("PROMETHEUS COMBINED FITNESS REPORT")
        if args.library:
            safe_print("(Library Mode - adjusted scoring for libraries)")
        safe_print("=" * 70)
        safe_print(f"\n{report.fitness_verdict}")

        safe_print(f"\nComplexity: {report.complexity_risk} (Score: {report.complexity_score:.0f})")
        safe_print(f"Resilience: {report.shield_rating} (Score: {report.resilience_score:.0f})")

        if report.priorities:
            safe_print("\nTop Priorities:")
            for p in report.priorities[:3]:
                safe_print(f"  [{p['category']}] {p['action']}")

        # Report output files
        safe_print("\n" + "-" * 70)
        safe_print("OUTPUT FILES")
        safe_print("-" * 70)

        safe_print(f"  JSON:     {json_path}")

        html_path = args.html or f"prometheus_{prometheus.repo_name}.html"
        generate_quadrant_html(report, html_path, repo_name=prometheus.repo_name)
        safe_print(f"  HTML:     {html_path}")

        # Run security analysis if requested
        if args.security:
            try:
                from sentinel import Sentinel

                safe_print("\n[SECURITY] Running security analysis...")
                sentinel = Sentinel(str(prometheus.codebase_path))
                security_report = sentinel.analyze()

                security_path = f"sentinel_{prometheus.repo_name}.json"
                sentinel.save_report(security_report, security_path)
                safe_print(f"  Security: {security_path}")
                safe_print(f"\n  Security Score: {security_report.security_score:.0f}/100")
                safe_print(
                    f"  Issues: {security_report.critical_count} Critical, "
                    f"{security_report.high_count} High, "
                    f"{security_report.medium_count} Medium"
                )
            except ImportError:
                safe_print("\n  [WARNING] sentinel.py not found - skipping security analysis")

        # Run code smell analysis if requested
        if args.smells:
            try:
                from scent_analyzer import ScentAnalyzer

                safe_print("\n[SCENT] Running code smell analysis...")
                scent = ScentAnalyzer(str(prometheus.codebase_path))
                smell_report = scent.analyze()

                smell_path = f"scent_{prometheus.repo_name}.json"
                scent.save_report(smell_report, smell_path)
                safe_print(f"  Smells:   {smell_path}")

                # Freshness indicator (Windows-safe)
                freshness_indicator = {
                    "FRESH": "[FRESH]",
                    "STALE": "[STALE]",
                    "MOLDY": "[MOLDY]",
                    "ROTTEN": "[ROTTEN]",
                }.get(smell_report.freshness_rating, "[?]")
                safe_print(f"\n  {freshness_indicator} Freshness: {smell_report.freshness_rating}")
                safe_print(
                    f"  Smell Score: {smell_report.overall_smell_score:.0f}/100 (lower is better)"
                )

                if smell_report.top_issues:
                    safe_print("\n  Top Issues:")
                    for issue in smell_report.top_issues[:3]:
                        safe_print(f"    - {issue['issue']}: {issue['count']} occurrences")
            except ImportError:
                safe_print("\n  [WARNING] scent_analyzer.py not found - skipping smell analysis")

        # Generate technical report if requested
        if args.report:
            report_path = args.report_path or f"prometheus_{prometheus.repo_name}_report.md"
            generate_technical_report(report, report_path)
            safe_print(f"  Report:   {report_path}")

        # Generate data dump if requested
        if args.dump:
            dump_path = args.dump_path or f"prometheus_{prometheus.repo_name}_data.txt"
            dump_raw_data(report, dump_path)
            safe_print(f"  Data:     {dump_path}")

    finally:
        # Cleanup cloned repo unless --keep was specified
        if not args.keep:
            prometheus.cleanup()
        elif prometheus.cloned and prometheus.temp_dir:
            safe_print(f"\n[KEEP] Repository kept at: {prometheus.temp_dir}")
            safe_print(f"       Re-run with: python prometheus.py {prometheus.temp_dir}")


if __name__ == "__main__":
    main()
