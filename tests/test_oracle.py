#!/usr/bin/env python3
"""
Tests for oracle.py - Production Readiness Analyzer

Tests cover:
- Data models (ObservabilityInstrumentation, DeploymentArtifacts, etc.)
- Oracle analyzer class
- Category scoring
- Readiness level determination
- Recommendation generation
"""

import pytest
import tempfile
import json
from pathlib import Path

from oracle import (
    ObservabilityInstrumentation,
    DeploymentArtifacts,
    OracleReport,
    Oracle,
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
def production_ready_codebase(temp_codebase):
    """Create a production-ready codebase."""
    src_dir = Path(temp_codebase) / "src"
    src_dir.mkdir()

    app_py = src_dir / "app.py"
    app_py.write_text(
        """
import os
from prometheus_client import Counter
import structlog

logger = structlog.get_logger(__name__)
REQUEST_COUNT = Counter('requests_total', 'Total requests')

def validate_input(data):
    if data is None:
        raise ValueError("Data cannot be None")
    return True

def process_request(request):
    REQUEST_COUNT.inc()
    logger.info("Processing request")
    validate_input(request.data)
    return {"status": "ok"}
"""
    )

    health_py = src_dir / "health.py"
    health_py.write_text(
        """
@app.route('/health')
def health():
    return {"status": "healthy"}

@app.route('/ready')
def ready():
    return {"ready": True}
"""
    )

    dockerfile = Path(temp_codebase) / "Dockerfile"
    dockerfile.write_text(
        """
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8080
USER nobody
HEALTHCHECK CMD curl -f http://localhost:8080/health
CMD ["python", "src/app.py"]
"""
    )

    github_dir = Path(temp_codebase) / ".github" / "workflows"
    github_dir.mkdir(parents=True)
    (github_dir / "ci.yml").write_text("name: CI\non: push")

    readme = Path(temp_codebase) / "README.md"
    readme.write_text(
        "# App\n\n## Installation\n\npip install .\n\n## Usage\n\npython app.py"
    )

    (Path(temp_codebase) / "CONTRIBUTING.md").write_text("# Contributing")
    (Path(temp_codebase) / "CHANGELOG.md").write_text("# Changelog")

    tests_dir = Path(temp_codebase) / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_app.py").write_text("def test_app(): pass")

    (Path(temp_codebase) / "requirements.txt").write_text("flask>=2.0\npytest>=7.0")
    (Path(temp_codebase) / "Makefile").write_text("test:\n\tpytest")

    return temp_codebase


@pytest.fixture
def minimal_codebase(temp_codebase):
    """Create a minimal codebase."""
    (Path(temp_codebase) / "app.py").write_text('print("Hello")')
    return temp_codebase


# =============================================================================
# DATA MODEL TESTS
# =============================================================================


class TestObservabilityInstrumentation:
    def test_default_values(self):
        obs = ObservabilityInstrumentation()
        assert obs.prometheus_client is False
        assert obs.log_levels_used == set()

    def test_custom_values(self):
        obs = ObservabilityInstrumentation(
            prometheus_client=True,
            structured_logging=True,
            log_levels_used={"INFO", "ERROR"},
        )
        assert obs.prometheus_client is True
        assert len(obs.log_levels_used) == 2


class TestDeploymentArtifacts:
    def test_default_values(self):
        deploy = DeploymentArtifacts()
        assert deploy.dockerfile is False
        assert deploy.ci_pipeline is False

    def test_custom_values(self):
        deploy = DeploymentArtifacts(
            dockerfile=True,
            dockerfile_quality=85,
            ci_platform="github",
        )
        assert deploy.dockerfile_quality == 85


class TestOracleReport:
    def test_default_values(self):
        report = OracleReport(codebase_path="/test", timestamp="2024-01-01")
        assert report.overall_score == 0.0
        assert report.readiness_level == ""

    def test_nested_dataclasses(self):
        report = OracleReport(codebase_path="/test", timestamp="2024-01-01")
        assert isinstance(report.observability, ObservabilityInstrumentation)
        assert isinstance(report.deployment, DeploymentArtifacts)


# =============================================================================
# ORACLE ANALYZER TESTS
# =============================================================================


class TestOracle:
    def test_init(self, temp_codebase):
        oracle = Oracle(temp_codebase)
        assert oracle.codebase_path == Path(temp_codebase)

    def test_analyze_empty(self, temp_codebase):
        oracle = Oracle(temp_codebase)
        report = oracle.analyze()
        assert report is not None
        assert report.codebase_path == temp_codebase

    def test_analyze_production_ready(self, production_ready_codebase):
        oracle = Oracle(production_ready_codebase)
        report = oracle.analyze()
        assert report.overall_score > 0
        assert report.readiness_level in ["PRODUCTION", "HARDENED", "BASIC"]

    def test_analyze_minimal(self, minimal_codebase):
        oracle = Oracle(minimal_codebase)
        report = oracle.analyze()
        assert report.readiness_level in ["NOT_READY", "BASIC", ""]


# =============================================================================
# DETECTION TESTS
# =============================================================================


class TestObservabilityDetection:
    def test_detects_prometheus(self, temp_codebase):
        (Path(temp_codebase) / "metrics.py").write_text(
            "from prometheus_client import Counter\nCOUNT = Counter('c', 'd')"
        )
        oracle = Oracle(temp_codebase)
        report = oracle.analyze()
        assert report.observability.prometheus_client is True

    def test_detects_structlog(self, temp_codebase):
        (Path(temp_codebase) / "app.py").write_text(
            "import structlog\nlogger = structlog.get_logger()"
        )
        oracle = Oracle(temp_codebase)
        report = oracle.analyze()
        assert report.observability.structured_logging is True

    def test_detects_health_endpoint(self, temp_codebase):
        (Path(temp_codebase) / "health.py").write_text(
            "@app.route('/health')\ndef health(): pass"
        )
        oracle = Oracle(temp_codebase)
        report = oracle.analyze()
        assert report.observability.health_endpoint is True


class TestDeploymentDetection:
    def test_detects_dockerfile(self, temp_codebase):
        (Path(temp_codebase) / "Dockerfile").write_text(
            "FROM python:3.11\nCMD python app.py"
        )
        oracle = Oracle(temp_codebase)
        report = oracle.analyze()
        assert report.deployment.dockerfile is True

    def test_detects_github_actions(self, temp_codebase):
        workflow_dir = Path(temp_codebase) / ".github" / "workflows"
        workflow_dir.mkdir(parents=True)
        (workflow_dir / "ci.yml").write_text("name: CI")
        oracle = Oracle(temp_codebase)
        report = oracle.analyze()
        assert report.deployment.ci_pipeline is True
        assert report.deployment.ci_platform == "github"

    def test_detects_makefile(self, temp_codebase):
        (Path(temp_codebase) / "Makefile").write_text("test:\n\tpytest")
        oracle = Oracle(temp_codebase)
        report = oracle.analyze()
        assert report.deployment.makefile is True


class TestDocumentationDetection:
    def test_detects_readme(self, temp_codebase):
        (Path(temp_codebase) / "README.md").write_text(
            "# Project\n\n## Installation\n\npip install ."
        )
        oracle = Oracle(temp_codebase)
        report = oracle.analyze()
        assert report.documentation.readme_exists is True
        assert "install" in report.documentation.readme_sections

    def test_detects_contributing(self, temp_codebase):
        (Path(temp_codebase) / "CONTRIBUTING.md").write_text("# Contributing")
        oracle = Oracle(temp_codebase)
        report = oracle.analyze()
        assert report.documentation.contributing_guide is True


class TestTestingDetection:
    def test_detects_test_directory(self, temp_codebase):
        tests_dir = Path(temp_codebase) / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_app.py").write_text("def test_x(): pass")
        oracle = Oracle(temp_codebase)
        report = oracle.analyze()
        assert "tests" in report.testing.test_directories
        assert report.testing.test_files >= 1


class TestDependencyDetection:
    def test_detects_requirements(self, temp_codebase):
        (Path(temp_codebase) / "requirements.txt").write_text(
            "flask>=2.0\nrequests>=2.28"
        )
        oracle = Oracle(temp_codebase)
        report = oracle.analyze()
        assert report.dependencies.dependency_count == 2

    def test_detects_lock_file(self, temp_codebase):
        (Path(temp_codebase) / "poetry.lock").write_text("[metadata]")
        oracle = Oracle(temp_codebase)
        report = oracle.analyze()
        assert report.dependencies.lock_file is True


# =============================================================================
# READINESS LEVEL TESTS
# =============================================================================


class TestReadinessLevel:
    def test_hardened(self, temp_codebase):
        oracle = Oracle(temp_codebase)
        report = OracleReport(codebase_path=temp_codebase, timestamp="2024-01-01")
        report.overall_score = 85.0
        oracle._determine_readiness(report)
        assert report.readiness_level == "HARDENED"

    def test_production(self, temp_codebase):
        oracle = Oracle(temp_codebase)
        report = OracleReport(codebase_path=temp_codebase, timestamp="2024-01-01")
        report.overall_score = 65.0
        oracle._determine_readiness(report)
        assert report.readiness_level == "PRODUCTION"

    def test_basic(self, temp_codebase):
        oracle = Oracle(temp_codebase)
        report = OracleReport(codebase_path=temp_codebase, timestamp="2024-01-01")
        report.overall_score = 45.0
        oracle._determine_readiness(report)
        assert report.readiness_level == "BASIC"

    def test_not_ready(self, temp_codebase):
        oracle = Oracle(temp_codebase)
        report = OracleReport(codebase_path=temp_codebase, timestamp="2024-01-01")
        report.overall_score = 25.0
        oracle._determine_readiness(report)
        assert report.readiness_level == "NOT_READY"


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestIntegration:
    def test_full_analysis(self, production_ready_codebase):
        oracle = Oracle(production_ready_codebase)
        report = oracle.analyze()
        assert report.timestamp != ""
        assert report.readiness_level != ""
        assert 0 <= report.overall_score <= 100

    def test_save_report(self, production_ready_codebase):
        oracle = Oracle(production_ready_codebase)
        report = oracle.analyze()
        output_path = Path(production_ready_codebase) / "oracle_report.json"
        saved_path = oracle.save_report(report, str(output_path))
        assert Path(saved_path).exists()
        with open(saved_path) as f:
            data = json.load(f)
        assert "readiness_level" in data


# =============================================================================
# EDGE CASES
# =============================================================================


class TestEdgeCases:
    def test_empty_directory(self, temp_codebase):
        oracle = Oracle(temp_codebase)
        report = oracle.analyze()
        assert report is not None

    def test_binary_files_ignored(self, temp_codebase):
        (Path(temp_codebase) / "image.png").write_bytes(b"\x89PNG" + b"\x00" * 100)
        oracle = Oracle(temp_codebase)
        report = oracle.analyze()
        assert report is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
