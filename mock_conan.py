#!/usr/bin/env python3
"""
Mock Conan command for testing purposes
Simulates conan create and other commands when Conan is not available
"""

import sys
import os
from pathlib import Path
import json

def mock_conan_create(package_path, version, user, channel):
    """Mock conan create command."""
    print(f"🔨 Mock Conan Create: {package_path} --version={version} --user={user} --channel={channel}")

    # Validate package structure
    conanfile_path = Path(package_path) / "conanfile.py"
    if not conanfile_path.exists():
        print("❌ conanfile.py not found")
        return False

    # Check if it's a python_requires package
    with open(conanfile_path, 'r') as f:
        content = f.read()

    if 'package_type = "python-requires"' not in content:
        print("❌ Not a python-requires package")
        return False

    if f'version = "{version}"' not in content:
        print(f"❌ Version mismatch: expected {version}")
        return False

    # Simulate package creation
    print("✅ Validating package structure...")
    print("✅ Building package...")
    print("✅ Packaging Python utilities...")
    print("✅ Package created successfully!")

    return True

def mock_conan_upload(package_ref, remote):
    """Mock conan upload command."""
    print(f"📤 Mock Conan Upload: {package_ref} -r={remote}")
    print("✅ Package uploaded successfully!")
    return True

def main():
    """Main mock conan function."""
    if len(sys.argv) < 2:
        print("Usage: mock_conan.py <command> [args...]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "create":
        # Parse arguments: create . --version=0.1.0 --user=_ --channel=_
        package_path = "."
        version = "0.1.0"
        user = "_"
        channel = "_"

        for arg in sys.argv[2:]:
            if arg.startswith("--version="):
                version = arg.split("=", 1)[1]
            elif arg.startswith("--user="):
                user = arg.split("=", 1)[1]
            elif arg.startswith("--channel="):
                channel = arg.split("=", 1)[1]
            elif arg == ".":
                package_path = arg

        success = mock_conan_create(package_path, version, user, channel)
        sys.exit(0 if success else 1)

    elif command == "upload":
        # Parse upload arguments
        package_ref = None
        remote = None

        i = 2
        while i < len(sys.argv):
            if sys.argv[i].startswith("-r="):
                remote = sys.argv[i].split("=", 1)[1]
            elif not sys.argv[i].startswith("-"):
                package_ref = sys.argv[i]
            i += 1

        if not package_ref or not remote:
            print("Usage: mock_conan.py upload <package_ref> -r=<remote>")
            sys.exit(1)

        success = mock_conan_upload(package_ref, remote)
        sys.exit(0 if success else 1)

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()