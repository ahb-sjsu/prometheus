#!/usr/bin/env python3
"""
Aegis - Resilience Pattern Analyzer
====================================

Named after the legendary shield of Zeus and Athena.

Scans codebases for defensive programming patterns that make systems
resilient to failure. Works alongside the complexity analyzer to give
a 2D fitness score: Complexity vs Resilience.

The goal isn't minimum complexity — it's appropriate complexity with
adequate defense.

Patterns detected:
- Error handling (try/catch, exception specificity)
- Circuit breakers (Hystrix, resilience4j, Polly patterns)
- Retry logic (exponential backoff, jitter)
- Timeouts (network, database, general)
- Bulkheads (thread isolation, resource pools)
- Graceful degradation (fallbacks, feature flags)
- Observability (logging, metrics, tracing)
- Health checks (liveness, readiness, dependency checks)

"""

import re
import ast
import json
import logging
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional

logger = logging.getLogger(__name__)

# Import modular language analyzers
from lang_analyzers import (
    ANALYZER_REGISTRY, 
    LanguageResilienceMetrics,
    get_analyzer
)


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class ErrorHandlingMetrics:
    """Metrics for exception handling quality."""
    try_blocks: int = 0
    except_blocks: int = 0
    bare_excepts: int = 0  # except: with no type — bad practice
    specific_excepts: int = 0  # except ValueError: — good practice
    finally_blocks: int = 0
    raise_statements: int = 0
    custom_exceptions: int = 0
    
    # Ratios
    try_catch_ratio: float = 0.0  # try blocks per 100 LOC
    specificity_ratio: float = 0.0  # specific / total excepts


@dataclass
class CircuitBreakerMetrics:
    """Detection of circuit breaker patterns."""
    library_imports: list = field(default_factory=list)  # resilience4j, Hystrix, etc
    state_machine_patterns: int = 0  # OPEN/CLOSED/HALF_OPEN
    failure_threshold_configs: int = 0
    fallback_methods: int = 0
    manual_implementations: int = 0


@dataclass
class RetryMetrics:
    """Detection of retry patterns."""
    library_imports: list = field(default_factory=list)  # tenacity, retrying, Polly
    retry_decorators: int = 0
    exponential_backoff: int = 0
    max_retries_configs: int = 0
    jitter_patterns: int = 0
    manual_retry_loops: int = 0


@dataclass
class TimeoutMetrics:
    """Detection of timeout configurations."""
    http_timeouts: int = 0
    db_timeouts: int = 0
    socket_timeouts: int = 0
    generic_timeouts: int = 0
    timeout_handlers: int = 0
    missing_timeouts: int = 0  # Network calls without apparent timeout


@dataclass
class BulkheadMetrics:
    """Detection of isolation patterns."""
    thread_pool_configs: int = 0
    semaphore_usage: int = 0
    connection_pool_limits: int = 0
    resource_limits: int = 0
    queue_size_limits: int = 0


@dataclass
class DegradationMetrics:
    """Detection of graceful degradation patterns."""
    feature_flags: int = 0
    fallback_values: int = 0
    default_returns: int = 0
    cache_fallbacks: int = 0
    partial_response_patterns: int = 0


@dataclass
class ObservabilityMetrics:
    """Detection of logging, metrics, and tracing."""
    log_statements: int = 0
    log_levels_used: set = field(default_factory=set)
    metric_emissions: int = 0
    trace_spans: int = 0
    structured_logging: int = 0
    error_logging: int = 0  # Specifically logging errors
    
    # Coverage
    logs_per_100_loc: float = 0.0
    functions_with_logging: int = 0
    functions_without_logging: int = 0


@dataclass
class HealthCheckMetrics:
    """Detection of health check patterns."""
    health_endpoints: int = 0
    liveness_probes: int = 0
    readiness_probes: int = 0
    dependency_checks: int = 0
    startup_probes: int = 0


@dataclass
class FileResilienceMetrics:
    """Resilience metrics for a single file."""
    path: str
    language: str
    lines_of_code: int = 0
    
    error_handling: ErrorHandlingMetrics = field(default_factory=ErrorHandlingMetrics)
    circuit_breakers: CircuitBreakerMetrics = field(default_factory=CircuitBreakerMetrics)
    retries: RetryMetrics = field(default_factory=RetryMetrics)
    timeouts: TimeoutMetrics = field(default_factory=TimeoutMetrics)
    bulkheads: BulkheadMetrics = field(default_factory=BulkheadMetrics)
    degradation: DegradationMetrics = field(default_factory=DegradationMetrics)
    observability: ObservabilityMetrics = field(default_factory=ObservabilityMetrics)
    health_checks: HealthCheckMetrics = field(default_factory=HealthCheckMetrics)
    
    # Per-file score
    resilience_score: float = 0.0
    vulnerabilities: list = field(default_factory=list)


@dataclass
class AegisReport:
    """Complete resilience analysis report."""
    codebase_path: str
    timestamp: str
    
    # Aggregate scores (0-100)
    overall_resilience_score: float = 0.0
    error_handling_score: float = 0.0
    circuit_breaker_score: float = 0.0
    retry_score: float = 0.0
    timeout_score: float = 0.0
    bulkhead_score: float = 0.0
    degradation_score: float = 0.0
    observability_score: float = 0.0
    health_check_score: float = 0.0
    
    # Size metrics
    total_loc: int = 0
    too_small_to_score: bool = False
    too_small_reason: str = ""
    
    # Risk assessment
    shield_rating: str = ""  # ADAMANTINE, STEEL, BRONZE, WOOD, PAPER, TOO_SMALL
    vulnerabilities: list = field(default_factory=list)
    recommendations: list = field(default_factory=list)
    
    # File details
    file_metrics: list = field(default_factory=list)
    
    # Libraries detected
    resilience_libraries: list = field(default_factory=list)


# =============================================================================
# PATTERN DETECTORS
# =============================================================================

class PatternDetector:
    """Base class for pattern detection."""
    
    # Known resilience libraries by language
    RESILIENCE_LIBRARIES = {
        'python': {
            'circuit_breaker': ['pybreaker', 'circuitbreaker', 'aiobreaker'],
            'retry': ['tenacity', 'retrying', 'backoff', 'retry'],
            'timeout': ['timeout_decorator', 'wrapt_timeout_decorator', 'async_timeout'],
            'observability': ['structlog', 'loguru', 'opentelemetry', 'prometheus_client', 
                            'statsd', 'datadog', 'sentry_sdk', 'rollbar'],
            'resilience': ['resilience', 'pyfailsafe'],
        },
        'javascript': {
            'circuit_breaker': ['opossum', 'cockatiel', 'brakes'],
            'retry': ['async-retry', 'retry', 'p-retry', 'axios-retry'],
            'timeout': ['p-timeout', 'promise-timeout'],
            'observability': ['winston', 'pino', 'bunyan', 'opentelemetry', 
                            'prom-client', 'dd-trace', '@sentry/node'],
        },
        'java': {
            'circuit_breaker': ['resilience4j', 'hystrix', 'failsafe', 'sentinel'],
            'retry': ['resilience4j', 'spring-retry', 'failsafe', 'guava-retrying'],
            'observability': ['slf4j', 'log4j', 'logback', 'micrometer', 
                            'opentelemetry', 'prometheus', 'dropwizard-metrics'],
        },
        'go': {
            'circuit_breaker': ['sony/gobreaker', 'hystrix-go', 'go-resiliency'],
            'retry': ['avast/retry-go', 'cenkalti/backoff', 'sethvargo/go-retry'],
            'observability': ['zap', 'logrus', 'zerolog', 'prometheus', 'opentelemetry'],
        },
    }
    
    # Regex patterns for various resilience constructs
    PATTERNS = {
        # Circuit breaker patterns - require multiple state machine indicators
        # Single OPEN/CLOSED matches too many things (file open, connection closed)
        'circuit_states': re.compile(r'\b(HALF_OPEN|CircuitState|circuit_state|circuit_breaker|CircuitBreaker)\b'),
        'circuit_state_machine': re.compile(r'\b(OPEN|CLOSED)\b.*\b(OPEN|CLOSED|HALF_OPEN)\b', re.DOTALL),
        'failure_threshold': re.compile(r'\b(failure_threshold|failureThreshold|failure_rate|error_threshold|failure_count)\s*[=:]\s*\d+'),
        'fallback': re.compile(r'\b(@Fallback|with_fallback|fallbackMethod|on_fallback|fallback_handler)\b'),
        
        # Retry patterns
        'retry_decorator': re.compile(r'@(retry|Retry|Retryable|with_retry|retrying)'),
        'exponential_backoff': re.compile(r'\b(exponential|ExponentialBackoff|expo_backoff|backoff\.expo)\b'),
        'max_retries': re.compile(r'\b(max_retries|maxRetries|max_attempts|maxAttempts|retry_count)\s*[=:]\s*\d+'),
        'jitter': re.compile(r'\b(jitter|add_jitter|randomize|random_delay)\b'),
        'retry_loop': re.compile(r'for\s+\w+\s+in\s+range\s*\([^)]*retry|while.*retry|attempts?\s*[<>=]+\s*max'),
        
        # Timeout patterns
        'timeout_config': re.compile(r'\b(timeout|Timeout|TIMEOUT|connect_timeout|read_timeout|socket_timeout)\s*[=:]\s*\d+'),
        'timeout_exception': re.compile(r'\b(TimeoutError|TimeoutException|SocketTimeoutException|ConnectTimeoutException)\b'),
        'async_timeout': re.compile(r'\b(asyncio\.timeout|async_timeout|with_timeout|wait_for.*timeout)\b'),
        
        # Bulkhead patterns  
        'thread_pool': re.compile(r'\b(ThreadPoolExecutor|thread_pool|ThreadPool|Executors\.newFixedThreadPool)\b'),
        'semaphore': re.compile(r'\b(Semaphore|BoundedSemaphore|asyncio\.Semaphore)\b'),
        'connection_pool': re.compile(r'\b(pool_size|max_connections|maxPoolSize|connectionPoolSize)\s*[=:]\s*\d+'),
        'queue_limit': re.compile(r'\b(max_queue|queue_size|maxQueueSize|bounded_queue)\s*[=:]\s*\d+'),
        
        # Graceful degradation
        'feature_flag': re.compile(r'\b(feature_flag|FeatureFlag|is_enabled|isFeatureEnabled|toggle|LaunchDarkly|split\.io)\b'),
        'cache_fallback': re.compile(r'\b(cache\.get|getFromCache|cached_value|stale_if_error)\b'),
        'default_value': re.compile(r'\b(default=|\.get\([^,]+,\s*[^)]+\)|getOrDefault|orElse|unwrap_or)\b'),
        
        # Observability
        'log_statement': re.compile(r'\b(log\.|logger\.|logging\.|console\.(log|error|warn)|print\(|println)\b'),
        'log_level': re.compile(r'\.(debug|info|warning|warn|error|critical|fatal)\s*\('),
        'metric_emit': re.compile(r'\b(counter|gauge|histogram|timer|increment|observe|record|emit_metric)\b'),
        'trace_span': re.compile(r'\b(span|Span|tracer\.start|with_span|@trace|createSpan|startSpan)\b'),
        'structured_log': re.compile(r'\b(structlog|loguru|extra=|context=|fields=)\b'),
        
        # Health checks
        'health_endpoint': re.compile(r'["\']/(health|healthz|healthcheck|_health|status)["\']'),
        'liveness': re.compile(r'\b(liveness|livenessProbe|is_alive|ping)\b'),
        'readiness': re.compile(r'\b(readiness|readinessProbe|is_ready|ready)\b'),
        'dependency_check': re.compile(r'\b(check_dependency|checkDependency|dependency_health|ping_database|ping_redis)\b'),
        
        # Network calls (to check for missing timeouts)
        # More specific patterns to avoid matching ORM methods or internal functions
        'http_call': re.compile(r'\b(requests\.(get|post|put|delete|patch|head|options)\s*\(|urllib\.request\.|httpx\.(get|post|put|delete|patch|head|options|Client)|aiohttp\.(get|post|ClientSession)|fetch\s*\(\s*["\']https?://|axios\.(get|post|put|delete)|http\.request\s*\(|new\s+HttpClient)\b'),
        'db_call': re.compile(r'\b(cursor\.execute|\.raw\s*\(|connection\.execute)\s*\('),
    }


class PythonResilienceAnalyzer(PatternDetector):
    """Deep analysis for Python files using AST."""
    
    def analyze(self, content: str, metrics: FileResilienceMetrics):
        """Analyze Python file for resilience patterns."""
        import warnings
        try:
            # Suppress SyntaxWarnings from invalid escape sequences in analyzed code
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=SyntaxWarning)
                tree = ast.parse(content)
        except SyntaxError:
            self._analyze_with_regex(content, metrics)
            return
        
        # AST-based analysis
        self._analyze_error_handling(tree, content, metrics)
        self._analyze_imports(tree, metrics)
        self._analyze_decorators(tree, metrics)
        
        # Regex-based analysis for patterns AST can't catch
        self._analyze_with_regex(content, metrics)
        
        # Calculate ratios
        if metrics.lines_of_code > 0:
            metrics.error_handling.try_catch_ratio = (
                metrics.error_handling.try_blocks / metrics.lines_of_code * 100
            )
            metrics.observability.logs_per_100_loc = (
                metrics.observability.log_statements / metrics.lines_of_code * 100
            )
        
        if metrics.error_handling.except_blocks > 0:
            metrics.error_handling.specificity_ratio = (
                metrics.error_handling.specific_excepts / 
                metrics.error_handling.except_blocks
            )
    
    def _analyze_error_handling(self, tree: ast.AST, content: str, metrics: FileResilienceMetrics):
        """Analyze exception handling patterns."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                metrics.error_handling.try_blocks += 1
                
                for handler in node.handlers:
                    metrics.error_handling.except_blocks += 1
                    if handler.type is None:
                        metrics.error_handling.bare_excepts += 1
                        metrics.vulnerabilities.append({
                            'type': 'bare_except',
                            'line': handler.lineno,
                            'severity': 'MEDIUM',
                            'message': 'Bare except catches all exceptions including KeyboardInterrupt'
                        })
                    else:
                        metrics.error_handling.specific_excepts += 1
                
                if node.finalbody:
                    metrics.error_handling.finally_blocks += 1
            
            elif isinstance(node, ast.Raise):
                metrics.error_handling.raise_statements += 1
            
            elif isinstance(node, ast.ClassDef):
                # Check for custom exception classes
                for base in node.bases:
                    if isinstance(base, ast.Name) and 'Exception' in base.id:
                        metrics.error_handling.custom_exceptions += 1
                    elif isinstance(base, ast.Attribute) and 'Exception' in base.attr:
                        metrics.error_handling.custom_exceptions += 1
    
    def _analyze_imports(self, tree: ast.AST, metrics: FileResilienceMetrics):
        """Detect resilience library imports."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self._check_library(alias.name, metrics)
            elif isinstance(node, ast.ImportFrom) and node.module:
                self._check_library(node.module, metrics)
    
    def _check_library(self, module_name: str, metrics: FileResilienceMetrics):
        """Check if module is a known resilience library."""
        libs = self.RESILIENCE_LIBRARIES.get('python', {})
        
        for category, lib_list in libs.items():
            for lib in lib_list:
                if lib in module_name.lower():
                    if category == 'circuit_breaker':
                        metrics.circuit_breakers.library_imports.append(module_name)
                    elif category == 'retry':
                        metrics.retries.library_imports.append(module_name)
                    elif category == 'observability':
                        metrics.observability.structured_logging += 1
    
    def _analyze_decorators(self, tree: ast.AST, metrics: FileResilienceMetrics):
        """Analyze function decorators for resilience patterns."""
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                has_logging = False
                
                for decorator in node.decorator_list:
                    dec_name = ''
                    if isinstance(decorator, ast.Name):
                        dec_name = decorator.id
                    elif isinstance(decorator, ast.Call):
                        if isinstance(decorator.func, ast.Name):
                            dec_name = decorator.func.id
                        elif isinstance(decorator.func, ast.Attribute):
                            dec_name = decorator.func.attr
                    
                    if dec_name.lower() in ['retry', 'retrying', 'backoff']:
                        metrics.retries.retry_decorators += 1
                    elif dec_name.lower() in ['timeout', 'with_timeout']:
                        metrics.timeouts.timeout_handlers += 1
                    elif dec_name.lower() in ['trace', 'traced', 'span']:
                        metrics.observability.trace_spans += 1
                
                # Check if function body has logging
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        if isinstance(child.func, ast.Attribute):
                            if child.func.attr in ['debug', 'info', 'warning', 'error', 'critical']:
                                has_logging = True
                                break
                
                if has_logging:
                    metrics.observability.functions_with_logging += 1
                else:
                    metrics.observability.functions_without_logging += 1
    
    def _analyze_with_regex(self, content: str, metrics: FileResilienceMetrics):
        """Use regex for patterns AST can't detect."""
        # Circuit breaker patterns
        metrics.circuit_breakers.state_machine_patterns += len(
            self.PATTERNS['circuit_states'].findall(content)
        )
        metrics.circuit_breakers.failure_threshold_configs += len(
            self.PATTERNS['failure_threshold'].findall(content)
        )
        metrics.circuit_breakers.fallback_methods += len(
            self.PATTERNS['fallback'].findall(content)
        )
        
        # Retry patterns
        metrics.retries.exponential_backoff += len(
            self.PATTERNS['exponential_backoff'].findall(content)
        )
        metrics.retries.max_retries_configs += len(
            self.PATTERNS['max_retries'].findall(content)
        )
        metrics.retries.jitter_patterns += len(
            self.PATTERNS['jitter'].findall(content)
        )
        metrics.retries.manual_retry_loops += len(
            self.PATTERNS['retry_loop'].findall(content)
        )
        
        # Timeout patterns
        metrics.timeouts.generic_timeouts += len(
            self.PATTERNS['timeout_config'].findall(content)
        )
        metrics.timeouts.timeout_handlers += len(
            self.PATTERNS['timeout_exception'].findall(content)
        )
        metrics.timeouts.timeout_handlers += len(
            self.PATTERNS['async_timeout'].findall(content)
        )
        
        # Check for network calls without timeouts
        # Only flag this as a vulnerability if:
        # 1. There are actual HTTP calls (not just method names)
        # 2. The file is not a test file (tests often use synchronous clients intentionally)
        http_calls = self.PATTERNS['http_call'].findall(content)
        timeout_mentions = self.PATTERNS['timeout_config'].findall(content)
        
        # Count actual HTTP calls (filter out partial matches)
        actual_http_calls = len([c for c in http_calls if c[0]])  # First group is the actual call
        
        if actual_http_calls > len(timeout_mentions):
            missing = actual_http_calls - len(timeout_mentions)
            metrics.timeouts.missing_timeouts += missing
            # Don't add vulnerability here - will be filtered at report level
            # based on file path (test files excluded)
        
        # Bulkhead patterns
        metrics.bulkheads.thread_pool_configs += len(
            self.PATTERNS['thread_pool'].findall(content)
        )
        metrics.bulkheads.semaphore_usage += len(
            self.PATTERNS['semaphore'].findall(content)
        )
        metrics.bulkheads.connection_pool_limits += len(
            self.PATTERNS['connection_pool'].findall(content)
        )
        metrics.bulkheads.queue_size_limits += len(
            self.PATTERNS['queue_limit'].findall(content)
        )
        
        # Graceful degradation
        metrics.degradation.feature_flags += len(
            self.PATTERNS['feature_flag'].findall(content)
        )
        metrics.degradation.cache_fallbacks += len(
            self.PATTERNS['cache_fallback'].findall(content)
        )
        metrics.degradation.default_returns += len(
            self.PATTERNS['default_value'].findall(content)
        )
        
        # Observability
        metrics.observability.log_statements += len(
            self.PATTERNS['log_statement'].findall(content)
        )
        log_levels = self.PATTERNS['log_level'].findall(content)
        metrics.observability.log_levels_used = set(log_levels)
        metrics.observability.error_logging = log_levels.count('error') + log_levels.count('critical')
        
        metrics.observability.metric_emissions += len(
            self.PATTERNS['metric_emit'].findall(content)
        )
        metrics.observability.trace_spans += len(
            self.PATTERNS['trace_span'].findall(content)
        )
        metrics.observability.structured_logging += len(
            self.PATTERNS['structured_log'].findall(content)
        )
        
        # Health checks
        metrics.health_checks.health_endpoints += len(
            self.PATTERNS['health_endpoint'].findall(content)
        )
        metrics.health_checks.liveness_probes += len(
            self.PATTERNS['liveness'].findall(content)
        )
        metrics.health_checks.readiness_probes += len(
            self.PATTERNS['readiness'].findall(content)
        )
        metrics.health_checks.dependency_checks += len(
            self.PATTERNS['dependency_check'].findall(content)
        )


class GenericResilienceAnalyzer(PatternDetector):
    """Regex-based analysis for non-Python files."""
    
    def analyze(self, content: str, metrics: FileResilienceMetrics, language: str):
        """Analyze file using regex patterns."""
        # All the regex patterns work cross-language
        python_analyzer = PythonResilienceAnalyzer()
        python_analyzer._analyze_with_regex(content, metrics)
        
        # Count basic error handling via regex
        if language in ['javascript', 'typescript', 'java', 'go']:
            metrics.error_handling.try_blocks = len(re.findall(r'\btry\s*\{', content))
            metrics.error_handling.except_blocks = len(re.findall(r'\bcatch\s*\(', content))
            metrics.error_handling.finally_blocks = len(re.findall(r'\bfinally\s*\{', content))
        
        # Language-specific library detection
        libs = self.RESILIENCE_LIBRARIES.get(language, {})
        for category, lib_list in libs.items():
            for lib in lib_list:
                if lib.lower() in content.lower():
                    if category == 'circuit_breaker':
                        metrics.circuit_breakers.library_imports.append(lib)
                    elif category == 'retry':
                        metrics.retries.library_imports.append(lib)


# =============================================================================
# MAIN ANALYZER
# =============================================================================

class Aegis:
    """
    The Shield - Main resilience analyzer.
    
    Scans codebases for defensive programming patterns and generates
    a resilience score alongside vulnerability report.
    
    library_mode: When True, adjusts scoring for libraries:
    - Less penalty for missing timeouts (libraries expose, not enforce)
    - Less penalty for missing retries (caller's responsibility)
    - Lower observability expectations (libraries shouldn't spam logs)
    - Higher weight on error handling (libraries must handle errors gracefully)
    """
    
    LANGUAGE_EXTENSIONS = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.jsx': 'javascript',
        '.tsx': 'typescript',
        '.java': 'java',
        '.go': 'go',
        '.rs': 'rust',
        '.rb': 'ruby',
    }
    
    def __init__(self, codebase_path: str, library_mode: bool = False):
        self.codebase_path = Path(codebase_path)
        self.file_metrics: list[FileResilienceMetrics] = []
        self.python_analyzer = PythonResilienceAnalyzer()
        self.generic_analyzer = GenericResilienceAnalyzer()
        self.library_mode = library_mode
    
    def analyze(self) -> AegisReport:
        """Run full resilience analysis."""
        from datetime import datetime
        
        print(f"[AEGIS] Scanning {self.codebase_path} for resilience patterns...")
        
        # Scan all files
        self._scan_files()
        
        # Generate report
        report = AegisReport(
            codebase_path=str(self.codebase_path),
            timestamp=datetime.now().isoformat()
        )
        
        # Aggregate scores
        self._calculate_scores(report)
        
        # Determine shield rating
        self._rate_shield(report)
        
        # Generate recommendations
        self._generate_recommendations(report)
        
        # Collect library detections
        libs = set()
        for fm in self.file_metrics:
            libs.update(fm.circuit_breakers.library_imports)
            libs.update(fm.retries.library_imports)
        report.resilience_libraries = list(libs)
        
        # Attach file metrics
        report.file_metrics = [self._serialize_metrics(fm) for fm in self.file_metrics]
        
        # Output depends on whether codebase is large enough to score
        if report.too_small_to_score:
            print(f"  Shield Rating: {report.shield_rating}")
            print(f"  {report.too_small_reason}")
        else:
            print(f"  Shield Rating: {report.shield_rating}")
            print(f"  Overall Score: {report.overall_resilience_score:.1f}/100")
        
        return report
    
    def _scan_files(self):
        """Scan all source files for resilience patterns."""
        # Use modular analyzer registry for supported extensions
        supported_extensions = ANALYZER_REGISTRY.supported_extensions()
        
        for ext in supported_extensions:
            for filepath in self.codebase_path.rglob(f'*{ext}'):
                if any(skip in str(filepath) for skip in [
                    'node_modules', 'venv', '.venv', '__pycache__',
                    '.git', 'dist', 'build', '.tox', 'egg-info'
                ]):
                    continue
                
                metrics = self._analyze_file(filepath)
                if metrics:
                    self.file_metrics.append(metrics)
    
    def _analyze_file(self, filepath: Path) -> Optional[FileResilienceMetrics]:
        """Analyze a single file for resilience patterns using modular analyzers."""
        try:
            content = filepath.read_text(encoding='utf-8', errors='ignore')
        except (OSError, UnicodeDecodeError) as e:
            logger.debug(f"Could not read {filepath}: {e}")
            return None
        
        # Get the appropriate language analyzer
        analyzer = get_analyzer(str(filepath))
        if not analyzer:
            return None
        
        lines = [l for l in content.splitlines() if l.strip()]
        
        metrics = FileResilienceMetrics(
            path=str(filepath.relative_to(self.codebase_path)),
            language=analyzer.LANGUAGE_NAME,
            lines_of_code=len(lines)
        )
        
        # Use the modular analyzer to get language-specific metrics
        lang_metrics = analyzer.analyze(content, str(filepath))
        
        # Map language-agnostic metrics to our FileResilienceMetrics
        self._map_lang_metrics_to_file_metrics(lang_metrics, metrics, content)
        
        # Also run legacy analyzers for backward compatibility (Python-specific deep analysis)
        if analyzer.LANGUAGE_NAME == 'python':
            self.python_analyzer.analyze(content, metrics)
        
        # Calculate file-level resilience score
        metrics.resilience_score = self._calculate_file_score(metrics)
        
        return metrics
    
    def _map_lang_metrics_to_file_metrics(self, lang: LanguageResilienceMetrics, 
                                           file: FileResilienceMetrics, content: str):
        """Map language-agnostic metrics to FileResilienceMetrics structure."""
        # Error handling
        file.error_handling.try_blocks = lang.error_handlers
        file.error_handling.except_blocks = lang.error_handlers  # Approximation
        file.error_handling.bare_excepts = lang.bare_handlers
        file.error_handling.finally_blocks = lang.cleanup_blocks
        file.error_handling.raise_statements = lang.error_propagation
        
        # Calculate specificity ratio
        total_handlers = lang.error_handlers + lang.bare_handlers
        if total_handlers > 0:
            file.error_handling.specificity_ratio = lang.error_handlers / total_handlers
        
        # Timeouts
        file.timeouts.generic_timeouts = lang.timeout_configs
        
        # Observability
        file.observability.log_statements = lang.log_statements
        file.observability.error_logging = lang.error_logging
        if file.lines_of_code > 0:
            file.observability.logs_per_100_loc = lang.log_statements / file.lines_of_code * 100
        
        # Retries
        file.retries.retry_decorators = lang.retry_patterns
        
        # Degradation (default returns count as degradation)
        file.degradation.default_returns = lang.null_checks  # Approximation
        
        # Store extra metrics for language-specific patterns
        if lang.extras:
            # Store in a way that can be reported
            if 'goto_cleanup' in lang.extras:
                file.error_handling.try_blocks += lang.extras['goto_cleanup']
            if 'unsafe_unwrap' in lang.extras:
                file.error_handling.bare_excepts += lang.extras['unsafe_unwrap']
    
    def _calculate_file_score(self, m: FileResilienceMetrics) -> float:
        """Calculate resilience score for a single file (0-100).
        
        Scoring is adjusted based on:
        - library_mode: Adjusts weights for libraries vs applications
        - language: C/C++ code uses different patterns than Python/JS
        """
        score = 0.0
        max_score = 0.0
        
        # Detect if this is C/C++ code (different resilience patterns)
        is_c_style = m.language in ('c', 'cpp', 'go', 'rust')
        
        if self.library_mode:
            # LIBRARY MODE SCORING
            # Error handling is most important (40 points max)
            max_score += 40
            if m.error_handling.try_blocks > 0:
                score += 15
            if m.error_handling.specificity_ratio > 0.8:
                score += 15
            elif m.error_handling.specificity_ratio > 0.5:
                score += 8
            if m.error_handling.bare_excepts == 0:
                score += 10
            
            # Timeouts (5 points max) - libraries expose, not enforce
            max_score += 5
            if m.timeouts.generic_timeouts > 0 or m.timeouts.timeout_handlers > 0:
                score += 5
            
            # Observability (10 points max) - libraries should be quiet
            max_score += 10
            if m.observability.logs_per_100_loc > 0.5:
                score += 5
            if m.observability.error_logging > 0:
                score += 5
            
            # Retries (5 points max) - caller's responsibility
            max_score += 5
            if m.retries.library_imports or m.retries.retry_decorators > 0:
                score += 5
            
            # Graceful degradation (25 points max)
            max_score += 25
            if m.degradation.default_returns > 0:
                score += 10
            if m.degradation.fallback_values > 0 or m.degradation.cache_fallbacks > 0:
                score += 10
            if m.error_handling.custom_exceptions > 0:
                score += 5
            
            # API cleanliness (15 points max)
            max_score += 15
            if m.error_handling.raise_statements > 0:
                score += 5
            if m.error_handling.finally_blocks > 0:
                score += 5
            if m.max_nesting_depth <= 3 if hasattr(m, 'max_nesting_depth') else True:
                score += 5
                
        elif is_c_style:
            # C/C++/Go/Rust SCORING
            # 
            # KEY INSIGHT: Only code that crosses system boundaries needs error handling!
            # - Network, file I/O, database, external processes, user input = needs handling
            # - Pure computation, string formatting, data traversal = doesn't need it
            #
            # We detect boundary-crossing patterns and only then expect error handling
            
            # Check if this file has boundary-crossing code
            has_io = m.resource_acquisition if hasattr(m, 'resource_acquisition') else 0
            has_network = m.timeouts.http_calls if hasattr(m.timeouts, 'http_calls') else 0
            has_file_ops = m.timeouts.generic_timeouts  # rough proxy
            
            # Also check via the metrics we do have
            has_boundaries = (
                has_io > 0 or 
                has_network > 0 or 
                m.error_handling.try_blocks > 0 or  # if they have error handling, they probably need it
                m.observability.error_logging > 0    # if they log errors, they deal with errors
            )
            
            if has_boundaries:
                # This file crosses system boundaries - expect error handling
                max_score = 100
                score = 30  # Base score
                
                # Error handling (up to +40)
                if m.error_handling.try_blocks > 0:
                    score += min(20, m.error_handling.try_blocks * 4)
                if m.error_handling.finally_blocks > 0:
                    score += 10
                if m.observability.error_logging > 0:
                    score += min(10, m.observability.error_logging * 2)
                
                # Defensive patterns (up to +20)
                if m.degradation.default_returns > 0:
                    score += min(10, m.degradation.default_returns)
                if m.error_handling.raise_statements > 0:
                    score += min(10, m.error_handling.raise_statements * 2)
                
                # Penalties
                if m.error_handling.bare_excepts > 0:
                    score -= min(20, m.error_handling.bare_excepts * 5)
                
                return min(100, max(0, score))
            else:
                # Pure computation - no error handling needed
                # Give a good score by default, penalize only for obvious problems
                return 70  # "Good enough" - it's just computation code
                
        else:
            # APPLICATION MODE SCORING for Python/JS/Java etc.
            # 
            # Same principle: only boundary-crossing code needs error handling
            
            # Detect if this file crosses system boundaries
            has_http = m.timeouts.http_calls if hasattr(m.timeouts, 'http_calls') else 0
            has_db = m.timeouts.db_calls if hasattr(m.timeouts, 'db_calls') else 0
            has_file = m.timeouts.file_calls if hasattr(m.timeouts, 'file_calls') else 0
            
            has_boundaries = (
                has_http > 0 or
                has_db > 0 or
                has_file > 0 or
                m.timeouts.missing_timeouts > 0 or  # detected HTTP without timeout
                m.retries.library_imports or  # has retry lib = probably needs it
                m.circuit_breakers.library_imports or  # has circuit breaker = needs it
                m.error_handling.try_blocks > 0  # has try/catch = probably needs it
            )
            
            if not has_boundaries:
                # Pure computation - give good score
                return 70
            
            # Has boundaries - full scoring
            # Error handling (25 points max)
            max_score += 25
            if m.error_handling.try_blocks > 0:
                score += 10
            if m.error_handling.specificity_ratio > 0.8:
                score += 10
            elif m.error_handling.specificity_ratio > 0.5:
                score += 5
            if m.error_handling.bare_excepts == 0:
                score += 5
            
            # Timeouts (20 points max)
            max_score += 20
            if m.timeouts.generic_timeouts > 0 or m.timeouts.timeout_handlers > 0:
                score += 15
            if m.timeouts.missing_timeouts == 0:
                score += 5
            
            # Observability (20 points max)
            max_score += 20
            if m.observability.logs_per_100_loc > 2:
                score += 10
            elif m.observability.logs_per_100_loc > 0.5:
                score += 5
            if m.observability.error_logging > 0:
                score += 5
            if m.observability.metric_emissions > 0 or m.observability.trace_spans > 0:
                score += 5
            
            # Retries (15 points max)
            max_score += 15
            if m.retries.library_imports or m.retries.retry_decorators > 0:
                score += 10
            if m.retries.exponential_backoff > 0:
                score += 3
            if m.retries.jitter_patterns > 0:
                score += 2
            
            # Circuit breakers (10 points max)
            max_score += 10
            if m.circuit_breakers.library_imports:
                score += 7
            if m.circuit_breakers.fallback_methods > 0:
                score += 3
            
            # Graceful degradation (10 points max)
            max_score += 10
            if m.degradation.default_returns > 0:
                score += 4
            if m.degradation.fallback_values > 0 or m.degradation.cache_fallbacks > 0:
                score += 3
            if m.degradation.feature_flags > 0:
                score += 3
        
        return (score / max_score) * 100 if max_score > 0 else 0
    
    def _calculate_scores(self, report: AegisReport):
        """Calculate aggregate scores for the report."""
        if not self.file_metrics:
            return
        
        # Calculate total LOC
        total_loc = sum(fm.lines_of_code for fm in self.file_metrics)
        report.total_loc = total_loc
        
        # MINIMUM SIZE CHECK
        # Codebases under 2000 LOC are too small to have meaningful resilience patterns.
        # We mark them as "TOO_SMALL" rather than giving a misleading low score.
        MIN_LOC_FOR_SCORING = 2000
        
        if total_loc < MIN_LOC_FOR_SCORING:
            report.too_small_to_score = True
            report.overall_resilience_score = -1  # Sentinel value
            report.shield_rating = "TOO_SMALL"
            report.too_small_reason = (
                f"Codebase has {total_loc:,} LOC (minimum {MIN_LOC_FOR_SCORING:,} required). "
                f"Small codebases don't have enough patterns to analyze meaningfully."
            )
            # Still calculate category scores for informational purposes
            # but they won't affect the overall rating
        
        # Overall resilience score (weighted average)
        if total_loc > 0:
            weighted_score = sum(
                fm.resilience_score * fm.lines_of_code 
                for fm in self.file_metrics
            ) / total_loc
            if not getattr(report, 'too_small_to_score', False):
                report.overall_resilience_score = weighted_score
        
        # Category scores (always calculate for informational purposes)
        n = len(self.file_metrics)
        
        # Error handling score
        total_try = sum(fm.error_handling.try_blocks for fm in self.file_metrics)
        total_bare = sum(fm.error_handling.bare_excepts for fm in self.file_metrics)
        total_specific = sum(fm.error_handling.specific_excepts for fm in self.file_metrics)
        
        if total_try > 0:
            report.error_handling_score = min(100, (
                (total_try / total_loc * 1000) * 0.5 +  # Try density
                (total_specific / max(1, total_specific + total_bare)) * 50  # Specificity
            ))
        
        # Circuit breaker score - require actual circuit breaker patterns
        # Not just fallback methods (which could be normal code)
        cb_files = sum(1 for fm in self.file_metrics if fm.circuit_breakers.library_imports)
        cb_state_machines = sum(fm.circuit_breakers.state_machine_patterns for fm in self.file_metrics)
        cb_thresholds = sum(fm.circuit_breakers.failure_threshold_configs for fm in self.file_metrics)
        cb_fallbacks = sum(fm.circuit_breakers.fallback_methods for fm in self.file_metrics)
        
        # Only count fallbacks if there's evidence of actual circuit breaker usage
        has_cb_evidence = cb_files > 0 or cb_state_machines > 0 or cb_thresholds > 0
        effective_fallbacks = cb_fallbacks if has_cb_evidence else 0
        
        report.circuit_breaker_score = min(100, (
            cb_files / n * 50 + 
            min(cb_state_machines, 5) * 5 +
            min(cb_thresholds, 5) * 5 +
            min(effective_fallbacks, 5) * 4
        ))
        
        # Retry score
        retry_files = sum(1 for fm in self.file_metrics if 
                        fm.retries.library_imports or fm.retries.retry_decorators > 0)
        backoff_count = sum(fm.retries.exponential_backoff for fm in self.file_metrics)
        report.retry_score = min(100, (retry_files / n * 60 + min(backoff_count, 5) * 8))
        
        # Timeout score - different calculation in library mode
        timeout_count = sum(fm.timeouts.generic_timeouts + fm.timeouts.timeout_handlers 
                          for fm in self.file_metrics)
        missing_count = sum(fm.timeouts.missing_timeouts for fm in self.file_metrics)
        
        if self.library_mode:
            # Libraries get credit for timeout support without penalty for not using them
            report.timeout_score = min(100, timeout_count / max(1, n) * 30 + 50)
        else:
            report.timeout_score = min(100, max(0, 
                (timeout_count / max(1, n) * 20) - (missing_count * 5)
            ))
        
        # Bulkhead score
        bulkhead_patterns = sum(
            fm.bulkheads.thread_pool_configs + fm.bulkheads.semaphore_usage +
            fm.bulkheads.connection_pool_limits
            for fm in self.file_metrics
        )
        report.bulkhead_score = min(100, bulkhead_patterns * 15)
        
        # Degradation score
        degradation_patterns = sum(
            fm.degradation.feature_flags + fm.degradation.default_returns +
            fm.degradation.cache_fallbacks + fm.degradation.fallback_values
            for fm in self.file_metrics
        )
        report.degradation_score = min(100, degradation_patterns / n * 30)
        
        # Observability score - different expectations in library mode
        avg_log_density = sum(fm.observability.logs_per_100_loc for fm in self.file_metrics) / n
        has_metrics = sum(1 for fm in self.file_metrics if fm.observability.metric_emissions > 0)
        has_traces = sum(1 for fm in self.file_metrics if fm.observability.trace_spans > 0)
        
        if self.library_mode:
            # Libraries shouldn't be heavily logged - just error logging is fine
            error_logging = sum(fm.observability.error_logging for fm in self.file_metrics)
            report.observability_score = min(100, (
                min(avg_log_density, 2) * 15 +  # Some logging is fine
                (error_logging > 0) * 35 +      # Error logging is good
                50                               # Base score for libraries
            ))
        else:
            report.observability_score = min(100, (
                min(avg_log_density, 5) * 10 +
                (has_metrics / n * 25) +
                (has_traces / n * 25)
            ))
        
        # Health check score - less important for libraries
        health_patterns = sum(
            fm.health_checks.health_endpoints + fm.health_checks.liveness_probes +
            fm.health_checks.readiness_probes + fm.health_checks.dependency_checks
            for fm in self.file_metrics
        )
        if self.library_mode:
            report.health_check_score = min(100, health_patterns * 20 + 50)  # Base score for libraries
        else:
            report.health_check_score = min(100, health_patterns * 20)
        
        # Collect all vulnerabilities (filter test files for missing_timeout)
        for fm in self.file_metrics:
            for vuln in fm.vulnerabilities:
                vuln['file'] = fm.path
                report.vulnerabilities.append(vuln)
        
        # Add missing timeout vulnerabilities (excluding test files)
        for fm in self.file_metrics:
            # Skip test files for timeout vulnerability reporting
            is_test_file = any(t in fm.path.lower() for t in [
                '/test', '/tests', 'test_', '_test.', 'spec.', '.spec',
                '/fixtures', '/mocks', '/conftest'
            ])
            
            if not is_test_file and fm.timeouts.missing_timeouts > 0:
                report.vulnerabilities.append({
                    'type': 'missing_timeout',
                    'severity': 'HIGH',
                    'message': f'{fm.timeouts.missing_timeouts} network calls may lack timeout configuration',
                    'file': fm.path
                })
    
    def _rate_shield(self, report: AegisReport):
        """Assign shield rating based on overall score."""
        # Skip rating if already marked as too small
        if report.too_small_to_score:
            # Rating already set to TOO_SMALL in _calculate_scores
            return
        
        score = report.overall_resilience_score
        
        if score >= 80:
            report.shield_rating = "ADAMANTINE"  # Legendary, nearly unbreakable
        elif score >= 60:
            report.shield_rating = "STEEL"  # Strong, reliable
        elif score >= 40:
            report.shield_rating = "BRONZE"  # Decent, room for improvement
        elif score >= 20:
            report.shield_rating = "WOOD"  # Basic protection only
        else:
            report.shield_rating = "PAPER"  # Essentially undefended
    
    def _generate_recommendations(self, report: AegisReport):
        """Generate actionable recommendations."""
        recs = []
        
        if report.error_handling_score < 40:
            recs.append({
                'priority': 'HIGH',
                'category': 'Error Handling',
                'message': 'Add try/catch blocks around I/O operations, network calls, and parsing logic.',
                'libraries': ['Custom exceptions for domain errors']
            })
        
        if report.timeout_score < 30:
            recs.append({
                'priority': 'CRITICAL',
                'category': 'Timeouts',
                'message': 'Network calls without timeouts can hang indefinitely. Add timeout configs to all HTTP clients and database connections.',
                'libraries': ['httpx (Python)', 'axios with timeout (JS)', 'OkHttp timeouts (Java)']
            })
        
        if report.retry_score < 30:
            recs.append({
                'priority': 'HIGH',
                'category': 'Retry Logic',
                'message': 'Transient failures are common. Implement retry with exponential backoff for external service calls.',
                'libraries': ['tenacity (Python)', 'async-retry (JS)', 'resilience4j (Java)', 'cenkalti/backoff (Go)']
            })
        
        if report.circuit_breaker_score < 20:
            recs.append({
                'priority': 'MEDIUM',
                'category': 'Circuit Breakers',
                'message': 'Protect against cascading failures by adding circuit breakers to external dependencies.',
                'libraries': ['pybreaker (Python)', 'opossum (JS)', 'resilience4j (Java)', 'sony/gobreaker (Go)']
            })
        
        if report.observability_score < 40:
            recs.append({
                'priority': 'HIGH',
                'category': 'Observability',
                'message': 'Insufficient logging/metrics makes debugging production issues nearly impossible.',
                'libraries': ['structlog (Python)', 'pino (JS)', 'OpenTelemetry (all languages)']
            })
        
        if report.health_check_score < 20:
            recs.append({
                'priority': 'MEDIUM',
                'category': 'Health Checks',
                'message': 'Add /health endpoints with liveness and readiness probes for orchestration.',
                'libraries': ['FastAPI health (Python)', 'Terminus (JS)', 'Spring Actuator (Java)']
            })
        
        if report.bulkhead_score < 20:
            recs.append({
                'priority': 'LOW',
                'category': 'Bulkheads',
                'message': 'Consider thread pool isolation and connection pool limits to prevent resource exhaustion.',
                'libraries': ['concurrent.futures (Python)', 'generic-pool (JS)', 'HikariCP (Java)']
            })
        
        # Sort by priority
        priority_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        recs.sort(key=lambda x: priority_order.get(x['priority'], 99))
        
        report.recommendations = recs
    
    def _serialize_metrics(self, fm: FileResilienceMetrics) -> dict:
        """Convert metrics to JSON-serializable dict."""
        d = asdict(fm)
        # Convert sets to lists
        if 'observability' in d and 'log_levels_used' in d['observability']:
            d['observability']['log_levels_used'] = list(d['observability']['log_levels_used'])
        return d
    
    def save_report(self, report: AegisReport, output_path: str = None) -> str:
        """Save report to JSON file."""
        if output_path is None:
            output_path = f"aegis_report_{self.codebase_path.name}.json"
        
        report_dict = {
            'codebase_path': report.codebase_path,
            'timestamp': report.timestamp,
            'shield_rating': report.shield_rating,
            'overall_resilience_score': report.overall_resilience_score,
            'category_scores': {
                'error_handling': report.error_handling_score,
                'circuit_breakers': report.circuit_breaker_score,
                'retries': report.retry_score,
                'timeouts': report.timeout_score,
                'bulkheads': report.bulkhead_score,
                'degradation': report.degradation_score,
                'observability': report.observability_score,
                'health_checks': report.health_check_score,
            },
            'resilience_libraries_detected': report.resilience_libraries,
            'vulnerabilities': report.vulnerabilities,
            'recommendations': report.recommendations,
            'file_metrics': report.file_metrics,
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_dict, f, indent=2)
        
        return output_path


# =============================================================================
# CLI
# =============================================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Aegis - Analyze codebase resilience patterns"
    )
    parser.add_argument('path', help='Path to codebase')
    parser.add_argument('-o', '--output', help='Output JSON path')
    parser.add_argument('--summary', action='store_true', help='Print summary only')
    
    args = parser.parse_args()
    
    aegis = Aegis(args.path)
    report = aegis.analyze()
    
    if args.output:
        output_path = aegis.save_report(report, args.output)
        print(f"\nReport saved to: {output_path}")
    
    # Print results
    print("\n" + "="*70)
    print(f"AEGIS RESILIENCE REPORT - Shield Rating: {report.shield_rating}")
    print("="*70)
    
    print(f"\nOverall Resilience Score: {report.overall_resilience_score:.1f}/100")
    
    print("\nCategory Scores:")
    print(f"  Error Handling:    {report.error_handling_score:5.1f}/100")
    print(f"  Timeouts:          {report.timeout_score:5.1f}/100")
    print(f"  Retries:           {report.retry_score:5.1f}/100")
    print(f"  Circuit Breakers:  {report.circuit_breaker_score:5.1f}/100")
    print(f"  Observability:     {report.observability_score:5.1f}/100")
    print(f"  Graceful Degrade:  {report.degradation_score:5.1f}/100")
    print(f"  Bulkheads:         {report.bulkhead_score:5.1f}/100")
    print(f"  Health Checks:     {report.health_check_score:5.1f}/100")
    
    if report.resilience_libraries:
        print(f"\nResilience Libraries Detected: {', '.join(report.resilience_libraries)}")
    
    if report.vulnerabilities and not args.summary:
        print(f"\nVulnerabilities ({len(report.vulnerabilities)}):")
        for v in report.vulnerabilities[:5]:
            print(f"  [{v['severity']}] {v.get('file', 'unknown')}: {v['message']}")
    
    if report.recommendations:
        print("\nRecommendations:")
        for rec in report.recommendations[:5]:
            print(f"  [{rec['priority']}] {rec['category']}: {rec['message']}")
            if rec.get('libraries'):
                print(f"         Suggested: {', '.join(rec['libraries'][:2])}")


if __name__ == '__main__':
    main()
