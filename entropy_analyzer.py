#!/usr/bin/env python3
"""
Complexity Fitness Analyzer
============================
A rigorous ETL pipeline that measures whether a codebase is too complex for its task.

Core thesis (from Shannon/thermodynamics):
- Simpler systems are more reliable
- Complexity should be proportional to task requirements
- Excess complexity = excess failure modes

Pipeline stages:
1. EXTRACT: Parse codebase, extract AST, gather metrics
2. TRANSFORM: Normalize metrics, compute ratios, estimate task complexity
3. LOAD: Generate report with verdicts and recommendations

"""

import ast
import gzip
import json
import logging
import math
import re
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path

from ignore_patterns import load_ignore_patterns, should_exclude

logger = logging.getLogger(__name__)


# =============================================================================
# DATA MODELS
# =============================================================================


@dataclass
class FileMetrics:
    """Metrics for a single source file."""

    path: str
    language: str
    lines_of_code: int = 0
    lines_total: int = 0
    blank_lines: int = 0
    comment_lines: int = 0

    # Complexity metrics
    cyclomatic_complexity: float = 0.0
    cognitive_complexity: float = 0.0
    halstead_volume: float = 0.0
    halstead_difficulty: float = 0.0
    halstead_effort: float = 0.0
    halstead_bugs: float = 0.0
    maintainability_index: float = 0.0

    # Structural metrics
    num_functions: int = 0
    num_classes: int = 0
    max_nesting_depth: int = 0
    avg_function_length: float = 0.0

    # Coupling metrics
    imports: int = 0
    dependencies: list = field(default_factory=list)

    # Shannon/information metrics
    token_entropy: float = 0.0
    compression_ratio: float = 0.0


@dataclass
class TaskMetrics:
    """Metrics estimating task complexity from tests/specs."""

    num_test_files: int = 0
    num_test_cases: int = 0
    num_assertions: int = 0
    api_endpoints: int = 0
    distinct_features: int = 0
    estimated_function_points: float = 0.0


@dataclass
class CodebaseMetrics:
    """Aggregate metrics for entire codebase."""

    total_files: int = 0
    total_loc: int = 0
    total_functions: int = 0
    total_classes: int = 0

    # Aggregated complexity
    avg_cyclomatic: float = 0.0
    max_cyclomatic: float = 0.0
    avg_cognitive: float = 0.0
    total_halstead_bugs: float = 0.0
    avg_maintainability: float = 0.0

    # Information theoretic
    codebase_entropy: float = 0.0
    total_compression_ratio: float = 0.0

    # Coupling
    avg_imports_per_file: float = 0.0
    dependency_graph_density: float = 0.0


@dataclass
class FitnessReport:
    """Final verdict on complexity fitness."""

    codebase_path: str
    timestamp: str

    # Raw metrics
    codebase_metrics: CodebaseMetrics = None
    task_metrics: TaskMetrics = None
    file_metrics: list = field(default_factory=list)

    # Fitness ratios (the key outputs)
    complexity_per_feature: float = 0.0
    complexity_per_test: float = 0.0
    loc_per_function_point: float = 0.0

    # Shannon-inspired metrics
    bits_per_feature: float = 0.0
    redundancy_ratio: float = 0.0

    # Verdicts
    overall_verdict: str = ""
    risk_level: str = ""  # LOW, MEDIUM, HIGH, CRITICAL
    recommendations: list = field(default_factory=list)
    hotspots: list = field(default_factory=list)  # Files needing attention


# =============================================================================
# EXTRACT STAGE
# =============================================================================


class Extractor:
    """Extract raw metrics from codebase."""

    LANGUAGE_EXTENSIONS = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".jsx": "javascript",
        ".tsx": "typescript",
        ".java": "java",
        ".go": "go",
        ".rs": "rust",
        ".c": "c",
        ".cpp": "cpp",
        ".h": "c",
        ".hpp": "cpp",
        ".rb": "ruby",
        ".php": "php",
    }

    def __init__(self, codebase_path: str):
        self.codebase_path = Path(codebase_path)
        self.file_metrics: list[FileMetrics] = []
        self.task_metrics = TaskMetrics()

    def extract(self) -> tuple[list[FileMetrics], TaskMetrics]:
        """Run full extraction."""
        self._discover_files()
        self._extract_task_metrics()
        return self.file_metrics, self.task_metrics

    def _discover_files(self):
        """Find and analyze all source files."""
        # Load ignore patterns from .prometheusignore or defaults
        ignore_spec = load_ignore_patterns(self.codebase_path)

        for ext, lang in self.LANGUAGE_EXTENSIONS.items():
            for filepath in self.codebase_path.rglob(f"*{ext}"):
                # Check if file should be excluded via .prometheusignore
                if should_exclude(filepath, self.codebase_path, ignore_spec):
                    continue

                metrics = self._analyze_file(filepath, lang)
                if metrics:
                    self.file_metrics.append(metrics)

    def _analyze_file(self, filepath: Path, language: str) -> FileMetrics | None:
        """Extract all metrics for a single file."""
        try:
            content = filepath.read_text(encoding="utf-8", errors="ignore")
        except (OSError, UnicodeDecodeError) as e:
            logger.debug(f"Could not read {filepath}: {e}")
            return None

        metrics = FileMetrics(path=str(filepath.relative_to(self.codebase_path)), language=language)

        # Basic line counts
        lines = content.splitlines()
        metrics.lines_total = len(lines)
        metrics.blank_lines = sum(1 for l in lines if not l.strip())
        metrics.lines_of_code = metrics.lines_total - metrics.blank_lines

        # Language-specific analysis
        if language == "python":
            self._analyze_python(content, metrics)
        else:
            self._analyze_generic(content, metrics, language)

        # Shannon metrics (language-agnostic)
        metrics.token_entropy = self._calculate_entropy(content)
        metrics.compression_ratio = self._calculate_compression_ratio(content)

        return metrics

    def _analyze_python(self, content: str, metrics: FileMetrics):
        """Deep analysis for Python files using AST."""
        import warnings

        try:
            # Suppress SyntaxWarnings from invalid escape sequences in analyzed code
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=SyntaxWarning)
                tree = ast.parse(content)
        except SyntaxError:
            return

        # Count structures
        functions = [
            n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
        imports = [n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))]

        metrics.num_functions = len(functions)
        metrics.num_classes = len(classes)
        metrics.imports = len(imports)

        # Extract dependencies
        for node in imports:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    metrics.dependencies.append(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom) and node.module:
                metrics.dependencies.append(node.module.split(".")[0])

        # Calculate nesting depth
        metrics.max_nesting_depth = self._max_depth(tree)

        # Average function length
        if functions:
            func_lengths = []
            for func in functions:
                func_lengths.append(func.end_lineno - func.lineno + 1)
            metrics.avg_function_length = sum(func_lengths) / len(func_lengths)

        # Use radon for complexity metrics
        self._radon_metrics(content, metrics)

    def _analyze_generic(self, content: str, metrics: FileMetrics, language: str):
        """Generic analysis using lizard for non-Python files."""
        self._lizard_metrics(content, metrics, language)

        # Simple structural counts via regex
        metrics.num_functions = len(
            re.findall(r"\b(function|def|fn|func|void|int|string|bool)\s+\w+\s*\(", content)
        )
        metrics.num_classes = len(re.findall(r"\bclass\s+\w+", content))
        metrics.imports = len(re.findall(r"\b(import|require|include|using)\b", content))

    def _max_depth(self, node, current_depth=0) -> int:
        """Calculate maximum nesting depth in AST."""
        max_child_depth = current_depth
        for child in ast.iter_child_nodes(node):
            if isinstance(
                child,
                (ast.If, ast.For, ast.While, ast.With, ast.Try, ast.FunctionDef, ast.ClassDef),
            ):
                child_depth = self._max_depth(child, current_depth + 1)
                max_child_depth = max(max_child_depth, child_depth)
            else:
                child_depth = self._max_depth(child, current_depth)
                max_child_depth = max(max_child_depth, child_depth)
        return max_child_depth

    def _radon_metrics(self, content: str, metrics: FileMetrics):
        """Use radon for Python complexity metrics."""
        try:
            from radon.complexity import cc_visit
            from radon.metrics import h_visit, mi_visit
            from radon.raw import analyze
        except ImportError:
            # Radon not installed - use fallback
            if not getattr(self, "_radon_warned", False):
                print(
                    "  [WARNING] radon not installed. Using AST-based fallback. For better metrics: pip install radon"
                )
                self._radon_warned = True
            self._fallback_cyclomatic(content, metrics)
            return

        try:
            # Cyclomatic complexity
            cc_results = cc_visit(content)
            if cc_results:
                complexities = [block.complexity for block in cc_results]
                metrics.cyclomatic_complexity = sum(complexities) / len(complexities)

            # Maintainability index
            metrics.maintainability_index = mi_visit(content, multi=True)

            # Halstead metrics
            h_results = h_visit(content)
            if h_results.total:
                metrics.halstead_volume = h_results.total.volume or 0
                metrics.halstead_difficulty = h_results.total.difficulty or 0
                metrics.halstead_effort = h_results.total.effort or 0
                metrics.halstead_bugs = h_results.total.bugs or 0

            # Raw metrics for comment lines
            raw = analyze(content)
            metrics.comment_lines = raw.comments + raw.multi

        except Exception as e:
            # Radon analysis failed - use fallback
            import sys

            print(f"  [DEBUG] Radon failed on {metrics.path}: {e}", file=sys.stderr)
            self._fallback_cyclomatic(content, metrics)

    def _fallback_cyclomatic(self, content: str, metrics: FileMetrics):
        """
        Calculate cyclomatic complexity using AST when radon isn't available.

        Cyclomatic complexity = E - N + 2P where:
        - E = edges, N = nodes, P = connected components

        For a single function: CC = 1 + (decision points)
        Decision points: if, elif, for, while, and, or, except, with, assert,
                        comprehensions, ternary operators
        """
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return

        class ComplexityVisitor(ast.NodeVisitor):
            def __init__(self):
                self.complexities = []
                self.current_complexity = 0

            def _count_bool_ops(self, node):
                """Count boolean operators which add decision points."""
                count = 0
                for child in ast.walk(node):
                    if isinstance(child, ast.BoolOp):
                        # 'and' and 'or' each add a decision point per operand-1
                        count += len(child.values) - 1
                return count

            def visit_FunctionDef(self, node):
                old_complexity = self.current_complexity
                self.current_complexity = 1  # Base complexity

                for child in ast.walk(node):
                    # Decision points
                    if isinstance(child, (ast.If, ast.IfExp)):  # if and ternary
                        self.current_complexity += 1
                    elif isinstance(child, ast.For):
                        self.current_complexity += 1
                    elif isinstance(child, ast.While):
                        self.current_complexity += 1
                    elif isinstance(child, ast.ExceptHandler):
                        self.current_complexity += 1
                    elif isinstance(child, ast.With):
                        self.current_complexity += 1
                    elif isinstance(child, ast.Assert):
                        self.current_complexity += 1
                    elif isinstance(
                        child, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)
                    ):
                        self.current_complexity += 1
                    elif isinstance(child, ast.BoolOp):
                        # and/or add complexity
                        self.current_complexity += len(child.values) - 1

                self.complexities.append(self.current_complexity)
                self.current_complexity = old_complexity

            visit_AsyncFunctionDef = visit_FunctionDef

        visitor = ComplexityVisitor()
        visitor.visit(tree)

        if visitor.complexities:
            metrics.cyclomatic_complexity = sum(visitor.complexities) / len(visitor.complexities)

        # Fallback maintainability estimate based on LOC and complexity
        # MI = 171 - 5.2*ln(V) - 0.23*CC - 16.2*ln(LOC)
        # Simplified: we estimate based on LOC and complexity
        loc = metrics.lines_of_code or 1
        cc = metrics.cyclomatic_complexity or 1
        if loc > 0:
            import math

            # Simplified MI formula
            metrics.maintainability_index = max(
                0, min(100, 100 - (math.log(loc + 1) * 8) - (cc * 2))
            )

    def _lizard_metrics(self, content: str, metrics: FileMetrics, language: str):
        """Use lizard for complexity metrics on non-Python files."""
        try:
            import lizard

            # Map our language names to lizard's
            lang_map = {
                "javascript": "javascript",
                "typescript": "typescript",
                "java": "java",
                "go": "go",
                "rust": "rust",
                "c": "c",
                "cpp": "cpp",
            }

            analysis = lizard.analyze_file.analyze_source_code(f"temp.{language[:2]}", content)

            if analysis.function_list:
                complexities = [f.cyclomatic_complexity for f in analysis.function_list]
                metrics.cyclomatic_complexity = sum(complexities) / len(complexities)
                metrics.num_functions = len(analysis.function_list)

                lengths = [f.nloc for f in analysis.function_list]
                metrics.avg_function_length = sum(lengths) / len(lengths)

        except ImportError:
            # Lizard not available - use regex-based fallback
            if not getattr(self, "_lizard_warned", False):
                logger.debug("lizard not installed - using regex-based complexity estimate")
                self._lizard_warned = True
            self._fallback_complexity_generic(content, metrics, language)
        except Exception as e:
            logger.debug(f"lizard analysis failed: {e}")
            self._fallback_complexity_generic(content, metrics, language)

    def _fallback_complexity_generic(self, content: str, metrics: FileMetrics, language: str):
        """
        Estimate cyclomatic complexity for non-Python files using regex.

        This is a rough estimate based on counting decision points.
        """
        # Count decision points using regex patterns
        decision_patterns = [
            r"\bif\s*\(",  # if statements
            r"\belse\s+if\s*\(",  # else if
            r"\belif\s*\(",  # Python-style elif
            r"\bfor\s*\(",  # for loops
            r"\bwhile\s*\(",  # while loops
            r"\bcase\s+\w+:",  # switch case
            r"\bcatch\s*\(",  # catch blocks
            r"\b\?\s*[^:]+:",  # ternary operators
            r"\b&&\b",  # logical and
            r"\b\|\|\b",  # logical or
        ]

        decision_count = 0
        for pattern in decision_patterns:
            decision_count += len(re.findall(pattern, content))

        # Count functions for averaging
        func_patterns = {
            "javascript": r"\bfunction\s+\w+\s*\(|const\s+\w+\s*=\s*(?:async\s*)?\([^)]*\)\s*=>",
            "typescript": r"\bfunction\s+\w+\s*\(|(?:const|let)\s+\w+\s*=\s*(?:async\s*)?\([^)]*\)\s*=>",
            "java": r"(?:public|private|protected)?\s*(?:static\s+)?(?:\w+\s+)+\w+\s*\([^)]*\)\s*\{",
            "go": r"\bfunc\s+(?:\([^)]+\)\s*)?\w+\s*\(",
            "rust": r"\bfn\s+\w+\s*(?:<[^>]+>)?\s*\(",
            "c": r"(?:\w+\s+)+\w+\s*\([^)]*\)\s*\{",
            "cpp": r"(?:\w+\s+)+\w+\s*\([^)]*\)\s*\{",
        }

        func_pattern = func_patterns.get(language, r"\bfunction\s+\w+\s*\(")
        func_count = len(re.findall(func_pattern, content))

        if func_count > 0:
            # Average complexity = 1 (base) + decisions per function
            metrics.cyclomatic_complexity = 1 + (decision_count / func_count)
            metrics.num_functions = func_count
        elif decision_count > 0:
            # No functions found but has decisions - estimate
            metrics.cyclomatic_complexity = 1 + decision_count * 0.1
        else:
            metrics.cyclomatic_complexity = 1.0  # Base complexity

    def _calculate_entropy(self, content: str) -> float:
        """Calculate Shannon entropy of token distribution."""
        if not content:
            return 0.0

        # Tokenize (simple word-based)
        tokens = re.findall(r"\b\w+\b", content.lower())
        if not tokens:
            return 0.0

        # Calculate frequency distribution
        freq = defaultdict(int)
        for token in tokens:
            freq[token] += 1

        total = len(tokens)
        entropy = 0.0

        for count in freq.values():
            p = count / total
            if p > 0:
                entropy -= p * math.log2(p)

        return entropy

    def _calculate_compression_ratio(self, content: str) -> float:
        """Calculate compression ratio (original/compressed size)."""
        if not content:
            return 1.0

        original = len(content.encode("utf-8"))
        compressed = len(gzip.compress(content.encode("utf-8")))

        if compressed == 0:
            return 1.0

        return original / compressed

    def _extract_task_metrics(self):
        """Estimate task complexity from tests and structure."""
        # Count test files and cases
        test_patterns = [
            "test_*.py",
            "*_test.py",
            "*.test.js",
            "*.spec.js",
            "*Test.java",
            "*_test.go",
            "*_test.rs",
        ]

        for pattern in test_patterns:
            for filepath in self.codebase_path.rglob(pattern):
                if "node_modules" in str(filepath):
                    continue
                self.task_metrics.num_test_files += 1

                try:
                    content = filepath.read_text(encoding="utf-8", errors="ignore")
                    # Count test functions/methods
                    self.task_metrics.num_test_cases += len(
                        re.findall(r"\b(def test_|it\(|test\(|func Test|#\[test\])", content)
                    )
                    # Count assertions
                    self.task_metrics.num_assertions += len(
                        re.findall(r"\b(assert|expect|should|Assert\.|assertEquals)", content)
                    )
                except (OSError, UnicodeDecodeError) as e:
                    logger.debug(f"Could not read test file {filepath}: {e}")

        # Estimate API endpoints (REST patterns)
        for filepath in self.codebase_path.rglob("*.py"):
            if "node_modules" in str(filepath):
                continue
            try:
                content = filepath.read_text(encoding="utf-8", errors="ignore")
                self.task_metrics.api_endpoints += len(
                    re.findall(r"@(app|router)\.(get|post|put|delete|patch)\(", content)
                )
            except (OSError, UnicodeDecodeError) as e:
                logger.debug(f"Could not read {filepath}: {e}")

        # Estimate function points (simplified COCOMO-style)
        # FP ≈ (test_cases * 0.5) + (endpoints * 2) + (distinct_imports * 0.1)
        distinct_imports = set()
        for fm in self.file_metrics:
            distinct_imports.update(fm.dependencies)

        self.task_metrics.distinct_features = len(distinct_imports)
        self.task_metrics.estimated_function_points = (
            self.task_metrics.num_test_cases * 0.5
            + self.task_metrics.api_endpoints * 2
            + len(distinct_imports) * 0.1
        )

        # Minimum of 1 to avoid division by zero
        if self.task_metrics.estimated_function_points < 1:
            self.task_metrics.estimated_function_points = max(
                1, sum(1 for fm in self.file_metrics if fm.num_functions > 0)
            )


# =============================================================================
# TRANSFORM STAGE
# =============================================================================


class Transformer:
    """Transform raw metrics into fitness indicators."""

    def __init__(self, file_metrics: list[FileMetrics], task_metrics: TaskMetrics):
        self.file_metrics = file_metrics
        self.task_metrics = task_metrics
        self.codebase_metrics = CodebaseMetrics()

    def transform(self) -> CodebaseMetrics:
        """Aggregate and normalize all metrics."""
        if not self.file_metrics:
            return self.codebase_metrics

        # Totals
        self.codebase_metrics.total_files = len(self.file_metrics)
        self.codebase_metrics.total_loc = sum(fm.lines_of_code for fm in self.file_metrics)
        self.codebase_metrics.total_functions = sum(fm.num_functions for fm in self.file_metrics)
        self.codebase_metrics.total_classes = sum(fm.num_classes for fm in self.file_metrics)

        # Complexity aggregates
        complexities = [
            fm.cyclomatic_complexity for fm in self.file_metrics if fm.cyclomatic_complexity > 0
        ]
        if complexities:
            self.codebase_metrics.avg_cyclomatic = sum(complexities) / len(complexities)
            self.codebase_metrics.max_cyclomatic = max(complexities)

        cognitive = [
            fm.cognitive_complexity for fm in self.file_metrics if fm.cognitive_complexity > 0
        ]
        if cognitive:
            self.codebase_metrics.avg_cognitive = sum(cognitive) / len(cognitive)

        self.codebase_metrics.total_halstead_bugs = sum(
            fm.halstead_bugs for fm in self.file_metrics
        )

        maintainability = [
            fm.maintainability_index for fm in self.file_metrics if fm.maintainability_index > 0
        ]
        if maintainability:
            self.codebase_metrics.avg_maintainability = sum(maintainability) / len(maintainability)

        # Information theoretic
        entropies = [fm.token_entropy for fm in self.file_metrics if fm.token_entropy > 0]
        if entropies:
            self.codebase_metrics.codebase_entropy = sum(entropies) / len(entropies)

        compressions = [
            fm.compression_ratio for fm in self.file_metrics if fm.compression_ratio > 0
        ]
        if compressions:
            self.codebase_metrics.total_compression_ratio = sum(compressions) / len(compressions)

        # Coupling
        total_imports = sum(fm.imports for fm in self.file_metrics)
        self.codebase_metrics.avg_imports_per_file = total_imports / len(self.file_metrics)

        # Dependency graph density (edges / possible edges)
        all_deps = set()
        for fm in self.file_metrics:
            all_deps.update(fm.dependencies)
        n = len(self.file_metrics)
        if n > 1:
            possible_edges = n * (n - 1)
            actual_edges = total_imports
            self.codebase_metrics.dependency_graph_density = actual_edges / possible_edges

        return self.codebase_metrics


# =============================================================================
# ANALYZE/LOAD STAGE
# =============================================================================


class Analyzer:
    """Generate fitness verdicts and recommendations."""

    # Thresholds based on industry research and Shannon principles
    THRESHOLDS = {
        "cyclomatic_low": 5,
        "cyclomatic_medium": 10,
        "cyclomatic_high": 20,
        "maintainability_good": 65,
        "maintainability_poor": 40,
        "loc_per_fp_good": 50,
        "loc_per_fp_poor": 150,
        "entropy_low": 4.0,  # Low entropy = repetitive code
        "entropy_high": 8.0,  # High entropy = possibly random/complex
        "compression_redundant": 4.0,  # High ratio = lots of redundancy
    }

    def __init__(
        self,
        codebase_path: str,
        file_metrics: list[FileMetrics],
        task_metrics: TaskMetrics,
        codebase_metrics: CodebaseMetrics,
    ):
        self.codebase_path = codebase_path
        self.file_metrics = file_metrics
        self.task_metrics = task_metrics
        self.codebase_metrics = codebase_metrics

    def analyze(self) -> FitnessReport:
        """Generate complete fitness report."""
        from datetime import datetime

        report = FitnessReport(
            codebase_path=self.codebase_path,
            timestamp=datetime.now().isoformat(),
            codebase_metrics=self.codebase_metrics,
            task_metrics=self.task_metrics,
            file_metrics=[asdict(fm) for fm in self.file_metrics],
        )

        # Calculate fitness ratios
        self._calculate_ratios(report)

        # Identify hotspots
        self._identify_hotspots(report)

        # Generate verdicts
        self._generate_verdicts(report)

        return report

    def _calculate_ratios(self, report: FitnessReport):
        """Calculate key complexity-to-task ratios."""
        cm = self.codebase_metrics
        tm = self.task_metrics

        # Complexity per feature
        if tm.estimated_function_points > 0:
            total_complexity = cm.avg_cyclomatic * cm.total_functions
            report.complexity_per_feature = total_complexity / tm.estimated_function_points
            report.loc_per_function_point = cm.total_loc / tm.estimated_function_points

        # Complexity per test
        if tm.num_test_cases > 0:
            report.complexity_per_test = cm.avg_cyclomatic / tm.num_test_cases

        # Bits per feature (Shannon-inspired)
        if tm.estimated_function_points > 0:
            # Total information content ≈ LOC * entropy
            total_bits = cm.total_loc * cm.codebase_entropy
            report.bits_per_feature = total_bits / tm.estimated_function_points

        # Redundancy ratio (high compression = high redundancy)
        report.redundancy_ratio = cm.total_compression_ratio

    def _identify_hotspots(self, report: FitnessReport):
        """Find files that are disproportionately complex."""
        hotspots = []

        for fm in self.file_metrics:
            issues = []

            if fm.cyclomatic_complexity > self.THRESHOLDS["cyclomatic_high"]:
                issues.append(f"Very high cyclomatic complexity: {fm.cyclomatic_complexity:.1f}")
            elif fm.cyclomatic_complexity > self.THRESHOLDS["cyclomatic_medium"]:
                issues.append(f"High cyclomatic complexity: {fm.cyclomatic_complexity:.1f}")

            if (
                fm.maintainability_index > 0
                and fm.maintainability_index < self.THRESHOLDS["maintainability_poor"]
            ):
                issues.append(f"Poor maintainability index: {fm.maintainability_index:.1f}")

            if fm.max_nesting_depth > 4:
                issues.append(f"Deep nesting: {fm.max_nesting_depth} levels")

            if fm.halstead_bugs > 1.0:
                issues.append(f"High estimated bug count: {fm.halstead_bugs:.2f}")

            if issues:
                hotspots.append(
                    {
                        "file": fm.path,
                        "issues": issues,
                        "severity": "HIGH" if len(issues) > 2 else "MEDIUM",
                    }
                )

        # Sort by number of issues
        report.hotspots = sorted(hotspots, key=lambda x: len(x["issues"]), reverse=True)[:10]

    def _generate_verdicts(self, report: FitnessReport):
        """Generate overall verdict and recommendations."""
        cm = self.codebase_metrics

        # Risk scoring
        risk_score = 0
        recommendations = []

        # Check cyclomatic complexity
        if cm.avg_cyclomatic > self.THRESHOLDS["cyclomatic_high"]:
            risk_score += 3
            recommendations.append(
                "CRITICAL: Average cyclomatic complexity is very high. "
                "Break down complex functions into smaller units."
            )
        elif cm.avg_cyclomatic > self.THRESHOLDS["cyclomatic_medium"]:
            risk_score += 2
            recommendations.append(
                "WARNING: Average cyclomatic complexity is elevated. "
                "Consider refactoring functions with complexity > 10."
            )

        # Check maintainability
        if cm.avg_maintainability > 0:
            if cm.avg_maintainability < self.THRESHOLDS["maintainability_poor"]:
                risk_score += 3
                recommendations.append(
                    "CRITICAL: Low maintainability index indicates the code will be "
                    "difficult and error-prone to modify."
                )
            elif cm.avg_maintainability < self.THRESHOLDS["maintainability_good"]:
                risk_score += 1
                recommendations.append(
                    "NOTE: Maintainability index could be improved through "
                    "better documentation and smaller functions."
                )

        # Check LOC per function point
        if report.loc_per_function_point > self.THRESHOLDS["loc_per_fp_poor"]:
            risk_score += 2
            recommendations.append(
                f"WARNING: {report.loc_per_function_point:.0f} lines per function point "
                f"suggests over-engineering. Industry standard is ~50."
            )

        # Check entropy (information density)
        if cm.codebase_entropy < self.THRESHOLDS["entropy_low"]:
            risk_score += 1
            recommendations.append(
                "NOTE: Low token entropy suggests repetitive code. "
                "Consider DRY refactoring and abstractions."
            )
        elif cm.codebase_entropy > self.THRESHOLDS["entropy_high"]:
            risk_score += 1
            recommendations.append(
                "NOTE: High token entropy may indicate inconsistent naming "
                "or overly complex logic."
            )

        # Check redundancy
        if report.redundancy_ratio > self.THRESHOLDS["compression_redundant"]:
            risk_score += 1
            recommendations.append(
                "NOTE: High compression ratio indicates redundant code. "
                "Look for copy-paste patterns to abstract."
            )

        # Check estimated bugs
        if cm.total_halstead_bugs > cm.total_functions * 0.5:
            risk_score += 2
            recommendations.append(
                f"WARNING: Halstead analysis estimates ~{cm.total_halstead_bugs:.1f} bugs "
                "based on code complexity."
            )

        # Determine risk level
        if risk_score >= 8:
            report.risk_level = "CRITICAL"
        elif risk_score >= 5:
            report.risk_level = "HIGH"
        elif risk_score >= 3:
            report.risk_level = "MEDIUM"
        else:
            report.risk_level = "LOW"

        # Overall verdict
        if report.risk_level == "CRITICAL":
            report.overall_verdict = (
                "This codebase exhibits excessive complexity relative to its apparent "
                "functionality. Per Shannon's principle, high complexity = high failure "
                "probability. Significant refactoring recommended before adding features."
            )
        elif report.risk_level == "HIGH":
            report.overall_verdict = (
                "Complexity is higher than warranted for the task at hand. "
                "Error rates will be elevated. Targeted refactoring of hotspots recommended."
            )
        elif report.risk_level == "MEDIUM":
            report.overall_verdict = (
                "Complexity is within acceptable bounds but trending toward excess. "
                "Monitor during future development and address hotspots proactively."
            )
        else:
            report.overall_verdict = (
                "Complexity appears well-matched to task requirements. "
                "The codebase follows the principle that simplicity enables reliability."
            )

        report.recommendations = recommendations


# =============================================================================
# PIPELINE ORCHESTRATION
# =============================================================================


class ComplexityFitnessPipeline:
    """
    Main ETL pipeline orchestrator.

    Implements the pragmatic proof:
    - Extract measurable quantities from code
    - Transform into Shannon-inspired fitness metrics
    - Load into actionable report with verdicts
    """

    def __init__(self, codebase_path: str):
        self.codebase_path = codebase_path

    def run(self) -> FitnessReport:
        """Execute full pipeline."""
        print(f"[EXTRACT] Analyzing {self.codebase_path}...")
        extractor = Extractor(self.codebase_path)
        file_metrics, task_metrics = extractor.extract()
        print(f"  Found {len(file_metrics)} source files")

        print("[TRANSFORM] Computing aggregate metrics...")
        transformer = Transformer(file_metrics, task_metrics)
        codebase_metrics = transformer.transform()
        print(f"  Total LOC: {codebase_metrics.total_loc}")
        print(f"  Avg complexity: {codebase_metrics.avg_cyclomatic:.2f}")

        print("[ANALYZE] Generating fitness report...")
        analyzer = Analyzer(self.codebase_path, file_metrics, task_metrics, codebase_metrics)
        report = analyzer.analyze()
        print(f"  Risk level: {report.risk_level}")

        return report

    def run_and_save(self, output_path: str = None) -> str:
        """Run pipeline and save JSON report."""
        report = self.run()

        if output_path is None:
            output_path = f"complexity_report_{Path(self.codebase_path).name}.json"

        # Convert to JSON-serializable dict
        report_dict = {
            "codebase_path": report.codebase_path,
            "timestamp": report.timestamp,
            "risk_level": report.risk_level,
            "overall_verdict": report.overall_verdict,
            "recommendations": report.recommendations,
            "hotspots": report.hotspots,
            "metrics": {
                "codebase": asdict(report.codebase_metrics) if report.codebase_metrics else {},
                "task": asdict(report.task_metrics) if report.task_metrics else {},
            },
            "fitness_ratios": {
                "complexity_per_feature": report.complexity_per_feature,
                "complexity_per_test": report.complexity_per_test,
                "loc_per_function_point": report.loc_per_function_point,
                "bits_per_feature": report.bits_per_feature,
                "redundancy_ratio": report.redundancy_ratio,
            },
            "file_details": report.file_metrics,
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report_dict, f, indent=2)

        return output_path


# =============================================================================
# CLI INTERFACE
# =============================================================================


def main():
    """Command-line interface."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Analyze codebase complexity fitness using Shannon-inspired metrics"
    )
    parser.add_argument("path", help="Path to codebase to analyze")
    parser.add_argument("-o", "--output", help="Output JSON report path")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--summary", action="store_true", help="Print summary only")

    args = parser.parse_args()

    pipeline = ComplexityFitnessPipeline(args.path)

    if args.output:
        output_path = pipeline.run_and_save(args.output)
        print(f"\nReport saved to: {output_path}")
    else:
        report = pipeline.run()

        print("\n" + "=" * 70)
        print("COMPLEXITY FITNESS REPORT")
        print("=" * 70)
        print(f"\nCodebase: {report.codebase_path}")
        print(f"Risk Level: {report.risk_level}")
        print(f"\n{report.overall_verdict}")

        if report.recommendations:
            print("\nRecommendations:")
            for i, rec in enumerate(report.recommendations, 1):
                print(f"  {i}. {rec}")

        if report.hotspots and not args.summary:
            print("\nHotspots (files needing attention):")
            for hs in report.hotspots[:5]:
                print(f"  • {hs['file']}")
                for issue in hs["issues"]:
                    print(f"      - {issue}")

        if not args.summary:
            print("\nKey Metrics:")
            cm = report.codebase_metrics
            print(f"  Total files: {cm.total_files}")
            print(f"  Total LOC: {cm.total_loc}")
            print(f"  Avg cyclomatic complexity: {cm.avg_cyclomatic:.2f}")
            print(f"  Avg maintainability index: {cm.avg_maintainability:.1f}")
            print(f"  LOC per function point: {report.loc_per_function_point:.1f}")
            print(f"  Estimated bugs (Halstead): {cm.total_halstead_bugs:.1f}")
            print(f"  Code entropy: {cm.codebase_entropy:.2f} bits/token")
            print(f"  Compression ratio: {cm.total_compression_ratio:.2f}x")


if __name__ == "__main__":
    main()
