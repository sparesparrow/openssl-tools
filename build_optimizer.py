#!/usr/bin/env python3
"""
Backward compatibility wrapper for BuildOptimizer.
This file provides backward compatibility for existing scripts that import from the root level.
"""

import sys
from openssl_tools.development.build_system.optimizer import (
    BuildOptimizer, BuildCacheManager, main
)

if __name__ == "__main__":
    sys.exit(main())