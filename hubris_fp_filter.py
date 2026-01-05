#!/usr/bin/env python3
"""
Hubris Fix: False Positive Filtering
====================================

This module provides functions to filter out false positives in Hubris detection.

The main issues:
1. Regex patterns in analyzer code flagged as actual resilience patterns
2. Detection code detecting itself

Usage:
    Add these functions to hubris.py and call is_false_positive() before 
    flagging issues in each detector's detect() method.
"""

import re
from pathlib import Path


def is_pattern_definition_context(
    content: str, match_start: int, match_end: int
) -> bool:
    """
    Check if a regex match is inside a pattern definition context.

    Returns True if the match appears to be in:
    - A regex pattern: re.compile(r'...')
    - A pattern dictionary: PATTERNS = { ... }
    - A string constant that defines a pattern

    This prevents the analyzer from flagging its own detection patterns.
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

    # Check for raw string patterns
    if re.search(r"r['\"].*?['\"]", line):
        # If the match is inside a raw string, it's a pattern definition
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
    ]

    for indicator in pattern_dict_indicators:
        if indicator in context:
            return True

    return False


def is_in_comment_or_docstring(content: str, position: int) -> bool:
    """
    Check if a position is inside a comment or docstring.
    """
    # Get content before position
    before = content[:position]

    # Check for single-line comment
    last_newline = before.rfind("\n")
    current_line = before[last_newline + 1 :]

    # Python single-line comment
    if "#" in current_line:
        hash_pos = current_line.find("#")
        pos_in_line = len(current_line)
        if pos_in_line > hash_pos:
            return True

    # Check for docstrings (triple quotes)
    # Count opening triple quotes - odd number means we're inside
    triple_double = before.count('"""')
    triple_single = before.count("'''")

    if triple_double % 2 == 1:
        return True
    if triple_single % 2 == 1:
        return True

    return False


def is_analyzer_file(filepath: str) -> bool:
    """
    Check if a file is an analyzer/detector file that defines patterns.

    These files need special handling because they contain pattern
    definitions that will trigger false positives.
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
    ]

    return any(ind in filename for ind in analyzer_indicators)


def should_flag_match(content: str, match, filepath: str) -> bool:
    """
    Determine if a regex match should be flagged as an issue.

    Returns False (don't flag) if:
    - It's inside a pattern definition
    - It's in a comment or docstring
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

    # Additional check for analyzer files - be more conservative
    if is_analyzer_file(filepath):
        # In analyzer files, also check if this looks like example code
        line_start = content.rfind("\n", 0, match_start) + 1
        line_end = content.find("\n", match_end)
        line = content[line_start : line_end if line_end != -1 else len(content)]

        # Skip if line looks like it's defining patterns
        if any(
            x in line for x in ["Pattern", "pattern", "PATTERN", "compile", "regex"]
        ):
            return False

    return True


# =============================================================================
# INTEGRATION EXAMPLE
# =============================================================================

"""
To integrate this into the existing hubris.py, update each detector's 
detect() method to filter matches:

BEFORE:
    for match in pattern.finditer(content):
        line_num = content[:match.start()].count('\\n') + 1
        # ... process match

AFTER:
    for match in pattern.finditer(content):
        # NEW: Filter false positives
        if not should_flag_match(content, match, filepath):
            continue
            
        line_num = content[:match.start()].count('\\n') + 1
        # ... process match


Apply this to:
- RetryDetector.detect()
- TimeoutDetector.detect()  
- CircuitBreakerDetector.detect()
- ExceptionDetector.detect()
"""


# =============================================================================
# QUICK TEST
# =============================================================================


def test_filtering():
    """Quick test of the filtering logic."""

    # Test case 1: Pattern definition (should NOT flag)
    code1 = """
    RETRY_PATTERNS = {
        'tenacity_decorator': re.compile(r'@retry\\b|@tenacity\\.retry'),
    }
    """

    import re as regex

    match = regex.search(r"@retry", code1)
    assert not should_flag_match(
        code1, match, "hubris.py"
    ), "Should not flag pattern definition"

    # Test case 2: Actual retry usage (SHOULD flag)
    code2 = """
    from tenacity import retry
    
    @retry
    def flaky_function():
        pass
    """

    match = regex.search(r"@retry", code2)
    assert should_flag_match(code2, match, "app.py"), "Should flag actual usage"

    # Test case 3: Comment (should NOT flag)
    code3 = """
    # TODO: add @retry decorator here
    def function():
        pass
    """

    match = regex.search(r"@retry", code3)
    assert not should_flag_match(code3, match, "app.py"), "Should not flag comments"

    print("All tests passed!")


if __name__ == "__main__":
    test_filtering()
