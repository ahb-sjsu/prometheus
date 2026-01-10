#!/usr/bin/env python3
"""
Hubris Detectors
================
Pattern detectors for resilience anti-patterns.

Uses a base class to eliminate repetition across detector types.
"""

import re

from .fp_filter import filter_matches
from .models import CircuitBreakerIssue, ExceptionIssue, PatternDetection, RetryIssue, TimeoutIssue
from .patterns import (
    CB_QUALITY,
    CB_TRIGGERS,
    CIRCUIT_BREAKER_PATTERNS,
    EXCEPTION_ANTI_PATTERNS,
    EXCEPTION_PATTERNS,
    LIBRARY_PATTERNS,
    RETRY_PATTERNS,
    RETRY_QUALITY,
    RETRY_TRIGGERS,
    TIMEOUT_ISSUES,
    TIMEOUT_PATTERNS,
)


class BaseDetector:
    """Base class for all pattern detectors."""

    PATTERNS: dict = {}
    TRIGGERS: set = set()
    QUALITY_INDICATORS: set = set()
    PATTERN_TYPE: str = ""

    def get_patterns(self, language: str) -> dict:
        """Get patterns for a language, with fallback to python."""
        return self.PATTERNS.get(language, self.PATTERNS.get("python", {}))

    def get_context(self, content: str, line_num: int, before: int = 5, after: int = 15) -> str:
        """Get surrounding context for a match."""
        lines = content.splitlines()
        start = max(0, line_num - before)
        end = min(len(lines), line_num + after)
        return "\n".join(lines[start:end])

    def get_line_number(self, content: str, position: int) -> int:
        """Get line number for a position in content."""
        return content[:position].count("\n") + 1


class RetryDetector(BaseDetector):
    """Detect retry patterns and evaluate their quality."""

    PATTERNS = RETRY_PATTERNS
    TRIGGERS = RETRY_TRIGGERS
    QUALITY_INDICATORS = RETRY_QUALITY
    PATTERN_TYPE = "retry"

    def detect(self, content: str, filepath: str, language: str) -> tuple[list, list]:
        """Detect retry patterns and issues."""
        patterns = []
        issues = []

        lang_patterns = self.get_patterns(language)

        for pattern_name, pattern in lang_patterns.items():
            # Only check trigger patterns, not quality indicators
            if pattern_name not in self.TRIGGERS:
                continue

            for match in filter_matches(pattern, content, filepath):
                line_num = self.get_line_number(content, match.start())
                context = self.get_context(content, line_num)
                quality = self._evaluate_quality(context, lang_patterns)

                patterns.append(
                    PatternDetection(
                        pattern_type=self.PATTERN_TYPE,
                        file=filepath,
                        line=line_num,
                        quality=quality,
                        details={
                            "pattern": pattern_name,
                            "library": "decorator" in pattern_name or "lib" in pattern_name,
                        },
                    )
                )

                if quality != "CORRECT":
                    issues.extend(self._generate_issues(filepath, line_num, context, lang_patterns))

        return patterns, issues

    def _evaluate_quality(self, context: str, lang_patterns: dict) -> str:
        """Evaluate retry implementation quality."""
        has_backoff = bool(
            lang_patterns.get("exponential_backoff", re.compile(r"$^")).search(context)
        )
        has_jitter = bool(lang_patterns.get("jitter", re.compile(r"$^")).search(context))
        has_max = bool(lang_patterns.get("max_retries", re.compile(r"$^")).search(context))
        has_sleep = bool(lang_patterns.get("sleep_call", re.compile(r"sleep")).search(context))

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

    def _generate_issues(self, filepath: str, line: int, context: str, lang_patterns: dict) -> list:
        """Generate specific issues for a retry pattern."""
        issues = []

        has_backoff = bool(
            lang_patterns.get("exponential_backoff", re.compile(r"$^")).search(context)
        )
        has_jitter = bool(lang_patterns.get("jitter", re.compile(r"$^")).search(context))
        has_max = bool(lang_patterns.get("max_retries", re.compile(r"$^")).search(context))

        if not has_backoff:
            issues.append(
                RetryIssue(
                    file=filepath,
                    line=line,
                    issue_type="no_backoff",
                    severity="HIGH",
                    description="Retry without exponential backoff - can cause thundering herd",
                    fix_suggestion="Add exponential backoff: delay = base_delay * (2 ** attempt)",
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


class TimeoutDetector(BaseDetector):
    """Detect timeout configurations and issues."""

    PATTERNS = TIMEOUT_PATTERNS
    PATTERN_TYPE = "timeout"

    def detect(self, content: str, filepath: str, language: str) -> tuple[list, list]:
        """Detect timeout patterns and issues."""
        patterns = []
        issues = []

        lang_patterns = self.get_patterns(language)

        # Check for missing timeouts first
        for pattern_name in TIMEOUT_ISSUES:
            pattern = lang_patterns.get(pattern_name)
            if not pattern:
                continue

            for match in filter_matches(pattern, content, filepath):
                line_num = self.get_line_number(content, match.start())
                context = self.get_context(content, line_num, before=5, after=2)

                # Skip if timeout is set elsewhere in context
                if "timeout" in context.lower() and pattern_name == "requests_no_timeout":
                    continue

                # CALIBRATION: Skip timeout=None in function/method definitions
                # This is often intentional - the library wants the caller to set timeout
                if pattern_name == "timeout_none":
                    if self._is_default_parameter(context):
                        continue

                quality = "CARGO_CULT"

                patterns.append(
                    PatternDetection(
                        pattern_type=self.PATTERN_TYPE,
                        file=filepath,
                        line=line_num,
                        quality=quality,
                        details={"issue": pattern_name},
                    )
                )

                if pattern_name == "timeout_none":
                    # Lower severity if it looks like configuration/setup
                    severity = "MEDIUM" if self._is_config_context(context) else "HIGH"
                    issues.append(
                        TimeoutIssue(
                            file=filepath,
                            line=line_num,
                            issue_type="explicit_none",
                            severity=severity,
                            description="Explicit timeout=None disables timeout - can hang indefinitely",
                        )
                    )
                else:
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

        # Check for configured timeouts (these are good)
        for pattern_name, pattern in lang_patterns.items():
            if pattern_name in TIMEOUT_ISSUES:
                continue

            for match in filter_matches(pattern, content, filepath):
                line_num = self.get_line_number(content, match.start())

                patterns.append(
                    PatternDetection(
                        pattern_type=self.PATTERN_TYPE,
                        file=filepath,
                        line=line_num,
                        quality="CORRECT",
                        details={"pattern": pattern_name},
                    )
                )

        return patterns, issues

    def _is_default_parameter(self, context: str) -> bool:
        """Check if timeout=None is a default parameter in a function definition."""
        # Function/method definitions
        if re.search(r"def\s+\w+\s*\([^)]*timeout\s*=\s*None", context):
            return True
        # Class __init__ with timeout parameter
        if re.search(r"def\s+__init__\s*\([^)]*timeout\s*=\s*None", context):
            return True
        # Constructor or function signature patterns in other languages
        if re.search(r"function\s+\w+\s*\([^)]*timeout\s*[=:]\s*null", context, re.IGNORECASE):
            return True
        return False

    def _is_config_context(self, context: str) -> bool:
        """Check if timeout=None is in a configuration/setup context."""
        context_lower = context.lower()
        config_indicators = [
            "config",
            "settings",
            "options",
            "defaults",
            "self.timeout",
            "this.timeout",
        ]
        return any(ind in context_lower for ind in config_indicators)


class CircuitBreakerDetector(BaseDetector):
    """Detect circuit breaker patterns and issues."""

    PATTERNS = CIRCUIT_BREAKER_PATTERNS
    TRIGGERS = CB_TRIGGERS
    QUALITY_INDICATORS = CB_QUALITY
    PATTERN_TYPE = "circuit_breaker"

    def detect(self, content: str, filepath: str, language: str) -> tuple[list, list]:
        """Detect circuit breaker patterns and issues."""
        patterns = []
        issues = []

        lang_patterns = self.get_patterns(language)

        for pattern_name, pattern in lang_patterns.items():
            if pattern_name in self.QUALITY_INDICATORS:
                continue

            for match in filter_matches(pattern, content, filepath):
                line_num = self.get_line_number(content, match.start())
                context = self.get_context(content, line_num, before=5, after=30)
                quality = self._evaluate_quality(context, lang_patterns)

                patterns.append(
                    PatternDetection(
                        pattern_type=self.PATTERN_TYPE,
                        file=filepath,
                        line=line_num,
                        quality=quality,
                        details={"library": pattern_name},
                    )
                )

                if quality != "CORRECT":
                    issues.extend(self._generate_issues(filepath, line_num, context, lang_patterns))

        return patterns, issues

    def _evaluate_quality(self, context: str, lang_patterns: dict) -> str:
        """Evaluate circuit breaker implementation quality."""
        has_fallback = any(
            lang_patterns.get(p, re.compile(r"$^")).search(context)
            for p in ["cb_fallback", "fallback"]
        )
        has_metrics = any(
            lang_patterns.get(p, re.compile(r"$^")).search(context)
            for p in ["cb_metrics", "cb_listener", "cb_events", "cb_on_state", "cb_logging"]
        )

        if has_fallback and has_metrics:
            return "CORRECT"
        elif has_fallback or has_metrics:
            return "PARTIAL"
        else:
            return "CARGO_CULT"

    def _generate_issues(self, filepath: str, line: int, context: str, lang_patterns: dict) -> list:
        """Generate circuit breaker issues."""
        issues = []

        has_metrics = any(
            lang_patterns.get(p, re.compile(r"$^")).search(context)
            for p in ["cb_metrics", "cb_listener", "cb_events", "cb_on_state", "cb_logging"]
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
                    description="Circuit breaker without metrics/logging - state changes invisible to operators",
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


class ExceptionDetector(BaseDetector):
    """Detect problematic exception handling patterns."""

    PATTERNS = EXCEPTION_PATTERNS
    PATTERN_TYPE = "exception_handling"

    # CALIBRATED: Severity based on actual impact, not theoretical purity
    SEVERITY_MAP = {
        "bare_except": "MEDIUM",  # Bad but common, often intentional for cleanup
        "broad_except": "LOW",  # Lowered - often intentional at boundaries
        "except_pass": "MEDIUM",  # Context matters - check for logging
        "except_continue": "MEDIUM",
        "empty_catch": "MEDIUM",
        "catch_all": "LOW",  # Lowered - often intentional
        "catch_throwable": "LOW",  # Lowered - often intentional in Java
        "swallow_exception": "LOW",  # Has comment, somewhat intentional
        "ignore_error": "LOW",  # Go idiom - sometimes intentional
        "empty_if_err": "MEDIUM",
        "ignore_return": "LOW",  # Very common, often fine
        "empty_error_check": "LOW",
    }

    def detect(self, content: str, filepath: str, language: str) -> tuple[list, list]:
        """Detect exception handling patterns and issues."""
        patterns = []
        issues = []

        lang_patterns = self.get_patterns(language)

        for pattern_name, pattern in lang_patterns.items():
            is_anti_pattern = pattern_name in EXCEPTION_ANTI_PATTERNS

            for match in filter_matches(pattern, content, filepath):
                line_num = self.get_line_number(content, match.start())
                context = self.get_context(content, line_num, before=3, after=3)

                # CALIBRATION: Skip if context suggests intentional handling
                if self._is_intentional_handling(context, pattern_name):
                    continue

                quality = "CARGO_CULT" if is_anti_pattern else "CORRECT"

                patterns.append(
                    PatternDetection(
                        pattern_type=self.PATTERN_TYPE,
                        file=filepath,
                        line=line_num,
                        quality=quality,
                        details={"pattern": pattern_name},
                    )
                )

                if is_anti_pattern:
                    severity = self.SEVERITY_MAP.get(pattern_name, "LOW")
                    issues.append(
                        ExceptionIssue(
                            file=filepath,
                            line=line_num,
                            issue_type=pattern_name,
                            severity=severity,
                            description=self._get_issue_description(pattern_name),
                        )
                    )

        return patterns, issues

    def _is_intentional_handling(self, context: str, pattern_name: str) -> bool:
        """Check if the exception handling appears intentional."""
        context_lower = context.lower()

        # Logging nearby suggests the exception is being recorded
        if any(
            log in context_lower for log in ["log.", "logger.", "logging.", "print(", "console."]
        ):
            return True

        # Comments suggesting intentional ignoring
        if any(
            comment in context_lower
            for comment in ["# ignore", "# skip", "# optional", "// ignore", "/* ignore"]
        ):
            return True

        # Cleanup/finally context - often intentional
        if "finally" in context_lower or "cleanup" in context_lower or "__del__" in context_lower:
            return True

        # Top-level handlers (main, run, start) - often intentional
        if any(fn in context_lower for fn in ["def main", "def run", "def start", "if __name__"]):
            return True

        return False

    def _get_issue_description(self, pattern_name: str) -> str:
        """Get description for an exception anti-pattern."""
        descriptions = {
            "bare_except": "Bare except catches all exceptions including KeyboardInterrupt",
            "broad_except": "Catching Exception/BaseException hides bugs and makes debugging hard",
            "except_pass": "Silently swallowing exceptions hides errors",
            "except_continue": "Continuing after exception without handling hides errors",
            "empty_catch": "Empty catch block silently swallows errors",
            "catch_all": "Catching all exceptions hides specific errors",
            "catch_throwable": "Catching Throwable/Exception is too broad",
            "swallow_exception": "Swallowing exception with comment is not handling it",
            "ignore_error": "Ignoring error return value with _ assignment",
            "empty_if_err": "Empty error handling block ignores the error",
            "ignore_return": "Ignoring function return value may miss errors",
            "empty_error_check": "Empty error check block does nothing with the error",
        }
        return descriptions.get(pattern_name, f"Problematic pattern: {pattern_name}")


class LibraryDetector(BaseDetector):
    """Detect which resilience libraries are in use."""

    PATTERNS = LIBRARY_PATTERNS

    def detect(self, content: str, language: str) -> list[str]:
        """Detect which resilience libraries are in use."""
        found = []
        lang_libs = self.get_patterns(language)

        for lib_name, pattern in lang_libs.items():
            if pattern.search(content):
                found.append(lib_name)

        return found
