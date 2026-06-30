#!/usr/bin/env python3
"""
OpenSSL Tools - Main Entry Point
Provides command-line interface for OpenSSL development tools
"""

import sys
import argparse
from pathlib import Path

# Add the package root to the path
package_root = Path(__file__).parent.parent
sys.path.insert(0, str(package_root))

from openssl_tools.foundation.command_line.main import main as cli_main

if __name__ == "__main__":
    cli_main()