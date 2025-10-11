#!/usr/bin/env python3
"""
OpenSSL Security Scanner Module
Run comprehensive security scans including SAST/DAST
"""

import os
import sys
import subprocess
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List, NamedTuple
from dataclasses import dataclass
import yaml
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ScanResult:
    """Individual scan result"""
    tool: str
    scan_type: str
    issues: int
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    output_file: Optional[str] = None


@dataclass
class SecurityScanResult:
    """Result of security scan execution"""
    success: bool
    output_dir: Optional[str] = None
    scan_results: List[ScanResult] = None
    total_issues: int = 0
    issues_by_severity: Dict[str, int] = None
    fixed_issues: int = 0
    error: Optional[str] = None


class OpenSSLSecurityScanner:
    """OpenSSL security scanner with multiple tools"""
    
    def __init__(self, conan_api, profile=None, openssl_dir=None, output_dir=None,
                 scan_types=None, tools=None, severity="medium", format="json",
                 fix=False, baseline=None, verbose=False):
        self.conan_api = conan_api
        self.profile = profile
        self.openssl_dir = Path(openssl_dir or "openssl-source")
        self.output_dir = Path(output_dir or "security-scans")
        self.scan_types = scan_types or ["all"]
        self.tools = tools or ["all"]
        self.severity = severity
        self.format = format
        self.fix = fix
        self.baseline = baseline
        self.verbose = verbose
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _check_tool_available(self, tool: str) -> bool:
        """Check if security tool is available"""
        try:
            result = subprocess.run(
                ["which", tool],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def _run_trivy_scan(self) -> ScanResult:
        """Run Trivy vulnerability scan"""
        if not self._check_tool_available("trivy"):
            logger.warning("Trivy not available, skipping vulnerability scan")
            return ScanResult(tool="trivy", scan_type="vulnerability", issues=0)
        
        try:
            output_file = self.output_dir / "trivy_results.json"
            
            cmd = [
                "trivy", "fs",
                "--format", "json",
                "--output", str(output_file),
                str(self.openssl_dir)
            ]
            
            if self.verbose:
                logger.info(f"Running Trivy scan: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            if result.returncode == 0:
                # Parse Trivy results
                return self._parse_trivy_results(output_file)
            else:
                logger.error(f"Trivy scan failed: {result.stderr}")
                return ScanResult(tool="trivy", scan_type="vulnerability", issues=0)
                
        except subprocess.TimeoutExpired:
            logger.error("Trivy scan timed out")
            return ScanResult(tool="trivy", scan_type="vulnerability", issues=0)
        except Exception as e:
            logger.error(f"Trivy scan error: {e}")
            return ScanResult(tool="trivy", scan_type="vulnerability", issues=0)
    
    def _parse_trivy_results(self, output_file: Path) -> ScanResult:
        """Parse Trivy JSON results"""
        try:
            with open(output_file, 'r') as f:
                data = json.load(f)
            
            issues = 0
            critical = 0
            high = 0
            medium = 0
            low = 0
            
            for result in data.get("Results", []):
                for vuln in result.get("Vulnerabilities", []):
                    issues += 1
                    severity = vuln.get("Severity", "").lower()
                    
                    if severity == "critical":
                        critical += 1
                    elif severity == "high":
                        high += 1
                    elif severity == "medium":
                        medium += 1
                    elif severity == "low":
                        low += 1
            
            return ScanResult(
                tool="trivy",
                scan_type="vulnerability",
                issues=issues,
                critical=critical,
                high=high,
                medium=medium,
                low=low,
                output_file=str(output_file)
            )
            
        except Exception as e:
            logger.error(f"Failed to parse Trivy results: {e}")
            return ScanResult(tool="trivy", scan_type="vulnerability", issues=0)
    
    def _run_bandit_scan(self) -> ScanResult:
        """Run Bandit SAST scan"""
        if not self._check_tool_available("bandit"):
            logger.warning("Bandit not available, skipping SAST scan")
            return ScanResult(tool="bandit", scan_type="sast", issues=0)
        
        try:
            output_file = self.output_dir / "bandit_results.json"
            
            cmd = [
                "bandit", "-r", "-f", "json",
                "-o", str(output_file),
                str(self.openssl_dir)
            ]
            
            if self.verbose:
                logger.info(f"Running Bandit scan: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            # Bandit returns non-zero for issues found, which is normal
            if result.returncode in [0, 1]:
                return self._parse_bandit_results(output_file)
            else:
                logger.error(f"Bandit scan failed: {result.stderr}")
                return ScanResult(tool="bandit", scan_type="sast", issues=0)
                
        except subprocess.TimeoutExpired:
            logger.error("Bandit scan timed out")
            return ScanResult(tool="bandit", scan_type="sast", issues=0)
        except Exception as e:
            logger.error(f"Bandit scan error: {e}")
            return ScanResult(tool="bandit", scan_type="sast", issues=0)
    
    def _parse_bandit_results(self, output_file: Path) -> ScanResult:
        """Parse Bandit JSON results"""
        try:
            with open(output_file, 'r') as f:
                data = json.load(f)
            
            issues = len(data.get("results", []))
            critical = 0
            high = 0
            medium = 0
            low = 0
            
            for result in data.get("results", []):
                severity = result.get("issue_severity", "").lower()
                
                if severity == "high":
                    high += 1
                elif severity == "medium":
                    medium += 1
                elif severity == "low":
                    low += 1
            
            return ScanResult(
                tool="bandit",
                scan_type="sast",
                issues=issues,
                critical=critical,
                high=high,
                medium=medium,
                low=low,
                output_file=str(output_file)
            )
            
        except Exception as e:
            logger.error(f"Failed to parse Bandit results: {e}")
            return ScanResult(tool="bandit", scan_type="sast", issues=0)
    
    def _run_semgrep_scan(self) -> ScanResult:
        """Run Semgrep SAST scan"""
        if not self._check_tool_available("semgrep"):
            logger.warning("Semgrep not available, skipping SAST scan")
            return ScanResult(tool="semgrep", scan_type="sast", issues=0)
        
        try:
            output_file = self.output_dir / "semgrep_results.json"
            
            cmd = [
                "semgrep", "--config=auto",
                "--json",
                "--output", str(output_file),
                str(self.openssl_dir)
            ]
            
            if self.verbose:
                logger.info(f"Running Semgrep scan: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            if result.returncode in [0, 1]:  # Semgrep returns 1 for findings
                return self._parse_semgrep_results(output_file)
            else:
                logger.error(f"Semgrep scan failed: {result.stderr}")
                return ScanResult(tool="semgrep", scan_type="sast", issues=0)
                
        except subprocess.TimeoutExpired:
            logger.error("Semgrep scan timed out")
            return ScanResult(tool="semgrep", scan_type="sast", issues=0)
        except Exception as e:
            logger.error(f"Semgrep scan error: {e}")
            return ScanResult(tool="semgrep", scan_type="sast", issues=0)
    
    def _parse_semgrep_results(self, output_file: Path) -> ScanResult:
        """Parse Semgrep JSON results"""
        try:
            with open(output_file, 'r') as f:
                data = json.load(f)
            
            issues = len(data.get("results", []))
            critical = 0
            high = 0
            medium = 0
            low = 0
            
            for result in data.get("results", []):
                severity = result.get("extra", {}).get("severity", "").lower()
                
                if severity == "error":
                    critical += 1
                elif severity == "warning":
                    high += 1
                elif severity == "info":
                    medium += 1
                else:
                    low += 1
            
            return ScanResult(
                tool="semgrep",
                scan_type="sast",
                issues=issues,
                critical=critical,
                high=high,
                medium=medium,
                low=low,
                output_file=str(output_file)
            )
            
        except Exception as e:
            logger.error(f"Failed to parse Semgrep results: {e}")
            return ScanResult(tool="semgrep", scan_type="sast", issues=0)
    
    def _run_safety_scan(self) -> ScanResult:
        """Run Safety dependency scan"""
        if not self._check_tool_available("safety"):
            logger.warning("Safety not available, skipping dependency scan")
            return ScanResult(tool="safety", scan_type="dependency", issues=0)
        
        try:
            output_file = self.output_dir / "safety_results.json"
            
            cmd = [
                "safety", "check",
                "--json",
                "--output", str(output_file)
            ]
            
            if self.verbose:
                logger.info(f"Running Safety scan: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode in [0, 64]:  # Safety returns 64 for vulnerabilities
                return self._parse_safety_results(output_file)
            else:
                logger.error(f"Safety scan failed: {result.stderr}")
                return ScanResult(tool="safety", scan_type="dependency", issues=0)
                
        except subprocess.TimeoutExpired:
            logger.error("Safety scan timed out")
            return ScanResult(tool="safety", scan_type="dependency", issues=0)
        except Exception as e:
            logger.error(f"Safety scan error: {e}")
            return ScanResult(tool="safety", scan_type="dependency", issues=0)
    
    def _parse_safety_results(self, output_file: Path) -> ScanResult:
        """Parse Safety JSON results"""
        try:
            with open(output_file, 'r') as f:
                data = json.load(f)
            
            issues = len(data)
            critical = 0
            high = 0
            medium = 0
            low = 0
            
            for vuln in data:
                severity = vuln.get("severity", "").lower()
                
                if severity == "critical":
                    critical += 1
                elif severity == "high":
                    high += 1
                elif severity == "medium":
                    medium += 1
                elif severity == "low":
                    low += 1
            
            return ScanResult(
                tool="safety",
                scan_type="dependency",
                issues=issues,
                critical=critical,
                high=high,
                medium=medium,
                low=low,
                output_file=str(output_file)
            )
            
        except Exception as e:
            logger.error(f"Failed to parse Safety results: {e}")
            return ScanResult(tool="safety", scan_type="dependency", issues=0)
    
    def _generate_summary_report(self, scan_results: List[ScanResult]) -> str:
        """Generate security scan summary report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.output_dir / f"security_summary_{timestamp}.json"
        
        total_issues = sum(r.issues for r in scan_results)
        issues_by_severity = {
            "critical": sum(r.critical for r in scan_results),
            "high": sum(r.high for r in scan_results),
            "medium": sum(r.medium for r in scan_results),
            "low": sum(r.low for r in scan_results)
        }
        
        summary_data = {
            "timestamp": datetime.now().isoformat(),
            "total_issues": total_issues,
            "issues_by_severity": issues_by_severity,
            "scan_results": [
                {
                    "tool": r.tool,
                    "scan_type": r.scan_type,
                    "issues": r.issues,
                    "critical": r.critical,
                    "high": r.high,
                    "medium": r.medium,
                    "low": r.low,
                    "output_file": r.output_file
                }
                for r in scan_results
            ]
        }
        
        with open(report_file, 'w') as f:
            json.dump(summary_data, f, indent=2)
        
        return str(report_file)
    
    def scan(self) -> SecurityScanResult:
        """Execute comprehensive security scan"""
        scan_results = []
        
        try:
            if not self.openssl_dir.exists():
                return SecurityScanResult(
                    success=False,
                    error=f"OpenSSL source directory not found: {self.openssl_dir}"
                )
            
            # Run vulnerability scans
            if "vulnerability" in self.scan_types or "all" in self.scan_types:
                if "trivy" in self.tools or "all" in self.tools:
                    trivy_result = self._run_trivy_scan()
                    scan_results.append(trivy_result)
            
            # Run SAST scans
            if "sast" in self.scan_types or "all" in self.scan_types:
                if "bandit" in self.tools or "all" in self.tools:
                    bandit_result = self._run_bandit_scan()
                    scan_results.append(bandit_result)
                
                if "semgrep" in self.tools or "all" in self.tools:
                    semgrep_result = self._run_semgrep_scan()
                    scan_results.append(semgrep_result)
            
            # Run dependency scans
            if "dependency" in self.scan_types or "all" in self.scan_types:
                if "safety" in self.tools or "all" in self.tools:
                    safety_result = self._run_safety_scan()
                    scan_results.append(safety_result)
            
            # Generate summary report
            summary_file = self._generate_summary_report(scan_results)
            
            # Calculate totals
            total_issues = sum(r.issues for r in scan_results)
            issues_by_severity = {
                "critical": sum(r.critical for r in scan_results),
                "high": sum(r.high for r in scan_results),
                "medium": sum(r.medium for r in scan_results),
                "low": sum(r.low for r in scan_results)
            }
            
            return SecurityScanResult(
                success=True,
                output_dir=str(self.output_dir),
                scan_results=scan_results,
                total_issues=total_issues,
                issues_by_severity=issues_by_severity,
                fixed_issues=0  # TODO: Implement auto-fix functionality
            )
            
        except Exception as e:
            return SecurityScanResult(
                success=False,
                error=f"Security scan failed: {str(e)}"
            )


def main():
    """Main function for standalone execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="OpenSSL Security Scanner")
    parser.add_argument("--profile", "-p", help="Conan profile to use")
    parser.add_argument("--openssl-dir", help="OpenSSL source directory")
    parser.add_argument("--output-dir", help="Scan output directory")
    parser.add_argument("--scan-types", nargs="+", 
                       choices=["sast", "dast", "dependency", "license", "compliance", "all"], 
                       default=["all"], help="Types of scans to run")
    parser.add_argument("--tools", nargs="+", 
                       choices=["trivy", "bandit", "semgrep", "safety", "license-checker", "all"], 
                       default=["all"], help="Security tools to use")
    parser.add_argument("--severity", choices=["low", "medium", "high", "critical"], 
                       default="medium", help="Minimum severity to report")
    parser.add_argument("--format", choices=["json", "sarif", "html", "table"], 
                       default="json", help="Output format")
    parser.add_argument("--fix", action="store_true", help="Attempt to fix auto-fixable issues")
    parser.add_argument("--baseline", help="Baseline scan results")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Create scanner
    scanner = OpenSSLSecurityScanner(
        conan_api=None,  # Not needed for standalone
        profile=args.profile,
        openssl_dir=args.openssl_dir,
        output_dir=args.output_dir,
        scan_types=args.scan_types,
        tools=args.tools,
        severity=args.severity,
        format=args.format,
        fix=args.fix,
        baseline=args.baseline,
        verbose=args.verbose
    )
    
    # Execute security scan
    result = scanner.scan()
    
    if result.success:
        print("✅ OpenSSL security scan completed successfully")
        print(f"Output directory: {result.output_dir}")
        print(f"Scans completed: {len(result.scan_results)}")
        print(f"Total issues found: {result.total_issues}")
        print(f"Critical: {result.issues_by_severity.get('critical', 0)}")
        print(f"High: {result.issues_by_severity.get('high', 0)}")
        print(f"Medium: {result.issues_by_severity.get('medium', 0)}")
        print(f"Low: {result.issues_by_severity.get('low', 0)}")
        if args.verbose:
            for scan_result in result.scan_results:
                print(f"  - {scan_result.tool}: {scan_result.issues} issues")
    else:
        print(f"❌ OpenSSL security scan failed: {result.error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
