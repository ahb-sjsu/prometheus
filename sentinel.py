#!/usr/bin/env python3
"""
Sentinel - Security & OWASP Compliance Analyzer
================================================

Wraps and orchestrates existing security analysis tools rather than
reinventing the wheel. Each tool is best-in-class for its domain.

Tools orchestrated:
- bandit (Python security)
- gosec (Go security)
- semgrep (multi-language, OWASP rules)
- npm audit / pip-audit (dependency vulnerabilities)
- gitleaks / trufflehog (secrets detection)
- safety (Python dependency CVEs)

OWASP Top 10 Coverage:
- A01: Broken Access Control
- A02: Cryptographic Failures
- A03: Injection
- A04: Insecure Design
- A05: Security Misconfiguration
- A06: Vulnerable Components
- A07: Auth Failures
- A08: Data Integrity Failures
- A09: Logging Failures
- A10: SSRF

This module checks which tools are available and runs them,
aggregating results into a unified security report.
"""

import json
import logging
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


# =============================================================================
# DATA MODELS
# =============================================================================


@dataclass
class SecurityFinding:
    """A single security finding."""

    severity: str  # CRITICAL, HIGH, MEDIUM, LOW, INFO
    category: str  # OWASP category or tool-specific
    title: str
    description: str
    file: str = ""
    line: int = 0
    tool: str = ""
    cwe: str = ""  # CWE ID if available
    owasp: str = ""  # OWASP category if available
    fix: str = ""  # Suggested fix


@dataclass
class DependencyVuln:
    """A vulnerable dependency."""

    package: str
    version: str
    vulnerability: str
    severity: str
    fixed_version: str = ""
    cve: str = ""


@dataclass
class SecretFinding:
    """A detected secret/credential."""

    type: str  # API key, password, token, etc.
    file: str
    line: int
    snippet: str  # Redacted snippet
    severity: str = "HIGH"


@dataclass
class SecurityReport:
    """Complete security analysis report."""

    codebase_path: str
    timestamp: str

    # Tool availability
    tools_available: dict = field(default_factory=dict)
    tools_run: list = field(default_factory=list)

    # Findings
    findings: list = field(default_factory=list)
    dependency_vulns: list = field(default_factory=list)
    secrets: list = field(default_factory=list)

    # Scores
    security_score: float = 0.0  # 0-100
    owasp_coverage: dict = field(default_factory=dict)

    # Summary
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0


# =============================================================================
# TOOL WRAPPERS
# =============================================================================


class ToolWrapper:
    """Base class for security tool wrappers."""

    TOOL_NAME: str = ""
    INSTALL_CMD: str = ""

    @classmethod
    def is_available(cls) -> bool:
        """Check if the tool is installed."""
        return shutil.which(cls.TOOL_NAME) is not None

    @classmethod
    def run(cls, codebase_path: str) -> list[SecurityFinding]:
        """Run the tool and return findings."""
        raise NotImplementedError


class BanditWrapper(ToolWrapper):
    """Wrapper for bandit (Python security)."""

    TOOL_NAME = "bandit"
    INSTALL_CMD = "pip install bandit"

    SEVERITY_MAP = {
        "HIGH": "HIGH",
        "MEDIUM": "MEDIUM",
        "LOW": "LOW",
    }

    # Map bandit test IDs to OWASP categories
    OWASP_MAP = {
        "B101": "A04",  # assert used
        "B102": "A01",  # exec used
        "B103": "A05",  # set bad file permissions
        "B104": "A05",  # hardcoded bind all interfaces
        "B105": "A02",  # hardcoded password string
        "B106": "A02",  # hardcoded password funcarg
        "B107": "A02",  # hardcoded password default
        "B108": "A03",  # hardcoded tmp directory
        "B110": "A09",  # try except pass
        "B112": "A09",  # try except continue
        "B201": "A03",  # flask debug true
        "B301": "A08",  # pickle
        "B302": "A08",  # marshal
        "B303": "A02",  # md5/sha1 for security
        "B304": "A02",  # des/rc4 ciphers
        "B305": "A02",  # cipher mode without authentication
        "B306": "A02",  # mktemp
        "B307": "A03",  # eval
        "B308": "A03",  # mark_safe
        "B310": "A10",  # urllib urlopen
        "B311": "A02",  # random for crypto
        "B312": "A10",  # telnetlib
        "B313": "A03",  # xml bad
        "B320": "A03",  # xml lxml
        "B321": "A10",  # ftp
        "B323": "A02",  # ssl unverified context
        "B324": "A02",  # hashlib insecure
        "B501": "A02",  # ssl with bad version
        "B502": "A02",  # ssl with bad defaults
        "B503": "A02",  # ssl with no version
        "B504": "A02",  # ssl without SNI
        "B505": "A02",  # weak cryptographic key
        "B506": "A05",  # yaml load
        "B507": "A02",  # ssh no host key verification
        "B601": "A03",  # paramiko calls
        "B602": "A03",  # subprocess popen shell=True
        "B603": "A03",  # subprocess without shell
        "B604": "A03",  # any other function with shell=True
        "B605": "A03",  # start process with shell
        "B606": "A03",  # start process no shell
        "B607": "A03",  # start process partial path
        "B608": "A03",  # SQL injection
        "B609": "A03",  # wildcard injection
        "B610": "A03",  # django extra
        "B611": "A03",  # django rawsql
        "B701": "A03",  # jinja2 autoescape false
        "B702": "A03",  # mako templates
        "B703": "A03",  # django mark_safe
    }

    @classmethod
    def run(cls, codebase_path: str) -> list[SecurityFinding]:
        findings = []

        try:
            result = subprocess.run(
                ["bandit", "-r", "-f", "json", codebase_path],
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.stdout:
                data = json.loads(result.stdout)
                for r in data.get("results", []):
                    test_id = r.get("test_id", "")
                    findings.append(
                        SecurityFinding(
                            severity=cls.SEVERITY_MAP.get(r.get("issue_severity", "LOW"), "LOW"),
                            category="security",
                            title=r.get("test_name", "Unknown"),
                            description=r.get("issue_text", ""),
                            file=r.get("filename", ""),
                            line=r.get("line_number", 0),
                            tool="bandit",
                            cwe=(
                                r.get("issue_cwe", {}).get("id", "")
                                if isinstance(r.get("issue_cwe"), dict)
                                else ""
                            ),
                            owasp=cls.OWASP_MAP.get(test_id, ""),
                        )
                    )
        except subprocess.TimeoutExpired:
            logger.debug("bandit timed out after 300s")
        except json.JSONDecodeError:
            logger.debug("bandit returned invalid JSON")
        except FileNotFoundError:
            logger.debug("bandit not installed")

        return findings


class GosecWrapper(ToolWrapper):
    """Wrapper for gosec (Go security)."""

    TOOL_NAME = "gosec"
    INSTALL_CMD = "go install github.com/securego/gosec/v2/cmd/gosec@latest"

    @classmethod
    def run(cls, codebase_path: str) -> list[SecurityFinding]:
        findings = []

        try:
            result = subprocess.run(
                ["gosec", "-fmt=json", "-quiet", "./..."],
                capture_output=True,
                text=True,
                timeout=300,
                cwd=codebase_path,
            )

            if result.stdout:
                data = json.loads(result.stdout)
                for issue in data.get("Issues", []):
                    findings.append(
                        SecurityFinding(
                            severity=issue.get("severity", "MEDIUM"),
                            category="security",
                            title=issue.get("rule_id", "Unknown"),
                            description=issue.get("details", ""),
                            file=issue.get("file", ""),
                            line=int(issue.get("line", 0)),
                            tool="gosec",
                            cwe=(
                                issue.get("cwe", {}).get("id", "")
                                if isinstance(issue.get("cwe"), dict)
                                else ""
                            ),
                        )
                    )
        except subprocess.TimeoutExpired:
            logger.debug("gosec timed out after 300s")
        except json.JSONDecodeError:
            logger.debug("gosec returned invalid JSON")
        except FileNotFoundError:
            logger.debug("gosec not installed")

        return findings


class SemgrepWrapper(ToolWrapper):
    """Wrapper for semgrep (multi-language)."""

    TOOL_NAME = "semgrep"
    INSTALL_CMD = "pip install semgrep"

    @classmethod
    def run(cls, codebase_path: str, config: str = "p/owasp-top-ten") -> list[SecurityFinding]:
        findings = []

        try:
            result = subprocess.run(
                ["semgrep", "--config", config, "--json", codebase_path],
                capture_output=True,
                text=True,
                timeout=600,
            )

            if result.stdout:
                data = json.loads(result.stdout)
                for r in data.get("results", []):
                    extra = r.get("extra", {})
                    metadata = extra.get("metadata", {})

                    findings.append(
                        SecurityFinding(
                            severity=extra.get("severity", "MEDIUM").upper(),
                            category=metadata.get("category", "security"),
                            title=r.get("check_id", "Unknown"),
                            description=extra.get("message", ""),
                            file=r.get("path", ""),
                            line=r.get("start", {}).get("line", 0),
                            tool="semgrep",
                            cwe=(metadata.get("cwe", [""])[0] if metadata.get("cwe") else ""),
                            owasp=(metadata.get("owasp", [""])[0] if metadata.get("owasp") else ""),
                        )
                    )
        except subprocess.TimeoutExpired:
            logger.debug("semgrep timed out after 600s")
        except json.JSONDecodeError:
            logger.debug("semgrep returned invalid JSON")
        except FileNotFoundError:
            logger.debug("semgrep not installed")

        return findings


class GitleaksWrapper(ToolWrapper):
    """Wrapper for gitleaks (secrets detection)."""

    TOOL_NAME = "gitleaks"
    INSTALL_CMD = "brew install gitleaks  # or download from GitHub releases"

    @classmethod
    def run(cls, codebase_path: str) -> list[SecretFinding]:
        secrets = []

        try:
            result = subprocess.run(
                [
                    "gitleaks",
                    "detect",
                    "--source",
                    codebase_path,
                    "--report-format",
                    "json",
                    "--report-path",
                    "/dev/stdout",
                    "--no-git",
                ],
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.stdout:
                data = json.loads(result.stdout)
                for leak in data if isinstance(data, list) else []:
                    # Redact the actual secret
                    secret = leak.get("Secret", "")
                    redacted = secret[:4] + "..." + secret[-4:] if len(secret) > 8 else "***"

                    secrets.append(
                        SecretFinding(
                            type=leak.get("RuleID", "unknown"),
                            file=leak.get("File", ""),
                            line=leak.get("StartLine", 0),
                            snippet=redacted,
                            severity="HIGH",
                        )
                    )
        except subprocess.TimeoutExpired:
            logger.debug("gitleaks timed out after 300s")
        except json.JSONDecodeError:
            logger.debug("gitleaks returned invalid JSON")
        except FileNotFoundError:
            logger.debug("gitleaks not installed")

        return secrets


class NpmAuditWrapper(ToolWrapper):
    """Wrapper for npm audit (JS dependencies)."""

    TOOL_NAME = "npm"
    INSTALL_CMD = "npm is usually pre-installed with Node.js"

    @classmethod
    def is_applicable(cls, codebase_path: str) -> bool:
        """Check if this is a Node.js project."""
        return (Path(codebase_path) / "package.json").exists()

    @classmethod
    def run(cls, codebase_path: str) -> list[DependencyVuln]:
        vulns = []

        if not cls.is_applicable(codebase_path):
            return vulns

        try:
            result = subprocess.run(
                ["npm", "audit", "--json"],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=codebase_path,
            )

            if result.stdout:
                data = json.loads(result.stdout)
                for name, advisory in data.get("vulnerabilities", {}).items():
                    vulns.append(
                        DependencyVuln(
                            package=name,
                            version=advisory.get("range", "unknown"),
                            vulnerability=advisory.get("title", advisory.get("name", "Unknown")),
                            severity=advisory.get("severity", "unknown").upper(),
                            cve=advisory.get("cve", ""),
                        )
                    )
        except subprocess.TimeoutExpired:
            logger.debug("npm audit timed out after 120s")
        except json.JSONDecodeError:
            logger.debug("npm audit returned invalid JSON")
        except FileNotFoundError:
            logger.debug("npm not installed")

        return vulns


class PipAuditWrapper(ToolWrapper):
    """Wrapper for pip-audit (Python dependencies)."""

    TOOL_NAME = "pip-audit"
    INSTALL_CMD = "pip install pip-audit"

    @classmethod
    def is_applicable(cls, codebase_path: str) -> bool:
        """Check if this is a Python project."""
        path = Path(codebase_path)
        return (
            (path / "requirements.txt").exists()
            or (path / "setup.py").exists()
            or (path / "pyproject.toml").exists()
        )

    @classmethod
    def run(cls, codebase_path: str) -> list[DependencyVuln]:
        vulns = []

        if not cls.is_applicable(codebase_path):
            return vulns

        try:
            result = subprocess.run(
                ["pip-audit", "--format", "json"],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=codebase_path,
            )

            if result.stdout:
                data = json.loads(result.stdout)
                for item in data:
                    for vuln in item.get("vulns", []):
                        vulns.append(
                            DependencyVuln(
                                package=item.get("name", "unknown"),
                                version=item.get("version", "unknown"),
                                vulnerability=vuln.get("id", "Unknown"),
                                severity=(
                                    vuln.get("fix_versions", [""])[0]
                                    if vuln.get("fix_versions")
                                    else "unknown"
                                ),
                                fixed_version=(
                                    vuln.get("fix_versions", [""])[0]
                                    if vuln.get("fix_versions")
                                    else ""
                                ),
                            )
                        )
        except subprocess.TimeoutExpired:
            logger.debug("pip-audit timed out after 120s")
        except json.JSONDecodeError:
            logger.debug("pip-audit returned invalid JSON")
        except FileNotFoundError:
            logger.debug("pip-audit not installed")

        return vulns


# =============================================================================
# FALLBACK REGEX PATTERNS (when tools aren't available)
# =============================================================================


class FallbackSecurityScanner:
    """
    Regex-based security scanner for when proper tools aren't available.

    NOT a replacement for real security tools, but better than nothing.
    """

    PATTERNS = {
        # Secrets/credentials
        "hardcoded_password": (
            re.compile(
                r'(?i)(password|passwd|pwd|secret|api_key|apikey|auth_token|access_token)\s*[=:]\s*["\'][^"\']{8,}["\']'
            ),
            "HIGH",
            "A02",
            "Hardcoded credential detected",
        ),
        "aws_key": (
            re.compile(r"AKIA[0-9A-Z]{16}"),
            "CRITICAL",
            "A02",
            "AWS Access Key detected",
        ),
        "private_key": (
            re.compile(r"-----BEGIN (RSA |DSA |EC |OPENSSH )?PRIVATE KEY-----"),
            "CRITICAL",
            "A02",
            "Private key detected",
        ),
        "jwt_token": (
            re.compile(r"eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*"),
            "HIGH",
            "A02",
            "JWT token detected",
        ),
        # SQL Injection
        "sql_injection": (
            re.compile(
                r'(?i)(execute|query|cursor\.execute)\s*\(\s*["\']?\s*(%s|{|\+|\.format|f["\'])'
            ),
            "HIGH",
            "A03",
            "Potential SQL injection - use parameterized queries",
        ),
        "sql_concat": (
            re.compile(r"(?i)(SELECT|INSERT|UPDATE|DELETE).*\+.*\$|\$\{.*\}"),
            "MEDIUM",
            "A03",
            "SQL string concatenation detected",
        ),
        # Command Injection
        "os_system": (
            re.compile(r"\b(os\.system|os\.popen|subprocess\.call|subprocess\.run)\s*\([^)]*\+"),
            "HIGH",
            "A03",
            "Potential command injection",
        ),
        "shell_true": (
            re.compile(r"shell\s*=\s*True"),
            "MEDIUM",
            "A03",
            "subprocess with shell=True",
        ),
        "eval_exec": (
            re.compile(r"\b(eval|exec)\s*\("),
            "HIGH",
            "A03",
            "eval/exec usage - potential code injection",
        ),
        # XSS
        "innerhtml": (
            re.compile(r"\.innerHTML\s*=|\.outerHTML\s*=|document\.write\s*\("),
            "MEDIUM",
            "A03",
            "Potential XSS - innerHTML/document.write",
        ),
        "dangerously_set": (
            re.compile(r"dangerouslySetInnerHTML"),
            "MEDIUM",
            "A03",
            "React dangerouslySetInnerHTML usage",
        ),
        # Path Traversal
        "path_traversal": (
            re.compile(r"\.\./|\.\.\\"),
            "LOW",
            "A01",
            "Path traversal pattern detected",
        ),
        "open_user_input": (
            re.compile(r"open\s*\([^)]*\+|\bopen\s*\(\s*request\."),
            "HIGH",
            "A01",
            "File open with user input",
        ),
        # Crypto issues
        "weak_hash": (
            re.compile(r"\b(md5|sha1)\s*\("),
            "MEDIUM",
            "A02",
            "Weak hash algorithm (MD5/SHA1)",
        ),
        "weak_random": (
            re.compile(r"\brandom\.(random|randint|choice)\s*\("),
            "LOW",
            "A02",
            "Weak random for security context - use secrets module",
        ),
        "no_verify_ssl": (
            re.compile(r"verify\s*=\s*False|ssl\._create_unverified_context"),
            "HIGH",
            "A02",
            "SSL verification disabled",
        ),
        # Auth issues
        "hardcoded_admin": (
            re.compile(r'(?i)(admin|root|administrator)\s*[=:]\s*["\'][^"\']+["\']'),
            "MEDIUM",
            "A07",
            "Hardcoded admin credentials",
        ),
        # Data exposure
        "debug_true": (
            re.compile(r"(?i)debug\s*[=:]\s*True|DEBUG\s*=\s*1"),
            "MEDIUM",
            "A05",
            "Debug mode enabled",
        ),
        "stack_trace_expose": (
            re.compile(r"\.printStackTrace\s*\(|traceback\.print_exc"),
            "LOW",
            "A05",
            "Stack trace exposure",
        ),
        # Deserialization
        "pickle_load": (
            re.compile(r"pickle\.loads?\s*\(|cPickle\.loads?\s*\("),
            "HIGH",
            "A08",
            "Unsafe deserialization (pickle)",
        ),
        "yaml_load": (
            re.compile(r"yaml\.load\s*\([^)]*\)(?!\s*,\s*Loader)"),
            "HIGH",
            "A08",
            "Unsafe YAML load without Loader",
        ),
        # SSRF
        "ssrf_pattern": (
            re.compile(r"requests\.(get|post|put|delete)\s*\([^)]*\+|\burllib.*\+"),
            "MEDIUM",
            "A10",
            "Potential SSRF - URL from user input",
        ),
    }

    @classmethod
    def scan(cls, codebase_path: str) -> list[SecurityFinding]:
        findings = []
        path = Path(codebase_path)

        extensions = [
            ".py",
            ".js",
            ".ts",
            ".jsx",
            ".tsx",
            ".java",
            ".go",
            ".rb",
            ".php",
        ]

        for ext in extensions:
            for filepath in path.rglob(f"*{ext}"):
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
                        "test",
                        "tests",
                        "vendor",
                    ]
                ):
                    continue

                try:
                    content = filepath.read_text(encoding="utf-8", errors="ignore")
                    for pattern_name, (
                        pattern,
                        severity,
                        owasp,
                        desc,
                    ) in cls.PATTERNS.items():
                        for match in pattern.finditer(content):
                            line_num = content[: match.start()].count("\n") + 1
                            findings.append(
                                SecurityFinding(
                                    severity=severity,
                                    category="security",
                                    title=pattern_name,
                                    description=desc,
                                    file=str(filepath.relative_to(path)),
                                    line=line_num,
                                    tool="fallback-scanner",
                                    owasp=owasp,
                                )
                            )
                except (UnicodeDecodeError, OSError) as e:
                    logger.debug(f"Could not read {filepath}: {e}")

        return findings


# =============================================================================
# MAIN ANALYZER
# =============================================================================


class Sentinel:
    """
    The Watcher - Security and OWASP compliance analyzer.

    Orchestrates available security tools and provides unified reporting.
    """

    TOOL_WRAPPERS = [
        BanditWrapper,
        GosecWrapper,
        SemgrepWrapper,
        GitleaksWrapper,
    ]

    DEPENDENCY_WRAPPERS = [
        NpmAuditWrapper,
        PipAuditWrapper,
    ]

    def __init__(self, codebase_path: str):
        self.codebase_path = Path(codebase_path)
        self.available_tools = {}
        self._check_tools()

    def _check_tools(self):
        """Check which tools are available."""
        for wrapper in self.TOOL_WRAPPERS + self.DEPENDENCY_WRAPPERS:
            self.available_tools[wrapper.TOOL_NAME] = wrapper.is_available()

    def analyze(self) -> SecurityReport:
        """Run security analysis."""
        from datetime import datetime

        report = SecurityReport(
            codebase_path=str(self.codebase_path),
            timestamp=datetime.now().isoformat(),
            tools_available=self.available_tools.copy(),
        )

        print(f"[SENTINEL] Scanning {self.codebase_path} for security issues...")
        print(f"  Available tools: {[k for k, v in self.available_tools.items() if v]}")

        # Run available security tools
        for wrapper in self.TOOL_WRAPPERS:
            if wrapper.is_available():
                print(f"  Running {wrapper.TOOL_NAME}...")
                findings = wrapper.run(str(self.codebase_path))
                report.findings.extend(findings)
                report.tools_run.append(wrapper.TOOL_NAME)

        # Run dependency scanners
        for wrapper in self.DEPENDENCY_WRAPPERS:
            if wrapper.is_available():
                print(f"  Running {wrapper.TOOL_NAME}...")
                vulns = wrapper.run(str(self.codebase_path))
                report.dependency_vulns.extend(vulns)
                report.tools_run.append(wrapper.TOOL_NAME)

        # Run secrets detection
        if GitleaksWrapper.is_available():
            print("  Running gitleaks...")
            report.secrets = GitleaksWrapper.run(str(self.codebase_path))
            report.tools_run.append("gitleaks")

        # If no tools available, use fallback scanner
        if not report.tools_run:
            print("  No security tools found, using fallback regex scanner...")
            print("  (Install bandit, semgrep, or gosec for better results)")
            report.findings = FallbackSecurityScanner.scan(str(self.codebase_path))
            report.tools_run.append("fallback-scanner")

        # Calculate counts
        for f in report.findings:
            if f.severity == "CRITICAL":
                report.critical_count += 1
            elif f.severity == "HIGH":
                report.high_count += 1
            elif f.severity == "MEDIUM":
                report.medium_count += 1
            else:
                report.low_count += 1

        # Add secrets to high count
        report.high_count += len(report.secrets)

        # Calculate security score
        report.security_score = self._calculate_score(report)

        # Calculate OWASP coverage
        report.owasp_coverage = self._calculate_owasp_coverage(report)

        print(
            f"  Found {len(report.findings)} issues, {len(report.secrets)} secrets, {len(report.dependency_vulns)} vulnerable dependencies"
        )
        print(f"  Security Score: {report.security_score:.1f}/100")

        return report

    def _calculate_score(self, report: SecurityReport) -> float:
        """Calculate overall security score (100 = no issues found)."""
        # Start at 100, deduct for issues
        score = 100.0

        score -= report.critical_count * 20
        score -= report.high_count * 10
        score -= report.medium_count * 3
        score -= report.low_count * 1
        score -= len(report.dependency_vulns) * 5

        return max(0, min(100, score))

    def _calculate_owasp_coverage(self, report: SecurityReport) -> dict:
        """Calculate which OWASP categories were checked."""
        categories = {
            "A01": {"name": "Broken Access Control", "findings": 0},
            "A02": {"name": "Cryptographic Failures", "findings": 0},
            "A03": {"name": "Injection", "findings": 0},
            "A04": {"name": "Insecure Design", "findings": 0},
            "A05": {"name": "Security Misconfiguration", "findings": 0},
            "A06": {
                "name": "Vulnerable Components",
                "findings": len(report.dependency_vulns),
            },
            "A07": {"name": "Auth Failures", "findings": 0},
            "A08": {"name": "Data Integrity Failures", "findings": 0},
            "A09": {"name": "Logging Failures", "findings": 0},
            "A10": {"name": "SSRF", "findings": 0},
        }

        for f in report.findings:
            if f.owasp and f.owasp in categories:
                categories[f.owasp]["findings"] += 1

        return categories

    def save_report(self, report: SecurityReport, output_path: str) -> str:
        """Save report to JSON."""
        from dataclasses import asdict

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(asdict(report), f, indent=2, default=str)

        return output_path


# =============================================================================
# CLI
# =============================================================================


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Sentinel - Security and OWASP compliance analyzer"
    )
    parser.add_argument("path", help="Path to codebase")
    parser.add_argument("-o", "--output", help="Output JSON path")
    parser.add_argument(
        "--install-tools",
        action="store_true",
        help="Show commands to install security tools",
    )

    args = parser.parse_args()

    if args.install_tools:
        print("Install security tools with:")
        print("  pip install bandit semgrep pip-audit")
        print("  go install github.com/securego/gosec/v2/cmd/gosec@latest")
        print("  brew install gitleaks  # or download from GitHub")
        return

    sentinel = Sentinel(args.path)
    report = sentinel.analyze()

    # Print summary
    print("\n" + "=" * 70)
    print("SENTINEL SECURITY REPORT")
    print("=" * 70)

    print(f"\nSecurity Score: {report.security_score:.0f}/100")
    print(
        f"\nFindings: {report.critical_count} Critical, {report.high_count} High, "
        f"{report.medium_count} Medium, {report.low_count} Low"
    )
    print(f"Secrets Detected: {len(report.secrets)}")
    print(f"Vulnerable Dependencies: {len(report.dependency_vulns)}")

    if report.findings:
        print("\nTop Issues:")
        for f in sorted(
            report.findings,
            key=lambda x: {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}.get(x.severity, 4),
        )[:5]:
            print(f"  [{f.severity}] {f.file}:{f.line} - {f.title}")

    if args.output:
        sentinel.save_report(report, args.output)
        print(f"\nReport saved to: {args.output}")


if __name__ == "__main__":
    main()
