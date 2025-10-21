#!/usr/bin/env python3
"""
Test consumer for openssl-tools package
"""

from conan import ConanFile

class TestConsumer(ConanFile):
    name = "test_consumer"
    version = "1.0.0"

    requires = "openssl-tools/0.1.0-10-g168b04c-dirty"

    def test(self):
        """Test the openssl-tools package"""
        import sys
        import os

        # Add the package to Python path
        openssl_tools_path = self.dependencies["openssl-tools"].package_folder
        openssl_tools_module_path = os.path.join(openssl_tools_path, "openssl_tools")
        sys.path.insert(0, openssl_tools_module_path)

        # Also add the package folder to Python path
        sys.path.insert(0, openssl_tools_path)

        # Test imports
        try:
            from openssl_tools.automation.config import ConfigLoaderManager
            print("✓ ConfigLoaderManager imported successfully")
        except ImportError as e:
            print(f"✗ Failed to import ConfigLoaderManager: {e}")
            return False

        try:
            from openssl_tools.utils.build_optimizer import BuildOptimizer
            print("✓ BuildOptimizer imported successfully")
        except ImportError as e:
            print(f"✗ Failed to import BuildOptimizer: {e}")
            return False

        try:
            from openssl_tools.utils.sbom_generator import SBOMGenerator
            print("✓ SBOMGenerator imported successfully")
        except ImportError as e:
            print(f"✗ Failed to import SBOMGenerator: {e}")
            return False

        try:
            from openssl_tools.utils.python_env_manager import PythonEnvironmentManager
            print("✓ PythonEnvironmentManager imported successfully")
        except ImportError as e:
            print(f"✗ Failed to import PythonEnvironmentManager: {e}")
            return False

        # Test configuration
        try:
            config_loader = ConfigLoaderManager()
            config = config_loader.get_configuration()
            print("✓ Configuration loaded successfully")
        except Exception as e:
            print(f"✗ Failed to load configuration: {e}")
            return False

        # Test build optimizer
        try:
            config = {
                'source_dir': '.',
                'build_dir': 'build',
                'max_jobs': 2,
                'enable_ccache': False,
                'optimize_build': True
            }
            optimizer = BuildOptimizer(config)
            print("✓ BuildOptimizer initialized successfully")
        except Exception as e:
            print(f"✗ Failed to initialize BuildOptimizer: {e}")
            return False

        print("🎉 All tests passed! Package is working correctly.")
        return True
