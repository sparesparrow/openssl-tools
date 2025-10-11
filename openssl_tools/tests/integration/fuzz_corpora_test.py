#!/usr/bin/env python3
"""
Test Fuzz Corpora Integration
Tests the integration of fuzz-corpora Conan package with OpenSSL.
"""

import os
import sys
import subprocess
from pathlib import Path


def test_fuzz_corpora_integration():
    """Test the fuzz corpora integration."""
    print("[TEST] Testing fuzz corpora integration...")
    
    try:
        # Set environment variable to trigger fuzz corpora setup
        os.environ['OSSL_RUN_CI_TESTS'] = '1'
        
        # Use the local conanfile.py to test the integration
        cmd = [
            "conan", "create", ".",
            "--profile=linux-gcc11.profile",
            "--build=missing",
            "--format=json",
            "-o", "openssl/*:enable_fuzzer_libfuzzer=True",
            "-o", "openssl/*:enable_unit_test=True"
        ]
        
        print(f"[CMD] {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Check if fuzz/corpora was created
        corpora_path = Path("fuzz/corpora")
        if corpora_path.exists() and any(corpora_path.iterdir()):
            print("[SUCCESS] Fuzz corpora integration working!")
            
            # Count files
            corpora_files = list(corpora_path.rglob('*'))
            corpora_files = [f for f in corpora_files if f.is_file()]
            print(f"[INFO] Found {len(corpora_files)} corpora files")
            
            # Show some example files
            example_files = corpora_files[:5]
            for file in example_files:
                rel_path = file.relative_to(corpora_path)
                print(f"[INFO] Example file: {rel_path}")
            
            return True
        else:
            print("[ERROR] Fuzz corpora directory not found or empty")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Conan command failed: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return False
    finally:
        # No cleanup needed for local conanfile.py
        pass


def main():
    """Main entry point."""
    success = test_fuzz_corpora_integration()
    
    if success:
        print("\n[SUCCESS] Fuzz corpora integration test passed!")
        return 0
    else:
        print("\n[ERROR] Fuzz corpora integration test failed!")
        return 1


if __name__ == '__main__':
    sys.exit(main())