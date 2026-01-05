#!/usr/bin/env python3
"""
Hubris v3 - Resilience Theater Detector
========================================

v3 CHANGES (over v2):
- Better false positive filtering for class/dataclass definitions
- Skip matches in class names (class CircuitBreakerIssue)
- Skip matches in comments about patterns
- More robust pattern definition detection

v2 CHANGES:
- Added false positive filtering for pattern definition code
- Detectors no longer flag regex patterns that DEFINE what to look for
"""

import re
import json
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime


# =============================================================================
# FALSE POSITIVE FILTERING (IMPROVED IN V3)
# =============================================================================

def is_pattern_definition(content: str, match_start: int) -> bool:
    """
    Check if a match is inside a pattern definition context.
    """
    line_start = content.rfind('\n', 0, match_start) + 1
    line_end = content.find('\n', match_start)
    if line_end == -1:
        line_end = len(content)
    line = content[line_start:line_end]
    
    # Regex compilation
    if 're.compile(' in line:
        return True
    
    # Check broader context for pattern dictionary
    context_start = max(0, match_start - 500)
    context = content[context_start:match_start]
    
    pattern_indicators = [
        '_PATTERNS = {',
        '_PATTERNS= {', 
        '_PATTERNS={',
        'PATTERNS = {',
        'PATTERNS={',
        ': re.compile(',
    ]
    
    for indicator in pattern_indicators:
        if indicator in context:
            # Check we're still inside the dict (count braces)
            open_braces = context.count('{') - context.count('}')
            if open_braces > 0:
                return True
    
    return False


def is_class_or_dataclass_definition(content: str, match_start: int) -> bool:
    """
    Check if match is in a class name or dataclass definition.
    
    Catches:
    - class CircuitBreakerIssue:
    - @dataclass class CircuitBreakerMetrics:
    - class MyCircuitBreaker(BaseClass):
    """
    line_start = content.rfind('\n', 0, match_start) + 1
    line_end = content.find('\n', match_start)
    if line_end == -1:
        line_end = len(content)
    line = content[line_start:line_end]
    
    # Check if this line is a class definition
    if re.match(r'\s*class\s+\w*', line):
        return True
    
    # Check if previous line is @dataclass
    prev_line_end = line_start - 1
    if prev_line_end > 0:
        prev_line_start = content.rfind('\n', 0, prev_line_end) + 1
        prev_line = content[prev_line_start:prev_line_end]
        if '@dataclass' in prev_line:
            return True
    
    return False


def is_in_docstring(content: str, position: int) -> bool:
    """Check if position is inside a docstring."""
    before = content[:position]
    triple_double = before.count('"""')
    triple_single = before.count("'''")
    return (triple_double % 2 == 1) or (triple_single % 2 == 1)


def is_in_comment(content: str, position: int) -> bool:
    """Check if position is inside a comment."""
    line_start = content.rfind('\n', 0, position) + 1
    line = content[line_start:position]
    return '#' in line


def is_type_hint_or_annotation(content: str, match_start: int) -> bool:
    """
    Check if match is in a type hint or string annotation.
    
    Catches:
    - issue_type: str  # 'invisible', 'no_fallback'...
    - def func() -> CircuitBreakerIssue:
    """
    line_start = content.rfind('\n', 0, match_start) + 1
    line_end = content.find('\n', match_start)
    if line_end == -1:
        line_end = len(content)
    line = content[line_start:line_end]
    
    # Type hint patterns
    if re.search(r':\s*\w+\s*=|:\s*str\s*#|->\s*\w+:', line):
        return True
    
    # String in comment describing types
    if '#' in line and ("'" in line or '"' in line):
        hash_pos = line.find('#')
        match_pos_in_line = match_start - line_start
        if match_pos_in_line > hash_pos:
            return True
    
    return False


def should_skip_match(content: str, match_start: int) -> bool:
    """
    Master filter: should this match be skipped?
    """
    if is_pattern_definition(content, match_start):
        return True
    if is_class_or_dataclass_definition(content, match_start):
        return True
    if is_in_docstring(content, match_start):
        return True
    if is_in_comment(content, match_start):
        return True
    if is_type_hint_or_annotation(content, match_start):
        return True
    return False


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class RetryIssue:
    file: str
    line: int
    issue_type: str
    severity: str
    description: str
    code_snippet: str = ""
    fix_suggestion: str = ""


@dataclass
class TimeoutIssue:
    file: str
    line: int
    issue_type: str
    severity: str
    description: str
    timeout_value: float = 0
    context: str = ""


@dataclass
class CircuitBreakerIssue:
    file: str
    line: int
    issue_type: str
    severity: str
    description: str


@dataclass
class ExceptionIssue:
    file: str
    line: int
    issue_type: str
    severity: str
    description: str
    exception_type: str = ""


@dataclass
class FallbackIssue:
    file: str
    line: int
    issue_type: str
    severity: str
    description: str


@dataclass
class PatternDetection:
    pattern_type: str
    file: str
    line: int
    quality: str
    details: dict = field(default_factory=dict)


@dataclass
class HubrisReport:
    codebase_path: str
    timestamp: str
    
    patterns_detected: int = 0
    patterns_correct: int = 0
    patterns_partial: int = 0
    patterns_cargo_cult: int = 0
    
    theater_ratio: float = 0.0
    
    retry_issues: list = field(default_factory=list)
    timeout_issues: list = field(default_factory=list)
    circuit_breaker_issues: list = field(default_factory=list)
    exception_issues: list = field(default_factory=list)
    fallback_issues: list = field(default_factory=list)
    
    patterns: list = field(default_factory=list)
    
    resilience_libraries: list = field(default_factory=list)
    library_count: int = 0
    
    quadrant: str = ""
    verdict: str = ""
    risk_level: str = ""
    
    recommendations: list = field(default_factory=list)
    
    total_issues: int = 0
    high_severity_count: int = 0
    medium_severity_count: int = 0
    low_severity_count: int = 0


# =============================================================================
# PATTERN DETECTORS
# =============================================================================

def is_generator_loop(context: str) -> bool:
    """Check if a while True loop is actually a generator pattern, not retry."""
    has_yield = bool(re.search(r'\byield\b', context))
    has_stop_iteration = bool(re.search(r'StopIteration', context))
    return has_yield or has_stop_iteration


def is_user_input_loop(context: str) -> bool:
    """Check if loop is waiting for user input."""
    input_patterns = [
        r'input\s*\(',
        r'raw_input\s*\(',
        r'sys\.stdin',
        r'readline\s*\(',
        r'getpass',
        r'prompt',
    ]
    has_input = any(re.search(p, context) for p in input_patterns)
    has_return_on_valid = bool(re.search(r'if\s+.*:\s*\n\s*return', context))
    return has_input and has_return_on_valid


def is_data_streaming_loop(context: str) -> bool:
    """Check if loop is reading a data stream (exits on EOF/empty)."""
    streaming_patterns = [
        r'marshal\.load',
        r'pickle\.load',
        r'\.read\s*\(',
        r'\.recv\s*\(',
        r'EOFError',
        r'StopIteration',
    ]
    return any(re.search(p, context) for p in streaming_patterns)


def is_algorithm_loop(context: str) -> bool:
    """Check if loop is an algorithm (bisect, tree traversal, etc.)."""
    algorithm_patterns = [
        r'bisect',
        r'binary.?search',
        r'rsplit.*\/',  # path traversal
        r'parent.*=|=.*parent',  # tree traversal
        r'\.pop\s*\(',  # stack/queue processing
        r'left.*right|right.*left',  # tree traversal
    ]
    return any(re.search(p, context, re.IGNORECASE) for p in algorithm_patterns)


def is_pagination_loop(context: str) -> bool:
    """Check if loop is paginating through data."""
    pagination_patterns = [
        r'block_size',
        r'page_size',
        r'offset\s*\+',
        r'start\s*=.*end',
        r'changeStart|changeEnd',
        r'cursor',
        r'next_page',
    ]
    return any(re.search(p, context, re.IGNORECASE) for p in pagination_patterns)


def has_loop_exit(context: str) -> bool:
    """Check if a while True loop has proper exit conditions."""
    # Look for return, break, raise, die, exit inside the loop
    exit_patterns = [
        r'\breturn\b',
        r'\bbreak\b', 
        r'\braise\b',
        r'\bdie\s*\(',
        r'sys\.exit',
        r'exit\s*\(',
    ]
    return any(re.search(p, context) for p in exit_patterns)


def has_bounded_exit(context: str) -> bool:
    """Check if a loop has bounded exit conditions."""
    bounded_patterns = [
        r'max_redirects',
        r'max_retries',
        r'max_attempts',
        r'retry_count\s*>=',
        r'attempt\s*>=',
        r'tries\s*>=',
        r'if\s+.*>\s*\d+.*:.*(?:break|raise|return)',
        r'if\s+len\s*\(.*\)\s*>',
    ]
    for pattern in bounded_patterns:
        if re.search(pattern, context, re.IGNORECASE):
            return True
    return False


def is_likely_retry_loop(context: str) -> bool:
    """
    Determine if a while True loop is likely a retry loop vs other patterns.
    Returns True only if it looks like actual retry logic.
    """
    # Strong indicators this IS a retry loop
    retry_indicators = [
        r'retry',
        r'attempt',
        r'tries',
        r'backoff',
        r'sleep.*\d',  # sleep with a number (delay)
        r'time\.sleep',
        r'failed.*try|try.*again',
        r'reconnect',
        r'connection.*error|error.*connection',
    ]
    
    has_retry_indicator = any(re.search(p, context, re.IGNORECASE) for p in retry_indicators)
    
    # If no retry indicators, probably not a retry loop
    if not has_retry_indicator:
        return False
    
    # Even with retry indicators, exclude known non-retry patterns
    if is_user_input_loop(context):
        return False
    if is_data_streaming_loop(context):
        return False
    if is_algorithm_loop(context):
        return False
    if is_pagination_loop(context):
        return False
    
    return True


class RetryDetector:
    RETRY_PATTERNS = {
        'python': {
            'tenacity_decorator': re.compile(r'@retry\b|@tenacity\.retry'),
            'retrying_decorator': re.compile(r'@retrying\b'),
            'backoff_decorator': re.compile(r'@backoff\.(on_exception|on_predicate)'),
            'for_retry': re.compile(r'for\s+\w+\s+in\s+range\s*\(\s*\d+\s*\).*?(?:try|except)', re.DOTALL),
            'while_retry': re.compile(r'while\s+(?:True|retry|attempt|tries)'),
            'exponential_backoff': re.compile(r'wait_exponential|exponential_backoff|backoff\.expo|\*\*\s*attempt|\*\*\s*retry|\*\s*2\s*\*\*'),
            'jitter': re.compile(r'jitter|wait_random|random\.uniform|random\.random'),
            'max_retries': re.compile(r'max_retries|stop_after_attempt|max_tries|retry_limit|MAX_RETRIES|max_redirects|max_attempts'),
            'sleep_call': re.compile(r'time\.sleep|asyncio\.sleep|await\s+sleep'),
        },
        'javascript': {
            'async_retry': re.compile(r'async-retry|p-retry|retry\s*\('),
            'for_retry': re.compile(r'for\s*\([^)]*(?:retry|attempt|tries)[^)]*\)'),
            'while_retry': re.compile(r'while\s*\([^)]*(?:retry|attempt|tries)[^)]*\)'),
            'exponential_backoff': re.compile(r'exponentialBackoff|Math\.pow\s*\(\s*2|backoff\s*\*\s*2'),
            'jitter': re.compile(r'jitter|Math\.random'),
            'max_retries': re.compile(r'maxRetries|maxAttempts|MAX_RETRIES'),
        },
        'go': {
            'retry_lib': re.compile(r'cenkalti/backoff|avast/retry-go|hashicorp/go-retryablehttp'),
            'for_retry': re.compile(r'for\s+\w+\s*:?=\s*0\s*;\s*\w+\s*<\s*\d+'),
            'exponential_backoff': re.compile(r'ExponentialBackOff|backoff\.Exponential|math\.Pow\(2'),
            'jitter': re.compile(r'jitter|rand\.Float|rand\.Int'),
        },
        'java': {
            'resilience4j_retry': re.compile(r'@Retry|Retry\.of|RetryConfig'),
            'spring_retry': re.compile(r'@Retryable|RetryTemplate'),
            'failsafe': re.compile(r'Failsafe\.with|RetryPolicy\.builder'),
            'exponential_backoff': re.compile(r'exponentialBackoff|ExponentialBackoff|Math\.pow\(2'),
            'jitter': re.compile(r'jitter|randomDelay|Random\(\)'),
        }
    }
    
    def detect(self, content: str, filepath: str, language: str) -> tuple[list, list]:
        patterns = []
        issues = []
        
        lang_patterns = self.RETRY_PATTERNS.get(language, self.RETRY_PATTERNS.get('python', {}))
        
        for pattern_name, pattern in lang_patterns.items():
            if 'decorator' in pattern_name or 'lib' in pattern_name:
                for match in pattern.finditer(content):
                    if should_skip_match(content, match.start()):
                        continue
                    
                    line_num = content[:match.start()].count('\n') + 1
                    lines = content.splitlines()
                    start = max(0, line_num - 5)
                    end = min(len(lines), line_num + 15)
                    context = '\n'.join(lines[start:end])
                    
                    quality = self._evaluate_retry_quality(context, lang_patterns)
                    
                    patterns.append(PatternDetection(
                        pattern_type='retry',
                        file=filepath,
                        line=line_num,
                        quality=quality,
                        details={'pattern': pattern_name, 'library': True}
                    ))
                    
                    if quality != 'CORRECT':
                        issues.extend(self._generate_retry_issues(filepath, line_num, context, quality, lang_patterns))
        
        for pattern_name in ['for_retry', 'while_retry']:
            pattern = lang_patterns.get(pattern_name)
            if pattern:
                for match in pattern.finditer(content):
                    if should_skip_match(content, match.start()):
                        continue
                    
                    line_num = content[:match.start()].count('\n') + 1
                    lines = content.splitlines()
                    start = max(0, line_num - 2)
                    end = min(len(lines), line_num + 40)  # Larger context for loop body
                    context = '\n'.join(lines[start:end])
                    
                    # Skip generator patterns - they're not retry loops
                    if is_generator_loop(context):
                        continue
                    
                    # Skip user input loops
                    if is_user_input_loop(context):
                        continue
                    
                    # Skip data streaming loops (exit on EOF)
                    if is_data_streaming_loop(context):
                        continue
                    
                    # Skip algorithm loops (bisect, tree traversal, etc.)
                    if is_algorithm_loop(context):
                        continue
                    
                    # Skip pagination loops
                    if is_pagination_loop(context):
                        continue
                    
                    # For while True loops, require retry-like indicators
                    if pattern_name == 'while_retry' and 'while True' in match.group(0):
                        if not is_likely_retry_loop(context):
                            # Has exit conditions but doesn't look like retry - skip
                            if has_loop_exit(context):
                                continue
                    
                    # Skip if loop has explicit bounded exit
                    if has_bounded_exit(context):
                        # Still detect but mark as PARTIAL (bounded but no backoff)
                        quality = 'PARTIAL'
                        patterns.append(PatternDetection(
                            pattern_type='retry',
                            file=filepath,
                            line=line_num,
                            quality=quality,
                            details={'pattern': pattern_name, 'library': False, 'manual': True, 'bounded': True}
                        ))
                        continue
                    
                    # Check if this really looks like a retry loop
                    if not is_likely_retry_loop(context) and has_loop_exit(context):
                        # Has proper exits and doesn't look like retry - skip entirely
                        continue
                    
                    quality = self._evaluate_retry_quality(context, lang_patterns)
                    
                    patterns.append(PatternDetection(
                        pattern_type='retry',
                        file=filepath,
                        line=line_num,
                        quality=quality,
                        details={'pattern': pattern_name, 'library': False, 'manual': True}
                    ))
                    
                    if quality != 'CORRECT':
                        issues.extend(self._generate_retry_issues(filepath, line_num, context, quality, lang_patterns))
        
        return patterns, issues
    
    def _evaluate_retry_quality(self, context: str, lang_patterns: dict) -> str:
        has_backoff = bool(lang_patterns.get('exponential_backoff', re.compile(r'$^')).search(context))
        has_jitter = bool(lang_patterns.get('jitter', re.compile(r'$^')).search(context))
        has_max = bool(lang_patterns.get('max_retries', re.compile(r'$^')).search(context))
        has_sleep = bool(lang_patterns.get('sleep_call', re.compile(r'sleep')).search(context))
        
        # Also check for bounded exit patterns
        has_bounded = has_bounded_exit(context)
        
        broad_exception = bool(re.search(r'except\s*:|except\s+Exception\s*:', context))
        
        if has_backoff and (has_max or has_bounded) and (has_jitter or not broad_exception):
            return 'CORRECT'
        elif has_sleep and (has_max or has_bounded):
            return 'PARTIAL'
        elif has_sleep or has_max or has_bounded:
            return 'PARTIAL'
        else:
            return 'CARGO_CULT'
    
    def _generate_retry_issues(self, filepath: str, line: int, context: str, quality: str, lang_patterns: dict) -> list:
        issues = []
        has_backoff = bool(lang_patterns.get('exponential_backoff', re.compile(r'$^')).search(context))
        has_max = bool(lang_patterns.get('max_retries', re.compile(r'$^')).search(context))
        has_sleep = bool(lang_patterns.get('sleep_call', re.compile(r'sleep')).search(context))
        has_bounded = has_bounded_exit(context)
        
        if not has_backoff and not has_sleep:
            issues.append(RetryIssue(
                file=filepath, line=line, issue_type='no_backoff', severity='HIGH',
                description='Retry without backoff - will cause thundering herd on failure',
                fix_suggestion='Add exponential backoff: time.sleep(base_delay * (2 ** attempt))'
            ))
        
        if not has_max and not has_bounded:
            issues.append(RetryIssue(
                file=filepath, line=line, issue_type='no_max', severity='HIGH',
                description='Retry without maximum attempts - may retry forever',
                fix_suggestion='Add max_retries limit (typically 3-5 attempts)'
            ))
        
        return issues


class TimeoutDetector:
    TIMEOUT_PATTERNS = {
        'python': {
            'socket_timeout': re.compile(r'socket\.setdefaulttimeout\s*\(\s*(\d+(?:\.\d+)?)\s*\)'),
            'requests_timeout': re.compile(r'timeout\s*=\s*(\d+(?:\.\d+)?)'),
            'async_timeout': re.compile(r'async_timeout\.timeout\s*\(\s*(\d+(?:\.\d+)?)\s*\)'),
            'timeout_decorator': re.compile(r'@timeout\s*\(\s*(\d+(?:\.\d+)?)\s*\)'),
            'no_timeout': re.compile(r'timeout\s*=\s*None'),
        },
    }
    
    def detect(self, content: str, filepath: str, language: str) -> tuple[list, list]:
        patterns = []
        issues = []
        
        lang_patterns = self.TIMEOUT_PATTERNS.get(language, self.TIMEOUT_PATTERNS.get('python', {}))
        
        no_timeout = lang_patterns.get('no_timeout')
        if no_timeout:
            for match in no_timeout.finditer(content):
                if should_skip_match(content, match.start()):
                    continue
                    
                line_num = content[:match.start()].count('\n') + 1
                patterns.append(PatternDetection(
                    pattern_type='timeout', file=filepath, line=line_num,
                    quality='CARGO_CULT', details={'no_timeout': True}
                ))
                issues.append(TimeoutIssue(
                    file=filepath, line=line_num, issue_type='disabled', severity='HIGH',
                    description='Explicit timeout=None disables timeout - can hang indefinitely'
                ))
        
        for pattern_name, pattern in lang_patterns.items():
            if 'no_timeout' in pattern_name:
                continue
            
            for match in pattern.finditer(content):
                if should_skip_match(content, match.start()):
                    continue
                    
                line_num = content[:match.start()].count('\n') + 1
                timeout_val = None
                if match.groups():
                    try:
                        timeout_val = float(match.group(1) if match.lastindex else 0)
                    except (ValueError, TypeError):
                        pass
                
                quality = 'CORRECT'
                if timeout_val and timeout_val > 120:
                    quality = 'PARTIAL'
                    issues.append(TimeoutIssue(
                        file=filepath, line=line_num, issue_type='too_long', severity='MEDIUM',
                        description=f'Timeout of {timeout_val}s is very long', timeout_value=timeout_val
                    ))
                
                patterns.append(PatternDetection(
                    pattern_type='timeout', file=filepath, line=line_num,
                    quality=quality, details={'timeout_value': timeout_val}
                ))
        
        return patterns, issues


class CircuitBreakerDetector:
    CB_PATTERNS = {
        'python': {
            'pybreaker': re.compile(r'from\s+pybreaker|import\s+pybreaker|CircuitBreaker\s*\('),
            'circuitbreaker': re.compile(r'@circuit\b|from\s+circuitbreaker'),
            # Don't detect custom_cb by individual states - too many false positives
            'cb_listener': re.compile(r'listeners?\s*=|on_state_change|add_listener'),
            'cb_metrics': re.compile(r'prometheus|statsd|metrics\.emit|counter\.inc'),
            'cb_fallback': re.compile(r'fallback|default_value|on_failure'),
            'cb_threshold': re.compile(r'fail_max|failure_threshold|error_threshold'),
        },
    }
    
    def _is_circuit_breaker_state_machine(self, content: str) -> bool:
        """
        Check if content contains a real circuit breaker state machine.
        Requires at least 2 of: OPEN, CLOSED, HALF_OPEN appearing as state definitions.
        """
        # Look for state machine patterns - need multiple states defined together
        has_open = bool(re.search(r'\bOPEN\s*=|state\s*==?\s*["\']?OPEN|CircuitState\.OPEN', content))
        has_closed = bool(re.search(r'\bCLOSED\s*=|state\s*==?\s*["\']?CLOSED|CircuitState\.CLOSED', content))
        has_half_open = bool(re.search(r'\bHALF_OPEN\s*=|state\s*==?\s*["\']?HALF_OPEN|CircuitState\.HALF_OPEN', content))
        
        # Need at least 2 states to be a real circuit breaker
        state_count = sum([has_open, has_closed, has_half_open])
        return state_count >= 2
    
    def detect(self, content: str, filepath: str, language: str) -> tuple[list, list]:
        patterns = []
        issues = []
        
        lang_patterns = self.CB_PATTERNS.get(language, self.CB_PATTERNS.get('python', {}))
        
        # Check for library-based circuit breakers
        for pattern_name, pattern in lang_patterns.items():
            if any(x in pattern_name for x in ['fallback', 'metrics', 'listener', 'events', 'threshold', 'on_state']):
                continue
            
            for match in pattern.finditer(content):
                if should_skip_match(content, match.start()):
                    continue
                
                line_num = content[:match.start()].count('\n') + 1
                lines = content.splitlines()
                start = max(0, line_num - 5)
                end = min(len(lines), line_num + 30)
                context = '\n'.join(lines[start:end])
                
                quality = self._evaluate_cb_quality(context, lang_patterns)
                
                patterns.append(PatternDetection(
                    pattern_type='circuit_breaker', file=filepath, line=line_num,
                    quality=quality, details={'library': pattern_name}
                ))
                
                if quality != 'CORRECT':
                    issues.extend(self._generate_cb_issues(filepath, line_num, context, quality, lang_patterns))
        
        # Check for custom circuit breaker implementations (state machine pattern)
        if self._is_circuit_breaker_state_machine(content):
            # Find where the states are defined
            state_match = re.search(r'\b(OPEN|CLOSED|HALF_OPEN)\s*=', content)
            if state_match:
                line_num = content[:state_match.start()].count('\n') + 1
                lines = content.splitlines()
                start = max(0, line_num - 10)
                end = min(len(lines), line_num + 50)
                context = '\n'.join(lines[start:end])
                
                quality = self._evaluate_cb_quality(context, lang_patterns)
                
                patterns.append(PatternDetection(
                    pattern_type='circuit_breaker', file=filepath, line=line_num,
                    quality=quality, details={'library': 'custom_state_machine'}
                ))
                
                if quality != 'CORRECT':
                    issues.extend(self._generate_cb_issues(filepath, line_num, context, quality, lang_patterns))
        
        return patterns, issues
        
        return patterns, issues
    
    def _evaluate_cb_quality(self, context: str, lang_patterns: dict) -> str:
        has_fallback = any(
            lang_patterns.get(p, re.compile(r'$^')).search(context)
            for p in ['cb_fallback', 'fallback']
        )
        has_metrics = any(
            lang_patterns.get(p, re.compile(r'$^')).search(context)
            for p in ['cb_metrics', 'cb_listener', 'cb_events', 'cb_on_state']
        )
        
        if has_fallback and has_metrics:
            return 'CORRECT'
        elif has_fallback or has_metrics:
            return 'PARTIAL'
        else:
            return 'CARGO_CULT'
    
    def _generate_cb_issues(self, filepath: str, line: int, context: str, quality: str, lang_patterns: dict) -> list:
        issues = []
        has_metrics = any(
            lang_patterns.get(p, re.compile(r'$^')).search(context)
            for p in ['cb_metrics', 'cb_listener', 'cb_events', 'cb_on_state']
        )
        has_fallback = any(
            lang_patterns.get(p, re.compile(r'$^')).search(context)
            for p in ['cb_fallback', 'fallback']
        )
        
        if not has_metrics:
            issues.append(CircuitBreakerIssue(
                file=filepath, line=line, issue_type='invisible', severity='HIGH',
                description='Circuit breaker without metrics/logging - state changes are invisible'
            ))
        if not has_fallback:
            issues.append(CircuitBreakerIssue(
                file=filepath, line=line, issue_type='no_fallback', severity='MEDIUM',
                description='Circuit breaker without fallback'
            ))
        return issues


class ExceptionDetector:
    EXCEPTION_PATTERNS = {
        'python': {
            # Bare except - always bad
            'bare_except': re.compile(r'except\s*:'),
            # Broad except (Exception or BaseException)
            'broad_except': re.compile(r'except\s+(?:Exception|BaseException)\s*(?:as\s+\w+)?:'),
            # Bare except with pass - always bad
            'bare_except_pass': re.compile(r'except\s*:\s*\n\s*pass\b'),
            # Broad except with pass - bad (swallowing all errors)
            'broad_except_pass': re.compile(r'except\s+(?:Exception|BaseException)\s*(?:as\s+\w+)?:\s*\n\s*pass\b'),
            # Bare except with continue - always bad
            'bare_except_continue': re.compile(r'except\s*:\s*\n\s*continue\b'),
            # Broad except with continue - bad
            'broad_except_continue': re.compile(r'except\s+(?:Exception|BaseException)\s*(?:as\s+\w+)?:\s*\n\s*continue\b'),
        },
    }
    
    def _is_exception_mapper(self, context: str) -> bool:
        """
        Check if this is an exception mapper pattern (catch, transform, re-raise).
        These are legitimate patterns, not cargo cult.
        """
        # Look for re-raise patterns
        has_reraise = bool(re.search(r'\braise\b.*\bfrom\b|\braise\s+\w+\(', context))
        # Look for exception mapping logic
        has_mapping = bool(re.search(r'mapped.*exc|exc.*map|for.*exc.*in|isinstance\(exc', context, re.IGNORECASE))
        return has_reraise or has_mapping
    
    def _is_specific_exception(self, match_text: str) -> bool:
        """
        Check if the except clause catches a specific exception (not Exception/BaseException).
        """
        # Extract the exception type from the match
        specific_match = re.search(r'except\s+(\w+)', match_text)
        if not specific_match:
            return False  # bare except
        exc_type = specific_match.group(1)
        # These are considered "broad" catches
        broad_types = {'Exception', 'BaseException'}
        return exc_type not in broad_types
    
    def detect(self, content: str, filepath: str, language: str) -> tuple[list, list]:
        patterns = []
        issues = []
        
        lang_patterns = self.EXCEPTION_PATTERNS.get(language, self.EXCEPTION_PATTERNS.get('python', {}))
        
        # Track which lines we've already flagged to avoid duplicates
        flagged_lines = set()
        
        # Check for swallowing patterns first (most severe)
        for pattern_name in ['bare_except_pass', 'broad_except_pass', 'bare_except_continue', 'broad_except_continue']:
            pattern = lang_patterns.get(pattern_name)
            if not pattern:
                continue
            
            for match in pattern.finditer(content):
                if should_skip_match(content, match.start()):
                    continue
                    
                line_num = content[:match.start()].count('\n') + 1
                if line_num in flagged_lines:
                    continue
                flagged_lines.add(line_num)
                
                lines = content.splitlines()
                start = max(0, line_num - 1)
                end = min(len(lines), line_num + 5)
                context = '\n'.join(lines[start:end])
                
                has_logging = bool(re.search(r'log|logger|logging|print', context, re.IGNORECASE))
                
                if has_logging:
                    quality = 'PARTIAL'
                else:
                    quality = 'CARGO_CULT'
                
                base_pattern = 'bare_except' if 'bare' in pattern_name else 'broad_except'
                patterns.append(PatternDetection(
                    pattern_type='exception_handling', file=filepath, line=line_num,
                    quality=quality, details={'pattern': pattern_name}
                ))
                
                if quality == 'CARGO_CULT':
                    issues.append(ExceptionIssue(
                        file=filepath, line=line_num,
                        issue_type='swallow',
                        severity='HIGH',
                        description='Exception swallowed silently - errors invisible'
                    ))
        
        # Check for bare/broad except (without pass/continue)
        for pattern_name in ['bare_except', 'broad_except']:
            pattern = lang_patterns.get(pattern_name)
            if not pattern:
                continue
            
            for match in pattern.finditer(content):
                if should_skip_match(content, match.start()):
                    continue
                    
                line_num = content[:match.start()].count('\n') + 1
                if line_num in flagged_lines:
                    continue
                flagged_lines.add(line_num)
                
                lines = content.splitlines()
                start = max(0, line_num - 3)
                end = min(len(lines), line_num + 10)
                context = '\n'.join(lines[start:end])
                
                # Check if this is an exception mapper (legitimate pattern)
                if self._is_exception_mapper(context):
                    quality = 'CORRECT'
                    continue  # Don't flag exception mappers
                
                has_logging = bool(re.search(r'log|logger|logging|print', context, re.IGNORECASE))
                has_raise = bool(re.search(r'\braise\b', context))
                
                if has_logging or has_raise:
                    quality = 'PARTIAL'
                else:
                    quality = 'CARGO_CULT'
                
                patterns.append(PatternDetection(
                    pattern_type='exception_handling', file=filepath, line=line_num,
                    quality=quality, details={'pattern': pattern_name}
                ))
                
                if quality == 'CARGO_CULT':
                    desc = {
                        'bare_except': 'Bare except catches everything including KeyboardInterrupt',
                        'broad_except': 'Catching Exception hides specific error types',
                    }.get(pattern_name, 'Problematic exception handling')
                    
                    issues.append(ExceptionIssue(
                        file=filepath, line=line_num,
                        issue_type='broad_catch',
                        severity='MEDIUM',
                        description=desc
                    ))
        
        return patterns, issues


class LibraryDetector:
    LIBRARIES = {
        'python': {
            'tenacity': re.compile(r'from\s+tenacity|import\s+tenacity'),
            'retrying': re.compile(r'from\s+retrying|import\s+retrying'),
            'backoff': re.compile(r'from\s+backoff|import\s+backoff'),
            'pybreaker': re.compile(r'from\s+pybreaker|import\s+pybreaker'),
            'circuitbreaker': re.compile(r'from\s+circuitbreaker|import\s+circuitbreaker'),
        },
    }
    
    def detect(self, content: str, language: str) -> list:
        found = []
        lang_libs = self.LIBRARIES.get(language, {})
        for lib_name, pattern in lang_libs.items():
            if pattern.search(content):
                found.append(lib_name)
        return found


# =============================================================================
# MAIN ANALYZER
# =============================================================================

class Hubris:
    LANGUAGE_EXTENSIONS = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'javascript',
        '.go': 'go',
        '.java': 'java',
    }
    
    def __init__(self, codebase_path: str):
        self.codebase_path = Path(codebase_path)
        self.retry_detector = RetryDetector()
        self.timeout_detector = TimeoutDetector()
        self.cb_detector = CircuitBreakerDetector()
        self.exception_detector = ExceptionDetector()
        self.library_detector = LibraryDetector()
    
    def analyze(self) -> HubrisReport:
        report = HubrisReport(
            codebase_path=str(self.codebase_path),
            timestamp=datetime.now().isoformat()
        )
        
        print(f"[HUBRIS v3] Scanning for resilience theater in {self.codebase_path}...")
        
        all_libraries = set()
        
        for ext, language in self.LANGUAGE_EXTENSIONS.items():
            for filepath in self.codebase_path.rglob(f'*{ext}'):
                if any(skip in str(filepath) for skip in [
                    'node_modules', 'venv', '.venv', '__pycache__',
                    '.git', 'dist', 'build', 'vendor', 'test', 'tests',
                ]):
                    continue
                
                try:
                    content = filepath.read_text(encoding='utf-8', errors='ignore')
                    rel_path = str(filepath.relative_to(self.codebase_path))
                    
                    libs = self.library_detector.detect(content, language)
                    all_libraries.update(libs)
                    
                    patterns, issues = self.retry_detector.detect(content, rel_path, language)
                    report.patterns.extend(patterns)
                    report.retry_issues.extend(issues)
                    
                    patterns, issues = self.timeout_detector.detect(content, rel_path, language)
                    report.patterns.extend(patterns)
                    report.timeout_issues.extend(issues)
                    
                    patterns, issues = self.cb_detector.detect(content, rel_path, language)
                    report.patterns.extend(patterns)
                    report.circuit_breaker_issues.extend(issues)
                    
                    patterns, issues = self.exception_detector.detect(content, rel_path, language)
                    report.patterns.extend(patterns)
                    report.exception_issues.extend(issues)
                    
                except Exception as e:
                    print(f"  Warning: Could not analyze {filepath}: {e}")
        
        report.resilience_libraries = sorted(all_libraries)
        report.library_count = len(all_libraries)
        
        self._calculate_statistics(report)
        self._determine_quadrant(report)
        self._generate_recommendations(report)
        
        print(f"  Patterns detected: {report.patterns_detected}")
        print(f"  Correctly implemented: {report.patterns_correct}")
        print(f"  Theater ratio: {report.theater_ratio:.2f}")
        print(f"  Verdict: {report.quadrant}")
        
        return report
    
    def _calculate_statistics(self, report: HubrisReport):
        report.patterns_detected = len(report.patterns)
        report.patterns_correct = sum(1 for p in report.patterns if p.quality == 'CORRECT')
        report.patterns_partial = sum(1 for p in report.patterns if p.quality == 'PARTIAL')
        report.patterns_cargo_cult = sum(1 for p in report.patterns if p.quality == 'CARGO_CULT')
        
        # Theater ratio: patterns_detected / (correct + partial)
        # PARTIAL is acceptable - it means there's logging even if exception is broad
        acceptable = report.patterns_correct + report.patterns_partial
        if acceptable > 0:
            report.theater_ratio = report.patterns_detected / acceptable
        elif report.patterns_detected > 0:
            report.theater_ratio = float('inf')
        else:
            report.theater_ratio = 1.0
        
        all_issues = (
            report.retry_issues + report.timeout_issues + 
            report.circuit_breaker_issues + report.exception_issues
        )
        
        report.total_issues = len(all_issues)
        report.high_severity_count = sum(1 for i in all_issues if getattr(i, 'severity', '') == 'HIGH')
        report.medium_severity_count = sum(1 for i in all_issues if getattr(i, 'severity', '') == 'MEDIUM')
        report.low_severity_count = sum(1 for i in all_issues if getattr(i, 'severity', '') == 'LOW')
    
    def _determine_quadrant(self, report: HubrisReport):
        complexity = report.patterns_detected
        # Quality includes PARTIAL as acceptable
        acceptable = report.patterns_correct + report.patterns_partial
        quality = acceptable / max(1, report.patterns_detected)
        
        low_complexity = complexity < 5
        high_quality = quality >= 0.6
        
        if low_complexity and high_quality:
            report.quadrant = "SIMPLE"
            report.verdict = "Low complexity, correctly implemented. Clean."
            report.risk_level = "LOW"
        elif not low_complexity and high_quality:
            report.quadrant = "BATTLE_HARDENED"
            report.verdict = "High complexity, correctly implemented. Genuinely resilient."
            report.risk_level = "LOW"
        elif low_complexity and not high_quality:
            report.quadrant = "CARGO_CULT"
            report.verdict = "Few patterns, implemented incorrectly."
            report.risk_level = "MEDIUM"
        else:
            report.quadrant = "CARGO_CULT"
            report.verdict = "Many patterns, implemented incorrectly. High risk."
            report.risk_level = "CRITICAL"
    
    def _generate_recommendations(self, report: HubrisReport):
        if report.high_severity_count > 0:
            report.recommendations.append({
                'priority': 'CRITICAL',
                'category': 'High Severity Issues',
                'message': f'{report.high_severity_count} high-severity issues found'
            })
        
        swallowed = [i for i in report.exception_issues if i.issue_type == 'swallow']
        if swallowed:
            report.recommendations.append({
                'priority': 'HIGH',
                'category': 'Swallowed Exceptions',
                'message': f'{len(swallowed)} locations silently ignore exceptions'
            })
    
    def save_report(self, report: HubrisReport, output_path: str):
        data = {
            'codebase_path': report.codebase_path,
            'timestamp': report.timestamp,
            'quadrant': report.quadrant,
            'verdict': report.verdict,
            'risk_level': report.risk_level,
            'theater_ratio': report.theater_ratio if report.theater_ratio != float('inf') else 'infinity',
            'patterns_detected': report.patterns_detected,
            'patterns_correct': report.patterns_correct,
            'patterns_partial': report.patterns_partial,
            'patterns_cargo_cult': report.patterns_cargo_cult,
            'total_issues': report.total_issues,
            'high_severity_count': report.high_severity_count,
            'medium_severity_count': report.medium_severity_count,
            'low_severity_count': report.low_severity_count,
            'resilience_libraries': report.resilience_libraries,
            'recommendations': report.recommendations,
            'issues': {
                'high': [],
                'medium': [],
                'low': []
            },
            'patterns': []
        }
        
        # Collect all issues with details
        all_issues = (
            [(i, 'exception') for i in report.exception_issues] +
            [(i, 'retry') for i in report.retry_issues] +
            [(i, 'circuit_breaker') for i in report.circuit_breaker_issues] +
            [(i, 'timeout') for i in report.timeout_issues]
        )
        
        for issue, issue_type in all_issues:
            issue_data = {
                'file': issue.file,
                'line': issue.line,
                'type': issue_type,
                'issue_type': issue.issue_type,
                'severity': issue.severity,
                'description': issue.description
            }
            if issue.severity == 'HIGH':
                data['issues']['high'].append(issue_data)
            elif issue.severity == 'MEDIUM':
                data['issues']['medium'].append(issue_data)
            else:
                data['issues']['low'].append(issue_data)
        
        # Include pattern details
        for p in report.patterns:
            data['patterns'].append({
                'file': p.file,
                'line': p.line,
                'pattern_type': p.pattern_type,
                'quality': p.quality,
                'details': p.details
            })
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)


# =============================================================================
# URL CLONING SUPPORT
# =============================================================================

def is_github_url(path: str) -> bool:
    """Check if the path looks like a GitHub URL."""
    import re
    github_patterns = [
        r'^https?://github\.com/',
        r'^git@github\.com:',
        r'^[\w\-]+/[\w\-\.]+$',  # owner/repo format
    ]
    return any(re.match(p, path) for p in github_patterns)


def clone_github_repo(url: str) -> tuple[str, str, str]:
    """
    Clone a GitHub repository and return (local_path, repo_name, temp_dir).
    
    Accepts formats:
    - https://github.com/owner/repo
    - https://github.com/owner/repo.git
    - git@github.com:owner/repo.git
    - owner/repo (assumes GitHub)
    
    Returns:
        (clone_path, repo_name, temp_dir) - temp_dir is the parent to clean up
    """
    import subprocess
    import tempfile
    import re
    from urllib.parse import urlparse
    
    original_url = url
    
    # Handle short form: owner/repo
    if re.match(r'^[\w\-]+/[\w\-\.]+$', url):
        url = f'https://github.com/{url}'
    
    # Handle SSH format
    if url.startswith('git@'):
        match = re.match(r'git@github\.com:(.+?)(?:\.git)?$', url)
        if match:
            url = f'https://github.com/{match.group(1)}'
    
    # Extract repo name
    parsed = urlparse(url)
    path_parts = parsed.path.strip('/').replace('.git', '').split('/')
    
    if len(path_parts) >= 2:
        owner = path_parts[-2]
        repo = path_parts[-1]
        repo_name = f"{owner}_{repo}"
    else:
        repo_name = path_parts[-1] if path_parts else 'unknown_repo'
    
    # Create temp directory
    temp_dir = tempfile.mkdtemp(prefix=f'hubris_{repo_name}_')
    clone_path = Path(temp_dir) / repo_name
    
    print(f"[CLONE] Cloning {url}...")
    print(f"        Target: {clone_path}")
    
    try:
        result = subprocess.run(
            ['git', 'clone', '--depth', '1', url, str(clone_path)],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode != 0:
            error_msg = result.stderr.strip()
            raise RuntimeError(f"Git clone failed: {error_msg}")
        
        print("        Done!")
        return str(clone_path), repo_name, temp_dir
        
    except subprocess.TimeoutExpired:
        raise RuntimeError("Git clone timed out after 120 seconds")
    except FileNotFoundError:
        raise RuntimeError("Git is not installed or not in PATH")


def main():
    import argparse
    import shutil
    
    parser = argparse.ArgumentParser(
        description="Hubris v3 - Resilience Theater Detector",
        epilog="Examples:\n"
               "  python hubris.py .                           # Local directory\n"
               "  python hubris.py /path/to/repo               # Local path\n"
               "  python hubris.py pallets/flask               # GitHub shorthand\n"
               "  python hubris.py https://github.com/owner/repo  # Full URL\n",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('path', help='Path to codebase or GitHub URL (owner/repo or full URL)')
    parser.add_argument('-o', '--output', help='Output JSON path')
    parser.add_argument('--html', help='Output HTML report path')
    parser.add_argument('--keep', action='store_true', help='Keep cloned repo after analysis')
    args = parser.parse_args()
    
    # Check if it's a URL or local path
    codebase_path = args.path
    temp_dir = None
    repo_name = None
    
    if is_github_url(args.path):
        # Extract repo name for local check
        path_parts = args.path.replace('https://github.com/', '').replace('http://github.com/', '').split('/')
        if len(path_parts) >= 2:
            # owner/repo format - check for owner_repo directory
            owner = path_parts[0] if path_parts[0] not in ['https:', 'http:', ''] else path_parts[-2]
            repo = path_parts[-1].replace('.git', '')
            local_check = Path(f"{owner}_{repo}")
            local_check_alt = Path(repo)
        else:
            repo = path_parts[-1].replace('.git', '')
            local_check = Path(repo)
            local_check_alt = None
        
        # Only use local if it looks like a real repo clone (has .git folder)
        if local_check.exists() and local_check.is_dir() and (local_check / '.git').exists():
            print(f"[INFO] Found local clone: {local_check}")
            codebase_path = str(local_check)
        elif local_check_alt and local_check_alt.exists() and local_check_alt.is_dir() and (local_check_alt / '.git').exists():
            print(f"[INFO] Found local clone: {local_check_alt}")
            codebase_path = str(local_check_alt)
        else:
            codebase_path, repo_name, temp_dir = clone_github_repo(args.path)
    
    try:
        hubris = Hubris(codebase_path)
        report = hubris.analyze()
        
        print("\n" + "="*70)
        print("HUBRIS v3 - RESILIENCE THEATER REPORT")
        print("="*70)
        
        emoji = {'SIMPLE': '🟢', 'BATTLE_HARDENED': '🔵', 'CARGO_CULT': '🔴'}.get(report.quadrant, '⚪')
        print(f"\n{emoji} Quadrant: {report.quadrant}")
        print(f"Risk Level: {report.risk_level}")
        print(f"Theater Ratio: {report.theater_ratio:.2f}")
        print(f"\n{report.verdict}")
        
        if report.total_issues > 0:
            print(f"\nIssues: {report.high_severity_count} HIGH, {report.medium_severity_count} MEDIUM")
        
        # Auto-generate output filename for GitHub repos
        if args.output:
            output_path = args.output
        elif repo_name:
            output_path = f"hubris_{repo_name}.json"
        else:
            output_path = None
        
        if output_path:
            hubris.save_report(report, output_path)
            print(f"\nJSON: {output_path}")
    
    finally:
        # Cleanup temp directory unless --keep
        if temp_dir and not args.keep:
            print(f"\n[CLEANUP] Removing {temp_dir}")
            shutil.rmtree(temp_dir, ignore_errors=True)
        elif temp_dir and args.keep:
            print(f"\n[KEEP] Repo preserved at: {codebase_path}")


if __name__ == '__main__':
    main()
