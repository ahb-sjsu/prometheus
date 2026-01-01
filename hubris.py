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
class GitHubMetadata:
    """Metadata fetched from GitHub API."""
    name: str = ""
    full_name: str = ""
    description: str = ""
    stars: int = 0
    forks: int = 0
    language: str = ""
    topics: list = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""
    open_issues: int = 0
    license: str = ""
    url: str = ""


def fetch_github_metadata(repo_path: str) -> GitHubMetadata:
    """
    Fetch metadata from GitHub API for a repo.
    repo_path can be 'owner/repo' or full URL.
    """
    import urllib.request
    import json as json_lib
    
    # Extract owner/repo from various formats
    if 'github.com' in repo_path:
        # https://github.com/owner/repo or git@github.com:owner/repo
        match = re.search(r'github\.com[/:]([^/]+)/([^/\.]+)', repo_path)
        if match:
            owner, repo = match.groups()
        else:
            return GitHubMetadata()
    elif '/' in repo_path and not repo_path.startswith('/'):
        # owner/repo format
        parts = repo_path.split('/')
        owner, repo = parts[0], parts[1].replace('.git', '')
    else:
        return GitHubMetadata()
    
    try:
        api_url = f"https://api.github.com/repos/{owner}/{repo}"
        req = urllib.request.Request(api_url, headers={'User-Agent': 'Hubris/3.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json_lib.loads(response.read().decode())
            
            return GitHubMetadata(
                name=data.get('name', ''),
                full_name=data.get('full_name', ''),
                description=data.get('description', '') or '',
                stars=data.get('stargazers_count', 0),
                forks=data.get('forks_count', 0),
                language=data.get('language', '') or '',
                topics=data.get('topics', []),
                created_at=data.get('created_at', ''),
                updated_at=data.get('updated_at', ''),
                open_issues=data.get('open_issues_count', 0),
                license=data.get('license', {}).get('spdx_id', '') if data.get('license') else '',
                url=data.get('html_url', '')
            )
    except Exception as e:
        # Silently fail - metadata is optional
        return GitHubMetadata(name=repo, full_name=f"{owner}/{repo}")


@dataclass
class HubrisReport:
    codebase_path: str
    timestamp: str
    
    # GitHub metadata (optional)
    github: GitHubMetadata = field(default_factory=GitHubMetadata)
    
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
    
    def save_html_report(self, report: HubrisReport, output_path: str, comparison_reports: list = None):
        """Generate an HTML report with visual quadrant chart."""
        
        # For single report or as base for comparison
        reports_data = []
        
        if comparison_reports:
            reports_data = comparison_reports
        else:
            reports_data = [report]
        
        # Generate points for all reports
        points_html = ""
        legend_html = ""
        colors = ['#3b82f6', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16']
        
        for idx, r in enumerate(reports_data):
            # X-axis: Pattern count (0-100 scale, log-ish)
            pattern_count = r.patterns_detected
            x = min(95, max(5, (pattern_count / 50) * 100)) if pattern_count > 0 else 5
            
            # Y-axis: Quality (% correct + partial)
            acceptable = r.patterns_correct + r.patterns_partial
            y = (acceptable / max(1, r.patterns_detected)) * 100 if r.patterns_detected > 0 else 50
            
            color = colors[idx % len(colors)]
            name = r.github.full_name if r.github.full_name else Path(r.codebase_path).name
            
            # Quadrant-based color if single report
            if len(reports_data) == 1:
                quadrant_colors = {
                    'SIMPLE': '#22c55e',
                    'BATTLE_HARDENED': '#3b82f6', 
                    'CARGO_CULT': '#ef4444',
                }
                color = quadrant_colors.get(r.quadrant, '#6b7280')
            
            points_html += f'''
                <div class="point" style="left: {x}%; bottom: {y}%; background: {color};" title="{name}: {r.quadrant}">
                    {'<span class="point-label">' + name.split('/')[-1][:10] + '</span>' if len(reports_data) > 1 else ''}
                </div>'''
            
            if len(reports_data) > 1:
                stars_str = f" ⭐{r.github.stars:,}" if r.github.stars else ""
                legend_html += f'''
                    <div class="legend-item">
                        <span class="legend-dot" style="background: {color};"></span>
                        <span class="legend-name">{name}{stars_str}</span>
                        <span class="legend-quadrant" style="color: {color};">{r.quadrant}</span>
                    </div>'''
        
        # Use first report for main stats (or primary report)
        main_report = report
        
        # Determine color for single report mode
        quadrant_colors = {
            'SIMPLE': '#22c55e',
            'BATTLE_HARDENED': '#3b82f6',
            'CARGO_CULT': '#ef4444',
        }
        color = quadrant_colors.get(main_report.quadrant, '#6b7280')
        
        # Generate issues table rows
        all_issues = (
            [(i, 'exception') for i in main_report.exception_issues] +
            [(i, 'retry') for i in main_report.retry_issues] +
            [(i, 'circuit_breaker') for i in main_report.circuit_breaker_issues] +
            [(i, 'timeout') for i in main_report.timeout_issues]
        )
        
        issues_rows = ""
        for issue, issue_type in sorted(all_issues, key=lambda x: (0 if x[0].severity == 'HIGH' else 1 if x[0].severity == 'MEDIUM' else 2, x[0].file)):
            severity_color = {'HIGH': '#ef4444', 'MEDIUM': '#f59e0b', 'LOW': '#6b7280'}[issue.severity]
            issues_rows += f"""
            <tr>
                <td><span style="color: {severity_color}; font-weight: bold;">{issue.severity}</span></td>
                <td><code>{issue.file}:{issue.line}</code></td>
                <td>{issue_type}</td>
                <td>{issue.description}</td>
            </tr>"""
        
        # Generate patterns table rows
        patterns_rows = ""
        for p in sorted(main_report.patterns, key=lambda x: (0 if x.quality == 'CARGO_CULT' else 1 if x.quality == 'PARTIAL' else 2, x.file)):
            quality_color = {'CORRECT': '#22c55e', 'PARTIAL': '#f59e0b', 'CARGO_CULT': '#ef4444'}[p.quality]
            patterns_rows += f"""
            <tr>
                <td><span style="color: {quality_color}; font-weight: bold;">{p.quality}</span></td>
                <td><code>{p.file}:{p.line}</code></td>
                <td>{p.pattern_type}</td>
                <td><code>{p.details}</code></td>
            </tr>"""
        
        # Comparison table if multiple reports
        comparison_table = ""
        if len(reports_data) > 1:
            comparison_rows = ""
            for r in sorted(reports_data, key=lambda x: (-x.github.stars if x.github.stars else 0, x.theater_ratio)):
                q_color = quadrant_colors.get(r.quadrant, '#6b7280')
                name = r.github.full_name if r.github.full_name else Path(r.codebase_path).name
                stars = f"⭐ {r.github.stars:,}" if r.github.stars else "-"
                lang = r.github.language or "-"
                comparison_rows += f"""
                <tr>
                    <td>
                        <strong>{name}</strong>
                        {f'<br/><small style="color: #64748b;">{r.github.description[:50]}...</small>' if r.github.description else ''}
                    </td>
                    <td>{stars}</td>
                    <td>{lang}</td>
                    <td><span style="color: {q_color}; font-weight: bold;">{r.quadrant}</span></td>
                    <td>{r.theater_ratio:.2f}</td>
                    <td>{r.patterns_detected}</td>
                    <td style="color: #ef4444;">{r.high_severity_count}</td>
                    <td style="color: #f59e0b;">{r.medium_severity_count}</td>
                </tr>"""
            comparison_table = f'''
            <h2>Comparison ({len(reports_data)} repositories)</h2>
            <table>
                <thead>
                    <tr>
                        <th>Repository</th>
                        <th>Stars</th>
                        <th>Language</th>
                        <th>Quadrant</th>
                        <th>Theater Ratio</th>
                        <th>Patterns</th>
                        <th>HIGH</th>
                        <th>MEDIUM</th>
                    </tr>
                </thead>
                <tbody>{comparison_rows}</tbody>
            </table>'''
        
        # Build title with metadata
        if len(reports_data) > 1:
            title = "Comparison"
            subtitle = f"{len(reports_data)} repositories analyzed"
        else:
            gh = main_report.github
            if gh.full_name:
                title = gh.full_name
                meta_parts = []
                if gh.stars:
                    meta_parts.append(f"⭐ {gh.stars:,}")
                if gh.language:
                    meta_parts.append(gh.language)
                if gh.license:
                    meta_parts.append(gh.license)
                subtitle = " • ".join(meta_parts) if meta_parts else ""
                if gh.description:
                    subtitle += f"<br/><span style='color: #94a3b8;'>{gh.description}</span>"
            else:
                title = Path(main_report.codebase_path).name
                subtitle = main_report.timestamp[:19]
        
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hubris Report - {title}</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0f172a; 
            color: #e2e8f0;
            padding: 2rem;
            line-height: 1.6;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        h1 {{ color: #f8fafc; margin-bottom: 0.5rem; font-size: 2rem; }}
        h2 {{ color: #94a3b8; margin: 2rem 0 1rem; font-size: 1.25rem; border-bottom: 1px solid #334155; padding-bottom: 0.5rem; }}
        .subtitle {{ color: #64748b; margin-bottom: 2rem; }}
        
        .grid {{ display: grid; grid-template-columns: 450px 1fr; gap: 2rem; margin-bottom: 2rem; }}
        @media (max-width: 900px) {{ .grid {{ grid-template-columns: 1fr; }} }}
        
        /* Quadrant Chart */
        .quadrant-container {{ 
            background: #1e293b; 
            border-radius: 12px; 
            padding: 1.5rem;
            border: 1px solid #334155;
        }}
        .quadrant {{
            position: relative;
            width: 400px;
            height: 400px;
            margin: 0 auto;
        }}
        .quadrant-bg {{
            position: absolute;
            width: 50%;
            height: 50%;
        }}
        .q-simple {{ top: 0; left: 0; background: rgba(34, 197, 94, 0.15); border-radius: 12px 0 0 0; }}
        .q-battle {{ top: 0; right: 0; background: rgba(59, 130, 246, 0.15); border-radius: 0 12px 0 0; }}
        .q-cargo-low {{ bottom: 0; left: 0; background: rgba(239, 68, 68, 0.1); border-radius: 0 0 0 12px; }}
        .q-cargo-high {{ bottom: 0; right: 0; background: rgba(239, 68, 68, 0.2); border-radius: 0 0 12px 0; }}
        
        .quadrant-label {{
            position: absolute;
            font-size: 0.75rem;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 600;
        }}
        .label-simple {{ top: 10px; left: 10px; color: #22c55e; }}
        .label-battle {{ top: 10px; right: 10px; color: #3b82f6; }}
        .label-cargo-low {{ bottom: 30px; left: 10px; color: #ef4444; opacity: 0.7; }}
        .label-cargo-high {{ bottom: 30px; right: 10px; color: #ef4444; }}
        
        .axis-label {{
            position: absolute;
            font-size: 0.7rem;
            color: #94a3b8;
            text-transform: uppercase;
            font-weight: 500;
        }}
        .axis-x {{ bottom: -30px; left: 50%; transform: translateX(-50%); }}
        .axis-y {{ top: 50%; left: -45px; transform: rotate(-90deg) translateX(-50%); transform-origin: left; white-space: nowrap; }}
        
        .axis-tick {{
            position: absolute;
            font-size: 0.6rem;
            color: #475569;
        }}
        .tick-x-0 {{ bottom: -15px; left: 0; }}
        .tick-x-100 {{ bottom: -15px; right: 0; }}
        .tick-y-0 {{ left: -20px; bottom: 0; }}
        .tick-y-100 {{ left: -20px; top: 0; }}
        
        .point {{
            position: absolute;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            border: 3px solid white;
            box-shadow: 0 0 20px currentColor;
            transform: translate(-50%, 50%);
            z-index: 10;
            cursor: pointer;
            transition: transform 0.2s;
        }}
        .point:hover {{ transform: translate(-50%, 50%) scale(1.3); }}
        .point-label {{
            position: absolute;
            top: -20px;
            left: 50%;
            transform: translateX(-50%);
            font-size: 0.6rem;
            color: white;
            white-space: nowrap;
            background: #0f172a;
            padding: 2px 6px;
            border-radius: 4px;
        }}
        
        .crosshair {{
            position: absolute;
            background: #475569;
        }}
        .crosshair-h {{ width: 100%; height: 1px; top: 50%; }}
        .crosshair-v {{ height: 100%; width: 1px; left: 50%; }}
        
        .legend {{
            margin-top: 1rem;
            display: flex;
            flex-wrap: wrap;
            gap: 0.75rem;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.8rem;
        }}
        .legend-dot {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
        }}
        .legend-name {{ color: #e2e8f0; }}
        .legend-quadrant {{ font-size: 0.7rem; }}
        
        /* Stats */
        .stats-container {{
            background: #1e293b;
            border-radius: 12px;
            padding: 1.5rem;
            border: 1px solid #334155;
        }}
        .stat-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; }}
        .stat {{
            background: #0f172a;
            padding: 1rem;
            border-radius: 8px;
            text-align: center;
        }}
        .stat-value {{ font-size: 2rem; font-weight: bold; color: #f8fafc; }}
        .stat-label {{ font-size: 0.75rem; color: #64748b; text-transform: uppercase; }}
        .stat-high .stat-value {{ color: #ef4444; }}
        .stat-medium .stat-value {{ color: #f59e0b; }}
        .stat-good .stat-value {{ color: #22c55e; }}
        .stat-blue .stat-value {{ color: #3b82f6; }}
        
        .verdict {{
            margin-top: 1.5rem;
            padding: 1rem;
            background: {color}22;
            border-left: 4px solid {color};
            border-radius: 0 8px 8px 0;
        }}
        .verdict-title {{ font-size: 1.5rem; font-weight: bold; color: {color}; }}
        .verdict-text {{ color: #94a3b8; margin-top: 0.5rem; }}
        
        /* Tables */
        table {{ 
            width: 100%; 
            border-collapse: collapse; 
            background: #1e293b;
            border-radius: 8px;
            overflow: hidden;
        }}
        th, td {{ 
            padding: 0.75rem 1rem; 
            text-align: left; 
            border-bottom: 1px solid #334155;
        }}
        th {{ 
            background: #0f172a; 
            color: #94a3b8; 
            font-weight: 500;
            text-transform: uppercase;
            font-size: 0.7rem;
            letter-spacing: 0.05em;
        }}
        tr:hover {{ background: #334155; }}
        code {{ 
            font-family: 'JetBrains Mono', 'Fira Code', monospace;
            font-size: 0.85rem;
            color: #7dd3fc;
        }}
        
        .empty {{ color: #64748b; font-style: italic; padding: 2rem; text-align: center; }}
        
        .repo-header {{
            margin-bottom: 2rem;
        }}
        .repo-title {{
            font-size: 1.75rem;
            color: #f8fafc;
            margin-bottom: 0.5rem;
        }}
        .repo-title a {{
            color: #f8fafc;
            text-decoration: none;
        }}
        .repo-title a:hover {{
            color: #7dd3fc;
        }}
        .repo-meta {{
            color: #94a3b8;
            font-size: 0.9rem;
        }}
        .repo-meta .stars {{
            color: #fbbf24;
        }}
        .repo-description {{
            color: #64748b;
            margin-top: 0.5rem;
            font-size: 0.9rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎭 Hubris v3 - Resilience Theater Analysis</h1>
        <div class="repo-header">
            <div class="repo-title">
                {f'<a href="{main_report.github.url}" target="_blank">{title}</a>' if main_report.github.url else title}
            </div>
            <div class="repo-meta">{subtitle}</div>
        </div>
        
        <div class="grid">
            <div class="quadrant-container">
                <div class="quadrant">
                    <div class="quadrant-bg q-simple"></div>
                    <div class="quadrant-bg q-battle"></div>
                    <div class="quadrant-bg q-cargo-low"></div>
                    <div class="quadrant-bg q-cargo-high"></div>
                    
                    <div class="crosshair crosshair-h"></div>
                    <div class="crosshair crosshair-v"></div>
                    
                    <span class="quadrant-label label-simple">Simple<br/>Clean</span>
                    <span class="quadrant-label label-battle">Battle<br/>Hardened</span>
                    <span class="quadrant-label label-cargo-low">Cargo<br/>Cult</span>
                    <span class="quadrant-label label-cargo-high">Cargo Cult<br/>⚠️ Critical</span>
                    
                    <span class="axis-label axis-x">Patterns Detected →</span>
                    <span class="axis-label axis-y">Pattern Quality (% Correct) →</span>
                    
                    <span class="axis-tick tick-x-0">0</span>
                    <span class="axis-tick tick-x-100">50+</span>
                    <span class="axis-tick tick-y-0">0%</span>
                    <span class="axis-tick tick-y-100">100%</span>
                    
                    {points_html}
                </div>
                {f'<div class="legend">{legend_html}</div>' if legend_html else ''}
            </div>
            
            <div class="stats-container">
                <div class="stat-grid">
                    <div class="stat stat-blue">
                        <div class="stat-value">{main_report.patterns_detected}</div>
                        <div class="stat-label">Patterns Detected</div>
                    </div>
                    <div class="stat {'stat-good' if main_report.theater_ratio <= 1.5 else 'stat-high'}">
                        <div class="stat-value">{main_report.theater_ratio:.2f}</div>
                        <div class="stat-label">Theater Ratio</div>
                    </div>
                    <div class="stat stat-high">
                        <div class="stat-value">{main_report.high_severity_count}</div>
                        <div class="stat-label">High Severity</div>
                    </div>
                    <div class="stat stat-medium">
                        <div class="stat-value">{main_report.medium_severity_count}</div>
                        <div class="stat-label">Medium Severity</div>
                    </div>
                    <div class="stat stat-good">
                        <div class="stat-value">{main_report.patterns_correct}</div>
                        <div class="stat-label">Correct</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">{main_report.patterns_partial}</div>
                        <div class="stat-label">Partial</div>
                    </div>
                </div>
                
                <div class="verdict">
                    <div class="verdict-title">{main_report.quadrant}</div>
                    <div class="verdict-text">{main_report.verdict}</div>
                </div>
            </div>
        </div>
        
        {comparison_table}
        
        <h2>Issues ({main_report.total_issues})</h2>
        {f'<table><thead><tr><th>Severity</th><th>Location</th><th>Type</th><th>Description</th></tr></thead><tbody>{issues_rows}</tbody></table>' if issues_rows else '<div class="empty">No issues found ✓</div>'}
        
        <h2>Patterns ({main_report.patterns_detected})</h2>
        {f'<table><thead><tr><th>Quality</th><th>Location</th><th>Type</th><th>Details</th></tr></thead><tbody>{patterns_rows}</tbody></table>' if patterns_rows else '<div class="empty">No patterns detected</div>'}
    </div>
</body>
</html>'''
        
        with open(output_path, 'w') as f:
            f.write(html)


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
        
        print(f"        Done!")
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
               "  python hubris.py https://github.com/owner/repo  # Full URL\n"
               "  python hubris.py repo1 repo2 repo3 --compare # Compare multiple repos\n",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('paths', nargs='+', help='Path(s) to codebase or GitHub URL(s)')
    parser.add_argument('-o', '--output', help='Output JSON path')
    parser.add_argument('--html', help='Output HTML report path')
    parser.add_argument('--keep', action='store_true', help='Keep cloned repo after analysis')
    parser.add_argument('--compare', action='store_true', help='Generate comparison chart for multiple repos')
    args = parser.parse_args()
    
    temp_dirs = []
    reports = []
    
    try:
        for path in args.paths:
            codebase_path = path
            temp_dir = None
            repo_name = None
            
            if is_github_url(path):
                # Extract repo name for local check
                path_parts = path.replace('https://github.com/', '').replace('http://github.com/', '').split('/')
                if len(path_parts) >= 2:
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
                    codebase_path, repo_name, temp_dir = clone_github_repo(path)
                    if temp_dir:
                        temp_dirs.append(temp_dir)
            
            hubris = Hubris(codebase_path)
            report = hubris.analyze()
            
            # Fetch GitHub metadata if it's a GitHub repo
            original_path = path
            if is_github_url(original_path):
                print(f"[META] Fetching GitHub metadata...")
                report.github = fetch_github_metadata(original_path)
                if report.github.stars:
                    print(f"       ⭐ {report.github.stars:,} stars | {report.github.language} | {report.github.description[:60]}...")
            
            reports.append((report, hubris, repo_name, original_path))
        
        # Print results
        print("\n" + "="*70)
        print("HUBRIS v3 - RESILIENCE THEATER REPORT")
        print("="*70)
        
        for report, hubris, repo_name, original_path in reports:
            emoji = {'SIMPLE': '🟢', 'BATTLE_HARDENED': '🔵', 'CARGO_CULT': '🔴'}.get(report.quadrant, '⚪')
            name = report.github.full_name if report.github.full_name else Path(report.codebase_path).name
            stars = f" ⭐{report.github.stars:,}" if report.github.stars else ""
            print(f"\n{emoji} {name}{stars}: {report.quadrant} (ratio: {report.theater_ratio:.2f}, issues: {report.high_severity_count}H/{report.medium_severity_count}M)")
        
        # Single repo mode
        if len(reports) == 1:
            report, hubris, repo_name, original_path = reports[0]
            print(f"\nRisk Level: {report.risk_level}")
            print(f"\n{report.verdict}")
            
            # Save JSON
            if args.output:
                output_path = args.output
            elif repo_name:
                output_path = f"hubris_{repo_name}.json"
            else:
                output_path = None
            
            if output_path:
                hubris.save_report(report, output_path)
                print(f"\nJSON: {output_path}")
            
            # Generate HTML report
            if args.html:
                html_path = args.html
            elif repo_name:
                html_path = f"hubris_{repo_name}.html"
            else:
                html_path = "hubris_report.html"
            
            hubris.save_html_report(report, html_path)
            print(f"HTML: {html_path}")
        
        # Multi-repo comparison mode
        else:
            # Save individual JSONs
            for report, hubris, repo_name, original_path in reports:
                if repo_name:
                    output_path = f"hubris_{repo_name}.json"
                    hubris.save_report(report, output_path)
            
            # Generate comparison HTML
            html_path = args.html or "hubris_comparison.html"
            main_report, main_hubris, _ = reports[0]
            all_reports = [r[0] for r in reports]
            main_hubris.save_html_report(main_report, html_path, comparison_reports=all_reports)
            print(f"\nComparison HTML: {html_path}")
    
    finally:
        # Cleanup temp directories unless --keep
        if not args.keep:
            for temp_dir in temp_dirs:
                print(f"[CLEANUP] Removing {temp_dir}")
                shutil.rmtree(temp_dir, ignore_errors=True)
        elif temp_dirs:
            print(f"\n[KEEP] Repos preserved")


if __name__ == '__main__':
    main()
