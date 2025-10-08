#!/usr/bin/env python3
"""
OpenSSL Tools Conan Test Script
Tests the Conan package following ngapy patterns
"""

import os
import sys
import subprocess
import platform
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import argparse
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OpenSSLToolsConanTest:
    """OpenSSL Tools Conan testing following ngapy patterns"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.platform = platform.system().lower()
        self.conan_dir = project_root / "conan-dev"
        self.test_dir = project_root / "test_package"
        self.venv_dir = self.conan_dir / "venv"
        
    def run_tests(self, profile: str = None, verbose: bool = False) -> bool:
        """Run comprehensive tests"""
        try:
            logger.info("🧪 Running OpenSSL Tools Conan tests...")
            
            # Set up test environment
            self._setup_test_environment()
            
            # Get default profile if not specified
            if not profile:
                profile = self._get_default_profile()
            
            # Run Conan tests
            success = self._run_conan_tests(profile, verbose)
            
            if success:
                logger.info("✅ All tests passed!")
            else:
                logger.error("❌ Some tests failed!")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Test execution failed: {e}")
            return False
    
    def _setup_test_environment(self):
        """Set up test environment"""
        logger.info("🔧 Setting up test environment...")
        
        # Create test directory
        self.test_dir.mkdir(exist_ok=True)
        
        # Create test package structure
        self._create_test_package()
        
        logger.info("✅ Test environment ready")
    
    def _create_test_package(self):
        """Create test package following ngapy patterns"""
        logger.info("📦 Creating test package...")
        
        # Create test_package directory
        test_package_dir = self.test_dir / "test_package"
        test_package_dir.mkdir(exist_ok=True)
        
        # Create test_package conanfile.py
        test_conanfile = test_package_dir / "conanfile.py"
        test_conanfile_content = '''from conans import ConanFile, tools
import os

class OpenSSLToolsTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "virtualenv"
    requires = "openssl-tools/1.0.0@"
    
    def build(self):
        pass
    
    def test(self):
        # Test that openssl-tools is available
        self.run("python -c 'import openssl_tools; print(openssl_tools.__version__)'", run_environment=True)
        
        # Test that tools are available
        self.run("python -c 'from openssl_tools import review_tools, release_tools, statistics; print(\"Tools imported successfully\")'", run_environment=True)
        
        # Test environment variables
        openssl_tools_root = os.environ.get("OPENSSL_TOOLS_ROOT")
        if not openssl_tools_root:
            raise Exception("OPENSSL_TOOLS_ROOT environment variable not set")
        
        print(f"OpenSSL Tools Root: {openssl_tools_root}")
        print("Test package executed successfully!")
'''
        
        with open(test_conanfile, 'w') as f:
            f.write(test_conanfile_content)
        
        logger.info("✅ Test package created")
    
    def _get_default_profile(self) -> str:
        """Get default profile for current platform"""
        if self.platform == "windows":
            return "windows-msvc2022"
        elif self.platform == "darwin":
            return "macos-clang14"
        else:
            return "linux-gcc11"
    
    def _run_conan_tests(self, profile: str, verbose: bool) -> bool:
        """Run Conan tests"""
        logger.info(f"🔨 Running Conan tests with profile: {profile}")
        
        # Get Conan executable
        conan_exe = self._get_conan_executable()
        
        # Get profile path
        profile_path = self.conan_dir / "profiles" / f"{profile}.profile"
        if not profile_path.exists():
            logger.error(f"Profile not found: {profile_path}")
            return False
        
        # Run conan create with test (Conan 2.x syntax)
        cmd = [
            str(conan_exe),
            "create",
            ".",
            "--profile", str(profile_path),
            "--test-folder", "test_package"
        ]
        
        if verbose:
            cmd.append("--verbose")
        
        logger.info(f"Running: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, cwd=self.project_root, check=True, capture_output=True, text=True)
            logger.info("✅ Conan create with test successful")
            if verbose:
                logger.info(f"Output: {result.stdout}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Conan test failed: {e}")
            logger.error(f"STDOUT: {e.stdout}")
            logger.error(f"STDERR: {e.stderr}")
            return False
    
    def _get_conan_executable(self) -> Path:
        """Get Conan executable path"""
        # Try to find Conan in virtual environment first
        if self.platform == "windows":
            conan_exe = self.venv_dir / "Scripts" / "conan.exe"
        else:
            conan_exe = self.venv_dir / "bin" / "conan"
        
        if conan_exe.exists():
            return conan_exe
        
        # Fall back to system Conan
        return Path("conan")
    
    def run_unit_tests(self) -> bool:
        """Run unit tests"""
        logger.info("🧪 Running unit tests...")
        
        # Get Python executable
        if self.platform == "windows":
            python_exe = self.venv_dir / "Scripts" / "python.exe"
        else:
            python_exe = self.venv_dir / "bin" / "python"
        
        # Run pytest
        cmd = [str(python_exe), "-m", "pytest", "tests/", "-v"]
        
        try:
            result = subprocess.run(cmd, cwd=self.project_root, check=True, capture_output=True, text=True)
            logger.info("✅ Unit tests passed")
            logger.info(f"Output: {result.stdout}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Unit tests failed: {e}")
            logger.error(f"STDOUT: {e.stdout}")
            logger.error(f"STDERR: {e.stderr}")
            return False
    
    def run_integration_tests(self) -> bool:
        """Run integration tests"""
        logger.info("🔗 Running integration tests...")
        
        # Test that the package can be imported and used
        test_script = self.test_dir / "integration_test.py"
        test_script_content = '''#!/usr/bin/env python3
"""
Integration test for openssl-tools
"""

import sys
import os

# Add the package to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

try:
    import openssl_tools
    print(f"OpenSSL Tools version: {openssl_tools.__version__}")
    
    # Test imports
    from openssl_tools import review_tools, release_tools, statistics
    print("All modules imported successfully")
    
    # Test environment variables
    openssl_tools_root = os.environ.get("OPENSSL_TOOLS_ROOT")
    if openssl_tools_root:
        print(f"OpenSSL Tools Root: {openssl_tools_root}")
    else:
        print("Warning: OPENSSL_TOOLS_ROOT not set")
    
    print("Integration test passed!")
    
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Test error: {e}")
    sys.exit(1)
'''
        
        with open(test_script, 'w') as f:
            f.write(test_script_content)
        
        # Make executable on Unix
        if self.platform != "windows":
            os.chmod(test_script, 0o755)
        
        # Run integration test
        try:
            result = subprocess.run([sys.executable, str(test_script)], 
                                  cwd=self.test_dir, check=True, capture_output=True, text=True)
            logger.info("✅ Integration tests passed")
            logger.info(f"Output: {result.stdout}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Integration tests failed: {e}")
            logger.error(f"STDOUT: {e.stdout}")
            logger.error(f"STDERR: {e.stderr}")
            return False

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Test OpenSSL Tools Conan package")
    parser.add_argument("--project-root", type=Path, default=Path.cwd(),
                       help="Project root directory")
    parser.add_argument("--profile", "-p", 
                       help="Conan profile to use")
    parser.add_argument("--test-type", "-t", 
                       choices=["conan", "unit", "integration", "all"],
                       default="all",
                       help="Type of test to run")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize test runner
    test_runner = OpenSSLToolsConanTest(args.project_root)
    
    success = True
    
    try:
        if args.test_type in ["conan", "all"]:
            success &= test_runner.run_tests(profile=args.profile, verbose=args.verbose)
        
        if args.test_type in ["unit", "all"]:
            success &= test_runner.run_unit_tests()
        
        if args.test_type in ["integration", "all"]:
            success &= test_runner.run_integration_tests()
    
    except Exception as e:
        logger.error(f"❌ Test execution failed: {e}")
        success = False
    
    if success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()