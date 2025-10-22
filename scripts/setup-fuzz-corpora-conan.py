#!/usr/bin/env python3
"""
Fuzz Corpora Setup via Conan
Sets up fuzz corpora data by building OpenSSL with Conan (which handles corpora download).
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Optional


class FuzzCorporaConanSetup:
    """Handles fuzz corpora setup using Conan build process."""
    
    def __init__(self):
        self.repo_root = Path(os.environ.get('GITHUB_WORKSPACE', os.getcwd()))
        self.conan_home = Path(os.environ.get('CONAN_USER_HOME', self.repo_root / '.conan2'))
        
    def setup_corpora_via_conan(self, profile: str = "default") -> bool:
        """Set up fuzz corpora by building OpenSSL with Conan."""
        print(f"[FUZZ] Setting up fuzz corpora via Conan build with profile: {profile}")
        
        try:
            # Ensure Conan is available
            if not self._check_conan_available():
                print("[ERROR] Conan is not available")
                return False
            
            # Use the local conanfile.py to build OpenSSL with fuzz corpora
            conanfile_path = self.repo_root / "conanfile.py"
            
            if not conanfile_path.exists():
                print("[ERROR] Local conanfile.py not found")
                return False
            
            # Ensure profile has .profile extension if it's not 'default'
            if profile != "default" and not profile.endswith('.profile'):
                profile = f"{profile}.profile"
            
            # Build OpenSSL with fuzzer options enabled
            cmd = [
                "conan", "create", ".",
                f"--profile={profile}",
                "--build=missing",
                "--format=json",
                "-o", "openssl/*:enable_fuzzer_libfuzzer=True",
                "-o", "openssl/*:enable_unit_test=True"
            ]
            
            print(f"[INFO] Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Check if fuzz/corpora was created
            corpora_path = self.repo_root / "fuzz" / "corpora"
            if corpora_path.exists() and any(corpora_path.iterdir()):
                print(f"[SUCCESS] Fuzz corpora data set up successfully")
                print(f"[INFO] Corpora data available at: {corpora_path}")
                
                # Count files
                corpora_files = list(corpora_path.rglob('*'))
                corpora_files = [f for f in corpora_files if f.is_file()]
                print(f"[INFO] Found {len(corpora_files)} corpora files")
                
                return True
            else:
                print("[WARNING] Fuzz corpora data not found after Conan build")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Conan build failed: {e}")
            print(f"STDOUT: {e.stdout}")
            print(f"STDERR: {e.stderr}")
            return False
        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")
            return False
    
    def _check_conan_available(self) -> bool:
        """Check if Conan is available."""
        try:
            result = subprocess.run(['conan', '--version'], 
                                  capture_output=True, text=True, check=True)
            print(f"[INFO] Using Conan: {result.stdout.strip()}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def print_environment_info(self) -> None:
        """Print environment information for debugging."""
        print("\n[INFO] Fuzz Corpora Environment Information:")
        print(f"Repository root: {self.repo_root}")
        print(f"CONAN_USER_HOME: {self.conan_home}")
        
        corpora_path = self.repo_root / "fuzz" / "corpora"
        print(f"Corpora path: {corpora_path}")
        print(f"Corpora exists: {corpora_path.exists()}")
        
        if corpora_path.exists():
            corpora_files = list(corpora_path.rglob('*'))
            corpora_files = [f for f in corpora_files if f.is_file()]
            print(f"Corpora files count: {len(corpora_files)}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Set up fuzz corpora data via Conan build")
    parser.add_argument("--profile", default="default", help="Conan profile to use")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    # Initialize setup
    setup = FuzzCorporaConanSetup()
    
    # Set up corpora data via Conan
    success = setup.setup_corpora_via_conan(args.profile)
    
    if args.verbose:
        setup.print_environment_info()
    
    if success:
        print("\n[SUCCESS] Fuzz corpora setup completed successfully!")
        return 0
    else:
        print("\n[ERROR] Fuzz corpora setup failed!")
        return 1


if __name__ == '__main__':
    sys.exit(main())