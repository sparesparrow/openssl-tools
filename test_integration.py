#!/usr/bin/env python3
"""
Test script to verify OpenSSL Tools integration
"""

import sys
import os
import subprocess
import tempfile
import shutil
from pathlib import Path

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        from openssl_tools.review_tools import AddRevTool, GitAddRevTool, CherryCheckerTool
        from openssl_tools.release_tools import StageReleaseTool, CopyrightYearTool
        from openssl_tools.statistics import BnRandRangeTool
        from openssl_tools.utils import ConfigManager
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

def test_config_manager():
    """Test configuration manager"""
    print("Testing configuration manager...")
    
    try:
        from openssl_tools.utils import ConfigManager
        
        # Test with default config
        config = ConfigManager()
        assert config.get('tools.review_tools.min_reviewers') == 2
        assert config.get('tools.release_tools.enabled') == True
        print("✓ Configuration manager working")
        return True
    except Exception as e:
        print(f"✗ Configuration manager failed: {e}")
        return False

def test_tools_initialization():
    """Test that tools can be initialized"""
    print("Testing tool initialization...")
    
    try:
        from openssl_tools.review_tools import AddRevTool, GitAddRevTool, CherryCheckerTool
        from openssl_tools.release_tools import StageReleaseTool, CopyrightYearTool
        from openssl_tools.statistics import BnRandRangeTool
        
        # Test tool initialization
        addrev = AddRevTool()
        gitaddrev = GitAddRevTool()
        cherry_checker = CherryCheckerTool()
        stage = StageReleaseTool()
        copyright_year = CopyrightYearTool()
        bn_rand = BnRandRangeTool()
        
        print("✓ All tools initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Tool initialization failed: {e}")
        return False

def test_command_line_tools():
    """Test command line tools"""
    print("Testing command line tools...")
    
    try:
        # Test help for each tool using the virtual environment
        tools = [
            'addrev --help',
            'gitaddrev --help',
            'cherry-checker --help',
            'stage-release --help',
            'copyright-year --help',
            'bn-rand-range --help'
        ]
        
        for tool_cmd in tools:
            # Use the virtual environment python
            result = subprocess.run(['python', '-m', 'openssl_tools.review_tools.' + tool_cmd.split()[0]], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print(f"✗ {tool_cmd} failed: {result.stderr}")
                return False
        
        print("✓ All command line tools working")
        return True
    except Exception as e:
        print(f"✗ Command line tools test failed: {e}")
        return False

def test_conan_integration():
    """Test Conan integration"""
    print("Testing Conan integration...")
    
    try:
        # Check if conanfile.py exists and is valid
        conanfile_path = Path('conanfile.py')
        if not conanfile_path.exists():
            print("✗ conanfile.py not found")
            return False
        
        # Try to import the conanfile
        import importlib.util
        spec = importlib.util.spec_from_file_location("conanfile", conanfile_path)
        conanfile = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(conanfile)
        
        # Check if OpenSSLToolsConan class exists
        if hasattr(conanfile, 'OpenSSLToolsConan'):
            print("✓ Conan integration working")
            return True
        else:
            print("✗ OpenSSLToolsConan class not found")
            return False
            
    except Exception as e:
        print(f"✗ Conan integration test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("OpenSSL Tools Integration Test")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_config_manager,
        test_tools_initialization,
        test_command_line_tools,
        test_conan_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed!")
        return 1

if __name__ == '__main__':
    sys.exit(main())