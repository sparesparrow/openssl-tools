#!/usr/bin/env python3
"""
Automated Publishing Script for OpenSSL Python-Based Modernization
Handles component publishing to Cloudsmith with validation and rollback
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
import json

class AutomatedPublisher:
    """Automated publisher for OpenSSL components with validation"""

    def __init__(self, remote_name="sparesparrow", dry_run=False):
        self.remote_name = remote_name
        self.dry_run = dry_run
        self.publish_log = []
        self.rollback_info = []

    def log(self, message, level="INFO"):
        """Log a message with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        print(log_entry)
        self.publish_log.append(log_entry)

    def validate_environment(self):
        """Validate publishing environment"""
        self.log("Validating publishing environment...")

        # Check Cloudsmith API key
        api_key = os.environ.get("CLOUDSMITH_API_KEY")
        if not api_key:
            raise RuntimeError("CLOUDSMITH_API_KEY environment variable not set")

        # Check Conan installation
        try:
            result = subprocess.run(["conan", "--version"],
                                  capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                raise RuntimeError("Conan not found or not working")
            self.log(f"Conan version: {result.stdout.strip()}")
        except Exception as e:
            raise RuntimeError(f"Conan validation failed: {e}")

        # Check remote configuration
        try:
            result = subprocess.run(["conan", "remote", "list"],
                                  capture_output=True, text=True, timeout=10)
            if self.remote_name not in result.stdout:
                raise RuntimeError(f"Remote '{self.remote_name}' not configured")
            self.log(f"Remote '{self.remote_name}' is configured")
        except Exception as e:
            raise RuntimeError(f"Remote validation failed: {e}")

        self.log("Environment validation completed")

    def validate_component(self, component_name, version):
        """Validate a component before publishing"""
        self.log(f"Validating component: {component_name}/{version}")

        # Check if package exists in local cache
        try:
            result = subprocess.run(
                ["conan", "search", f"{component_name}/{version}@sparesparrow/stable"],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode != 0:
                raise RuntimeError(f"Package {component_name}/{version} not found in local cache")
            self.log(f"Package {component_name}/{version} found in local cache")
        except Exception as e:
            raise RuntimeError(f"Package validation failed: {e}")

        # Run comprehensive validation
        try:
            result = subprocess.run([
                sys.executable, "../validate_publish.py",
                f"{component_name}/{version}@sparesparrow/stable",
                self.remote_name, "--comprehensive"
            ], cwd=Path(__file__).parent.parent, timeout=60)

            if result.returncode != 0:
                raise RuntimeError(f"Comprehensive validation failed for {component_name}")
            self.log(f"Comprehensive validation passed for {component_name}")
        except Exception as e:
            raise RuntimeError(f"Validation failed: {e}")

    def publish_component(self, component_name, version):
        """Publish a component to Cloudsmith"""
        package_ref = f"{component_name}/{version}@sparesparrow/stable"

        self.log(f"Publishing component: {package_ref}")

        if self.dry_run:
            self.log(f"DRY RUN: Would publish {package_ref}")
            return True

        # Publish to Cloudsmith
        cmd = ["conan", "upload", package_ref, "-r", self.remote_name, "--confirm"]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode != 0:
                error_msg = result.stderr or result.stdout
                raise RuntimeError(f"Upload failed: {error_msg}")

            self.log(f"Successfully published {package_ref}")
            self.rollback_info.append({
                "action": "upload",
                "package_ref": package_ref,
                "timestamp": datetime.now().isoformat()
            })
            return True

        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Upload timed out for {package_ref}")
        except Exception as e:
            raise RuntimeError(f"Upload failed for {package_ref}: {e}")

    def rollback_failed_publish(self):
        """Rollback any failed publishes (not implemented - would need API access)"""
        self.log("WARNING: Rollback not implemented - manual intervention required")
        self.log("Rollback information:", "WARN")
        for rollback_item in self.rollback_info:
            self.log(f"  - {rollback_item}", "WARN")

    def publish_all_components(self, version="3.6.0"):
        """Publish all components for a given version"""
        components = ["openssl-tools", "libcrypto", "libssl", "openssl"]

        self.log(f"Starting automated publish for version {version}")
        self.log(f"Dry run mode: {self.dry_run}")

        try:
            # Validate environment
            self.validate_environment()

            # Publish components in dependency order
            for component in components:
                try:
                    self.validate_component(component, version)
                    self.publish_component(component, version)
                except Exception as e:
                    self.log(f"Failed to publish {component}: {e}", "ERROR")
                    self.rollback_failed_publish()
                    raise

            self.log("All components published successfully!")

        except Exception as e:
            self.log(f"Automated publish failed: {e}", "ERROR")
            self.rollback_failed_publish()
            raise

    def save_publish_log(self, filename=None):
        """Save the publish log to a file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"publish_log_{timestamp}.txt"

        with open(filename, 'w') as f:
            f.write("OpenSSL Automated Publish Log\\n")
            f.write("=" * 40 + "\\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\\n")
            f.write(f"Dry Run: {self.dry_run}\\n\\n")
            f.write("\\n".join(self.publish_log))

        self.log(f"Publish log saved to: {filename}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Automated publishing for OpenSSL components')
    parser.add_argument('--version', default='3.6.0',
                       help='Version to publish (default: 3.6.0)')
    parser.add_argument('--remote', default='sparesparrow',
                       help='Cloudsmith remote name (default: sparesparrow)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Perform dry run without actual publishing')
    parser.add_argument('--log-file', help='Save publish log to specified file')

    args = parser.parse_args()

    publisher = AutomatedPublisher(remote_name=args.remote, dry_run=args.dry_run)

    try:
        publisher.publish_all_components(version=args.version)
        publisher.save_publish_log(args.log_file)
        print("\\n🎉 Automated publish completed successfully!")
        return 0

    except Exception as e:
        publisher.save_publish_log(args.log_file)
        print(f"\\n❌ Automated publish failed: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())