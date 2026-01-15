#!/usr/bin/env python3
"""
Integrate Cache Validation with Conan Package Storage
Integrates database schema validation with Conan package storage for all build stages
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# Add the openssl_tools module to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from openssl_tools.database.openssl_schema_validator import OpenSSLSchemaValidator

logger = logging.getLogger(__name__)

class ConanCacheValidator:
    """Integrates database schema validation with Conan cache management"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.validator = OpenSSLSchemaValidator(project_root)
        self.conan_cache_root = Path.home() / ".conan2" / "p"

    def setup_cache_validation(self):
        """Set up cache validation system"""
        logger.info("🔧 Setting up cache validation system...")

        try:
            # Setup OpenSSL databases
            self.validator.setup_openssl_databases()

            # Create cache monitoring configuration
            self._create_cache_monitoring_config()

            # Setup cache hooks
            self._setup_cache_hooks()

            logger.info("✅ Cache validation system setup complete")
            return True

        except Exception as e:
            logger.error(f"❌ Cache validation setup failed: {e}")
            return False

    def _create_cache_monitoring_config(self):
        """Create cache monitoring configuration"""
        config = {
            "cache_monitoring": {
                "enabled": True,
                "monitor_package_creation": True,
                "monitor_package_validation": True,
                "monitor_package_removal": True,
                "validation_rules": {
                    "validate_on_create": True,
                    "validate_on_access": False,
                    "validate_on_remove": True,
                    "strict_validation": True
                },
                "build_stages": {
                    "foundation": {
                        "packages": ["openssl-conan-base", "openssl-fips-policy"],
                        "validation_required": True
                    },
                    "tooling": {
                        "packages": ["openssl-tools"],
                        "validation_required": True
                    },
                    "domain": {
                        "packages": ["openssl"],
                        "validation_required": True
                    },
                    "orchestration": {
                        "packages": ["mcp-project-orchestrator"],
                        "validation_required": False
                    }
                }
            }
        }

        config_path = self.project_root / "conan-dev" / "cache-monitoring.yml"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(config_path, 'w') as f:
            import yaml
            yaml.dump(config, f, default_flow_style=False)

        logger.info(f"✅ Cache monitoring configuration created: {config_path}")

    def _setup_cache_hooks(self):
        """Set up cache monitoring hooks"""
        hooks_dir = self.project_root / "conan-dev" / "hooks"
        hooks_dir.mkdir(parents=True, exist_ok=True)

        # Create package creation hook
        creation_hook = hooks_dir / "package_creation_hook.py"
        with open(creation_hook, 'w') as f:
            f.write('''#!/usr/bin/env python3
"""
Conan Package Creation Hook
Monitors package creation and triggers database validation
"""

import os
import sys
import json
from pathlib import Path

def post_package_creation(conanfile, package_folder, **kwargs):
    """Hook called after package creation"""
    try:
        # Get package information
        package_info = {
            "name": conanfile.name,
            "version": conanfile.version,
            "user": conanfile.user or "unknown",
            "channel": conanfile.channel or "unknown",
            "package_id": str(conanfile.package_id),
            "config": {
                "options": dict(conanfile.options),
                "settings": dict(conanfile.settings)
            }
        }

        # Determine build stage based on package name
        build_stage = determine_build_stage(package_info["name"])

        # Call validation script
        validation_script = Path(__file__).parent.parent / "scripts" / "conan" / "validate_package.py"
        if validation_script.exists():
            import subprocess
            subprocess.run([
                sys.executable, str(validation_script),
                "--package-info", json.dumps(package_info),
                "--build-stage", build_stage,
                "--package-folder", str(package_folder)
            ], check=False)

    except Exception as e:
        print(f"Warning: Package creation hook failed: {e}")

def determine_build_stage(package_name: str) -> str:
    """Determine build stage based on package name"""
    if "openssl-conan-base" in package_name or "openssl-fips-policy" in package_name:
        return "foundation"
    elif "openssl-tools" in package_name:
        return "tooling"
    elif package_name == "openssl":
        return "domain"
    elif "mcp-project-orchestrator" in package_name:
        return "orchestration"
    else:
        return "unknown"
''')

        # Create package removal hook
        removal_hook = hooks_dir / "package_removal_hook.py"
        with open(removal_hook, 'w') as f:
            f.write('''#!/usr/bin/env python3
"""
Conan Package Removal Hook
Monitors package removal and updates database
"""

import os
import sys
import json
from pathlib import Path

def pre_package_removal(conanfile, package_folder, **kwargs):
    """Hook called before package removal"""
    try:
        # Get package information
        package_info = {
            "name": conanfile.name,
            "version": conanfile.version,
            "user": conanfile.user or "unknown",
            "channel": conanfile.channel or "unknown",
            "package_id": str(conanfile.package_id)
        }

        # Call removal script
        removal_script = Path(__file__).parent.parent / "scripts" / "conan" / "remove_package.py"
        if removal_script.exists():
            import subprocess
            subprocess.run([
                sys.executable, str(removal_script),
                "--package-info", json.dumps(package_info)
            ], check=False)

    except Exception as e:
        print(f"Warning: Package removal hook failed: {e}")
''')

        logger.info(f"✅ Cache hooks created in: {hooks_dir}")

    def validate_existing_cache(self):
        """Validate existing packages in Conan cache"""
        logger.info("🔍 Validating existing packages in Conan cache...")

        try:
            if not self.conan_cache_root.exists():
                logger.warning("Conan cache root does not exist")
                return False

            # Find all OpenSSL-related packages
            openssl_packages = self._find_openssl_packages()

            validation_results = {
                "total_packages": len(openssl_packages),
                "validated_packages": 0,
                "failed_packages": 0,
                "package_details": []
            }

            for package_info in openssl_packages:
                logger.info(f"Validating package: {package_info['name']}/{package_info['version']}")

                # Determine build stage
                build_stage = self._determine_build_stage(package_info['name'])

                # Track package in database
                success = self.validator.track_package_in_cache(package_info, build_stage)

                if success:
                    validation_results["validated_packages"] += 1
                    validation_results["package_details"].append({
                        "package": f"{package_info['name']}/{package_info['version']}",
                        "stage": build_stage,
                        "status": "validated"
                    })
                else:
                    validation_results["failed_packages"] += 1
                    validation_results["package_details"].append({
                        "package": f"{package_info['name']}/{package_info['version']}",
                        "stage": build_stage,
                        "status": "failed"
                    })

            # Save validation results
            results_path = self.project_root / "conan-dev" / "cache-validation-results.json"
            with open(results_path, 'w') as f:
                json.dump(validation_results, f, indent=2)

            logger.info(f"✅ Cache validation complete: {validation_results['validated_packages']}/{validation_results['total_packages']} packages validated")
            logger.info(f"📄 Results saved to: {results_path}")

            return True

        except Exception as e:
            logger.error(f"❌ Cache validation failed: {e}")
            return False

    def _find_openssl_packages(self) -> List[Dict]:
        """Find OpenSSL-related packages in Conan cache"""
        openssl_packages = []

        try:
            # Look for packages with OpenSSL-related names
            openssl_patterns = [
                "openssl*",
                "*openssl*",
                "ssl*",
                "crypto*"
            ]

            for pattern in openssl_patterns:
                for package_dir in self.conan_cache_root.glob(pattern):
                    if package_dir.is_dir():
                        package_info = self._extract_package_info(package_dir)
                        if package_info:
                            openssl_packages.append(package_info)

            # Also look for packages in subdirectories
            for subdir in self.conan_cache_root.iterdir():
                if subdir.is_dir():
                    for package_dir in subdir.glob("*openssl*"):
                        if package_dir.is_dir():
                            package_info = self._extract_package_info(package_dir)
                            if package_info:
                                openssl_packages.append(package_info)

        except Exception as e:
            logger.error(f"Failed to find OpenSSL packages: {e}")

        return openssl_packages

    def _extract_package_info(self, package_dir: Path) -> Optional[Dict]:
        """Extract package information from directory"""
        try:
            # Parse package directory name
            # Format: name-version-user-channel-package_id
            dir_name = package_dir.name
            parts = dir_name.split('-')

            if len(parts) < 5:
                return None

            # Reconstruct package info
            package_info = {
                "name": parts[0],
                "version": parts[1],
                "user": parts[2],
                "channel": parts[3],
                "package_id": '-'.join(parts[4:]),
                "cache_path": str(package_dir),
                "config": {}  # Would be extracted from conaninfo.txt in real implementation
            }

            # Try to read conaninfo.txt for more details
            conaninfo_path = package_dir / "conaninfo.txt"
            if conaninfo_path.exists():
                try:
                    with open(conaninfo_path, 'r') as f:
                        content = f.read()
                        # Parse conaninfo.txt content (simplified)
                        package_info["config"]["conaninfo"] = content
                except Exception:
                    pass

            return package_info

        except Exception as e:
            logger.warning(f"Failed to extract package info from {package_dir}: {e}")
            return None

    def _determine_build_stage(self, package_name: str) -> str:
        """Determine build stage based on package name"""
        if "openssl-conan-base" in package_name or "openssl-fips-policy" in package_name:
            return "foundation"
        elif "openssl-tools" in package_name:
            return "tooling"
        elif package_name == "openssl":
            return "domain"
        elif "mcp-project-orchestrator" in package_name:
            return "orchestration"
        else:
            return "unknown"

    def monitor_cache_changes(self):
        """Monitor cache changes and update database"""
        logger.info("👁️ Starting cache monitoring...")

        try:
            # This would typically use file system monitoring
            # For now, we'll just validate the current state
            return self.validate_existing_cache()

        except Exception as e:
            logger.error(f"❌ Cache monitoring failed: {e}")
            return False

    def generate_cache_report(self) -> str:
        """Generate comprehensive cache report"""
        logger.info("📊 Generating comprehensive cache report...")

        try:
            # Get package cache summary
            summary = self.validator.get_package_cache_summary()

            # Generate detailed report
            report_content = f"""# OpenSSL Conan Cache Validation Report

**Generated:** {datetime.now().isoformat()}
**Project Root:** {self.project_root}
**Conan Cache Root:** {self.conan_cache_root}

## Executive Summary

- **Total Packages:** {summary.get('total_packages', 0)}
- **Validated Packages:** {summary.get('validated_packages', 0)}
- **Failed Packages:** {summary.get('failed_packages', 0)}
- **Pending Packages:** {summary.get('pending_packages', 0)}

## Build Stage Analysis

"""

            for stage_stat in summary.get('stage_statistics', []):
                report_content += f"""### {stage_stat['stage'].title()} Stage
- **Package Count:** {stage_stat['count']}
- **Total Files:** {stage_stat['total_files']}
- **Total Size:** {stage_stat['total_size']:,} bytes
- **Average Size per Package:** {stage_stat['total_size'] // max(stage_stat['count'], 1):,} bytes

"""

            # Add cache health analysis
            report_content += """## Cache Health Analysis

### Validation Status
"""

            if summary.get('failed_packages', 0) > 0:
                report_content += f"- ⚠️ **{summary['failed_packages']} packages failed validation**\n"
                report_content += "- 🔍 **Investigation required** for failed packages\n"
            else:
                report_content += "- ✅ **All packages passed validation**\n"

            if summary.get('pending_packages', 0) > 0:
                report_content += f"- ⏳ **{summary['pending_packages']} packages pending validation**\n"

            # Add recommendations
            report_content += """
## Recommendations

1. **Regular Validation**: Run cache validation after each build
2. **Cleanup Failed Packages**: Remove packages that consistently fail validation
3. **Monitor Cache Growth**: Track cache size and implement cleanup policies
4. **Backup Validated Packages**: Ensure validated packages are backed up

## Next Steps

1. Review failed package validations
2. Implement automated cache cleanup
3. Set up regular cache monitoring
4. Document cache management procedures
"""

            # Save report
            report_path = self.project_root / "conan-dev" / "cache-validation-report.md"
            with open(report_path, 'w') as f:
                f.write(report_content)

            logger.info(f"✅ Cache report generated: {report_path}")
            return str(report_path)

        except Exception as e:
            logger.error(f"❌ Failed to generate cache report: {e}")
            return ""

def main():
    """Main function for cache validation integration"""
    import argparse

    parser = argparse.ArgumentParser(description="Integrate Cache Validation with Conan")
    parser.add_argument("--project-root", type=Path, default=Path.cwd(),
                       help="Project root directory")
    parser.add_argument("--action", required=True,
                       choices=["setup", "validate", "monitor", "report"],
                       help="Action to perform")

    args = parser.parse_args()

    # Initialize cache validator
    cache_validator = ConanCacheValidator(args.project_root)

    if args.action == "setup":
        success = cache_validator.setup_cache_validation()
        return 0 if success else 1

    elif args.action == "validate":
        success = cache_validator.validate_existing_cache()
        return 0 if success else 1

    elif args.action == "monitor":
        success = cache_validator.monitor_cache_changes()
        return 0 if success else 1

    elif args.action == "report":
        report_path = cache_validator.generate_cache_report()
        if report_path:
            print(f"Report generated: {report_path}")
            return 0
        else:
            return 1

if __name__ == "__main__":
    exit(main())
