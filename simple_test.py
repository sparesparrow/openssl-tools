#!/usr/bin/env python3
"""
Simple test script to verify OpenSSL Tools integration
"""

import sys
import os

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

def main():
    """Run all tests"""
    print("OpenSSL Tools Simple Test")
    print("=" * 30)
    
    tests = [
        test_imports,
        test_config_manager,
        test_tools_initialization
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