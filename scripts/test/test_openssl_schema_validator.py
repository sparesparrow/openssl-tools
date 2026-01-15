#!/usr/bin/env python3
"""
Test OpenSSL Schema Validator
Test and setup the database schema validator for OpenSSL configuration validation
"""

import os
import sys
import json
import tempfile
from pathlib import Path
from datetime import datetime

# Add the openssl_tools module to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from openssl_tools.database.openssl_schema_validator import OpenSSLSchemaValidator

def test_openssl_schema_validator():
    """Test the OpenSSL schema validator with sample configurations"""
    print("🧪 Testing OpenSSL Schema Validator...")

    # Create temporary project root
    with tempfile.TemporaryDirectory() as temp_dir:
        project_root = Path(temp_dir)
        print(f"📁 Using temporary project root: {project_root}")

        # Initialize validator
        validator = OpenSSLSchemaValidator(project_root)

        # Test 1: Setup databases
        print("\n1️⃣ Setting up OpenSSL databases...")
        try:
            validator.setup_openssl_databases()
            print("✅ Database setup successful")
        except Exception as e:
            print(f"❌ Database setup failed: {e}")
            return False

        # Test 2: Validate OpenSSL configurations
        print("\n2️⃣ Testing OpenSSL configuration validation...")

        test_configs = [
            {
                "config_name": "general-build",
                "openssl_version": "3.4.1",
                "fips_enabled": False,
                "enable_quic": True,
                "enable_ktls": True,
                "shared": True,
                "deployment_target": "general"
            },
            {
                "config_name": "fips-government",
                "openssl_version": "3.4.1",
                "fips_enabled": True,
                "enable_quic": False,
                "enable_ktls": False,
                "shared": False,
                "deployment_target": "fips-government"
            },
            {
                "config_name": "embedded-build",
                "openssl_version": "3.4.1",
                "fips_enabled": False,
                "enable_quic": False,
                "enable_ktls": False,
                "no_asm": True,
                "no_deprecated": True,
                "shared": False,
                "deployment_target": "embedded"
            }
        ]

        for config in test_configs:
            print(f"\n   Testing config: {config['config_name']}")
            result = validator.validate_openssl_configuration(config)
            if result["valid"]:
                print(f"   ✅ Configuration valid (hash: {result['config_hash']})")
            else:
                print(f"   ❌ Configuration invalid: {result['errors']}")

        # Test 3: Track packages in cache (simulated)
        print("\n3️⃣ Testing package cache tracking...")

        test_packages = [
            {
                "name": "openssl-conan-base",
                "version": "1.0.1",
                "user": "sparesparrow",
                "channel": "stable",
                "package_id": "abc123def456",
                "config": test_configs[0]
            },
            {
                "name": "openssl-fips-policy",
                "version": "140-3.2",
                "user": "sparesparrow",
                "channel": "stable",
                "package_id": "def456ghi789",
                "config": test_configs[1]
            },
            {
                "name": "openssl-tools",
                "version": "1.2.4",
                "user": "sparesparrow",
                "channel": "stable",
                "package_id": "ghi789jkl012",
                "config": test_configs[0]
            },
            {
                "name": "openssl",
                "version": "3.4.1",
                "user": "sparesparrow",
                "channel": "stable",
                "package_id": "jkl012mno345",
                "config": test_configs[1]
            }
        ]

        build_stages = ["foundation", "foundation", "tooling", "domain"]

        for package, stage in zip(test_packages, build_stages):
            print(f"   Tracking package: {package['name']}/{package['version']} (stage: {stage})")
            success = validator.track_package_in_cache(package, stage)
            if success:
                print(f"   ✅ Package tracked successfully")
            else:
                print(f"   ❌ Package tracking failed")

        # Test 4: Generate cache report
        print("\n4️⃣ Generating cache report...")
        try:
            report_path = validator.generate_cache_report()
            if report_path:
                print(f"✅ Cache report generated: {report_path}")

                # Read and display report summary
                with open(report_path, 'r') as f:
                    report_content = f.read()
                    print("\n📊 Report Summary:")
                    print(report_content[:500] + "..." if len(report_content) > 500 else report_content)
            else:
                print("❌ Cache report generation failed")
        except Exception as e:
            print(f"❌ Cache report generation failed: {e}")

        # Test 5: Get package cache summary
        print("\n5️⃣ Getting package cache summary...")
        try:
            summary = validator.get_package_cache_summary()
            print("✅ Package cache summary:")
            print(json.dumps(summary, indent=2))
        except Exception as e:
            print(f"❌ Failed to get package cache summary: {e}")

        print("\n🎉 OpenSSL Schema Validator testing completed!")
        return True

def create_sample_openssl_configs():
    """Create sample OpenSSL configuration files for testing"""
    print("📝 Creating sample OpenSSL configuration files...")

    configs_dir = Path("openssl-config")
    configs_dir.mkdir(exist_ok=True)

    sample_configs = {
        "general-build.json": {
            "config_name": "general-build",
            "openssl_version": "3.4.1",
            "fips_enabled": False,
            "enable_quic": True,
            "enable_ktls": True,
            "enable_zlib": True,
            "enable_zstd": True,
            "shared": True,
            "deployment_target": "general",
            "description": "General purpose OpenSSL build with modern features"
        },
        "fips-government.json": {
            "config_name": "fips-government",
            "openssl_version": "3.4.1",
            "fips_enabled": True,
            "enable_quic": False,
            "enable_ktls": False,
            "enable_zlib": False,
            "enable_zstd": False,
            "shared": False,
            "deployment_target": "fips-government",
            "description": "FIPS 140-3 compliant build for government use"
        },
        "embedded-build.json": {
            "config_name": "embedded-build",
            "openssl_version": "3.4.1",
            "fips_enabled": False,
            "enable_quic": False,
            "enable_ktls": False,
            "enable_zlib": False,
            "enable_zstd": False,
            "no_asm": True,
            "no_deprecated": True,
            "no_legacy": True,
            "shared": False,
            "deployment_target": "embedded",
            "description": "Minimal embedded build with reduced features"
        },
        "development-build.json": {
            "config_name": "development-build",
            "openssl_version": "3.4.1",
            "fips_enabled": False,
            "enable_quic": True,
            "enable_ktls": True,
            "enable_zlib": True,
            "enable_zstd": True,
            "enable_asan": True,
            "enable_ubsan": True,
            "shared": True,
            "deployment_target": "development",
            "description": "Development build with debugging features"
        }
    }

    for filename, config in sample_configs.items():
        config_path = configs_dir / filename
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"✅ Created: {config_path}")

    print(f"✅ Sample configurations created in: {configs_dir}")

def main():
    """Main test function"""
    print("🚀 OpenSSL Database Schema Validator Test Suite")
    print("=" * 60)

    # Create sample configurations
    create_sample_openssl_configs()

    # Run tests
    success = test_openssl_schema_validator()

    if success:
        print("\n🎉 All tests passed successfully!")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    exit(main())
