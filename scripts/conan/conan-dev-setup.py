#!/usr/bin/env python3
"""
Conan Development Setup - Cross-platform environment setup
Replaces the bash conan-dev-setup script
"""

import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from conan_cli import ConanCLI

def main():
    """Main entry point for conan-dev-setup"""
    cli = ConanCLI()
    
    # Parse arguments (simple version for backward compatibility)
    force = False
    
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ["-f", "--force"]:
            force = True
        elif arg in ["-h", "--help"]:
            print("Usage: conan-dev-setup [OPTIONS]")
            print("Options:")
            print("  -f, --force           Force setup (recreate environment)")
            print("  -h, --help           Show this help")
            print()
            print("This script sets up a complete Conan development environment")
            print("with Python virtual environment and cross-platform support.")
            return
        else:
            print(f"Unknown option: {arg}")
            print("Use --help for usage information")
            sys.exit(1)
        i += 1
    
    # Check if we're in the right directory
    if not (Path.cwd() / "conanfile.py").exists():
        print("❌ conanfile.py not found. Please run this script from the project root.")
        sys.exit(1)
    
    # Execute setup
    cli.setup(force=force)

if __name__ == "__main__":
    main()