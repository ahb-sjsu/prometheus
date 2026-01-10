"""
Ignore pattern handling for Prometheus analyzers.

Supports .prometheusignore files with gitignore-style patterns.
Falls back to sensible defaults when no config file exists.

Copyright (c) 2025 Andrew H. Bond <andrew.bond@sjsu.edu>
All rights reserved.
"""

import logging
from pathlib import Path

import pathspec

logger = logging.getLogger(__name__)

# Default patterns to always exclude (common non-source directories)
DEFAULT_EXCLUDE_PATTERNS = [
    # Package managers and dependencies
    "node_modules/",
    "venv/",
    ".venv/",
    "vendor/",
    "packages/",
    # Build outputs
    "dist/",
    "build/",
    "target/",
    "out/",
    "bin/",
    "obj/",
    # Cache directories
    "__pycache__/",
    ".cache/",
    ".pytest_cache/",
    ".ruff_cache/",
    ".mypy_cache/",
    ".tox/",
    # IDE and editor
    ".idea/",
    ".vscode/",
    ".vs/",
    # Version control
    ".git/",
    ".hg/",
    ".svn/",
    # Package metadata
    "*.egg-info/",
    ".eggs/",
    # Prometheus-specific
    ".olympus_cache/",
    # Common test fixtures (large generated data)
    "fixtures/",
    "testdata/",
]


def load_ignore_patterns(codebase_path: Path) -> pathspec.PathSpec:
    """Load ignore patterns from .prometheusignore or use defaults.

    Args:
        codebase_path: Root path of the codebase to analyze

    Returns:
        PathSpec object for matching files to exclude
    """
    patterns = list(DEFAULT_EXCLUDE_PATTERNS)

    # Check for .prometheusignore file
    ignore_file = codebase_path / ".prometheusignore"
    if ignore_file.exists():
        try:
            content = ignore_file.read_text(encoding="utf-8")
            custom_patterns = []
            for line in content.splitlines():
                line = line.strip()
                # Skip empty lines and comments
                if line and not line.startswith("#"):
                    custom_patterns.append(line)

            if custom_patterns:
                logger.info(f"Loaded {len(custom_patterns)} patterns from .prometheusignore")
                patterns.extend(custom_patterns)
        except Exception as e:
            logger.warning(f"Error reading .prometheusignore: {e}")

    # Also check for .gitignore patterns (optional, lower priority)
    gitignore_file = codebase_path / ".gitignore"
    if gitignore_file.exists():
        try:
            content = gitignore_file.read_text(encoding="utf-8")
            for line in content.splitlines():
                line = line.strip()
                # Only include patterns that look like directories to exclude
                # Skip file patterns like *.pyc (handled elsewhere)
                if line and not line.startswith("#") and not line.startswith("!"):
                    # Include directory patterns and specific exclusions
                    if line.endswith("/") or "/" in line:
                        patterns.append(line)
        except Exception as e:
            logger.debug(f"Could not read .gitignore: {e}")

    return pathspec.PathSpec.from_lines("gitwildmatch", patterns)


def should_exclude(filepath: Path, codebase_path: Path, spec: pathspec.PathSpec) -> bool:
    """Check if a file should be excluded from analysis.

    Args:
        filepath: Path to the file to check
        codebase_path: Root path of the codebase
        spec: PathSpec with ignore patterns

    Returns:
        True if the file should be excluded
    """
    try:
        rel_path = filepath.relative_to(codebase_path)
        # Check both the file path and parent directories
        return spec.match_file(str(rel_path))
    except ValueError:
        # filepath is not relative to codebase_path
        return False


# Convenience function for one-off checks
_cached_specs: dict[Path, pathspec.PathSpec] = {}


def is_excluded(filepath: Path, codebase_path: Path) -> bool:
    """Check if a file should be excluded, with caching.

    Args:
        filepath: Path to the file to check
        codebase_path: Root path of the codebase

    Returns:
        True if the file should be excluded
    """
    if codebase_path not in _cached_specs:
        _cached_specs[codebase_path] = load_ignore_patterns(codebase_path)

    return should_exclude(filepath, codebase_path, _cached_specs[codebase_path])


def clear_cache():
    """Clear the cached PathSpec objects."""
    _cached_specs.clear()
