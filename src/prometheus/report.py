#!/usr/bin/env python3
"""
Hubris Report Generator
=======================
Generates HTML reports from analysis results.
"""

from .models import HubrisReport


def generate_html_report(report: HubrisReport, output_path: str, repo_name: str = "") -> str:
    """Generate an HTML report from analysis results."""

    # Prepare theater ratio display
    if report.theater_ratio == "N/A":
        theater_display = "N/A"
        theater_desc = "Unsupported language"
    elif isinstance(report.theater_ratio, float) and report.theater_ratio == float("inf"):
        theater_display = "∞"
        theater_desc = "All patterns are cargo cult"
    elif isinstance(report.theater_ratio, (int, float)):
        theater_display = f"{report.theater_ratio:.2f}"
        if report.theater_ratio <= 1.2:
            theater_desc = "Excellent - patterns well implemented"
        elif report.theater_ratio <= 2.0:
            theater_desc = "Good - minor issues"
        elif report.theater_ratio <= 3.0:
            theater_desc = "Concerning - significant gaps"
        else:
            theater_desc = "Critical - mostly theater"
    else:
        theater_display = str(report.theater_ratio)
        theater_desc = ""

    # Build issues HTML
    all_issues = (
        report.retry_issues
        + report.timeout_issues
        + report.circuit_breaker_issues
        + report.exception_issues
        + report.fallback_issues
    )

    issues_html = ""
    for issue in all_issues[:20]:  # Limit to top 20
        severity_class = issue.severity.lower()
        issues_html += f"""
            <div class="issue issue-{severity_class}">
                <span class="severity">{issue.severity}</span>
                <span class="file">{issue.file}:{issue.line}</span>
                <span class="desc">{issue.description}</span>
            </div>
        """

    if len(all_issues) > 20:
        issues_html += f'<p class="more">... and {len(all_issues) - 20} more issues</p>'

    # Build recommendations HTML
    recs_html = ""
    for rec in report.recommendations[:5]:
        recs_html += f"""
            <div class="recommendation">
                <span class="priority">{rec["priority"]}</span>
                <span class="category">{rec["category"]}</span>
                <p>{rec["message"]}</p>
            </div>
        """

    # Libraries section
    libraries_html = ""
    if report.resilience_libraries:
        libs = "".join(
            f'<span class="library-tag">{lib}</span>' for lib in report.resilience_libraries
        )
        warning = (
            '<p class="warning">⚠️ Multiple libraries suggest inconsistent resilience strategy</p>'
            if report.library_count > 2
            else ""
        )
        libraries_html = f"""
            <div class="card">
                <h2>Resilience Libraries ({report.library_count})</h2>
                <div class="libraries">{libs}</div>
                {warning}
            </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hubris Report{f" — {repo_name}" if repo_name else ""}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #0f172a; color: #e2e8f0; line-height: 1.6;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 2rem; }}
        header {{ text-align: center; margin-bottom: 2rem; }}
        h1 {{ font-size: 2.5rem; color: #f8fafc; letter-spacing: 0.1em; }}
        .subtitle {{ color: #94a3b8; margin-top: 0.5rem; }}

        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; margin-bottom: 1.5rem; }}
        .card {{ background: #1e293b; border-radius: 12px; padding: 1.5rem; }}
        h2 {{ color: #f8fafc; font-size: 1.1rem; margin-bottom: 1rem; }}

        .quadrant-display {{ text-align: center; }}
        .quadrant-name {{ font-size: 1.8rem; font-weight: 700; color: #f8fafc; }}
        .quadrant-desc {{ color: #94a3b8; margin: 0.5rem 0; }}

        .risk-badge {{
            display: inline-block; padding: 0.25rem 1rem; border-radius: 9999px;
            font-weight: 600; font-size: 0.875rem; margin-top: 1rem;
        }}
        .risk-LOW {{ background: #166534; color: #bbf7d0; }}
        .risk-MEDIUM {{ background: #854d0e; color: #fef08a; }}
        .risk-HIGH {{ background: #991b1b; color: #fecaca; }}
        .risk-CRITICAL {{ background: #7f1d1d; color: #fecaca; animation: pulse 2s infinite; }}

        @keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.7; }} }}

        .quadrant-chart {{
            display: grid; grid-template-columns: 1fr 1fr; gap: 4px;
            margin-top: 1.5rem; font-size: 0.75rem;
        }}
        .quadrant-cell {{
            padding: 0.75rem; background: #334155; border-radius: 4px;
            display: flex; align-items: center; justify-content: center;
        }}
        .quadrant-cell.active {{ background: #3b82f6; font-weight: 600; }}

        .theater-ratio {{ text-align: center; }}
        .theater-value {{ font-size: 3rem; font-weight: 700; color: #f8fafc; }}
        .theater-label {{ color: #94a3b8; }}

        .metric {{ display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid #334155; }}
        .metric:last-child {{ border-bottom: none; }}
        .metric-label {{ color: #94a3b8; }}
        .metric-value {{ font-weight: 600; }}

        .issue {{ padding: 0.75rem; margin-bottom: 0.5rem; background: #334155; border-radius: 6px; display: flex; flex-wrap: wrap; gap: 0.5rem; align-items: center; }}
        .issue-high {{ border-left: 3px solid #ef4444; }}
        .issue-medium {{ border-left: 3px solid #eab308; }}
        .issue-low {{ border-left: 3px solid #64748b; }}
        .severity {{ font-weight: 600; font-size: 0.75rem; padding: 0.125rem 0.5rem; border-radius: 4px; }}
        .issue-high .severity {{ background: #991b1b; color: #fecaca; }}
        .issue-medium .severity {{ background: #854d0e; color: #fef08a; }}
        .issue-low .severity {{ background: #475569; color: #cbd5e1; }}
        .file {{ color: #60a5fa; font-family: monospace; font-size: 0.875rem; }}
        .desc {{ color: #cbd5e1; flex: 1; min-width: 200px; }}
        .more {{ color: #64748b; font-style: italic; margin-top: 0.5rem; }}

        .recommendation {{ padding: 1rem; margin-bottom: 0.75rem; background: #334155; border-radius: 6px; }}
        .priority {{ font-weight: 600; font-size: 0.75rem; padding: 0.125rem 0.5rem; border-radius: 4px; background: #3b82f6; color: white; }}
        .category {{ color: #60a5fa; margin-left: 0.5rem; }}
        .recommendation p {{ margin-top: 0.5rem; color: #cbd5e1; }}

        .libraries {{ display: flex; flex-wrap: wrap; gap: 0.5rem; }}
        .library-tag {{ background: #334155; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.875rem; }}
        .warning {{ color: #fbbf24; margin-top: 1rem; font-size: 0.9rem; }}

        footer {{ text-align: center; margin-top: 2rem; padding-top: 2rem; border-top: 1px solid #334155; color: #64748b; font-size: 0.875rem; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>HUBRIS</h1>
            <p class="subtitle">Resilience Theater Analysis{f" — {repo_name}" if repo_name else ""}</p>
        </header>

        <div class="grid">
            <div class="card quadrant-display">
                <div class="quadrant-name">{report.quadrant.replace("_", " ")}</div>
                <div class="quadrant-desc">{report.verdict.split(".")[0]}.</div>
                <div class="risk-badge risk-{report.risk_level}">{report.risk_level} RISK</div>

                <div class="quadrant-chart">
                    <div class="quadrant-cell {"active" if report.quadrant == "OVERENGINEERED" else ""}">OVERENGINEERED</div>
                    <div class="quadrant-cell {"active" if report.quadrant == "BATTLE_HARDENED" else ""}">BATTLE-HARDENED</div>
                    <div class="quadrant-cell {"active" if report.quadrant == "CARGO_CULT" else ""}">CARGO CULT</div>
                    <div class="quadrant-cell {"active" if report.quadrant == "SIMPLE" else ""}">SIMPLE</div>
                </div>
            </div>

            <div class="card theater-ratio">
                <h2>Theater Ratio</h2>
                <div class="theater-value">{theater_display}</div>
                <div class="theater-label">{theater_desc}</div>
                <p style="margin-top: 1rem; font-size: 0.8rem; color: #64748b;">
                    patterns detected / patterns correct<br>(lower is better, 1.0 is perfect)
                </p>
            </div>
        </div>

        <div class="grid">
            <div class="card">
                <h2>Pattern Analysis</h2>
                <div class="metric">
                    <span class="metric-label">Patterns Detected</span>
                    <span class="metric-value">{report.patterns_detected}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Correctly Implemented</span>
                    <span class="metric-value" style="color: #22c55e">{report.patterns_correct}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Partially Correct</span>
                    <span class="metric-value" style="color: #eab308">{report.patterns_partial}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Cargo Cult</span>
                    <span class="metric-value" style="color: #ef4444">{report.patterns_cargo_cult}</span>
                </div>
            </div>

            <div class="card">
                <h2>Issues by Severity</h2>
                <div class="metric">
                    <span class="metric-label">Total Issues</span>
                    <span class="metric-value">{report.total_issues}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">High Severity</span>
                    <span class="metric-value" style="color: #ef4444">{report.high_severity_count}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Medium Severity</span>
                    <span class="metric-value" style="color: #eab308">{report.medium_severity_count}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Low Severity</span>
                    <span class="metric-value" style="color: #64748b">{report.low_severity_count}</span>
                </div>
            </div>
        </div>

        {libraries_html}

        {"<div class='card'><h2>Issues Found</h2>" + issues_html + "</div>" if all_issues else ""}

        {"<div class='card'><h2>Recommendations</h2>" + recs_html + "</div>" if report.recommendations else ""}

        <footer>
            <p>Hubris - Resilience Theater Detector</p>
            <p>"The complexity added by reliability patterns can introduce more failure modes than it prevents."</p>
            <p style="margin-top: 0.5rem;">Generated: {report.timestamp}</p>
        </footer>
    </div>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    return output_path
