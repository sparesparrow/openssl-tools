#!/usr/bin/env python3
"""
Backward compatibility wrapper for Python Environment Setup.
This file provides backward compatibility for existing scripts that import from the root level.
"""

import sys
from openssl_tools.automation.deployment.python_env_setup import main

if __name__ == "__main__":
    sys.exit(main())