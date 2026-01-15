#!/usr/bin/env python3
"""
Version-Aware Build Matrix Generator for OpenSSL CI/CD

Supports intelligent version fallback (4.0.0 → 3.6.0 → 3.4.1) and
component-based build matrices for the Python-based modernization.
"""

import argparse
import json
import os
import sys
from typing import Dict, List, Set, Any, Optional, Tuple
from pathlib import Path


class VersionAwareMatrixGenerator:
    """Generates build matrices with version fallback support for OpenSSL modernization"""

    def __init__(self):
        # Version compatibility matrix
        self.version_matrix = {
            "4.0.0": {
                "fallback_versions": ["4.0.0", "3.6.0"],
                "components": ["openssl", "libcrypto", "libssl"],
                "priority": "latest",
                "description": "OpenSSL 4.0.0 (development)"
            },
            "3.6.0": {
                "fallback_versions": ["3.6.0"],
                "components": ["openssl", "libcrypto", "libssl"],
                "priority": "stable",
                "description": "OpenSSL 3.6.0 (production-ready)"
            },
            "3.4.1": {
                "fallback_versions": ["3.4.1"],
                "components": ["openssl", "libcrypto", "libssl"],
                "priority": "lts",
                "description": "OpenSSL 3.4.1 (LTS)"
            }
        }

        # Platform configurations
        self.platform_configs = {
            "linux-x86_64": {
                "os": "ubuntu-22.04",
                "arch": "x86_64",
                "compilers": ["gcc-11", "clang-14"],
                "cache_key": "linux-x86_64"
            },
            "linux-aarch64": {
                "os": "ubuntu-22.04-arm",
                "arch": "arm64",
                "compilers": ["gcc-11"],
                "cache_key": "linux-aarch64"
            },
            "windows-x86_64": {
                "os": "windows-2022",
                "arch": "x86_64",
                "compilers": ["msvc-2022"],
                "cache_key": "windows-x86_64"
            },
            "macos-x86_64": {
                "os": "macos-13",
                "arch": "x86_64",
                "compilers": ["clang-15"],
                "cache_key": "macos-x86_64"
            },
            "macos-arm64": {
                "os": "macos-13",
                "arch": "arm64",
                "compilers": ["clang-15"],
                "cache_key": "macos-arm64"
            }
        }

        # Build configurations
        self.build_configs = {
            "release": {
                "build_type": "Release",
                "options": {"shared": False, "fips": False},
                "cache_key_suffix": "rel"
            },
            "debug": {
                "build_type": "Debug",
                "options": {"shared": False, "fips": False},
                "cache_key_suffix": "dbg"
            },
            "shared": {
                "build_type": "Release",
                "options": {"shared": True, "fips": False},
                "cache_key_suffix": "shared"
            },
            "fips": {
                "build_type": "Release",
                "options": {"shared": False, "fips": True},
                "cache_key_suffix": "fips"
            }
        }

    def get_available_versions(self) -> List[str]:
        """Get list of available OpenSSL versions in preference order"""
        return ["4.0.0", "3.6.0", "3.4.1"]

    def check_version_availability(self, version: str) -> bool:
        """Check if a specific OpenSSL version is available"""
        # In a real implementation, this would check:
        # - Git tags/branches
        # - Remote repository availability
        # - Local version files
        # For now, simulate availability
        available_versions = ["3.6.0", "3.4.1"]  # 4.0.0 not yet available
        return version in available_versions

    def resolve_version_with_fallback(self, target_version: str) -> Tuple[str, str]:
        """Resolve version with fallback logic. Returns (actual_version, reason)"""
        if self.check_version_availability(target_version):
            return target_version, "available"

        # Apply fallback logic
        fallback_versions = self.version_matrix.get(target_version, {}).get("fallback_versions", [])

        for fallback_version in fallback_versions[1:]:  # Skip the first (original) version
            if self.check_version_availability(fallback_version):
                return fallback_version, f"fallback_from_{target_version}"

        # Ultimate fallback
        return "3.6.0", f"fallback_from_{target_version}_to_default"

    def generate_component_matrix(self, target_version: str = "4.0.0") -> Dict[str, Any]:
        """Generate build matrix for all components with version fallback"""

        # Resolve version with fallback
        actual_version, fallback_reason = self.resolve_version_with_fallback(target_version)

        print(f"Target version: {target_version}", file=sys.stderr)
        print(f"Resolved version: {actual_version} ({fallback_reason})", file=sys.stderr)

        # Get version configuration
        version_config = self.version_matrix.get(actual_version, self.version_matrix["3.6.0"])

        # Generate matrix entries
        matrix_entries = []

        for component in version_config["components"]:
            for platform_name, platform_config in self.platform_configs.items():
                for compiler in platform_config["compilers"]:
                    for build_name, build_config in self.build_configs.items():

                        # Create matrix entry
                        entry = {
                            "component": component,
                            "version": actual_version,
                            "platform": platform_name,
                            "os": platform_config["os"],
                            "arch": platform_config["arch"],
                            "compiler": compiler,
                            "build_type": build_config["build_type"],
                            "cache_key": f"{platform_config['cache_key']}-{compiler.replace('-', '')}-{build_config['cache_key_suffix']}",
                            "options": build_config["options"].copy(),
                            "fallback_reason": fallback_reason if fallback_reason != "available" else None
                        }

                        # Add component-specific options
                        if component == "libcrypto":
                            entry["options"]["crypto_only"] = True
                        elif component == "libssl":
                            entry["options"]["ssl_only"] = True

                        matrix_entries.append(entry)

        # Create result matrix
        result = {
            "version": {
                "target": target_version,
                "actual": actual_version,
                "fallback_reason": fallback_reason,
                "description": version_config["description"]
            },
            "include": matrix_entries,
            "total_jobs": len(matrix_entries),
            "components": version_config["components"],
            "platforms": list(self.platform_configs.keys()),
            "build_types": list(self.build_configs.keys()),
            "version_fallback_applied": fallback_reason != "available"
        }

        return result

    def generate_minimal_matrix(self, target_version: str = "4.0.0") -> Dict[str, Any]:
        """Generate minimal build matrix for quick validation"""

        # Resolve version with fallback
        actual_version, fallback_reason = self.resolve_version_with_fallback(target_version)

        # Only include essential builds
        minimal_entries = [
            {
                "component": "openssl",
                "version": actual_version,
                "platform": "linux-x86_64",
                "os": "ubuntu-22.04",
                "arch": "x86_64",
                "compiler": "gcc-11",
                "build_type": "Release",
                "cache_key": "linux-x86_64-gcc11-rel",
                "options": {"shared": False, "fips": False},
                "fallback_reason": fallback_reason if fallback_reason != "available" else None
            },
            {
                "component": "openssl",
                "version": actual_version,
                "platform": "linux-x86_64",
                "os": "ubuntu-22.04",
                "arch": "x86_64",
                "compiler": "gcc-11",
                "build_type": "Debug",
                "cache_key": "linux-x86_64-gcc11-dbg",
                "options": {"shared": False, "fips": False},
                "fallback_reason": fallback_reason if fallback_reason != "available" else None
            }
        ]

        return {
            "version": {
                "target": target_version,
                "actual": actual_version,
                "fallback_reason": fallback_reason,
                "description": self.version_matrix.get(actual_version, {}).get("description", "")
            },
            "include": minimal_entries,
            "total_jobs": len(minimal_entries),
            "minimal": True,
            "version_fallback_applied": fallback_reason != "available"
        }

    def generate_matrix_for_changes(self, changed_files: List[str], target_version: str = "4.0.0") -> Dict[str, Any]:
        """Generate optimized matrix based on changed files"""

        # Resolve version with fallback
        actual_version, fallback_reason = self.resolve_version_with_fallback(target_version)

        # Analyze changed files to determine what needs testing
        components_to_test = set()
        platforms_to_test = set()
        build_types_to_test = {"release"}  # Always include release

        for file_path in changed_files:
            if file_path.startswith("crypto/") or file_path.startswith("include/openssl/"):
                components_to_test.add("libcrypto")
            if file_path.startswith("ssl/"):
                components_to_test.add("libssl")
            if "fips" in file_path.lower():
                build_types_to_test.add("fips")
            if file_path.startswith("test/"):
                build_types_to_test.add("debug")

        # Default to full openssl if no specific component detected
        if not components_to_test:
            components_to_test.add("openssl")

        # Default to linux platform if not specified
        if not platforms_to_test:
            platforms_to_test.add("linux-x86_64")

        # Generate targeted matrix
        matrix_entries = []

        for component in components_to_test:
            for platform in platforms_to_test:
                if platform in self.platform_configs:
                    platform_config = self.platform_configs[platform]
                    compiler = platform_config["compilers"][0]  # Use first compiler

                    for build_type in build_types_to_test:
                        if build_type in self.build_configs:
                            build_config = self.build_configs[build_type]

                            entry = {
                                "component": component,
                                "version": actual_version,
                                "platform": platform,
                                "os": platform_config["os"],
                                "arch": platform_config["arch"],
                                "compiler": compiler,
                                "build_type": build_config["build_type"],
                                "cache_key": f"{platform_config['cache_key']}-{compiler.replace('-', '')}-{build_config['cache_key_suffix']}",
                                "options": build_config["options"].copy(),
                                "fallback_reason": fallback_reason if fallback_reason != "available" else None,
                                "triggered_by_changes": True
                            }

                            matrix_entries.append(entry)

        return {
            "version": {
                "target": target_version,
                "actual": actual_version,
                "fallback_reason": fallback_reason,
                "description": self.version_matrix.get(actual_version, {}).get("description", "")
            },
            "include": matrix_entries,
            "total_jobs": len(matrix_entries),
            "components_analyzed": list(components_to_test),
            "changed_files_count": len(changed_files),
            "version_fallback_applied": fallback_reason != "available",
            "change_based_optimization": True
        }


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Generate version-aware build matrix for OpenSSL')
    parser.add_argument('--target-version', default='4.0.0',
                       help='Target OpenSSL version (with fallback support)')
    parser.add_argument('--mode', choices=['full', 'minimal', 'changes'],
                       default='full', help='Matrix generation mode')
    parser.add_argument('--changed-files', nargs='*', default=[],
                       help='List of changed files for change-based optimization')
    parser.add_argument('--output', required=True,
                       help='Output JSON file')
    parser.add_argument('--verbose', action='store_true',
                       help='Verbose output')

    args = parser.parse_args()

    try:
        generator = VersionAwareMatrixGenerator()

        if args.verbose:
            print(f"Generating {args.mode} matrix for version {args.target_version}", file=sys.stderr)

        # Generate appropriate matrix
        if args.mode == 'minimal':
            result = generator.generate_minimal_matrix(args.target_version)
        elif args.mode == 'changes':
            result = generator.generate_matrix_for_changes(args.changed_files, args.target_version)
        else:  # full
            result = generator.generate_component_matrix(args.target_version)

        # Write output
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)

        if args.verbose:
            print(f"Generated matrix with {result['total_jobs']} jobs", file=sys.stderr)
            if result.get('version_fallback_applied'):
                print(f"Version fallback applied: {result['version']['target']} -> {result['version']['actual']}", file=sys.stderr)
            print(f"Matrix written to: {args.output}", file=sys.stderr)

    except Exception as e:
        print(f"Error generating build matrix: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()