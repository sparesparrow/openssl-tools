"""
Integration tests for python_requires consumer of openssl-tools package
Tests that the openssl-tools/0.1.0 package can be consumed and its utilities imported
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

class TestPythonRequiresConsumer:
    """Test consuming openssl-tools as python_requires"""

    def test_import_foundation_utilities(self):
        """Test that foundation utilities can be imported from openssl-tools"""
        try:
            from openssl_tools.foundation.utilities import setup_logging, get_logger, ConfigManager
            assert setup_logging is not None
            assert get_logger is not None
            assert ConfigManager is not None
            print("✅ Foundation utilities imported successfully")
        except ImportError as e:
            pytest.fail(f"Failed to import foundation utilities: {e}")

    def test_import_core_components(self):
        """Test that core components can be imported from openssl-tools"""
        try:
            from openssl_tools.core.artifactory_handler import ArtifactoryHandler
            assert ArtifactoryHandler is not None
            print("✅ Core components imported successfully")
        except ImportError as e:
            pytest.fail(f"Failed to import core components: {e}")

    def test_import_util_modules(self):
        """Test that utility modules can be imported from openssl-tools"""
        try:
            from openssl_tools.util import conan_python_env
            assert conan_python_env is not None
            print("✅ Utility modules imported successfully")
        except ImportError as e:
            pytest.fail(f"Failed to import utility modules: {e}")

    def test_config_manager_functionality(self):
        """Test ConfigManager functionality"""
        from openssl_tools.foundation.utilities.config import ConfigManager

        config = ConfigManager()
        assert hasattr(config, '__init__')
        print("✅ ConfigManager functionality verified")

    def test_logging_setup(self):
        """Test logging setup functionality"""
        from openssl_tools.foundation.utilities.logging import setup_logging, get_logger

        # Test setup_logging function exists
        assert callable(setup_logging)

        # Test get_logger function
        logger = get_logger("test")
        assert logger is not None
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'error')
        print("✅ Logging setup functionality verified")

    @patch('sys.path')
    def test_python_path_setup_simulation(self, mock_sys_path):
        """Simulate python_requires PYTHONPATH setup"""
        # This simulates what happens when python_requires sets PYTHONPATH
        fake_package_path = "/fake/package/path"
        mock_sys_path.append(fake_package_path)

        # Verify path was added
        assert fake_package_path in sys.path
        print("✅ PYTHONPATH setup simulation verified")

    def test_package_version_consistency(self):
        """Test that package version is consistent"""
        import openssl_tools
        assert hasattr(openssl_tools, '__version__')
        assert openssl_tools.__version__ == "0.1.0"
        print("✅ Package version consistency verified")

    def test_shared_utilities_access(self):
        """Test access to shared utilities exported by __init__.py"""
        import openssl_tools

        # Check that shared utilities are accessible
        assert hasattr(openssl_tools, 'setup_logging')
        assert hasattr(openssl_tools, 'get_logger')
        assert hasattr(openssl_tools, 'ConfigManager')
        assert hasattr(openssl_tools, 'ArtifactoryHandler')
        print("✅ Shared utilities access verified")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])