#!/usr/bin/env python3
"""
Backward compatibility wrapper for OpenSSL Conan Helper.
This file provides backward compatibility for existing scripts that import from the root level.
"""

import sys
from pathlib import Path

# Add the scripts directory to the path
sys.path.insert(0, str(Path(__file__).parent / 'scripts'))

from openssl_conan.conan.openssl_conan_example import main

if __name__ == '__main__':
    sys.exit(main())