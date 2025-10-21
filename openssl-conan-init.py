#!/usr/bin/env python3
"""
OpenSSL Conan Bootstrap Script
Initializes Conan environment with zero pip dependencies.

This script sets up the basic Conan configuration needed for OpenSSL development
without requiring any external Python dependencies beyond the standard library.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, check=True, capture_output=False):
    """Run a shell command safely."""
    try:
        result = subprocess.run(cmd, shell=True, check=check, capture_output=capture_output, text=True)
        return result.returncode == 0, result.stdout if capture_output else None
    except subprocess.CalledProcessError:
        return False, None

def check_conan_installed():
    """Check if Conan is installed and available."""
    success, _ = run_command("conan --version", capture_output=True)
    return success

def init_conan_config():
    """Initialize basic Conan configuration."""
    print("🔧 Initializing Conan configuration...")

    # Set basic config
    configs = [
        "conan config init",
        "conan config set general.default_profile=default",
        "conan config set general.revisions_enabled=True"
    ]

    for config in configs:
        success, _ = run_command(config)
        if not success:
            print(f"⚠️  Warning: Failed to set config: {config}")
        else:
            print(f"✅ Set: {config}")

def create_default_profile():
    """Create a basic default profile if it doesn't exist."""
    profile_path = Path.home() / ".conan2" / "profiles" / "default"
    if not profile_path.exists():
        print("📝 Creating default profile...")
        profile_content = """[settings]
os=Linux
arch=x86_64
compiler=gcc
compiler.version=11
compiler.libcxx=libstdc++11
build_type=Release

[conf]
tools.cmake.cmaketoolchain:generator=Ninja
"""
        profile_path.parent.mkdir(parents=True, exist_ok=True)
        with open(profile_path, 'w') as f:
            f.write(profile_content)
        print("✅ Created default profile")
    else:
        print("ℹ️  Default profile already exists")

def setup_cache_symlink():
    """Setup cache symlink to /OSSL if it exists."""
    ossl_path = Path("/OSSL")
    cache_path = Path.home() / ".conan2" / "p"

    if ossl_path.exists():
        print("🔗 Setting up cache symlink to /OSSL...")
        if cache_path.exists():
            if cache_path.is_symlink():
                cache_path.unlink()
            else:
                shutil.rmtree(cache_path)

        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.symlink_to(ossl_path)
        print("✅ Cache symlink created")
    else:
        print("ℹ️  /OSSL path not found, skipping symlink setup")

def main():
    """Main bootstrap function."""
    print("🚀 OpenSSL Conan Bootstrap")
    print("=" * 40)

    if not check_conan_installed():
        print("❌ Conan is not installed or not in PATH")
        print("Please install Conan 2.0+ first:")
        print("  pip install conan>=2.0.0")
        sys.exit(1)

    init_conan_config()
    create_default_profile()
    setup_cache_symlink()

    print("\n🎉 Bootstrap complete!")
    print("You can now use Conan for OpenSSL development.")
    print("\nNext steps:")
    print("  conan create . --version=0.1.0 --user=_ --channel=_")

if __name__ == "__main__":
    main()