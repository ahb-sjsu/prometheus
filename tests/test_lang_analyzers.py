#!/usr/bin/env python3
"""
Tests for lang_analyzers.py - Language-specific Resilience Analyzers
"""

import tempfile
from pathlib import Path

import pytest

from prometheus.lang_analyzers import (
    AnalyzerRegistry,
    CAnalyzer,
    GoAnalyzer,
    JavaAnalyzer,
    JavaScriptAnalyzer,
    LanguageResilienceMetrics,
    PythonAnalyzer,
    RustAnalyzer,
    analyze_file,
    get_analyzer,
)

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


# =============================================================================
# DATA MODEL TESTS
# =============================================================================


class TestLanguageResilienceMetrics:
    """Tests for LanguageResilienceMetrics dataclass."""

    def test_default_values(self):
        """Test default values."""
        metrics = LanguageResilienceMetrics()
        assert metrics.error_handlers == 0
        assert metrics.resource_guards == 0
        assert metrics.null_checks == 0

    def test_custom_values(self):
        """Test custom values."""
        metrics = LanguageResilienceMetrics(
            error_handlers=10,
            resource_guards=5,
            null_checks=20,
            log_statements=15,  # Correct field name
        )
        assert metrics.error_handlers == 10
        assert metrics.log_statements == 15

    def test_extras_dict(self):
        """Test extras dictionary."""
        metrics = LanguageResilienceMetrics()
        assert isinstance(metrics.extras, dict)

        metrics.extras["custom_key"] = "custom_value"
        assert metrics.extras["custom_key"] == "custom_value"


# =============================================================================
# ANALYZER REGISTRY TESTS
# =============================================================================


class TestAnalyzerRegistry:
    """Tests for analyzer registry."""

    def test_registry_singleton(self):
        """Test that registry provides analyzers."""
        registry = AnalyzerRegistry()
        assert registry is not None

    def test_get_python_analyzer(self):
        """Test getting Python analyzer from registry."""
        registry = AnalyzerRegistry()
        # Use get_analyzer_for_file, not get_analyzer (which takes language name)
        analyzer = registry.get_analyzer_for_file("test.py")
        assert analyzer is not None
        assert isinstance(analyzer, PythonAnalyzer)

    def test_get_javascript_analyzer(self):
        """Test getting JavaScript analyzer from registry."""
        registry = AnalyzerRegistry()
        analyzer = registry.get_analyzer_for_file("test.js")
        assert analyzer is not None
        assert isinstance(analyzer, JavaScriptAnalyzer)

    def test_get_analyzer_by_language_name(self):
        """Test getting analyzer by language name."""
        registry = AnalyzerRegistry()
        analyzer = registry.get_analyzer("python")
        assert analyzer is not None
        assert isinstance(analyzer, PythonAnalyzer)


class TestGetAnalyzer:
    """Tests for get_analyzer factory function."""

    def test_get_python_analyzer(self):
        """Test getting Python analyzer."""
        analyzer = get_analyzer("test.py")
        assert analyzer is not None
        assert isinstance(analyzer, PythonAnalyzer)

    def test_get_javascript_analyzer(self):
        """Test getting JavaScript analyzer."""
        analyzer = get_analyzer("test.js")
        assert analyzer is not None
        assert isinstance(analyzer, JavaScriptAnalyzer)

    def test_get_go_analyzer(self):
        """Test getting Go analyzer."""
        analyzer = get_analyzer("test.go")
        assert analyzer is not None
        assert isinstance(analyzer, GoAnalyzer)

    def test_get_java_analyzer(self):
        """Test getting Java analyzer."""
        analyzer = get_analyzer("test.java")
        assert analyzer is not None
        assert isinstance(analyzer, JavaAnalyzer)

    def test_get_c_analyzer(self):
        """Test getting C analyzer."""
        analyzer = get_analyzer("test.c")
        assert analyzer is not None
        assert isinstance(analyzer, CAnalyzer)

    def test_get_rust_analyzer(self):
        """Test getting Rust analyzer."""
        analyzer = get_analyzer("test.rs")
        assert analyzer is not None
        assert isinstance(analyzer, RustAnalyzer)

    def test_unknown_extension_returns_none(self):
        """Test that unknown extension returns None."""
        analyzer = get_analyzer("test.xyz")
        assert analyzer is None

    def test_handles_path_objects(self):
        """Test that Path objects are handled."""
        analyzer = get_analyzer(Path("test.py"))
        assert analyzer is not None


# =============================================================================
# PYTHON ANALYZER TESTS
# =============================================================================


class TestPythonAnalyzer:
    """Tests for PythonAnalyzer class."""

    def test_language_name(self):
        """Test language name."""
        analyzer = PythonAnalyzer()
        assert analyzer.LANGUAGE_NAME == "python"

    def test_detects_try_except(self):
        """Test detection of try-except blocks."""
        analyzer = PythonAnalyzer()
        code = """
try:
    risky_operation()
except ValueError:
    handle_error()
"""
        metrics = analyzer.analyze(code, "test.py")
        assert metrics.error_handlers >= 1

    def test_detects_context_manager(self):
        """Test detection of context managers."""
        analyzer = PythonAnalyzer()
        code = """
with open('file.txt') as f:
    content = f.read()
"""
        metrics = analyzer.analyze(code, "test.py")
        assert metrics.resource_guards >= 1

    def test_detects_logging(self):
        """Test detection of logging calls."""
        analyzer = PythonAnalyzer()
        code = """
import logging
logger = logging.getLogger(__name__)
logger.info("Processing started")
logger.error("An error occurred")
"""
        metrics = analyzer.analyze(code, "test.py")
        # Use correct field name: log_statements
        assert metrics.log_statements >= 2

    def test_detects_null_checks(self):
        """Test detection of null checks."""
        analyzer = PythonAnalyzer()
        code = """
if value is None:
    return default
if other is not None:
    process(other)
"""
        metrics = analyzer.analyze(code, "test.py")
        assert metrics.null_checks >= 2

    def test_detects_assertions(self):
        """Test detection of assertions."""
        analyzer = PythonAnalyzer()
        code = """
assert value > 0, "Value must be positive"
assert isinstance(data, dict)
"""
        metrics = analyzer.analyze(code, "test.py")
        assert metrics.assertions >= 2


# =============================================================================
# JAVASCRIPT ANALYZER TESTS
# =============================================================================


class TestJavaScriptAnalyzer:
    """Tests for JavaScriptAnalyzer class."""

    def test_language_name(self):
        """Test language name."""
        analyzer = JavaScriptAnalyzer()
        assert analyzer.LANGUAGE_NAME == "javascript"

    def test_detects_try_catch(self):
        """Test detection of try-catch blocks."""
        analyzer = JavaScriptAnalyzer()
        code = """
try {
    riskyOperation();
} catch (error) {
    handleError(error);
}
"""
        metrics = analyzer.analyze(code, "test.js")
        assert metrics.error_handlers >= 1

    def test_detects_console_logging(self):
        """Test detection of console logging."""
        analyzer = JavaScriptAnalyzer()
        code = """
console.log("Debug message");
console.error("Error occurred");
console.warn("Warning");
"""
        metrics = analyzer.analyze(code, "test.js")
        # Use correct field name: log_statements
        assert metrics.log_statements >= 3

    def test_detects_null_checks(self):
        """Test detection of null checks."""
        analyzer = JavaScriptAnalyzer()
        code = """
if (value === null) return;
if (other !== undefined) process(other);
const result = data ?? defaultValue;
"""
        metrics = analyzer.analyze(code, "test.js")
        assert metrics.null_checks >= 1


# =============================================================================
# GO ANALYZER TESTS
# =============================================================================


class TestGoAnalyzer:
    """Tests for GoAnalyzer class."""

    def test_language_name(self):
        """Test language name."""
        analyzer = GoAnalyzer()
        assert analyzer.LANGUAGE_NAME == "go"

    def test_detects_error_handling(self):
        """Test detection of Go error handling."""
        analyzer = GoAnalyzer()
        code = """
result, err := doSomething()
if err != nil {
    return fmt.Errorf("failed: %w", err)
}
"""
        metrics = analyzer.analyze(code, "test.go")
        # Go counts error_checks for `if err != nil`
        assert metrics.error_checks >= 1

    def test_detects_defer(self):
        """Test detection of defer statements."""
        analyzer = GoAnalyzer()
        code = """
func process() {
    f, _ := os.Open("file.txt")
    defer f.Close()
}
"""
        metrics = analyzer.analyze(code, "test.go")
        assert metrics.resource_guards >= 1 or metrics.cleanup_blocks >= 1

    def test_detects_logging(self):
        """Test detection of logging."""
        analyzer = GoAnalyzer()
        code = """
log.Printf("Processing %s", item)
log.Fatal("Critical error")
"""
        metrics = analyzer.analyze(code, "test.go")
        # Use correct field name: log_statements
        assert metrics.log_statements >= 2

    def test_detects_nil_checks(self):
        """Test detection of nil checks."""
        analyzer = GoAnalyzer()
        code = """
if ptr == nil {
    return errors.New("nil pointer")
}
if result != nil {
    process(result)
}
"""
        metrics = analyzer.analyze(code, "test.go")
        assert metrics.null_checks >= 2


# =============================================================================
# JAVA ANALYZER TESTS
# =============================================================================


class TestJavaAnalyzer:
    """Tests for JavaAnalyzer class."""

    def test_language_name(self):
        """Test language name."""
        analyzer = JavaAnalyzer()
        assert analyzer.LANGUAGE_NAME == "java"

    def test_detects_try_catch(self):
        """Test detection of try-catch blocks."""
        analyzer = JavaAnalyzer()
        code = """
try {
    riskyOperation();
} catch (IOException e) {
    logger.error("IO error", e);
}
"""
        metrics = analyzer.analyze(code, "Test.java")
        assert metrics.error_handlers >= 1

    def test_detects_logging(self):
        """Test detection of logging."""
        analyzer = JavaAnalyzer()
        code = """
logger.info("Processing started");
logger.error("An error occurred");
log.debug("Debug info");
"""
        metrics = analyzer.analyze(code, "Test.java")
        # Use correct field name: log_statements
        assert metrics.log_statements >= 3

    def test_detects_null_checks(self):
        """Test detection of null checks."""
        analyzer = JavaAnalyzer()
        code = """
if (value == null) {
    return defaultValue;
}
Objects.requireNonNull(param);
Optional.ofNullable(data);
"""
        metrics = analyzer.analyze(code, "Test.java")
        assert metrics.null_checks >= 1


# =============================================================================
# C ANALYZER TESTS
# =============================================================================


class TestCAnalyzer:
    """Tests for CAnalyzer class."""

    def test_language_name(self):
        """Test language name."""
        analyzer = CAnalyzer()
        assert analyzer.LANGUAGE_NAME == "c"

    def test_detects_null_checks(self):
        """Test detection of null checks."""
        analyzer = CAnalyzer()
        code = """
if (ptr == NULL) {
    return -1;
}
if (other != NULL) {
    process(other);
}
"""
        metrics = analyzer.analyze(code, "test.c")
        assert metrics.null_checks >= 2


# =============================================================================
# ANALYZE_FILE FUNCTION TESTS
# =============================================================================


class TestAnalyzeFile:
    """Tests for analyze_file function."""

    def test_analyze_python_file(self, temp_dir):
        """Test analyzing a Python file."""
        py_file = Path(temp_dir) / "test.py"
        py_file.write_text(
            """
try:
    risky()
except Exception:
    pass
"""
        )

        content = py_file.read_text()
        metrics = analyze_file(str(py_file), content)
        assert metrics is not None
        assert metrics.error_handlers >= 1

    def test_analyze_javascript_file(self, temp_dir):
        """Test analyzing a JavaScript file."""
        js_file = Path(temp_dir) / "test.js"
        js_file.write_text(
            """
try {
    risky();
} catch (e) {
    console.error(e);
}
"""
        )

        content = js_file.read_text()
        metrics = analyze_file(str(js_file), content)
        assert metrics is not None

    def test_analyze_unknown_extension(self, temp_dir):
        """Test analyzing file with unknown extension."""
        unknown_file = Path(temp_dir) / "test.xyz"
        unknown_file.write_text("content")

        content = unknown_file.read_text()
        metrics = analyze_file(str(unknown_file), content)
        assert metrics is None


# =============================================================================
# EDGE CASES
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases."""

    def test_empty_file(self):
        """Test analyzing empty file."""
        analyzer = PythonAnalyzer()
        metrics = analyzer.analyze("", "test.py")

        assert metrics is not None
        assert metrics.error_handlers == 0

    def test_comments_only(self):
        """Test file with only comments."""
        analyzer = PythonAnalyzer()
        code = '''
# This is a comment
# Another comment
"""
Docstring
"""
'''
        metrics = analyzer.analyze(code, "test.py")
        assert metrics is not None

    def test_unicode_content(self):
        """Test content with unicode characters."""
        analyzer = PythonAnalyzer()
        code = """
# 日本語コメント
def greet():
    return "こんにちは 🎉"
"""
        metrics = analyzer.analyze(code, "test.py")
        assert metrics is not None

    def test_very_long_line(self):
        """Test file with very long lines."""
        analyzer = PythonAnalyzer()
        code = "x = '" + "a" * 10000 + "'"

        metrics = analyzer.analyze(code, "test.py")
        assert metrics is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
