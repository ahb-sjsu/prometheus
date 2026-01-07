#!/usr/bin/env python3
"""
Hubris Detectors
================
Pattern detectors for resilience anti-patterns.

Uses a base class to eliminate repetition across detector types.
"""

import re
from typing import Any

from models import (
    PatternDetection, RetryIssue, TimeoutIssue, 
    CircuitBreakerIssue, ExceptionIssue
)
from patterns import (
    RETRY_PATTERNS, RETRY_TRIGGERS, RETRY_QUALITY,
    TIMEOUT_PATTERNS, TIMEOUT_ISSUES,
    CIRCUIT_BREAKER_PATTERNS, CB_TRIGGERS, CB_QUALITY,
    EXCEPTION_PATTERNS, EXCEPTION_ANTI_PATTERNS,
    LIBRARY_PATTERNS,
)
from fp_filter import filter_matches


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
                
                patterns.append(PatternDetection(
                    pattern_type=self.PATTERN_TYPE,
                    file=filepath,
                    line=line_num,
                    quality=quality,
                    details={"pattern": pattern_name, "library": "decorator" in pattern_name or "lib" in pattern_name},
                ))
                
                if quality != "CORRECT":
                    issues.extend(self._generate_issues(filepath, line_num, context, lang_patterns))
        
        return patterns, issues
    
    def _evaluate_quality(self, context: str, lang_patterns: dict) -> str:
        """Evaluate retry implementation quality."""
        has_backoff = bool(lang_patterns.get("exponential_backoff", re.compile(r"$^")).search(context))
        has_jitter = bool(lang_patterns.get("jitter", re.compile(r"$^")).search(context))
        has_max = bool(lang_patterns.get("max_retries", re.compile(r"$^")).search(context))
        has_sleep = bool(lang_patterns.get("sleep_call", re.compile(r"sleep")).search(context))
        
        broad_exception = bool(re.search(
            r"except\s*:|except\s+Exception\s*:|catch\s*\(\s*(?:Exception|Error|Throwable)\s*\)",
            context
        ))
        
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
        
        has_backoff = bool(lang_patterns.get("exponential_backoff", re.compile(r"$^")).search(context))
        has_jitter = bool(lang_patterns.get("jitter", re.compile(r"$^")).search(context))
        has_max = bool(lang_patterns.get("max_retries", re.compile(r"$^")).search(context))
        
        if not has_backoff:
            issues.append(RetryIssue(
                file=filepath, line=line,
                issue_type="no_backoff", severity="HIGH",
                description="Retry without exponential backoff - can cause thundering herd",
                fix_suggestion="Add exponential backoff: delay = base_delay * (2 ** attempt)",
            ))
        
        if not has_max:
            issues.append(RetryIssue(
                file=filepath, line=line,
                issue_type="no_max", severity="HIGH",
                description="Retry without maximum attempts - may retry forever",
                fix_suggestion="Add max_retries limit (typically 3-5 attempts)",
            ))
        
        if has_backoff and not has_jitter:
            issues.append(RetryIssue(
                file=filepath, line=line,
                issue_type="no_jitter", severity="MEDIUM",
                description="Backoff without jitter - synchronized retries can still overwhelm",
                fix_suggestion="Add random jitter: delay * (1 + random.uniform(-0.1, 0.1))",
            ))
        
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
                context = self.get_context(content, line_num, before=10, after=5)
                
                # Skip if timeout is set elsewhere in context
                if "timeout" in context.lower() and pattern_name == "requests_no_timeout":
                    continue
                
                quality = "CARGO_CULT"
                
                patterns.append(PatternDetection(
                    pattern_type=self.PATTERN_TYPE,
                    file=filepath,
                    line=line_num,
                    quality=quality,
                    details={"issue": pattern_name},
                ))
                
                if pattern_name == "timeout_none":
                    issues.append(TimeoutIssue(
                        file=filepath, line=line_num,
                        issue_type="explicit_none", severity="HIGH",
                        description="Explicit timeout=None disables timeout - can hang indefinitely",
                    ))
                else:
                    issues.append(TimeoutIssue(
                        file=filepath, line=line_num,
                        issue_type="missing", severity="HIGH",
                        description="Network call without timeout - can hang indefinitely",
                        context=match.group(0)[:100],
                    ))
        
        # Check for configured timeouts (these are good)
        for pattern_name, pattern in lang_patterns.items():
            if pattern_name in TIMEOUT_ISSUES:
                continue
                
            for match in filter_matches(pattern, content, filepath):
                line_num = self.get_line_number(content, match.start())
                
                patterns.append(PatternDetection(
                    pattern_type=self.PATTERN_TYPE,
                    file=filepath,
                    line=line_num,
                    quality="CORRECT",
                    details={"pattern": pattern_name},
                ))
        
        return patterns, issues


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
                
                patterns.append(PatternDetection(
                    pattern_type=self.PATTERN_TYPE,
                    file=filepath,
                    line=line_num,
                    quality=quality,
                    details={"library": pattern_name},
                ))
                
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
            issues.append(CircuitBreakerIssue(
                file=filepath, line=line,
                issue_type="invisible", severity="HIGH",
                description="Circuit breaker without metrics/logging - state changes invisible to operators",
            ))
        
        if not has_fallback:
            issues.append(CircuitBreakerIssue(
                file=filepath, line=line,
                issue_type="no_fallback", severity="MEDIUM",
                description="Circuit breaker without fallback - open circuit will just throw exceptions",
            ))
        
        return issues


class ExceptionDetector(BaseDetector):
    """Detect problematic exception handling patterns."""
    
    PATTERNS = EXCEPTION_PATTERNS
    PATTERN_TYPE = "exception_handling"
    
    def detect(self, content: str, filepath: str, language: str) -> tuple[list, list]:
        """Detect exception handling patterns and issues."""
        patterns = []
        issues = []
        
        lang_patterns = self.get_patterns(language)
        
        for pattern_name, pattern in lang_patterns.items():
            is_anti_pattern = pattern_name in EXCEPTION_ANTI_PATTERNS
            
            for match in filter_matches(pattern, content, filepath):
                line_num = self.get_line_number(content, match.start())
                
                quality = "CARGO_CULT" if is_anti_pattern else "CORRECT"
                
                patterns.append(PatternDetection(
                    pattern_type=self.PATTERN_TYPE,
                    file=filepath,
                    line=line_num,
                    quality=quality,
                    details={"pattern": pattern_name},
                ))
                
                if is_anti_pattern:
                    issues.append(ExceptionIssue(
                        file=filepath, line=line_num,
                        issue_type=pattern_name, severity="MEDIUM",
                        description=self._get_issue_description(pattern_name),
                    ))
        
        return patterns, issues
    
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
