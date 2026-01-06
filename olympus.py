#!/usr/bin/env python3
"""
Olympus - Multi-Repository Fitness Comparator

Copyright (c) 2025 Andrew H. Bond <andrew.bond@sjsu.edu>
All rights reserved.

This software is provided for educational and research purposes.
Unauthorized copying, modification, or distribution is prohibited.

Named after the home of the Greek gods - a place of oversight.

Takes multiple Prometheus/Hubris reports and generates:
1. A Gartner-style quadrant chart comparing all repos
2. A ranked comparison table
3. Trend analysis (if historical data available)
"""

import os
import sys

# Fix Windows console encoding for emoji support
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    # Also try to set console to UTF-8 mode
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass  # Python < 3.7

import json
import argparse
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

# Import shared UI components
from prometheus_ui import (
    FALLBACK_COLORS,
    get_github_avatar_url,
    get_base_css,
    get_quadrant_css,
    get_table_css,
    generate_repo_dot_html,
    generate_legend_item_html,
    generate_quadrant_chart_html,
    generate_comparison_table_html,
    calculate_dot_position,
)


@dataclass
class RepoSnapshot:
    """A snapshot of a repository's health metrics."""
    name: str
    timestamp: str
    
    # From Prometheus
    quadrant: str = ""
    complexity_score: float = 0.0
    complexity_risk: str = ""
    resilience_score: float = 0.0
    shield_rating: str = ""
    
    # From Hubris (if available)
    theater_ratio: float = 1.0
    hubris_quadrant: str = ""
    patterns_detected: int = 0
    patterns_correct: int = 0
    high_severity_issues: int = 0
    
    # Computed
    overall_health: float = 0.0
    
    # Source
    source_file: str = ""


@dataclass
class OlympusReport:
    """Comparison report across multiple repositories."""
    timestamp: str
    repos: list = field(default_factory=list)
    
    # Rankings
    healthiest: list = field(default_factory=list)
    riskiest: list = field(default_factory=list)
    
    # Quadrant distribution
    quadrant_counts: dict = field(default_factory=dict)
    
    # Theater analysis
    avg_theater_ratio: float = 0.0
    cargo_cult_repos: list = field(default_factory=list)


def safe_theater_ratio(value) -> float:
    """Convert theater_ratio to a safe float value.
    
    Handles strings like 'inf', '∞', 'N/A', numeric strings, floats, and None.
    Returns float('inf') for infinite values, 1.0 for N/A/None, or the numeric value.
    """
    import math
    
    if value is None:
        return 1.0
    
    if isinstance(value, (int, float)):
        return float(value)
    
    if isinstance(value, str):
        value_lower = value.lower().strip()
        if value_lower in ('inf', '∞', 'infinity'):
            return float('inf')
        elif value_lower in ('n/a', 'na', 'none', ''):
            return 1.0  # Treat as neutral
        else:
            try:
                return float(value)
            except (ValueError, TypeError):
                return 1.0
    
    return 1.0


def load_prometheus_report(path: str) -> Optional[RepoSnapshot]:
    """Load a Prometheus JSON report."""
    try:
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
        
        name = data.get('codebase_path', path)
        if '/' in name:
            name = name.split('/')[-1]
        if '\\' in name:
            name = name.split('\\')[-1]
        
        scores = data.get('scores', {})
        
        # Load hubris/theater data if present
        hubris = data.get('hubris', {})
        theater_ratio = safe_theater_ratio(hubris.get('theater_ratio', 1.0))
        hubris_quadrant = hubris.get('quadrant', '')
        patterns_detected = hubris.get('patterns_detected', 0)
        patterns_correct = hubris.get('patterns_correct', 0)
        high_severity = hubris.get('high_severity_issues', 0)
        
        return RepoSnapshot(
            name=name,
            timestamp=data.get('timestamp', ''),
            quadrant=data.get('quadrant', ''),
            complexity_score=scores.get('complexity_score', 0),
            complexity_risk=scores.get('complexity_risk', ''),
            resilience_score=scores.get('resilience_score', 0),
            shield_rating=scores.get('shield_rating', ''),
            theater_ratio=theater_ratio,
            hubris_quadrant=hubris_quadrant,
            patterns_detected=patterns_detected,
            patterns_correct=patterns_correct,
            high_severity_issues=high_severity,
            source_file=path
        )
    except Exception as e:
        print(f"Warning: Could not load {path}: {e}")
        return None


def calculate_overall_health(snapshot: RepoSnapshot) -> float:
    """Calculate a combined health score.
    
    Formula: health = simplicity×0.35 + resilience×0.35 + theater_bonus×0.30
    
    NOTE: Complexity score semantics depend on when the JSON was generated:
    - OLD format (before inversion): higher = simpler (score IS simplicity)
    - NEW format (after inversion): higher = more complex (need to invert)
    
    For now, we assume OLD format since most cached JSONs use that.
    The complexity score directly represents "simplicity" (higher = simpler = healthier).
    
    - Resilience: 0-100, higher = more resilient (-1 = unknown)
    - Theater bonus: 0-30 points based on theater ratio
    """
    import math
    
    # Complexity score from JSON - assume OLD format where higher = simpler
    # This directly contributes to health (simpler code = healthier)
    complexity_component = snapshot.complexity_score * 0.35
    
    # Handle -1 (TOO_SMALL or NO_IO) resilience
    if snapshot.resilience_score < 0:
        # For unknown resilience, use neutral value (50)
        resilience_component = 50 * 0.35
    else:
        resilience_component = snapshot.resilience_score * 0.35
    
    # Convert theater_ratio to float if it's a string
    theater = snapshot.theater_ratio
    if isinstance(theater, str):
        if theater.lower() in ('inf', '∞', 'infinity'):
            theater = float('inf')
        elif theater.lower() in ('n/a', 'na', 'none', ''):
            theater = None  # Treat N/A as no theater data
        else:
            try:
                theater = float(theater)
            except (ValueError, TypeError):
                theater = None
    
    # Calculate theater component using bounded transform: 30 / (1 + theater)
    # This gives: theater=0 -> 30, theater=1 -> 15, theater=2 -> 10, theater=∞ -> 0
    if theater is None:
        theater_component = 30  # No theater data = assume okay (full points)
    elif math.isinf(theater):
        theater_component = 0  # Infinite theater = worst case
    elif theater >= 0:
        theater_component = 30 / (1 + theater)
    else:
        theater_component = 30  # Invalid theater = assume okay
    
    return complexity_component + resilience_component + theater_component


def generate_comparison_html(report: OlympusReport, output_path: str) -> str:
    """Generate an interactive HTML comparison report."""
    
    # Build dots and legend HTML
    dots_html = ""
    legend_html = ""
    
    for i, repo in enumerate(report.repos):
        x_pct, y_pct = calculate_dot_position(repo.complexity_score, repo.resilience_score)
        avatar_url = get_github_avatar_url(repo.name)
        fallback_color = FALLBACK_COLORS[i % len(FALLBACK_COLORS)]
        
        dots_html += generate_repo_dot_html(
            name=repo.name,
            x_pct=x_pct,
            y_pct=y_pct,
            avatar_url=avatar_url,
            fallback_color=fallback_color,
            quadrant=repo.quadrant,
            complexity=repo.complexity_score,
            resilience=repo.resilience_score,
            theater=repo.theater_ratio
        )
        
        legend_html += generate_legend_item_html(
            name=repo.name,
            avatar_url=avatar_url,
            fallback_color=fallback_color,
            quadrant=repo.quadrant
        )
    
    # Build table data
    sorted_repos = sorted(report.repos, key=lambda r: -r.overall_health)
    table_data = [
        {
            'name': r.name,
            'health': r.overall_health,
            'quadrant': r.quadrant,
            'complexity': r.complexity_score,
            'resilience': r.resilience_score,
            'theater': r.theater_ratio,
        }
        for r in sorted_repos
    ]
    
    # Generate quadrant chart
    quadrant_html = generate_quadrant_chart_html(dots_html, legend_html)
    
    # Generate table
    table_html = generate_comparison_table_html(table_data)
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Olympus - Repository Comparison</title>
    <style>
        {get_base_css()}
        {get_quadrant_css()}
        {get_table_css()}
        
        header {{
            text-align: center;
            margin-bottom: 2rem;
        }}
        
        header h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #f59e0b, #d97706);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        header .subtitle {{
            color: #94a3b8;
            margin-top: 0.5rem;
        }}
        
        .stats-row {{
            display: flex;
            justify-content: center;
            gap: 2rem;
            margin-bottom: 2rem;
            flex-wrap: wrap;
        }}
        
        .stat {{
            text-align: center;
        }}
        
        .stat-value {{
            font-size: 1.5rem;
            font-weight: 700;
            color: #f59e0b;
        }}
        
        .stat-label {{
            color: #64748b;
            font-size: 0.8rem;
        }}
        
        footer {{
            text-align: center;
            margin-top: 2rem;
            color: #64748b;
            font-size: 0.75rem;
        }}
        
        /* Glossary tooltip styles */
        .glossary {{
            position: fixed;
            bottom: 1rem;
            right: 1rem;
            z-index: 1000;
        }}
        
        .glossary-toggle {{
            background: #334155;
            border: 1px solid #475569;
            color: #94a3b8;
            padding: 0.5rem 1rem;
            border-radius: 0.5rem;
            cursor: pointer;
            font-size: 0.85rem;
            transition: all 0.2s;
        }}
        
        .glossary-toggle:hover {{
            background: #3f4f63;
            color: #e2e8f0;
        }}
        
        .glossary-content {{
            display: none;
            position: absolute;
            bottom: 100%;
            right: 0;
            background: #1e293b;
            border: 1px solid #475569;
            border-radius: 0.5rem;
            padding: 1rem;
            padding-bottom: 0.5rem;
            margin-bottom: 0.5rem;
            width: 320px;
            max-height: 400px;
            overflow-y: auto;
            box-shadow: 0 10px 25px rgba(0,0,0,0.3);
        }}
        
        /* Show on click (mobile-friendly) */
        .glossary-content.show {{
            display: block;
        }}
        
        /* Also show on hover for desktop */
        @media (hover: hover) {{
            .glossary:hover .glossary-content {{
                display: block;
            }}
        }}
        
        .glossary-item {{
            margin-bottom: 0.75rem;
            padding-bottom: 0.75rem;
            border-bottom: 1px solid #334155;
        }}
        
        .glossary-item:last-child {{
            margin-bottom: 0;
            padding-bottom: 0;
            border-bottom: none;
        }}
        
        .glossary-term {{
            font-weight: 600;
            color: #f59e0b;
            font-size: 0.85rem;
        }}
        
        .glossary-def {{
            color: #94a3b8;
            font-size: 0.8rem;
            margin-top: 0.25rem;
            line-height: 1.4;
        }}
        
        .stat-label {{
            color: #64748b;
            font-size: 0.8rem;
            cursor: help;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>⚡ OLYMPUS</h1>
            <p class="subtitle">Multi-Repository Fitness Comparison</p>
            <p class="subtitle" style="font-size: 0.8rem; margin-top: 0.25rem;">
                {len(report.repos)} repositories • {report.timestamp[:10]}
            </p>
        </header>
        
        <div class="stats-row">
            <div class="stat">
                <div class="stat-value">{len(report.repos)}</div>
                <div class="stat-label">Repositories</div>
            </div>
            <div class="stat">
                <div class="stat-value">{report.quadrant_counts.get('BUNKER', 0)}</div>
                <div class="stat-label" title="Low complexity, high resilience. The ideal state - simple, maintainable code with strong error handling. Goal quadrant.">BUNKER</div>
            </div>
            <div class="stat">
                <div class="stat-value">{report.quadrant_counts.get('GLASS HOUSE', 0)}</div>
                <div class="stat-label" title="Low complexity, low resilience. Simple but fragile - clean code that lacks defensive patterns. Add error handling.">GLASS HOUSE</div>
            </div>
            <div class="stat">
                <div class="stat-value">{report.quadrant_counts.get('FORTRESS', 0)}</div>
                <div class="stat-label" title="High complexity, high resilience. Over-engineered but defended - complex code with good error handling. Consider simplifying.">FORTRESS</div>
            </div>
            <div class="stat">
                <div class="stat-value">{report.quadrant_counts.get('DEATHTRAP', 0)}</div>
                <div class="stat-label" title="High complexity, low resilience. The worst state - complex code with poor error handling. High risk of cascading failures.">DEATHTRAP</div>
            </div>
        </div>
        
        <div class="card">
            <h2>Fitness Quadrant</h2>
            {quadrant_html}
        </div>
        
        <div class="card">
            <h2>Rankings (by Overall Health)</h2>
            {table_html}
        </div>
        
        <footer>
            <p>Olympus • "Complexity is the enemy of reliability"</p>
            <p style="margin-top: 0.5rem;">Copyright © 2025 Andrew H. Bond &lt;andrew.bond@sjsu.edu&gt; • All rights reserved</p>
        </footer>
    </div>
    
    <div class="glossary">
        <div class="glossary-content">
            <div class="glossary-item">
                <div class="glossary-term">🏰 BUNKER</div>
                <div class="glossary-def">Low complexity, high resilience. The ideal state - simple, maintainable code with strong error handling. Goal quadrant.</div>
            </div>
            <div class="glossary-item">
                <div class="glossary-term">🏯 FORTRESS</div>
                <div class="glossary-def">High complexity, high resilience. Over-engineered but defended - complex code with good error handling. Consider simplifying.</div>
            </div>
            <div class="glossary-item">
                <div class="glossary-term">🏠 GLASS HOUSE</div>
                <div class="glossary-def">Low complexity, low resilience. Simple but fragile - clean code that lacks defensive patterns. Add error handling.</div>
            </div>
            <div class="glossary-item">
                <div class="glossary-term">💀 DEATHTRAP</div>
                <div class="glossary-def">High complexity, low resilience. The worst state - complex code with poor error handling. High risk of cascading failures.</div>
            </div>
            <div class="glossary-item">
                <div class="glossary-term">🎭 Theater Ratio</div>
                <div class="glossary-def">Ratio of "resilience theater" (patterns that look protective but aren't) to genuine resilience. Lower is better. ∞ = theater detected but no genuine resilience patterns found. N/A = metric not applicable (e.g., language not supported).</div>
            </div>
            <div class="glossary-item">
                <div class="glossary-term">📊 Complexity Score</div>
                <div class="glossary-def">0-100 scale where HIGHER = SIMPLER code (inverted semantics). Factors: code size, cyclomatic complexity, maintainability index, hotspot density. Score ≥50 = "low complexity" (simpler, healthier code).</div>
            </div>
            <div class="glossary-item">
                <div class="glossary-term">🛡️ Resilience Score</div>
                <div class="glossary-def">0-100 scale where HIGHER = MORE RESILIENT. Factors: error handling, timeouts, retries, circuit breakers, observability. Score ≥35 = "high resilience". N/A (-1) = codebase too small to analyze.</div>
            </div>
            <div class="glossary-item">
                <div class="glossary-term">❤️ Overall Health</div>
                <div class="glossary-def">Weighted composite: Simplicity (35%) + Resilience (35%) + Theater bonus (30%). Formula: health = complexity×0.35 + resilience×0.35 + 30/(1+theater). Range 0-100, higher is better. Note: "complexity" score uses inverted semantics (higher = simpler).</div>
            </div>
        </div>
        <button class="glossary-toggle" onclick="toggleGlossary()" aria-expanded="false" aria-controls="glossary-content">📖 Glossary</button>
    </div>
    
    <script>
    // Mobile-friendly glossary toggle
    function toggleGlossary() {{
        const content = document.querySelector('.glossary-content');
        const button = document.querySelector('.glossary-toggle');
        const isOpen = content.classList.contains('show');
        
        if (isOpen) {{
            content.classList.remove('show');
            button.setAttribute('aria-expanded', 'false');
        }} else {{
            content.classList.add('show');
            button.setAttribute('aria-expanded', 'true');
        }}
    }}
    
    // Close on ESC key
    document.addEventListener('keydown', function(e) {{
        if (e.key === 'Escape') {{
            const content = document.querySelector('.glossary-content');
            const button = document.querySelector('.glossary-toggle');
            content.classList.remove('show');
            button.setAttribute('aria-expanded', 'false');
        }}
    }});
    
    // Close when clicking outside
    document.addEventListener('click', function(e) {{
        const glossary = document.querySelector('.glossary');
        if (!glossary.contains(e.target)) {{
            const content = document.querySelector('.glossary-content');
            const button = document.querySelector('.glossary-toggle');
            content.classList.remove('show');
            button.setAttribute('aria-expanded', 'false');
        }}
    }});
    
    // Interactive highlighting between table and chart
    function highlightRepo(repoId, shouldScroll = false) {{
        // Remove existing highlights
        document.querySelectorAll('.repo-dot.highlighted, tr.highlighted').forEach(el => {{
            el.classList.remove('highlighted');
        }});
        
        // Add highlight to matching elements
        const dot = document.querySelector(`.repo-dot[data-repo="${{repoId}}"]`);
        const row = document.querySelector(`tr[data-repo="${{repoId}}"]`);
        
        if (dot) {{
            dot.classList.add('highlighted');
            if (shouldScroll) {{
                dot.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
            }}
        }}
        if (row) {{
            row.classList.add('highlighted');
            if (shouldScroll) {{
                row.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
            }}
        }}
    }}
    
    function clearHighlight() {{
        document.querySelectorAll('.repo-dot.highlighted, tr.highlighted').forEach(el => {{
            el.classList.remove('highlighted');
        }});
    }}
    
    // Add event listeners to table rows
    document.querySelectorAll('tr[data-repo]').forEach(row => {{
        row.addEventListener('mouseenter', function() {{
            highlightRepo(this.dataset.repo, false);  // No scroll on hover
        }});
        row.addEventListener('mouseleave', clearHighlight);
        row.addEventListener('click', function() {{
            highlightRepo(this.dataset.repo, true);  // Scroll on click
        }});
    }});
    
    // Add event listeners to chart dots
    document.querySelectorAll('.repo-dot[data-repo]').forEach(dot => {{
        dot.addEventListener('mouseenter', function() {{
            highlightRepo(this.dataset.repo, false);  // No scroll on hover
        }});
        dot.addEventListener('mouseleave', clearHighlight);
        dot.addEventListener('click', function() {{
            highlightRepo(this.dataset.repo, true);  // Scroll on click
        }});
    }});
    </script>
    
    <style>
    /* Highlight styles */
    .repo-dot.highlighted {{
        transform: translate(-50%, -50%) scale(1.5);
        z-index: 1000;
        box-shadow: 0 0 20px rgba(255, 255, 0, 0.8), 0 0 40px rgba(255, 255, 0, 0.4);
        border: 3px solid #ffd700 !important;
    }}
    
    tr.highlighted {{
        background: rgba(255, 215, 0, 0.2) !important;
        box-shadow: inset 0 0 0 2px #ffd700;
    }}
    
    tr[data-repo] {{
        cursor: pointer;
        transition: background-color 0.2s;
    }}
    
    tr[data-repo]:hover {{
        background: rgba(255, 255, 255, 0.05);
    }}
    
    .repo-dot {{
        transition: transform 0.2s, box-shadow 0.2s;
    }}
    </style>
</body>
</html>'''
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return output_path


def clone_and_analyze(repo: str, work_dir: Path) -> Optional[str]:
    """Clone a repo and run full prometheus+hubris analysis. Returns JSON report path or None."""
    import subprocess
    
    # Parse repo format: owner/repo, full URL, or local path
    if repo.startswith('http'):
        url = repo
        name = repo.rstrip('/').split('/')[-1].replace('.git', '')
        owner = repo.rstrip('/').split('/')[-2]
        repo_dir = work_dir / f"{owner}_{name}"
        json_path = work_dir / f"prometheus_{owner}_{name}.json"
        is_local = False
    elif '/' in repo:
        # owner/repo format
        owner, name = repo.split('/')
        url = f"https://github.com/{owner}/{name}.git"
        repo_dir = work_dir / f"{owner}_{name}"
        json_path = work_dir / f"prometheus_{owner}_{name}.json"
        is_local = False
    else:
        # Local path
        repo_dir = Path(repo).resolve()  # Resolve to absolute path
        if not repo_dir.exists():
            print(f"  [skip] {repo} - path not found")
            return None
        name = repo_dir.name
        if not name:  # Handle '.' case
            name = repo_dir.resolve().name
        json_path = work_dir / f"prometheus_{name}.json"
        is_local = True
        owner = "local"
    
    display_name = f"{owner}/{name}" if not is_local else name
    
    # Skip if already analyzed
    if json_path.exists():
        print(f"  [cached] {display_name}")
        return str(json_path)
    
    # Clone if remote
    if not is_local and not repo_dir.exists():
        print(f"  [clone] {display_name}...", end=' ', flush=True)
        result = subprocess.run(
            ['git', 'clone', '--depth', '1', '--quiet', url, str(repo_dir)],
            capture_output=True, text=True, encoding='utf-8', errors='replace'
        )
        if result.returncode != 0:
            print(f"FAILED: {result.stderr.strip()}")
            return None
        print("OK")
    
    # Find scripts - check common locations
    script_dir = Path(__file__).parent
    prometheus_py = script_dir / 'prometheus.py'
    hubris_py = script_dir / 'hubris.py'
    
    if not prometheus_py.exists():
        prometheus_py = Path.cwd() / 'prometheus.py'
    if not hubris_py.exists():
        hubris_py = Path.cwd() / 'hubris.py'
    
    if not prometheus_py.exists():
        print(f"  [analyze] {owner}/{name}... FAILED: prometheus.py not found")
        return None
    
    # Run prometheus (full analysis: complexity, resilience, smells, etc.)
    print(f"  [prometheus] {display_name}...", end=' ', flush=True)
    
    # Set UTF-8 encoding for subprocess to handle emojis on Windows
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    
    result = subprocess.run(
        ['python', str(prometheus_py), str(repo_dir), '-o', str(json_path)],
        capture_output=True, text=True, encoding='utf-8', errors='replace', env=env
    )
    
    if result.returncode != 0 or not json_path.exists():
        print("FAILED")
        if result.stderr:
            print(f"    {result.stderr.strip()[:100]}")
        return None
    print("OK")
    
    # Run hubris (theater detection) if available
    if hubris_py.exists():
        hubris_json = work_dir / f"hubris_{owner}_{name}.json"
        print(f"  [hubris] {display_name}...", end=' ', flush=True)
        
        # Set UTF-8 encoding for subprocess to handle emojis on Windows
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        
        result = subprocess.run(
            ['python', str(hubris_py), str(repo_dir), '-o', str(hubris_json)],
            capture_output=True, text=True, encoding='utf-8', errors='replace', env=env
        )
        
        if result.returncode == 0 and hubris_json.exists():
            print("OK")
            # Merge hubris data into prometheus JSON
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    prom_data = json.load(f)
                with open(hubris_json, 'r', encoding='utf-8') as f:
                    hubris_data = json.load(f)
                
                prom_data['hubris'] = {
                    'theater_ratio': hubris_data.get('theater_ratio', 1.0),
                    'quadrant': hubris_data.get('quadrant', ''),
                    'patterns_detected': hubris_data.get('patterns_detected', 0),
                    'patterns_correct': hubris_data.get('patterns_correct', 0),
                    'high_severity_issues': hubris_data.get('high_severity_count', 0),
                }
                
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(prom_data, f, indent=2)
            except Exception as e:
                print(f"    Warning: Could not merge hubris data: {e}")
        else:
            # Show why it failed
            if result.stderr:
                # Show first 200 chars of error
                err_msg = result.stderr.strip()[:200]
                print(f"FAILED: {err_msg}")
            elif not hubris_json.exists():
                print("FAILED: No output file")
            else:
                print(f"FAILED: exit code {result.returncode}")
    else:
        print(f"  [hubris] {display_name}... SKIPPED (hubris.py not found)")
    
    return str(json_path)


def main():
    parser = argparse.ArgumentParser(
        description="Olympus - Multi-Repository Fitness Comparator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python olympus.py -f repos.txt -o comparison.html
  python olympus.py pallets/flask psf/requests -o comparison.html
  python olympus.py report1.json report2.json -o comparison.html

repos.txt format (one per line):
  pallets/flask
  psf/requests
  https://github.com/django/django.git
"""
    )
    parser.add_argument('repos', nargs='*', help='Repos (owner/repo) or JSON report files')
    parser.add_argument('-f', '--file', help='File containing list of repos (one per line)')
    parser.add_argument('-o', '--output', default='olympus_comparison.html', help='Output HTML path')
    parser.add_argument('-w', '--work-dir', default='.olympus_cache', help='Working directory for clones')
    parser.add_argument('--json', help='Also output JSON report')
    
    args = parser.parse_args()
    
    # Collect repos from arguments and/or file
    repos = list(args.repos) if args.repos else []
    
    if args.file:
        try:
            with open(args.file, encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Skip empty lines and full-line comments
                    if not line or line.startswith('#'):
                        continue
                    # Strip inline comments (e.g., "owner/repo  # comment")
                    if '#' in line:
                        line = line.split('#')[0].strip()
                    if line:
                        repos.append(line)
        except Exception as e:
            print(f"Error reading file: {e}")
            return
    
    if not repos:
        parser.print_help()
        return
    
    print("="*70)
    print("OLYMPUS - Multi-Repository Comparison")
    print("="*70)
    
    work_dir = Path(args.work_dir)
    work_dir.mkdir(exist_ok=True)
    
    # Process each repo - either analyze or load existing JSON
    report_paths = []
    for repo in repos:
        if repo.endswith('.json'):
            # Already a JSON report
            report_paths.append(repo)
        else:
            # Need to clone and analyze
            json_path = clone_and_analyze(repo, work_dir)
            if json_path:
                report_paths.append(json_path)
    
    print()
    
    # Load all reports
    snapshots = []
    hubris_data = {}
    
    for report_path in report_paths:
        try:
            with open(report_path, encoding='utf-8') as f:
                data = json.load(f)
            
            if 'theater_ratio' in data:
                name = Path(report_path).stem.replace('hubris_', '')
                hubris_data[name] = data
                print(f"  Loaded Hubris: {report_path}")
            else:
                snapshot = load_prometheus_report(report_path)
                if snapshot:
                    snapshots.append(snapshot)
                    print(f"  Loaded Prometheus: {report_path}")
        except Exception as e:
            print(f"  Warning: {report_path}: {e}")
    
    # Merge hubris data
    for snapshot in snapshots:
        for key in [snapshot.name, snapshot.name.replace('prometheus_', ''), Path(snapshot.source_file).stem]:
            hub = hubris_data.get(key)
            if hub:
                snapshot.theater_ratio = safe_theater_ratio(hub.get('theater_ratio', 1.0))
                snapshot.hubris_quadrant = hub.get('quadrant', '')
                snapshot.patterns_detected = hub.get('patterns_detected', 0)
                snapshot.patterns_correct = hub.get('patterns_correct', 0)
                snapshot.high_severity_issues = hub.get('high_severity_count', 0)
                break
        
        snapshot.overall_health = calculate_overall_health(snapshot)
    
    if not snapshots:
        print("\nNo valid Prometheus reports found!")
        return
    
    # Deduplicate repos by name (keep first occurrence)
    seen_names = set()
    unique_snapshots = []
    for snapshot in snapshots:
        if snapshot.name not in seen_names:
            seen_names.add(snapshot.name)
            unique_snapshots.append(snapshot)
        else:
            print(f"  Skipping duplicate: {snapshot.name}")
    snapshots = unique_snapshots
    
    if not snapshots:
        print("\nNo valid Prometheus reports after deduplication!")
        return
    
    # Build report
    report = OlympusReport(timestamp=datetime.now().isoformat(), repos=snapshots)
    
    for snap in snapshots:
        q = snap.quadrant or 'UNKNOWN'
        report.quadrant_counts[q] = report.quadrant_counts.get(q, 0) + 1
    
    # Calculate avg theater ratio, excluding infinite values
    import math
    finite_theaters = [s.theater_ratio for s in snapshots if not math.isinf(s.theater_ratio)]
    if finite_theaters:
        report.avg_theater_ratio = sum(finite_theaters) / len(finite_theaters)
    else:
        report.avg_theater_ratio = float('inf')
    
    report.cargo_cult_repos = [s.name for s in snapshots if s.hubris_quadrant == 'CARGO_CULT']
    report.healthiest = sorted(snapshots, key=lambda s: -s.overall_health)[:5]
    report.riskiest = sorted(snapshots, key=lambda s: s.overall_health)[:5]
    
    generate_comparison_html(report, args.output)
    print(f"\n  HTML: {args.output}")
    
    if args.json:
        with open(args.json, 'w') as f:
            json.dump({
                'timestamp': report.timestamp,
                'repos': [{'name': s.name, 'quadrant': s.quadrant, 'hubris': s.hubris_quadrant,
                          'complexity': s.complexity_score, 'resilience': s.resilience_score,
                          'theater': s.theater_ratio, 'health': s.overall_health} for s in snapshots],
                'quadrant_counts': report.quadrant_counts,
                'avg_theater_ratio': report.avg_theater_ratio,
                'cargo_cult_repos': report.cargo_cult_repos
            }, f, indent=2)
        print(f"  JSON: {args.json}")
    
    print(f"\nSummary: {len(snapshots)} repos")
    for q, count in report.quadrant_counts.items():
        print(f"  {q}: {count}")


if __name__ == '__main__':
    main()
