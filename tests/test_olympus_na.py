#!/usr/bin/env python3
"""
Tests for olympus.py - N/A Theater Ratio Handling

Tests cover:
- RepoSnapshot with None theater_ratio
- calculate_overall_health with None/inf values
- JSON output with N/A values
- load_prometheus_report N/A parsing
"""

import json
import math
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from olympus import (
    OlympusReport,
    RepoSnapshot,
    calculate_overall_health,
    load_prometheus_report,
)

# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def temp_dir():
    """Create a temporary directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def prometheus_report_with_na(temp_dir):
    """Create a Prometheus report with N/A theater ratio."""
    report_path = Path(temp_dir) / "prometheus_report.json"
    report_data = {
        "codebase_path": "/test/repo",
        "timestamp": datetime.now().isoformat(),
        "quadrant": "GLASS_HOUSE",
        "scores": {
            "complexity_score": 55,
            "complexity_risk": "MEDIUM",
            "resilience_score": 40,
            "shield_rating": "BRONZE"
        },
        "hubris": {
            "theater_ratio": "N/A",
            "quadrant": "N/A",
            "patterns_detected": 0,
            "patterns_correct": 0,
            "high_severity_issues": 0
        }
    }

    with open(report_path, 'w') as f:
        json.dump(report_data, f)

    return str(report_path)


@pytest.fixture
def prometheus_report_with_infinity(temp_dir):
    """Create a Prometheus report with infinity theater ratio."""
    report_path = Path(temp_dir) / "prometheus_report.json"
    report_data = {
        "codebase_path": "/test/repo",
        "timestamp": datetime.now().isoformat(),
        "quadrant": "DEATHTRAP",
        "scores": {
            "complexity_score": 70,
            "complexity_risk": "HIGH",
            "resilience_score": 20,
            "shield_rating": "PAPER"
        },
        "hubris": {
            "theater_ratio": "∞",
            "quadrant": "CARGO_CULT",
            "patterns_detected": 10,
            "patterns_correct": 0,
            "high_severity_issues": 5
        }
    }

    with open(report_path, 'w') as f:
        json.dump(report_data, f)

    return str(report_path)


@pytest.fixture
def prometheus_report_normal(temp_dir):
    """Create a normal Prometheus report."""
    report_path = Path(temp_dir) / "prometheus_report.json"
    report_data = {
        "codebase_path": "/test/repo",
        "timestamp": datetime.now().isoformat(),
        "quadrant": "FORTRESS",
        "scores": {
            "complexity_score": 60,
            "complexity_risk": "MEDIUM",
            "resilience_score": 70,
            "shield_rating": "STEEL"
        },
        "hubris": {
            "theater_ratio": 1.5,
            "quadrant": "BATTLE_HARDENED",
            "patterns_detected": 10,
            "patterns_correct": 7,
            "high_severity_issues": 1
        }
    }

    with open(report_path, 'w') as f:
        json.dump(report_data, f)

    return str(report_path)


# =============================================================================
# REPO SNAPSHOT TESTS
# =============================================================================

class TestRepoSnapshot:
    """Tests for RepoSnapshot dataclass."""

    def test_default_theater_ratio(self):
        """Test default theater_ratio value."""
        snapshot = RepoSnapshot(name="test", timestamp="2024-01-01")
        assert snapshot.theater_ratio == 1.0

    def test_none_theater_ratio(self):
        """Test that theater_ratio can be None."""
        snapshot = RepoSnapshot(
            name="test",
            timestamp="2024-01-01",
            theater_ratio=None
        )
        assert snapshot.theater_ratio is None

    def test_infinity_theater_ratio(self):
        """Test that theater_ratio can be infinity."""
        snapshot = RepoSnapshot(
            name="test",
            timestamp="2024-01-01",
            theater_ratio=float('inf')
        )
        assert math.isinf(snapshot.theater_ratio)

    def test_normal_theater_ratio(self):
        """Test normal theater_ratio value."""
        snapshot = RepoSnapshot(
            name="test",
            timestamp="2024-01-01",
            theater_ratio=2.5
        )
        assert snapshot.theater_ratio == 2.5


# =============================================================================
# CALCULATE_OVERALL_HEALTH TESTS
# =============================================================================

class TestCalculateOverallHealth:
    """Tests for calculate_overall_health function."""

    def test_health_with_none_theater(self):
        """Test health calculation with None theater_ratio."""
        snapshot = RepoSnapshot(
            name="test",
            timestamp="2024-01-01",
            complexity_score=50,
            resilience_score=50,
            theater_ratio=None
        )

        health = calculate_overall_health(snapshot)

        # Formula: complexity*0.35 + resilience*0.35 + theater_component
        # None theater = full theater component (30)
        # complexity: 50 * 0.35 = 17.5
        # resilience: 50 * 0.35 = 17.5
        # theater: 30 (None = assume okay)
        # total: 65.0
        assert health == 65.0

    def test_health_with_infinity_theater(self):
        """Test health calculation with infinity theater_ratio."""
        snapshot = RepoSnapshot(
            name="test",
            timestamp="2024-01-01",
            complexity_score=50,
            resilience_score=50,
            theater_ratio=float('inf')
        )

        health = calculate_overall_health(snapshot)

        # Infinity theater = 0 theater component
        # complexity: 50 * 0.35 = 17.5
        # resilience: 50 * 0.35 = 17.5
        # theater: 0
        # total: 35.0
        assert health == 35.0

    def test_health_with_zero_theater(self):
        """Test health calculation with zero theater_ratio."""
        snapshot = RepoSnapshot(
            name="test",
            timestamp="2024-01-01",
            complexity_score=50,
            resilience_score=50,
            theater_ratio=0.0
        )

        health = calculate_overall_health(snapshot)

        # Zero theater = 30 / (1 + 0) = 30 (best possible)
        # complexity: 50 * 0.35 = 17.5
        # resilience: 50 * 0.35 = 17.5
        # theater: 30
        # total: 65.0
        assert health == 65.0

    def test_health_with_perfect_theater(self):
        """Test health calculation with theater_ratio of 1.0."""
        snapshot = RepoSnapshot(
            name="test",
            timestamp="2024-01-01",
            complexity_score=50,
            resilience_score=50,
            theater_ratio=1.0
        )

        health = calculate_overall_health(snapshot)

        # Theater ratio 1.0 = 30 / (1 + 1) = 15
        # complexity: 50 * 0.35 = 17.5
        # resilience: 50 * 0.35 = 17.5
        # theater: 15
        # total: 50.0
        assert health == 50.0

    def test_health_with_high_theater(self):
        """Test health calculation with high theater_ratio."""
        snapshot = RepoSnapshot(
            name="test",
            timestamp="2024-01-01",
            complexity_score=50,
            resilience_score=50,
            theater_ratio=4.0  # 4x more patterns than correct
        )

        health = calculate_overall_health(snapshot)

        # High theater ratio = reduced theater component
        # theater: 30 / (1 + 4) = 6
        # complexity: 50 * 0.35 = 17.5
        # resilience: 50 * 0.35 = 17.5
        # total: 17.5 + 17.5 + 6 = 41.0
        assert health == 41.0

    def test_health_range(self):
        """Test that health is always in valid range."""
        test_cases = [
            (0, 0, None),
            (100, 100, 1.0),
            (50, 50, float('inf')),
            (0, 100, 0.5),
            (100, 0, 10.0),
        ]

        for complexity, resilience, theater in test_cases:
            snapshot = RepoSnapshot(
                name="test",
                timestamp="2024-01-01",
                complexity_score=complexity,
                resilience_score=resilience,
                theater_ratio=theater
            )

            health = calculate_overall_health(snapshot)
            assert 0 <= health <= 100, f"Health {health} out of range for {complexity}, {resilience}, {theater}"


# =============================================================================
# LOAD_PROMETHEUS_REPORT TESTS
# =============================================================================

class TestLoadPrometheusReport:
    """Tests for load_prometheus_report function."""

    def test_load_na_theater_ratio(self, prometheus_report_with_na):
        """Test loading report with N/A theater ratio."""
        snapshot = load_prometheus_report(prometheus_report_with_na)

        assert snapshot is not None
        # theater_ratio is converted during loading - may be string or float
        # The important thing is health calculation should work correctly
        health = calculate_overall_health(snapshot)
        assert health > 0  # Should not crash and give valid result

    def test_load_infinity_theater_ratio(self, prometheus_report_with_infinity):
        """Test loading report with infinity theater ratio."""
        snapshot = load_prometheus_report(prometheus_report_with_infinity)

        assert snapshot is not None
        # theater_ratio may be string "∞" from JSON, conversion happens later
        # Just verify health calculation handles it
        health = calculate_overall_health(snapshot)
        # Fixture has complexity=70, resilience=20
        # Infinity = 0 theater component: 70*0.35 + 20*0.35 + 0 = 24.5 + 7 + 0 = 31.5
        assert health == 31.5

    def test_load_normal_theater_ratio(self, prometheus_report_normal):
        """Test loading report with normal theater ratio."""
        snapshot = load_prometheus_report(prometheus_report_normal)

        assert snapshot is not None
        assert snapshot.theater_ratio == 1.5

    def test_load_handles_string_inf(self, temp_dir):
        """Test loading handles 'inf' string."""
        report_path = Path(temp_dir) / "report.json"
        report_data = {
            "codebase_path": "/test",
            "timestamp": "2024-01-01",
            "scores": {},
            "hubris": {"theater_ratio": "inf"}
        }

        with open(report_path, 'w') as f:
            json.dump(report_data, f)

        snapshot = load_prometheus_report(str(report_path))
        assert snapshot is not None
        # theater_ratio is converted to float('inf') during loading
        assert math.isinf(snapshot.theater_ratio)
        # Verify health calculation handles it (inf = 0 theater component)
        health = calculate_overall_health(snapshot)
        # scores are empty so defaults to 0: 0*0.35 + 0*0.35 + 0 = 0
        assert health == 0.0

    def test_load_handles_string_infinity(self, temp_dir):
        """Test loading handles 'Infinity' string."""
        report_path = Path(temp_dir) / "report.json"
        report_data = {
            "codebase_path": "/test",
            "timestamp": "2024-01-01",
            "scores": {},
            "hubris": {"theater_ratio": "Infinity"}
        }

        with open(report_path, 'w') as f:
            json.dump(report_data, f)

        snapshot = load_prometheus_report(str(report_path))
        assert snapshot is not None
        # theater_ratio is converted to float('inf') during loading
        assert math.isinf(snapshot.theater_ratio)
        # Verify health calculation handles it
        health = calculate_overall_health(snapshot)
        assert health == 0.0  # 0*0.35 + 0*0.35 + 0 = 0 (default scores)

    def test_load_handles_invalid_theater(self, temp_dir):
        """Test loading handles invalid theater ratio gracefully."""
        report_path = Path(temp_dir) / "report.json"
        report_data = {
            "codebase_path": "/test",
            "timestamp": "2024-01-01",
            "scores": {},
            "hubris": {"theater_ratio": "invalid_value"}
        }

        with open(report_path, 'w') as f:
            json.dump(report_data, f)

        snapshot = load_prometheus_report(str(report_path))
        assert snapshot is not None
        # Invalid string is converted to a default value during loading
        # Health calculation should handle it gracefully
        health = calculate_overall_health(snapshot)
        # Health should be valid (not crash)
        assert 0 <= health <= 100


# =============================================================================
# OLYMPUS REPORT TESTS
# =============================================================================

class TestOlympusReport:
    """Tests for OlympusReport dataclass."""

    def test_default_values(self):
        """Test default values."""
        report = OlympusReport(timestamp="2024-01-01")

        assert report.repos == []
        assert report.avg_theater_ratio == 0.0
        assert report.cargo_cult_repos == []

    def test_repos_list(self):
        """Test adding repos to report."""
        snapshot1 = RepoSnapshot(name="repo1", timestamp="2024-01-01", theater_ratio=1.5)
        snapshot2 = RepoSnapshot(name="repo2", timestamp="2024-01-01", theater_ratio=None)

        report = OlympusReport(
            timestamp="2024-01-01",
            repos=[snapshot1, snapshot2]
        )

        assert len(report.repos) == 2


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestIntegration:
    """Integration tests for olympus N/A handling."""

    def test_multiple_reports_with_mixed_theater(self, temp_dir):
        """Test handling multiple reports with mixed theater ratios."""
        # Create reports with different theater ratios
        reports = [
            ("repo1", 1.5),
            ("repo2", "N/A"),
            ("repo3", "∞"),
            ("repo4", 2.0),
        ]

        snapshots = []
        for name, theater in reports:
            if theater == "N/A":
                theater_val = None
            elif theater == "∞":
                theater_val = float('inf')
            else:
                theater_val = theater

            snapshot = RepoSnapshot(
                name=name,
                timestamp="2024-01-01",
                complexity_score=50,
                resilience_score=50,
                theater_ratio=theater_val
            )
            snapshots.append(snapshot)

        # Calculate health for each
        for snapshot in snapshots:
            health = calculate_overall_health(snapshot)
            assert 0 <= health <= 100

        # Calculate average excluding None and inf
        finite_ratios = [
            s.theater_ratio for s in snapshots
            if s.theater_ratio is not None and not math.isinf(s.theater_ratio)
        ]

        assert len(finite_ratios) == 2  # Only repo1 and repo4
        avg = sum(finite_ratios) / len(finite_ratios)
        assert avg == 1.75  # (1.5 + 2.0) / 2


# =============================================================================
# EDGE CASES
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases."""

    def test_negative_theater_ratio(self):
        """Test handling of negative theater ratio."""
        snapshot = RepoSnapshot(
            name="test",
            timestamp="2024-01-01",
            complexity_score=50,
            resilience_score=50,
            theater_ratio=-1.0
        )

        health = calculate_overall_health(snapshot)
        # Negative treated as invalid = full theater component (30)
        # complexity: 50 * 0.35 = 17.5
        # resilience: 50 * 0.35 = 17.5
        # theater: 30 (invalid = assume okay)
        # total: 65.0
        assert health == 65.0

    def test_very_small_theater_ratio(self):
        """Test handling of very small theater ratio."""
        snapshot = RepoSnapshot(
            name="test",
            timestamp="2024-01-01",
            complexity_score=50,
            resilience_score=50,
            theater_ratio=0.001
        )

        health = calculate_overall_health(snapshot)
        # Very small positive ratio = nearly full theater component
        # theater: 30 / (1 + 0.001) ≈ 29.97
        # complexity: 50 * 0.35 = 17.5, resilience: 50 * 0.35 = 17.5
        # total: 17.5 + 17.5 + 29.97 ≈ 64.97
        import pytest
        assert health == pytest.approx(64.97, rel=0.01)

    def test_theater_ratio_exactly_one(self):
        """Test theater ratio of exactly 1.0."""
        snapshot = RepoSnapshot(
            name="test",
            timestamp="2024-01-01",
            complexity_score=100,
            resilience_score=100,
            theater_ratio=1.0
        )

        health = calculate_overall_health(snapshot)
        # theater: 30 / (1 + 1) = 15
        # complexity: 100 * 0.35 = 35
        # resilience: 100 * 0.35 = 35
        # total: 35 + 35 + 15 = 85.0
        assert health == 85.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
