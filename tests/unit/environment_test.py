#!/usr/bin/env python3
"""
Conan Environment Testing Suite
Tests the Conan Python environment setup and configuration
"""

import os
import sys
import subprocess
import json
import platform
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
import pytest
import yaml

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ConanEnvironmentTester:
    """Test suite for Conan environment validation"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.conan_home = project_root / ".conan2"
        self.test_results = []
        
    def test_python_environment(self) -> bool:
        """Test Python environment setup"""
        logger.info("Testing Python environment...")
        
        try:
            # Test Python version
            python_version = sys.version_info
            assert python_version >= (3, 8), f"Python 3.8+ required, got {python_version}"
            
            # Test required packages
            required_packages = ['conan', 'pyyaml', 'requests']
            for package in required_packages:
                try:
                    __import__(package)
                except ImportError:
                    logger.error(f"Required package {package} not found")
                    return False
            
            # Test Conan version
            result = subprocess.run(['conan', '--version'], capture_output=True, text=True)
            assert result.returncode == 0, f"Conan not properly installed: {result.stderr}"
            
            logger.info(f"✅ Python environment test passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Python environment test failed: {e}")
            return False
    
    def test_conan_configuration(self) -> bool:
        """Test Conan configuration"""
        logger.info("Testing Conan configuration...")
        
        try:
            # Test Conan home directory
            assert self.conan_home.exists(), f"Conan home directory not found: {self.conan_home}"
            
            # Test conan.conf
            conan_conf = self.conan_home / "conan.conf"
            if conan_conf.exists():
                with open(conan_conf, 'r') as f:
                    content = f.read()
                    assert 'conancenter' in content, "ConanCenter remote not configured"
            
            # Test profile detection
            result = subprocess.run(['conan', 'profile', 'detect', '--force'], 
                                  capture_output=True, text=True, cwd=self.project_root)
            assert result.returncode == 0, f"Profile detection failed: {result.stderr}"
            
            # Test profile listing
            result = subprocess.run(['conan', 'profile', 'list'], 
                                  capture_output=True, text=True, cwd=self.project_root)
            assert result.returncode == 0, f"Profile listing failed: {result.stderr}"
            
            logger.info("✅ Conan configuration test passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Conan configuration test failed: {e}")
            return False
    
    def test_profiles(self) -> bool:
        """Test Conan profiles"""
        logger.info("Testing Conan profiles...")
        
        try:
            profiles_dir = self.project_root / "conan-dev" / "profiles"
            assert profiles_dir.exists(), f"Profiles directory not found: {profiles_dir}"
            
            # Test each profile
            profile_files = list(profiles_dir.glob("*.profile"))
            assert len(profile_files) > 0, "No profile files found"
            
            for profile_file in profile_files:
                logger.info(f"Testing profile: {profile_file.name}")
                
                # Test profile syntax
                result = subprocess.run(['conan', 'profile', 'show', str(profile_file)], 
                                      capture_output=True, text=True, cwd=self.project_root)
                assert result.returncode == 0, f"Profile {profile_file.name} is invalid: {result.stderr}"
            
            logger.info("✅ Conan profiles test passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Conan profiles test failed: {e}")
            return False
    
    def test_conanfile_validation(self) -> bool:
        """Test conanfile.py validation"""
        logger.info("Testing conanfile.py validation...")
        
        try:
            conanfile = self.project_root / "conanfile.py"
            assert conanfile.exists(), "conanfile.py not found"
            
            # Test conanfile syntax
            result = subprocess.run(['conan', 'graph', 'info', '.'], 
                                  capture_output=True, text=True, cwd=self.project_root)
            assert result.returncode == 0, f"conanfile.py validation failed: {result.stderr}"
            
            # Test dependency resolution
            result = subprocess.run(['conan', 'install', '.', '--dry-run'], 
                                  capture_output=True, text=True, cwd=self.project_root)
            assert result.returncode == 0, f"Dependency resolution failed: {result.stderr}"
            
            logger.info("✅ conanfile.py validation test passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ conanfile.py validation test failed: {e}")
            return False
    
    def test_python_scripts(self) -> bool:
        """Test Python Conan scripts"""
        logger.info("Testing Python Conan scripts...")
        
        try:
            scripts_dir = self.project_root / "scripts" / "conan"
            assert scripts_dir.exists(), f"Scripts directory not found: {scripts_dir}"
            
            # Test conan_cli.py
            cli_script = scripts_dir / "conan_cli.py"
            assert cli_script.exists(), "conan_cli.py not found"
            
            # Test script execution
            result = subprocess.run([sys.executable, str(cli_script), '--help'], 
                                  capture_output=True, text=True, cwd=self.project_root)
            assert result.returncode == 0, f"conan_cli.py execution failed: {result.stderr}"
            
            # Test conan_orchestrator.py
            orchestrator_script = scripts_dir / "conan_orchestrator.py"
            assert orchestrator_script.exists(), "conan_orchestrator.py not found"
            
            # Test orchestrator import
            sys.path.insert(0, str(scripts_dir))
            try:
                import conan_orchestrator
                assert hasattr(conan_orchestrator, 'ConanOrchestrator'), "ConanOrchestrator class not found"
            finally:
                sys.path.pop(0)
            
            logger.info("✅ Python scripts test passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Python scripts test failed: {e}")
            return False
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all environment tests"""
        logger.info("Starting Conan environment tests...")
        
        tests = [
            ("python_environment", self.test_python_environment),
            ("conan_configuration", self.test_conan_configuration),
            ("profiles", self.test_profiles),
            ("conanfile_validation", self.test_conanfile_validation),
            ("python_scripts", self.test_python_scripts),
        ]
        
        results = {}
        for test_name, test_func in tests:
            try:
                results[test_name] = test_func()
            except Exception as e:
                logger.error(f"Test {test_name} failed with exception: {e}")
                results[test_name] = False
        
        # Summary
        passed = sum(results.values())
        total = len(results)
        logger.info(f"Environment tests completed: {passed}/{total} passed")
        
        return results

def main():
    """Main entry point"""
    project_root = Path(__file__).parent.parent.parent
    tester = ConanEnvironmentTester(project_root)
    results = tester.run_all_tests()
    
    # Exit with error code if any test failed
    if not all(results.values()):
        sys.exit(1)

if __name__ == "__main__":
    main()