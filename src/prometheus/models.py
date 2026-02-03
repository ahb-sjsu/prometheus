#!/usr/bin/env python3
"""
Hubris Data Models
==================
All dataclasses for the resilience theater analyzer.
"""

from dataclasses import dataclass, field


@dataclass
class RetryIssue:
    """A problematic retry implementation."""

    file: str
    line: int
    issue_type: str  # 'no_backoff', 'no_max', 'no_jitter', 'broad_exception'
    severity: str  # 'HIGH', 'MEDIUM', 'LOW'
    description: str
    code_snippet: str = ""
    fix_suggestion: str = ""


@dataclass
class TimeoutIssue:
    """A timeout configuration problem."""

    file: str
    line: int
    issue_type: str  # 'uncoordinated', 'too_long', 'missing', 'hardcoded'
    severity: str
    description: str
    timeout_value: float = 0
    context: str = ""


@dataclass
class CircuitBreakerIssue:
    """A circuit breaker implementation problem."""

    file: str
    line: int
    issue_type: str  # 'invisible', 'no_fallback', 'no_metrics', 'wrong_threshold'
    severity: str
    description: str


@dataclass
class ExceptionIssue:
    """A problematic exception handling pattern."""

    file: str
    line: int
    issue_type: str  # 'swallow', 'broad_catch', 'reraise_without_context'
    severity: str
    description: str
    exception_type: str = ""


@dataclass
class FallbackIssue:
    """A fallback implementation problem."""

    file: str
    line: int
    issue_type: str  # 'untested', 'silent', 'returns_none', 'stale_data'
    severity: str
    description: str


@dataclass
class DesignPatternIssue:
    """A detected design pattern anti-pattern."""

    pattern_type: str  # singleton_abuse, factory_overkill, god_class, etc.
    severity: str
    file: str
    line: int
    description: str
    recommendation: str
    code_snippet: str = ""


@dataclass
class PatternDetection:
    """A detected resilience pattern (good or bad)."""

    pattern_type: str  # 'retry', 'circuit_breaker', 'timeout', 'fallback', 'bulkhead'
    file: str
    line: int
    quality: str  # 'CORRECT', 'PARTIAL', 'CARGO_CULT'
    details: dict = field(default_factory=dict)


@dataclass
class HubrisReport:
    """Complete resilience theater analysis."""

    codebase_path: str
    timestamp: str

    # Pattern counts
    patterns_detected: int = 0
    patterns_correct: int = 0
    patterns_partial: int = 0
    patterns_cargo_cult: int = 0

    # The key metric
    theater_ratio: float | str = 0.0

    # Categorized issues
    retry_issues: list = field(default_factory=list)
    timeout_issues: list = field(default_factory=list)
    circuit_breaker_issues: list = field(default_factory=list)
    exception_issues: list = field(default_factory=list)
    fallback_issues: list = field(default_factory=list)
    design_pattern_issues: list = field(default_factory=list)

    # All detected patterns
    patterns: list = field(default_factory=list)
    design_patterns_detected: list = field(default_factory=list)

    # Libraries detected
    resilience_libraries: list = field(default_factory=list)
    library_count: int = 0

    # Verdict
    quadrant: str = ""
    verdict: str = ""
    risk_level: str = ""

    # Recommendations
    recommendations: list = field(default_factory=list)

    # Summary stats
    total_issues: int = 0
    high_severity_count: int = 0
    medium_severity_count: int = 0
    low_severity_count: int = 0

    # Design pattern stats
    design_pattern_issue_count: int = 0
    singleton_abuse_count: int = 0
    god_class_count: int = 0
    factory_abuse_count: int = 0
    inheritance_abuse_count: int = 0
    observer_leak_count: int = 0

    # Language tracking
    languages_analyzed: list = field(default_factory=list)
    languages_skipped: list = field(default_factory=list)
    primary_language: str = ""
    supported_language_ratio: float = 0.0
