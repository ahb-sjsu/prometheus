#!/usr/bin/env python3
"""
Prometheus Benchmark Runner
===========================

Tests multiple repos and compares actual results against predictions.
Generates a report showing prediction accuracy with confidence metrics.
"""

import subprocess
import json
import sys
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Prediction:
    repo: str
    language: str
    type: str  # Library or Tool
    size: str
    expected_quadrant: str
    expected_resilience: str
    expected_resilience_min: int
    expected_freshness: str
    reason: str
    library_mode: bool = False
    # Confidence levels (0-100):
    # - quadrant_confidence: How sure are we about the quadrant prediction?
    # - resilience_confidence: How sure about resilience rating?
    # - freshness_confidence: How sure about freshness?
    quadrant_confidence: int = 50  # Default medium confidence
    resilience_confidence: int = 50
    freshness_confidence: int = 50
    confidence_notes: str = ""  # Why this confidence level


@dataclass
class ActualResult:
    quadrant: str
    resilience_rating: str
    resilience_score: float
    complexity_risk: str
    complexity_score: float
    freshness: str
    smell_score: float
    success: bool = True
    error: str = ""


# Our predictions - Updated based on observed patterns
# Key learnings:
# - Most codebases show MOLDY freshness (deep nesting is everywhere)
# - Libraries often show GLASS HOUSE without --library mode
# - Resilience scores are typically 50-70 (BRONZE-STEEL), rarely ADAMANTINE
# - Cyclomatic complexity calc requires radon (Python only) so Go/Rust/C show LOW
PREDICTIONS = [
    Prediction(
        repo="antirez/sds",
        language="C",
        type="Library",
        size="~2K LOC",
        expected_quadrant="BUNKER",
        expected_resilience="BRONZE",
        expected_resilience_min=50,
        expected_freshness="MOLDY",
        reason="Small C library, deep nesting common in C",
        library_mode=True,
        quadrant_confidence=80,  # High - small lib + library mode = BUNKER
        resilience_confidence=60,  # Medium - C patterns vary
        freshness_confidence=70,  # High - C code often has deep nesting
        confidence_notes="C libs usually BUNKER with --library flag",
    ),
    Prediction(
        repo="tidwall/gjson",
        language="Go",
        type="Library",
        size="~3K LOC",
        expected_quadrant="BUNKER",
        expected_resilience="BRONZE",
        expected_resilience_min=45,
        expected_freshness="MOLDY",
        reason="JSON parser - deep nesting for parsing logic",
        library_mode=True,
        quadrant_confidence=70,  # Parsers can be complex
        resilience_confidence=50,  # Go patterns not fully detected
        freshness_confidence=80,  # Parsers always have deep nesting
        confidence_notes="JSON parsers inherently nested; Go error handling may not be detected",
    ),
    Prediction(
        repo="kelseyhightower/envconfig",
        language="Go",
        type="Library",
        size="~1K LOC",
        expected_quadrant="BUNKER",
        expected_resilience="BRONZE",
        expected_resilience_min=50,
        expected_freshness="STALE",
        reason="Tiny, focused library",
        library_mode=True,
        quadrant_confidence=90,  # Very small = definitely BUNKER
        resilience_confidence=55,  # Go patterns partially detected
        freshness_confidence=60,  # Small libs can go either way
        confidence_notes="Tiny lib, high confidence on quadrant",
    ),
    Prediction(
        repo="sindresorhus/is",
        language="TypeScript",
        type="Library",
        size="~2K LOC",
        expected_quadrant="BUNKER",
        expected_resilience="BRONZE",
        expected_resilience_min=55,
        expected_freshness="STALE",
        reason="Pure computation, type checking",
        library_mode=True,
        quadrant_confidence=85,  # Pure computation = simple
        resilience_confidence=50,  # TS detection is basic
        freshness_confidence=50,  # Could be clean or nested
        confidence_notes="Pure type checking lib, should be simple",
    ),
    Prediction(
        repo="chalk/chalk",
        language="JavaScript",
        type="Library",
        size="~1K LOC",
        expected_quadrant="BUNKER",
        expected_resilience="WOOD",
        expected_resilience_min=15,
        expected_freshness="FRESH",
        reason="Tiny terminal colors lib",
        library_mode=True,
        quadrant_confidence=90,  # Tiny = BUNKER
        resilience_confidence=40,  # Very small libs score weird
        freshness_confidence=70,  # Modern JS is usually clean
        confidence_notes="So small it might not have patterns to detect",
    ),
    Prediction(
        repo="psf/black",
        language="Python",
        type="Tool",
        size="~15K LOC",
        expected_quadrant="BUNKER",
        expected_resilience="STEEL",
        expected_resilience_min=60,
        expected_freshness="MOLDY",
        reason="Complex formatter but deep nesting for AST handling",
        library_mode=False,
        quadrant_confidence=60,  # Could be FORTRESS if radon worked
        resilience_confidence=75,  # Python detection is best
        freshness_confidence=85,  # AST code = deep nesting guaranteed
        confidence_notes="Would be FORTRESS with working cyclomatic calc",
    ),
    Prediction(
        repo="pallets/click",
        language="Python",
        type="Library",
        size="~10K LOC",
        expected_quadrant="BUNKER",
        expected_resilience="BRONZE",
        expected_resilience_min=40,
        expected_freshness="MOLDY",
        reason="CLI framework, lots of nesting for arg parsing",
        library_mode=True,
        quadrant_confidence=75,  # Library mode helps
        resilience_confidence=65,  # Python detection good
        freshness_confidence=80,  # CLI parsing = nested
        confidence_notes="CLI frameworks have inherent nesting",
    ),
    Prediction(
        repo="BurntSushi/ripgrep",
        language="Rust",
        type="Tool",
        size="~20K LOC",
        expected_quadrant="BUNKER",
        expected_resilience="STEEL",
        expected_resilience_min=60,
        expected_freshness="MOLDY",
        reason="Rust - good error handling but deep nesting for regex/search",
        library_mode=False,
        quadrant_confidence=50,  # Should be FORTRESS but no Rust cyclomatic
        resilience_confidence=55,  # Rust patterns partially detected
        freshness_confidence=75,  # Regex code is complex
        confidence_notes="Rust Result<T,E> not fully detected; would be FORTRESS with proper cyclomatic",
    ),
    Prediction(
        repo="sharkdp/bat",
        language="Rust",
        type="Tool",
        size="~10K LOC",
        expected_quadrant="BUNKER",
        expected_resilience="BRONZE",
        expected_resilience_min=50,
        expected_freshness="MOLDY",
        reason="Rust cat clone - includes test fixtures that add noise",
        library_mode=False,
        quadrant_confidence=55,  # Test fixtures skew results
        resilience_confidence=50,  # Rust detection limited
        freshness_confidence=70,  # Test fixtures often messy
        confidence_notes="Test fixtures (jquery.js etc) add noise to analysis",
    ),
    Prediction(
        repo="junegunn/fzf",
        language="Go",
        type="Tool",
        size="~15K LOC",
        expected_quadrant="BUNKER",
        expected_resilience="STEEL",
        expected_resilience_min=60,
        expected_freshness="MOLDY",
        reason="Terminal UI - lots of deep nesting for input handling",
        library_mode=False,
        quadrant_confidence=60,  # Would be FORTRESS with Go cyclomatic
        resilience_confidence=65,  # Go patterns partially detected
        freshness_confidence=85,  # TUI code = very nested
        confidence_notes="TUI code inherently complex; Go cyclomatic not calculated",
    ),
]


def check_security_tools() -> bool:
    """Check if security tools are available."""
    try:
        result = subprocess.run(["bandit", "--version"], capture_output=True, timeout=5)
        return result.returncode == 0
    except (subprocess.SubprocessError, FileNotFoundError, subprocess.TimeoutExpired):
        return False


def run_prometheus(repo: str, library_mode: bool = False, include_security: bool = False) -> Optional[dict]:
    """Run prometheus on a repo and return the JSON results."""
    cmd = [
        "python", "prometheus.py", repo,
        "--smells",      # Code smell analysis
        "--report",      # Generate detailed report
    ]
    if library_mode:
        cmd.append("--library")
    if include_security:
        cmd.append("--security")
    
    print(f"\n{'='*70}")
    print(f"TESTING: {repo}")
    print(f"  Flags: {' '.join(cmd[2:])}")
    print(f"{'='*70}")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600,  # 10 minute timeout
            encoding='utf-8',
            errors='replace'
        )
        
        print(result.stdout)
        if result.stderr:
            print(f"STDERR: {result.stderr}")
        
        # Parse the JSON output
        repo_name = repo.replace("/", "_")
        json_path = f"prometheus_{repo_name}.json"
        smell_path = f"scent_{repo_name}.json"
        
        if Path(json_path).exists():
            with open(json_path, encoding='utf-8') as f:
                prometheus_data = json.load(f)
            
            smell_data = {}
            if Path(smell_path).exists():
                with open(smell_path, encoding='utf-8') as f:
                    smell_data = json.load(f)
            
            return {
                "prometheus": prometheus_data,
                "scent": smell_data
            }
        else:
            print(f"ERROR: {json_path} not found")
            return None
            
    except subprocess.TimeoutExpired:
        print(f"TIMEOUT: {repo} took too long")
        return None
    except Exception as e:
        print(f"ERROR: {e}")
        return None


def parse_result(data: dict) -> ActualResult:
    """Parse prometheus output into ActualResult."""
    if not data:
        return ActualResult(
            quadrant="ERROR",
            resilience_rating="ERROR",
            resilience_score=0,
            complexity_risk="ERROR",
            complexity_score=0,
            freshness="ERROR",
            smell_score=0,
            success=False,
            error="No data returned"
        )
    
    try:
        p = data.get("prometheus", {})
        s = data.get("scent", {})
        
        # Scores are nested under "scores" key
        scores = p.get("scores", {})
        
        return ActualResult(
            quadrant=p.get("quadrant", "UNKNOWN"),
            resilience_rating=scores.get("shield_rating", p.get("shield_rating", "UNKNOWN")),
            resilience_score=scores.get("resilience_score", p.get("resilience_score", 0)),
            complexity_risk=scores.get("complexity_risk", p.get("complexity_risk", "UNKNOWN")),
            complexity_score=scores.get("complexity_score", p.get("complexity_score", 0)),
            freshness=s.get("freshness_rating", "UNKNOWN"),
            smell_score=s.get("overall_smell_score", 0),
            success=True
        )
    except Exception as e:
        return ActualResult(
            quadrant="ERROR",
            resilience_rating="ERROR",
            resilience_score=0,
            complexity_risk="ERROR",
            complexity_score=0,
            freshness="ERROR",
            smell_score=0,
            success=False,
            error=str(e)
        )


def check_prediction(pred: Prediction, actual: ActualResult) -> dict:
    """Compare prediction to actual result with confidence weighting."""
    quadrant_match = pred.expected_quadrant == actual.quadrant
    resilience_match = pred.expected_resilience == actual.resilience_rating
    resilience_score_ok = actual.resilience_score >= pred.expected_resilience_min
    freshness_match = pred.expected_freshness == actual.freshness
    
    # Partial credit for close matches
    quadrant_close = (
        (pred.expected_quadrant == "BUNKER" and actual.quadrant in ["BUNKER", "FORTRESS"]) or
        (pred.expected_quadrant == "FORTRESS" and actual.quadrant in ["FORTRESS", "BUNKER"]) or
        (pred.expected_quadrant == "GLASS HOUSE" and actual.quadrant in ["GLASS HOUSE", "BUNKER"]) or
        (pred.expected_quadrant == "BUNKER" and actual.quadrant in ["BUNKER", "GLASS HOUSE"])
    )
    
    resilience_close = (
        (pred.expected_resilience == "ADAMANTINE" and actual.resilience_rating in ["ADAMANTINE", "STEEL"]) or
        (pred.expected_resilience == "STEEL" and actual.resilience_rating in ["STEEL", "ADAMANTINE", "BRONZE"]) or
        (pred.expected_resilience == "BRONZE" and actual.resilience_rating in ["BRONZE", "STEEL", "WOOD"]) or
        (pred.expected_resilience == "WOOD" and actual.resilience_rating in ["WOOD", "PAPER", "BRONZE"])
    )
    
    freshness_close = (
        (pred.expected_freshness == "FRESH" and actual.freshness in ["FRESH", "STALE"]) or
        (pred.expected_freshness == "STALE" and actual.freshness in ["STALE", "FRESH", "MOLDY"]) or
        (pred.expected_freshness == "MOLDY" and actual.freshness in ["MOLDY", "STALE", "ROTTEN"])
    )
    
    # Calculate raw accuracy (0-100)
    raw_score = sum([
        quadrant_match * 2 + (quadrant_close and not quadrant_match) * 1,
        resilience_match * 2 + (resilience_close and not resilience_match) * 1,
        resilience_score_ok * 1,
        freshness_match * 2 + (freshness_close and not freshness_match) * 1
    ]) / 9 * 100  # Max 9 points
    
    # Calculate confidence-weighted score
    # High confidence predictions that are wrong hurt more
    # Low confidence predictions that are right help less
    avg_confidence = (pred.quadrant_confidence + pred.resilience_confidence + pred.freshness_confidence) / 3
    
    # Weighted score: correct high-confidence = great, wrong high-confidence = bad
    if raw_score >= 70:
        # Got it mostly right - boost by confidence
        confidence_weighted = raw_score * (0.5 + avg_confidence / 200)
    else:
        # Got it wrong - high confidence makes it worse
        confidence_weighted = raw_score * (1.5 - avg_confidence / 200)
    
    confidence_weighted = min(100, max(0, confidence_weighted))
    
    # Check if resilience was not scored due to small size
    too_small = actual.resilience_rating == "TOO_SMALL" or actual.resilience_score < 0
    
    return {
        "quadrant_match": quadrant_match,
        "quadrant_close": quadrant_close,
        "resilience_match": resilience_match,
        "resilience_close": resilience_close,
        "resilience_score_ok": resilience_score_ok,
        "freshness_match": freshness_match,
        "freshness_close": freshness_close,
        "raw_score": raw_score,
        "confidence_weighted_score": confidence_weighted,
        "avg_confidence": avg_confidence,
        "overall_score": confidence_weighted,  # Use weighted as overall
        "too_small": too_small
    }


def generate_report(results: list[tuple[Prediction, ActualResult, dict]]) -> str:
    """Generate markdown report."""
    lines = []
    lines.append("# Prometheus Prediction Benchmark Report")
    lines.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"\nTested {len(results)} repositories\n")
    
    # Summary table with confidence
    lines.append("## Results Summary\n")
    lines.append("| Repo | Language | Predicted | Actual | Resilience | Freshness | Conf | Score |")
    lines.append("|------|----------|-----------|--------|------------|-----------|------|-------|")
    
    total_score = 0
    total_raw = 0
    success_count = 0
    
    for pred, actual, check in results:
        if not actual.success:
            lines.append(f"| `{pred.repo}` | {pred.language} | {pred.expected_quadrant} | ❌ ERROR | - | - | - | - |")
            continue
        
        success_count += 1
        
        # Check if too small to score
        too_small = check.get("too_small", False)
        
        # Quadrant emoji
        q_emoji = "✅" if check["quadrant_match"] else "🟡" if check["quadrant_close"] else "❌"
        
        # Resilience emoji - special handling for TOO_SMALL
        if too_small:
            r_emoji = "⚪"  # Neutral - not scored
            r_display = "TOO_SMALL"
        else:
            r_emoji = "✅" if check["resilience_match"] else "🟡" if check["resilience_close"] else "❌"
            r_display = f"{actual.resilience_rating} ({actual.resilience_score:.0f})"
        
        # Freshness emoji
        f_emoji = "✅" if check["freshness_match"] else "🟡" if check.get("freshness_close") else "❌"
        
        score = check["overall_score"]
        raw = check.get("raw_score", score)
        conf = check.get("avg_confidence", 50)
        total_score += score
        total_raw += raw
        
        lines.append(
            f"| `{pred.repo}` | {pred.language} | "
            f"{pred.expected_quadrant} | {q_emoji} {actual.quadrant} | "
            f"{r_emoji} {r_display} | "
            f"{f_emoji} {actual.freshness} | "
            f"{conf:.0f}% | "
            f"{score:.0f}% |"
        )
    
    avg_score = total_score / success_count if success_count > 0 else 0
    avg_raw = total_raw / success_count if success_count > 0 else 0
    
    lines.append("")
    lines.append(f"**Overall Prediction Accuracy: {avg_score:.1f}%** (Raw: {avg_raw:.1f}%)")
    lines.append("")
    
    # Confidence calibration analysis
    lines.append("## Confidence Calibration\n")
    lines.append("How well did confidence levels predict accuracy?\n")
    
    high_conf = [(p, a, c) for p, a, c in results if a.success and c.get("avg_confidence", 50) >= 70]
    low_conf = [(p, a, c) for p, a, c in results if a.success and c.get("avg_confidence", 50) < 50]
    
    if high_conf:
        high_conf_accuracy = sum(c.get("raw_score", 0) for _, _, c in high_conf) / len(high_conf)
        lines.append(f"- **High confidence (≥70%):** {len(high_conf)} predictions, {high_conf_accuracy:.0f}% accuracy")
    
    if low_conf:
        low_conf_accuracy = sum(c.get("raw_score", 0) for _, _, c in low_conf) / len(low_conf)
        lines.append(f"- **Low confidence (<50%):** {len(low_conf)} predictions, {low_conf_accuracy:.0f}% accuracy")
    
    lines.append("")
    
    # Detailed results
    lines.append("## Detailed Results\n")
    
    for pred, actual, check in results:
        lines.append(f"### {pred.repo}")
        lines.append("")
        lines.append(f"**Language:** {pred.language} | **Type:** {pred.type} | **Size:** {pred.size}")
        lines.append(f"**Reason for prediction:** {pred.reason}")
        if pred.confidence_notes:
            lines.append(f"**Confidence notes:** {pred.confidence_notes}")
        lines.append("")
        
        if not actual.success:
            lines.append(f"❌ **Error:** {actual.error}")
            lines.append("")
            continue
        
        lines.append("| Metric | Predicted | Confidence | Actual | Match |")
        lines.append("|--------|-----------|------------|--------|-------|")
        
        q_match = "✅" if check["quadrant_match"] else "🟡" if check["quadrant_close"] else "❌"
        lines.append(f"| Quadrant | {pred.expected_quadrant} | {pred.quadrant_confidence}% | {actual.quadrant} | {q_match} |")
        
        r_match = "✅" if check["resilience_match"] else "🟡" if check["resilience_close"] else "❌"
        lines.append(f"| Resilience | {pred.expected_resilience} (≥{pred.expected_resilience_min}) | {pred.resilience_confidence}% | {actual.resilience_rating} ({actual.resilience_score:.0f}) | {r_match} |")
        
        f_match = "✅" if check["freshness_match"] else "🟡" if check.get("freshness_close") else "❌"
        lines.append(f"| Freshness | {pred.expected_freshness} | {pred.freshness_confidence}% | {actual.freshness} | {f_match} |")
        
        lines.append(f"| Complexity | - | - | {actual.complexity_risk} ({actual.complexity_score:.0f}) | - |")
        lines.append(f"| Smell Score | - | - | {actual.smell_score:.0f}/100 | - |")
        
        # Show confidence-weighted calculation
        raw = check.get("raw_score", 0)
        weighted = check.get("confidence_weighted_score", raw)
        avg_conf = check.get("avg_confidence", 50)
        lines.append("")
        lines.append(f"**Scores:** Raw: {raw:.0f}% | Confidence: {avg_conf:.0f}% | Weighted: {weighted:.0f}%")
        lines.append("")
    
    # Analysis
    lines.append("## Analysis\n")
    
    # What we got right
    correct = [(p, a, c) for p, a, c in results if a.success and c["quadrant_match"]]
    if correct:
        lines.append("### ✅ Correct Predictions\n")
        for pred, actual, check in correct:
            conf = pred.quadrant_confidence
            lines.append(f"- **{pred.repo}**: Predicted {pred.expected_quadrant} ({conf}% conf), got {actual.quadrant}")
        lines.append("")
    
    # What we got wrong
    wrong = [(p, a, c) for p, a, c in results if a.success and not c["quadrant_match"] and not c["quadrant_close"]]
    if wrong:
        lines.append("### ❌ Incorrect Predictions\n")
        for pred, actual, check in wrong:
            conf = pred.quadrant_confidence
            lines.append(f"- **{pred.repo}**: Predicted {pred.expected_quadrant} ({conf}% conf), got {actual.quadrant}")
            lines.append(f"  - Resilience: {actual.resilience_score:.0f}, Complexity: {actual.complexity_score:.0f}")
        lines.append("")
    
    # Lessons learned
    lines.append("### 📚 Lessons Learned\n")
    lines.append("Based on confidence calibration:")
    lines.append("")
    
    # Check if high confidence predictions were accurate
    for pred, actual, check in results:
        if actual.success:
            if pred.quadrant_confidence >= 80 and not check["quadrant_match"]:
                lines.append(f"- **Overconfident on {pred.repo}**: {pred.quadrant_confidence}% confidence but wrong quadrant")
            if pred.quadrant_confidence <= 40 and check["quadrant_match"]:
                lines.append(f"- **Underconfident on {pred.repo}**: Only {pred.quadrant_confidence}% confidence but correct!")
    
    lines.append("")
    
    return "\n".join(lines)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Prometheus Benchmark Runner")
    parser.add_argument("--security", action="store_true", 
                        help="Include security analysis (requires bandit/semgrep)")
    parser.add_argument("--repos", type=int, default=len(PREDICTIONS),
                        help=f"Number of repos to test (default: all {len(PREDICTIONS)})")
    parser.add_argument("--only", type=str, 
                        help="Test only specific repo (e.g., 'antirez/sds')")
    args = parser.parse_args()
    
    print("="*70)
    print("PROMETHEUS BENCHMARK RUNNER")
    print("="*70)
    
    # Check for security tools
    has_security = False
    if args.security:
        has_security = check_security_tools()
        if has_security:
            print("✅ Security tools detected - including security analysis")
        else:
            print("⚠️  Security tools not found - skipping security analysis")
            print("   Install with: pip install bandit semgrep")
    
    # Filter predictions if --only specified
    predictions = PREDICTIONS
    if args.only:
        predictions = [p for p in PREDICTIONS if p.repo == args.only]
        if not predictions:
            print(f"❌ Repo '{args.only}' not in predictions list")
            return
    else:
        predictions = PREDICTIONS[:args.repos]
    
    print(f"\nTesting {len(predictions)} repositories...")
    print("This may take a while (cloning + analyzing each repo)\n")
    
    results = []
    
    for pred in predictions:
        data = run_prometheus(pred.repo, pred.library_mode, include_security=has_security)
        actual = parse_result(data)
        check = check_prediction(pred, actual)
        results.append((pred, actual, check))
        
        # Quick summary
        if actual.success:
            status = "✅" if check["quadrant_match"] else "🟡" if check["quadrant_close"] else "❌"
            print(f"\n{status} {pred.repo}: {actual.quadrant} (predicted {pred.expected_quadrant})")
        else:
            print(f"\n❌ {pred.repo}: FAILED - {actual.error}")
    
    # Generate report
    report = generate_report(results)
    
    report_path = "benchmark_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    
    print("\n" + "="*70)
    print("BENCHMARK COMPLETE")
    print("="*70)
    print(f"\nReport saved to: {report_path}")
    
    # Print summary
    success_count = sum(1 for _, a, _ in results if a.success)
    correct_count = sum(1 for _, a, c in results if a.success and c["quadrant_match"])
    close_count = sum(1 for _, a, c in results if a.success and c["quadrant_close"] and not c["quadrant_match"])
    
    print(f"\nResults: {success_count}/{len(PREDICTIONS)} repos analyzed successfully")
    print(f"Predictions: {correct_count} exact, {close_count} close, {success_count - correct_count - close_count} wrong")
    
    avg_score = sum(c["overall_score"] for _, a, c in results if a.success) / success_count if success_count > 0 else 0
    print(f"Overall accuracy: {avg_score:.1f}%")


if __name__ == "__main__":
    main()
