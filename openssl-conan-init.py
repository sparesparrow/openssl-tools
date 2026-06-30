#!/usr/bin/env python3
"""
OpenSSL Conan initialization script - stdlib only, Conan 2.21.0 pinned
Per Space requirements: Bootstrap via openssl-conan-init.py
"""
import subprocess
import sys
import os

def bootstrap_openssl_tools():
    """Bootstrap OpenSSL tools environment"""
    print("🔧 Bootstrapping OpenSSL Tools Environment...")

    # Install Conan 2.21.0 (pinned per Space requirements)
    print("📦 Installing Conan 2.21.0...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'conan==2.21.0'])

    # Configure Conan
    print("⚙️  Configuring Conan...")
    subprocess.check_call(['conan', 'profile', 'detect', '--force'])
    subprocess.check_call(['conan', 'config', 'set', 'general.revisions_enabled=1'])

    # Export this repository as python_requires
    if os.path.exists('conanfile.py'):
        print("📤 Exporting openssl-tools as python_requires...")
        # Get version dynamically
        try:
            git_version = subprocess.check_output(['git', 'describe', '--tags', '--always']).decode().strip()
            if '-' in git_version:
                base_version = git_version.split('-')[0].lstrip('v')
                commit_count = git_version.split('-')[1]
                version = f"{base_version}.{commit_count}"
            else:
                version = git_version.lstrip('v')
        except subprocess.CalledProcessError:
            version = "1.2.7-dev"

        subprocess.check_call(['conan', 'export', '.', f'openssl-tools/{version}@'])
        print(f"✅ OpenSSL Tools {version} exported successfully!")
    else:
        print("⚠️  No conanfile.py found - skipping export")

if __name__ == "__main__":
    bootstrap_openssl_tools()