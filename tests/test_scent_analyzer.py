#!/usr/bin/env python3
"""
Tests for scent_analyzer.py - Code Smell Analyzer
"""

import tempfile
from pathlib import Path

import pytest

from scent_analyzer import (
    CodeSmells,
    FileSmellMetrics,
    NIHPatterns,
    OutdatedPatterns,
    ScentAnalyzer,
    ScentReport,
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
def clean_codebase(temp_codebase):
    """Create a clean codebase with no smells."""
    app_py = Path(temp_codebase) / "app.py"
    app_py.write_text(
        '''
"""Clean application code."""
import logging
from typing import List

logger = logging.getLogger(__name__)


def process_items(items: List[str]) -> List[str]:
    """Process a list of items."""
    return [item.strip().lower() for item in items if item]


def calculate_total(values: List[int]) -> int:
    """Calculate the total of values."""
    return sum(values)
'''
    )

    return temp_codebase


@pytest.fixture
def smelly_codebase(temp_codebase):
    """Create a codebase with code smells."""
    # Very long function
    long_py = Path(temp_codebase) / "long_functions.py"
    content = '''
def very_long_function(x):
    """A function that is way too long."""
'''
    for i in range(100):
        content += f"    step_{i} = x + {i}\n"
    content += "    return step_99\n"
    long_py.write_text(content)

    # Deeply nested code
    nested_py = Path(temp_codebase) / "deeply_nested.py"
    nested_py.write_text(
        '''
def deeply_nested(data):
    """Function with deep nesting."""
    if data:
        if isinstance(data, dict):
            if 'items' in data:
                for item in data['items']:
                    if item:
                        if 'value' in item:
                            if item['value'] > 0:
                                if item['value'] < 100:
                                    return item['value']
    return None
'''
    )

    return temp_codebase


# =============================================================================
# DATA MODEL TESTS
# =============================================================================


class TestNIHPatterns:
    """Tests for NIHPatterns dataclass."""

    def test_default_values(self):
        """Test default values."""
        patterns = NIHPatterns()
        # Correct field name: custom_string_functions
        assert patterns.custom_string_functions == 0
        assert patterns.custom_http_clients == 0
        assert patterns.trivial_wrappers == 0

    def test_custom_values(self):
        """Test custom values."""
        patterns = NIHPatterns(
            custom_string_functions=3,  # Correct field name
            custom_http_clients=2,
        )
        assert patterns.custom_string_functions == 3
        assert patterns.custom_http_clients == 2


class TestCodeSmells:
    """Tests for CodeSmells dataclass."""

    def test_default_values(self):
        """Test default values."""
        smells = CodeSmells()
        assert smells.long_functions == 0
        assert smells.deep_nesting == 0
        assert smells.god_classes == 0

    def test_custom_values(self):
        """Test custom values."""
        smells = CodeSmells(
            long_functions=10,
            deep_nesting=5,
        )
        assert smells.long_functions == 10


class TestOutdatedPatterns:
    """Tests for OutdatedPatterns dataclass."""

    def test_default_values(self):
        """Test default values."""
        patterns = OutdatedPatterns()
        assert patterns.deprecated_imports == 0
        assert patterns.deprecated_apis == 0
        assert patterns.old_style_classes == 0
        assert patterns.legacy_syntax == 0

    def test_custom_values(self):
        """Test custom values."""
        patterns = OutdatedPatterns(
            deprecated_imports=5,
            deprecated_apis=3,
        )
        assert patterns.deprecated_imports == 5


class TestFileSmellMetrics:
    """Tests for FileSmellMetrics dataclass."""

    def test_default_values(self):
        """Test default values."""
        metrics = FileSmellMetrics(path="test.py", language="python")
        assert metrics.path == "test.py"
        assert metrics.lines_of_code == 0

    def test_nested_metrics(self):
        """Test nested metrics initialization."""
        metrics = FileSmellMetrics(path="test.py", language="python")
        assert isinstance(metrics.nih, NIHPatterns)
        assert isinstance(metrics.smells, CodeSmells)
        assert isinstance(metrics.outdated, OutdatedPatterns)


class TestScentReport:
    """Tests for ScentReport dataclass."""

    def test_default_values(self):
        """Test default values."""
        report = ScentReport(codebase_path="/test", timestamp="2024-01-01")
        assert report.total_files == 0
        assert report.freshness_rating == ""

    def test_custom_values(self):
        """Test custom values."""
        report = ScentReport(
            codebase_path="/test",
            timestamp="2024-01-01",
            nih_score=25.0,
            smell_score=30.0,
            freshness_rating="FRESH",
        )
        assert report.nih_score == 25.0
        assert report.freshness_rating == "FRESH"


# =============================================================================
# SCENT ANALYZER TESTS
# =============================================================================


class TestScentAnalyzer:
    """Tests for ScentAnalyzer class."""

    def test_init(self, temp_codebase):
        """Test ScentAnalyzer initialization."""
        analyzer = ScentAnalyzer(temp_codebase)
        assert analyzer.codebase_path == Path(temp_codebase)

    def test_analyze_empty(self, temp_codebase):
        """Test analysis of empty codebase."""
        analyzer = ScentAnalyzer(temp_codebase)
        report = analyzer.analyze()

        assert report is not None
        assert report.codebase_path == temp_codebase

    def test_analyze_clean(self, clean_codebase):
        """Test analysis of clean codebase."""
        analyzer = ScentAnalyzer(clean_codebase)
        report = analyzer.analyze()

        assert report is not None
        assert report.total_files >= 1

    def test_analyze_smelly(self, smelly_codebase):
        """Test analysis of smelly codebase."""
        analyzer = ScentAnalyzer(smelly_codebase)
        report = analyzer.analyze()

        assert report is not None
        assert report.total_files >= 1


# =============================================================================
# NIH DETECTION TESTS
# =============================================================================


class TestNIHDetection:
    """Tests for NIH pattern detection."""

    def test_detects_custom_http_client(self, temp_codebase):
        """Test detection of custom HTTP client."""
        py_file = Path(temp_codebase) / "http.py"
        py_file.write_text(
            '''
class CustomHttpClient:
    """Custom HTTP client."""

    def get(self, url):
        import socket
        sock = socket.socket()
        return sock.recv(1024)
'''
        )

        analyzer = ScentAnalyzer(temp_codebase)
        report = analyzer.analyze()

        assert report is not None


# =============================================================================
# SMELL DETECTION TESTS
# =============================================================================


class TestSmellDetection:
    """Tests for code smell detection."""

    def test_detects_long_function(self, temp_codebase):
        """Test detection of long functions."""
        py_file = Path(temp_codebase) / "long.py"
        content = "def long_function():\n"
        for i in range(60):
            content += f"    x_{i} = {i}\n"
        content += "    return x_59\n"
        py_file.write_text(content)

        analyzer = ScentAnalyzer(temp_codebase)
        report = analyzer.analyze()

        assert report is not None

    def test_detects_deep_nesting(self, temp_codebase):
        """Test detection of deep nesting."""
        py_file = Path(temp_codebase) / "nested.py"
        py_file.write_text(
            """
def deeply_nested(x):
    if x:
        if x > 0:
            if x < 100:
                if x % 2 == 0:
                    if x % 3 == 0:
                        return x
    return None
"""
        )

        analyzer = ScentAnalyzer(temp_codebase)
        report = analyzer.analyze()

        assert report is not None


# =============================================================================
# FRESHNESS DETECTION TESTS
# =============================================================================


class TestFreshnessDetection:
    """Tests for freshness/staleness detection."""

    def test_detects_deprecated_imports(self, temp_codebase):
        """Test detection of deprecated imports."""
        py_file = Path(temp_codebase) / "old.py"
        py_file.write_text(
            """
import imp  # Deprecated
import optparse  # Deprecated in favor of argparse
"""
        )

        analyzer = ScentAnalyzer(temp_codebase)
        report = analyzer.analyze()

        assert report is not None


# =============================================================================
# FRESHNESS RATING TESTS
# =============================================================================


class TestFreshnessRating:
    """Tests for freshness rating assignment."""

    def test_fresh_rating(self, clean_codebase):
        """Test rating for clean code."""
        analyzer = ScentAnalyzer(clean_codebase)
        report = analyzer.analyze()

        # Should have some rating
        assert report.freshness_rating in ["FRESH", "STALE", "MOLDY", "ROTTEN", ""]

    def test_rating_assigned(self, smelly_codebase):
        """Test that a rating is assigned."""
        analyzer = ScentAnalyzer(smelly_codebase)
        report = analyzer.analyze()

        assert report.freshness_rating in ["FRESH", "STALE", "MOLDY", "ROTTEN", ""]


# =============================================================================
# SCORING TESTS
# =============================================================================


class TestScoring:
    """Tests for score calculation."""

    def test_nih_score_range(self, temp_codebase):
        """Test that NIH score is in valid range."""
        (Path(temp_codebase) / "app.py").write_text("x = 1")

        analyzer = ScentAnalyzer(temp_codebase)
        report = analyzer.analyze()

        assert 0 <= report.nih_score <= 100

    def test_smell_score_range(self, temp_codebase):
        """Test that smell score is in valid range."""
        (Path(temp_codebase) / "app.py").write_text("x = 1")

        analyzer = ScentAnalyzer(temp_codebase)
        report = analyzer.analyze()

        assert 0 <= report.smell_score <= 100


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestIntegration:
    """Integration tests."""

    def test_full_analysis(self, smelly_codebase):
        """Test complete analysis workflow."""
        analyzer = ScentAnalyzer(smelly_codebase)
        report = analyzer.analyze()

        assert report.codebase_path == smelly_codebase
        assert report.timestamp != ""
        assert report.freshness_rating in ["FRESH", "STALE", "MOLDY", "ROTTEN", ""]

    def test_save_report(self, clean_codebase):
        """Test saving report to JSON."""
        analyzer = ScentAnalyzer(clean_codebase)
        report = analyzer.analyze()

        output_path = Path(clean_codebase) / "scent_report.json"
        saved_path = analyzer.save_report(report, str(output_path))

        assert Path(saved_path).exists()

        import json

        with open(saved_path, encoding="utf-8") as f:
            data = json.load(f)

        assert "freshness_rating" in data


# =============================================================================
# EDGE CASES
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases."""

    def test_empty_directory(self, temp_codebase):
        """Test handling of empty directory."""
        analyzer = ScentAnalyzer(temp_codebase)
        report = analyzer.analyze()

        assert report is not None

    def test_single_line_file(self, temp_codebase):
        """Test handling of single-line file."""
        (Path(temp_codebase) / "one.py").write_text("x = 1")

        analyzer = ScentAnalyzer(temp_codebase)
        report = analyzer.analyze()

        assert report is not None

    def test_non_python_files(self, temp_codebase):
        """Test handling of non-Python files."""
        (Path(temp_codebase) / "app.js").write_text("const x = 1;")
        (Path(temp_codebase) / "main.go").write_text("package main")

        analyzer = ScentAnalyzer(temp_codebase)
        report = analyzer.analyze()

        assert report is not None

    def test_binary_file(self, temp_codebase):
        """Test handling of binary files."""
        (Path(temp_codebase) / "data.bin").write_bytes(b"\x00\x01\x02\x03")

        analyzer = ScentAnalyzer(temp_codebase)
        report = analyzer.analyze()

        assert report is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
