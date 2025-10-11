#!/usr/bin/env python3
"""
OpenSSL Security Scan Command for Conan Extension
Runs comprehensive security scans including SAST/DAST
"""

from conan.api.conan_api import ConanAPI
from conan.api.output import ConanOutput
from conan.cli.command import conan_command
import argparse
import os
import sys
from pathlib import Path


@conan_command(group="openssl")
def scan(conan_api: ConanAPI, parser, *args):
    """
    Run comprehensive security scans on OpenSSL.
    
    This command executes static and dynamic security analysis including
    vulnerability scanning, dependency analysis, and compliance checks.
    """
    parser.add_argument("--profile", "-p", help="Conan profile to use for scanning")
    parser.add_argument("--openssl-dir", help="OpenSSL source directory (default: openssl-source)")
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
    parser.add_argument("--baseline", help="Baseline scan results for comparison")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args(*args)
    
    try:
        # Import the OpenSSL security scanner script
        openssl_tools_root = Path(__file__).parent.parent.parent.parent
        sys.path.insert(0, str(openssl_tools_root / "scripts" / "conan"))
        
        from openssl_security_scanner import OpenSSLSecurityScanner
        
        # Create scanner instance
        scanner = OpenSSLSecurityScanner(
            conan_api=conan_api,
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
            ConanOutput().info("✅ OpenSSL security scan completed successfully")
            ConanOutput().info(f"Output directory: {result.output_dir}")
            ConanOutput().info(f"Scans completed: {len(result.scan_results)}")
            ConanOutput().info(f"Total issues found: {result.total_issues}")
            ConanOutput().info(f"Critical: {result.issues_by_severity.get('critical', 0)}")
            ConanOutput().info(f"High: {result.issues_by_severity.get('high', 0)}")
            ConanOutput().info(f"Medium: {result.issues_by_severity.get('medium', 0)}")
            ConanOutput().info(f"Low: {result.issues_by_severity.get('low', 0)}")
            if result.fixed_issues:
                ConanOutput().info(f"Auto-fixed issues: {result.fixed_issues}")
            if args.verbose:
                for scan_result in result.scan_results:
                    ConanOutput().info(f"  - {scan_result.tool}: {scan_result.issues} issues")
        else:
            ConanOutput().error(f"❌ OpenSSL security scan failed: {result.error}")
            return 1
            
    except ImportError as e:
        ConanOutput().error(f"❌ Failed to import OpenSSL security scanner module: {e}")
        ConanOutput().info("Make sure you're running from the openssl-tools repository")
        return 1
    except Exception as e:
        ConanOutput().error(f"❌ Unexpected error during security scan: {e}")
        return 1
    
    return 0
