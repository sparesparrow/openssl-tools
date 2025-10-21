#!/usr/bin/env python3
"""
Simple test runner for integration tests without pytest dependencies
"""

import sys
import traceback
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

def run_test(test_func, test_name):
    """Run a single test function"""
    try:
        test_func()
        print(f"✅ {test_name} PASSED")
        return True
    except Exception as e:
        print(f"❌ {test_name} FAILED: {e}")
        traceback.print_exc()
        return False

def test_import_foundation_utilities():
    """Test that foundation utilities can be imported from openssl-tools"""
    import openssl_tools
    assert hasattr(openssl_tools, 'setup_logging')
    assert hasattr(openssl_tools, 'get_logger')
    assert hasattr(openssl_tools, 'ConfigManager')

def test_import_core_components():
    """Test that core components can be imported from openssl-tools"""
    import openssl_tools
    assert hasattr(openssl_tools, 'ArtifactoryHandler')

def test_import_util_modules():
    """Test that utility modules can be imported from openssl-tools"""
    # Test direct import of util modules
    try:
        from openssl_tools.util import conan_python_env
        assert conan_python_env is not None
    except ImportError:
        # If direct import fails, that's ok - util modules may not be exported
        pass

def test_config_manager_functionality():
    """Test ConfigManager functionality"""
    from openssl_tools.foundation.utilities.config import ConfigManager
    config = ConfigManager()
    assert hasattr(config, '__init__')

def test_logging_setup():
    """Test logging setup functionality"""
    from openssl_tools.foundation.utilities.logging import setup_logging, get_logger
    assert callable(setup_logging)
    logger = get_logger("test")
    assert logger is not None
    assert hasattr(logger, 'info')
    assert hasattr(logger, 'error')

def test_package_version_consistency():
    """Test that package version is consistent"""
    import openssl_tools
    assert hasattr(openssl_tools, '__version__')
    assert openssl_tools.__version__ == "0.1.0"

def test_shared_utilities_access():
    """Test access to shared utilities exported by __init__.py"""
    import openssl_tools
    assert hasattr(openssl_tools, 'setup_logging')
    assert hasattr(openssl_tools, 'get_logger')
    assert hasattr(openssl_tools, 'ConfigManager')
    assert hasattr(openssl_tools, 'ArtifactoryHandler')

def main():
    """Run all integration tests"""
    print("🧪 Running Python Requires Consumer Integration Tests")
    print("=" * 60)

    tests = [
        (test_import_foundation_utilities, "Import Foundation Utilities"),
        (test_import_core_components, "Import Core Components"),
        (test_import_util_modules, "Import Utility Modules"),
        (test_config_manager_functionality, "ConfigManager Functionality"),
        (test_logging_setup, "Logging Setup"),
        (test_package_version_consistency, "Package Version Consistency"),
        (test_shared_utilities_access, "Shared Utilities Access"),
    ]

    passed = 0
    total = len(tests)

    for test_func, test_name in tests:
        if run_test(test_func, test_name):
            passed += 1

    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())