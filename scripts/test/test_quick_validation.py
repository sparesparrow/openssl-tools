#!/usr/bin/env python3
"""
Quick validation test for OpenSSL database schema validation
"""

import sys
from pathlib import Path

# Add the openssl_tools module to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from openssl_tools.database.openssl_schema_validator import OpenSSLSchemaValidator

def quick_test():
    """Run a quick validation test"""
    print("🧪 Quick OpenSSL Database Validation Test")
    print("=" * 50)
    
    # Initialize validator
    project_root = Path(__file__).parent.parent.parent
    validator = OpenSSLSchemaValidator(project_root)
    
    # Test configuration validation
    test_config = {
        "config_name": "quick-test",
        "openssl_version": "3.4.1",
        "fips_enabled": False,
        "shared": True,
        "deployment_target": "general"
    }
    
    print("🔍 Testing configuration validation...")
    result = validator.validate_openssl_configuration(test_config)
    
    if result["valid"]:
        print(f"✅ Configuration valid (hash: {result['config_hash']})")
    else:
        print(f"❌ Configuration invalid: {result['errors']}")
        return False
    
    # Test cache summary
    print("📊 Testing cache summary...")
    summary = validator.get_package_cache_summary()
    print(f"Total packages: {summary.get('total_packages', 0)}")
    
    print("🎉 Quick test completed successfully!")
    return True

if __name__ == "__main__":
    success = quick_test()
    sys.exit(0 if success else 1)
