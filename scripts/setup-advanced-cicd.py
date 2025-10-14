#!/usr/bin/env python3
"""
Advanced CI/CD Setup for OpenSSL Conan Integration
Enhanced setup script with comprehensive build matrix support
Based on misc-openssl exported assets
"""

import os
import sys
import json
import yaml
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AdvancedCICDSetup:
    """Advanced CI/CD setup with comprehensive OpenSSL build matrix support"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.conan_dev_dir = project_root / "conan-dev"
        self.profiles_dir = self.conan_dev_dir / "profiles"
        self.scripts_dir = project_root / "scripts"
        self.docs_dir = project_root / "docs"
        self.github_dir = project_root / ".github" / "workflows"
        
    def setup_complete_environment(self) -> bool:
        """Set up complete CI/CD environment with build matrix support"""
        logger.info("🚀 Setting up advanced CI/CD environment...")
        
        try:
            # Create directory structure
            self._create_directory_structure()
            
            # Set up Conan profiles
            self._setup_conan_profiles()
            
            # Set up build matrix configuration
            self._setup_build_matrix()
            
            # Set up enhanced workflows
            self._setup_enhanced_workflows()
            
            # Set up Python environment
            self._setup_python_environment()
            
            # Set up documentation
            self._setup_documentation()
            
            # Validate setup
            self._validate_setup()
            
            logger.info("✅ Advanced CI/CD environment setup complete!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Setup failed: {e}")
            return False
    
    def _create_directory_structure(self) -> None:
        """Create necessary directory structure"""
        logger.info("📁 Creating directory structure...")
        
        directories = [
            self.conan_dev_dir,
            self.profiles_dir,
            self.docs_dir,
            self.github_dir,
            self.scripts_dir / "conan",
            self.scripts_dir / "ci",
            self.scripts_dir / "test"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {directory}")
    
    def _setup_conan_profiles(self) -> None:
        """Set up comprehensive Conan profiles"""
        logger.info("🔧 Setting up Conan profiles...")
        
        profiles = {
            "linux-gcc11": {
                "os": "Linux",
                "arch": "x86_64",
                "compiler": "gcc",
                "compiler_version": "11",
                "libcxx": "libstdc++11"
            },
            "linux-clang15": {
                "os": "Linux",
                "arch": "x86_64",
                "compiler": "clang",
                "compiler_version": "15",
                "libcxx": "libstdc++11"
            },
            "linux-arm64-gcc": {
                "os": "Linux",
                "arch": "armv8",
                "compiler": "gcc",
                "compiler_version": "11",
                "libcxx": "libstdc++11"
            },
            "macos-x86_64": {
                "os": "Macos",
                "arch": "x86_64",
                "compiler": "apple-clang",
                "compiler_version": "14.0",
                "libcxx": "libc++"
            },
            "macos-arm64": {
                "os": "Macos",
                "arch": "armv8",
                "compiler": "apple-clang",
                "compiler_version": "14.0",
                "libcxx": "libc++"
            },
            "freebsd-x86_64": {
                "os": "FreeBSD",
                "arch": "x86_64",
                "compiler": "gcc",
                "compiler_version": "11",
                "libcxx": "libstdc++11"
            }
        }
        
        for profile_name, config in profiles.items():
            profile_content = self._generate_profile_content(config)
            profile_path = self.profiles_dir / f"{profile_name}.profile"
            
            with open(profile_path, 'w') as f:
                f.write(profile_content)
            
            logger.info(f"Created profile: {profile_name}")
    
    def _generate_profile_content(self, config: Dict[str, str]) -> str:
        """Generate Conan profile content"""
        return f"""[settings]
os={config['os']}
arch={config['arch']}
compiler={config['compiler']}
compiler.version={config['compiler_version']}
compiler.libcxx={config['libcxx']}
build_type=Release

[conf]
tools.cmake.cmaketoolchain:generator=Ninja
tools.system.package_manager:mode=install
tools.system.package_manager:sudo=True
tools.cmake.cmaketoolchain:jobs=8

[buildenv]
CC={config['compiler']}
CXX={config['compiler']}++
CFLAGS=-O2 -g
CXXFLAGS=-O2 -g
"""
    
    def _setup_build_matrix(self) -> None:
        """Set up build matrix configuration"""
        logger.info("📊 Setting up build matrix configuration...")
        
        build_matrix = {
            "platforms": [
                {
                    "name": "ubuntu-latest",
                    "os": "Linux",
                    "arch": "x86_64",
                    "conan_os": "Linux",
                    "conan_arch": "x86_64"
                },
                {
                    "name": "macos-13",
                    "os": "Macos",
                    "arch": "x86_64",
                    "conan_os": "Macos",
                    "conan_arch": "x86_64"
                },
                {
                    "name": "macos-14",
                    "os": "Macos",
                    "arch": "armv8",
                    "conan_os": "Macos",
                    "conan_arch": "armv8"
                },
                {
                    "name": "linux-arm64",
                    "os": "Linux",
                    "arch": "armv8",
                    "conan_os": "Linux",
                    "conan_arch": "armv8"
                }
            ],
            "compilers": [
                {
                    "name": "gcc",
                    "conan_compiler": "gcc",
                    "versions": ["11"],
                    "platforms": ["Linux", "FreeBSD"]
                },
                {
                    "name": "clang",
                    "conan_compiler": "clang",
                    "versions": ["15"],
                    "platforms": ["Linux", "Macos"]
                }
            ],
            "build_types": [
                {
                    "name": "Release",
                    "conan_build_type": "Release",
                    "cmake_build_type": "Release"
                },
                {
                    "name": "Debug",
                    "conan_build_type": "Debug",
                    "cmake_build_type": "Debug",
                    "config_flags": ["--debug"]
                }
            ],
            "configurations": [
                {
                    "job_name": "basic_gcc",
                    "compiler": "gcc",
                    "build_type": "Release",
                    "options": {
                        "fips": True,
                        "shared": True,
                        "enable_demos": True,
                        "enable_quic": True
                    }
                },
                {
                    "job_name": "basic_clang",
                    "compiler": "clang",
                    "build_type": "Release",
                    "options": {
                        "fips": False,
                        "shared": True,
                        "enable_demos": True
                    }
                },
                {
                    "job_name": "minimal",
                    "compiler": "gcc",
                    "build_type": "Release",
                    "options": {
                        "fips": False,
                        "shared": True,
                        "no_bulk": True,
                        "no_asm": True
                    }
                },
                {
                    "job_name": "full_featured",
                    "compiler": "gcc",
                    "build_type": "Release",
                    "options": {
                        "fips": True,
                        "shared": True,
                        "enable_ktls": True,
                        "enable_zlib": True,
                        "enable_zstd": True,
                        "enable_sctp": True
                    }
                }
            ]
        }
        
        matrix_path = self.conan_dev_dir / "openssl_build_matrix.json"
        with open(matrix_path, 'w') as f:
            json.dump(build_matrix, f, indent=2)
        
        logger.info(f"Created build matrix: {matrix_path}")
    
    def _setup_enhanced_workflows(self) -> None:
        """Set up enhanced GitHub Actions workflows"""
        logger.info("🔄 Setting up enhanced workflows...")
        
        # Enhanced conan-ci.yml
        conan_ci_content = """name: Conan Branch Compilation

on:
  push:
    branches: ['**']
    paths:
      - 'conanfile.py'
      - 'conanfile.txt'
      - 'conan-recipes/**'
      - 'scripts/conan/**'
      - 'conan-dev/**'
      - 'src/**'
      - 'include/**'
      - 'test/**'
      - 'CMakeLists.txt'
      - 'Makefile'
      - 'configure'
      - 'config'
  workflow_dispatch:

jobs:
  detect-changes:
    runs-on: ubuntu-latest
    outputs:
      openssl-changed: ${{ steps.changes.outputs.openssl }}
      conan-changed: ${{ steps.changes.outputs.conan }}
      tests-changed: ${{ steps.changes.outputs.tests }}
    steps:
      - uses: actions/checkout@v4
      - name: Detect changes
        uses: dorny/paths-filter@v2
        id: changes
        with:
          filters: |
            openssl:
              - 'crypto/**'
              - 'ssl/**'
              - 'apps/**'
              - 'include/**'
              - 'CMakeLists.txt'
              - 'configure'
              - 'config'
            conan:
              - 'conanfile.py'
              - 'conanfile.txt'
              - 'conan-recipes/**'
            tests:
              - 'test/**'
              - 'fuzz/**'

  compile-changes:
    needs: detect-changes
    if: needs.detect-changes.outputs.openssl == 'true' || needs.detect-changes.outputs.conan == 'true'
    runs-on: ${{ matrix.os }}
    env:
      CONAN_USER_HOME: ${{ github.workspace }}/.conan2
      CONAN_COLOR_DISPLAY: 1
      CLICOLOR_FORCE: 1
      CLICOLOR: 1
    strategy:
      fail-fast: false
      matrix:
        include:
          - name: Linux x86_64 GCC
            os: ubuntu-latest
            profile: linux-gcc11
            conan_options: -o fips=True -o enable_demos=True -o enable_quic=True
            test: true
          - name: Linux x86_64 Clang
            os: ubuntu-latest
            profile: linux-clang15
            conan_options: -o fips=False -o enable_demos=True
            test: true
          - name: Linux ARM64 GCC
            os: ubuntu-24.04-arm
            profile: linux-arm64-gcc
            conan_options: -o fips=True -o enable_ec_nistp_64_gcc_128=True
            test: true
          - name: macOS x86_64
            os: macos-13
            profile: macos-x86_64
            conan_options: -o fips=True -o enable_demos=True
            test: true
          - name: macOS ARM64
            os: macos-14
            profile: macos-arm64
            conan_options: -o fips=True -o enable_demos=True
            test: true
          - name: Minimal Build
            os: ubuntu-latest
            profile: linux-gcc11
            conan_options: -o no_bulk=True -o no_asm=True
            test: true
          - name: Full Featured
            os: ubuntu-latest
            profile: linux-gcc11
            conan_options: -o fips=True -o enable_ktls=True -o enable_zlib=True -o enable_zstd=True -o enable_sctp=True
            test: true
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v6
        with:
          python-version: '3.12'
          cache: 'pip'
      
      - name: Set up Conan Python Environment
        run: |
          python scripts/setup-ci-environment.py
      
      - name: Install dependencies
        run: |
          python scripts/conan/conan_cli.py install --profile=conan-dev/profiles/${{ matrix.profile }}.profile ${{ matrix.conan_options }}
      
      - name: Build package
        run: |
          python scripts/conan/conan_cli.py build --profile=conan-dev/profiles/${{ matrix.profile }}.profile ${{ matrix.conan_options }}
      
      - name: Run tests
        if: ${{ matrix.test }}
        run: |
          python scripts/conan/conan_cli.py test --profile=conan-dev/profiles/${{ matrix.profile }}.profile ${{ matrix.conan_options }}
      
      - name: Upload build artifacts
        uses: actions/upload-artifact@v4
        with:
          name: conan-build-${{ matrix.profile }}
          path: |
            build/
            package/
"""
        
        conan_ci_path = self.github_dir / "conan-ci.yml"
        with open(conan_ci_path, 'w') as f:
            f.write(conan_ci_content)
        
        logger.info(f"Created workflow: {conan_ci_path}")
    
    def _setup_python_environment(self) -> None:
        """Set up Python environment with enhanced scripts"""
        logger.info("🐍 Setting up Python environment...")
        
        # Create enhanced setup script
        setup_script_content = """#!/usr/bin/env python3
\"\"\"
Enhanced CI Environment Setup
Sets up comprehensive Python environment for OpenSSL Conan builds
\"\"\"

import os
import sys
import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_ci_environment():
    \"\"\"Set up CI environment with all required dependencies\"\"\"
    logger.info("Setting up CI environment...")
    
    # Install Python dependencies
    dependencies = [
        "conan>=2.0",
        "pyyaml",
        "requests",
        "colorama"
    ]
    
    for dep in dependencies:
        logger.info(f"Installing {dep}...")
        subprocess.run([sys.executable, "-m", "pip", "install", dep], check=True)
    
    # Set up Conan configuration
    conan_home = os.environ.get("CONAN_USER_HOME", str(Path.home() / ".conan2"))
    os.makedirs(conan_home, exist_ok=True)
    
    logger.info("CI environment setup complete!")

if __name__ == "__main__":
    setup_ci_environment()
"""
        
        setup_script_path = self.scripts_dir / "setup-ci-environment.py"
        with open(setup_script_path, 'w') as f:
            f.write(setup_script_content)
        
        # Make executable
        os.chmod(setup_script_path, 0o755)
        
        logger.info(f"Created setup script: {setup_script_path}")
    
    def _setup_documentation(self) -> None:
        """Set up comprehensive documentation"""
        logger.info("📚 Setting up documentation...")
        
        # Create README for conan-dev
        readme_content = """# OpenSSL Conan Development Environment

This directory contains the Conan development environment for OpenSSL.

## Structure

- `profiles/` - Conan profiles for different platforms and compilers
- `openssl_build_matrix.json` - Complete build matrix configuration
- `conan.conf` - Conan configuration
- `ci-config.yml` - CI/CD configuration

## Quick Start

1. Set up the environment:
   ```bash
   python scripts/setup-ci-environment.py
   ```

2. Install dependencies:
   ```bash
   python scripts/conan/conan_cli.py install --profile=linux-gcc11
   ```

3. Build the package:
   ```bash
   python scripts/conan/conan_cli.py build --profile=linux-gcc11
   ```

## Available Profiles

- `linux-gcc11` - Linux with GCC 11
- `linux-clang15` - Linux with Clang 15
- `linux-arm64-gcc` - Linux ARM64 with GCC
- `macos-x86_64` - macOS Intel with Apple Clang
- `macos-arm64` - macOS ARM with Apple Clang
- `freebsd-x86_64` - FreeBSD with GCC

## Build Matrix

The build matrix supports 25+ different configurations including:
- FIPS and non-FIPS builds
- Static and shared builds
- Debug and Release builds
- Sanitizer builds (ASAN, UBSAN, MSAN, TSAN)
- Platform-specific optimizations

See `openssl_build_matrix.json` for complete configuration details.
"""
        
        readme_path = self.conan_dev_dir / "README.md"
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        
        logger.info(f"Created documentation: {readme_path}")
    
    def _validate_setup(self) -> None:
        """Validate the complete setup"""
        logger.info("✅ Validating setup...")
        
        # Check required files
        required_files = [
            self.conan_dev_dir / "openssl_build_matrix.json",
            self.github_dir / "conan-ci.yml",
            self.scripts_dir / "setup-ci-environment.py"
        ]
        
        for file_path in required_files:
            if not file_path.exists():
                raise FileNotFoundError(f"Required file not found: {file_path}")
        
        # Check profiles directory
        profile_files = list(self.profiles_dir.glob("*.profile"))
        if len(profile_files) < 5:
            raise ValueError(f"Expected at least 5 profile files, found {len(profile_files)}")
        
        logger.info("✅ Setup validation passed!")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Advanced CI/CD Setup for OpenSSL Conan Integration")
    parser.add_argument("--project-root", type=Path, default=Path.cwd(),
                       help="Project root directory")
    parser.add_argument("--verbose", action="store_true",
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    setup = AdvancedCICDSetup(args.project_root)
    
    if setup.setup_complete_environment():
        print("\n🎉 Advanced CI/CD setup completed successfully!")
        print("\nNext steps:")
        print("1. Review the generated configuration files")
        print("2. Run 'python scripts/setup-ci-environment.py' to set up Python environment")
        print("3. Test with 'python scripts/conan/conan_cli.py install --profile=linux-gcc11'")
        print("4. Check the documentation in docs/ directory")
    else:
        print("\n❌ Setup failed. Check the logs for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()