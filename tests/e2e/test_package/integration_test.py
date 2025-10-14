#!/usr/bin/env python3
"""
Integration test for openssl-tools
"""

import sys
import os

# Add the package to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

try:
    import openssl_tools
    print(f"OpenSSL Tools version: {openssl_tools.__version__}")
    
    # Test imports
    from openssl_tools import review_tools, release_tools, statistics
    print("All modules imported successfully")
    
    # Test environment variables
    openssl_tools_root = os.environ.get("OPENSSL_TOOLS_ROOT")
    if openssl_tools_root:
        print(f"OpenSSL Tools Root: {openssl_tools_root}")
    else:
        print("Warning: OPENSSL_TOOLS_ROOT not set")
    
    print("Integration test passed!")
    
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Test error: {e}")
    sys.exit(1)
