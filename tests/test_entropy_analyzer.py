#!/usr/bin/env python3
"""
Tests for entropy_analyzer.py - Complexity Fitness Analyzer

Tests cover:
- Data models (FileMetrics, TaskMetrics, CodebaseMetrics, FitnessReport)
- Extractor class (file discovery, analysis, entropy calculation)
- Transformer class (metric aggregation)
- Analyzer class (risk assessment, verdicts)
- ComplexityFitnessPipeline (end-to-end)
"""

import tempfile
from dataclasses import asdict
from pathlib import Path

import pytest

from prometheus.entropy_analyzer import (
    Analyzer,
    CodebaseMetrics,
    ComplexityFitnessPipeline,
    Extractor,
    FileMetrics,
    TaskMetrics,
    Transformer,
)

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def temp_codebase():
    """Create a temporary codebase for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a simple Python file
        simple_py = Path(tmpdir) / "simple.py"
        simple_py.write_text(
            '''
def hello():
    """Say hello."""
    print("Hello, world!")

def add(a, b):
    """Add two numbers."""
    return a + b
'''
        )

        # Create a more complex Python file
        complex_py = Path(tmpdir) / "complex.py"
        complex_py.write_text(
            '''
import os
import sys
from typing import List, Optional

class DataProcessor:
    """Process data with multiple methods."""

    def __init__(self, config: dict):
        self.config = config
        self.data = []

    def process(self, items: List[str]) -> List[str]:
        """Process items with conditional logic."""
        results = []
        for item in items:
            if item.startswith('a'):
                if len(item) > 5:
                    results.append(item.upper())
                else:
                    results.append(item.lower())
            elif item.startswith('b'):
                results.append(item[::-1])
            else:
                results.append(item)
        return results

    def validate(self, data: Optional[str]) -> bool:
        """Validate data with nested conditions."""
        if data is None:
            return False
        if len(data) < 1:
            return False
        if not data.isalnum():
            return False
        return True
'''
        )

        # Create a test file
        test_py = Path(tmpdir) / "test_simple.py"
        test_py.write_text(
            '''
import pytest
from simple import hello, add

def test_hello():
    """Test hello function."""
    assert hello() is None

def test_add():
    """Test add function."""
    assert add(1, 2) == 3
    assert add(-1, 1) == 0
'''
        )

        yield tmpdir


@pytest.fixture
def sample_file_metrics():
    """Create sample FileMetrics for testing."""
    return [
        FileMetrics(
            path="file1.py",
            language="python",
            lines_of_code=100,
            lines_total=120,
            cyclomatic_complexity=3.5,
            maintainability_index=75.0,
            num_functions=10,
            num_classes=2,
            token_entropy=5.5,
            compression_ratio=2.5,
        ),
        FileMetrics(
            path="file2.py",
            language="python",
            lines_of_code=200,
            lines_total=250,
            cyclomatic_complexity=5.0,
            maintainability_index=60.0,
            num_functions=20,
            num_classes=5,
            token_entropy=6.0,
            compression_ratio=2.8,
        ),
    ]


@pytest.fixture
def sample_task_metrics():
    """Create sample TaskMetrics for testing."""
    return TaskMetrics(
        num_test_files=5,
        num_test_cases=25,
        num_assertions=50,
        api_endpoints=10,
        distinct_features=15,
        estimated_function_points=30.0,
    )


# =============================================================================
# DATA MODEL TESTS
# =============================================================================


class TestFileMetrics:
    """Tests for FileMetrics dataclass."""

    def test_default_values(self):
        """Test that default values are set correctly."""
        metrics = FileMetrics(path="test.py", language="python")
        assert metrics.path == "test.py"
        assert metrics.language == "python"
        assert metrics.lines_of_code == 0
        assert metrics.cyclomatic_complexity == 0.0
        assert metrics.dependencies == []

    def test_custom_values(self):
        """Test setting custom values."""
        metrics = FileMetrics(
            path="complex.py",
            language="python",
            lines_of_code=500,
            cyclomatic_complexity=15.0,
            maintainability_index=45.0,
        )
        assert metrics.lines_of_code == 500
        assert metrics.cyclomatic_complexity == 15.0
        assert metrics.maintainability_index == 45.0

    def test_serialization(self):
        """Test that FileMetrics can be serialized."""
        metrics = FileMetrics(path="test.py", language="python", lines_of_code=100)
        data = asdict(metrics)
        assert data["path"] == "test.py"
        assert data["lines_of_code"] == 100


class TestTaskMetrics:
    """Tests for TaskMetrics dataclass."""

    def test_default_values(self):
        """Test default values."""
        metrics = TaskMetrics()
        assert metrics.num_test_files == 0
        assert metrics.estimated_function_points == 0.0

    def test_function_point_calculation(self):
        """Test that function points can be set."""
        metrics = TaskMetrics(
            num_test_cases=20,
            api_endpoints=5,
            estimated_function_points=25.0,
        )
        assert metrics.estimated_function_points == 25.0


class TestCodebaseMetrics:
    """Tests for CodebaseMetrics dataclass."""

    def test_default_values(self):
        """Test default values."""
        metrics = CodebaseMetrics()
        assert metrics.total_files == 0
        assert metrics.avg_cyclomatic == 0.0

    def test_aggregate_values(self):
        """Test setting aggregate values."""
        metrics = CodebaseMetrics(
            total_files=50,
            total_loc=10000,
            avg_cyclomatic=4.5,
            avg_maintainability=70.0,
        )
        assert metrics.total_files == 50
        assert metrics.total_loc == 10000


# =============================================================================
# EXTRACTOR TESTS
# =============================================================================


class TestExtractor:
    """Tests for Extractor class."""

    def test_init(self, temp_codebase):
        """Test Extractor initialization."""
        extractor = Extractor(temp_codebase)
        assert extractor.codebase_path == Path(temp_codebase)
        assert extractor.file_metrics == []

    def test_language_extensions(self):
        """Test that language extensions are properly defined."""
        assert Extractor.LANGUAGE_EXTENSIONS[".py"] == "python"
        assert Extractor.LANGUAGE_EXTENSIONS[".js"] == "javascript"
        assert Extractor.LANGUAGE_EXTENSIONS[".go"] == "go"

    def test_extract_finds_files(self, temp_codebase):
        """Test that extract finds Python files."""
        extractor = Extractor(temp_codebase)
        file_metrics, task_metrics = extractor.extract()

        # Should find simple.py, complex.py, test_simple.py
        assert len(file_metrics) >= 2
        paths = [m.path for m in file_metrics]
        assert any("simple.py" in p for p in paths)

    def test_extract_counts_lines(self, temp_codebase):
        """Test that line counts are accurate."""
        extractor = Extractor(temp_codebase)
        file_metrics, _ = extractor.extract()

        for metrics in file_metrics:
            assert metrics.lines_total > 0
            assert metrics.lines_of_code <= metrics.lines_total

    def test_extract_calculates_entropy(self, temp_codebase):
        """Test that entropy is calculated."""
        extractor = Extractor(temp_codebase)
        file_metrics, _ = extractor.extract()

        for metrics in file_metrics:
            # Entropy should be positive for non-empty files
            assert metrics.token_entropy >= 0

    def test_extract_calculates_compression_ratio(self, temp_codebase):
        """Test that compression ratio is calculated."""
        extractor = Extractor(temp_codebase)
        file_metrics, _ = extractor.extract()

        for metrics in file_metrics:
            # Compression ratio should be >= 1
            assert metrics.compression_ratio >= 1.0

    def test_extract_finds_test_files(self, temp_codebase):
        """Test that test files are detected."""
        extractor = Extractor(temp_codebase)
        _, task_metrics = extractor.extract()

        assert task_metrics.num_test_files >= 1
        assert task_metrics.num_test_cases >= 1

    def test_skips_excluded_directories(self, temp_codebase):
        """Test that node_modules, venv, etc. are skipped."""
        # Create a file in a directory that should be skipped
        venv_dir = Path(temp_codebase) / "venv" / "lib"
        venv_dir.mkdir(parents=True)
        (venv_dir / "skipped.py").write_text("# should be skipped")

        extractor = Extractor(temp_codebase)
        file_metrics, _ = extractor.extract()

        paths = [m.path for m in file_metrics]
        assert not any("venv" in p for p in paths)


class TestExtractorEntropyCalculation:
    """Tests for entropy calculation in Extractor."""

    def test_empty_content_returns_zero(self, temp_codebase):
        """Test that empty content returns 0 entropy."""
        extractor = Extractor(temp_codebase)
        assert extractor._calculate_entropy("") == 0.0

    def test_single_token_returns_zero(self, temp_codebase):
        """Test that single repeated token returns 0 entropy."""
        extractor = Extractor(temp_codebase)
        # All same tokens = 0 entropy (no uncertainty)
        entropy = extractor._calculate_entropy("word word word word")
        assert entropy == 0.0

    def test_diverse_tokens_higher_entropy(self, temp_codebase):
        """Test that diverse tokens produce higher entropy."""
        extractor = Extractor(temp_codebase)

        # Low diversity
        low_entropy = extractor._calculate_entropy("a a a a b b")

        # High diversity
        high_entropy = extractor._calculate_entropy("a b c d e f g h")

        assert high_entropy > low_entropy

    def test_entropy_is_positive(self, temp_codebase):
        """Test that entropy is non-negative."""
        extractor = Extractor(temp_codebase)
        entropy = extractor._calculate_entropy("def foo(): return bar")
        assert entropy >= 0


class TestExtractorCompressionRatio:
    """Tests for compression ratio calculation."""

    def test_empty_content_returns_one(self, temp_codebase):
        """Test that empty content returns ratio of 1."""
        extractor = Extractor(temp_codebase)
        assert extractor._calculate_compression_ratio("") == 1.0

    def test_repetitive_content_high_ratio(self, temp_codebase):
        """Test that repetitive content compresses well."""
        extractor = Extractor(temp_codebase)
        repetitive = "x = 1\n" * 100
        ratio = extractor._calculate_compression_ratio(repetitive)
        # Repetitive content should compress well (high ratio)
        assert ratio > 2.0

    def test_random_content_low_ratio(self, temp_codebase):
        """Test that random content doesn't compress as well."""
        extractor = Extractor(temp_codebase)
        import random
        import string

        random_content = "".join(random.choices(string.ascii_letters, k=1000))
        ratio = extractor._calculate_compression_ratio(random_content)
        # Random content compresses poorly (ratio closer to 1)
        assert ratio < 3.0


# =============================================================================
# TRANSFORMER TESTS
# =============================================================================


class TestTransformer:
    """Tests for Transformer class."""

    def test_empty_metrics(self):
        """Test transformer with no file metrics."""
        transformer = Transformer([], TaskMetrics())
        result = transformer.transform()

        assert result.total_files == 0
        assert result.total_loc == 0

    def test_aggregates_loc(self, sample_file_metrics, sample_task_metrics):
        """Test that LOC is aggregated correctly."""
        transformer = Transformer(sample_file_metrics, sample_task_metrics)
        result = transformer.transform()

        expected_loc = sum(m.lines_of_code for m in sample_file_metrics)
        assert result.total_loc == expected_loc

    def test_aggregates_functions(self, sample_file_metrics, sample_task_metrics):
        """Test that function counts are aggregated."""
        transformer = Transformer(sample_file_metrics, sample_task_metrics)
        result = transformer.transform()

        expected_funcs = sum(m.num_functions for m in sample_file_metrics)
        assert result.total_functions == expected_funcs

    def test_calculates_average_cyclomatic(self, sample_file_metrics, sample_task_metrics):
        """Test that average cyclomatic complexity is calculated."""
        transformer = Transformer(sample_file_metrics, sample_task_metrics)
        result = transformer.transform()

        # Average of 3.5 and 5.0 = 4.25
        assert result.avg_cyclomatic == pytest.approx(4.25, rel=0.01)

    def test_finds_max_cyclomatic(self, sample_file_metrics, sample_task_metrics):
        """Test that max cyclomatic complexity is found."""
        transformer = Transformer(sample_file_metrics, sample_task_metrics)
        result = transformer.transform()

        assert result.max_cyclomatic == 5.0

    def test_calculates_average_maintainability(self, sample_file_metrics, sample_task_metrics):
        """Test that average maintainability is calculated."""
        transformer = Transformer(sample_file_metrics, sample_task_metrics)
        result = transformer.transform()

        # Average of 75.0 and 60.0 = 67.5
        assert result.avg_maintainability == pytest.approx(67.5, rel=0.01)


# =============================================================================
# ANALYZER TESTS
# =============================================================================


class TestAnalyzer:
    """Tests for Analyzer class."""

    def test_low_risk_codebase(self, sample_file_metrics, sample_task_metrics):
        """Test that low complexity codebase gets LOW risk."""
        # Modify metrics to be low risk
        for m in sample_file_metrics:
            m.cyclomatic_complexity = 2.0
            m.maintainability_index = 80.0

        transformer = Transformer(sample_file_metrics, sample_task_metrics)
        codebase_metrics = transformer.transform()

        analyzer = Analyzer(
            "/fake/path", sample_file_metrics, sample_task_metrics, codebase_metrics
        )
        report = analyzer.analyze()

        assert report.risk_level in ["LOW", "MEDIUM"]

    def test_high_risk_codebase(self, sample_file_metrics, sample_task_metrics):
        """Test that high complexity codebase gets HIGH/CRITICAL risk."""
        # Modify metrics to be high risk
        for m in sample_file_metrics:
            m.cyclomatic_complexity = 25.0
            m.maintainability_index = 30.0
            m.halstead_bugs = 10.0

        transformer = Transformer(sample_file_metrics, sample_task_metrics)
        codebase_metrics = transformer.transform()

        analyzer = Analyzer(
            "/fake/path", sample_file_metrics, sample_task_metrics, codebase_metrics
        )
        report = analyzer.analyze()

        assert report.risk_level in ["HIGH", "CRITICAL"]

    def test_generates_recommendations(self, sample_file_metrics, sample_task_metrics):
        """Test that recommendations are generated."""
        transformer = Transformer(sample_file_metrics, sample_task_metrics)
        codebase_metrics = transformer.transform()

        analyzer = Analyzer(
            "/fake/path", sample_file_metrics, sample_task_metrics, codebase_metrics
        )
        report = analyzer.analyze()

        # Should have some verdict
        assert report.overall_verdict != ""

    def test_identifies_hotspots(self, sample_file_metrics, sample_task_metrics):
        """Test that hotspots are identified for complex files."""
        # Make one file a hotspot
        sample_file_metrics[0].cyclomatic_complexity = 30.0
        sample_file_metrics[0].maintainability_index = 25.0

        transformer = Transformer(sample_file_metrics, sample_task_metrics)
        codebase_metrics = transformer.transform()

        analyzer = Analyzer(
            "/fake/path", sample_file_metrics, sample_task_metrics, codebase_metrics
        )
        report = analyzer.analyze()

        # Should identify at least one hotspot
        assert len(report.hotspots) >= 1


# =============================================================================
# PIPELINE TESTS
# =============================================================================


class TestComplexityFitnessPipeline:
    """Tests for the full pipeline."""

    def test_pipeline_runs(self, temp_codebase):
        """Test that pipeline runs without error."""
        pipeline = ComplexityFitnessPipeline(temp_codebase)
        report = pipeline.run()

        assert report is not None
        assert report.codebase_path == temp_codebase

    def test_pipeline_produces_valid_report(self, temp_codebase):
        """Test that pipeline produces a valid report."""
        pipeline = ComplexityFitnessPipeline(temp_codebase)
        report = pipeline.run()

        assert report.risk_level in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        assert report.codebase_metrics is not None
        assert report.codebase_metrics.total_files > 0

    def test_pipeline_calculates_fitness_ratios(self, temp_codebase):
        """Test that fitness ratios are calculated."""
        pipeline = ComplexityFitnessPipeline(temp_codebase)
        report = pipeline.run()

        # LOC per function point should be positive
        assert report.loc_per_function_point >= 0


# =============================================================================
# EDGE CASES
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_directory(self):
        """Test handling of empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            extractor = Extractor(tmpdir)
            file_metrics, task_metrics = extractor.extract()

            assert file_metrics == []
            assert task_metrics.num_test_files == 0

    @pytest.mark.xfail(
        reason="Binary file handling not yet implemented - raises ValueError on null bytes"
    )
    def test_binary_file_handling(self, temp_codebase):
        """Test that binary files don't crash the extractor."""
        # Create a binary file with .py extension (edge case)
        binary_py = Path(temp_codebase) / "binary.py"
        binary_py.write_bytes(b"\x00\x01\x02\x03\xff\xfe")

        extractor = Extractor(temp_codebase)
        # Should not raise an exception
        file_metrics, _ = extractor.extract()

        # The binary file might be skipped or have minimal metrics
        assert isinstance(file_metrics, list)

    def test_deeply_nested_directory(self, temp_codebase):
        """Test handling of deeply nested directories."""
        deep_path = Path(temp_codebase)
        for i in range(10):
            deep_path = deep_path / f"level{i}"
        deep_path.mkdir(parents=True)

        (deep_path / "deep.py").write_text("x = 1")

        extractor = Extractor(temp_codebase)
        file_metrics, _ = extractor.extract()

        paths = [m.path for m in file_metrics]
        assert any("deep.py" in p for p in paths)

    def test_unicode_content(self, temp_codebase):
        """Test handling of unicode content."""
        unicode_py = Path(temp_codebase) / "unicode.py"
        unicode_py.write_text(
            '''
# -*- coding: utf-8 -*-
"""Unicode test: 你好世界 🌍"""

def greet():
    return "Héllo Wörld! 👋"
''',
            encoding="utf-8",
        )

        extractor = Extractor(temp_codebase)
        file_metrics, _ = extractor.extract()

        unicode_metrics = [m for m in file_metrics if "unicode.py" in m.path]
        assert len(unicode_metrics) == 1
        assert unicode_metrics[0].lines_of_code > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
