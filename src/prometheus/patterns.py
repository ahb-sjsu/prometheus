#!/usr/bin/env python3
"""
Hubris Pattern Definitions
==========================
All regex patterns for detecting resilience patterns across languages.

Organized by:
- Pattern type (retry, timeout, circuit_breaker, exception)
- Language (python, javascript, go, java, c, cpp)
- Category (triggers, quality_indicators, anti_patterns)
"""

import re
from re import Pattern

# =============================================================================
# RETRY PATTERNS
# =============================================================================

RETRY_PATTERNS: dict[str, dict[str, Pattern]] = {
    "python": {
        # Triggers (library-based)
        "tenacity_decorator": re.compile(r"@retry\b|@tenacity\.retry"),
        "retrying_decorator": re.compile(r"@retrying\b"),
        "backoff_decorator": re.compile(r"@backoff\.(on_exception|on_predicate)"),
        # Manual retry loops
        "for_retry": re.compile(
            r"for\s+\w+\s+in\s+range\s*\(\s*\d+\s*\).*?(?:try|except)", re.DOTALL
        ),
        "while_retry": re.compile(
            r"while\s+(?:True|retry|attempt|tries).*?(?:try|except)", re.DOTALL
        ),
        # Quality indicators
        "exponential_backoff": re.compile(
            r"wait_exponential|exponential_backoff|backoff\.expo|\*\*\s*attempt|\*\*\s*retry|\*\s*2\s*\*\*"
        ),
        "jitter": re.compile(r"jitter|wait_random|random\.uniform|random\.random"),
        "max_retries": re.compile(
            r"max_retries|stop_after_attempt|max_tries|retry_limit|MAX_RETRIES"
        ),
        "sleep_call": re.compile(r"time\.sleep|asyncio\.sleep|await\s+sleep"),
    },
    "javascript": {
        "async_retry": re.compile(r"async-retry|p-retry|retry\s*\("),
        "for_retry": re.compile(r"for\s*\([^)]*(?:retry|attempt|tries)[^)]*\)"),
        "while_retry": re.compile(r"while\s*\([^)]*(?:retry|attempt|tries)[^)]*\)"),
        "exponential_backoff": re.compile(
            r"exponentialBackoff|Math\.pow\s*\(\s*2|backoff\s*\*\s*2"
        ),
        "jitter": re.compile(r"jitter|Math\.random"),
        "max_retries": re.compile(r"maxRetries|maxAttempts|MAX_RETRIES"),
    },
    "go": {
        "retry_lib": re.compile(r"cenkalti/backoff|avast/retry-go|hashicorp/go-retryablehttp"),
        "for_retry": re.compile(r"for\s+\w+\s*:?=\s*0\s*;\s*\w+\s*<\s*\d+"),
        "exponential_backoff": re.compile(r"ExponentialBackOff|backoff\.Exponential|math\.Pow\(2"),
        "jitter": re.compile(r"jitter|rand\.Float|rand\.Int"),
    },
    "java": {
        "resilience4j_retry": re.compile(r"@Retry|Retry\.of|RetryConfig"),
        "spring_retry": re.compile(r"@Retryable|RetryTemplate"),
        "failsafe": re.compile(r"Failsafe\.with|RetryPolicy\.builder"),
        "exponential_backoff": re.compile(r"exponentialBackoff|ExponentialBackoff|Math\.pow\(2"),
        "jitter": re.compile(r"jitter|randomDelay|Random\(\)"),
    },
    "c": {
        "for_retry": re.compile(
            r"for\s*\([^;]*;\s*\w+\s*<\s*(?:max_retries|MAX_RETRIES|retry_count|retries|MAX_ATTEMPTS|attempts)\s*;"
        ),
        "while_retry": re.compile(
            r"while\s*\(\s*(?:retries|retry_count|attempts|tries)\s*(?:<|<=|>|--|\+\+)"
        ),
        "retry_label": re.compile(r"\bretry\s*:|again\s*:"),
        "goto_retry": re.compile(r"goto\s+(?:retry|again|repeat)\s*;"),
        "exponential_backoff": re.compile(
            r"<<\s*(?:retry|attempt|tries)|(?:delay|sleep|wait)\s*\*=?\s*2|pow\s*\(\s*2"
        ),
        "jitter": re.compile(r"rand\s*\(\s*\)|random\s*\(\s*\)|drand48|arc4random"),
        "max_retries": re.compile(
            r"(?:max_retries|MAX_RETRIES|retry_count|MAX_ATTEMPTS|max_attempts)\s*[=<>]|#define\s+MAX_RETRIES"
        ),
        "sleep_call": re.compile(r"\b(?:sleep|usleep|nanosleep|Sleep)\s*\("),
    },
    "cpp": {
        "for_retry": re.compile(
            r"for\s*\([^;]*;\s*\w+\s*<\s*(?:max_retries|kMaxRetries|maxRetries|retry_count)\s*;"
        ),
        "while_retry": re.compile(
            r"while\s*\(\s*(?:retries|retry_count|attempts)\s*(?:<|<=|>|--|\+\+)"
        ),
        "catch_retry": re.compile(r"catch\s*\([^)]*\)\s*\{[^}]*(?:retry|continue|goto)"),
        "exponential_backoff": re.compile(
            r"std::chrono|std::this_thread::sleep_for|backoff\s*\*=?\s*2"
        ),
        "jitter": re.compile(
            r"std::uniform_int_distribution|std::uniform_real_distribution|std::random_device|std::mt19937"
        ),
        "max_retries": re.compile(
            r"(?:max_retries|kMaxRetries|maxRetries)\s*[=<>]|constexpr.*max.*retry", re.IGNORECASE
        ),
        "sleep_call": re.compile(
            r"std::this_thread::sleep_for|std::this_thread::sleep_until|Sleep\s*\("
        ),
    },
}

# Patterns that trigger detection (vs quality indicators)
RETRY_TRIGGERS = {
    "tenacity_decorator",
    "retrying_decorator",
    "backoff_decorator",
    "async_retry",
    "retry_lib",
    "resilience4j_retry",
    "spring_retry",
    "failsafe",
    "for_retry",
    "while_retry",
    "retry_label",
    "goto_retry",
    "catch_retry",
}

# Patterns that indicate quality
RETRY_QUALITY = {"exponential_backoff", "jitter", "max_retries", "sleep_call"}


# =============================================================================
# TIMEOUT PATTERNS
# =============================================================================

TIMEOUT_PATTERNS: dict[str, dict[str, Pattern]] = {
    "python": {
        "requests_timeout": re.compile(
            r"requests\.(get|post|put|delete|patch)\s*\([^)]*timeout\s*=\s*(\d+(?:\.\d+)?|None)"
        ),
        "requests_no_timeout": re.compile(
            r"requests\.(get|post|put|delete|patch)\s*\([^)]*\)(?![^)]*timeout)"
        ),
        "httpx_timeout": re.compile(r"httpx\.\w+\s*\([^)]*timeout\s*="),
        "aiohttp_timeout": re.compile(r"aiohttp\.ClientTimeout|timeout\s*=\s*aiohttp"),
        "socket_timeout": re.compile(r"socket\.setdefaulttimeout|\.settimeout\s*\("),
        "generic_timeout": re.compile(r"timeout\s*=\s*(\d+(?:\.\d+)?|None)"),
        "timeout_none": re.compile(r"timeout\s*=\s*None"),
    },
    "javascript": {
        "axios_timeout": re.compile(r"axios\.\w+\s*\([^)]*timeout\s*:"),
        "fetch_signal": re.compile(r"AbortController|signal\s*:"),
        "generic_timeout": re.compile(r"timeout\s*:\s*(\d+)"),
    },
    "go": {
        "http_timeout": re.compile(r"&http\.Client\s*\{[^}]*Timeout\s*:"),
        "context_timeout": re.compile(r"context\.WithTimeout|context\.WithDeadline"),
        "no_timeout": re.compile(r"http\.DefaultClient|&http\.Client\s*\{\s*\}"),
    },
    "java": {
        "okhttp_timeout": re.compile(r"\.connectTimeout\(|\.readTimeout\(|\.writeTimeout\("),
        "spring_timeout": re.compile(r"@Timeout|\.timeout\("),
        "socket_timeout": re.compile(r"setSoTimeout|setConnectTimeout"),
    },
    "c": {
        "socket_timeout": re.compile(
            r"setsockopt\s*\([^)]*SO_RCVTIMEO|setsockopt\s*\([^)]*SO_SNDTIMEO"
        ),
        "select_timeout": re.compile(
            r"\bselect\s*\([^)]*&\s*\w*timeout|poll\s*\([^)]*,\s*\d+\s*\)"
        ),
        "alarm_timeout": re.compile(r"\balarm\s*\(\s*\d+\s*\)|signal\s*\(\s*SIGALRM"),
        "generic_timeout": re.compile(r"(?:timeout|TIMEOUT)\s*[=:]\s*\d+|#define\s+\w*TIMEOUT"),
        "curl_timeout": re.compile(
            r"CURLOPT_TIMEOUT|CURLOPT_CONNECTTIMEOUT|curl_easy_setopt\s*\([^)]*TIMEOUT"
        ),
        "no_timeout": re.compile(r"connect\s*\([^)]*\)\s*;(?![^;]*timeout)", re.IGNORECASE),
    },
    "cpp": {
        "chrono_timeout": re.compile(r"std::chrono::(?:seconds|milliseconds|microseconds)"),
        "future_timeout": re.compile(r"std::future.*wait_for|std::future.*wait_until"),
        "condition_timeout": re.compile(
            r"std::condition_variable.*wait_for|std::condition_variable.*wait_until"
        ),
        "mutex_timeout": re.compile(r"std::timed_mutex|try_lock_for|try_lock_until"),
        "asio_timeout": re.compile(
            r"boost::asio::deadline_timer|asio::steady_timer|expires_after|expires_at"
        ),
        "socket_timeout": re.compile(r"setsockopt\s*\([^)]*SO_RCVTIMEO|socket_base::timeout"),
    },
}

TIMEOUT_ISSUES = {"requests_no_timeout", "no_timeout", "timeout_none"}


# =============================================================================
# CIRCUIT BREAKER PATTERNS
# =============================================================================

CIRCUIT_BREAKER_PATTERNS: dict[str, dict[str, Pattern]] = {
    "python": {
        "pybreaker": re.compile(r"from\s+pybreaker|import\s+pybreaker|CircuitBreaker\s*\("),
        "circuitbreaker": re.compile(r"@circuit\b|from\s+circuitbreaker"),
        "cb_fallback": re.compile(r"fallback\s*=|@fallback"),
        "cb_listener": re.compile(r"add_listener|CircuitBreakerListener"),
    },
    "javascript": {
        "opossum": re.compile(r"from\s+['\"]opossum|require\s*\(\s*['\"]opossum"),
        "brakes": re.compile(r"from\s+['\"]brakes|require\s*\(\s*['\"]brakes"),
        "cb_fallback": re.compile(r"\.fallback\s*\(|fallbackFn"),
        "cb_events": re.compile(r"\.on\s*\(['\"](?:open|close|halfOpen)"),
    },
    "java": {
        "resilience4j_cb": re.compile(
            r"@CircuitBreaker|CircuitBreakerConfig|CircuitBreakerRegistry"
        ),
        "hystrix": re.compile(r"@HystrixCommand|HystrixCircuitBreaker"),
        "cb_fallback": re.compile(r"fallbackMethod|@Fallback"),
        "cb_metrics": re.compile(r"CircuitBreakerMetrics|HealthIndicator"),
    },
    "go": {
        "gobreaker": re.compile(r"gobreaker\.NewCircuitBreaker|gobreaker\.Settings"),
        "hystrix_go": re.compile(r"hystrix\.Do|hystrix\.ConfigureCommand"),
        "cb_on_state": re.compile(r"OnStateChange|ReadyToTrip"),
    },
    "c": {
        "custom_cb": re.compile(
            r"(?:circuit|cb)_state\s*==?\s*(?:OPEN|CLOSED|HALF_OPEN)|enum\s+\w*circuit\w*state",
            re.IGNORECASE,
        ),
        "state_machine": re.compile(
            r"(?:CIRCUIT|CB)_(?:OPEN|CLOSED|HALF_OPEN)|failure_count\s*>=?\s*threshold"
        ),
        "cb_threshold": re.compile(
            r"(?:failure|error)_(?:threshold|limit|max)\s*[=:]|#define\s+\w*(?:FAILURE|ERROR)_(?:THRESHOLD|LIMIT)"
        ),
        "cb_logging": re.compile(
            r"(?:syslog|fprintf\s*\(\s*stderr|printf).*(?:circuit|state|open|closed)", re.IGNORECASE
        ),
    },
    "cpp": {
        "custom_cb": re.compile(
            r"class\s+\w*CircuitBreaker|CircuitBreaker\s*<|circuit_breaker", re.IGNORECASE
        ),
        "state_enum": re.compile(
            r"enum\s+(?:class\s+)?(?:State|CircuitState)\s*\{[^}]*OPEN[^}]*CLOSED"
        ),
        "cb_metrics": re.compile(r"prometheus|statsd|metrics::|counter\+\+|gauge"),
        "cb_logging": re.compile(r"LOG\(|SPDLOG|spdlog::|std::cerr|std::clog"),
        "cb_atomic": re.compile(r"std::atomic|atomic_|compare_exchange"),
    },
}

CB_TRIGGERS = {
    "pybreaker",
    "circuitbreaker",
    "opossum",
    "brakes",
    "resilience4j_cb",
    "hystrix",
    "gobreaker",
    "hystrix_go",
    "custom_cb",
    "state_machine",
    "state_enum",
}

CB_QUALITY = {
    "cb_fallback",
    "cb_listener",
    "cb_events",
    "cb_metrics",
    "cb_on_state",
    "cb_threshold",
    "cb_logging",
    "cb_atomic",
}


# =============================================================================
# EXCEPTION HANDLING PATTERNS
# =============================================================================

EXCEPTION_PATTERNS: dict[str, dict[str, Pattern]] = {
    "python": {
        # Anti-patterns
        "bare_except": re.compile(r"except\s*:"),
        "broad_except": re.compile(r"except\s+(?:Exception|BaseException)\s*(?:as\s+\w+)?:"),
        "except_pass": re.compile(r"except[^:]*:\s*\n\s*pass\b"),
        "except_continue": re.compile(r"except[^:]*:\s*\n\s*continue\b"),
        # Good patterns
        "specific_except": re.compile(
            r"except\s+(?!Exception|BaseException)\w+(?:Error|Exception)"
        ),
        "except_log": re.compile(r"except[^:]*:\s*\n[^\n]*(?:log|logger|logging)"),
        "except_raise": re.compile(r"except[^:]*:\s*\n[^\n]*raise\b"),
    },
    "javascript": {
        "empty_catch": re.compile(r"catch\s*\([^)]*\)\s*\{\s*\}"),
        "catch_all": re.compile(r"catch\s*\(\s*(?:e|err|error|ex)?\s*\)\s*\{"),
        "catch_log": re.compile(r"catch\s*\([^)]*\)\s*\{[^}]*console\.(log|error|warn)"),
    },
    "go": {
        "ignore_error": re.compile(r"\w+,\s*_\s*:?=|_\s*=\s*\w+\("),
        "empty_if_err": re.compile(r"if\s+err\s*!=\s*nil\s*\{\s*\}"),
    },
    "java": {
        "empty_catch": re.compile(r"catch\s*\([^)]+\)\s*\{\s*\}"),
        "catch_throwable": re.compile(r"catch\s*\(\s*(?:Throwable|Exception)\s+"),
        "swallow_exception": re.compile(r"catch\s*\([^)]+\)\s*\{[^}]*(?:// *ignore|// *TODO)"),
    },
    "c": {
        "ignore_return": re.compile(r"^\s*\w+\s*\([^)]*\)\s*;\s*$", re.MULTILINE),
        "empty_error_check": re.compile(
            r"if\s*\([^)]*(?:err|error|ret|rc|status)\s*[!=<>]=?[^)]*\)\s*\{\s*\}"
        ),
        "check_errno": re.compile(r"if\s*\(\s*errno\s*[!=]=|perror\s*\("),
        "error_logging": re.compile(r"(?:syslog|fprintf\s*\(\s*stderr|perror)\s*\("),
    },
    "cpp": {
        "empty_catch": re.compile(r"catch\s*\([^)]*\)\s*\{\s*\}"),
        "catch_all": re.compile(r"catch\s*\(\s*\.\.\.\s*\)"),
        "catch_log": re.compile(r"catch\s*\([^)]*\)\s*\{[^}]*(?:LOG|cerr|clog)"),
    },
}

EXCEPTION_ANTI_PATTERNS = {
    "bare_except",
    "broad_except",
    "except_pass",
    "except_continue",
    "empty_catch",
    "catch_all",
    "catch_throwable",
    "swallow_exception",
    "ignore_error",
    "empty_if_err",
    "ignore_return",
    "empty_error_check",
}


# =============================================================================
# LIBRARY DETECTION PATTERNS
# =============================================================================

LIBRARY_PATTERNS: dict[str, dict[str, Pattern]] = {
    "python": {
        "tenacity": re.compile(r"from\s+tenacity|import\s+tenacity"),
        "retrying": re.compile(r"from\s+retrying|import\s+retrying"),
        "backoff": re.compile(r"from\s+backoff|import\s+backoff"),
        "pybreaker": re.compile(r"from\s+pybreaker|import\s+pybreaker"),
        "circuitbreaker": re.compile(r"from\s+circuitbreaker|import\s+circuitbreaker"),
        "requests": re.compile(r"import\s+requests|from\s+requests"),
        "httpx": re.compile(r"import\s+httpx|from\s+httpx"),
        "aiohttp": re.compile(r"import\s+aiohttp|from\s+aiohttp"),
    },
    "javascript": {
        "opossum": re.compile(r"from\s+['\"]opossum|require\s*\(\s*['\"]opossum"),
        "cockatiel": re.compile(r"from\s+['\"]cockatiel|require\s*\(\s*['\"]cockatiel"),
        "async-retry": re.compile(r"from\s+['\"]async-retry|require\s*\(\s*['\"]async-retry"),
        "p-retry": re.compile(r"from\s+['\"]p-retry|require\s*\(\s*['\"]p-retry"),
        "axios": re.compile(r"from\s+['\"]axios|require\s*\(\s*['\"]axios"),
    },
    "java": {
        "resilience4j": re.compile(r"io\.github\.resilience4j|resilience4j"),
        "hystrix": re.compile(r"com\.netflix\.hystrix|HystrixCommand"),
        "failsafe": re.compile(r"net\.jodah\.failsafe|Failsafe"),
        "spring-retry": re.compile(r"org\.springframework\.retry|@Retryable"),
    },
    "go": {
        "gobreaker": re.compile(r"github\.com/sony/gobreaker|gobreaker\."),
        "hystrix-go": re.compile(r"github\.com/afex/hystrix-go|hystrix\."),
        "go-retryablehttp": re.compile(r"github\.com/hashicorp/go-retryablehttp"),
        "backoff": re.compile(r"github\.com/cenkalti/backoff"),
    },
    "c": {
        "curl": re.compile(r"#include\s*[<\"]curl/curl\.h|CURLOPT_"),
        "libevent": re.compile(r"#include\s*[<\"]event\.h|event_base_"),
        "libev": re.compile(r"#include\s*[<\"]ev\.h|ev_io_"),
    },
    "cpp": {
        "boost_asio": re.compile(r'#include\s*[<"]boost/asio|boost::asio'),
        "abseil": re.compile(r'#include\s*[<"]absl/|absl::'),
        "spdlog": re.compile(r'#include\s*[<"]spdlog/|spdlog::'),
    },
}


# =============================================================================
# LANGUAGE EXTENSION MAPPING
# =============================================================================

LANGUAGE_EXTENSIONS = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "javascript",
    ".jsx": "javascript",
    ".tsx": "javascript",
    ".java": "java",
    ".go": "go",
    ".c": "c",
    ".h": "c",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".hpp": "cpp",
}

SUPPORTED_LANGUAGES = {"python", "javascript", "java", "go", "c", "cpp"}
