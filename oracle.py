#!/usr/bin/env python3
"""
Oracle - Production Readiness Analyzer
======================================

Analyzes what's ACTUALLY IN THE CODEBASE to assess production readiness.
Does not guess about external systems - only analyzes repo contents.
"""

import re
import logging
from pathlib import Path
from dataclasses import dataclass, field
import json

logger = logging.getLogger(__name__)


@dataclass
class ObservabilityInstrumentation:
    """What observability is instrumented IN THE CODE."""

    prometheus_client: bool = False
    statsd_client: bool = False
    datadog_client: bool = False
    opentelemetry: bool = False
    custom_metrics: int = 0
    structured_logging: bool = False
    log_levels_used: set = field(default_factory=set)
    context_logging: int = 0
    trace_instrumentation: bool = False
    span_creation: int = 0
    health_endpoint: bool = False
    readiness_endpoint: bool = False


@dataclass
class DefensiveCoding:
    """Defensive coding patterns found in code."""

    input_validation: int = 0
    null_checks: int = 0
    bounds_checks: int = 0
    type_assertions: int = 0
    resource_cleanup: int = 0
    assertions: int = 0


@dataclass
class ConfigurationHygiene:
    """How configuration is handled."""

    env_var_usage: int = 0
    hardcoded_strings: int = 0
    dotenv_usage: bool = False


@dataclass
class DeploymentArtifacts:
    """Deployment-related files in repo."""

    dockerfile: bool = False
    dockerfile_quality: int = 0
    docker_compose: bool = False
    kubernetes_manifests: int = 0
    helm_chart: bool = False
    ci_pipeline: bool = False
    ci_platform: str = ""
    makefile: bool = False
    scripts_dir: bool = False


@dataclass
class DocumentationQuality:
    """Documentation present in repo."""

    readme_exists: bool = False
    readme_sections: list = field(default_factory=list)
    readme_score: int = 0
    contributing_guide: bool = False
    changelog: bool = False
    runbooks_dir: bool = False
    architecture_docs: bool = False


@dataclass
class TestCoverage:
    """Test-related indicators."""

    test_files: int = 0
    test_directories: list = field(default_factory=list)
    integration_tests: bool = False
    e2e_tests: bool = False


@dataclass
class DependencyHealth:
    """Dependency management indicators."""

    lock_file: bool = False
    lock_file_type: str = ""
    dependency_count: int = 0


@dataclass
class OracleReport:
    """Production readiness report based on code analysis."""

    codebase_path: str
    timestamp: str

    observability: ObservabilityInstrumentation = field(
        default_factory=ObservabilityInstrumentation
    )
    defensive_coding: DefensiveCoding = field(default_factory=DefensiveCoding)
    configuration: ConfigurationHygiene = field(default_factory=ConfigurationHygiene)
    deployment: DeploymentArtifacts = field(default_factory=DeploymentArtifacts)
    documentation: DocumentationQuality = field(default_factory=DocumentationQuality)
    testing: TestCoverage = field(default_factory=TestCoverage)
    dependencies: DependencyHealth = field(default_factory=DependencyHealth)

    overall_score: float = 0.0
    category_scores: dict = field(default_factory=dict)
    readiness_level: str = ""
    recommendations: list = field(default_factory=list)


class Oracle:
    """Production Readiness Analyzer - analyzes what's ACTUALLY IN THE REPO."""

    OBSERVABILITY_PATTERNS = {
        "prometheus": re.compile(
            r"prometheus_client|prom_client|from prometheus|Counter\s*\(|Gauge\s*\(|Histogram\s*\("
        ),
        "statsd": re.compile(r"statsd|dogstatsd|from statsd"),
        "datadog": re.compile(r"ddtrace|datadog|from datadog"),
        "opentelemetry": re.compile(r"opentelemetry|from otel|@trace"),
        "structured_log": re.compile(
            r"structlog|loguru|from loguru|zap\.|zerolog|pino|bunyan"
        ),
        "log_context": re.compile(r"extra\s*=|context\s*=|\.bind\(|with_fields"),
        "tracing": re.compile(r"start_span|tracer\.|with_span|@traced|Span\("),
        "health_endpoint": re.compile(
            r'["\']/(health|healthz|_health)["\']|@app\.route.*health|def health'
        ),
        "readiness": re.compile(r'["\']/(ready|readiness|readyz)["\']'),
    }

    DEFENSIVE_PATTERNS = {
        "input_validation": re.compile(
            r"validate|sanitize|escape|clean_input|is_valid"
        ),
        "null_check": re.compile(
            r"is None|is not None|!= None|== None|!= null|=== null|\?\.|Optional\["
        ),
        "bounds_check": re.compile(r"len\(|\.length|\.size\(\)|< len|> 0|>= 0"),
        "type_check": re.compile(r"isinstance\(|typeof|is_a\?|\.is_a\("),
        "assertion": re.compile(r"\bassert\b|require\(|check\(|verify\("),
    }

    CONFIG_PATTERNS = {
        "env_var": re.compile(r"os\.environ|os\.getenv|process\.env|ENV\[|getenv\("),
        "dotenv": re.compile(r"dotenv|load_dotenv|from dotenv"),
        "hardcoded_url": re.compile(r"https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
    }

    def __init__(self, codebase_path: str):
        self.codebase_path = Path(codebase_path)

    def analyze(self) -> OracleReport:
        from datetime import datetime

        report = OracleReport(
            codebase_path=str(self.codebase_path), timestamp=datetime.now().isoformat()
        )

        print(f"[ORACLE] Analyzing {self.codebase_path} for production readiness...")

        self._analyze_source_code(report)
        self._check_deployment_artifacts(report)
        self._check_documentation(report)
        self._check_testing(report)
        self._check_dependencies(report)
        self._calculate_scores(report)
        self._determine_readiness(report)
        self._generate_recommendations(report)

        print(f"  Readiness Level: {report.readiness_level}")
        print(f"  Overall Score: {report.overall_score:.1f}/100")

        return report

    def _analyze_source_code(self, report: OracleReport):
        extensions = [
            ".py",
            ".js",
            ".ts",
            ".go",
            ".java",
            ".rb",
            ".rs",
            ".c",
            ".cpp",
            ".h",
        ]

        for ext in extensions:
            for filepath in self.codebase_path.rglob(f"*{ext}"):
                if any(
                    skip in str(filepath)
                    for skip in [
                        "node_modules",
                        "venv",
                        ".venv",
                        "__pycache__",
                        ".git",
                        "dist",
                        "build",
                        "vendor",
                    ]
                ):
                    continue

                if "test" in str(filepath).lower():
                    continue

                try:
                    content = filepath.read_text(encoding="utf-8", errors="ignore")
                    self._analyze_file_content(content, report)
                except (OSError, UnicodeDecodeError) as e:
                    logger.debug(f"Could not read {filepath}: {e}")

    def _analyze_file_content(self, content: str, report: OracleReport):
        obs = report.observability

        if self.OBSERVABILITY_PATTERNS["prometheus"].search(content):
            obs.prometheus_client = True
            obs.custom_metrics += len(
                re.findall(r"Counter\s*\(|Gauge\s*\(|Histogram\s*\(", content)
            )
        if self.OBSERVABILITY_PATTERNS["statsd"].search(content):
            obs.statsd_client = True
        if self.OBSERVABILITY_PATTERNS["datadog"].search(content):
            obs.datadog_client = True
        if self.OBSERVABILITY_PATTERNS["opentelemetry"].search(content):
            obs.opentelemetry = True
        if self.OBSERVABILITY_PATTERNS["structured_log"].search(content):
            obs.structured_logging = True
        obs.context_logging += len(
            self.OBSERVABILITY_PATTERNS["log_context"].findall(content)
        )
        if self.OBSERVABILITY_PATTERNS["tracing"].search(content):
            obs.trace_instrumentation = True
            obs.span_creation += len(
                self.OBSERVABILITY_PATTERNS["tracing"].findall(content)
            )
        if self.OBSERVABILITY_PATTERNS["health_endpoint"].search(content):
            obs.health_endpoint = True
        if self.OBSERVABILITY_PATTERNS["readiness"].search(content):
            obs.readiness_endpoint = True

        for level in ["debug", "info", "warning", "warn", "error", "critical", "fatal"]:
            if re.search(rf"\.{level}\s*\(", content, re.IGNORECASE):
                obs.log_levels_used.add(level)

        defense = report.defensive_coding
        defense.input_validation += len(
            self.DEFENSIVE_PATTERNS["input_validation"].findall(content)
        )
        defense.null_checks += len(
            self.DEFENSIVE_PATTERNS["null_check"].findall(content)
        )
        defense.bounds_checks += len(
            self.DEFENSIVE_PATTERNS["bounds_check"].findall(content)
        )
        defense.type_assertions += len(
            self.DEFENSIVE_PATTERNS["type_check"].findall(content)
        )
        defense.assertions += len(self.DEFENSIVE_PATTERNS["assertion"].findall(content))
        defense.resource_cleanup += len(
            re.findall(r"\bfinally\s*:|defer\s+|using\s*\(|with\s+\w+\s+as\b", content)
        )

        config = report.configuration
        config.env_var_usage += len(self.CONFIG_PATTERNS["env_var"].findall(content))
        if self.CONFIG_PATTERNS["dotenv"].search(content):
            config.dotenv_usage = True
        config.hardcoded_strings += len(
            self.CONFIG_PATTERNS["hardcoded_url"].findall(content)
        )

    def _check_deployment_artifacts(self, report: OracleReport):
        deploy = report.deployment
        path = self.codebase_path

        dockerfiles = list(path.rglob("Dockerfile*"))
        if dockerfiles:
            deploy.dockerfile = True
            try:
                content = dockerfiles[0].read_text()
                score = 0
                if "FROM" in content:
                    score += 20
                if "COPY" in content or "ADD" in content:
                    score += 15
                if "RUN" in content:
                    score += 15
                if "EXPOSE" in content:
                    score += 10
                if "CMD" in content or "ENTRYPOINT" in content:
                    score += 15
                if "USER" in content:
                    score += 15
                if "HEALTHCHECK" in content:
                    score += 10
                deploy.dockerfile_quality = score
            except (OSError, UnicodeDecodeError) as e:
                logger.debug(f"Could not read Dockerfile: {e}")
                deploy.dockerfile_quality = 50

        deploy.docker_compose = bool(list(path.rglob("docker-compose*.y*ml")))

        for pattern in ["deployment", "service", "ingress"]:
            deploy.kubernetes_manifests += len(list(path.rglob(f"*{pattern}*.y*ml")))

        deploy.helm_chart = (path / "Chart.yaml").exists()

        ci_files = {
            ".github/workflows": "github",
            ".gitlab-ci.yml": "gitlab",
            "Jenkinsfile": "jenkins",
        }
        for ci_path, platform in ci_files.items():
            if (path / ci_path).exists():
                deploy.ci_pipeline = True
                deploy.ci_platform = platform
                break

        deploy.makefile = (path / "Makefile").exists()
        deploy.scripts_dir = (path / "scripts").is_dir()

    def _check_documentation(self, report: OracleReport):
        docs = report.documentation
        path = self.codebase_path

        for readme_name in ["README.md", "README.rst", "README"]:
            readme_path = path / readme_name
            if readme_path.exists():
                docs.readme_exists = True
                try:
                    content = readme_path.read_text(
                        encoding="utf-8", errors="ignore"
                    ).lower()
                    sections = []
                    for section in [
                        "install",
                        "usage",
                        "api",
                        "config",
                        "contribut",
                        "license",
                        "test",
                    ]:
                        if section in content:
                            sections.append(section)
                    docs.readme_sections = sections
                    docs.readme_score = min(100, len(sections) * 15)
                except Exception:
                    docs.readme_score = 25
                break

        docs.contributing_guide = (path / "CONTRIBUTING.md").exists()
        docs.changelog = (path / "CHANGELOG.md").exists()
        docs.runbooks_dir = (path / "runbooks").exists()
        docs.architecture_docs = (path / "ARCHITECTURE.md").exists()

    def _check_testing(self, report: OracleReport):
        test = report.testing
        path = self.codebase_path

        for test_dir in ["tests", "test", "spec", "__tests__"]:
            if (path / test_dir).is_dir():
                test.test_directories.append(test_dir)

        for pattern in [
            "test_*.py",
            "*_test.py",
            "*_test.go",
            "*.test.js",
            "*.spec.js",
        ]:
            test.test_files += len(list(path.rglob(pattern)))

        test.integration_tests = (path / "tests" / "integration").exists()
        test.e2e_tests = (path / "e2e").exists()

    def _check_dependencies(self, report: OracleReport):
        deps = report.dependencies
        path = self.codebase_path

        lock_files = {
            "package-lock.json": "npm",
            "yarn.lock": "yarn",
            "poetry.lock": "poetry",
            "go.sum": "go",
            "Cargo.lock": "cargo",
        }
        for lock_file, manager in lock_files.items():
            if (path / lock_file).exists():
                deps.lock_file = True
                deps.lock_file_type = manager
                break

        if (path / "package.json").exists():
            try:
                pkg = json.loads((path / "package.json").read_text())
                deps.dependency_count = len(pkg.get("dependencies", {}))
            except (OSError, json.JSONDecodeError) as e:
                logger.debug(f"Could not parse package.json: {e}")

        if (path / "requirements.txt").exists():
            try:
                lines = (path / "requirements.txt").read_text().splitlines()
                deps.dependency_count = len(
                    [
                        line
                        for line in lines
                        if line.strip() and not line.startswith("#")
                    ]
                )
            except OSError as e:
                logger.debug(f"Could not read requirements.txt: {e}")

    def _calculate_scores(self, report: OracleReport):
        scores = {}

        obs = report.observability
        obs_score = 0
        if obs.prometheus_client or obs.statsd_client or obs.datadog_client:
            obs_score += 25
        if obs.structured_logging:
            obs_score += 20
        if obs.trace_instrumentation:
            obs_score += 20
        if obs.health_endpoint:
            obs_score += 15
        if len(obs.log_levels_used) >= 3:
            obs_score += 10
        if obs.context_logging > 0:
            obs_score += 10
        scores["observability"] = min(100, obs_score)

        defense = report.defensive_coding
        scores["defensive_coding"] = min(
            100,
            min(defense.null_checks, 50)
            + min(defense.input_validation, 20) * 2
            + min(defense.resource_cleanup, 20) * 2,
        )

        config = report.configuration
        config_score = 50
        if config.env_var_usage > 5:
            config_score += 30
        if config.dotenv_usage:
            config_score += 20
        config_score -= min(30, config.hardcoded_strings * 2)
        scores["configuration"] = max(0, min(100, config_score))

        deploy = report.deployment
        deploy_score = 0
        if deploy.dockerfile:
            deploy_score += 25 + (deploy.dockerfile_quality / 4)
        if deploy.ci_pipeline:
            deploy_score += 25
        if deploy.kubernetes_manifests > 0 or deploy.helm_chart:
            deploy_score += 15
        if deploy.makefile:
            deploy_score += 10
        scores["deployment"] = min(100, deploy_score)

        docs = report.documentation
        doc_score = docs.readme_score
        if docs.contributing_guide:
            doc_score += 15
        if docs.changelog:
            doc_score += 10
        if docs.runbooks_dir:
            doc_score += 20
        scores["documentation"] = min(100, doc_score)

        test = report.testing
        test_score = 0
        if test.test_files > 0:
            test_score += min(50, test.test_files * 3)
        if test.test_directories:
            test_score += 20
        if test.integration_tests:
            test_score += 15
        if test.e2e_tests:
            test_score += 15
        scores["testing"] = min(100, test_score)

        deps = report.dependencies
        dep_score = 50
        if deps.lock_file:
            dep_score += 30
        if 0 < deps.dependency_count < 100:
            dep_score += 20
        scores["dependencies"] = min(100, dep_score)

        report.category_scores = scores

        weights = {
            "observability": 0.20,
            "defensive_coding": 0.15,
            "deployment": 0.20,
            "testing": 0.20,
            "documentation": 0.15,
            "configuration": 0.05,
            "dependencies": 0.05,
        }
        report.overall_score = sum(scores.get(k, 0) * weights[k] for k in weights)

    def _determine_readiness(self, report: OracleReport):
        score = report.overall_score
        if score >= 80:
            report.readiness_level = "HARDENED"
        elif score >= 60:
            report.readiness_level = "PRODUCTION"
        elif score >= 40:
            report.readiness_level = "BASIC"
        else:
            report.readiness_level = "NOT_READY"

    def _generate_recommendations(self, report: OracleReport):
        recs = []
        scores = report.category_scores

        if scores.get("observability", 0) < 50:
            recs.append(
                {
                    "category": "Observability",
                    "priority": "HIGH",
                    "recommendation": "Add metrics, structured logging, and health endpoints",
                }
            )
        if scores.get("testing", 0) < 40:
            recs.append(
                {
                    "category": "Testing",
                    "priority": "HIGH",
                    "recommendation": "Add unit tests for critical paths",
                }
            )
        if scores.get("deployment", 0) < 50:
            recs.append(
                {
                    "category": "Deployment",
                    "priority": "MEDIUM",
                    "recommendation": "Add Dockerfile and CI pipeline",
                }
            )
        if scores.get("documentation", 0) < 50:
            recs.append(
                {
                    "category": "Documentation",
                    "priority": "MEDIUM",
                    "recommendation": "Improve README with install, usage, config sections",
                }
            )
        if not report.dependencies.lock_file:
            recs.append(
                {
                    "category": "Dependencies",
                    "priority": "MEDIUM",
                    "recommendation": "Commit lock file for reproducible builds",
                }
            )

        report.recommendations = recs

    def save_report(self, report: OracleReport, output_path: str) -> str:
        from dataclasses import asdict

        report_dict = asdict(report)
        if "observability" in report_dict:
            report_dict["observability"]["log_levels_used"] = list(
                report_dict["observability"]["log_levels_used"]
            )
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report_dict, f, indent=2, default=str)
        return output_path


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Oracle - Production Readiness Analyzer"
    )
    parser.add_argument("path", help="Path to codebase")
    parser.add_argument("-o", "--output", help="Output JSON path")

    args = parser.parse_args()

    oracle = Oracle(args.path)
    report = oracle.analyze()

    print("\n" + "=" * 70)
    print("ORACLE PRODUCTION READINESS REPORT")
    print("=" * 70)

    print(f"\nReadiness Level: {report.readiness_level}")
    print(f"Overall Score: {report.overall_score:.0f}/100")

    print("\nCategory Scores:")
    for cat, score in sorted(report.category_scores.items(), key=lambda x: -x[1]):
        bar = "█" * int(score / 5) + "░" * (20 - int(score / 5))
        status = "✓" if score >= 60 else "⚠" if score >= 40 else "✗"
        print(f"  {status} {cat:20} [{bar}] {score:.0f}")

    if report.recommendations:
        print("\nRecommendations:")
        for rec in report.recommendations[:5]:
            print(f"  [{rec['priority']}] {rec['category']}: {rec['recommendation']}")

    if args.output:
        oracle.save_report(report, args.output)
        print(f"\nReport saved to: {args.output}")


if __name__ == "__main__":
    main()
