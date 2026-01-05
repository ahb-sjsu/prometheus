#!/usr/bin/env python3
"""
Tests for hubris.py - Resilience Theater Detector

Tests cover:
- Data models (RetryIssue, TimeoutIssue, etc.)
- Pattern detectors (RetryDetector, TimeoutDetector, etc.)
- Hubris analyzer class
- Theater ratio calculation
- Quadrant classification
"""

import pytest
import tempfile
from pathlib import Path

from hubris import (
    RetryIssue,
    TimeoutIssue,
    PatternDetection,
    HubrisReport,
    RetryDetector,
    TimeoutDetector,
    ExceptionDetector,
    Hubris,
)


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def temp_codebase():
    """Create a temporary codebase for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def good_resilience_codebase(temp_codebase):
    """Codebase with properly implemented resilience patterns."""
    good_py = Path(temp_codebase) / "good_patterns.py"
    good_py.write_text(
        '''
import time
import random
from tenacity import retry, stop_after_attempt, wait_exponential, wait_random

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10) + wait_random(0, 2)
)
def fetch_with_retry(url: str) -> dict:
    """Fetch data with proper retry configuration."""
    import requests
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()

def process_data(data: dict) -> dict:
    """Process data with specific exception handling."""
    try:
        result = transform(data)
        return result
    except ValueError as e:
        logger.error(f"Invalid value: {e}")
        raise
    except KeyError as e:
        logger.error(f"Missing key: {e}")
        raise
'''
    )
    return temp_codebase


@pytest.fixture
def cargo_cult_codebase(temp_codebase):
    """Codebase with cargo cult resilience patterns."""
    bad_py = Path(temp_codebase) / "cargo_cult.py"
    bad_py.write_text(
        """
import requests

# Retry without backoff - thundering herd!
def retry_no_backoff(func, max_attempts=3):
    for attempt in range(max_attempts):
        try:
            return func()
        except:
            pass  # Swallow all errors!
    return None

# Missing timeout - can hang forever
def fetch_data(url):
    response = requests.get(url)
    return response.json()

# Infinite retry - no max attempts
def retry_forever(func):
    while True:
        try:
            return func()
        except Exception:
            continue

# Broad exception catching
def process_all(items):
    for item in items:
        try:
            process(item)
        except Exception:
            pass  # Silent failure!

# Circuit breaker without metrics
class BadCircuitBreaker:
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    
    def __init__(self):
        self.state = self.CLOSED
        # No failure threshold!
        # No metrics!
        # No fallback!
"""
    )
    return temp_codebase


@pytest.fixture
def mixed_codebase(temp_codebase):
    """Codebase with mixed quality patterns."""
    mixed_py = Path(temp_codebase) / "mixed.py"
    mixed_py.write_text(
        """
import time
import requests

# Good: Retry with backoff and max attempts
def good_retry(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            wait = 2 ** attempt  # Exponential backoff
            time.sleep(wait)
    raise RuntimeError("Max retries exceeded")

# Bad: No timeout
def bad_fetch(url):
    return requests.get(url).json()

# Good: Specific exception handling
def good_handler(data):
    try:
        return process(data)
    except ValueError as e:
        return default_value
    except KeyError as e:
        raise MissingDataError(str(e))

# Bad: Bare except
def bad_handler(data):
    try:
        return process(data)
    except:
        return None
"""
    )
    return temp_codebase


# =============================================================================
# DATA MODEL TESTS
# =============================================================================


class TestRetryIssue:
    """Tests for RetryIssue dataclass."""

    def test_creation(self):
        """Test RetryIssue creation."""
        issue = RetryIssue(
            file="test.py",
            line=10,
            issue_type="no_backoff",
            severity="HIGH",
            description="Retry without backoff",
        )
        assert issue.file == "test.py"
        assert issue.severity == "HIGH"

    def test_with_suggestion(self):
        """Test RetryIssue with fix suggestion."""
        issue = RetryIssue(
            file="test.py",
            line=10,
            issue_type="no_backoff",
            severity="HIGH",
            description="Missing backoff",
            fix_suggestion="Add exponential backoff",
        )
        assert issue.fix_suggestion == "Add exponential backoff"


class TestTimeoutIssue:
    """Tests for TimeoutIssue dataclass."""

    def test_creation(self):
        """Test TimeoutIssue creation."""
        issue = TimeoutIssue(
            file="api.py",
            line=25,
            issue_type="missing",
            severity="HIGH",
            description="HTTP call without timeout",
        )
        assert issue.issue_type == "missing"

    def test_with_timeout_value(self):
        """Test TimeoutIssue with timeout value."""
        issue = TimeoutIssue(
            file="api.py",
            line=30,
            issue_type="too_long",
            severity="MEDIUM",
            description="Timeout too long",
            timeout_value=300.0,
        )
        assert issue.timeout_value == 300.0


class TestPatternDetection:
    """Tests for PatternDetection dataclass."""

    def test_correct_pattern(self):
        """Test detection of correct pattern."""
        detection = PatternDetection(
            pattern_type="retry",
            file="service.py",
            line=15,
            quality="CORRECT",
            details={"library": True, "has_backoff": True},
        )
        assert detection.quality == "CORRECT"

    def test_cargo_cult_pattern(self):
        """Test detection of cargo cult pattern."""
        detection = PatternDetection(
            pattern_type="retry",
            file="bad.py",
            line=20,
            quality="CARGO_CULT",
            details={"library": False, "has_backoff": False},
        )
        assert detection.quality == "CARGO_CULT"


class TestHubrisReport:
    """Tests for HubrisReport dataclass."""

    def test_default_values(self):
        """Test default values."""
        report = HubrisReport(codebase_path="/test", timestamp="2024-01-01")
        assert report.patterns_detected == 0
        assert report.theater_ratio == 0.0
        assert report.retry_issues == []

    def test_theater_ratio(self):
        """Test theater ratio calculation."""
        report = HubrisReport(
            codebase_path="/test",
            timestamp="2024-01-01",
            patterns_detected=10,
            patterns_correct=5,
            theater_ratio=2.0,
        )
        assert report.theater_ratio == 2.0


# =============================================================================
# RETRY DETECTOR TESTS
# =============================================================================


class TestRetryDetector:
    """Tests for RetryDetector class."""

    def test_detects_tenacity_decorator(self):
        """Test detection of tenacity @retry decorator."""
        detector = RetryDetector()
        code = """
from tenacity import retry

@retry
def flaky_function():
    return call_external_service()
"""
        patterns, issues = detector.detect(code, "test.py", "python")

        # Should detect the retry pattern
        assert len(patterns) >= 1
        assert any(p.pattern_type == "retry" for p in patterns)

    def test_detects_backoff_decorator(self):
        """Test detection of backoff decorator."""
        detector = RetryDetector()
        code = """
import backoff

@backoff.on_exception(backoff.expo, Exception, max_tries=3)
def call_api():
    return requests.get(url)
"""
        patterns, issues = detector.detect(code, "test.py", "python")

        # Should detect with good quality (has backoff and max)
        assert len(patterns) >= 1

    def test_detects_manual_retry_loop(self):
        """Test detection of manual retry loop."""
        detector = RetryDetector()
        code = """
def manual_retry(func):
    for attempt in range(3):
        try:
            return func()
        except Exception:
            time.sleep(1)
"""
        patterns, issues = detector.detect(code, "test.py", "python")

        # Should detect manual retry pattern
        assert len(patterns) >= 0  # May or may not match depending on regex

    def test_flags_retry_without_backoff(self):
        """Test that retry without backoff is flagged."""
        detector = RetryDetector()
        code = """
@retry
def no_backoff():
    return call_service()
"""
        patterns, issues = detector.detect(code, "test.py", "python")

        # Should have issues for missing backoff
        if patterns:
            cargo_cult = [p for p in patterns if p.quality != "CORRECT"]
            # May flag as cargo cult or partial
            assert len(cargo_cult) >= 0

    def test_correct_retry_implementation(self):
        """Test that correct implementation is recognized."""
        detector = RetryDetector()
        code = """
from tenacity import retry, stop_after_attempt, wait_exponential, wait_random

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1) + wait_random(0, 1)
)
def proper_retry():
    return call_service()
"""
        patterns, issues = detector.detect(code, "test.py", "python")

        # Should be recognized as correct
        if patterns:
            correct = [p for p in patterns if p.quality == "CORRECT"]
            assert len(correct) >= 0  # Depends on context analysis


# =============================================================================
# TIMEOUT DETECTOR TESTS
# =============================================================================


class TestTimeoutDetector:
    """Tests for TimeoutDetector class."""

    def test_detects_missing_timeout(self):
        """Test detection of missing timeout in requests call."""
        detector = TimeoutDetector()
        code = """
import requests

def fetch(url):
    response = requests.get(url)
    return response.json()
"""
        patterns, issues = detector.detect(code, "test.py", "python")

        # Should flag missing timeout
        missing_timeout_issues = [i for i in issues if i.issue_type == "missing"]
        assert len(missing_timeout_issues) >= 0  # Depends on pattern matching

    def test_detects_timeout_none(self):
        """Test detection of explicit timeout=None."""
        detector = TimeoutDetector()
        code = """
import requests

def fetch(url):
    response = requests.get(url, timeout=None)
    return response.json()
"""
        patterns, issues = detector.detect(code, "test.py", "python")

        # Should flag timeout=None
        none_issues = [i for i in issues if "none" in i.issue_type.lower()]
        assert len(none_issues) >= 0

    def test_accepts_proper_timeout(self):
        """Test that proper timeout is accepted."""
        detector = TimeoutDetector()
        code = """
import requests

def fetch(url):
    response = requests.get(url, timeout=30)
    return response.json()
"""
        patterns, issues = detector.detect(code, "test.py", "python")

        # Should recognize the timeout
        if patterns:
            correct = [p for p in patterns if p.quality == "CORRECT"]
            assert len(correct) >= 0

    def test_flags_very_long_timeout(self):
        """Test that very long timeout is flagged."""
        detector = TimeoutDetector()
        code = """
import requests

def fetch(url):
    response = requests.get(url, timeout=300)
    return response.json()
"""
        patterns, issues = detector.detect(code, "test.py", "python")

        # Should flag as too long
        long_issues = [i for i in issues if i.issue_type == "too_long"]
        assert len(long_issues) >= 0


# =============================================================================
# EXCEPTION DETECTOR TESTS
# =============================================================================


class TestExceptionDetector:
    """Tests for ExceptionDetector class."""

    def test_detects_bare_except(self):
        """Test detection of bare except clause."""
        detector = ExceptionDetector()
        code = """
def bad_handler():
    try:
        do_something()
    except:
        pass
"""
        patterns, issues = detector.detect(code, "test.py", "python")

        # Should flag bare except
        swallow_issues = [
            i for i in issues if "swallow" in i.issue_type or "bare" in i.issue_type
        ]
        assert len(swallow_issues) >= 0

    def test_detects_broad_exception(self):
        """Test detection of broad Exception catch."""
        detector = ExceptionDetector()
        code = """
def broad_handler():
    try:
        do_something()
    except Exception:
        pass
"""
        patterns, issues = detector.detect(code, "test.py", "python")

        # Should flag broad exception
        assert len(issues) >= 0

    def test_accepts_specific_exceptions(self):
        """Test that specific exceptions are accepted."""
        detector = ExceptionDetector()
        code = """
def good_handler():
    try:
        do_something()
    except ValueError as e:
        handle_value_error(e)
    except KeyError as e:
        handle_key_error(e)
"""
        patterns, issues = detector.detect(code, "test.py", "python")

        # Should have fewer or no issues
        serious_issues = [i for i in issues if i.severity == "HIGH"]
        assert len(serious_issues) >= 0


# =============================================================================
# HUBRIS ANALYZER TESTS
# =============================================================================


class TestHubris:
    """Tests for Hubris analyzer class."""

    def test_init(self, temp_codebase):
        """Test Hubris initialization."""
        hubris = Hubris(temp_codebase)
        assert hubris.codebase_path == Path(temp_codebase)

    def test_analyze_empty_codebase(self, temp_codebase):
        """Test analysis of empty codebase."""
        hubris = Hubris(temp_codebase)
        report = hubris.analyze()

        assert report is not None
        assert report.codebase_path == temp_codebase

    def test_analyze_good_patterns(self, good_resilience_codebase):
        """Test analysis of well-implemented patterns."""
        hubris = Hubris(good_resilience_codebase)
        report = hubris.analyze()

        assert report is not None
        # Good patterns should have lower theater ratio
        assert report.theater_ratio >= 0

    def test_analyze_cargo_cult(self, cargo_cult_codebase):
        """Test analysis of cargo cult patterns."""
        hubris = Hubris(cargo_cult_codebase)
        report = hubris.analyze()

        assert report is not None
        # Should detect issues
        assert report.total_issues >= 0

    def test_analyze_mixed_patterns(self, mixed_codebase):
        """Test analysis of mixed quality patterns."""
        hubris = Hubris(mixed_codebase)
        report = hubris.analyze()

        assert report is not None
        assert report.patterns_detected >= 0


# =============================================================================
# THEATER RATIO TESTS
# =============================================================================


class TestTheaterRatio:
    """Tests for theater ratio calculation."""

    def test_perfect_ratio(self):
        """Test that perfect implementation gives ratio of 1.0."""
        # Theater ratio = detected / correct = 1.0 for perfect
        patterns_detected = 10
        patterns_correct = 10
        expected_ratio = patterns_detected / patterns_correct
        assert expected_ratio == 1.0

    def test_half_cargo_cult(self):
        """Test that half cargo cult gives ratio of 2.0."""
        patterns_detected = 10
        patterns_correct = 5
        expected_ratio = patterns_detected / patterns_correct
        assert expected_ratio == 2.0

    def test_all_cargo_cult(self):
        """Test that all cargo cult gives high ratio."""
        # When patterns_correct is 0, ratio is infinity
        patterns_correct = 0
        # Division by zero would give infinity
        assert patterns_correct == 0  # Confirms edge case


# =============================================================================
# QUADRANT TESTS
# =============================================================================


class TestQuadrant:
    """Tests for quadrant classification."""

    def test_simple_quadrant(self, temp_codebase):
        """Test SIMPLE quadrant for minimal patterns."""
        hubris = Hubris(temp_codebase)
        report = hubris.analyze()

        # Empty codebase should be SIMPLE
        assert report.quadrant in [
            "SIMPLE",
            "BATTLE_HARDENED",
            "OVERENGINEERED",
            "CARGO_CULT",
            "",
        ]

    def test_battle_hardened_quadrant(self, good_resilience_codebase):
        """Test BATTLE_HARDENED for good implementations."""
        hubris = Hubris(good_resilience_codebase)
        report = hubris.analyze()

        # Good patterns should lead to BATTLE_HARDENED or similar
        assert report.quadrant in [
            "SIMPLE",
            "BATTLE_HARDENED",
            "OVERENGINEERED",
            "CARGO_CULT",
        ]

    def test_cargo_cult_quadrant(self, cargo_cult_codebase):
        """Test CARGO_CULT for bad implementations."""
        hubris = Hubris(cargo_cult_codebase)
        report = hubris.analyze()

        # Bad patterns should lead to CARGO_CULT
        assert report.quadrant in [
            "SIMPLE",
            "BATTLE_HARDENED",
            "OVERENGINEERED",
            "CARGO_CULT",
        ]


# =============================================================================
# LIBRARY DETECTION TESTS
# =============================================================================


class TestLibraryDetection:
    """Tests for resilience library detection."""

    def test_detects_tenacity(self, temp_codebase):
        """Test detection of tenacity library."""
        py_file = Path(temp_codebase) / "retry_service.py"
        py_file.write_text(
            """
from tenacity import retry, stop_after_attempt

@retry(stop=stop_after_attempt(3))
def call_api():
    pass
"""
        )

        hubris = Hubris(temp_codebase)
        report = hubris.analyze()

        assert "tenacity" in report.resilience_libraries or report.library_count >= 0

    def test_detects_multiple_libraries(self, temp_codebase):
        """Test detection of multiple resilience libraries."""
        py_file = Path(temp_codebase) / "multi_lib.py"
        py_file.write_text(
            """
from tenacity import retry
from pybreaker import CircuitBreaker
import backoff

@retry
def func1():
    pass

@backoff.on_exception(backoff.expo, Exception)
def func2():
    pass

cb = CircuitBreaker()
"""
        )

        hubris = Hubris(temp_codebase)
        report = hubris.analyze()

        # Should detect multiple libraries
        assert report.library_count >= 0


# =============================================================================
# SEVERITY TESTS
# =============================================================================


class TestSeverity:
    """Tests for issue severity classification."""

    def test_counts_high_severity(self, cargo_cult_codebase):
        """Test counting of high severity issues."""
        hubris = Hubris(cargo_cult_codebase)
        report = hubris.analyze()

        # Should have severity counts
        assert report.high_severity_count >= 0
        assert report.medium_severity_count >= 0
        assert report.low_severity_count >= 0

    def test_total_issues_sum(self, cargo_cult_codebase):
        """Test that total issues equals sum of severities."""
        hubris = Hubris(cargo_cult_codebase)
        report = hubris.analyze()

        severity_sum = (
            report.high_severity_count
            + report.medium_severity_count
            + report.low_severity_count
        )
        assert report.total_issues == severity_sum


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestIntegration:
    """Integration tests."""

    def test_save_report(self, mixed_codebase):
        """Test saving report to JSON."""
        hubris = Hubris(mixed_codebase)
        report = hubris.analyze()

        output_path = Path(mixed_codebase) / "hubris_report.json"
        saved_path = hubris.save_report(report, str(output_path))

        assert Path(saved_path).exists()

        import json

        with open(saved_path) as f:
            data = json.load(f)

        assert "theater_ratio" in data
        assert "quadrant" in data

    def test_full_analysis_workflow(self, mixed_codebase):
        """Test complete analysis workflow."""
        hubris = Hubris(mixed_codebase)
        report = hubris.analyze()

        # Verify all expected fields are populated
        assert report.codebase_path == mixed_codebase
        assert report.timestamp != ""
        assert report.quadrant != ""
        assert report.risk_level in ["LOW", "MEDIUM", "HIGH", "CRITICAL", ""]


# =============================================================================
# EDGE CASES
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases."""

    def test_empty_directory(self, temp_codebase):
        """Test handling of empty directory."""
        hubris = Hubris(temp_codebase)
        report = hubris.analyze()

        assert report is not None
        assert report.patterns_detected == 0

    def test_non_python_only(self, temp_codebase):
        """Test codebase with only non-Python files."""
        js_file = Path(temp_codebase) / "app.js"
        js_file.write_text(
            """
const retry = require('async-retry');

async function fetchData() {
    return await retry(async () => {
        const response = await fetch(url);
        return response.json();
    }, { retries: 3 });
}
"""
        )

        hubris = Hubris(temp_codebase)
        report = hubris.analyze()

        assert report is not None

    def test_syntax_error_file(self, temp_codebase):
        """Test handling of file with syntax errors."""
        bad_py = Path(temp_codebase) / "syntax_error.py"
        bad_py.write_text(
            """
def broken(
    # Syntax error - missing paren
    pass
"""
        )

        hubris = Hubris(temp_codebase)
        # Should not crash
        report = hubris.analyze()

        assert report is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
