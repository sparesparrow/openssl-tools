#!/usr/bin/env python3
"""
Test Package Upload
Tests the package upload functionality to multiple registries.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Optional


class PackageUploadTester:
    """Tests package upload functionality."""
    
    def __init__(self):
        self.repo_root = Path(__file__).parent.parent
        self.conan_home = Path(os.environ.get('CONAN_USER_HOME', self.repo_root / '.conan2'))
    
    def test_conan_availability(self) -> bool:
        """Test if Conan is available and working."""
        print("[TEST] Testing Conan availability...")
        
        try:
            result = subprocess.run(['conan', '--version'], 
                                  capture_output=True, text=True, check=True)
            print(f"[OK] Conan version: {result.stdout.strip()}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"[ERROR] Conan not available: {e}")
            return False
    
    def test_registry_configuration(self, registry_name: str) -> bool:
        """Test registry configuration."""
        print(f"[TEST] Testing {registry_name} registry configuration...")
        
        try:
            # Check if remote exists
            result = subprocess.run(['conan', 'remote', 'list'], 
                                  capture_output=True, text=True, check=True)
            
            if registry_name in result.stdout:
                print(f"[OK] {registry_name} remote configured")
                return True
            else:
                print(f"[WARN] {registry_name} remote not found")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to check {registry_name} configuration: {e}")
            return False
    
    def test_package_build(self) -> bool:
        """Test building a simple package."""
        print("[TEST] Testing package build...")
        
        try:
            # Create a simple test package
            test_conanfile = """
from conan import ConanFile

class TestPackageConan(ConanFile):
    name = "test-package"
    version = "1.0.0"
    description = "Test package for upload testing"
    
    def package(self):
        pass
"""
            
            test_file = self.repo_root / "test-package-conanfile.py"
            test_file.write_text(test_conanfile)
            
            # Build the test package
            cmd = ['conan', 'create', str(test_file), '--build=missing']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            print("[OK] Test package built successfully")
            
            # Clean up
            test_file.unlink()
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to build test package: {e}")
            if e.stderr:
                print(f"STDERR: {e.stderr}")
            return False
    
    def test_package_upload(self, package_ref: str, registry_name: str) -> bool:
        """Test uploading a package to a registry."""
        print(f"[TEST] Testing package upload to {registry_name}...")
        
        try:
            # Try to upload (this might fail if credentials are not set)
            cmd = ['conan', 'upload', package_ref, '-r', registry_name, '--all', '--confirm']
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"[OK] Package uploaded to {registry_name}")
                return True
            else:
                print(f"[WARN] Package upload to {registry_name} failed (expected if credentials not set)")
                print(f"STDERR: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"[ERROR] Failed to test upload to {registry_name}: {e}")
            return False
    
    def test_environment_variables(self) -> Dict[str, bool]:
        """Test environment variable availability."""
        print("[TEST] Testing environment variables...")
        
        env_vars = {
            'ARTIFACTORY_URL': os.environ.get('ARTIFACTORY_URL'),
            'ARTIFACTORY_USERNAME': os.environ.get('ARTIFACTORY_USERNAME'),
            'ARTIFACTORY_PASSWORD': os.environ.get('ARTIFACTORY_PASSWORD'),
            'GITHUB_TOKEN': os.environ.get('GITHUB_TOKEN'),
            'GITHUB_ACTOR': os.environ.get('GITHUB_ACTOR'),
            'GITHUB_REPOSITORY': os.environ.get('GITHUB_REPOSITORY'),
        }
        
        results = {}
        for var_name, var_value in env_vars.items():
            if var_value:
                print(f"[OK] {var_name} is set")
                results[var_name] = True
            else:
                print(f"[WARN] {var_name} is not set")
                results[var_name] = False
        
        return results
    
    def test_workflow_files(self) -> bool:
        """Test that workflow files have upload steps."""
        print("[TEST] Testing workflow files...")
        
        workflow_files = [
            '.github/workflows/conan-ci.yml',
            '.github/workflows/package-artifacts-upload.yml'
        ]
        
        all_good = True
        for workflow_file in workflow_files:
            file_path = self.repo_root / workflow_file
            if file_path.exists():
                content = file_path.read_text(encoding='utf-8')
                
                if 'Upload packages to Artifactory' in content:
                    print(f"[OK] {workflow_file} has Artifactory upload step")
                else:
                    print(f"[WARN] {workflow_file} missing Artifactory upload step")
                    all_good = False
                
                if 'Upload packages to GitHub Packages' in content:
                    print(f"[OK] {workflow_file} has GitHub Packages upload step")
                else:
                    print(f"[WARN] {workflow_file} missing GitHub Packages upload step")
                    all_good = False
            else:
                print(f"[WARN] {workflow_file} not found")
                all_good = False
        
        return all_good
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all tests."""
        print("[START] Running package upload tests...\n")
        
        results = {}
        
        # Test Conan availability
        results['conan_available'] = self.test_conan_availability()
        print()
        
        # Test environment variables
        env_results = self.test_environment_variables()
        results.update(env_results)
        print()
        
        # Test package build
        results['package_build'] = self.test_package_build()
        print()
        
        # Test registry configurations
        registries = ['artifactory', 'github-packages', 'conancenter']
        for registry in registries:
            results[f'{registry}_configured'] = self.test_registry_configuration(registry)
        print()
        
        # Test workflow files
        results['workflow_files'] = self.test_workflow_files()
        print()
        
        # Test package upload (if credentials are available)
        if results.get('ARTIFACTORY_URL') and results.get('ARTIFACTORY_USERNAME'):
            results['artifactory_upload'] = self.test_package_upload(
                'test-package/1.0.0', 'artifactory'
            )
        else:
            print("[SKIP] Skipping Artifactory upload test (credentials not set)")
            results['artifactory_upload'] = None
        
        return results
    
    def print_summary(self, results: Dict[str, bool]) -> None:
        """Print test summary."""
        print("\n" + "="*50)
        print("PACKAGE UPLOAD TEST SUMMARY")
        print("="*50)
        
        total_tests = len([r for r in results.values() if r is not None])
        passed_tests = len([r for r in results.values() if r is True])
        failed_tests = len([r for r in results.values() if r is False])
        skipped_tests = len([r for r in results.values() if r is None])
        
        print(f"Total tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Skipped: {skipped_tests}")
        print()
        
        print("Detailed results:")
        for test_name, result in results.items():
            if result is True:
                status = "✅ PASS"
            elif result is False:
                status = "❌ FAIL"
            else:
                status = "⏭️  SKIP"
            print(f"  {test_name}: {status}")
        
        print("\n" + "="*50)
        
        if failed_tests == 0:
            print("🎉 All tests passed!")
            return 0
        else:
            print("⚠️  Some tests failed. Check the output above for details.")
            return 1


def main():
    """Main entry point."""
    tester = PackageUploadTester()
    results = tester.run_all_tests()
    return tester.print_summary(results)


if __name__ == '__main__':
    sys.exit(main())