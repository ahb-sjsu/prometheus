#!/usr/bin/env python3
"""
Language Analyzers - Modular resilience pattern detection per language
======================================================================

Each language has its own idioms for resilience:
- Python: try/except, decorators, context managers
- JavaScript/TypeScript: try/catch, Promises, async/await
- Java: try/catch/finally, annotations, checked exceptions
- Go: if err != nil, defer, panic/recover
- C/C++: if (ret < 0), goto cleanup, errno, RAII
- Rust: Result<T,E>, ?, panic!, unwrap_or
- Bash/Shell: set -e, trap, || exit 1
- SQL: transactions, savepoints, exception blocks
- HTML/CSS: N/A (markup, not code)

This module provides a base class and language-specific analyzers
that can be extended for new languages.
"""

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

# =============================================================================
# BASE METRICS (language-agnostic)
# =============================================================================


@dataclass
class LanguageResilienceMetrics:
    """Base metrics that all language analyzers populate."""

    # Error handling (universal concept, different syntax)
    error_checks: int = 0  # Any form of error checking
    error_handlers: int = 0  # Blocks that handle errors
    error_propagation: int = 0  # Explicit error returns/throws
    cleanup_blocks: int = 0  # finally/defer/RAII
    bare_handlers: int = 0  # Catch-all without specificity

    # Resource management
    resource_acquisition: int = 0  # Opens, connects, allocates
    resource_release: int = 0  # Closes, disconnects, frees
    resource_guards: int = 0  # RAII, context managers, using

    # Logging/observability
    log_statements: int = 0
    error_logging: int = 0
    debug_logging: int = 0

    # Defensive patterns
    null_checks: int = 0
    bounds_checks: int = 0
    input_validation: int = 0
    assertions: int = 0

    # Timeout/retry (if applicable)
    timeout_configs: int = 0
    retry_patterns: int = 0

    # Language-specific extras stored here
    extras: dict = field(default_factory=dict)


# =============================================================================
# BASE ANALYZER
# =============================================================================


class LanguageAnalyzer(ABC):
    """Base class for language-specific resilience analyzers."""

    # Override in subclass
    LANGUAGE_NAME: str = "unknown"
    FILE_EXTENSIONS: list = []

    @abstractmethod
    def analyze(self, content: str, filepath: str = "") -> LanguageResilienceMetrics:
        """Analyze source code and return resilience metrics."""
        pass

    def _count_pattern(self, content: str, pattern: re.Pattern) -> int:
        """Helper to count regex matches."""
        return len(pattern.findall(content))


# =============================================================================
# PYTHON ANALYZER
# =============================================================================


class PythonAnalyzer(LanguageAnalyzer):
    """Python resilience pattern detector."""

    LANGUAGE_NAME = "python"
    FILE_EXTENSIONS = [".py"]

    PATTERNS = {
        "try_block": re.compile(r"\btry\s*:"),
        "except_block": re.compile(r"\bexcept\s*(\w+)?.*:"),
        "bare_except": re.compile(r"\bexcept\s*:"),
        "finally_block": re.compile(r"\bfinally\s*:"),
        "raise": re.compile(r"\braise\b"),
        "with_statement": re.compile(r"\bwith\b.*:"),
        "assert": re.compile(r"\bassert\b"),
        # Logging
        "log_call": re.compile(r"\b(log|logger|logging)\.\w+\("),
        "log_error": re.compile(r"\b(log|logger|logging)\.(error|exception|critical)\("),
        "log_debug": re.compile(r"\b(log|logger|logging)\.(debug|info)\("),
        "print_call": re.compile(r"\bprint\s*\("),
        # Null checks
        "none_check": re.compile(r"\bif\s+\w+\s+(is\s+None|is\s+not\s+None|==\s*None|!=\s*None)"),
        "or_default": re.compile(r'\bor\s+[\'"{\[\w]'),
        # Type hints (defensive)
        "type_hint": re.compile(r"->\s*\w+|:\s*\w+\s*="),
        # Retry/timeout libraries
        "tenacity": re.compile(r"@retry|from tenacity|import tenacity"),
        "timeout": re.compile(r"timeout\s*=\s*\d+"),
    }

    def analyze(self, content: str, filepath: str = "") -> LanguageResilienceMetrics:
        metrics = LanguageResilienceMetrics()

        # Try/except handling
        metrics.error_handlers = self._count_pattern(content, self.PATTERNS["try_block"])
        metrics.bare_handlers = self._count_pattern(content, self.PATTERNS["bare_except"])
        metrics.error_propagation = self._count_pattern(content, self.PATTERNS["raise"])
        metrics.cleanup_blocks = self._count_pattern(content, self.PATTERNS["finally_block"])

        # Resource management
        metrics.resource_guards = self._count_pattern(content, self.PATTERNS["with_statement"])

        # Logging
        metrics.log_statements = self._count_pattern(content, self.PATTERNS["log_call"])
        metrics.log_statements += self._count_pattern(content, self.PATTERNS["print_call"])
        metrics.error_logging = self._count_pattern(content, self.PATTERNS["log_error"])
        metrics.debug_logging = self._count_pattern(content, self.PATTERNS["log_debug"])

        # Defensive patterns
        metrics.null_checks = self._count_pattern(content, self.PATTERNS["none_check"])
        metrics.null_checks += self._count_pattern(content, self.PATTERNS["or_default"])
        metrics.assertions = self._count_pattern(content, self.PATTERNS["assert"])

        # Timeout/retry
        metrics.retry_patterns = self._count_pattern(content, self.PATTERNS["tenacity"])
        metrics.timeout_configs = self._count_pattern(content, self.PATTERNS["timeout"])

        # Calculate error checks (try blocks + asserts)
        metrics.error_checks = metrics.error_handlers + metrics.assertions

        return metrics


# =============================================================================
# C/C++ ANALYZER
# =============================================================================


class CAnalyzer(LanguageAnalyzer):
    """C and C++ resilience pattern detector."""

    LANGUAGE_NAME = "c"
    FILE_EXTENSIONS = [".c", ".h", ".cpp", ".hpp", ".cc", ".cxx"]

    PATTERNS = {
        # Error checking (C style)
        "return_check": re.compile(r"if\s*\([^)]*[<>=!]=?\s*(-1|NULL|0|nullptr)\s*\)"),
        "errno_check": re.compile(r"\berrno\b"),
        "goto_error": re.compile(
            r"\bgoto\s+(err|error|fail|cleanup|out|done|bail)\w*\s*;", re.IGNORECASE
        ),
        "error_label": re.compile(
            r"^(err|error|fail|cleanup|out|done|bail)\w*\s*:",
            re.MULTILINE | re.IGNORECASE,
        ),
        # Error reporting (Git/Linux style)
        "die_call": re.compile(r"\b(die|die_errno|fatal|panic|usage|usage_with_options)\s*\("),
        "error_call": re.compile(r"\b(error|err|warn|warning|perror)\s*\("),
        "bug_on": re.compile(r"\b(BUG_ON|BUG|WARN_ON|WARN)\s*\("),
        # Logging
        "printf_error": re.compile(r"\bfprintf\s*\(\s*stderr"),
        "syslog": re.compile(r"\bsyslog\s*\("),
        "log_call": re.compile(r"\b(LOG_|log_|pr_err|pr_warn|pr_info|pr_debug)\w*\s*\("),
        # Resource management
        "malloc": re.compile(r"\b(malloc|calloc|realloc|alloc|xmalloc|xcalloc)\s*\("),
        "free": re.compile(r"\bfree\s*\("),
        "open_call": re.compile(r"\b(open|fopen|socket|connect)\s*\("),
        "close_call": re.compile(r"\b(close|fclose|shutdown)\s*\("),
        # Null checks
        "null_check": re.compile(r"if\s*\(\s*!?\s*\w+\s*\)"),  # if (!ptr) or if (ptr)
        "null_explicit": re.compile(r"if\s*\([^)]*\s*(==|!=)\s*(NULL|nullptr)\s*\)"),
        # Defensive patterns
        "assert": re.compile(
            r"\b(assert|ASSERT|g_assert|g_return_if_fail|g_return_val_if_fail)\s*\("
        ),
        "static_assert": re.compile(r"\b(static_assert|_Static_assert|STATIC_ASSERT)\s*\("),
        # RAII (C++ only)
        "unique_ptr": re.compile(r"\b(unique_ptr|shared_ptr|scoped_ptr|auto_ptr)\s*<"),
        "raii_guard": re.compile(r"\b(lock_guard|scoped_lock|unique_lock)\s*<"),
        # Try/catch (C++)
        "try_block": re.compile(r"\btry\s*\{"),
        "catch_block": re.compile(r"\bcatch\s*\("),
        # Signal handling
        "signal_handler": re.compile(r"\bsignal\s*\(|sigaction\s*\("),
        # Bounds checking
        "sizeof_check": re.compile(r"\bsizeof\s*\("),
        "strlen_check": re.compile(r"\b(strlen|strnlen|wcslen)\s*\("),
        "strncpy": re.compile(r"\b(strncpy|strncat|snprintf)\s*\("),  # Safe versions
    }

    def analyze(self, content: str, filepath: str = "") -> LanguageResilienceMetrics:
        metrics = LanguageResilienceMetrics()

        # Error checking (C style)
        metrics.error_checks = self._count_pattern(content, self.PATTERNS["return_check"])
        metrics.error_checks += self._count_pattern(content, self.PATTERNS["errno_check"])

        # Goto-based error handling (common in kernel/git)
        goto_errors = self._count_pattern(content, self.PATTERNS["goto_error"])
        error_labels = self._count_pattern(content, self.PATTERNS["error_label"])
        metrics.error_handlers = goto_errors + error_labels
        metrics.extras["goto_cleanup"] = goto_errors

        # Error reporting functions - in C these ARE error handling
        die_calls = self._count_pattern(content, self.PATTERNS["die_call"])
        error_calls = self._count_pattern(content, self.PATTERNS["error_call"])
        bug_calls = self._count_pattern(content, self.PATTERNS["bug_on"])

        metrics.error_logging = die_calls + error_calls + bug_calls

        # die() and BUG() are terminal error handlers in C - count them as handlers too
        metrics.error_handlers += die_calls + bug_calls
        metrics.extras["die_calls"] = die_calls

        # Logging
        metrics.log_statements = self._count_pattern(content, self.PATTERNS["printf_error"])
        metrics.log_statements += self._count_pattern(content, self.PATTERNS["syslog"])
        metrics.log_statements += self._count_pattern(content, self.PATTERNS["log_call"])
        metrics.log_statements += metrics.error_logging

        # Resource management
        metrics.resource_acquisition = self._count_pattern(content, self.PATTERNS["malloc"])
        metrics.resource_acquisition += self._count_pattern(content, self.PATTERNS["open_call"])
        metrics.resource_release = self._count_pattern(content, self.PATTERNS["free"])
        metrics.resource_release += self._count_pattern(content, self.PATTERNS["close_call"])

        # C++ RAII
        metrics.resource_guards = self._count_pattern(content, self.PATTERNS["unique_ptr"])
        metrics.resource_guards += self._count_pattern(content, self.PATTERNS["raii_guard"])

        # C++ exceptions
        try_blocks = self._count_pattern(content, self.PATTERNS["try_block"])
        metrics.error_handlers += try_blocks
        metrics.extras["cpp_try_catch"] = try_blocks

        # Null checks
        metrics.null_checks = self._count_pattern(content, self.PATTERNS["null_check"])
        metrics.null_checks += self._count_pattern(content, self.PATTERNS["null_explicit"])

        # Assertions
        metrics.assertions = self._count_pattern(content, self.PATTERNS["assert"])
        metrics.assertions += self._count_pattern(content, self.PATTERNS["static_assert"])

        # Bounds checking
        metrics.bounds_checks = self._count_pattern(content, self.PATTERNS["sizeof_check"])
        metrics.bounds_checks += self._count_pattern(content, self.PATTERNS["strncpy"])

        # Error propagation (return -1, return NULL patterns)
        metrics.error_propagation = self._count_pattern(content, self.PATTERNS["return_check"])

        # Cleanup blocks (error labels serve this purpose in C)
        metrics.cleanup_blocks = error_labels

        return metrics


# =============================================================================
# GO ANALYZER
# =============================================================================


class GoAnalyzer(LanguageAnalyzer):
    """Go resilience pattern detector."""

    LANGUAGE_NAME = "go"
    FILE_EXTENSIONS = [".go"]

    PATTERNS = {
        # Error handling (Go's bread and butter)
        "err_check": re.compile(r"if\s+err\s*!=\s*nil"),
        "err_return": re.compile(r"return\s+.*,?\s*err\b"),
        "err_wrap": re.compile(r"(fmt\.Errorf|errors\.Wrap|errors\.New|pkg/errors)"),
        # Panic/recover
        "panic": re.compile(r"\bpanic\s*\("),
        "recover": re.compile(r"\brecover\s*\("),
        "defer": re.compile(r"\bdefer\s+"),
        # Logging
        "log_call": re.compile(r"\b(log\.|logger\.|zap\.|logrus\.|zerolog\.)\w+"),
        "log_error": re.compile(r"\.(Error|Fatal|Panic)\w*\("),
        "log_debug": re.compile(r"\.(Debug|Info|Warn)\w*\("),
        # Context (timeout/cancellation)
        "context": re.compile(r"\bcontext\.(WithTimeout|WithDeadline|WithCancel)"),
        "ctx_param": re.compile(r"ctx\s+context\.Context"),
        # Resource management
        "close_call": re.compile(r"\.Close\s*\("),
        "defer_close": re.compile(r"defer\s+\w+\.Close\s*\("),
        # Null checks (nil in Go)
        "nil_check": re.compile(r"if\s+\w+\s*[!=]=\s*nil"),
        # Retry libraries
        "retry_lib": re.compile(r"(retry|backoff|circuit)"),
        # Assertions/testing
        "require": re.compile(r"\brequire\.\w+"),
        "assert": re.compile(r"\bassert\.\w+"),
    }

    def analyze(self, content: str, filepath: str = "") -> LanguageResilienceMetrics:
        metrics = LanguageResilienceMetrics()

        # Error handling (Go's primary pattern)
        metrics.error_checks = self._count_pattern(content, self.PATTERNS["err_check"])
        metrics.error_propagation = self._count_pattern(content, self.PATTERNS["err_return"])
        metrics.error_propagation += self._count_pattern(content, self.PATTERNS["err_wrap"])

        # Panic/recover
        panic_count = self._count_pattern(content, self.PATTERNS["panic"])
        recover_count = self._count_pattern(content, self.PATTERNS["recover"])
        metrics.extras["panic"] = panic_count
        metrics.extras["recover"] = recover_count
        metrics.error_handlers = recover_count

        # Defer (cleanup)
        metrics.cleanup_blocks = self._count_pattern(content, self.PATTERNS["defer"])

        # Logging
        metrics.log_statements = self._count_pattern(content, self.PATTERNS["log_call"])
        metrics.error_logging = self._count_pattern(content, self.PATTERNS["log_error"])
        metrics.debug_logging = self._count_pattern(content, self.PATTERNS["log_debug"])

        # Context (timeout/cancellation)
        context_usage = self._count_pattern(content, self.PATTERNS["context"])
        context_params = self._count_pattern(content, self.PATTERNS["ctx_param"])
        metrics.timeout_configs = context_usage
        metrics.extras["context_aware"] = context_params

        # Resource management
        metrics.resource_release = self._count_pattern(content, self.PATTERNS["close_call"])
        metrics.resource_guards = self._count_pattern(content, self.PATTERNS["defer_close"])

        # Nil checks
        metrics.null_checks = self._count_pattern(content, self.PATTERNS["nil_check"])

        # Assertions
        metrics.assertions = self._count_pattern(content, self.PATTERNS["require"])
        metrics.assertions += self._count_pattern(content, self.PATTERNS["assert"])

        return metrics


# =============================================================================
# RUST ANALYZER
# =============================================================================


class RustAnalyzer(LanguageAnalyzer):
    """Rust resilience pattern detector."""

    LANGUAGE_NAME = "rust"
    FILE_EXTENSIONS = [".rs"]

    PATTERNS = {
        # Error handling (Result/Option)
        "result_type": re.compile(r"Result\s*<"),
        "option_type": re.compile(r"Option\s*<"),
        "question_mark": re.compile(r"\?\s*;"),  # The ? operator
        "match_result": re.compile(r"match\s+\w+\s*\{[^}]*(Ok|Err|Some|None)"),
        "unwrap": re.compile(r"\.(unwrap|expect)\s*\("),
        "unwrap_or": re.compile(r"\.(unwrap_or|unwrap_or_else|unwrap_or_default)\s*\("),
        "ok_or": re.compile(r"\.(ok_or|ok_or_else)\s*\("),
        # Panic
        "panic": re.compile(r"\b(panic!|unreachable!|unimplemented!|todo!)"),
        # Logging
        "log_macro": re.compile(r"\b(log::|tracing::|error!|warn!|info!|debug!|trace!)"),
        "println": re.compile(r"\b(println!|eprintln!)"),
        # Resource management (RAII is automatic, but Drop is explicit)
        "drop": re.compile(r"\bdrop\s*\(|impl\s+Drop"),
        # Assertions
        "assert": re.compile(r"\b(assert!|assert_eq!|assert_ne!|debug_assert!)"),
        # Unsafe (inverse resilience)
        "unsafe": re.compile(r"\bunsafe\s*\{"),
    }

    def analyze(self, content: str, filepath: str = "") -> LanguageResilienceMetrics:
        metrics = LanguageResilienceMetrics()

        # Error handling (Rust's type system)
        metrics.error_checks = self._count_pattern(content, self.PATTERNS["result_type"])
        metrics.error_checks += self._count_pattern(content, self.PATTERNS["option_type"])

        # ? operator (error propagation)
        metrics.error_propagation = self._count_pattern(content, self.PATTERNS["question_mark"])

        # Safe unwrapping
        safe_unwrap = self._count_pattern(content, self.PATTERNS["unwrap_or"])
        safe_unwrap += self._count_pattern(content, self.PATTERNS["ok_or"])

        # Unsafe unwrap (potential panic)
        unsafe_unwrap = self._count_pattern(content, self.PATTERNS["unwrap"])
        metrics.extras["unsafe_unwrap"] = unsafe_unwrap
        metrics.extras["safe_unwrap"] = safe_unwrap

        # Error handlers (match on Result/Option)
        metrics.error_handlers = self._count_pattern(content, self.PATTERNS["match_result"])

        # Panic (bad in production code)
        panic_count = self._count_pattern(content, self.PATTERNS["panic"])
        metrics.extras["panic"] = panic_count
        metrics.bare_handlers = panic_count  # Treat panic as "bare" handling

        # Logging
        metrics.log_statements = self._count_pattern(content, self.PATTERNS["log_macro"])
        metrics.log_statements += self._count_pattern(content, self.PATTERNS["println"])

        # Resource management (RAII is default, Drop is explicit)
        metrics.resource_guards = self._count_pattern(content, self.PATTERNS["drop"])
        # In Rust, RAII is implicit, so we give base credit
        metrics.cleanup_blocks = (
            1
            if "drop" not in content.lower()
            else self._count_pattern(content, self.PATTERNS["drop"])
        )

        # Assertions
        metrics.assertions = self._count_pattern(content, self.PATTERNS["assert"])

        # Unsafe blocks (negative indicator)
        unsafe_count = self._count_pattern(content, self.PATTERNS["unsafe"])
        metrics.extras["unsafe_blocks"] = unsafe_count

        # Null checks (Option handling counts)
        metrics.null_checks = self._count_pattern(content, self.PATTERNS["option_type"])

        return metrics


# =============================================================================
# JAVA ANALYZER
# =============================================================================


class JavaAnalyzer(LanguageAnalyzer):
    """Java resilience pattern detector."""

    LANGUAGE_NAME = "java"
    FILE_EXTENSIONS = [".java"]

    PATTERNS = {
        # Exception handling
        "try_block": re.compile(r"\btry\s*\{"),
        "catch_block": re.compile(r"\bcatch\s*\([^)]+\)"),
        "catch_generic": re.compile(r"\bcatch\s*\(\s*(Exception|Throwable)\s+"),
        "finally_block": re.compile(r"\bfinally\s*\{"),
        "throw": re.compile(r"\bthrow\s+"),
        "throws": re.compile(r"\bthrows\s+\w+"),
        # Try-with-resources
        "try_with": re.compile(r"\btry\s*\([^)]+\)\s*\{"),
        # Logging
        "logger": re.compile(r"\b(LOG|LOGGER|log|logger)\.\w+\("),
        "log_error": re.compile(r"\.(error|severe|fatal)\s*\("),
        "log_debug": re.compile(r"\.(debug|info|fine|trace)\s*\("),
        "sysout": re.compile(r"System\.(out|err)\.print"),
        # Null checks
        "null_check": re.compile(r"if\s*\([^)]*\s*[!=]=\s*null"),
        "optional": re.compile(r"Optional\s*<"),
        "objects_null": re.compile(r"Objects\.(requireNonNull|isNull|nonNull)"),
        # Annotations
        "nullable": re.compile(r"@(Nullable|NonNull|NotNull|Nonnull)"),
        # Resilience libraries
        "hystrix": re.compile(r"@HystrixCommand|HystrixCommand"),
        "resilience4j": re.compile(r"@(CircuitBreaker|Retry|RateLimiter|Bulkhead)"),
        "retry": re.compile(r"@Retryable|RetryTemplate"),
        # Timeout
        "timeout": re.compile(r"timeout\s*=|@Timeout|\.timeout\s*\("),
        # Assertions
        "assert": re.compile(r"\bassert\s+"),
        # Resource management
        "closeable": re.compile(r"implements\s+.*Closeable|AutoCloseable"),
        "close": re.compile(r"\.close\s*\("),
    }

    def analyze(self, content: str, filepath: str = "") -> LanguageResilienceMetrics:
        metrics = LanguageResilienceMetrics()

        # Exception handling
        metrics.error_handlers = self._count_pattern(content, self.PATTERNS["try_block"])
        metrics.bare_handlers = self._count_pattern(content, self.PATTERNS["catch_generic"])
        metrics.cleanup_blocks = self._count_pattern(content, self.PATTERNS["finally_block"])
        metrics.error_propagation = self._count_pattern(content, self.PATTERNS["throw"])
        metrics.error_propagation += self._count_pattern(content, self.PATTERNS["throws"])

        # Try-with-resources (good pattern)
        try_with = self._count_pattern(content, self.PATTERNS["try_with"])
        metrics.resource_guards = try_with
        metrics.extras["try_with_resources"] = try_with

        # Logging
        metrics.log_statements = self._count_pattern(content, self.PATTERNS["logger"])
        metrics.log_statements += self._count_pattern(content, self.PATTERNS["sysout"])
        metrics.error_logging = self._count_pattern(content, self.PATTERNS["log_error"])
        metrics.debug_logging = self._count_pattern(content, self.PATTERNS["log_debug"])

        # Null checks
        metrics.null_checks = self._count_pattern(content, self.PATTERNS["null_check"])
        metrics.null_checks += self._count_pattern(content, self.PATTERNS["optional"])
        metrics.null_checks += self._count_pattern(content, self.PATTERNS["objects_null"])

        # Resilience libraries
        hystrix = self._count_pattern(content, self.PATTERNS["hystrix"])
        resilience4j = self._count_pattern(content, self.PATTERNS["resilience4j"])
        retry = self._count_pattern(content, self.PATTERNS["retry"])
        metrics.retry_patterns = hystrix + resilience4j + retry
        metrics.extras["resilience_annotations"] = hystrix + resilience4j

        # Timeout
        metrics.timeout_configs = self._count_pattern(content, self.PATTERNS["timeout"])

        # Assertions
        metrics.assertions = self._count_pattern(content, self.PATTERNS["assert"])

        # Resource management
        metrics.resource_release = self._count_pattern(content, self.PATTERNS["close"])

        # Calculate error checks
        metrics.error_checks = metrics.error_handlers + metrics.assertions

        return metrics


# =============================================================================
# JAVASCRIPT/TYPESCRIPT ANALYZER
# =============================================================================


class JavaScriptAnalyzer(LanguageAnalyzer):
    """JavaScript and TypeScript resilience pattern detector."""

    LANGUAGE_NAME = "javascript"
    FILE_EXTENSIONS = [".js", ".jsx", ".ts", ".tsx", ".mjs"]

    PATTERNS = {
        # Exception handling
        "try_block": re.compile(r"\btry\s*\{"),
        "catch_block": re.compile(r"\bcatch\s*\([^)]*\)\s*\{"),
        "finally_block": re.compile(r"\bfinally\s*\{"),
        "throw": re.compile(r"\bthrow\s+"),
        # Promise handling
        "promise_catch": re.compile(r"\.catch\s*\("),
        "promise_finally": re.compile(r"\.finally\s*\("),
        "async_await": re.compile(r"\basync\s+"),
        # Logging
        "console_log": re.compile(r"console\.(log|info|debug|warn|error|trace)\s*\("),
        "console_error": re.compile(r"console\.(error|warn)\s*\("),
        "logger": re.compile(r"(logger|log)\.(info|debug|warn|error)\s*\("),
        # Null checks
        "null_check": re.compile(r"[!=]==?\s*(null|undefined)"),
        "optional_chain": re.compile(r"\?\.\w+"),
        "nullish_coalesce": re.compile(r"\?\?"),
        "or_default": re.compile(r'\|\|\s*[\'"{\[\w]'),
        # Type guards (TypeScript)
        "type_guard": re.compile(r"typeof\s+\w+\s*[!=]=="),
        "instanceof": re.compile(r"instanceof\s+\w+"),
        # Retry/timeout libraries
        "retry_lib": re.compile(r"(async-retry|p-retry|retry|axios-retry)"),
        "timeout": re.compile(r"timeout\s*[:=]\s*\d+|setTimeout"),
        # Assertions (testing)
        "assert": re.compile(r"\b(assert|expect|should)\s*[\.(]"),
    }

    def analyze(self, content: str, filepath: str = "") -> LanguageResilienceMetrics:
        metrics = LanguageResilienceMetrics()

        # Exception handling
        metrics.error_handlers = self._count_pattern(content, self.PATTERNS["try_block"])
        metrics.cleanup_blocks = self._count_pattern(content, self.PATTERNS["finally_block"])
        metrics.error_propagation = self._count_pattern(content, self.PATTERNS["throw"])

        # Promise handling
        promise_catch = self._count_pattern(content, self.PATTERNS["promise_catch"])
        promise_finally = self._count_pattern(content, self.PATTERNS["promise_finally"])
        metrics.error_handlers += promise_catch
        metrics.cleanup_blocks += promise_finally
        metrics.extras["promise_catch"] = promise_catch

        # Async/await (modern pattern)
        async_usage = self._count_pattern(content, self.PATTERNS["async_await"])
        metrics.extras["async_await"] = async_usage

        # Logging
        metrics.log_statements = self._count_pattern(content, self.PATTERNS["console_log"])
        metrics.log_statements += self._count_pattern(content, self.PATTERNS["logger"])
        metrics.error_logging = self._count_pattern(content, self.PATTERNS["console_error"])

        # Null checks (JS has many patterns)
        metrics.null_checks = self._count_pattern(content, self.PATTERNS["null_check"])
        metrics.null_checks += self._count_pattern(content, self.PATTERNS["optional_chain"])
        metrics.null_checks += self._count_pattern(content, self.PATTERNS["nullish_coalesce"])
        metrics.null_checks += self._count_pattern(content, self.PATTERNS["or_default"])

        # Input validation
        metrics.input_validation = self._count_pattern(content, self.PATTERNS["type_guard"])
        metrics.input_validation += self._count_pattern(content, self.PATTERNS["instanceof"])

        # Timeout
        metrics.timeout_configs = self._count_pattern(content, self.PATTERNS["timeout"])

        # Assertions
        metrics.assertions = self._count_pattern(content, self.PATTERNS["assert"])

        # Calculate error checks
        metrics.error_checks = metrics.error_handlers + metrics.assertions

        return metrics


# =============================================================================
# BASH/SHELL ANALYZER
# =============================================================================


class BashAnalyzer(LanguageAnalyzer):
    """Bash and shell script resilience pattern detector."""

    LANGUAGE_NAME = "bash"
    FILE_EXTENSIONS = [".sh", ".bash", ".zsh"]

    PATTERNS = {
        # Error handling
        "set_e": re.compile(r"set\s+-e|set\s+-o\s+errexit"),
        "set_u": re.compile(r"set\s+-u|set\s+-o\s+nounset"),
        "set_pipefail": re.compile(r"set\s+-o\s+pipefail"),
        "trap": re.compile(r"\btrap\s+"),
        "or_exit": re.compile(r"\|\|\s*(exit|return|die|fatal)"),
        "and_check": re.compile(r"&&\s*\{"),
        # Error checking
        "if_check": re.compile(r"if\s+\[\s*[!\s]*\$\?"),
        "exit_check": re.compile(r"if\s+!\s*\w+"),
        "test_file": re.compile(r"\[\s*-[defrsxwz]\s+"),
        # Logging
        "echo_stderr": re.compile(r"echo\s+.*>&2"),
        "logger": re.compile(r"\blogger\s+"),
        "printf": re.compile(r"\bprintf\s+"),
        # Input validation
        "param_check": re.compile(r"\$\{[^}]+:-"),  # ${VAR:-default}
        "arg_check": re.compile(r'if\s+\[\s*-z\s+"\$'),
        # Cleanup
        "cleanup_trap": re.compile(r'trap\s+[\'"]?cleanup|trap\s+.*EXIT'),
    }

    def analyze(self, content: str, filepath: str = "") -> LanguageResilienceMetrics:
        metrics = LanguageResilienceMetrics()

        # Strict mode settings
        set_e = self._count_pattern(content, self.PATTERNS["set_e"])
        set_u = self._count_pattern(content, self.PATTERNS["set_u"])
        set_pipefail = self._count_pattern(content, self.PATTERNS["set_pipefail"])
        metrics.extras["strict_mode"] = set_e + set_u + set_pipefail

        # Error handling
        metrics.error_handlers = self._count_pattern(content, self.PATTERNS["trap"])
        metrics.error_propagation = self._count_pattern(content, self.PATTERNS["or_exit"])

        # Error checks
        metrics.error_checks = self._count_pattern(content, self.PATTERNS["if_check"])
        metrics.error_checks += self._count_pattern(content, self.PATTERNS["exit_check"])
        metrics.error_checks += self._count_pattern(content, self.PATTERNS["test_file"])

        # Logging
        metrics.log_statements = self._count_pattern(content, self.PATTERNS["echo_stderr"])
        metrics.log_statements += self._count_pattern(content, self.PATTERNS["logger"])
        metrics.error_logging = self._count_pattern(content, self.PATTERNS["echo_stderr"])

        # Input validation
        metrics.input_validation = self._count_pattern(content, self.PATTERNS["param_check"])
        metrics.input_validation += self._count_pattern(content, self.PATTERNS["arg_check"])

        # Cleanup
        metrics.cleanup_blocks = self._count_pattern(content, self.PATTERNS["cleanup_trap"])

        # Null checks (variable checks)
        metrics.null_checks = self._count_pattern(content, self.PATTERNS["param_check"])

        return metrics


# =============================================================================
# SQL ANALYZER
# =============================================================================


class SQLAnalyzer(LanguageAnalyzer):
    """SQL resilience pattern detector."""

    LANGUAGE_NAME = "sql"
    FILE_EXTENSIONS = [".sql"]

    PATTERNS = {
        # Transaction control
        "begin_transaction": re.compile(r"\b(BEGIN|START)\s+(TRANSACTION|TRAN)\b", re.IGNORECASE),
        "commit": re.compile(r"\bCOMMIT\b", re.IGNORECASE),
        "rollback": re.compile(r"\bROLLBACK\b", re.IGNORECASE),
        "savepoint": re.compile(r"\bSAVEPOINT\b", re.IGNORECASE),
        # Error handling (varies by dialect)
        "try_catch": re.compile(r"\bBEGIN\s+TRY\b", re.IGNORECASE),  # SQL Server
        "exception": re.compile(r"\bEXCEPTION\b", re.IGNORECASE),  # PL/SQL
        "declare_handler": re.compile(r"\bDECLARE\s+.*HANDLER\b", re.IGNORECASE),  # MySQL
        # Null handling
        "coalesce": re.compile(r"\bCOALESCE\s*\(", re.IGNORECASE),
        "ifnull": re.compile(r"\b(IFNULL|ISNULL|NVL)\s*\(", re.IGNORECASE),
        "nullif": re.compile(r"\bNULLIF\s*\(", re.IGNORECASE),
        "is_null": re.compile(r"\bIS\s+(NOT\s+)?NULL\b", re.IGNORECASE),
        # Constraints (defensive schema)
        "not_null": re.compile(r"\bNOT\s+NULL\b", re.IGNORECASE),
        "check": re.compile(r"\bCHECK\s*\(", re.IGNORECASE),
        "foreign_key": re.compile(r"\bFOREIGN\s+KEY\b", re.IGNORECASE),
        # Safe operations
        "if_exists": re.compile(r"\bIF\s+(NOT\s+)?EXISTS\b", re.IGNORECASE),
        "on_conflict": re.compile(r"\bON\s+CONFLICT\b", re.IGNORECASE),  # PostgreSQL
        "merge": re.compile(r"\bMERGE\s+INTO\b", re.IGNORECASE),
    }

    def analyze(self, content: str, filepath: str = "") -> LanguageResilienceMetrics:
        metrics = LanguageResilienceMetrics()

        # Transaction control
        begin_count = self._count_pattern(content, self.PATTERNS["begin_transaction"])
        commit_count = self._count_pattern(content, self.PATTERNS["commit"])
        rollback_count = self._count_pattern(content, self.PATTERNS["rollback"])

        metrics.error_handlers = rollback_count
        metrics.cleanup_blocks = commit_count
        metrics.extras["transactions"] = begin_count
        metrics.extras["savepoints"] = self._count_pattern(content, self.PATTERNS["savepoint"])

        # Error handling
        metrics.error_checks = self._count_pattern(content, self.PATTERNS["try_catch"])
        metrics.error_checks += self._count_pattern(content, self.PATTERNS["exception"])
        metrics.error_checks += self._count_pattern(content, self.PATTERNS["declare_handler"])

        # Null handling
        metrics.null_checks = self._count_pattern(content, self.PATTERNS["coalesce"])
        metrics.null_checks += self._count_pattern(content, self.PATTERNS["ifnull"])
        metrics.null_checks += self._count_pattern(content, self.PATTERNS["is_null"])

        # Defensive operations
        metrics.input_validation = self._count_pattern(content, self.PATTERNS["if_exists"])
        metrics.input_validation += self._count_pattern(content, self.PATTERNS["on_conflict"])

        return metrics


# =============================================================================
# ANALYZER REGISTRY
# =============================================================================


class AnalyzerRegistry:
    """Registry of all language analyzers."""

    def __init__(self):
        self._analyzers: dict[str, LanguageAnalyzer] = {}
        self._extension_map: dict[str, str] = {}

        # Register built-in analyzers
        self.register(PythonAnalyzer())
        self.register(CAnalyzer())
        self.register(GoAnalyzer())
        self.register(RustAnalyzer())
        self.register(JavaAnalyzer())
        self.register(JavaScriptAnalyzer())
        self.register(BashAnalyzer())
        self.register(SQLAnalyzer())

    def register(self, analyzer: LanguageAnalyzer):
        """Register a language analyzer."""
        self._analyzers[analyzer.LANGUAGE_NAME] = analyzer
        for ext in analyzer.FILE_EXTENSIONS:
            self._extension_map[ext] = analyzer.LANGUAGE_NAME

    def get_analyzer(self, language: str) -> LanguageAnalyzer | None:
        """Get analyzer by language name."""
        return self._analyzers.get(language)

    def get_analyzer_for_file(self, filepath: str) -> LanguageAnalyzer | None:
        """Get analyzer based on file extension."""
        from pathlib import Path

        ext = Path(filepath).suffix.lower()
        language = self._extension_map.get(ext)
        if language:
            return self._analyzers.get(language)
        return None

    def supported_extensions(self) -> list[str]:
        """Get all supported file extensions."""
        return list(self._extension_map.keys())

    def supported_languages(self) -> list[str]:
        """Get all supported language names."""
        return list(self._analyzers.keys())


# Global registry instance
ANALYZER_REGISTRY = AnalyzerRegistry()


def get_analyzer(filepath: str) -> LanguageAnalyzer | None:
    """Convenience function to get analyzer for a file."""
    return ANALYZER_REGISTRY.get_analyzer_for_file(filepath)


def analyze_file(filepath: str, content: str) -> LanguageResilienceMetrics | None:
    """Analyze a file and return metrics."""
    analyzer = get_analyzer(filepath)
    if analyzer:
        return analyzer.analyze(content, filepath)
    return None
