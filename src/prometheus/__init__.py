"""
Prometheus - Codebase Fitness Analyzer

A suite of tools for analyzing code quality, complexity, and resilience.

Main components:
- prometheus: Combined fitness analysis (complexity + resilience)
- hubris: Resilience theater detection
- olympus: Multi-repository comparison

Copyright (c) 2025 Andrew H. Bond <andrew.bond@sjsu.edu>
All rights reserved.
"""

__version__ = "0.2.0"

# Core analysis classes
from .shield_analyzer import Aegis, AegisReport
from .entropy_analyzer import ComplexityFitnessPipeline
from .ignore_patterns import load_ignore_patterns, should_exclude

# Main entry points
from .prometheus import Prometheus
from .hubris import Hubris

__all__ = [
    "Aegis",
    "AegisReport",
    "ComplexityFitnessPipeline",
    "Prometheus",
    "Hubris",
    "load_ignore_patterns",
    "should_exclude",
    "__version__",
]
