#!/usr/bin/env python3
"""
Simple Pre-commit Hook for OpenSSL Conan packages
Lightweight, well-documented pre-commit checks that don't discourage contributors
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Optional
import argparse


class SimplePreCommitHook:
    """Simple, contributor-friendly pre-commit hook"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []
        
    def run_checks(self, files: List[str]) -> bool:
        """Run essential pre-commit checks"""
        print("🔍 Running simple pre-commit checks...")
        
        # Only check files that are actually being committed
        if not files:
            print("ℹ️  No files to check")
            return True
        
        # Run essential checks
        self._check_basic_syntax(files)
        self._check_file_permissions(files)
        self._check_secrets(files)
        self._check_conanfile_basics(files)
        
        # Print summary
        self._print_summary()
        
        return len(self.errors) == 0
    
    def _check_basic_syntax(self, files: List[str]):
        """Check basic syntax for Python and YAML files"""
        print("  📝 Checking basic syntax...")
        
        for file_path in files:
            if file_path.endswith('.py'):
                self._check_python_syntax(file_path)
            elif file_path.endswith(('.yml', '.yaml')):
                self._check_yaml_syntax(file_path)
    
    def _check_python_syntax(self, file_path: str):
        """Check Python syntax"""
        try:
            result = subprocess.run(['python', '-m', 'py_compile', file_path], 
                                 capture_output=True, text=True)
            if result.returncode == 0:
                self.info.append(f"✓ Python syntax OK: {file_path}")
            else:
                self.errors.append(f"Python syntax error in {file_path}: {result.stderr}")
        except Exception as e:
            self.warnings.append(f"Could not check Python syntax for {file_path}: {e}")
    
    def _check_yaml_syntax(self, file_path: str):
        """Check YAML syntax"""
        try:
            import yaml
            with open(file_path, 'r') as f:
                yaml.safe_load(f)
            self.info.append(f"✓ YAML syntax OK: {file_path}")
        except Exception as e:
            self.errors.append(f"YAML syntax error in {file_path}: {e}")
    
    def _check_file_permissions(self, files: List[str]):
        """Check file permissions for security"""
        print("  🔒 Checking file permissions...")
        
        for file_path in files:
            if os.path.exists(file_path):
                stat = os.stat(file_path)
                # Check if file is world-writable
                if stat.st_mode & 0o002:
                    self.warnings.append(f"File {file_path} is world-writable")
                else:
                    self.info.append(f"✓ File permissions OK: {file_path}")
    
    def _check_secrets(self, files: List[str]):
        """Check for obvious secrets (lightweight)"""
        print("  🔐 Checking for obvious secrets...")
        
        secret_patterns = [
            'password=',
            'secret=',
            'key=',
            'token=',
            'api_key=',
            'private_key='
        ]
        
        for file_path in files:
            if file_path.endswith(('.py', '.yml', '.yaml', '.json', '.txt')):
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    for pattern in secret_patterns:
                        if pattern in content.lower():
                            self.warnings.append(f"Potential secret in {file_path}: {pattern}")
                            break
                    else:
                        self.info.append(f"✓ No obvious secrets in {file_path}")
                        
                except Exception as e:
                    self.warnings.append(f"Could not check {file_path} for secrets: {e}")
    
    def _check_conanfile_basics(self, files: List[str]):
        """Check basic conanfile.py structure"""
        print("  📦 Checking conanfile basics...")
        
        conanfile_path = None
        for file_path in files:
            if file_path.endswith('conanfile.py'):
                conanfile_path = file_path
                break
        
        if conanfile_path:
            self._validate_conanfile_basics(conanfile_path)
        else:
            self.info.append("ℹ️  No conanfile.py in commit")
    
    def _validate_conanfile_basics(self, conanfile_path: str):
        """Validate basic conanfile.py structure"""
        try:
            with open(conanfile_path, 'r') as f:
                content = f.read()
            
            # Check for required class
            if 'class OpenSSLConan(ConanFile):' in content:
                self.info.append("✓ conanfile.py has required class")
            else:
                self.errors.append("conanfile.py missing required class")
            
            # Check for required methods
            required_methods = ['configure', 'build', 'package', 'package_info']
            for method in required_methods:
                if f"def {method}(" in content:
                    self.info.append(f"✓ conanfile.py has {method} method")
                else:
                    self.warnings.append(f"conanfile.py missing {method} method")
            
            # Check for version detection
            if 'VERSION.dat' in content:
                self.info.append("✓ conanfile.py reads version from VERSION.dat")
            else:
                self.warnings.append("conanfile.py doesn't read version from VERSION.dat")
                
        except Exception as e:
            self.errors.append(f"Error validating conanfile.py: {e}")
    
    def _print_summary(self):
        """Print check summary"""
        print("\n" + "="*50)
        print("📊 PRE-COMMIT SUMMARY")
        print("="*50)
        
        if self.info:
            print(f"\n✅ INFO ({len(self.info)} items):")
            for item in self.info:
                print(f"  • {item}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)} items):")
            for item in self.warnings:
                print(f"  • {item}")
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)} items):")
            for item in self.errors:
                print(f"  • {item}")
        
        print("\n" + "="*50)
        
        if self.errors:
            print("❌ PRE-COMMIT FAILED - Fix errors before committing")
            return False
        elif self.warnings:
            print("⚠️  PRE-COMMIT PASSED WITH WARNINGS - Review warnings")
            return True
        else:
            print("✅ PRE-COMMIT PASSED - Ready to commit")
            return True


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Simple pre-commit hook for OpenSSL Conan packages')
    parser.add_argument('files', nargs='*', help='Files to check')
    parser.add_argument('--all', action='store_true', help='Check all files')
    
    args = parser.parse_args()
    
    hook = SimplePreCommitHook()
    
    if args.all:
        # Get all files from git
        try:
            result = subprocess.run(['git', 'diff', '--cached', '--name-only'], 
                                 capture_output=True, text=True)
            if result.returncode == 0:
                files = [f.strip() for f in result.stdout.split('\n') if f.strip()]
            else:
                files = []
        except:
            files = []
    else:
        files = args.files
    
    success = hook.run_checks(files)
    
    if not success:
        sys.exit(1)
    else:
        print("\n🎉 Pre-commit checks completed!")
        sys.exit(0)


if __name__ == '__main__':
    main()
