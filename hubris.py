#!/usr/bin/env python3
"""
Hubris - Resilience Theater Detector
=====================================

Named after the Greek concept of excessive pride that leads to downfall.

Core thesis: "The complexity added by reliability patterns can introduce 
more failure modes than it prevents."

This analyzer detects CARGO CULT resilience - patterns that look defensive
but are implemented incorrectly, adding complexity without adding reliability.

Resilience Theater Patterns:
- Retry without backoff (causes thundering herd)
- Retry without max attempts (infinite loops)
- Uncoordinated timeouts (retry_count * timeout > caller_timeout)
- Invisible circuit breakers (no metrics/logging on state change)
- Broad exception swallowing (except Exception: pass)
- Untested fallbacks (fallback code not covered by tests)
- Library soup (multiple resilience libraries = complexity explosion)
- Cargo cult decorators (copied patterns without understanding)

The Quadrant:
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
"""

import re
import json
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime


# =============================================================================
# DATA MODELS
# =============================================================================


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
    theater_ratio: float = 0.0  # patterns_detected / patterns_correct

    # Categorized issues
    retry_issues: list = field(default_factory=list)
    timeout_issues: list = field(default_factory=list)
    circuit_breaker_issues: list = field(default_factory=list)
    exception_issues: list = field(default_factory=list)
    fallback_issues: list = field(default_factory=list)

    # All detected patterns
    patterns: list = field(default_factory=list)

    # Libraries detected
    resilience_libraries: list = field(default_factory=list)
    library_count: int = 0

    # Verdict
    quadrant: str = ""  # SIMPLE, BATTLE_HARDENED, OVERENGINEERED, CARGO_CULT
    verdict: str = ""
    risk_level: str = ""  # LOW, MEDIUM, HIGH, CRITICAL

    # Recommendations
    recommendations: list = field(default_factory=list)

    # Summary stats
    total_issues: int = 0
    high_severity_count: int = 0
    medium_severity_count: int = 0
    low_severity_count: int = 0


# =============================================================================
# PATTERN DETECTORS
# =============================================================================


class RetryDetector:
    """Detect retry patterns and evaluate their quality."""

    # Patterns that indicate retry logic
    RETRY_PATTERNS = {
        "python": {
            # Library-based retries
            "tenacity_decorator": re.compile(r"@retry\b|@tenacity\.retry"),
            "retrying_decorator": re.compile(r"@retrying\b"),
            "backoff_decorator": re.compile(r"@backoff\.(on_exception|on_predicate)"),
            # Manual retry loops
            "for_retry": re.compile(
                r"for\s+\w+\s+in\s+range\s*\(\s*\d+\s*\).*?(?:try|except)", re.DOTALL
            ),
            "while_retry": re.compile(
                r"while\s+(?:True|retry|attempt|tries).*?(?:try|except)", re.DOTALL
            ),
            # Quality indicators
            "exponential_backoff": re.compile(
                r"wait_exponential|exponential_backoff|backoff\.expo|\*\*\s*attempt|\*\*\s*retry|\*\s*2\s*\*\*"
            ),
            "jitter": re.compile(r"jitter|wait_random|random\.uniform|random\.random"),
            "max_retries": re.compile(
                r"max_retries|stop_after_attempt|max_tries|retry_limit|MAX_RETRIES"
            ),
            "sleep_call": re.compile(r"time\.sleep|asyncio\.sleep|await\s+sleep"),
        },
        "javascript": {
            "async_retry": re.compile(r"async-retry|p-retry|retry\s*\("),
            "for_retry": re.compile(r"for\s*\([^)]*(?:retry|attempt|tries)[^)]*\)"),
            "while_retry": re.compile(r"while\s*\([^)]*(?:retry|attempt|tries)[^)]*\)"),
            "exponential_backoff": re.compile(
                r"exponentialBackoff|Math\.pow\s*\(\s*2|backoff\s*\*\s*2"
            ),
            "jitter": re.compile(r"jitter|Math\.random"),
            "max_retries": re.compile(r"maxRetries|maxAttempts|MAX_RETRIES"),
        },
        "go": {
            "retry_lib": re.compile(
                r"cenkalti/backoff|avast/retry-go|hashicorp/go-retryablehttp"
            ),
            "for_retry": re.compile(r"for\s+\w+\s*:?=\s*0\s*;\s*\w+\s*<\s*\d+"),
            "exponential_backoff": re.compile(
                r"ExponentialBackOff|backoff\.Exponential|math\.Pow\(2"
            ),
            "jitter": re.compile(r"jitter|rand\.Float|rand\.Int"),
        },
        "java": {
            "resilience4j_retry": re.compile(r"@Retry|Retry\.of|RetryConfig"),
            "spring_retry": re.compile(r"@Retryable|RetryTemplate"),
            "failsafe": re.compile(r"Failsafe\.with|RetryPolicy\.builder"),
            "exponential_backoff": re.compile(
                r"exponentialBackoff|ExponentialBackoff|Math\.pow\(2"
            ),
            "jitter": re.compile(r"jitter|randomDelay|Random\(\)"),
        },
    }

    def detect(
        self, content: str, filepath: str, language: str
    ) -> tuple[list[PatternDetection], list[RetryIssue]]:
        """Detect retry patterns and issues."""
        patterns = []
        issues = []

        lang_patterns = self.RETRY_PATTERNS.get(
            language, self.RETRY_PATTERNS.get("python", {})
        )

        # Check for library-based retries
        for pattern_name, pattern in lang_patterns.items():
            if "decorator" in pattern_name or "lib" in pattern_name:
                for match in pattern.finditer(content):
                    line_num = content[: match.start()].count("\n") + 1

                    # Get surrounding context (20 lines)
                    lines = content.splitlines()
                    start = max(0, line_num - 5)
                    end = min(len(lines), line_num + 15)
                    context = "\n".join(lines[start:end])

                    quality = self._evaluate_retry_quality(context, lang_patterns)

                    patterns.append(
                        PatternDetection(
                            pattern_type="retry",
                            file=filepath,
                            line=line_num,
                            quality=quality,
                            details={"pattern": pattern_name, "library": True},
                        )
                    )

                    if quality != "CORRECT":
                        issues.extend(
                            self._generate_retry_issues(
                                filepath, line_num, context, quality, lang_patterns
                            )
                        )

        # Check for manual retry loops
        for pattern_name in ["for_retry", "while_retry"]:
            pattern = lang_patterns.get(pattern_name)
            if pattern:
                for match in pattern.finditer(content):
                    line_num = content[: match.start()].count("\n") + 1

                    lines = content.splitlines()
                    start = max(0, line_num - 2)
                    end = min(len(lines), line_num + 20)
                    context = "\n".join(lines[start:end])

                    quality = self._evaluate_retry_quality(context, lang_patterns)

                    patterns.append(
                        PatternDetection(
                            pattern_type="retry",
                            file=filepath,
                            line=line_num,
                            quality=quality,
                            details={
                                "pattern": pattern_name,
                                "library": False,
                                "manual": True,
                            },
                        )
                    )

                    if quality != "CORRECT":
                        issues.extend(
                            self._generate_retry_issues(
                                filepath, line_num, context, quality, lang_patterns
                            )
                        )

        return patterns, issues

    def _evaluate_retry_quality(self, context: str, lang_patterns: dict) -> str:
        """Evaluate the quality of a retry implementation."""
        has_backoff = bool(
            lang_patterns.get("exponential_backoff", re.compile(r"$^")).search(context)
        )
        has_jitter = bool(
            lang_patterns.get("jitter", re.compile(r"$^")).search(context)
        )
        has_max = bool(
            lang_patterns.get("max_retries", re.compile(r"$^")).search(context)
        )
        has_sleep = bool(
            lang_patterns.get("sleep_call", re.compile(r"sleep")).search(context)
        )

        # Check for broad exception catching
        broad_exception = bool(
            re.search(
                r"except\s*:|except\s+Exception\s*:|catch\s*\(\s*(?:Exception|Error|Throwable)\s*\)",
                context,
            )
        )

        if has_backoff and has_max and (has_jitter or not broad_exception):
            return "CORRECT"
        elif has_sleep and has_max:
            return "PARTIAL"
        elif has_sleep or has_max:
            return "PARTIAL"
        else:
            return "CARGO_CULT"

    def _generate_retry_issues(
        self, filepath: str, line: int, context: str, quality: str, lang_patterns: dict
    ) -> list[RetryIssue]:
        """Generate specific issues for a retry pattern."""
        issues = []

        has_backoff = bool(
            lang_patterns.get("exponential_backoff", re.compile(r"$^")).search(context)
        )
        has_jitter = bool(
            lang_patterns.get("jitter", re.compile(r"$^")).search(context)
        )
        has_max = bool(
            lang_patterns.get("max_retries", re.compile(r"$^")).search(context)
        )
        has_sleep = bool(
            lang_patterns.get("sleep_call", re.compile(r"sleep")).search(context)
        )

        if not has_backoff and not has_sleep:
            issues.append(
                RetryIssue(
                    file=filepath,
                    line=line,
                    issue_type="no_backoff",
                    severity="HIGH",
                    description="Retry without backoff - will cause thundering herd on failure",
                    fix_suggestion="Add exponential backoff: time.sleep(base_delay * (2 ** attempt))",
                )
            )

        if not has_max:
            issues.append(
                RetryIssue(
                    file=filepath,
                    line=line,
                    issue_type="no_max",
                    severity="HIGH",
                    description="Retry without maximum attempts - may retry forever",
                    fix_suggestion="Add max_retries limit (typically 3-5 attempts)",
                )
            )

        if has_backoff and not has_jitter:
            issues.append(
                RetryIssue(
                    file=filepath,
                    line=line,
                    issue_type="no_jitter",
                    severity="MEDIUM",
                    description="Backoff without jitter - synchronized retries can still overwhelm",
                    fix_suggestion="Add random jitter: delay * (1 + random.uniform(-0.1, 0.1))",
                )
            )

        return issues


class TimeoutDetector:
    """Detect timeout configurations and evaluate their quality."""

    TIMEOUT_PATTERNS = {
        "python": {
            "requests_timeout": re.compile(
                r"requests\.(get|post|put|delete|patch)\s*\([^)]*timeout\s*=\s*(\d+(?:\.\d+)?|None)"
            ),
            "requests_no_timeout": re.compile(
                r"requests\.(get|post|put|delete|patch)\s*\([^)]*\)(?![^)]*timeout)"
            ),
            "httpx_timeout": re.compile(r"httpx\.\w+\s*\([^)]*timeout\s*="),
            "aiohttp_timeout": re.compile(
                r"aiohttp\.ClientTimeout|timeout\s*=\s*aiohttp"
            ),
            "socket_timeout": re.compile(
                r"socket\.setdefaulttimeout|\.settimeout\s*\("
            ),
            "generic_timeout": re.compile(r"timeout\s*=\s*(\d+(?:\.\d+)?|None)"),
            "timeout_none": re.compile(r"timeout\s*=\s*None"),
        },
        "javascript": {
            "axios_timeout": re.compile(r"axios\.\w+\s*\([^)]*timeout\s*:"),
            "fetch_signal": re.compile(r"AbortController|signal\s*:"),
            "generic_timeout": re.compile(r"timeout\s*:\s*(\d+)"),
        },
        "go": {
            "http_timeout": re.compile(r"&http\.Client\s*\{[^}]*Timeout\s*:"),
            "context_timeout": re.compile(
                r"context\.WithTimeout|context\.WithDeadline"
            ),
            "no_timeout": re.compile(r"http\.DefaultClient|&http\.Client\s*\{\s*\}"),
        },
        "java": {
            "okhttp_timeout": re.compile(
                r"\.connectTimeout\(|\.readTimeout\(|\.writeTimeout\("
            ),
            "spring_timeout": re.compile(r"@Timeout|\.timeout\("),
            "socket_timeout": re.compile(r"setSoTimeout|setConnectTimeout"),
        },
    }

    def detect(
        self, content: str, filepath: str, language: str
    ) -> tuple[list[PatternDetection], list[TimeoutIssue]]:
        """Detect timeout patterns and issues."""
        patterns = []
        issues = []

        lang_patterns = self.TIMEOUT_PATTERNS.get(
            language, self.TIMEOUT_PATTERNS.get("python", {})
        )

        # Check for missing timeouts on network calls
        no_timeout_pattern = lang_patterns.get(
            "requests_no_timeout"
        ) or lang_patterns.get("no_timeout")
        if no_timeout_pattern:
            for match in no_timeout_pattern.finditer(content):
                line_num = content[: match.start()].count("\n") + 1

                # Check if timeout is set elsewhere in context
                lines = content.splitlines()
                start = max(0, line_num - 10)
                end = min(len(lines), line_num + 5)
                context = "\n".join(lines[start:end])

                if "timeout" not in context.lower():
                    patterns.append(
                        PatternDetection(
                            pattern_type="timeout",
                            file=filepath,
                            line=line_num,
                            quality="CARGO_CULT",
                            details={"issue": "missing_timeout"},
                        )
                    )

                    issues.append(
                        TimeoutIssue(
                            file=filepath,
                            line=line_num,
                            issue_type="missing",
                            severity="HIGH",
                            description="Network call without timeout - can hang indefinitely",
                            context=match.group(0)[:100],
                        )
                    )

        # Check for timeout=None (explicit infinite timeout)
        timeout_none = lang_patterns.get("timeout_none")
        if timeout_none:
            for match in timeout_none.finditer(content):
                line_num = content[: match.start()].count("\n") + 1

                patterns.append(
                    PatternDetection(
                        pattern_type="timeout",
                        file=filepath,
                        line=line_num,
                        quality="CARGO_CULT",
                        details={"issue": "explicit_none"},
                    )
                )

                issues.append(
                    TimeoutIssue(
                        file=filepath,
                        line=line_num,
                        issue_type="explicit_none",
                        severity="HIGH",
                        description="Explicit timeout=None disables timeout - can hang indefinitely",
                    )
                )

        # Check for configured timeouts (these are good)
        for pattern_name, pattern in lang_patterns.items():
            if "no_timeout" in pattern_name or "none" in pattern_name:
                continue

            for match in pattern.finditer(content):
                line_num = content[: match.start()].count("\n") + 1

                # Extract timeout value if present
                timeout_val = None
                if match.groups():
                    try:
                        timeout_val = float(match.group(1) if match.lastindex else 0)
                    except (ValueError, TypeError):
                        pass

                quality = "CORRECT"

                # Check for very long timeouts
                if timeout_val and timeout_val > 120:
                    quality = "PARTIAL"
                    issues.append(
                        TimeoutIssue(
                            file=filepath,
                            line=line_num,
                            issue_type="too_long",
                            severity="MEDIUM",
                            description=f"Timeout of {timeout_val}s is very long - consider shorter timeout with retry",
                            timeout_value=timeout_val,
                        )
                    )

                patterns.append(
                    PatternDetection(
                        pattern_type="timeout",
                        file=filepath,
                        line=line_num,
                        quality=quality,
                        details={"timeout_value": timeout_val},
                    )
                )

        return patterns, issues


class CircuitBreakerDetector:
    """Detect circuit breaker patterns and evaluate their quality."""

    CB_PATTERNS = {
        "python": {
            "pybreaker": re.compile(
                r"from\s+pybreaker|import\s+pybreaker|CircuitBreaker\s*\("
            ),
            "circuitbreaker": re.compile(r"@circuit|from\s+circuitbreaker"),
            "custom_cb": re.compile(r"class\s+\w*CircuitBreaker|OPEN|CLOSED|HALF_OPEN"),
            # Quality indicators
            "cb_listener": re.compile(r"listeners?\s*=|on_state_change|add_listener"),
            "cb_metrics": re.compile(r"prometheus|statsd|metrics\.emit|counter\.inc"),
            "cb_fallback": re.compile(r"fallback|default_value|on_failure"),
            "cb_threshold": re.compile(r"fail_max|failure_threshold|error_threshold"),
        },
        "javascript": {
            "opossum": re.compile(r'from\s+[\'"]opossum|require\s*\([\'"]opossum'),
            "brakes": re.compile(r'from\s+[\'"]brakes|require\s*\([\'"]brakes'),
            "cb_fallback": re.compile(r"\.fallback\s*\(|fallbackFunction"),
            "cb_events": re.compile(r'\.on\s*\([\'"](?:open|close|halfOpen)'),
        },
        "java": {
            "resilience4j_cb": re.compile(
                r"@CircuitBreaker|CircuitBreakerConfig|CircuitBreakerRegistry"
            ),
            "hystrix": re.compile(r"@HystrixCommand|HystrixCircuitBreaker"),
            "cb_fallback": re.compile(r"fallbackMethod|@Fallback"),
            "cb_metrics": re.compile(r"CircuitBreakerMetrics|HealthIndicator"),
        },
        "go": {
            "gobreaker": re.compile(
                r"gobreaker\.NewCircuitBreaker|gobreaker\.Settings"
            ),
            "hystrix_go": re.compile(r"hystrix\.Do|hystrix\.ConfigureCommand"),
            "cb_on_state": re.compile(r"OnStateChange|ReadyToTrip"),
        },
    }

    def detect(
        self, content: str, filepath: str, language: str
    ) -> tuple[list[PatternDetection], list[CircuitBreakerIssue]]:
        """Detect circuit breaker patterns and issues."""
        patterns = []
        issues = []

        lang_patterns = self.CB_PATTERNS.get(
            language, self.CB_PATTERNS.get("python", {})
        )

        # Look for circuit breaker implementations
        for pattern_name, pattern in lang_patterns.items():
            if any(
                x in pattern_name
                for x in [
                    "fallback",
                    "metrics",
                    "listener",
                    "events",
                    "threshold",
                    "on_state",
                ]
            ):
                continue  # Skip quality indicators

            for match in pattern.finditer(content):
                line_num = content[: match.start()].count("\n") + 1

                # Get context for quality evaluation
                lines = content.splitlines()
                start = max(0, line_num - 5)
                end = min(len(lines), line_num + 30)
                context = "\n".join(lines[start:end])

                quality = self._evaluate_cb_quality(context, lang_patterns)

                patterns.append(
                    PatternDetection(
                        pattern_type="circuit_breaker",
                        file=filepath,
                        line=line_num,
                        quality=quality,
                        details={"library": pattern_name},
                    )
                )

                if quality != "CORRECT":
                    issues.extend(
                        self._generate_cb_issues(
                            filepath, line_num, context, quality, lang_patterns
                        )
                    )

        return patterns, issues

    def _evaluate_cb_quality(self, context: str, lang_patterns: dict) -> str:
        """Evaluate circuit breaker implementation quality."""
        has_fallback = any(
            lang_patterns.get(p, re.compile(r"$^")).search(context)
            for p in ["cb_fallback", "fallback"]
        )
        has_metrics = any(
            lang_patterns.get(p, re.compile(r"$^")).search(context)
            for p in ["cb_metrics", "cb_listener", "cb_events", "cb_on_state"]
        )
        has_threshold = bool(
            lang_patterns.get("cb_threshold", re.compile(r"threshold|fail_max")).search(
                context
            )
        )

        if has_fallback and has_metrics:
            return "CORRECT"
        elif has_fallback or has_metrics or has_threshold:
            return "PARTIAL"
        else:
            return "CARGO_CULT"

    def _generate_cb_issues(
        self, filepath: str, line: int, context: str, quality: str, lang_patterns: dict
    ) -> list[CircuitBreakerIssue]:
        """Generate circuit breaker issues."""
        issues = []

        has_metrics = any(
            lang_patterns.get(p, re.compile(r"$^")).search(context)
            for p in ["cb_metrics", "cb_listener", "cb_events", "cb_on_state"]
        )

        has_fallback = any(
            lang_patterns.get(p, re.compile(r"$^")).search(context)
            for p in ["cb_fallback", "fallback"]
        )

        if not has_metrics:
            issues.append(
                CircuitBreakerIssue(
                    file=filepath,
                    line=line,
                    issue_type="invisible",
                    severity="HIGH",
                    description="Circuit breaker without metrics/logging - state changes are invisible to operators",
                )
            )

        if not has_fallback:
            issues.append(
                CircuitBreakerIssue(
                    file=filepath,
                    line=line,
                    issue_type="no_fallback",
                    severity="MEDIUM",
                    description="Circuit breaker without fallback - open circuit will just throw exceptions",
                )
            )

        return issues


class ExceptionDetector:
    """Detect problematic exception handling patterns."""

    EXCEPTION_PATTERNS = {
        "python": {
            # Bad patterns
            "bare_except": re.compile(r"except\s*:"),
            "broad_except": re.compile(
                r"except\s+(?:Exception|BaseException)\s*(?:as\s+\w+)?:"
            ),
            "except_pass": re.compile(r"except[^:]*:\s*\n\s*pass\b"),
            "except_continue": re.compile(r"except[^:]*:\s*\n\s*continue\b"),
            # Good patterns
            "specific_except": re.compile(
                r"except\s+(?!Exception|BaseException)\w+(?:Error|Exception)"
            ),
            "except_log": re.compile(r"except[^:]*:\s*\n[^\n]*(?:log|logger|logging)"),
            "except_raise": re.compile(r"except[^:]*:\s*\n[^\n]*raise\b"),
        },
        "javascript": {
            "empty_catch": re.compile(r"catch\s*\([^)]*\)\s*\{\s*\}"),
            "catch_all": re.compile(r"catch\s*\(\s*(?:e|err|error|ex)?\s*\)\s*\{"),
            "catch_log": re.compile(
                r"catch\s*\([^)]*\)\s*\{[^}]*console\.(log|error|warn)"
            ),
        },
        "go": {
            "ignore_error": re.compile(r"\w+,\s*_\s*:?=|_\s*=\s*\w+\("),
            "empty_if_err": re.compile(r"if\s+err\s*!=\s*nil\s*\{\s*\}"),
        },
        "java": {
            "empty_catch": re.compile(r"catch\s*\([^)]+\)\s*\{\s*\}"),
            "catch_throwable": re.compile(r"catch\s*\(\s*(?:Throwable|Exception)\s+"),
            "swallow_exception": re.compile(
                r"catch\s*\([^)]+\)\s*\{[^}]*(?:// *ignore|// *TODO)"
            ),
        },
    }

    def detect(
        self, content: str, filepath: str, language: str
    ) -> tuple[list[PatternDetection], list[ExceptionIssue]]:
        """Detect exception handling patterns and issues."""
        patterns = []
        issues = []

        lang_patterns = self.EXCEPTION_PATTERNS.get(
            language, self.EXCEPTION_PATTERNS.get("python", {})
        )

        # Check for bad patterns
        bad_patterns = [
            "bare_except",
            "broad_except",
            "except_pass",
            "except_continue",
            "empty_catch",
            "catch_all",
            "ignore_error",
            "empty_if_err",
            "catch_throwable",
            "swallow_exception",
        ]

        for pattern_name in bad_patterns:
            pattern = lang_patterns.get(pattern_name)
            if not pattern:
                continue

            for match in pattern.finditer(content):
                line_num = content[: match.start()].count("\n") + 1

                # Check if it's mitigated by logging
                lines = content.splitlines()
                start = max(0, line_num - 1)
                end = min(len(lines), line_num + 5)
                context = "\n".join(lines[start:end])

                has_logging = bool(
                    re.search(
                        r"log|logger|logging|console\.|print|fmt\.Print",
                        context,
                        re.IGNORECASE,
                    )
                )
                has_raise = bool(
                    re.search(r"\braise\b|\bthrow\b|return\s+err", context)
                )

                if has_logging or has_raise:
                    quality = "PARTIAL"
                    severity = "LOW"
                else:
                    quality = "CARGO_CULT"
                    severity = (
                        "HIGH"
                        if "pass" in pattern_name
                        or "empty" in pattern_name
                        or "swallow" in pattern_name
                        else "MEDIUM"
                    )

                patterns.append(
                    PatternDetection(
                        pattern_type="exception_handling",
                        file=filepath,
                        line=line_num,
                        quality=quality,
                        details={"pattern": pattern_name},
                    )
                )

                if quality == "CARGO_CULT":
                    issues.append(
                        ExceptionIssue(
                            file=filepath,
                            line=line_num,
                            issue_type=self._map_issue_type(pattern_name),
                            severity=severity,
                            description=self._get_issue_description(pattern_name),
                        )
                    )

        return patterns, issues

    def _map_issue_type(self, pattern_name: str) -> str:
        """Map pattern name to issue type."""
        if (
            "pass" in pattern_name
            or "empty" in pattern_name
            or "swallow" in pattern_name
        ):
            return "swallow"
        elif (
            "bare" in pattern_name
            or "broad" in pattern_name
            or "all" in pattern_name
            or "throwable" in pattern_name
        ):
            return "broad_catch"
        elif "ignore" in pattern_name:
            return "ignored_error"
        return "other"

    def _get_issue_description(self, pattern_name: str) -> str:
        """Get description for issue type."""
        descriptions = {
            "bare_except": "Bare except catches everything including KeyboardInterrupt and SystemExit",
            "broad_except": "Catching Exception hides the specific error type and makes debugging harder",
            "except_pass": "Exception swallowed silently - errors will be invisible",
            "except_continue": "Exception swallowed in loop - may process corrupted state",
            "empty_catch": "Empty catch block - errors are silently ignored",
            "catch_all": "Catching all exceptions without specific handling",
            "ignore_error": "Error return value explicitly ignored",
            "empty_if_err": "Error checked but not handled",
            "catch_throwable": "Catching Throwable is too broad - catches JVM errors",
            "swallow_exception": "Exception intentionally swallowed",
        }
        return descriptions.get(pattern_name, "Problematic exception handling pattern")


class LibraryDetector:
    """Detect resilience libraries in use."""

    LIBRARIES = {
        "python": {
            "tenacity": re.compile(r"from\s+tenacity|import\s+tenacity"),
            "retrying": re.compile(r"from\s+retrying|import\s+retrying"),
            "backoff": re.compile(r"from\s+backoff|import\s+backoff"),
            "pybreaker": re.compile(r"from\s+pybreaker|import\s+pybreaker"),
            "circuitbreaker": re.compile(
                r"from\s+circuitbreaker|import\s+circuitbreaker"
            ),
            "pyfailsafe": re.compile(r"from\s+failsafe|import\s+failsafe"),
            "timeout_decorator": re.compile(
                r"from\s+timeout_decorator|import\s+timeout_decorator"
            ),
            "async_timeout": re.compile(r"from\s+async_timeout|import\s+async_timeout"),
            "aiobreaker": re.compile(r"from\s+aiobreaker|import\s+aiobreaker"),
        },
        "javascript": {
            "opossum": re.compile(r'[\'"]opossum[\'"]'),
            "cockatiel": re.compile(r'[\'"]cockatiel[\'"]'),
            "async-retry": re.compile(r'[\'"]async-retry[\'"]'),
            "p-retry": re.compile(r'[\'"]p-retry[\'"]'),
            "brakes": re.compile(r'[\'"]brakes[\'"]'),
        },
        "java": {
            "resilience4j": re.compile(r"io\.github\.resilience4j|resilience4j"),
            "hystrix": re.compile(r"com\.netflix\.hystrix|HystrixCommand"),
            "failsafe": re.compile(r"net\.jodah\.failsafe|dev\.failsafe"),
            "spring-retry": re.compile(r"org\.springframework\.retry"),
        },
        "go": {
            "gobreaker": re.compile(r"sony/gobreaker"),
            "go-retryablehttp": re.compile(r"hashicorp/go-retryablehttp"),
            "backoff": re.compile(r"cenkalti/backoff"),
            "retry-go": re.compile(r"avast/retry-go"),
            "hystrix-go": re.compile(r"afex/hystrix-go"),
        },
    }

    def detect(self, content: str, language: str) -> list[str]:
        """Detect which resilience libraries are in use."""
        found = []

        lang_libs = self.LIBRARIES.get(language, {})
        for lib_name, pattern in lang_libs.items():
            if pattern.search(content):
                found.append(lib_name)

        return found


# =============================================================================
# MAIN ANALYZER
# =============================================================================


class Hubris:
    """
    Resilience Theater Detector

    Analyzes codebases for cargo-cult resilience patterns that add complexity
    without adding reliability.
    """

    LANGUAGE_EXTENSIONS = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "javascript",
        ".jsx": "javascript",
        ".tsx": "javascript",
        ".go": "go",
        ".java": "java",
        ".rs": "rust",
        ".rb": "ruby",
    }

    def __init__(self, codebase_path: str):
        self.codebase_path = Path(codebase_path)

        # Initialize detectors
        self.retry_detector = RetryDetector()
        self.timeout_detector = TimeoutDetector()
        self.cb_detector = CircuitBreakerDetector()
        self.exception_detector = ExceptionDetector()
        self.library_detector = LibraryDetector()

    def analyze(self) -> HubrisReport:
        """Run resilience theater analysis."""
        report = HubrisReport(
            codebase_path=str(self.codebase_path), timestamp=datetime.now().isoformat()
        )

        print(f"[HUBRIS] Scanning for resilience theater in {self.codebase_path}...")

        all_libraries = set()

        # Scan all files
        for ext, language in self.LANGUAGE_EXTENSIONS.items():
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
                    ]
                ):
                    continue

                try:
                    content = filepath.read_text(encoding="utf-8", errors="ignore")
                    rel_path = str(filepath.relative_to(self.codebase_path))

                    # Detect libraries
                    libs = self.library_detector.detect(content, language)
                    all_libraries.update(libs)

                    # Detect patterns and issues
                    patterns, issues = self.retry_detector.detect(
                        content, rel_path, language
                    )
                    report.patterns.extend(patterns)
                    report.retry_issues.extend(issues)

                    patterns, issues = self.timeout_detector.detect(
                        content, rel_path, language
                    )
                    report.patterns.extend(patterns)
                    report.timeout_issues.extend(issues)

                    patterns, issues = self.cb_detector.detect(
                        content, rel_path, language
                    )
                    report.patterns.extend(patterns)
                    report.circuit_breaker_issues.extend(issues)

                    patterns, issues = self.exception_detector.detect(
                        content, rel_path, language
                    )
                    report.patterns.extend(patterns)
                    report.exception_issues.extend(issues)

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
        print(f"  Theater ratio: {report.theater_ratio:.2f}")
        print(f"  Verdict: {report.quadrant}")

        return report

    def _calculate_statistics(self, report: HubrisReport):
        """Calculate pattern statistics."""
        report.patterns_detected = len(report.patterns)
        report.patterns_correct = sum(
            1 for p in report.patterns if p.quality == "CORRECT"
        )
        report.patterns_partial = sum(
            1 for p in report.patterns if p.quality == "PARTIAL"
        )
        report.patterns_cargo_cult = sum(
            1 for p in report.patterns if p.quality == "CARGO_CULT"
        )

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

    def _determine_quadrant(self, report: HubrisReport):
        """Determine the quadrant and verdict."""
        complexity = report.patterns_detected
        quality = report.patterns_correct / max(1, report.patterns_detected)

        # Thresholds
        low_complexity = complexity < 5
        high_quality = quality >= 0.6

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
            report.risk_level = "CRITICAL" if report.theater_ratio > 2.5 else "HIGH"

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
        missing_timeouts = [
            i for i in report.timeout_issues if i.issue_type == "missing"
        ]
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
        invisible_cb = [
            i for i in report.circuit_breaker_issues if i.issue_type == "invisible"
        ]
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
        if report.quadrant == "CARGO_CULT" and report.theater_ratio > 1.5:
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


def generate_hubris_html(
    report: HubrisReport, output_path: str, repo_name: str = ""
) -> str:
    """Generate visual HTML report."""

    # Determine colors based on quadrant
    quadrant_colors = {
        "SIMPLE": ("#22c55e", "#166534"),  # Green
        "BATTLE_HARDENED": ("#3b82f6", "#1e40af"),  # Blue
        "CARGO_CULT": ("#ef4444", "#991b1b"),  # Red
        "OVERENGINEERED": ("#eab308", "#a16207"),  # Yellow
    }

    primary_color, dark_color = quadrant_colors.get(
        report.quadrant, ("#64748b", "#334155")
    )

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
    all_issues.sort(
        key=lambda x: severity_order.get(getattr(x[1], "severity", "LOW"), 3)
    )

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
    if report.theater_ratio == float("inf"):
        theater_display = "∞"
        theater_desc = "All patterns are cargo cult"
    else:
        theater_display = f"{report.theater_ratio:.1f}"
        if report.theater_ratio <= 1.2:
            theater_desc = "Healthy - patterns are implemented correctly"
        elif report.theater_ratio <= 1.5:
            theater_desc = "Some room for improvement"
        elif report.theater_ratio <= 2.0:
            theater_desc = "Warning - many patterns incorrectly implemented"
        else:
            theater_desc = "Critical - resilience theater detected"

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
        "SIMPLE": "🟢",
        "BATTLE_HARDENED": "🔵",
        "CARGO_CULT": "🔴",
        "OVERENGINEERED": "🟡",
    }

    print(f"\n{quadrant_emoji.get(report.quadrant, '⚪')} Quadrant: {report.quadrant}")
    print(f"Risk Level: {report.risk_level}")

    print(f"\nTheater Ratio: {report.theater_ratio:.2f}")
    print(f"  Patterns detected: {report.patterns_detected}")
    print(f"  Correctly implemented: {report.patterns_correct}")
    print(f"  Cargo cult: {report.patterns_cargo_cult}")

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
