#!/usr/bin/env python3
"""
Fuzz Corpora Setup Script
Replaces git submodule approach with Conan package for fuzz corpora data.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Optional


class FuzzCorporaSetup:
    """Handles fuzz corpora setup using Conan package."""
    
    def __init__(self):
        self.repo_root = Path(os.environ.get('GITHUB_WORKSPACE', os.getcwd()))
        self.conan_home = Path(os.environ.get('CONAN_USER_HOME', self.repo_root / '.conan2'))
        self.corpora_target = self.repo_root / 'fuzz' / 'corpora'
        
    def setup_corpora(self, profile: str = "default") -> bool:
        """Set up fuzz corpora data using Conan package."""
        print(f"[FUZZ] Setting up fuzz corpora data with profile: {profile}")
        
        try:
            # Ensure Conan is available
            if not self._check_conan_available():
                print("[ERROR] Conan is not available")
                return False
            
            # Create corpora target directory
            self.corpora_target.mkdir(parents=True, exist_ok=True)
            
            # Use the fuzz-corpora-manager to set up the data
            manager_script = self.repo_root / 'scripts' / 'conan' / 'fuzz-corpora-manager.py'
            
            if not manager_script.exists():
                print(f"[ERROR] Fuzz corpora manager script not found: {manager_script}")
                return False
            
            # Run the setup command
            cmd = [
                sys.executable, str(manager_script),
                "setup",
                f"--target-dir={self.corpora_target}",
                f"--profile={profile}"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(result.stdout)
            
            # Verify the setup
            if self._verify_corpora_setup():
                print("[SUCCESS] Fuzz corpora data set up successfully")
                return True
            else:
                print("[ERROR] Fuzz corpora data verification failed")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Setup failed: {e}")
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
    
    def _verify_corpora_setup(self) -> bool:
        """Verify that corpora data is properly set up."""
        if not self.corpora_target.exists():
            return False
        
        # Check if there are any files in the corpora directory
        corpora_files = list(self.corpora_target.rglob('*'))
        corpora_files = [f for f in corpora_files if f.is_file()]
        
        if not corpora_files:
            print("[WARN] No corpora files found")
            return False
        
        print(f"[INFO] Found {len(corpora_files)} corpora files")
        
        # List some example files
        example_files = corpora_files[:5]
        for file in example_files:
            rel_path = file.relative_to(self.corpora_target)
            print(f"[INFO] Example file: {rel_path}")
        
        if len(corpora_files) > 5:
            print(f"[INFO] ... and {len(corpora_files) - 5} more files")
        
        return True
    
    def print_environment_info(self) -> None:
        """Print environment information for debugging."""
        print("\n[INFO] Fuzz Corpora Environment Information:")
        print(f"Repository root: {self.repo_root}")
        print(f"CONAN_USER_HOME: {self.conan_home}")
        print(f"Corpora target: {self.corpora_target}")
        print(f"Corpora exists: {self.corpora_target.exists()}")
        
        if self.corpora_target.exists():
            corpora_files = list(self.corpora_target.rglob('*'))
            corpora_files = [f for f in corpora_files if f.is_file()]
            print(f"Corpora files count: {len(corpora_files)}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Set up fuzz corpora data using Conan package")
    parser.add_argument("--profile", default="default", help="Conan profile to use")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    # Initialize setup
    setup = FuzzCorporaSetup()
    
    # Set up corpora data
    success = setup.setup_corpora(args.profile)
    
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