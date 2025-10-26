#!/usr/bin/env python3
"""
OpenSSL Database Schema Validation System
Extends the base database schema validator with OpenSSL-specific validation rules
"""

import os
import sys
import json
import logging
import sqlite3
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import tempfile
import shutil

# Import the base validator
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent / "scripts" / "conan"))
from database_schema_validator import DatabaseSchemaValidator

logger = logging.getLogger(__name__)

class OpenSSLSchemaValidator(DatabaseSchemaValidator):
    """OpenSSL-specific database schema validator with package tracking"""

    def __init__(self, project_root: Path):
        super().__init__(project_root)

        # OpenSSL-specific paths
        self.openssl_config_dir = project_root / "openssl-config"
        self.package_cache_db = project_root / "conan-dev" / "package-cache.db"
        self.build_stages_db = project_root / "conan-dev" / "build-stages.db"

        # Create OpenSSL-specific directories
        self.openssl_config_dir.mkdir(parents=True, exist_ok=True)

        # OpenSSL configuration schema
        self.openssl_schema = {
            "build_configurations": {
                "table_name": "build_configurations",
                "columns": {
                    "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
                    "config_name": "TEXT NOT NULL UNIQUE",
                    "openssl_version": "TEXT NOT NULL",
                    "fips_enabled": "BOOLEAN DEFAULT FALSE",
                    "enable_quic": "BOOLEAN DEFAULT FALSE",
                    "enable_ktls": "BOOLEAN DEFAULT FALSE",
                    "enable_zlib": "BOOLEAN DEFAULT FALSE",
                    "enable_zstd": "BOOLEAN DEFAULT FALSE",
                    "enable_sctp": "BOOLEAN DEFAULT FALSE",
                    "enable_asan": "BOOLEAN DEFAULT FALSE",
                    "enable_ubsan": "BOOLEAN DEFAULT FALSE",
                    "enable_msan": "BOOLEAN DEFAULT FALSE",
                    "enable_tsan": "BOOLEAN DEFAULT FALSE",
                    "no_bulk": "BOOLEAN DEFAULT FALSE",
                    "no_asm": "BOOLEAN DEFAULT FALSE",
                    "no_deprecated": "BOOLEAN DEFAULT FALSE",
                    "no_legacy": "BOOLEAN DEFAULT FALSE",
                    "shared": "BOOLEAN DEFAULT TRUE",
                    "deployment_target": "TEXT DEFAULT 'general'",
                    "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                    "updated_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
                }
            },
            "package_cache": {
                "table_name": "package_cache",
                "columns": {
                    "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
                    "package_name": "TEXT NOT NULL",
                    "package_version": "TEXT NOT NULL",
                    "package_user": "TEXT NOT NULL",
                    "package_channel": "TEXT NOT NULL",
                    "package_id": "TEXT NOT NULL",
                    "build_stage": "TEXT NOT NULL",  # foundation, tooling, domain, orchestration
                    "config_hash": "TEXT NOT NULL",
                    "file_count": "INTEGER DEFAULT 0",
                    "total_size": "INTEGER DEFAULT 0",
                    "cache_path": "TEXT NOT NULL",
                    "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                    "validated_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                    "validation_status": "TEXT DEFAULT 'pending'",  # pending, validated, failed
                    "validation_errors": "TEXT DEFAULT NULL"
                }
            },
            "build_stages": {
                "table_name": "build_stages",
                "columns": {
                    "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
                    "stage_name": "TEXT NOT NULL",  # foundation, tooling, domain, orchestration
                    "package_name": "TEXT NOT NULL",
                    "package_version": "TEXT NOT NULL",
                    "build_config_id": "INTEGER NOT NULL",
                    "start_time": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                    "end_time": "TIMESTAMP DEFAULT NULL",
                    "status": "TEXT DEFAULT 'running'",  # running, completed, failed
                    "build_log": "TEXT DEFAULT NULL",
                    "artifacts": "TEXT DEFAULT NULL",  # JSON list of artifacts
                    "dependencies": "TEXT DEFAULT NULL"  # JSON list of dependencies
                },
                "foreign_keys": [
                    "FOREIGN KEY (build_config_id) REFERENCES build_configurations(id)"
                ]
            },
            "validation_results": {
                "table_name": "validation_results",
                "columns": {
                    "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
                    "package_cache_id": "INTEGER NOT NULL",
                    "validation_type": "TEXT NOT NULL",  # schema, integrity, security, compliance
                    "validation_status": "TEXT NOT NULL",  # passed, failed, warning
                    "validation_details": "TEXT DEFAULT NULL",  # JSON details
                    "validated_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
                },
                "foreign_keys": [
                    "FOREIGN KEY (package_cache_id) REFERENCES package_cache(id)"
                ]
            }
        }

    def setup_openssl_databases(self):
        """Set up OpenSSL-specific databases with schema validation"""
        logger.info("🗄️ Setting up OpenSSL databases...")

        # Create build configurations database first (needed for foreign keys)
        build_config_db = self.project_root / "conan-dev" / "build-configurations.db"
        self._create_database_with_schema(build_config_db, "build_configurations")

        # Create package cache database
        self._create_database_with_schema(self.package_cache_db, "package_cache")

        # Create build stages database
        self._create_database_with_schema(self.build_stages_db, "build_stages")

        # Create validation results database
        validation_db = self.project_root / "conan-dev" / "validation-results.db"
        self._create_database_with_schema(validation_db, "validation_results")

        logger.info("✅ OpenSSL databases created successfully")

    def _create_database_with_schema(self, db_path: Path, schema_name: str):
        """Create database with OpenSSL schema"""
        try:
            # Remove existing database
            if db_path.exists():
                db_path.unlink()

            # Create new database
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            # Get schema definition
            schema_def = self.openssl_schema[schema_name]
            table_name = schema_def["table_name"]
            columns = schema_def["columns"]

            # Build CREATE TABLE statement
            column_defs = []
            for col_name, col_type in columns.items():
                column_defs.append(f"{col_name} {col_type}")

            # Add foreign keys if they exist
            foreign_keys = schema_def.get("foreign_keys", [])
            all_defs = column_defs + foreign_keys

            create_sql = f"CREATE TABLE {table_name} ({', '.join(all_defs)})"
            cursor.execute(create_sql)

            # Create indexes for better performance
            if schema_name == "package_cache":
                cursor.execute("CREATE INDEX idx_package_cache_name_version ON package_cache(package_name, package_version)")
                cursor.execute("CREATE INDEX idx_package_cache_build_stage ON package_cache(build_stage)")
                cursor.execute("CREATE INDEX idx_package_cache_validation_status ON package_cache(validation_status)")

            elif schema_name == "build_stages":
                cursor.execute("CREATE INDEX idx_build_stages_stage_name ON build_stages(stage_name)")
                cursor.execute("CREATE INDEX idx_build_stages_status ON build_stages(status)")
                cursor.execute("CREATE INDEX idx_build_stages_package ON build_stages(package_name, package_version)")

            elif schema_name == "validation_results":
                cursor.execute("CREATE INDEX idx_validation_results_package ON validation_results(package_cache_id)")
                cursor.execute("CREATE INDEX idx_validation_results_type ON validation_results(validation_type)")
                cursor.execute("CREATE INDEX idx_validation_results_status ON validation_results(validation_status)")

            conn.commit()
            conn.close()

            logger.info(f"✅ Database created: {db_path}")

        except Exception as e:
            logger.error(f"❌ Failed to create database {db_path}: {e}")
            raise

    def validate_openssl_configuration(self, config_data: Dict) -> Dict:
        """Validate OpenSSL configuration against schema"""
        logger.info("🔍 Validating OpenSSL configuration...")

        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "config_hash": ""
        }

        try:
            # Validate required fields
            required_fields = ["config_name", "openssl_version"]
            for field in required_fields:
                if field not in config_data:
                    validation_result["errors"].append(f"Missing required field: {field}")
                    validation_result["valid"] = False

            # Validate OpenSSL version format
            if "openssl_version" in config_data:
                version = config_data["openssl_version"]
                if not self._validate_version_format(version):
                    validation_result["errors"].append(f"Invalid version format: {version}")
                    validation_result["valid"] = False

            # Validate boolean fields
            boolean_fields = [
                "fips_enabled", "enable_quic", "enable_ktls", "enable_zlib",
                "enable_zstd", "enable_sctp", "enable_asan", "enable_ubsan",
                "enable_msan", "enable_tsan", "no_bulk", "no_asm",
                "no_deprecated", "no_legacy", "shared"
            ]

            for field in boolean_fields:
                if field in config_data and not isinstance(config_data[field], bool):
                    validation_result["warnings"].append(f"Field {field} should be boolean")

            # Validate deployment target
            if "deployment_target" in config_data:
                valid_targets = ["general", "fips-government", "embedded", "development"]
                if config_data["deployment_target"] not in valid_targets:
                    validation_result["errors"].append(f"Invalid deployment target: {config_data['deployment_target']}")
                    validation_result["valid"] = False

            # Generate configuration hash
            config_hash = self._generate_config_hash(config_data)
            validation_result["config_hash"] = config_hash

            # Store configuration in database
            if validation_result["valid"]:
                self._store_build_configuration(config_data, config_hash)

        except Exception as e:
            logger.error(f"❌ Configuration validation failed: {e}")
            validation_result["valid"] = False
            validation_result["errors"].append(str(e))

        return validation_result

    def _validate_version_format(self, version: str) -> bool:
        """Validate OpenSSL version format"""
        import re
        # Accept formats like: 3.4.1, 3.4.1-dev, 3.4.1-alpha1, etc.
        pattern = r'^\d+\.\d+\.\d+(-[a-zA-Z0-9]+)*$'
        return bool(re.match(pattern, version))

    def _generate_config_hash(self, config_data: Dict) -> str:
        """Generate hash for configuration"""
        # Sort keys for consistent hashing
        sorted_config = json.dumps(config_data, sort_keys=True)
        return hashlib.sha256(sorted_config.encode()).hexdigest()[:16]

    def _store_build_configuration(self, config_data: Dict, config_hash: str):
        """Store build configuration in database"""
        try:
            build_config_db = self.project_root / "conan-dev" / "build-configurations.db"
            conn = sqlite3.connect(str(build_config_db))
            cursor = conn.cursor()

            # Insert or update configuration
            cursor.execute("""
                INSERT OR REPLACE INTO build_configurations
                (config_name, openssl_version, fips_enabled, enable_quic, enable_ktls,
                 enable_zlib, enable_zstd, enable_sctp, enable_asan, enable_ubsan,
                 enable_msan, enable_tsan, no_bulk, no_asm, no_deprecated, no_legacy,
                 shared, deployment_target, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                config_data.get("config_name"),
                config_data.get("openssl_version"),
                config_data.get("fips_enabled", False),
                config_data.get("enable_quic", False),
                config_data.get("enable_ktls", False),
                config_data.get("enable_zlib", False),
                config_data.get("enable_zstd", False),
                config_data.get("enable_sctp", False),
                config_data.get("enable_asan", False),
                config_data.get("enable_ubsan", False),
                config_data.get("enable_msan", False),
                config_data.get("enable_tsan", False),
                config_data.get("no_bulk", False),
                config_data.get("no_asm", False),
                config_data.get("no_deprecated", False),
                config_data.get("no_legacy", False),
                config_data.get("shared", True),
                config_data.get("deployment_target", "general")
            ))

            conn.commit()
            conn.close()

            logger.info(f"✅ Build configuration stored: {config_data.get('config_name')}")

        except Exception as e:
            logger.error(f"❌ Failed to store build configuration: {e}")
            raise

    def track_package_in_cache(self, package_info: Dict, build_stage: str) -> bool:
        """Track package in cache with database validation"""
        logger.info(f"📦 Tracking package in cache: {package_info.get('name')} (stage: {build_stage})")

        try:
            # Get package details
            package_name = package_info.get("name", "unknown")
            package_version = package_info.get("version", "unknown")
            package_user = package_info.get("user", "unknown")
            package_channel = package_info.get("channel", "unknown")
            package_id = package_info.get("package_id", "unknown")

            # Get cache path
            cache_path = self._get_conan_cache_path(package_name, package_version, package_user, package_channel, package_id)

            # Calculate package metrics
            file_count, total_size = self._calculate_package_metrics(cache_path)

            # Generate config hash
            config_hash = self._generate_config_hash(package_info.get("config", {}))

            # Store in database
            conn = sqlite3.connect(str(self.package_cache_db))
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO package_cache
                (package_name, package_version, package_user, package_channel, package_id,
                 build_stage, config_hash, file_count, total_size, cache_path, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                package_name, package_version, package_user, package_channel, package_id,
                build_stage, config_hash, file_count, total_size, str(cache_path)
            ))

            package_cache_id = cursor.lastrowid
            conn.commit()
            conn.close()

            # Validate package
            validation_result = self._validate_package_integrity(cache_path, package_info)
            self._store_validation_result(package_cache_id, "integrity", validation_result)

            logger.info(f"✅ Package tracked in cache: {package_name}/{package_version}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to track package in cache: {e}")
            return False

    def _get_conan_cache_path(self, name: str, version: str, user: str, channel: str, package_id: str) -> Path:
        """Get Conan cache path for package"""
        # Use test environment cache if available, otherwise use real Conan cache
        test_cache_root = self.project_root / "test-cache"
        if test_cache_root.exists():
            package_path = test_cache_root / f"{name}-{version}-{user}-{channel}-{package_id}"
        else:
            # Conan 2.x cache structure
            cache_root = Path.home() / ".conan2" / "p"
            package_path = cache_root / f"{name}-{version}-{user}-{channel}-{package_id}"
        return package_path

    def _calculate_package_metrics(self, package_path: Path) -> Tuple[int, int]:
        """Calculate package file count and total size"""
        if not package_path.exists():
            return 0, 0

        file_count = 0
        total_size = 0

        try:
            for item in package_path.rglob("*"):
                if item.is_file():
                    file_count += 1
                    total_size += item.stat().st_size
        except Exception as e:
            logger.warning(f"Failed to calculate metrics for {package_path}: {e}")

        return file_count, total_size

    def _validate_package_integrity(self, package_path: Path, package_info: Dict) -> Dict:
        """Validate package integrity"""
        validation_result = {
            "status": "passed",
            "errors": [],
            "warnings": [],
            "details": {}
        }

        try:
            if not package_path.exists():
                validation_result["status"] = "failed"
                validation_result["errors"].append("Package path does not exist")
                return validation_result

            # Check for required files
            required_files = ["conaninfo.txt", "conanmanifest.txt"]
            for required_file in required_files:
                if not (package_path / required_file).exists():
                    validation_result["warnings"].append(f"Missing {required_file}")

            # Validate manifest
            manifest_path = package_path / "conanmanifest.txt"
            if manifest_path.exists():
                manifest_validation = self._validate_conan_manifest(manifest_path)
                validation_result["details"]["manifest"] = manifest_validation

            # Check for OpenSSL-specific files
            openssl_files = ["libssl.so", "libcrypto.so", "openssl", "openssl.exe"]
            found_openssl_files = []
            for file_pattern in openssl_files:
                found_files = list(package_path.rglob(file_pattern))
                found_openssl_files.extend(found_files)

            validation_result["details"]["openssl_files"] = [str(f) for f in found_openssl_files]

            if not found_openssl_files:
                validation_result["warnings"].append("No OpenSSL files found in package")

        except Exception as e:
            validation_result["status"] = "failed"
            validation_result["errors"].append(str(e))

        return validation_result

    def _validate_conan_manifest(self, manifest_path: Path) -> Dict:
        """Validate Conan manifest file"""
        manifest_info = {
            "valid": True,
            "file_count": 0,
            "total_size": 0,
            "errors": []
        }

        try:
            with open(manifest_path, 'r') as f:
                lines = f.readlines()

            for line in lines:
                if line.strip():
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        try:
                            file_size = int(parts[0])
                            manifest_info["file_count"] += 1
                            manifest_info["total_size"] += file_size
                        except ValueError:
                            manifest_info["errors"].append(f"Invalid size format: {parts[0]}")
                            manifest_info["valid"] = False

        except Exception as e:
            manifest_info["valid"] = False
            manifest_info["errors"].append(str(e))

        return manifest_info

    def _store_validation_result(self, package_cache_id: int, validation_type: str, result: Dict):
        """Store validation result in database"""
        try:
            conn = sqlite3.connect(str(self.project_root / "conan-dev" / "validation-results.db"))
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO validation_results
                (package_cache_id, validation_type, validation_status, validation_details, validated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                package_cache_id, validation_type, result["status"],
                json.dumps(result)
            ))

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"❌ Failed to store validation result: {e}")

    def get_package_cache_summary(self) -> Dict:
        """Get summary of package cache with validation status"""
        try:
            conn = sqlite3.connect(str(self.package_cache_db))
            cursor = conn.cursor()

            # Get overall statistics
            cursor.execute("SELECT COUNT(*) FROM package_cache")
            total_packages = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM package_cache WHERE validation_status = 'validated'")
            validated_packages = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM package_cache WHERE validation_status = 'failed'")
            failed_packages = cursor.fetchone()[0]

            # Get statistics by build stage
            cursor.execute("""
                SELECT build_stage, COUNT(*) as count,
                       SUM(file_count) as total_files,
                       SUM(total_size) as total_size
                FROM package_cache
                GROUP BY build_stage
            """)
            stage_stats = cursor.fetchall()

            conn.close()

            return {
                "total_packages": total_packages,
                "validated_packages": validated_packages,
                "failed_packages": failed_packages,
                "pending_packages": total_packages - validated_packages - failed_packages,
                "stage_statistics": [
                    {
                        "stage": row[0],
                        "count": row[1],
                        "total_files": row[2],
                        "total_size": row[3]
                    }
                    for row in stage_stats
                ]
            }

        except Exception as e:
            logger.error(f"❌ Failed to get package cache summary: {e}")
            return {}

    def generate_cache_report(self) -> str:
        """Generate comprehensive cache report"""
        logger.info("📊 Generating cache report...")

        try:
            summary = self.get_package_cache_summary()

            report = f"""# OpenSSL Package Cache Report

**Generated:** {datetime.now().isoformat()}

## Summary

- **Total Packages:** {summary.get('total_packages', 0)}
- **Validated Packages:** {summary.get('validated_packages', 0)}
- **Failed Packages:** {summary.get('failed_packages', 0)}
- **Pending Packages:** {summary.get('pending_packages', 0)}

## Build Stage Statistics

"""

            for stage_stat in summary.get('stage_statistics', []):
                report += f"""### {stage_stat['stage'].title()} Stage
- **Package Count:** {stage_stat['count']}
- **Total Files:** {stage_stat['total_files']}
- **Total Size:** {stage_stat['total_size']:,} bytes

"""

            # Save report
            report_path = self.reports_dir / f"cache-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
            with open(report_path, 'w') as f:
                f.write(report)

            logger.info(f"✅ Cache report generated: {report_path}")
            return str(report_path)

        except Exception as e:
            logger.error(f"❌ Failed to generate cache report: {e}")
            return ""

def main():
    """Main entry point for OpenSSL schema validation"""
    import argparse

    parser = argparse.ArgumentParser(description="OpenSSL Database Schema Validation")
    parser.add_argument("--project-root", type=Path, default=Path.cwd(),
                       help="Project root directory")
    parser.add_argument("--action", choices=["setup", "validate-config", "track-package", "generate-report"],
                       required=True, help="Action to perform")
    parser.add_argument("--config-file", type=Path, help="Configuration file path")
    parser.add_argument("--package-info", type=str, help="Package info JSON string")
    parser.add_argument("--build-stage", choices=["foundation", "tooling", "domain", "orchestration"],
                       help="Build stage for package tracking")

    args = parser.parse_args()

    validator = OpenSSLSchemaValidator(args.project_root)

    if args.action == "setup":
        validator.setup_openssl_databases()
    elif args.action == "validate-config":
        if args.config_file:
            with open(args.config_file, 'r') as f:
                config_data = json.load(f)
            result = validator.validate_openssl_configuration(config_data)
            print(json.dumps(result, indent=2))
        else:
            logger.error("--config-file argument required for validate-config action")
    elif args.action == "track-package":
        if args.package_info and args.build_stage:
            package_info = json.loads(args.package_info)
            success = validator.track_package_in_cache(package_info, args.build_stage)
            print(f"Package tracking {'successful' if success else 'failed'}")
        else:
            logger.error("--package-info and --build-stage arguments required for track-package action")
    elif args.action == "generate-report":
        report_path = validator.generate_cache_report()
        print(f"Report generated: {report_path}")

if __name__ == "__main__":
    main()
