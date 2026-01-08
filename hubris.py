#!/usr/bin/env python3
"""
Hubris - Resilience Theater Detector
=====================================
Analyzes codebases for cargo-cult resilience patterns that add complexity
without adding reliability.

This is the main entry point. All detection logic is imported from:
- models.py: Data classes (HubrisReport, RetryIssue, etc.)
- patterns.py: Regex patterns for resilience anti-patterns
- detectors.py: Detector classes (RetryDetector, TimeoutDetector, etc.)
- fp_filter.py: False positive filtering
- design_patterns.py: Design pattern detector
- report.py: HTML report generation
"""

import json
from datetime import datetime
from pathlib import Path

# Import data models
from models import (
    HubrisReport,
    RetryIssue,
    TimeoutIssue,
    CircuitBreakerIssue,
    ExceptionIssue,
    FallbackIssue,
    DesignPatternIssue,
    PatternDetection,
)

# Import detectors
from detectors import (
    RetryDetector,
    TimeoutDetector,
    CircuitBreakerDetector,
    ExceptionDetector,
    LibraryDetector,
)

# Import design pattern detector
from design_patterns import DesignPatternDetector, _is_generated_file


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def _is_vendor_file(filepath: str) -> bool:
    """Check if file is from a vendor/third-party directory."""
    vendor_indicators = [
        "vendor/",
        "third_party/",
        "third-party/",
        "external/",
        "deps/",
        "lib/",
        "libs/",
        "packages/",
    ]
    filepath_lower = filepath.lower()
    return any(ind in filepath_lower for ind in vendor_indicators)


# =============================================================================
# MAIN ANALYZER
# =============================================================================


class Hubris:
    """
    Resilience Theater Detector

    Analyzes codebases for cargo-cult resilience patterns that add complexity
    without adding reliability.
    """

    # Languages with full resilience pattern support
    SUPPORTED_LANGUAGES = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "javascript",
        ".jsx": "javascript",
        ".tsx": "javascript",
        ".go": "go",
        ".java": "java",
        ".c": "c",
        ".h": "c",  # Treat .h as C by default
        ".cpp": "cpp",
        ".cc": "cpp",
        ".cxx": "cpp",
        ".hpp": "cpp",
        ".hxx": "cpp",
        ".C": "cpp",  # Uppercase .C is C++ by convention
        ".hh": "cpp",
    }

    # Languages we recognize but don't fully support - will return N/A
    UNSUPPORTED_LANGUAGES = {
        ".rs": "rust",
        ".rb": "ruby",
        ".php": "php",
        ".cs": "csharp",
        ".swift": "swift",
        ".kt": "kotlin",
        ".scala": "scala",
        ".ex": "elixir",
        ".exs": "elixir",
        ".erl": "erlang",
        ".hs": "haskell",
        ".ml": "ocaml",
        ".clj": "clojure",
        ".lua": "lua",
        ".pl": "perl",
        ".r": "r",
        ".R": "r",
        ".m": "objective-c",
        ".mm": "objective-c",
        ".asm": "assembly",
        ".s": "assembly",
        ".S": "assembly",
    }

    # Combined for backward compatibility
    LANGUAGE_EXTENSIONS = {**SUPPORTED_LANGUAGES, **UNSUPPORTED_LANGUAGES}

    def __init__(self, codebase_path: str):
        self.codebase_path = Path(codebase_path)

        # Initialize detectors
        self.retry_detector = RetryDetector()
        self.timeout_detector = TimeoutDetector()
        self.cb_detector = CircuitBreakerDetector()
        self.exception_detector = ExceptionDetector()
        self.library_detector = LibraryDetector()
        self.design_pattern_detector = DesignPatternDetector()

    def analyze(self) -> HubrisReport:
        """Run resilience theater analysis."""
        report = HubrisReport(
            codebase_path=str(self.codebase_path), timestamp=datetime.now().isoformat()
        )

        print(f"[HUBRIS] Scanning for resilience theater in {self.codebase_path}...")

        all_libraries = set()
        languages_found = {}  # language -> file_count
        unsupported_found = {}  # language -> file_count

        # First pass: count files by language to determine primary language
        for ext in list(self.SUPPORTED_LANGUAGES.keys()) + list(self.UNSUPPORTED_LANGUAGES.keys()):
            for filepath in self.codebase_path.rglob(f"*{ext}"):
                if any(
                    skip in str(filepath)
                    for skip in [
                        "node_modules",
                        "venv",
                        ".venv",
                        "__pycache__",
                        ".git",
                        "dist",
                        "build",
                        "vendor",
                        "test",
                        "tests",
                        "__tests__",
                        "spec",
                        "mock",
                        "fixture",
                        ".olympus_cache",
                    ]
                ):
                    continue

                if ext in self.SUPPORTED_LANGUAGES:
                    lang = self.SUPPORTED_LANGUAGES[ext]
                    languages_found[lang] = languages_found.get(lang, 0) + 1
                elif ext in self.UNSUPPORTED_LANGUAGES:
                    lang = self.UNSUPPORTED_LANGUAGES[ext]
                    unsupported_found[lang] = unsupported_found.get(lang, 0) + 1

        # Track languages in report
        report.languages_analyzed = sorted(languages_found.keys())
        report.languages_skipped = sorted(unsupported_found.keys())

        total_supported = sum(languages_found.values())
        total_unsupported = sum(unsupported_found.values())
        total_files = total_supported + total_unsupported

        if total_files > 0:
            report.supported_language_ratio = total_supported / total_files

        # Determine primary language
        all_langs = {**languages_found, **unsupported_found}
        if all_langs:
            report.primary_language = max(all_langs.keys(), key=lambda k: all_langs[k])

        # If majority of code is in unsupported languages, return N/A
        if report.supported_language_ratio < 0.2 and total_files > 0:
            print(f"  Primary language: {report.primary_language}")
            print(f"  Supported language ratio: {report.supported_language_ratio:.1%}")
            print("  Skipping detailed analysis - insufficient supported code")

            report.theater_ratio = "N/A"
            report.quadrant = "N/A"
            report.verdict = (
                f"Theater analysis not available. The codebase is primarily {report.primary_language} "
                f"({100 - report.supported_language_ratio*100:.0f}% of code), which is not yet fully supported. "
                f"Supported languages: Python, JavaScript, TypeScript, Go, Java, C/C++."
            )
            report.risk_level = "UNKNOWN"
            return report

        # Scan supported files
        for ext, language in self.SUPPORTED_LANGUAGES.items():
            for filepath in self.codebase_path.rglob(f"*{ext}"):
                # Skip non-source directories
                if any(
                    skip in str(filepath)
                    for skip in [
                        "node_modules",
                        "venv",
                        ".venv",
                        "__pycache__",
                        ".git",
                        "dist",
                        "build",
                        "vendor",
                        "test",
                        "tests",
                        "__tests__",
                        "spec",
                        "mock",
                        "fixture",
                        ".olympus_cache",
                    ]
                ):
                    continue

                try:
                    content = filepath.read_text(encoding="utf-8", errors="ignore")
                    rel_path = str(filepath.relative_to(self.codebase_path))

                    # Skip generated files
                    if _is_generated_file(rel_path, content):
                        continue

                    # Skip vendor/third-party files
                    if _is_vendor_file(rel_path):
                        continue

                    # Detect libraries
                    libs = self.library_detector.detect(content, language)
                    all_libraries.update(libs)

                    # Detect patterns and issues
                    patterns, issues = self.retry_detector.detect(content, rel_path, language)
                    report.patterns.extend(patterns)
                    report.retry_issues.extend(issues)

                    patterns, issues = self.timeout_detector.detect(content, rel_path, language)
                    report.patterns.extend(patterns)
                    report.timeout_issues.extend(issues)

                    patterns, issues = self.cb_detector.detect(content, rel_path, language)
                    report.patterns.extend(patterns)
                    report.circuit_breaker_issues.extend(issues)

                    patterns, issues = self.exception_detector.detect(content, rel_path, language)
                    report.patterns.extend(patterns)
                    report.exception_issues.extend(issues)

                    # Detect design pattern issues
                    dp_issues, dp_patterns = self.design_pattern_detector.detect(
                        content, rel_path, language
                    )
                    report.design_pattern_issues.extend(dp_issues)
                    report.design_patterns_detected.extend(dp_patterns)

                except Exception as e:
                    print(f"  Warning: Could not analyze {filepath}: {e}")

        report.resilience_libraries = sorted(all_libraries)
        report.library_count = len(all_libraries)

        # Calculate statistics
        self._calculate_statistics(report)

        # Determine quadrant and verdict
        self._determine_quadrant(report)

        # Generate recommendations
        self._generate_recommendations(report)

        print(f"  Patterns detected: {report.patterns_detected}")
        print(f"  Correctly implemented: {report.patterns_correct}")
        if isinstance(report.theater_ratio, str):
            print(f"  Theater ratio: {report.theater_ratio}")
        elif report.theater_ratio == float("inf"):
            print("  Theater ratio: ∞ (all patterns are cargo cult)")
        else:
            print(f"  Theater ratio: {report.theater_ratio:.2f}")
        print(f"  Verdict: {report.quadrant}")

        return report

    def _calculate_statistics(self, report: HubrisReport):
        """Calculate pattern statistics."""
        report.patterns_detected = len(report.patterns)
        report.patterns_correct = sum(1 for p in report.patterns if p.quality == "CORRECT")
        report.patterns_partial = sum(1 for p in report.patterns if p.quality == "PARTIAL")
        report.patterns_cargo_cult = sum(1 for p in report.patterns if p.quality == "CARGO_CULT")

        # Theater ratio: detected / correct (higher = more theater)
        if report.patterns_correct > 0:
            report.theater_ratio = report.patterns_detected / report.patterns_correct
        elif report.patterns_detected > 0:
            report.theater_ratio = float("inf")  # All patterns are cargo cult
        else:
            report.theater_ratio = 1.0  # No patterns = no theater

        # Count issues by severity
        all_issues = (
            report.retry_issues
            + report.timeout_issues
            + report.circuit_breaker_issues
            + report.exception_issues
            + report.fallback_issues
        )

        report.total_issues = len(all_issues)
        report.high_severity_count = sum(
            1 for i in all_issues if getattr(i, "severity", "") == "HIGH"
        )
        report.medium_severity_count = sum(
            1 for i in all_issues if getattr(i, "severity", "") == "MEDIUM"
        )
        report.low_severity_count = sum(
            1 for i in all_issues if getattr(i, "severity", "") == "LOW"
        )

        # Design pattern statistics
        report.design_pattern_issue_count = len(report.design_pattern_issues)
        report.design_patterns_detected = list(
            set(report.design_patterns_detected)
        )  # Unique patterns

        # Count by type
        for issue in report.design_pattern_issues:
            if issue.pattern_type == "singleton_abuse":
                report.singleton_abuse_count += 1
            elif issue.pattern_type == "god_class":
                report.god_class_count += 1
            elif issue.pattern_type in ("factory_overkill", "factory_abuse"):
                report.factory_abuse_count += 1
            elif issue.pattern_type == "inheritance_abuse":
                report.inheritance_abuse_count += 1
            elif issue.pattern_type == "observer_leak":
                report.observer_leak_count += 1

        # Add design pattern issues to severity counts
        report.high_severity_count += sum(
            1 for i in report.design_pattern_issues if i.severity == "HIGH"
        )
        report.medium_severity_count += sum(
            1 for i in report.design_pattern_issues if i.severity == "MEDIUM"
        )
        report.low_severity_count += sum(
            1 for i in report.design_pattern_issues if i.severity == "LOW"
        )
        report.total_issues += report.design_pattern_issue_count

    def _determine_quadrant(self, report: HubrisReport):
        """Determine the quadrant and verdict."""
        complexity = report.patterns_detected

        # FIX: Handle zero patterns case - no patterns means simple code, not cargo cult
        if complexity == 0:
            # No resilience patterns detected - this is simple code
            if report.high_severity_count == 0:
                report.quadrant = "SIMPLE"
                report.verdict = (
                    "No resilience patterns detected. This codebase takes a simple approach - "
                    "failures propagate naturally. This is often the right choice for libraries "
                    "and code that doesn't need defensive patterns."
                )
                report.risk_level = "LOW"
            else:
                # Has issues but no patterns - might have other problems
                report.quadrant = "SIMPLE"
                report.verdict = (
                    "No resilience patterns detected, but some code quality issues found. "
                    "Review the issues list for potential improvements."
                )
                report.risk_level = "LOW" if report.high_severity_count < 5 else "MEDIUM"
            return

        quality = report.patterns_correct / complexity

        # Thresholds - CALIBRATED based on analysis of 49 major open source projects
        low_complexity = complexity < 10  # Raised from 5 - most libs have 5-15 patterns
        high_quality = quality >= 0.4  # Lowered from 0.6 - even good code has some issues

        if low_complexity and high_quality:
            report.quadrant = "SIMPLE"
            report.verdict = (
                "Low defensive complexity, and what exists is implemented correctly. "
                "This code fails cleanly and is easy to debug. This is often the right choice."
            )
            report.risk_level = "LOW"

        elif not low_complexity and high_quality:
            report.quadrant = "BATTLE_HARDENED"
            report.verdict = (
                "High defensive complexity with correct implementation. "
                "This codebase has invested in resilience and done it right. "
                "Monitor for over-engineering but generally healthy."
            )
            report.risk_level = "LOW"

        elif low_complexity and not high_quality:
            report.quadrant = "CARGO_CULT"
            report.verdict = (
                "Few defensive patterns, but those present are implemented incorrectly. "
                "The added complexity provides no benefit. Consider removing these patterns "
                "until they can be implemented properly."
            )
            report.risk_level = "MEDIUM"

        else:  # not low_complexity and not high_quality
            report.quadrant = "CARGO_CULT"
            report.verdict = (
                "HIGH RISK: Many defensive patterns implemented incorrectly. "
                "This codebase has adopted resilience theater - patterns that look good "
                "but add failure modes rather than preventing them. "
                "The complexity likely makes the system LESS reliable."
            )
            report.risk_level = "CRITICAL" if report.theater_ratio > 3.0 else "HIGH"  # Raised from 2.5

        # Special case: library soup
        if report.library_count > 2:
            report.verdict += (
                f"\n\nWARNING: {report.library_count} different resilience libraries detected. "
                "This suggests copy-paste from multiple sources without a coherent strategy."
            )
            if report.risk_level == "LOW":
                report.risk_level = "MEDIUM"

    def _generate_recommendations(self, report: HubrisReport):
        """Generate actionable recommendations."""
        recs = []

        # Priority 1: High severity issues
        if report.high_severity_count > 0:
            recs.append(
                {
                    "priority": "CRITICAL",
                    "category": "High Severity Issues",
                    "message": f"{report.high_severity_count} high-severity issues found that likely cause production problems",
                    "actions": self._get_top_actions(report, "HIGH"),
                }
            )

        # Retry issues
        no_backoff = [i for i in report.retry_issues if i.issue_type == "no_backoff"]
        if no_backoff:
            recs.append(
                {
                    "priority": "HIGH",
                    "category": "Retry Without Backoff",
                    "message": f"{len(no_backoff)} retry implementations without exponential backoff",
                    "actions": [
                        "Add exponential backoff: delay = base_delay * (2 ** attempt)",
                        "Add jitter: delay * (1 + random.uniform(-0.1, 0.1))",
                        "Consider using tenacity or backoff libraries",
                    ],
                }
            )

        # Timeout issues
        missing_timeouts = [i for i in report.timeout_issues if i.issue_type == "missing"]
        if missing_timeouts:
            recs.append(
                {
                    "priority": "HIGH",
                    "category": "Missing Timeouts",
                    "message": f"{len(missing_timeouts)} network calls without timeout configuration",
                    "actions": [
                        "Add timeout to all HTTP clients: requests.get(url, timeout=(5, 30))",
                        "Use connect_timeout and read_timeout separately",
                        "Default suggestion: 5s connect, 30s read",
                    ],
                }
            )

        # Circuit breaker issues
        invisible_cb = [i for i in report.circuit_breaker_issues if i.issue_type == "invisible"]
        if invisible_cb:
            recs.append(
                {
                    "priority": "HIGH",
                    "category": "Invisible Circuit Breakers",
                    "message": f"{len(invisible_cb)} circuit breakers without metrics or logging",
                    "actions": [
                        "Add state change callbacks: on_state_change=lambda: metrics.emit(...)",
                        "Log circuit breaker state transitions",
                        "Expose circuit breaker state as a metric",
                    ],
                }
            )

        # Exception swallowing
        swallowed = [i for i in report.exception_issues if i.issue_type == "swallow"]
        if swallowed:
            recs.append(
                {
                    "priority": "HIGH",
                    "category": "Swallowed Exceptions",
                    "message": f"{len(swallowed)} locations where exceptions are silently ignored",
                    "actions": [
                        "At minimum, log the exception before ignoring",
                        "Consider whether the exception should propagate",
                        "Use specific exception types instead of bare except",
                    ],
                }
            )

        # Library soup
        if report.library_count > 2:
            recs.append(
                {
                    "priority": "MEDIUM",
                    "category": "Library Consolidation",
                    "message": f"{report.library_count} resilience libraries in use - consider consolidating",
                    "actions": [
                        "Pick one retry library and use it consistently",
                        "Document the resilience strategy in a central place",
                        f'Current libraries: {", ".join(report.resilience_libraries)}',
                    ],
                }
            )

        # If cargo cult, suggest simplification
        if (
            report.quadrant == "CARGO_CULT"
            and isinstance(report.theater_ratio, (int, float))
            and report.theater_ratio > 1.5
        ):
            recs.append(
                {
                    "priority": "MEDIUM",
                    "category": "Consider Simplification",
                    "message": "Resilience patterns are adding complexity without benefit",
                    "actions": [
                        "Consider removing retry/circuit breaker patterns until properly implemented",
                        "Simple code that fails obviously is better than complex code that fails silently",
                        "Start with timeouts and logging, add other patterns only when needed",
                    ],
                }
            )

        # Design pattern recommendations
        if report.singleton_abuse_count > 0:
            recs.append(
                {
                    "priority": "MEDIUM",
                    "category": "Singleton Abuse",
                    "message": f"{report.singleton_abuse_count} singleton anti-patterns detected",
                    "actions": [
                        "Replace singletons with dependency injection",
                        "Pass dependencies as constructor parameters",
                        "Use a DI container if you have many dependencies",
                    ],
                }
            )

        if report.god_class_count > 0:
            recs.append(
                {
                    "priority": "HIGH",
                    "category": "God Classes",
                    "message": f"{report.god_class_count} god classes with too many responsibilities",
                    "actions": [
                        "Apply Single Responsibility Principle (SRP)",
                        "Extract related methods into separate classes",
                        "Use composition to break up large classes",
                    ],
                }
            )

        if report.observer_leak_count > 0:
            recs.append(
                {
                    "priority": "HIGH",
                    "category": "Observer Pattern Leaks",
                    "message": f"{report.observer_leak_count} potential memory leaks from unsubscribed observers",
                    "actions": [
                        "Always unsubscribe in cleanup/destructor methods",
                        "Use WeakRef for observer references if possible",
                        "Track subscriptions and clean up on component unmount",
                    ],
                }
            )

        if report.inheritance_abuse_count > 0:
            recs.append(
                {
                    "priority": "MEDIUM",
                    "category": "Inheritance Abuse",
                    "message": f"{report.inheritance_abuse_count} cases of deep or multiple inheritance",
                    "actions": [
                        "Favor composition over inheritance",
                        "Use interfaces/protocols instead of base classes",
                        "Keep inheritance hierarchies shallow (max 3 levels)",
                    ],
                }
            )

        if report.factory_abuse_count > 0:
            recs.append(
                {
                    "priority": "LOW",
                    "category": "Factory Over-Engineering",
                    "message": f"{report.factory_abuse_count} over-engineered factory patterns",
                    "actions": [
                        "Use simple constructors or factory functions",
                        "Consider registry pattern for type-based factories",
                        'Ask: "Do I really need this abstraction?"',
                    ],
                }
            )

        report.recommendations = recs

    def _get_top_actions(self, report: HubrisReport, severity: str) -> list[str]:
        """Get top action items for a severity level."""
        actions = []

        all_issues = (
            report.retry_issues
            + report.timeout_issues
            + report.circuit_breaker_issues
            + report.exception_issues
        )

        for issue in all_issues[:5]:
            if getattr(issue, "severity", "") == severity:
                actions.append(f"{issue.file}:{issue.line} - {issue.description}")

        return actions[:5]

    def save_report(self, report: HubrisReport, output_path: str) -> str:
        """Save report to JSON."""

        def serialize(obj):
            if hasattr(obj, "__dataclass_fields__"):
                return {k: serialize(v) for k, v in obj.__dict__.items()}
            elif isinstance(obj, list):
                return [serialize(i) for i in obj]
            elif isinstance(obj, dict):
                return {k: serialize(v) for k, v in obj.items()}
            elif isinstance(obj, (set, frozenset)):
                return list(obj)
            elif isinstance(obj, float) and obj == float("inf"):
                return "Infinity"
            else:
                return obj

        report_dict = serialize(report)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report_dict, f, indent=2)

        return output_path


# =============================================================================
# HTML REPORT GENERATOR
# =============================================================================


def generate_hubris_html(report: HubrisReport, output_path: str, repo_name: str = "") -> str:
    """Generate visual HTML report."""

    # Determine colors based on quadrant
    quadrant_colors = {
        "SIMPLE": ("#22c55e", "#166534"),  # Green
        "BATTLE_HARDENED": ("#3b82f6", "#1e40af"),  # Blue
        "CARGO_CULT": ("#ef4444", "#991b1b"),  # Red
        "OVERENGINEERED": ("#eab308", "#a16207"),  # Yellow
    }

    primary_color, dark_color = quadrant_colors.get(report.quadrant, ("#64748b", "#334155"))

    # Build issues HTML
    issues_html = ""

    all_issues = []
    for issue in report.retry_issues:
        all_issues.append(("Retry", issue))
    for issue in report.timeout_issues:
        all_issues.append(("Timeout", issue))
    for issue in report.circuit_breaker_issues:
        all_issues.append(("Circuit Breaker", issue))
    for issue in report.exception_issues:
        all_issues.append(("Exception", issue))

    # Sort by severity
    severity_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    all_issues.sort(key=lambda x: severity_order.get(getattr(x[1], "severity", "LOW"), 3))

    for category, issue in all_issues[:20]:
        severity_color = {"HIGH": "#ef4444", "MEDIUM": "#eab308", "LOW": "#64748b"}.get(
            issue.severity, "#64748b"
        )

        issues_html += f"""
        <div class="issue">
            <div class="issue-header">
                <span class="severity" style="background: {severity_color}">{issue.severity}</span>
                <span class="category">{category}</span>
                <span class="location">{issue.file}:{issue.line}</span>
            </div>
            <div class="issue-body">{issue.description}</div>
        </div>
        """

    # Build recommendations HTML
    recs_html = ""
    for rec in report.recommendations[:5]:
        recs_html += f"""
        <div class="recommendation">
            <div class="rec-header">
                <span class="rec-priority">{rec['priority']}</span>
                <span class="rec-category">{rec['category']}</span>
            </div>
            <div class="rec-message">{rec['message']}</div>
            <ul class="rec-actions">
                {"".join(f'<li>{action}</li>' for action in rec.get('actions', [])[:3])}
            </ul>
        </div>
        """

    # Theater ratio display
    if report.theater_ratio == "N/A":
        theater_display = "N/A"
        theater_desc = "Unsupported language - analysis not available"
    elif isinstance(report.theater_ratio, float) and report.theater_ratio == float("inf"):
        theater_display = "∞"
        theater_desc = "All patterns are cargo cult"
    elif isinstance(report.theater_ratio, (int, float)):
        theater_display = f"{report.theater_ratio:.1f}"
        if report.theater_ratio <= 1.2:
            theater_desc = "Healthy - patterns are implemented correctly"
        elif report.theater_ratio <= 1.5:
            theater_desc = "Some room for improvement"
        elif report.theater_ratio <= 2.0:
            theater_desc = "Warning - many patterns incorrectly implemented"
        else:
            theater_desc = "Critical - resilience theater detected"
    else:
        theater_display = str(report.theater_ratio)
        theater_desc = "Unknown"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hubris Report - {repo_name or 'Resilience Theater Analysis'}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            min-height: 100vh;
            color: #e2e8f0;
            padding: 2rem;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}

        header {{
            text-align: center;
            margin-bottom: 2rem;
        }}

        header h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, {primary_color}, {dark_color});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        header .subtitle {{
            color: #94a3b8;
            margin-top: 0.5rem;
        }}

        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}

        .card {{
            background: rgba(30, 41, 59, 0.8);
            border-radius: 1rem;
            padding: 1.5rem;
            border: 1px solid rgba(148, 163, 184, 0.1);
        }}

        .card h2 {{
            font-size: 1rem;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 1rem;
        }}

        .quadrant-display {{
            text-align: center;
            padding: 2rem;
        }}

        .quadrant-name {{
            font-size: 2rem;
            font-weight: 700;
            color: {primary_color};
            margin-bottom: 0.5rem;
        }}

        .quadrant-desc {{
            color: #94a3b8;
            font-size: 0.9rem;
            line-height: 1.6;
        }}

        .metric {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.75rem 0;
            border-bottom: 1px solid rgba(148, 163, 184, 0.1);
        }}

        .metric:last-child {{
            border-bottom: none;
        }}

        .metric-label {{
            color: #94a3b8;
        }}

        .metric-value {{
            font-size: 1.25rem;
            font-weight: 600;
        }}

        .theater-ratio {{
            text-align: center;
            padding: 1.5rem;
        }}

        .theater-value {{
            font-size: 3rem;
            font-weight: 700;
            color: {primary_color};
        }}

        .theater-label {{
            color: #94a3b8;
            font-size: 0.9rem;
            margin-top: 0.5rem;
        }}

        .issue {{
            background: rgba(15, 23, 42, 0.6);
            border-radius: 0.5rem;
            padding: 1rem;
            margin-bottom: 0.75rem;
        }}

        .issue-header {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin-bottom: 0.5rem;
        }}

        .severity {{
            padding: 0.25rem 0.5rem;
            border-radius: 0.25rem;
            font-size: 0.75rem;
            font-weight: 600;
            color: white;
        }}

        .category {{
            color: #94a3b8;
            font-size: 0.85rem;
        }}

        .location {{
            color: #64748b;
            font-size: 0.8rem;
            font-family: monospace;
            margin-left: auto;
        }}

        .issue-body {{
            color: #cbd5e1;
            font-size: 0.9rem;
        }}

        .recommendation {{
            background: rgba(15, 23, 42, 0.6);
            border-radius: 0.5rem;
            padding: 1rem;
            margin-bottom: 0.75rem;
            border-left: 3px solid {primary_color};
        }}

        .rec-header {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin-bottom: 0.5rem;
        }}

        .rec-priority {{
            color: {primary_color};
            font-weight: 600;
            font-size: 0.85rem;
        }}

        .rec-category {{
            color: #e2e8f0;
            font-weight: 500;
        }}

        .rec-message {{
            color: #94a3b8;
            font-size: 0.9rem;
            margin-bottom: 0.75rem;
        }}

        .rec-actions {{
            margin-left: 1.5rem;
            color: #cbd5e1;
            font-size: 0.85rem;
        }}

        .rec-actions li {{
            margin-bottom: 0.25rem;
        }}

        .risk-badge {{
            display: inline-block;
            padding: 0.5rem 1rem;
            border-radius: 0.5rem;
            font-weight: 600;
            margin-top: 1rem;
        }}

        .risk-CRITICAL {{ background: #7f1d1d; color: #fecaca; }}
        .risk-HIGH {{ background: #991b1b; color: #fecaca; }}
        .risk-MEDIUM {{ background: #a16207; color: #fef3c7; }}
        .risk-LOW {{ background: #166534; color: #bbf7d0; }}

        .libraries {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
        }}

        .library-tag {{
            background: rgba(59, 130, 246, 0.2);
            color: #93c5fd;
            padding: 0.25rem 0.75rem;
            border-radius: 1rem;
            font-size: 0.85rem;
        }}

        footer {{
            text-align: center;
            margin-top: 2rem;
            color: #64748b;
            font-size: 0.85rem;
        }}

        .quadrant-chart {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            grid-template-rows: 1fr 1fr;
            gap: 2px;
            background: #334155;
            border-radius: 0.5rem;
            overflow: hidden;
            height: 200px;
            margin: 1rem 0;
        }}

        .quadrant-cell {{
            background: rgba(30, 41, 59, 0.9);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.75rem;
            color: #64748b;
            position: relative;
        }}

        .quadrant-cell.active {{
            background: {primary_color}22;
            color: {primary_color};
            font-weight: 600;
        }}

        .quadrant-cell.active::after {{
            content: '●';
            position: absolute;
            font-size: 1.5rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>HUBRIS</h1>
            <p class="subtitle">Resilience Theater Analysis{f' — {repo_name}' if repo_name else ''}</p>
        </header>

        <div class="grid">
            <div class="card quadrant-display">
                <div class="quadrant-name">{report.quadrant.replace('_', ' ')}</div>
                <div class="quadrant-desc">{report.verdict.split('.')[0]}.</div>
                <div class="risk-badge risk-{report.risk_level}">{report.risk_level} RISK</div>

                <div class="quadrant-chart">
                    <div class="quadrant-cell {'active' if report.quadrant == 'OVERENGINEERED' else ''}">OVERENGINEERED</div>
                    <div class="quadrant-cell {'active' if report.quadrant == 'BATTLE_HARDENED' else ''}">BATTLE-HARDENED</div>
                    <div class="quadrant-cell {'active' if report.quadrant == 'CARGO_CULT' else ''}">CARGO CULT</div>
                    <div class="quadrant-cell {'active' if report.quadrant == 'SIMPLE' else ''}">SIMPLE</div>
                </div>
            </div>

            <div class="card theater-ratio">
                <h2>Theater Ratio</h2>
                <div class="theater-value">{theater_display}</div>
                <div class="theater-label">{theater_desc}</div>
                <div style="margin-top: 1rem; font-size: 0.8rem; color: #64748b;">
                    patterns detected / patterns correct<br>
                    (lower is better, 1.0 is perfect)
                </div>
            </div>
        </div>

        <div class="grid">
            <div class="card">
                <h2>Pattern Analysis</h2>
                <div class="metric">
                    <span class="metric-label">Patterns Detected</span>
                    <span class="metric-value">{report.patterns_detected}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Correctly Implemented</span>
                    <span class="metric-value" style="color: #22c55e">{report.patterns_correct}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Partially Correct</span>
                    <span class="metric-value" style="color: #eab308">{report.patterns_partial}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Cargo Cult</span>
                    <span class="metric-value" style="color: #ef4444">{report.patterns_cargo_cult}</span>
                </div>
            </div>

            <div class="card">
                <h2>Issues by Severity</h2>
                <div class="metric">
                    <span class="metric-label">Total Issues</span>
                    <span class="metric-value">{report.total_issues}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">High Severity</span>
                    <span class="metric-value" style="color: #ef4444">{report.high_severity_count}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Medium Severity</span>
                    <span class="metric-value" style="color: #eab308">{report.medium_severity_count}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Low Severity</span>
                    <span class="metric-value" style="color: #64748b">{report.low_severity_count}</span>
                </div>
            </div>
        </div>

        {f'''
        <div class="card">
            <h2>Resilience Libraries Detected ({report.library_count})</h2>
            <div class="libraries">
                {"".join(f'<span class="library-tag">{lib}</span>' for lib in report.resilience_libraries)}
            </div>
            {'<p style="margin-top: 1rem; color: #f59e0b; font-size: 0.9rem;">⚠️ Multiple libraries suggest inconsistent resilience strategy</p>' if report.library_count > 2 else ''}
        </div>
        ''' if report.resilience_libraries else ''}

        {f'''
        <div class="card">
            <h2>Issues Found</h2>
            {issues_html if issues_html else '<p style="color: #64748b;">No issues detected</p>'}
        </div>
        ''' if all_issues else ''}

        {f'''
        <div class="card">
            <h2>Recommendations</h2>
            {recs_html if recs_html else '<p style="color: #64748b;">No recommendations</p>'}
        </div>
        ''' if report.recommendations else ''}

        <footer>
            <p>Hubris - Resilience Theater Detector</p>
            <p>"The complexity added by reliability patterns can introduce more failure modes than it prevents."</p>
            <p style="margin-top: 0.5rem;">Generated: {report.timestamp}</p>
        </footer>
    </div>
</body>
</html>
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    return output_path


# =============================================================================
# CLI
# =============================================================================


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Hubris - Resilience Theater Detector",
        epilog="""
Detects cargo-cult resilience patterns that add complexity without reliability.

Examples:
  python hubris.py /path/to/codebase
  python hubris.py https://github.com/owner/repo
  python hubris.py . --html report.html
        """,
    )
    parser.add_argument("path", help="Path to codebase")
    parser.add_argument("-o", "--output", help="Output JSON path")
    parser.add_argument("--html", help="Output HTML report path")

    args = parser.parse_args()

    hubris = Hubris(args.path)
    report = hubris.analyze()

    # Print results
    print("\n" + "=" * 70)
    print("HUBRIS - RESILIENCE THEATER REPORT")
    print("=" * 70)

    # Quadrant
    quadrant_emoji = {
        "SIMPLE": "[OK]",
        "BATTLE_HARDENED": "[++]",
        "CARGO_CULT": "[!!]",
        "OVERENGINEERED": "[~~]",
    }

    print(f"\n{quadrant_emoji.get(report.quadrant, '[??]')} Quadrant: {report.quadrant}")
    print(f"Risk Level: {report.risk_level}")

    # Handle N/A and infinity theater ratios
    if report.theater_ratio == "N/A":
        print("\nTheater Ratio: N/A (unsupported language)")
    elif isinstance(report.theater_ratio, float) and report.theater_ratio == float("inf"):
        print("\nTheater Ratio: ∞ (all patterns are cargo cult)")
    elif isinstance(report.theater_ratio, (int, float)):
        print(f"\nTheater Ratio: {report.theater_ratio:.2f}")
    else:
        print(f"\nTheater Ratio: {report.theater_ratio}")
    print(f"  Patterns detected: {report.patterns_detected}")
    print(f"  Correctly implemented: {report.patterns_correct}")
    print(f"  Cargo cult: {report.patterns_cargo_cult}")

    # Design pattern issues
    if report.design_pattern_issue_count > 0:
        print(f"\nDesign Pattern Issues: {report.design_pattern_issue_count}")
        if report.singleton_abuse_count:
            print(f"  Singleton abuse: {report.singleton_abuse_count}")
        if report.god_class_count:
            print(f"  God classes: {report.god_class_count}")
        if report.observer_leak_count:
            print(f"  Observer leaks: {report.observer_leak_count}")
        if report.inheritance_abuse_count:
            print(f"  Inheritance abuse: {report.inheritance_abuse_count}")
        if report.factory_abuse_count:
            print(f"  Factory over-engineering: {report.factory_abuse_count}")

    print(f"\n{report.verdict}")

    if report.total_issues > 0:
        print(
            f"\nIssues: {report.high_severity_count} HIGH, {report.medium_severity_count} MEDIUM, {report.low_severity_count} LOW"
        )

    if report.resilience_libraries:
        print(f"\nLibraries: {', '.join(report.resilience_libraries)}")

    if report.recommendations:
        print("\nTop Recommendations:")
        for rec in report.recommendations[:3]:
            print(f"  [{rec['priority']}] {rec['category']}: {rec['message']}")

    # Save outputs
    if args.output:
        hubris.save_report(report, args.output)
        print(f"\nJSON report: {args.output}")

    if args.html:
        repo_name = Path(args.path).name
        generate_hubris_html(report, args.html, repo_name)
        print(f"HTML report: {args.html}")


if __name__ == "__main__":
    main()
