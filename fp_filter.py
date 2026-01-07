#!/usr/bin/env python3
"""
Hubris False Positive Filter
=============================
Prevents the analyzer from flagging its own pattern definitions.

Key scenarios filtered:
1. Regex patterns: re.compile(r'@retry\b') - the @retry inside shouldn't trigger
2. Pattern dictionaries: PATTERNS = { ... }
3. Comments and docstrings
4. Example code in documentation
"""

import re
from pathlib import Path


def is_pattern_definition_context(content: str, match_start: int, match_end: int) -> bool:
    """
    Check if a regex match is inside a pattern definition context.

    Returns True if the match appears to be in:
    - A regex pattern: re.compile(r'...')
    - A pattern dictionary: PATTERNS = { ... }
    - A string constant that defines a pattern
    """
    # Get the line containing the match
    line_start = content.rfind("\n", 0, match_start) + 1
    line_end = content.find("\n", match_end)
    if line_end == -1:
        line_end = len(content)
    line = content[line_start:line_end]

    # Check for regex compilation - the clearest indicator
    if "re.compile(" in line:
        return True

    # Check for raw string patterns (r"..." or r'...')
    if re.search(r"r['\"].*?['\"]", line):
        raw_strings = list(re.finditer(r"r['\"].*?['\"]", line))
        match_pos_in_line = match_start - line_start
        for rs in raw_strings:
            if rs.start() <= match_pos_in_line <= rs.end():
                return True

    # Check for pattern dictionary context (look at surrounding lines)
    context_start = max(0, line_start - 500)
    context = content[context_start:line_end]

    # Common pattern dictionary indicators
    pattern_dict_indicators = [
        "_PATTERNS = {",
        "_PATTERNS={",
        "PATTERNS = {",
        "PATTERNS={",
        "PATTERNS: dict",
        ": re.compile(",
        "Pattern =",
        "PATTERN =",
    ]

    for indicator in pattern_dict_indicators:
        if indicator in context:
            return True

    return False


def is_in_comment_or_docstring(content: str, position: int) -> bool:
    """
    Check if a position is inside a comment or docstring.
    """
    before = content[:position]

    # Check for single-line comment
    last_newline = before.rfind("\n")
    current_line = before[last_newline + 1:]

    # Python single-line comment
    if "#" in current_line:
        hash_pos = current_line.find("#")
        pos_in_line = len(current_line)
        if pos_in_line > hash_pos:
            return True

    # Check for docstrings (triple quotes)
    triple_double = before.count('"""')
    triple_single = before.count("'''")

    if triple_double % 2 == 1:
        return True
    if triple_single % 2 == 1:
        return True

    return False


def is_in_string_literal(content: str, position: int) -> bool:
    """
    Check if position is inside a string literal.
    More comprehensive than just docstrings.
    """
    before = content[:position]
    last_newline = before.rfind("\n")
    current_line = before[last_newline + 1:]
    
    # Count quotes in current line before position
    pos_in_line = position - (last_newline + 1)
    line_before = current_line[:pos_in_line]
    
    # Skip escaped quotes
    line_clean = re.sub(r"\\'", "", re.sub(r'\\"', "", line_before))
    
    single_quotes = line_clean.count("'")
    double_quotes = line_clean.count('"')
    
    # If odd number of quotes, we're inside a string
    return (single_quotes % 2 == 1) or (double_quotes % 2 == 1)


def is_analyzer_file(filepath: str) -> bool:
    """
    Check if a file is an analyzer/detector file that defines patterns.
    """
    filename = Path(filepath).name.lower()

    analyzer_indicators = [
        "_analyzer",
        "_detector",
        "analyzer_",
        "detector_",
        "hubris",
        "sentinel",
        "patterns",
        "_patterns",
        "fp_filter",
    ]

    return any(ind in filename for ind in analyzer_indicators)


def is_test_file(filepath: str) -> bool:
    """Check if file is a test file."""
    filename = Path(filepath).name.lower()
    return filename.startswith("test_") or filename.endswith("_test.py") or "tests/" in filepath.lower()


def should_flag_match(content: str, match, filepath: str) -> bool:
    """
    Determine if a regex match should be flagged as an issue.

    Returns False (don't flag) if:
    - It's inside a pattern definition
    - It's in a comment or docstring
    - It's in a string literal (pattern definition)
    - Other false positive indicators

    Returns True if it looks like a real issue.
    """
    match_start = match.start()
    match_end = match.end()

    # Check if it's a pattern definition
    if is_pattern_definition_context(content, match_start, match_end):
        return False

    # Check if it's in a comment or docstring
    if is_in_comment_or_docstring(content, match_start):
        return False

    # Check if inside a string literal
    if is_in_string_literal(content, match_start):
        return False

    # Additional check for analyzer files - be more conservative
    if is_analyzer_file(filepath):
        line_start = content.rfind("\n", 0, match_start) + 1
        line_end = content.find("\n", match_end)
        line = content[line_start:line_end if line_end != -1 else len(content)]

        # Skip if line looks like it's defining patterns
        if any(x in line for x in ["Pattern", "pattern", "PATTERN", "compile", "regex", "re."]):
            return False

    return True


def filter_matches(pattern, content: str, filepath: str):
    """
    Generator that yields only non-false-positive matches.
    
    Usage:
        for match in filter_matches(pattern, content, filepath):
            # This match is a real detection, not a pattern definition
            process(match)
    """
    for match in pattern.finditer(content):
        if should_flag_match(content, match, filepath):
            yield match
