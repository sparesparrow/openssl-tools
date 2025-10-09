#!/usr/bin/env python3
"""
Simple Python Environment Package Builder
Creates a basic Conan package for the OpenSSL Python development environment
"""

import argparse
import os
import sys
import subprocess
import tempfile
from pathlib import Path


def create_conanfile(python_version: str, package_version: str, include_testing: bool = True) -> str:
    """Create a simple Conan recipe for the Python environment package."""
    
    # Create the Conan recipe
    conanfile_content = f'''from conan import ConanFile
from conan.tools.files import copy, save
import os
import sys
from pathlib import Path

class PythonEnvironmentConan(ConanFile):
    name = "openssl-python-environment"
    version = "{package_version}"
    description = "OpenSSL Python development environment with Conan tools"
    license = "Apache-2.0"
    url = "https://github.com/openssl/openssl"
    homepage = "https://www.openssl.org"
    topics = ("openssl", "python", "conan", "development", "environment")
    
    settings = "os", "arch", "compiler", "build_type"
    
    def requirements(self):
        pass  # No requirements for now
    
    def build_requirements(self):
        pass  # No build requirements for now
    
    def generate(self):
        # Create a simple Python setup script
        python_setup_content = """#!/usr/bin/env python
import os
import sys
import subprocess

def setup_environment():
    print("[PYTHON] Setting up OpenSSL Python environment...")
    
    python_exe = sys.executable
    
    # Install required packages
    requirements = [
        "conan>=2.0.0",
        "PyYAML",
        "pytest",
        "pytest-cov",
        "coverage",
        "black",
        "flake8",
        "pylint",
        "mypy",
        "isort",
        "markdown-it",
        "normalizer",
        "distro"
    ]
    
    if {str(include_testing).lower()}:
        requirements.extend([
            "pytest-xdist",
            "pytest-mock",
            "pytest-benchmark"
        ])
    
    for package in requirements:
        try:
            subprocess.run([python_exe, "-m", "pip", "install", package], 
                         check=True, capture_output=True)
            print(f"[OK] Installed {{package}}")
        except subprocess.CalledProcessError as e:
            print(f"[WARN] Warning: Failed to install {{package}}: {{e}}")
    
    # Set up environment variables
    os.environ['PYTHON_APPLICATION'] = python_exe
    os.environ['CONAN_COLOR_DISPLAY'] = '1'
    os.environ['CLICOLOR_FORCE'] = '1'
    os.environ['CLICOLOR'] = '1'
    
    print("[SUCCESS] OpenSSL Python environment setup complete!")
    print(f"Python executable: {{python_exe}}")
    print(f"Package version: {package_version}")

if __name__ == "__main__":
    setup_environment()
"""
        
        # Save the Python setup script
        save(self, "python_setup.py", python_setup_content)
        
        # Create a simple package_info
        self.output.info("Python environment package created successfully!")
        self.output.info(f"Version: {package_version}")
        self.output.info(f"Python version: {python_version}")
        self.output.info(f"Testing tools included: {include_testing}")
    
    def package(self):
        # Copy the setup script to the package
        copy(self, "python_setup.py", self.source_folder, self.package_folder)
    
    def package_info(self):
        # Set up environment variables
        self.env_info.PYTHON_APPLICATION = "python"
        self.env_info.CONAN_COLOR_DISPLAY = "1"
        self.env_info.CLICOLOR_FORCE = "1"
        self.env_info.CLICOLOR = "1"
        
        # Add the setup script to PATH
        self.env_info.PATH.append(os.path.join(self.package_folder, "python_setup.py"))
'''
    
    return conanfile_content


def build_package(python_version: str, package_version: str, profile: str = "default", include_testing: bool = True):
    """Build the Python environment package."""
    print(f"🔨 Building Python environment package...")
    print(f"   Python version: {python_version}")
    print(f"   Package version: {package_version}")
    print(f"   Profile: {profile}")
    print(f"   Testing tools: {include_testing}")
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        conanfile_path = temp_path / "conanfile.py"
        
        # Generate conanfile
        conanfile_content = create_conanfile(python_version, package_version, include_testing)
        conanfile_path.write_text(conanfile_content)
        
        # Build the package
        try:
            cmd = [
                "conan", "create", str(conanfile_path),
                "--profile", profile,
                "--build", "missing"
            ]
            
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("[OK] Package built successfully!")
            print(f"   Output: {result.stdout}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Build failed: {e}")
            print(f"   stdout: {e.stdout}")
            print(f"   stderr: {e.stderr}")
            return False


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Build OpenSSL Python environment package")
    parser.add_argument("--python-version", default="3.12", help="Python version to package")
    parser.add_argument("--package-version", default="latest", help="Package version")
    parser.add_argument("--profile", default="default", help="Conan profile to use")
    parser.add_argument("--no-testing", action="store_true", help="Exclude testing tools")
    
    args = parser.parse_args()
    
    include_testing = not args.no_testing
    
    success = build_package(
        python_version=args.python_version,
        package_version=args.package_version,
        profile=args.profile,
        include_testing=include_testing
    )
    
    if success:
        print("🎉 Build completed successfully!")
        sys.exit(0)
    else:
        print("💥 Build failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()