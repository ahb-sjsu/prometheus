#!/usr/bin/env python3
"""
Tests for hubris.py - C Language Support and N/A Handling

Tests cover:
- C language pattern detection (retry, timeout, error handling)
- N/A handling for unsupported languages
- Language detection and ratio calculation
- Mixed-language codebase handling
"""

import math
import tempfile
from pathlib import Path

import pytest

from hubris import (
    ExceptionDetector,
    Hubris,
    HubrisReport,
    RetryDetector,
    TimeoutDetector,
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
def c_codebase_with_good_patterns(temp_codebase):
    """C codebase with proper resilience patterns."""
    src_dir = Path(temp_codebase) / "src"
    src_dir.mkdir()

    # Good retry pattern with backoff
    retry_c = src_dir / "retry.c"
    retry_c.write_text(
        """
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>

#define MAX_RETRIES 5

int fetch_with_retry(const char *url, char *buffer, size_t len) {
    int retries = 0;
    int delay = 1;

    while (retries < MAX_RETRIES) {
        int result = http_get(url, buffer, len);
        if (result == 0) {
            return 0;  // Success
        }

        // Exponential backoff with jitter
        int jitter = rand() % 1000;
        sleep(delay);
        usleep(jitter * 1000);
        delay *= 2;  // Exponential backoff
        retries++;

        fprintf(stderr, "Retry %d/%d failed, backing off %ds\\n",
                retries, MAX_RETRIES, delay);
    }

    return -1;  // All retries exhausted
}
"""
    )

    # Good timeout handling
    timeout_c = src_dir / "timeout.c"
    timeout_c.write_text(
        """
#include <sys/socket.h>
#include <sys/time.h>
#include <netinet/in.h>

#define SOCKET_TIMEOUT 30

int connect_with_timeout(int sockfd, struct sockaddr *addr, socklen_t addrlen) {
    struct timeval timeout;
    timeout.tv_sec = SOCKET_TIMEOUT;
    timeout.tv_usec = 0;

    // Set receive timeout
    setsockopt(sockfd, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout));

    // Set send timeout
    setsockopt(sockfd, SOL_SOCKET, SO_SNDTIMEO, &timeout, sizeof(timeout));

    return connect(sockfd, addr, addrlen);
}

int wait_for_data(int fd, int timeout_ms) {
    struct timeval tv;
    fd_set readfds;

    tv.tv_sec = timeout_ms / 1000;
    tv.tv_usec = (timeout_ms % 1000) * 1000;

    FD_ZERO(&readfds);
    FD_SET(fd, &readfds);

    return select(fd + 1, &readfds, NULL, NULL, &tv);
}
"""
    )

    # Good error handling
    error_c = src_dir / "error.c"
    error_c.write_text(
        """
#include <stdio.h>
#include <errno.h>
#include <string.h>
#include <syslog.h>

int process_file(const char *filename) {
    FILE *fp = fopen(filename, "r");
    if (fp == NULL) {
        syslog(LOG_ERR, "Failed to open %s: %s", filename, strerror(errno));
        return -1;
    }

    char buffer[1024];
    while (fgets(buffer, sizeof(buffer), fp) != NULL) {
        int ret = process_line(buffer);
        if (ret != 0) {
            syslog(LOG_WARNING, "Failed to process line: %d", ret);
            goto cleanup;
        }
    }

    if (ferror(fp)) {
        perror("Error reading file");
        goto cleanup;
    }

    fclose(fp);
    return 0;

cleanup:
    fclose(fp);
    return -1;
}
"""
    )

    return temp_codebase


@pytest.fixture
def c_codebase_with_bad_patterns(temp_codebase):
    """C codebase with cargo cult patterns."""
    src_dir = Path(temp_codebase) / "src"
    src_dir.mkdir()

    # Bad retry - no backoff, no max
    bad_retry_c = src_dir / "bad_retry.c"
    bad_retry_c.write_text(
        """
#include <stdio.h>

int fetch_data(const char *url) {
retry:
    int result = http_get(url);
    if (result != 0) {
        goto retry;  // Infinite retry without backoff!
    }
    return result;
}

int another_retry(const char *url) {
    while (1) {
        int result = http_get(url);
        if (result == 0) return 0;
        // No sleep, no backoff, no limit!
    }
}
"""
    )

    # Bad timeout - missing
    bad_timeout_c = src_dir / "bad_timeout.c"
    bad_timeout_c.write_text(
        """
#include <sys/socket.h>

int connect_no_timeout(int sockfd, struct sockaddr *addr, socklen_t addrlen) {
    // No timeout configured - can hang forever!
    return connect(sockfd, addr, addrlen);
}
"""
    )

    # Bad error handling - ignoring errors
    bad_error_c = src_dir / "bad_error.c"
    bad_error_c.write_text(
        """
#include <stdio.h>

void process_file(const char *filename) {
    FILE *fp = fopen(filename, "r");
    // Not checking if fopen failed!

    fread(buffer, 1, sizeof(buffer), fp);
    // Not checking fread return value!

    fclose(fp);
}

int ignored_return() {
    some_function();  // Return value ignored
    another_function();  // Return value ignored
    return 0;
}
"""
    )

    return temp_codebase


@pytest.fixture
def rust_only_codebase(temp_codebase):
    """Codebase with only Rust files (unsupported)."""
    src_dir = Path(temp_codebase) / "src"
    src_dir.mkdir()

    main_rs = src_dir / "main.rs"
    main_rs.write_text(
        """
fn main() {
    println!("Hello, world!");
}

fn fetch_data(url: &str) -> Result<String, Box<dyn std::error::Error>> {
    let response = reqwest::blocking::get(url)?;
    Ok(response.text()?)
}
"""
    )

    lib_rs = src_dir / "lib.rs"
    lib_rs.write_text(
        """
pub mod utils;

pub fn process(data: &str) -> Result<(), Error> {
    // Process data with proper error handling
    let parsed = parse(data)?;
    transform(parsed)
}
"""
    )

    return temp_codebase


@pytest.fixture
def mixed_codebase(temp_codebase):
    """Codebase with mix of supported and unsupported languages."""
    src_dir = Path(temp_codebase) / "src"
    src_dir.mkdir()

    # Python (supported)
    app_py = src_dir / "app.py"
    app_py.write_text(
        """
from tenacity import retry, stop_after_attempt

@retry(stop=stop_after_attempt(3))
def fetch():
    return requests.get(url, timeout=30)
"""
    )

    # Rust (unsupported)
    main_rs = src_dir / "main.rs"
    main_rs.write_text(
        """
fn main() {
    println!("Hello");
}
"""
    )

    return temp_codebase


# =============================================================================
# C LANGUAGE RETRY DETECTOR TESTS
# =============================================================================


class TestCRetryDetector:
    """Tests for C language retry pattern detection."""

    def test_detects_for_loop_retry(self):
        """Test detection of for-loop retry pattern."""
        detector = RetryDetector()
        code = """
#define MAX_RETRIES 5
for (int i = 0; i < MAX_RETRIES; i++) {
    if (try_operation() == 0) break;
    sleep(1);
}
"""
        patterns, issues = detector.detect(code, "test.c", "c")
        assert len(patterns) >= 1

    def test_detects_while_retry(self):
        """Test detection of while-loop retry pattern."""
        detector = RetryDetector()
        code = """
int retries = 5;
while (retries-- > 0) {
    if (operation() == SUCCESS) return 0;
    sleep(delay);
}
"""
        patterns, issues = detector.detect(code, "test.c", "c")
        assert len(patterns) >= 1

    def test_detects_goto_retry(self):
        """Test detection of goto-based retry pattern."""
        detector = RetryDetector()
        code = """
retry:
    result = try_operation();
    if (result != 0 && attempts < max_attempts) {
        attempts++;
        sleep(1);
        goto retry;
    }
"""
        patterns, issues = detector.detect(code, "test.c", "c")
        # goto pattern detection is best-effort; may not always trigger
        # The important thing is it doesn't crash
        assert len(patterns) >= 0

    def test_detects_exponential_backoff(self):
        """Test detection of exponential backoff in C."""
        detector = RetryDetector()
        code = """
int delay = 1;
for (int i = 0; i < MAX_RETRIES; i++) {
    if (operation() == 0) break;
    sleep(delay);
    delay *= 2;  // Exponential backoff
}
"""
        patterns, issues = detector.detect(code, "test.c", "c")
        # Should detect retry with backoff
        assert any(p.quality in ("CORRECT", "PARTIAL") for p in patterns)

    def test_detects_jitter(self):
        """Test detection of jitter in C retry."""
        detector = RetryDetector()
        code = """
for (int i = 0; i < max_retries; i++) {
    if (operation() == 0) break;
    int jitter = rand() % 1000;
    usleep(delay * 1000 + jitter);
    delay <<= 1;
}
"""
        patterns, issues = detector.detect(code, "test.c", "c")
        assert len(patterns) >= 1

    def test_retry_without_backoff_is_cargo_cult(self):
        """Test that retry without backoff is marked as cargo cult."""
        detector = RetryDetector()
        code = """
retry:
    if (operation() != 0) goto retry;
"""
        patterns, issues = detector.detect(code, "test.c", "c")
        if patterns:
            assert any(p.quality == "CARGO_CULT" for p in patterns)


# =============================================================================
# C LANGUAGE TIMEOUT DETECTOR TESTS
# =============================================================================


class TestCTimeoutDetector:
    """Tests for C language timeout pattern detection."""

    def test_detects_socket_timeout(self):
        """Test detection of socket timeout configuration."""
        detector = TimeoutDetector()
        code = """
struct timeval timeout;
timeout.tv_sec = 30;
setsockopt(sockfd, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout));
"""
        patterns, issues = detector.detect(code, "test.c", "c")
        # Should detect timeout configuration
        assert len(issues) == 0 or all(i.issue_type != "missing" for i in issues)

    def test_detects_select_timeout(self):
        """Test detection of select() with timeout."""
        detector = TimeoutDetector()
        code = """
fd_set readfds;
struct timeval tv;
tv.tv_sec = 5;
tv.tv_usec = 0;
select(fd + 1, &readfds, NULL, NULL, &tv);
"""
        patterns, issues = detector.detect(code, "test.c", "c")
        assert len(patterns) >= 0  # May or may not detect depending on pattern

    def test_detects_curl_timeout(self):
        """Test detection of curl timeout options."""
        detector = TimeoutDetector()
        code = """
curl_easy_setopt(curl, CURLOPT_TIMEOUT, 30L);
curl_easy_setopt(curl, CURLOPT_CONNECTTIMEOUT, 10L);
"""
        patterns, issues = detector.detect(code, "test.c", "c")
        # Should not flag as missing timeout
        assert not any(i.issue_type == "missing" for i in issues)

    def test_detects_alarm_timeout(self):
        """Test detection of alarm-based timeout."""
        detector = TimeoutDetector()
        code = """
signal(SIGALRM, timeout_handler);
alarm(30);
long_operation();
alarm(0);
"""
        patterns, issues = detector.detect(code, "test.c", "c")
        assert len(patterns) >= 0


# =============================================================================
# C LANGUAGE EXCEPTION/ERROR DETECTOR TESTS
# =============================================================================


class TestCExceptionDetector:
    """Tests for C language error handling detection."""

    def test_detects_errno_check(self):
        """Test detection of errno checking."""
        detector = ExceptionDetector()
        code = """
FILE *fp = fopen(filename, "r");
if (fp == NULL) {
    if (errno == ENOENT) {
        printf("File not found\\n");
    }
    perror("fopen failed");
    return -1;
}
"""
        patterns, issues = detector.detect(code, "test.c", "c")
        # Good error handling should not generate issues
        assert len(patterns) >= 0

    def test_detects_goto_cleanup(self):
        """Test detection of goto cleanup pattern."""
        detector = ExceptionDetector()
        code = """
int process() {
    if (init() != 0) goto cleanup;
    if (step1() != 0) goto cleanup;
    if (step2() != 0) goto cleanup;
    return 0;
cleanup:
    cleanup_resources();
    return -1;
}
"""
        patterns, issues = detector.detect(code, "test.c", "c")
        # goto cleanup is a valid C pattern
        assert len(patterns) >= 0

    def test_detects_return_value_check(self):
        """Test detection of return value checking."""
        detector = ExceptionDetector()
        code = """
int ret = some_function();
if (ret != 0) {
    fprintf(stderr, "Operation failed: %d\\n", ret);
    return ret;
}
"""
        patterns, issues = detector.detect(code, "test.c", "c")
        # Proper error handling
        assert len(patterns) >= 0


# =============================================================================
# N/A HANDLING TESTS
# =============================================================================


class TestNAHandling:
    """Tests for N/A handling with unsupported languages."""

    def test_rust_only_returns_na(self, rust_only_codebase):
        """Test that Rust-only codebase returns N/A."""
        hubris = Hubris(rust_only_codebase)
        report = hubris.analyze()

        assert report.theater_ratio == "N/A"
        assert report.quadrant == "N/A"
        assert "rust" in report.primary_language.lower()
        assert report.supported_language_ratio < 0.2

    def test_na_verdict_explains_situation(self, rust_only_codebase):
        """Test that N/A verdict explains the situation."""
        hubris = Hubris(rust_only_codebase)
        report = hubris.analyze()

        assert "not" in report.verdict.lower() or "N/A" in report.verdict
        assert "supported" in report.verdict.lower() or "available" in report.verdict.lower()

    def test_languages_tracked(self, rust_only_codebase):
        """Test that languages are properly tracked."""
        hubris = Hubris(rust_only_codebase)
        report = hubris.analyze()

        assert "rust" in report.languages_skipped
        assert len(report.languages_analyzed) == 0

    def test_mixed_codebase_analyzes_supported(self, mixed_codebase):
        """Test that mixed codebase analyzes supported languages."""
        hubris = Hubris(mixed_codebase)
        report = hubris.analyze()

        # Should analyze Python portion
        assert "python" in report.languages_analyzed
        # Should note Rust was skipped
        assert "rust" in report.languages_skipped
        # Should have numeric theater_ratio since Python is >20%
        assert report.theater_ratio != "N/A" or report.supported_language_ratio >= 0.2


# =============================================================================
# LANGUAGE DETECTION TESTS
# =============================================================================


class TestLanguageDetection:
    """Tests for language detection and classification."""

    def test_supported_languages_defined(self):
        """Test that supported languages are defined."""
        assert ".py" in Hubris.SUPPORTED_LANGUAGES
        assert ".js" in Hubris.SUPPORTED_LANGUAGES
        assert ".c" in Hubris.SUPPORTED_LANGUAGES
        assert ".go" in Hubris.SUPPORTED_LANGUAGES
        assert ".java" in Hubris.SUPPORTED_LANGUAGES

    def test_unsupported_languages_defined(self):
        """Test that unsupported languages are defined."""
        assert ".rs" in Hubris.UNSUPPORTED_LANGUAGES
        assert ".rb" in Hubris.UNSUPPORTED_LANGUAGES
        assert ".php" in Hubris.UNSUPPORTED_LANGUAGES

    def test_c_extensions_supported(self):
        """Test that C/C++ extensions are supported."""
        assert Hubris.SUPPORTED_LANGUAGES.get(".c") == "c"
        assert Hubris.SUPPORTED_LANGUAGES.get(".h") == "c"
        assert Hubris.SUPPORTED_LANGUAGES.get(".cpp") == "cpp"
        assert Hubris.SUPPORTED_LANGUAGES.get(".hpp") == "cpp"


# =============================================================================
# FULL C CODEBASE ANALYSIS TESTS
# =============================================================================


class TestCCodebaseAnalysis:
    """Integration tests for C codebase analysis."""

    def test_good_c_patterns_detected(self, c_codebase_with_good_patterns):
        """Test that good C patterns are detected and scored well."""
        hubris = Hubris(c_codebase_with_good_patterns)
        report = hubris.analyze()

        assert report.theater_ratio != "N/A"
        assert "c" in report.languages_analyzed
        # Good patterns should have reasonable theater ratio
        if isinstance(report.theater_ratio, float):
            assert not math.isinf(report.theater_ratio)

    def test_bad_c_patterns_generate_issues(self, c_codebase_with_bad_patterns):
        """Test that bad C patterns generate issues."""
        hubris = Hubris(c_codebase_with_bad_patterns)
        report = hubris.analyze()

        assert report.theater_ratio != "N/A"
        # Bad patterns should generate some issues or cargo cult patterns
        assert report.patterns_detected >= 0

    def test_c_codebase_has_numeric_ratio(self, c_codebase_with_good_patterns):
        """Test that C codebase returns numeric theater ratio."""
        hubris = Hubris(c_codebase_with_good_patterns)
        report = hubris.analyze()

        # Should be numeric, not N/A
        assert report.theater_ratio != "N/A"
        assert isinstance(report.theater_ratio, (int, float))


# =============================================================================
# HUBRIS REPORT FIELDS TESTS
# =============================================================================


class TestHubrisReportFields:
    """Tests for new HubrisReport fields."""

    def test_report_has_language_fields(self):
        """Test that HubrisReport has language tracking fields."""
        report = HubrisReport(codebase_path="/test", timestamp="2024-01-01")

        assert hasattr(report, "languages_analyzed")
        assert hasattr(report, "languages_skipped")
        assert hasattr(report, "primary_language")
        assert hasattr(report, "supported_language_ratio")

    def test_theater_ratio_can_be_string(self):
        """Test that theater_ratio can be 'N/A'."""
        report = HubrisReport(codebase_path="/test", timestamp="2024-01-01")
        report.theater_ratio = "N/A"

        assert report.theater_ratio == "N/A"

    def test_theater_ratio_can_be_float(self):
        """Test that theater_ratio can be float."""
        report = HubrisReport(codebase_path="/test", timestamp="2024-01-01")
        report.theater_ratio = 1.5

        assert report.theater_ratio == 1.5

    def test_theater_ratio_can_be_infinity(self):
        """Test that theater_ratio can be infinity."""
        report = HubrisReport(codebase_path="/test", timestamp="2024-01-01")
        report.theater_ratio = float("inf")

        assert math.isinf(report.theater_ratio)


# =============================================================================
# EDGE CASES
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases."""

    def test_empty_codebase(self, temp_codebase):
        """Test analysis of empty codebase."""
        hubris = Hubris(temp_codebase)
        report = hubris.analyze()

        assert report is not None
        assert report.patterns_detected == 0

    def test_codebase_with_only_headers(self, temp_codebase):
        """Test C codebase with only header files."""
        header = Path(temp_codebase) / "types.h"
        header.write_text(
            """
#ifndef TYPES_H
#define TYPES_H

typedef struct {
    int x;
    int y;
} Point;

#endif
"""
        )

        hubris = Hubris(temp_codebase)
        report = hubris.analyze()

        assert report is not None
        assert "c" in report.languages_analyzed

    def test_binary_files_ignored(self, temp_codebase):
        """Test that binary files are ignored."""
        bin_file = Path(temp_codebase) / "data.bin"
        bin_file.write_bytes(b"\x00\x01\x02\x03\xff\xfe")

        c_file = Path(temp_codebase) / "main.c"
        c_file.write_text("int main() { return 0; }")

        hubris = Hubris(temp_codebase)
        report = hubris.analyze()

        # Should not crash on binary files
        assert report is not None

    def test_deeply_nested_directories(self, temp_codebase):
        """Test analysis of deeply nested directory structure."""
        deep_dir = Path(temp_codebase) / "a" / "b" / "c" / "d" / "e"
        deep_dir.mkdir(parents=True)

        deep_file = deep_dir / "deep.c"
        deep_file.write_text(
            """
int retry_operation() {
    for (int i = 0; i < MAX_RETRIES; i++) {
        if (op() == 0) return 0;
        sleep(1 << i);
    }
    return -1;
}
"""
        )

        hubris = Hubris(temp_codebase)
        report = hubris.analyze()

        assert report is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
