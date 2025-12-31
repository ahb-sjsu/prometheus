#!/usr/bin/env python3
"""
Scent Analyzer - Code Smell & Quality Detector
===============================================

Detects code quality issues that aren't bugs but indicate maintainability problems:

1. NIH (Not Invented Here) Syndrome
   - Custom implementations of standard library functions
   - Reimplementing well-known algorithms
   - Wrapper functions that add no value

2. Code Smells
   - Long functions
   - Deep nesting
   - Magic numbers
   - God classes/modules
   - Feature envy
   - Dead code patterns

3. Outdated Patterns
   - Deprecated APIs
   - Old-style syntax
   - Legacy patterns

4. Naming Issues
   - Single-letter variables (outside loops)
   - Inconsistent naming conventions
   - Misleading names
"""

import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
import json


@dataclass
class NIHPatterns:
    """Not Invented Here syndrome indicators."""
    custom_string_functions: int = 0  # my_strlen, custom_split
    custom_container_classes: int = 0  # MyList, CustomHashMap
    custom_http_clients: int = 0  # hand-rolled HTTP
    custom_json_parsers: int = 0  # manual JSON parsing
    custom_logging: int = 0  # print-based logging
    trivial_wrappers: int = 0  # def my_func(x): return other_func(x)
    reinvented_wheels: list = field(default_factory=list)  # specific examples


@dataclass
class CodeSmells:
    """Classic code smell indicators."""
    long_functions: int = 0  # functions > 50 lines
    very_long_functions: int = 0  # functions > 100 lines
    deep_nesting: int = 0  # nesting > 4 levels
    magic_numbers: int = 0  # hardcoded numbers without names
    god_classes: int = 0  # classes with too many methods
    long_parameter_lists: int = 0  # functions with > 5 params
    duplicate_code_hints: int = 0  # repeated patterns
    dead_code_hints: int = 0  # unreachable code patterns
    commented_code: int = 0  # large blocks of commented code
    global_variables: int = 0  # mutable global state


@dataclass
class OutdatedPatterns:
    """Deprecated or legacy code patterns."""
    deprecated_apis: int = 0
    old_style_classes: int = 0  # Python 2 style
    legacy_syntax: int = 0
    deprecated_imports: int = 0
    obsolete_patterns: list = field(default_factory=list)


@dataclass
class NamingIssues:
    """Naming convention problems."""
    single_char_vars: int = 0  # x, y, z (outside comprehensions)
    inconsistent_case: int = 0  # mixedCase and snake_case in same file
    misleading_names: int = 0  # patterns that suggest wrong behavior
    too_short_names: int = 0  # < 3 chars for non-loop vars
    too_long_names: int = 0  # > 40 chars


@dataclass
class FileSmellMetrics:
    """Smell metrics for a single file."""
    path: str
    language: str
    lines_of_code: int = 0
    
    nih: NIHPatterns = field(default_factory=NIHPatterns)
    smells: CodeSmells = field(default_factory=CodeSmells)
    outdated: OutdatedPatterns = field(default_factory=OutdatedPatterns)
    naming: NamingIssues = field(default_factory=NamingIssues)
    
    smell_score: float = 0.0  # 0-100, higher = more smelly (bad)
    specific_issues: list = field(default_factory=list)


@dataclass
class ScentReport:
    """Complete code smell report."""
    codebase_path: str
    timestamp: str
    
    # Aggregate counts
    total_files: int = 0
    total_loc: int = 0
    
    # Scores (0-100, higher = worse)
    nih_score: float = 0.0
    smell_score: float = 0.0
    outdated_score: float = 0.0
    naming_score: float = 0.0
    overall_smell_score: float = 0.0
    
    # Rating
    freshness_rating: str = ""  # FRESH, STALE, MOLDY, ROTTEN
    
    # Top issues
    worst_files: list = field(default_factory=list)
    top_issues: list = field(default_factory=list)
    recommendations: list = field(default_factory=list)


class ScentAnalyzer:
    """Analyzes code for smells and quality issues."""
    
    # NIH patterns by language
    NIH_PATTERNS = {
        'python': {
            'custom_string': re.compile(r'def\s+(my_|custom_)?(split|join|strip|replace|lower|upper)\s*\('),
            'custom_list': re.compile(r'class\s+(My|Custom)(List|Array|Queue|Stack|Set|Dict|Map|HashMap)\b'),
            'custom_http': re.compile(r'socket\..*connect|urllib\.request\.urlopen(?!.*timeout)'),
            'custom_json': re.compile(r'\.split\s*\(\s*["\'][:,{}]\s*["\']'),  # manual JSON parsing
            'print_logging': re.compile(r'print\s*\([^)]*\b(error|debug|info|warn)\b', re.IGNORECASE),
            'trivial_wrapper': re.compile(r'def\s+\w+\([^)]*\):\s*\n\s*return\s+\w+\([^)]*\)\s*$', re.MULTILINE),
        },
        'javascript': {
            'custom_string': re.compile(r'function\s+(my|custom)?(Split|Join|Trim|Replace)\s*\('),
            'custom_array': re.compile(r'class\s+(My|Custom)(Array|List|Queue|Stack|Set|Map)\b'),
            'custom_http': re.compile(r'new\s+XMLHttpRequest|\.open\s*\(\s*["\'](?:GET|POST)'),
            'console_logging': re.compile(r'console\.(log|warn|error)\s*\([^)]*\b(error|debug|info)\b'),
            'trivial_wrapper': re.compile(r'function\s+\w+\([^)]*\)\s*{\s*return\s+\w+\([^)]*\);\s*}'),
        },
        'c': {
            'custom_string': re.compile(r'\b(my_|custom_)(strlen|strcpy|strcmp|strcat|strdup|memcpy|memset)\s*\('),
            'custom_container': re.compile(r'struct\s+(my_|custom_)?(list|array|queue|stack|hashmap|hashtable)\b'),
            'printf_logging': re.compile(r'printf\s*\([^)]*%(s|d)[^)]*\b(error|warn|debug)\b', re.IGNORECASE),
        },
    }
    
    # Code smell patterns
    SMELL_PATTERNS = {
        'magic_number': re.compile(r'(?<!["\'\w])(?<!\.)\b(?!0\b|1\b|2\b|-1\b)([-+]?\d{2,}(?:\.\d+)?)\b(?!["\'])'),
        'deep_nesting': re.compile(r'^(\s{16,}|\t{4,})\S', re.MULTILINE),  # 4+ levels of indentation
        'commented_code': re.compile(r'^\s*(#|//)\s*(if|for|while|def|function|class|return|import)\b', re.MULTILINE),
        'todo_fixme': re.compile(r'\b(TODO|FIXME|HACK|XXX|TEMP|TEMPORARY)\b', re.IGNORECASE),
        'global_var': re.compile(r'^[A-Z_][A-Z0-9_]*\s*=\s*(?!.*\bfinal\b|.*\bconst\b)', re.MULTILINE),
        'long_line': re.compile(r'^.{120,}$', re.MULTILINE),
    }
    
    # Deprecated patterns by language
    DEPRECATED_PATTERNS = {
        'python': {
            'old_print': re.compile(r'^\s*print\s+["\']', re.MULTILINE),  # Python 2 print
            'old_except': re.compile(r'except\s+\w+\s*,\s*\w+:'),  # Python 2 except
            'has_key': re.compile(r'\.has_key\s*\('),  # dict.has_key()
            'raw_input': re.compile(r'\braw_input\s*\('),
            'xrange': re.compile(r'\bxrange\s*\('),
            'execfile': re.compile(r'\bexecfile\s*\('),
            'deprecated_import': re.compile(r'from\s+__future__\s+import|import\s+(imp|optparse|asynchat)\b'),
            'format_percent': re.compile(r'%\s*\(\s*\w+\s*\)'),  # old % formatting (debatable)
        },
        'javascript': {
            'var_keyword': re.compile(r'\bvar\s+\w+\s*='),  # should use let/const
            'document_write': re.compile(r'document\.write\s*\('),
            'eval_usage': re.compile(r'\beval\s*\('),
            'with_statement': re.compile(r'\bwith\s*\([^)]+\)\s*{'),
            'arguments_callee': re.compile(r'arguments\.callee'),
        },
        'c': {
            'gets_usage': re.compile(r'\bgets\s*\('),  # buffer overflow risk
            'sprintf': re.compile(r'\bsprintf\s*\('),  # should use snprintf
            'strcpy': re.compile(r'\bstrcpy\s*\('),  # should use strncpy
            'atoi': re.compile(r'\batoi\s*\('),  # should use strtol
        },
    }
    
    # Single char variables (excluding common loop vars)
    SINGLE_CHAR_VAR = re.compile(r'\b([a-z])\s*=\s*(?!.*\bfor\b|.*\bin\b)', re.MULTILINE)
    
    def __init__(self, codebase_path: str):
        self.codebase_path = Path(codebase_path)
        self.file_metrics: list[FileSmellMetrics] = []
    
    def analyze(self) -> ScentReport:
        """Run smell analysis."""
        from datetime import datetime
        
        report = ScentReport(
            codebase_path=str(self.codebase_path),
            timestamp=datetime.now().isoformat()
        )
        
        print(f"[SCENT] Analyzing {self.codebase_path} for code smells...")
        
        # Analyze files
        for filepath in self._get_source_files():
            metrics = self._analyze_file(filepath)
            if metrics:
                self.file_metrics.append(metrics)
        
        report.total_files = len(self.file_metrics)
        report.total_loc = sum(fm.lines_of_code for fm in self.file_metrics)
        
        # Calculate scores
        self._calculate_scores(report)
        
        # Determine rating
        self._determine_rating(report)
        
        # Generate recommendations
        self._generate_recommendations(report)
        
        print(f"  Freshness: {report.freshness_rating}")
        print(f"  Smell Score: {report.overall_smell_score:.1f}/100 (lower is better)")
        
        return report
    
    def _get_source_files(self):
        """Get source files to analyze."""
        extensions = ['.py', '.js', '.ts', '.c', '.cpp', '.h', '.java', '.go', '.rs']
        skip_dirs = ['node_modules', 'venv', '.venv', '__pycache__', '.git', 
                     'dist', 'build', 'vendor', 'third_party', 'external']
        
        for ext in extensions:
            for filepath in self.codebase_path.rglob(f'*{ext}'):
                if not any(skip in str(filepath) for skip in skip_dirs):
                    yield filepath
    
    def _get_language(self, filepath: Path) -> str:
        """Determine language from file extension."""
        ext = filepath.suffix.lower()
        mapping = {
            '.py': 'python',
            '.js': 'javascript', '.ts': 'javascript', '.jsx': 'javascript', '.tsx': 'javascript',
            '.c': 'c', '.h': 'c', '.cpp': 'c', '.hpp': 'c', '.cc': 'c',
            '.java': 'java',
            '.go': 'go',
            '.rs': 'rust',
        }
        return mapping.get(ext, 'unknown')
    
    def _analyze_file(self, filepath: Path) -> Optional[FileSmellMetrics]:
        """Analyze a single file."""
        try:
            content = filepath.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            return None
        
        lines = content.splitlines()
        language = self._get_language(filepath)
        
        metrics = FileSmellMetrics(
            path=str(filepath.relative_to(self.codebase_path)),
            language=language,
            lines_of_code=len([l for l in lines if l.strip()])
        )
        
        # Analyze NIH patterns
        self._analyze_nih(content, language, metrics)
        
        # Analyze code smells
        self._analyze_smells(content, lines, metrics)
        
        # Analyze outdated patterns
        self._analyze_outdated(content, language, metrics)
        
        # Analyze naming issues
        self._analyze_naming(content, language, metrics)
        
        # Calculate file smell score
        self._calculate_file_score(metrics)
        
        return metrics
    
    def _analyze_nih(self, content: str, language: str, metrics: FileSmellMetrics):
        """Analyze for NIH syndrome."""
        nih = metrics.nih
        patterns = self.NIH_PATTERNS.get(language, {})
        
        for name, pattern in patterns.items():
            count = len(pattern.findall(content))
            if 'string' in name:
                nih.custom_string_functions += count
            elif 'list' in name or 'array' in name or 'container' in name:
                nih.custom_container_classes += count
            elif 'http' in name:
                nih.custom_http_clients += count
            elif 'json' in name:
                nih.custom_json_parsers += count
            elif 'logging' in name or 'printf' in name:
                nih.custom_logging += count
            elif 'wrapper' in name:
                nih.trivial_wrappers += count
            
            if count > 0:
                nih.reinvented_wheels.append(f"{name}: {count}")
    
    def _analyze_smells(self, content: str, lines: list, metrics: FileSmellMetrics):
        """Analyze for code smells."""
        smells = metrics.smells
        
        # Long functions (approximate by counting lines between def/function and next def)
        function_starts = []
        for i, line in enumerate(lines):
            if re.match(r'^\s*(def|function|fn|func)\s+\w+', line):
                function_starts.append(i)
        
        for i, start in enumerate(function_starts):
            end = function_starts[i + 1] if i + 1 < len(function_starts) else len(lines)
            func_length = end - start
            if func_length > 100:
                smells.very_long_functions += 1
            elif func_length > 50:
                smells.long_functions += 1
        
        # Deep nesting
        smells.deep_nesting = len(self.SMELL_PATTERNS['deep_nesting'].findall(content))
        
        # Magic numbers
        smells.magic_numbers = len(self.SMELL_PATTERNS['magic_number'].findall(content))
        
        # Commented code
        smells.commented_code = len(self.SMELL_PATTERNS['commented_code'].findall(content))
        
        # Long parameter lists
        param_lists = re.findall(r'(?:def|function|fn|func)\s+\w+\s*\(([^)]+)\)', content)
        for params in param_lists:
            param_count = len([p for p in params.split(',') if p.strip()])
            if param_count > 5:
                smells.long_parameter_lists += 1
        
        # Global variables (rough heuristic)
        smells.global_variables = len(self.SMELL_PATTERNS['global_var'].findall(content))
        
        # TODO/FIXME etc - not a smell per se but indicates incomplete work
        smells.dead_code_hints = len(self.SMELL_PATTERNS['todo_fixme'].findall(content))
    
    def _analyze_outdated(self, content: str, language: str, metrics: FileSmellMetrics):
        """Analyze for outdated patterns."""
        outdated = metrics.outdated
        patterns = self.DEPRECATED_PATTERNS.get(language, {})
        
        for name, pattern in patterns.items():
            count = len(pattern.findall(content))
            if count > 0:
                outdated.deprecated_apis += count
                outdated.obsolete_patterns.append(f"{name}: {count}")
    
    def _analyze_naming(self, content: str, language: str, metrics: FileSmellMetrics):
        """Analyze naming issues."""
        naming = metrics.naming
        
        # Single character variables (excluding i, j, k in loops)
        single_chars = self.SINGLE_CHAR_VAR.findall(content)
        naming.single_char_vars = len([c for c in single_chars if c not in 'ijkxyn'])
        
        # Check for mixed naming conventions
        snake_case = len(re.findall(r'\b[a-z]+_[a-z]+\b', content))
        camel_case = len(re.findall(r'\b[a-z]+[A-Z][a-z]+\b', content))
        if snake_case > 10 and camel_case > 10:
            naming.inconsistent_case = 1
    
    def _calculate_file_score(self, metrics: FileSmellMetrics):
        """Calculate smell score for a file (0-100, higher = worse)."""
        score = 0
        loc = max(1, metrics.lines_of_code)
        
        # NIH (max 25 points)
        nih = metrics.nih
        nih_count = (nih.custom_string_functions + nih.custom_container_classes +
                     nih.custom_http_clients + nih.custom_json_parsers + 
                     nih.trivial_wrappers)
        score += min(25, nih_count * 5)
        
        # Code smells (max 40 points)
        smells = metrics.smells
        score += min(10, smells.very_long_functions * 5)
        score += min(5, smells.long_functions * 2)
        score += min(10, smells.deep_nesting)
        score += min(5, smells.long_parameter_lists * 2)
        score += min(5, smells.magic_numbers / loc * 100) if loc > 0 else 0
        score += min(5, smells.global_variables * 2)
        
        # Outdated patterns (max 20 points)
        score += min(20, metrics.outdated.deprecated_apis * 3)
        
        # Naming (max 15 points)
        score += min(10, metrics.naming.single_char_vars * 2)
        score += min(5, metrics.naming.inconsistent_case * 5)
        
        metrics.smell_score = min(100, score)
    
    def _calculate_scores(self, report: ScentReport):
        """Calculate aggregate scores."""
        if not self.file_metrics:
            return
        
        n = len(self.file_metrics)
        total_loc = max(1, report.total_loc)
        
        # NIH score (0-100)
        nih_total = sum(
            fm.nih.custom_string_functions + fm.nih.custom_container_classes +
            fm.nih.custom_http_clients + fm.nih.trivial_wrappers
            for fm in self.file_metrics
        )
        report.nih_score = min(100, nih_total / n * 20)
        
        # Smell score
        smell_total = sum(
            fm.smells.long_functions + fm.smells.very_long_functions * 2 +
            fm.smells.deep_nesting + fm.smells.long_parameter_lists
            for fm in self.file_metrics
        )
        report.smell_score = min(100, smell_total / n * 10)
        
        # Outdated score
        outdated_total = sum(fm.outdated.deprecated_apis for fm in self.file_metrics)
        report.outdated_score = min(100, outdated_total / n * 15)
        
        # Naming score
        naming_total = sum(fm.naming.single_char_vars for fm in self.file_metrics)
        report.naming_score = min(100, naming_total / n * 5)
        
        # Overall (weighted average)
        report.overall_smell_score = (
            report.smell_score * 0.4 +
            report.nih_score * 0.25 +
            report.outdated_score * 0.2 +
            report.naming_score * 0.15
        )
        
        # Worst files
        sorted_files = sorted(self.file_metrics, key=lambda x: -x.smell_score)
        report.worst_files = [
            {'path': fm.path, 'score': fm.smell_score, 'issues': fm.specific_issues[:3]}
            for fm in sorted_files[:10]
        ]
        
        # Top issues
        issue_counts = {}
        for fm in self.file_metrics:
            if fm.smells.very_long_functions:
                issue_counts['Very long functions'] = issue_counts.get('Very long functions', 0) + fm.smells.very_long_functions
            if fm.smells.deep_nesting:
                issue_counts['Deep nesting'] = issue_counts.get('Deep nesting', 0) + fm.smells.deep_nesting
            if fm.smells.magic_numbers > 5:
                issue_counts['Magic numbers'] = issue_counts.get('Magic numbers', 0) + 1
            if fm.outdated.deprecated_apis:
                issue_counts['Deprecated APIs'] = issue_counts.get('Deprecated APIs', 0) + fm.outdated.deprecated_apis
            if fm.nih.custom_logging:
                issue_counts['Print-based logging'] = issue_counts.get('Print-based logging', 0) + fm.nih.custom_logging
        
        report.top_issues = [
            {'issue': k, 'count': v}
            for k, v in sorted(issue_counts.items(), key=lambda x: -x[1])[:5]
        ]
    
    def _determine_rating(self, report: ScentReport):
        """Determine freshness rating."""
        score = report.overall_smell_score
        if score < 15:
            report.freshness_rating = "FRESH"  # Clean code
        elif score < 35:
            report.freshness_rating = "STALE"  # Some issues
        elif score < 60:
            report.freshness_rating = "MOLDY"  # Needs attention
        else:
            report.freshness_rating = "ROTTEN"  # Major problems
    
    def _generate_recommendations(self, report: ScentReport):
        """Generate improvement recommendations."""
        recs = []
        
        if report.smell_score > 30:
            recs.append({
                'category': 'Code Smells',
                'priority': 'HIGH',
                'recommendation': 'Break up long functions (>50 lines) and reduce nesting depth'
            })
        
        if report.nih_score > 20:
            recs.append({
                'category': 'NIH Syndrome',
                'priority': 'MEDIUM',
                'recommendation': 'Replace custom implementations with standard library equivalents'
            })
        
        if report.outdated_score > 20:
            recs.append({
                'category': 'Technical Debt',
                'priority': 'MEDIUM',
                'recommendation': 'Update deprecated APIs and legacy patterns'
            })
        
        if report.naming_score > 30:
            recs.append({
                'category': 'Naming',
                'priority': 'LOW',
                'recommendation': 'Use descriptive variable names, establish consistent conventions'
            })
        
        report.recommendations = recs
    
    def save_report(self, report: ScentReport, output_path: str) -> str:
        """Save report to JSON."""
        from dataclasses import asdict
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(report), f, indent=2, default=str)
        return output_path


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Scent - Code Smell Analyzer")
    parser.add_argument('path', help='Path to codebase')
    parser.add_argument('-o', '--output', help='Output JSON path')
    
    args = parser.parse_args()
    
    analyzer = ScentAnalyzer(args.path)
    report = analyzer.analyze()
    
    print("\n" + "="*70)
    print("SCENT CODE SMELL REPORT")
    print("="*70)
    
    # Freshness emoji
    emoji = {'FRESH': '🌿', 'STALE': '🍂', 'MOLDY': '🍄', 'ROTTEN': '🦨'}.get(report.freshness_rating, '❓')
    print(f"\n{emoji} Freshness: {report.freshness_rating}")
    print(f"Overall Smell Score: {report.overall_smell_score:.0f}/100 (lower is better)")
    
    print("\nCategory Scores (lower is better):")
    for cat, score in [
        ('Code Smells', report.smell_score),
        ('NIH Syndrome', report.nih_score),
        ('Outdated Patterns', report.outdated_score),
        ('Naming Issues', report.naming_score),
    ]:
        bar = "█" * int(score / 5) + "░" * (20 - int(score / 5))
        status = "✓" if score < 20 else "⚠" if score < 40 else "✗"
        print(f"  {status} {cat:20} [{bar}] {score:.0f}")
    
    if report.top_issues:
        print("\nTop Issues:")
        for issue in report.top_issues[:5]:
            print(f"  • {issue['issue']}: {issue['count']} occurrences")
    
    if report.worst_files:
        print("\nSmelliest Files:")
        for f in report.worst_files[:5]:
            print(f"  • {f['path']}: {f['score']:.0f}/100")
    
    if report.recommendations:
        print("\nRecommendations:")
        for rec in report.recommendations:
            print(f"  [{rec['priority']}] {rec['category']}: {rec['recommendation']}")
    
    if args.output:
        analyzer.save_report(report, args.output)
        print(f"\nReport saved to: {args.output}")


if __name__ == '__main__':
    main()
