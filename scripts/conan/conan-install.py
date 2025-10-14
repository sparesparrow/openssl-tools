#!/usr/bin/env python3
"""
Conan Install - Cross-platform dependency installation
Replaces the bash conan-install script
"""

import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from conan_cli import ConanCLI

def main():
    """Main entry point for conan-install"""
    cli = ConanCLI()
    
    # Parse arguments (simple version for backward compatibility)
    profile = None
    verbose = False
    clean = False
    
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ["-p", "--profile"]:
            if i + 1 < len(args):
                profile = args[i + 1]
                i += 1
        elif arg in ["-v", "--verbose"]:
            verbose = True
        elif arg in ["-c", "--clean"]:
            clean = True
        elif arg in ["-h", "--help"]:
            print("Usage: conan-install [OPTIONS]")
            print("Options:")
            print("  -p, --profile PROFILE    Conan profile to use")
            print("  -v, --verbose           Verbose output")
            print("  -c, --clean            Clean before install")
            print("  -h, --help             Show this help")
            print()
            print("Available profiles:")
            cli.list_profiles()
            return
        else:
            print(f"Unknown option: {arg}")
            print("Use --help for usage information")
            sys.exit(1)
        i += 1
    
    # Execute install
    cli.install(profile=profile, verbose=verbose, clean=clean)

if __name__ == "__main__":
    main()