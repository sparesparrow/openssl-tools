#!/usr/bin/env python3
"""
Minimal Python Environment Package Builder
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
    testing_code = ""
    if include_testing:
        testing_code = '''
            requirements.extend([
                "pytest-xdist",
                "pytest-mock", 
                "pytest-benchmark"
            ])'''
    
    return f'''from conan import ConanFile
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
        pass
    
    def build_requirements(self):
        pass
    
    def generate(self):
        # Create Python environment setup script
        python_setup = """#!/usr/bin/env python
import os
import sys
import subprocess
from pathlib import Path

def setup_environment():
    print("Setting up OpenSSL Python environment...")
    
    python_exe = sys.executable
    
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
    {testing_code}
    
    for package in requirements:
        try:
            subprocess.run([python_exe, "-m", "pip", "install", package], 
                         check=True, capture_output=True)
            print(f"Installed {{package}}")
        except subprocess.CalledProcessError as e:
            print(f"Warning: Failed to install {{package}}: {{e}}")
    
    os.environ['PYTHON_APPLICATION'] = python_exe
    os.environ['CONAN_COLOR_DISPLAY'] = '1'
    os.environ['CLICOLOR_FORCE'] = '1'
    os.environ['CLICOLOR'] = '1'
    
    print("OpenSSL Python environment setup complete!")
    print(f"Python executable: {{python_exe}}")
    print(f"Package version: {package_version}")

if __name__ == "__main__":
    setup_environment()
"""
        
        save(self, "python_setup.py", python_setup)
        self.output.info("Python environment package created successfully!")
    
    def package(self):
        copy(self, "python_setup.py", self.source_folder, self.package_folder)
    
    def package_info(self):
        self.env_info.PYTHON_APPLICATION = "python"
        self.env_info.CONAN_COLOR_DISPLAY = "1"
        self.env_info.CLICOLOR_FORCE = "1"
        self.env_info.CLICOLOR = "1"
'''


def build_python_environment(python_version: str, package_version: str, profile: str = "default", include_testing: bool = True):
    """Build the Python environment package using Conan."""
    print(f"🔨 Building Python environment package...")
    print(f"   Python version: {python_version}")
    print(f"   Package version: {package_version}")
    print(f"   Profile: {profile}")
    print(f"   Testing tools: {include_testing}")
    
    # Create temporary directory for conanfile
    with tempfile.TemporaryDirectory() as temp_dir:
        conanfile_path = os.path.join(temp_dir, "conanfile.py")
        
        # Generate conanfile
        conanfile_content = create_conanfile(python_version, package_version, include_testing)
        
        with open(conanfile_path, 'w') as f:
            f.write(conanfile_content)
        
        # Build the package
        cmd = [
            "conan", "create", conanfile_path,
            "--profile", profile,
            "--build", "missing"
        ]
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("[OK] Build successful!")
            print("Package created and installed in Conan cache")
            return True
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Build failed: {e}")
            if e.stdout:
                print(f"stdout: {e.stdout}")
            if e.stderr:
                print(f"stderr: {e.stderr}")
            return False


def main():
    """Main function to handle command line arguments and build the package."""
    parser = argparse.ArgumentParser(description="Build OpenSSL Python environment package")
    parser.add_argument("--python-version", default="3.12", help="Python version to package")
    parser.add_argument("--package-version", default="latest", help="Package version")
    parser.add_argument("--profile", default="default", help="Conan profile to use")
    parser.add_argument("--no-testing", action="store_true", help="Exclude testing tools")
    
    args = parser.parse_args()
    
    include_testing = not args.no_testing
    
    success = build_python_environment(
        python_version=args.python_version,
        package_version=args.package_version,
        profile=args.profile,
        include_testing=include_testing
    )
    
    if success:
        print("\n🎉 Python environment package built successfully!")
        print("You can now use it with: conan install openssl-python-environment/latest@")
    else:
        print("\n💥 Build failed. Check the error messages above.")
        sys.exit(1)


if __name__ == "__main__":
    main()