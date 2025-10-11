#!/usr/bin/env python3
"""
Backward compatibility wrapper for Fuzz Integration.
This file provides backward compatibility for existing scripts that import from the root level.
"""

import sys
from openssl_tools.testing.fuzz_manager import FuzzIntegration, main

if __name__ == "__main__":
    sys.exit(main())