#!/usr/bin/env python3
"""
Backward compatibility wrapper for Test Implementation.
This file provides backward compatibility for existing scripts that import from the root level.
"""

import sys
from openssl_tools.testing.test_harness import TestImplementation, main

if __name__ == "__main__":
    sys.exit(main())