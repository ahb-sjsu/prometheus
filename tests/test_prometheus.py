#!/usr/bin/env python3
"""
Tests for prometheus.py - Combined Complexity & Resilience Fitness Analyzer
"""

import json
import tempfile
from pathlib import Path

import pytest

from prometheus import (
    GitHubMetadata,
    Prometheus,
    PrometheusReport,
    is_github_url,
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
def simple_codebase(temp_codebase):
    """Create a simple, low-complexity codebase."""
    app_py = Path(temp_codebase) / "app.py"
    app_py.write_text(
        '''
"""Simple application."""

def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

def greet(name: str) -> str:
    """Greet someone."""
    return f"Hello, {name}!"

if __name__ == "__main__":
    print(greet("World"))
'''
    )

    return temp_codebase


@pytest.fixture
def complex_codebase(temp_codebase):
    """Create a more complex codebase."""
    # Complex main file
    app_py = Path(temp_codebase) / "app.py"
    app_py.write_text(
        '''
"""Complex application with multiple concerns."""
import os
import sys
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class DataProcessor:
    """Process data with various strategies."""

    def __init__(self, config: Dict):
        self.config = config
        self.cache = {}

    def process(self, items: List[str]) -> List[str]:
        """Process items with multiple conditions."""
        results = []
        for item in items:
            if item in self.cache:
                results.append(self.cache[item])
            elif item.startswith('a'):
                if len(item) > 5:
                    if item.endswith('z'):
                        results.append(item.upper())
                    else:
                        results.append(item.title())
                else:
                    results.append(item.lower())
            elif item.startswith('b'):
                try:
                    processed = self._transform(item)
                    results.append(processed)
                except ValueError as e:
                    logger.error(f"Transform failed: {e}")
                    results.append(item)
            else:
                results.append(item)
        return results

    def _transform(self, item: str) -> str:
        """Transform an item."""
        if not item:
            raise ValueError("Empty item")
        return item[::-1]
'''
    )

    # Add test file
    test_py = Path(temp_codebase) / "test_app.py"
    test_py.write_text(
        """
import pytest
from app import DataProcessor

def test_process_empty():
    processor = DataProcessor({})
    assert processor.process([]) == []

def test_process_items():
    processor = DataProcessor({})
    result = processor.process(['abc', 'bcd'])
    assert len(result) == 2
"""
    )

    return temp_codebase


# =============================================================================
# URL PARSING TESTS
# =============================================================================


class TestIsGitHubUrl:
    """Tests for is_github_url function."""

    def test_https_url(self):
        """Test HTTPS GitHub URL."""
        assert is_github_url("https://github.com/owner/repo") is True

    def test_https_url_with_git(self):
        """Test HTTPS URL with .git suffix."""
        assert is_github_url("https://github.com/owner/repo.git") is True

    def test_ssh_url(self):
        """Test SSH GitHub URL."""
        assert is_github_url("git@github.com:owner/repo.git") is True

    def test_short_form(self):
        """Test short form owner/repo."""
        assert is_github_url("owner/repo") is True
        assert is_github_url("pallets/flask") is True

    def test_local_path(self):
        """Test that local paths are not GitHub URLs."""
        assert is_github_url("/home/user/project") is False
        assert is_github_url("./my-project") is False
        assert is_github_url("C:\\Users\\project") is False

    def test_other_git_hosts(self):
        """Test that other Git hosts are not GitHub URLs."""
        assert is_github_url("https://gitlab.com/owner/repo") is False
        assert is_github_url("https://bitbucket.org/owner/repo") is False


# =============================================================================
# DATA MODEL TESTS
# =============================================================================


class TestGitHubMetadata:
    """Tests for GitHubMetadata dataclass."""

    def test_default_values(self):
        """Test default values."""
        meta = GitHubMetadata()
        assert meta.name == ""
        assert meta.stars == 0
        assert meta.topics == []

    def test_custom_values(self):
        """Test custom values."""
        meta = GitHubMetadata(
            name="flask",
            full_name="pallets/flask",
            description="Web framework",
            stars=50000,
            language="Python",
        )
        assert meta.stars == 50000
        assert meta.language == "Python"


class TestPrometheusReport:
    """Tests for PrometheusReport dataclass."""

    def test_default_values(self):
        """Test default values."""
        report = PrometheusReport(
            codebase_path="/test",
            timestamp="2024-01-01",
        )
        assert report.complexity_score == 0.0
        assert report.resilience_score == 0.0
        assert report.quadrant == ""

    def test_custom_values(self):
        """Test custom values."""
        report = PrometheusReport(
            codebase_path="/test",
            timestamp="2024-01-01",
            complexity_score=75.0,
            resilience_score=60.0,
            quadrant="BUNKER",
        )
        assert report.complexity_score == 75.0
        assert report.quadrant == "BUNKER"


# =============================================================================
# PROMETHEUS ANALYZER TESTS
# =============================================================================


class TestPrometheus:
    """Tests for Prometheus analyzer class."""

    def test_init_local_path(self, temp_codebase):
        """Test initialization with local path."""
        prometheus = Prometheus(temp_codebase)
        assert prometheus.codebase_path == Path(temp_codebase).resolve()
        assert prometheus.cloned is False

    def test_init_current_dir(self, temp_codebase):
        """Test initialization with current directory."""
        import os

        original_dir = os.getcwd()
        try:
            os.chdir(temp_codebase)
            prometheus = Prometheus(".")
            assert prometheus.codebase_path == Path(temp_codebase).resolve()
        finally:
            os.chdir(original_dir)

    def test_library_mode(self, temp_codebase):
        """Test library mode flag."""
        prometheus = Prometheus(temp_codebase, library_mode=True)
        assert prometheus.library_mode is True

    def test_analyze_simple(self, simple_codebase):
        """Test analysis of simple codebase."""
        prometheus = Prometheus(simple_codebase)
        report = prometheus.analyze()

        assert report is not None
        assert report.codebase_path == simple_codebase
        assert report.quadrant != ""

    def test_analyze_complex(self, complex_codebase):
        """Test analysis of complex codebase."""
        prometheus = Prometheus(complex_codebase)
        report = prometheus.analyze()

        assert report is not None
        assert report.complexity_score >= 0
        assert report.resilience_score >= 0 or report.resilience_score == -1  # -1 for too small


# =============================================================================
# QUADRANT TESTS
# =============================================================================


class TestQuadrantDetermination:
    """Tests for quadrant determination."""

    def test_quadrants_defined(self):
        """Test that all quadrants are defined."""
        assert "BUNKER" in Prometheus.QUADRANTS
        assert "FORTRESS" in Prometheus.QUADRANTS
        assert "GLASS_HOUSE" in Prometheus.QUADRANTS
        assert "DEATHTRAP" in Prometheus.QUADRANTS

    def test_quadrant_attributes(self):
        """Test that quadrants have required attributes."""
        for _name, quadrant in Prometheus.QUADRANTS.items():
            assert "name" in quadrant
            assert "description" in quadrant
            assert "emoji" in quadrant
            assert "action" in quadrant

    def test_quadrant_in_report(self, complex_codebase):
        """Test that quadrant is set in report."""
        prometheus = Prometheus(complex_codebase)
        report = prometheus.analyze()

        assert report.quadrant != ""
        assert report.fitness_verdict != ""


# =============================================================================
# PRIORITY GENERATION TESTS
# =============================================================================


class TestPriorityGeneration:
    """Tests for priority generation."""

    def test_priorities_list(self, complex_codebase):
        """Test that priorities are generated as a list."""
        prometheus = Prometheus(complex_codebase)
        report = prometheus.analyze()

        assert isinstance(report.priorities, list)

    def test_priority_structure(self, complex_codebase):
        """Test priority item structure."""
        prometheus = Prometheus(complex_codebase)
        report = prometheus.analyze()

        for priority in report.priorities:
            assert "priority" in priority
            assert "category" in priority
            assert "action" in priority


# =============================================================================
# SCORING TESTS
# =============================================================================


class TestScoring:
    """Tests for complexity and resilience scoring."""

    def test_complexity_score_range(self, simple_codebase):
        """Test that complexity score is in valid range."""
        prometheus = Prometheus(simple_codebase)
        report = prometheus.analyze()

        assert 0 <= report.complexity_score <= 100

    def test_resilience_score_range(self, simple_codebase):
        """Test that resilience score is in valid range."""
        prometheus = Prometheus(simple_codebase)
        report = prometheus.analyze()

        # Score is 0-100 or -1 for too small
        assert (0 <= report.resilience_score <= 100) or report.resilience_score == -1


# =============================================================================
# REPORT SAVING TESTS
# =============================================================================


class TestReportSaving:
    """Tests for report saving functionality."""

    def test_save_report(self, simple_codebase):
        """Test saving report to JSON."""
        prometheus = Prometheus(simple_codebase)
        report = prometheus.analyze()

        output_path = Path(simple_codebase) / "prometheus_report.json"
        saved_path = prometheus.save_report(report, str(output_path))

        assert Path(saved_path).exists()

    def test_saved_report_content(self, simple_codebase):
        """Test content of saved report."""
        prometheus = Prometheus(simple_codebase)
        report = prometheus.analyze()

        output_path = Path(simple_codebase) / "prometheus_report.json"
        prometheus.save_report(report, str(output_path))

        # Use UTF-8 encoding to handle special characters
        with open(output_path, encoding="utf-8") as f:
            data = json.load(f)

        assert "codebase_path" in data
        assert "quadrant" in data
        assert "scores" in data

    def test_default_output_path(self, simple_codebase):
        """Test default output path generation."""
        prometheus = Prometheus(simple_codebase)
        report = prometheus.analyze()

        # Save without specifying path
        saved_path = prometheus.save_report(report)

        assert Path(saved_path).exists()
        assert prometheus.repo_name in saved_path


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestIntegration:
    """Integration tests for full workflow."""

    def test_full_analysis_workflow(self, complex_codebase):
        """Test complete analysis workflow."""
        prometheus = Prometheus(complex_codebase)
        report = prometheus.analyze()

        # Verify all expected fields
        assert report.codebase_path == complex_codebase
        assert report.timestamp != ""
        assert report.quadrant != ""
        assert report.fitness_verdict != ""

    def test_library_mode_analysis(self, simple_codebase):
        """Test analysis in library mode."""
        prometheus = Prometheus(simple_codebase, library_mode=True)
        report = prometheus.analyze()

        assert report is not None

    def test_cleanup_not_cloned(self, simple_codebase):
        """Test that cleanup doesn't fail for non-cloned repos."""
        prometheus = Prometheus(simple_codebase)
        prometheus.analyze()  # Don't assign to unused variable

        # Should not raise an error
        prometheus.cleanup()


# =============================================================================
# EDGE CASES
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases."""

    def test_empty_directory(self, temp_codebase):
        """Test analysis of empty directory."""
        prometheus = Prometheus(temp_codebase)
        report = prometheus.analyze()

        assert report is not None

    def test_single_file(self, temp_codebase):
        """Test analysis of single file."""
        (Path(temp_codebase) / "main.py").write_text("x = 1")

        prometheus = Prometheus(temp_codebase)
        report = prometheus.analyze()

        assert report is not None

    def test_nested_directories(self, temp_codebase):
        """Test analysis of nested directory structure."""
        src_dir = Path(temp_codebase) / "src" / "core" / "utils"
        src_dir.mkdir(parents=True)
        (src_dir / "helpers.py").write_text("def helper(): pass")

        prometheus = Prometheus(temp_codebase)
        report = prometheus.analyze()

        assert report is not None

    def test_mixed_languages(self, temp_codebase):
        """Test codebase with multiple languages."""
        (Path(temp_codebase) / "app.py").write_text("print('Python')")
        (Path(temp_codebase) / "app.js").write_text("console.log('JavaScript');")
        (Path(temp_codebase) / "main.go").write_text("package main")

        prometheus = Prometheus(temp_codebase)
        report = prometheus.analyze()

        assert report is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
