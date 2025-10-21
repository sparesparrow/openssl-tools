#!/usr/bin/env python3
"""
Verify Cache Symlink Persistence
Checks if ~/.conan2/p/ symlink to /OSSL/ exists and is persistent
"""

import os
from pathlib import Path

def verify_cache_symlink():
    """Verify the cache symlink exists and points to /OSSL/"""
    cache_path = Path.home() / ".conan2" / "p"
    ossl_path = Path("/OSSL")

    print("🔗 Verifying cache symlink...")

    if not cache_path.exists():
        print(f"❌ Cache path does not exist: {cache_path}")
        return False

    if not cache_path.is_symlink():
        print(f"❌ Cache path is not a symlink: {cache_path}")
        return False

    target = cache_path.readlink()
    if target != ossl_path:
        print(f"❌ Symlink points to wrong target: {target} (expected: {ossl_path})")
        return False

    if not ossl_path.exists():
        print(f"⚠️  Target /OSSL/ does not exist, but symlink is correctly configured")
        return True

    print(f"✅ Cache symlink verified: {cache_path} -> {target}")
    return True

def main():
    """Main verification function"""
    success = verify_cache_symlink()
    if success:
        print("🎉 Cache symlink verification successful!")
        return 0
    else:
        print("❌ Cache symlink verification failed!")
        return 1

if __name__ == "__main__":
    exit(main())