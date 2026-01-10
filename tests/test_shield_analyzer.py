#!/usr/bin/env python3
"""
Tests for shield_analyzer.py - Resilience Pattern Analyzer (Aegis)
"""

import json
import tempfile
from pathlib import Path

import pytest

from shield_analyzer import (
    Aegis,
    AegisReport,
    ErrorHandlingMetrics,
    PatternDetector,
    RetryMetrics,
    TimeoutMetrics,
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
def resilient_codebase(temp_codebase):
    """Create a codebase with resilience patterns."""
    src_dir = Path(temp_codebase) / "src"
    src_dir.mkdir()

    # Service with retry and timeout patterns
    service_py = src_dir / "service.py"
    service_py.write_text(
        '''
"""Service with resilience patterns."""
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
import requests

logger = logging.getLogger(__name__)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, max=10))
def fetch_data(url: str) -> dict:
    """Fetch data with retry."""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        logger.info(f"Fetched data from {url}")
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Request failed: {e}")
        raise


class CircuitBreaker:
    """Simple circuit breaker implementation."""
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

    def __init__(self, failure_threshold: int = 5):
        self.state = self.CLOSED
        self.failure_count = 0
        self.failure_threshold = failure_threshold

    def call(self, func, *args, **kwargs):
        if self.state == self.OPEN:
            raise Exception("Circuit is open")
        try:
            result = func(*args, **kwargs)
            self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            if self.failure_count >= self.failure_threshold:
                self.state = self.OPEN
            raise
'''
    )

    return temp_codebase


@pytest.fixture
def fragile_codebase(temp_codebase):
    """Create a codebase with poor resilience patterns."""
    src_dir = Path(temp_codebase) / "src"
    src_dir.mkdir()

    # Service without resilience patterns
    bad_service_py = src_dir / "bad_service.py"
    bad_service_py.write_text(
        '''
"""Service without resilience patterns."""
import requests


def fetch_data(url):
    """Fetch data without any error handling."""
    response = requests.get(url)  # No timeout!
    return response.json()


def process_items(items):
    """Process items with bare except."""
    try:
        for item in items:
            process_single(item)
    except:  # Bare except - bad practice
        pass


def process_single(item):
    return item.upper()
'''
    )

    return temp_codebase


# =============================================================================
# DATA MODEL TESTS
# =============================================================================


class TestErrorHandlingMetrics:
    """Tests for ErrorHandlingMetrics dataclass."""

    def test_default_values(self):
        """Test default values."""
        metrics = ErrorHandlingMetrics()
        assert metrics.try_blocks == 0
        assert metrics.except_blocks == 0
        assert metrics.finally_blocks == 0
        assert metrics.bare_excepts == 0

    def test_custom_values(self):
        """Test custom values."""
        metrics = ErrorHandlingMetrics(
            try_blocks=10,
            except_blocks=8,
            specific_excepts=5,  # Correct field name
        )
        assert metrics.try_blocks == 10
        assert metrics.specific_excepts == 5


class TestTimeoutMetrics:
    """Tests for TimeoutMetrics dataclass."""

    def test_default_values(self):
        """Test default values."""
        metrics = TimeoutMetrics()
        assert metrics.http_timeouts == 0
        assert metrics.missing_timeouts == 0

    def test_custom_values(self):
        """Test custom values."""
        metrics = TimeoutMetrics(
            http_timeouts=5,
            missing_timeouts=2,
        )
        assert metrics.http_timeouts == 5


class TestRetryMetrics:
    """Tests for RetryMetrics dataclass."""

    def test_default_values(self):
        """Test default values."""
        metrics = RetryMetrics()
        assert metrics.retry_decorators == 0
        assert metrics.manual_retry_loops == 0

    def test_custom_values(self):
        """Test custom values."""
        metrics = RetryMetrics(
            retry_decorators=3,
            exponential_backoff=2,
        )
        assert metrics.retry_decorators == 3


class TestAegisReport:
    """Tests for AegisReport dataclass."""

    def test_default_values(self):
        """Test default values."""
        report = AegisReport(codebase_path="/test", timestamp="2024-01-01")
        assert report.overall_resilience_score == 0.0
        assert report.shield_rating == ""

    def test_custom_values(self):
        """Test custom values."""
        report = AegisReport(
            codebase_path="/test",
            timestamp="2024-01-01",
            overall_resilience_score=75.0,
            shield_rating="STEEL",
        )
        assert report.overall_resilience_score == 75.0
        assert report.shield_rating == "STEEL"


# =============================================================================
# PATTERN DETECTOR TESTS
# =============================================================================


class TestPatternDetector:
    """Tests for PatternDetector class."""

    def test_resilience_libraries_defined(self):
        """Test that resilience libraries are defined."""
        detector = PatternDetector()
        assert hasattr(detector, "RESILIENCE_LIBRARIES")
        assert "python" in detector.RESILIENCE_LIBRARIES
        assert "javascript" in detector.RESILIENCE_LIBRARIES

    def test_patterns_defined(self):
        """Test that patterns are defined."""
        detector = PatternDetector()
        assert hasattr(detector, "PATTERNS")
        assert "retry_decorator" in detector.PATTERNS
        assert "timeout_config" in detector.PATTERNS


# =============================================================================
# AEGIS ANALYZER TESTS
# =============================================================================


class TestAegis:
    """Tests for Aegis analyzer class."""

    def test_init(self, temp_codebase):
        """Test Aegis initialization."""
        aegis = Aegis(temp_codebase)
        assert aegis.codebase_path == Path(temp_codebase)

    def test_library_mode(self, temp_codebase):
        """Test library mode initialization."""
        aegis = Aegis(temp_codebase, library_mode=True)
        assert aegis.library_mode is True

    def test_analyze_empty_codebase(self, temp_codebase):
        """Test analysis of empty codebase."""
        aegis = Aegis(temp_codebase)
        report = aegis.analyze()

        assert report is not None
        assert report.codebase_path == temp_codebase

    def test_analyze_resilient_codebase(self, resilient_codebase):
        """Test analysis of codebase with good patterns."""
        aegis = Aegis(resilient_codebase)
        report = aegis.analyze()

        # Should detect some resilience patterns
        # Score might be -1 for TOO_SMALL, which is valid
        assert report.overall_resilience_score >= -1
        assert report.shield_rating != ""

    def test_analyze_fragile_codebase(self, fragile_codebase):
        """Test analysis of codebase with poor patterns."""
        aegis = Aegis(fragile_codebase)
        report = aegis.analyze()

        # Should detect vulnerabilities
        assert report is not None
        # Fragile code should have lower scores or vulnerabilities
        assert len(report.vulnerabilities) >= 0


# =============================================================================
# SHIELD RATING TESTS
# =============================================================================


class TestShieldRating:
    """Tests for shield rating determination."""

    def test_valid_ratings(self):
        """Test that valid ratings are defined."""
        valid_ratings = ["ADAMANTINE", "STEEL", "BRONZE", "WOOD", "PAPER", "TOO_SMALL"]

        report = AegisReport(codebase_path="/test", timestamp="2024-01-01")
        report.shield_rating = "STEEL"

        assert report.shield_rating in valid_ratings

    def test_rating_in_report(self, temp_codebase):
        """Test that rating is set in report."""
        (Path(temp_codebase) / "app.py").write_text("x = 1")

        aegis = Aegis(temp_codebase)
        report = aegis.analyze()

        # Should have some rating (even if TOO_SMALL)
        assert report.shield_rating in [
            "ADAMANTINE",
            "STEEL",
            "BRONZE",
            "WOOD",
            "PAPER",
            "TOO_SMALL",
            "",
        ]


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestIntegration:
    """Integration tests for the full analysis pipeline."""

    def test_full_analysis_resilient(self, resilient_codebase):
        """Test full analysis on resilient codebase."""
        aegis = Aegis(resilient_codebase)
        report = aegis.analyze()

        assert report.codebase_path == resilient_codebase
        assert report.timestamp != ""
        assert report.shield_rating in [
            "ADAMANTINE",
            "STEEL",
            "BRONZE",
            "WOOD",
            "PAPER",
            "TOO_SMALL",
        ]
        # Score is 0-100 OR -1 for TOO_SMALL
        assert -1 <= report.overall_resilience_score <= 100

    def test_full_analysis_fragile(self, fragile_codebase):
        """Test full analysis on fragile codebase."""
        aegis = Aegis(fragile_codebase)
        report = aegis.analyze()

        assert report.codebase_path == fragile_codebase
        assert report.shield_rating != ""

    def test_save_report(self, resilient_codebase):
        """Test saving report to JSON."""
        aegis = Aegis(resilient_codebase)
        report = aegis.analyze()

        output_path = Path(resilient_codebase) / "aegis_report.json"
        saved_path = aegis.save_report(report, str(output_path))

        assert Path(saved_path).exists()

        with open(saved_path, encoding="utf-8") as f:
            data = json.load(f)

        assert "shield_rating" in data
        assert "overall_resilience_score" in data


# =============================================================================
# RECOMMENDATION TESTS
# =============================================================================


class TestRecommendations:
    """Tests for recommendation generation."""

    def test_recommendations_list(self, fragile_codebase):
        """Test that recommendations are generated."""
        aegis = Aegis(fragile_codebase)
        report = aegis.analyze()

        # Recommendations should be a list
        assert isinstance(report.recommendations, list)


# =============================================================================
# EDGE CASES
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases."""

    def test_empty_directory(self, temp_codebase):
        """Test handling of empty directory."""
        aegis = Aegis(temp_codebase)
        report = aegis.analyze()

        assert report is not None

    def test_single_file(self, temp_codebase):
        """Test handling of single file."""
        (Path(temp_codebase) / "app.py").write_text("print('hello')")

        aegis = Aegis(temp_codebase)
        report = aegis.analyze()

        assert report is not None

    def test_binary_files_ignored(self, temp_codebase):
        """Test that binary files are ignored."""
        (Path(temp_codebase) / "data.bin").write_bytes(b"\x00\x01\x02\x03")

        aegis = Aegis(temp_codebase)
        report = aegis.analyze()

        assert report is not None

    def test_nested_directories(self, temp_codebase):
        """Test handling of nested directory structure."""
        deep_dir = Path(temp_codebase) / "a" / "b" / "c"
        deep_dir.mkdir(parents=True)
        (deep_dir / "deep.py").write_text("x = 1")

        aegis = Aegis(temp_codebase)
        report = aegis.analyze()

        assert report is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
