#!/usr/bin/env python3
"""
OpenSSL Package Tracker Conan Extension
Integrates database schema validation with Conan package storage
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from conan.api.output import ConanOutput
from conan.cli.command import ConanCommand
from conan.cli.commands import ExtCommand

# Import the OpenSSL schema validator
from ..database.openssl_schema_validator import OpenSSLSchemaValidator

logger = logging.getLogger(__name__)

class OpenSSLPackageTracker(ExtCommand):
    """Conan extension for tracking OpenSSL packages with database validation"""

    def __init__(self):
        super().__init__()
        self.name = "openssl track-package"
        self.description = "Track OpenSSL package in cache with database schema validation"

    def run(self, conan_api, parser, *args):
        """Execute OpenSSL package tracking"""
        output = ConanOutput()
        output.info("📦 Tracking OpenSSL package with database validation...")

        try:
            # Parse arguments
            import argparse
            arg_parser = argparse.ArgumentParser(description="Track OpenSSL Package")
            arg_parser.add_argument("--package", required=True, help="Package reference (name/version@user/channel)")
            arg_parser.add_argument("--build-stage", required=True,
                                  choices=["foundation", "tooling", "domain", "orchestration"],
                                  help="Build stage")
            arg_parser.add_argument("--config", type=Path, help="Configuration file path")
            arg_parser.add_argument("--project-root", type=Path, default=Path.cwd(),
                                  help="Project root directory")

            parsed_args = arg_parser.parse_args(args)

            # Initialize validator
            validator = OpenSSLSchemaValidator(parsed_args.project_root)

            # Load configuration if provided
            config_data = {}
            if parsed_args.config and parsed_args.config.exists():
                with open(parsed_args.config, 'r') as f:
                    config_data = json.load(f)

            # Parse package reference
            package_ref = parsed_args.package
            package_info = self._parse_package_reference(package_ref)
            package_info["config"] = config_data

            # Track package in cache
            success = validator.track_package_in_cache(package_info, parsed_args.build_stage)

            if success:
                output.success(f"✅ Package tracked successfully: {package_ref}")
                return 0
            else:
                output.error(f"❌ Package tracking failed: {package_ref}")
                return 1

        except Exception as e:
            output.error(f"❌ Package tracking failed: {e}")
            return 1

    def _parse_package_reference(self, package_ref: str) -> Dict:
        """Parse Conan package reference"""
        # Format: name/version@user/channel#package_id
        parts = package_ref.split('@')
        if len(parts) != 2:
            raise ValueError(f"Invalid package reference format: {package_ref}")

        name_version = parts[0]
        user_channel = parts[1]

        # Parse name/version
        name_version_parts = name_version.split('/')
        if len(name_version_parts) != 2:
            raise ValueError(f"Invalid name/version format: {name_version}")

        name = name_version_parts[0]
        version = name_version_parts[1]

        # Parse user/channel
        user_channel_parts = user_channel.split('/')
        if len(user_channel_parts) != 2:
            raise ValueError(f"Invalid user/channel format: {user_channel}")

        user = user_channel_parts[0]
        channel = user_channel_parts[1]

        # Generate package ID (in real implementation, this would come from Conan)
        package_id = f"{name}-{version}-{user}-{channel}".replace('/', '-').replace('@', '-')

        return {
            "name": name,
            "version": version,
            "user": user,
            "channel": channel,
            "package_id": package_id
        }

class OpenSSLCacheManager(ExtCommand):
    """Conan extension for managing OpenSSL package cache with validation"""

    def __init__(self):
        super().__init__()
        self.name = "openssl cache-manager"
        self.description = "Manage OpenSSL package cache with database validation"

    def run(self, conan_api, parser, *args):
        """Execute OpenSSL cache management"""
        output = ConanOutput()
        output.info("🗄️ Managing OpenSSL package cache...")

        try:
            # Parse arguments
            import argparse
            arg_parser = argparse.ArgumentParser(description="Manage OpenSSL Cache")
            arg_parser.add_argument("--action", required=True,
                                  choices=["validate", "clean", "report", "summary"],
                                  help="Action to perform")
            arg_parser.add_argument("--project-root", type=Path, default=Path.cwd(),
                                  help="Project root directory")
            arg_parser.add_argument("--build-stage",
                                  choices=["foundation", "tooling", "domain", "orchestration"],
                                  help="Filter by build stage")

            parsed_args = arg_parser.parse_args(args)

            # Initialize validator
            validator = OpenSSLSchemaValidator(parsed_args.project_root)

            if parsed_args.action == "validate":
                self._validate_cache(validator, output, parsed_args.build_stage)
            elif parsed_args.action == "clean":
                self._clean_cache(validator, output, parsed_args.build_stage)
            elif parsed_args.action == "report":
                self._generate_report(validator, output)
            elif parsed_args.action == "summary":
                self._show_summary(validator, output)

            return 0

        except Exception as e:
            output.error(f"❌ Cache management failed: {e}")
            return 1

    def _validate_cache(self, validator: OpenSSLSchemaValidator, output: ConanOutput, build_stage: Optional[str]):
        """Validate cache packages"""
        output.info("🔍 Validating cache packages...")

        # Get packages to validate
        packages = validator._get_packages_to_validate(build_stage)

        validated_count = 0
        failed_count = 0

        for package in packages:
            try:
                # Re-validate package
                cache_path = Path(package["cache_path"])
                validation_result = validator._validate_package_integrity(cache_path, package)

                # Update validation status
                validator._update_package_validation_status(package["id"], validation_result)

                if validation_result["status"] == "passed":
                    validated_count += 1
                else:
                    failed_count += 1
                    output.warning(f"⚠️ Package validation failed: {package['package_name']}/{package['package_version']}")

            except Exception as e:
                failed_count += 1
                output.error(f"❌ Validation error for {package['package_name']}: {e}")

        output.success(f"✅ Cache validation complete: {validated_count} passed, {failed_count} failed")

    def _clean_cache(self, validator: OpenSSLSchemaValidator, output: ConanOutput, build_stage: Optional[str]):
        """Clean invalid cache packages"""
        output.info("🧹 Cleaning invalid cache packages...")

        # Get invalid packages
        invalid_packages = validator._get_invalid_packages(build_stage)

        cleaned_count = 0

        for package in invalid_packages:
            try:
                cache_path = Path(package["cache_path"])
                if cache_path.exists():
                    import shutil
                    shutil.rmtree(cache_path)
                    cleaned_count += 1
                    output.info(f"🗑️ Cleaned: {package['package_name']}/{package['package_version']}")

                # Remove from database
                validator._remove_package_from_cache(package["id"])

            except Exception as e:
                output.error(f"❌ Failed to clean {package['package_name']}: {e}")

        output.success(f"✅ Cache cleaning complete: {cleaned_count} packages cleaned")

    def _generate_report(self, validator: OpenSSLSchemaValidator, output: ConanOutput):
        """Generate cache report"""
        output.info("📊 Generating cache report...")

        try:
            report_path = validator.generate_cache_report()
            if report_path:
                output.success(f"✅ Cache report generated: {report_path}")
            else:
                output.error("❌ Failed to generate cache report")
        except Exception as e:
            output.error(f"❌ Report generation failed: {e}")

    def _show_summary(self, validator: OpenSSLSchemaValidator, output: ConanOutput):
        """Show cache summary"""
        output.info("📋 Cache Summary:")

        try:
            summary = validator.get_package_cache_summary()

            output.info(f"Total Packages: {summary.get('total_packages', 0)}")
            output.info(f"Validated Packages: {summary.get('validated_packages', 0)}")
            output.info(f"Failed Packages: {summary.get('failed_packages', 0)}")
            output.info(f"Pending Packages: {summary.get('pending_packages', 0)}")

            output.info("\nBuild Stage Statistics:")
            for stage_stat in summary.get('stage_statistics', []):
                output.info(f"  {stage_stat['stage']}: {stage_stat['count']} packages, "
                          f"{stage_stat['total_files']} files, "
                          f"{stage_stat['total_size']:,} bytes")

        except Exception as e:
            output.error(f"❌ Failed to get cache summary: {e}")

class OpenSSLBuildTracker(ExtCommand):
    """Conan extension for tracking OpenSSL build stages"""

    def __init__(self):
        super().__init__()
        self.name = "openssl track-build"
        self.description = "Track OpenSSL build stage with database validation"

    def run(self, conan_api, parser, *args):
        """Execute OpenSSL build tracking"""
        output = ConanOutput()
        output.info("🏗️ Tracking OpenSSL build stage...")

        try:
            # Parse arguments
            import argparse
            arg_parser = argparse.ArgumentParser(description="Track OpenSSL Build")
            arg_parser.add_argument("--stage", required=True,
                                  choices=["foundation", "tooling", "domain", "orchestration"],
                                  help="Build stage")
            arg_parser.add_argument("--package", required=True, help="Package reference")
            arg_parser.add_argument("--action", required=True,
                                  choices=["start", "complete", "fail"],
                                  help="Build action")
            arg_parser.add_argument("--config", type=Path, help="Configuration file path")
            arg_parser.add_argument("--project-root", type=Path, default=Path.cwd(),
                                  help="Project root directory")
            arg_parser.add_argument("--log", type=Path, help="Build log file path")

            parsed_args = arg_parser.parse_args(args)

            # Initialize validator
            validator = OpenSSLSchemaValidator(parsed_args.project_root)

            # Parse package reference
            package_ref = parsed_args.package
            package_info = self._parse_package_reference(package_ref)

            # Load configuration if provided
            config_data = {}
            if parsed_args.config and parsed_args.config.exists():
                with open(parsed_args.config, 'r') as f:
                    config_data = json.load(f)

            # Track build stage
            success = validator._track_build_stage(
                parsed_args.stage,
                package_info,
                parsed_args.action,
                config_data,
                parsed_args.log
            )

            if success:
                output.success(f"✅ Build stage tracked: {parsed_args.stage} - {parsed_args.action}")
                return 0
            else:
                output.error(f"❌ Build stage tracking failed: {parsed_args.stage}")
                return 1

        except Exception as e:
            output.error(f"❌ Build tracking failed: {e}")
            return 1

    def _parse_package_reference(self, package_ref: str) -> Dict:
        """Parse Conan package reference"""
        # Same implementation as OpenSSLPackageTracker
        parts = package_ref.split('@')
        if len(parts) != 2:
            raise ValueError(f"Invalid package reference format: {package_ref}")

        name_version = parts[0]
        user_channel = parts[1]

        name_version_parts = name_version.split('/')
        if len(name_version_parts) != 2:
            raise ValueError(f"Invalid name/version format: {name_version}")

        name = name_version_parts[0]
        version = name_version_parts[1]

        user_channel_parts = user_channel.split('/')
        if len(user_channel_parts) != 2:
            raise ValueError(f"Invalid user/channel format: {user_channel}")

        user = user_channel_parts[0]
        channel = user_channel_parts[1]

        return {
            "name": name,
            "version": version,
            "user": user,
            "channel": channel
        }

# Register all OpenSSL package tracking commands
def register_openssl_package_commands():
    """Register all OpenSSL package tracking commands"""
    return [
        OpenSSLPackageTracker(),
        OpenSSLCacheManager(),
        OpenSSLBuildTracker()
    ]
