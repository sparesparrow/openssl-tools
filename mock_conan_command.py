#!/usr/bin/env python3
"""
Mock Conan Command
Simulates custom conan commands when conan is not available
"""

import sys
import os
import shutil
from pathlib import Path

def mock_openssl_profile_generate(profile_name):
    """Mock openssl-profile-generate command"""
    print(f"🔧 Mock Conan Command: openssl-profile-generate {profile_name}")

    # Check if profile exists in dev directory
    source_profile = Path("conan-profiles/dev") / f"{profile_name}.profile"
    target_dir = Path.home() / ".conan2" / "profiles"
    target_profile = target_dir / f"{profile_name}.profile"

    if not source_profile.exists():
        print(f"❌ Source profile not found: {source_profile}")
        return False

    # Create target directory
    target_dir.mkdir(parents=True, exist_ok=True)

    # Copy profile
    shutil.copy2(source_profile, target_profile)
    print(f"✅ Profile created: {target_profile}")

    return True

def main():
    """Main mock conan function"""
    if len(sys.argv) < 3:
        print("Usage: mock_conan_command.py <namespace> <command> [args...]")
        sys.exit(1)

    namespace = sys.argv[1]
    command = sys.argv[2]

    if namespace == "openssl" and command == "profile-generate":
        if len(sys.argv) < 4:
            print("Usage: mock_conan_command.py openssl profile-generate <profile-name>")
            sys.exit(1)

        profile_name = sys.argv[3]
        success = mock_openssl_profile_generate(profile_name)
        sys.exit(0 if success else 1)
    else:
        print(f"Unknown command: {namespace} {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()