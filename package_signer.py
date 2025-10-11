#!/usr/bin/env python3
"""
Backward compatibility wrapper for Package Signer.
This file provides backward compatibility for existing scripts that import from the root level.
"""

import sys
from openssl_tools.security.key_management import PackageSigner, main

if __name__ == "__main__":
    sys.exit(main())