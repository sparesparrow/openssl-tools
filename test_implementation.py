#!/usr/bin/env python3
"""
Test script for openssl-tools implementation
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_config_management():
    """Test configuration management"""
    print("Testing configuration management...")
    try:
        from launcher.conan_launcher import ConfigLoaderManager, create_default_config
        
        # Create default config
        config_dir = project_root / 'conf'
        create_default_config(config_dir)
        print("✓ Default configuration created")
        
        # Test config loader
        loader = ConfigLoaderManager(config_dir)
        config = loader.get_configuration()
        print("✓ Configuration loaded successfully")
        
        return True
    except Exception as e:
        print(f"✗ Configuration management failed: {e}")
        return False

def test_build_optimizer():
    """Test build optimizer"""
    print("Testing build optimizer...")
    try:
        from build_optimizer import BuildOptimizer
        
        config = {
            'source_dir': '.',
            'build_dir': 'build',
            'max_jobs': 2,
            'enable_ccache': False,  # Disable for testing
            'enable_sccache': False,
            'optimize_build': True,
            'reproducible_builds': True
        }
        
        optimizer = BuildOptimizer(config)
        env = optimizer.optimize_build_environment()
        print("✓ Build optimizer initialized")
        
        stats = optimizer.get_build_statistics()
        print(f"✓ Build statistics: {len(stats)} metrics")
        
        return True
    except Exception as e:
        print(f"✗ Build optimizer failed: {e}")
        return False

def test_sbom_generator():
    """Test SBOM generator"""
    print("Testing SBOM generator...")
    try:
        from scripts.sbom_generator import SBOMGenerator
        
        config = {
            'enable_vulnerability_scanning': False,  # Disable for testing
            'enable_package_signing': False,
            'enable_dependency_analysis': True,
            'enable_license_analysis': True
        }
        
        generator = SBOMGenerator(config)
        
        package_info = {
            'name': 'openssl-tools',
            'version': '1.0.0',
            'description': 'OpenSSL Tools',
            'homepage': 'https://github.com/sparesparrow/openssl-tools',
            'url': 'https://github.com/sparesparrow/openssl-tools',
            'license': 'Apache-2.0',
            'package_folder': '.',
            'os': 'Linux',
            'arch': 'x86_64',
            'build_type': 'Release',
            'options': {},
            'settings': {},
            'dependencies': {}
        }
        
        sbom_data = generator.generate_sbom(package_info)
        print("✓ SBOM generated successfully")
        print(f"✓ SBOM contains {len(sbom_data.get('components', []))} components")
        
        return True
    except Exception as e:
        print(f"✗ SBOM generator failed: {e}")
        return False

def test_python_env_manager():
    """Test Python environment manager"""
    print("Testing Python environment manager...")
    try:
        from setup_python_env import PythonEnvironmentManager
        
        manager = PythonEnvironmentManager()
        available_pythons = manager.available_pythons
        print(f"✓ Found {len(available_pythons)} Python versions: {list(available_pythons.keys())}")
        
        current_python = manager.current_python
        print(f"✓ Current Python: {current_python['version']} at {current_python['path']}")
        
        return True
    except Exception as e:
        print(f"✗ Python environment manager failed: {e}")
        return False

def test_utility_modules():
    """Test utility modules"""
    print("Testing utility modules...")
    try:
        from util.file_operations import get_file_metadata, ensure_target_exists
        from util.execute_command import execute_command_safe
        from util.custom_logging import setup_console_logging
        
        # Test file operations
        test_file = project_root / 'conanfile.py'
        if test_file.exists():
            metadata = get_file_metadata(test_file)
            print(f"✓ File metadata: {metadata['size']} bytes, MD5: {metadata['MD5'][:8]}...")
        
        # Test command execution
        success, output = execute_command_safe(['python3', '--version'])
        if success:
            print(f"✓ Command execution: {output[0] if output else 'No output'}")
        
        # Test logging
        setup_console_logging('INFO')
        print("✓ Logging system initialized")
        
        return True
    except Exception as e:
        print(f"✗ Utility modules failed: {e}")
        return False

def test_conanfile():
    """Test conanfile.py compilation"""
    print("Testing conanfile.py...")
    try:
        import py_compile
        py_compile.compile('conanfile.py', doraise=True)
        print("✓ conanfile.py compiles successfully")
        return True
    except Exception as e:
        print(f"✗ conanfile.py compilation failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("OpenSSL Tools Implementation Test")
    print("=" * 60)
    
    tests = [
        test_conanfile,
        test_config_management,
        test_build_optimizer,
        test_sbom_generator,
        test_python_env_manager,
        test_utility_modules
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("🎉 All tests passed! Implementation is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)