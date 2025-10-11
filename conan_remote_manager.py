#!/usr/bin/env python3
"""
Backward compatibility wrapper for ConanRemoteManager.
This file provides backward compatibility for existing scripts that import from the root level.
"""

import sys
from openssl_tools.development.package_management.remote_manager import (
    ConanRemoteManager, main
)

if __name__ == "__main__":
    sys.exit(main())