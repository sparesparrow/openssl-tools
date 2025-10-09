#!/usr/bin/env python3
"""
Conan Development Environment Setup Script
Sets up a complete Python environment for Conan development with automated CI/CD
"""

import os
import sys
import subprocess
import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional
import argparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ConanDevEnvironment:
    """Conan Development Environment Manager"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.conan_dir = project_root / "conan-dev"
        self.profiles_dir = self.conan_dir / "profiles"
        self.workflows_dir = project_root / ".github" / "workflows"
        self.scripts_dir = project_root / "scripts"
        
    def setup_environment(self) -> bool:
        """Set up the complete Conan development environment"""
        try:
            logger.info("🚀 Setting up Conan development environment...")
            
            # Create directory structure
            self._create_directory_structure()
            
            # Install Python dependencies
            self._install_python_dependencies()
            
            # Create Conan profiles
            self._create_conan_profiles()
            
            # Set up CI/CD workflows
            self._setup_cicd_workflows()
            
            # Create developer scripts
            self._create_developer_scripts()
            
            # Create configuration files
            self._create_configuration_files()
            
            logger.info("✅ Conan development environment setup complete!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Setup failed: {e}")
            return False
    
    def _create_directory_structure(self):
        """Create necessary directory structure"""
        directories = [
            self.conan_dir,
            self.profiles_dir,
            self.conan_dir / "locks",
            self.conan_dir / "cache",
            self.conan_dir / "artifacts",
            self.scripts_dir / "conan",
            self.scripts_dir / "ci",
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"📁 Created directory: {directory}")
    
    def _install_python_dependencies(self):
        """Install Python dependencies for Conan development"""
        requirements = [
            "conan>=2.0.0",
            "conan-tools>=0.1.0",
            "pyyaml>=6.0",
            "requests>=2.28.0",
            "click>=8.0.0",
            "rich>=13.0.0",
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ]
        
        logger.info("📦 Installing Python dependencies...")
        for req in requirements:
            subprocess.run([sys.executable, "-m", "pip", "install", req], check=True)
            logger.info(f"✅ Installed: {req}")
    
    def _create_conan_profiles(self):
        """Create Conan profiles for different platforms"""
        profiles = {
            "linux-gcc11": {
                "settings": {
                    "os": "Linux",
                    "arch": "x86_64",
                    "compiler": "gcc",
                    "compiler.version": "11",
                    "compiler.libcxx": "libstdc++11",
                    "build_type": "Release"
                },
                "conf": {
                    "tools.cmake.cmaketoolchain:generator": "Ninja",
                    "tools.system.package_manager:mode": "install",
                    "tools.system.package_manager:sudo": "True"
                }
            },
            "linux-clang15": {
                "settings": {
                    "os": "Linux",
                    "arch": "x86_64",
                    "compiler": "clang",
                    "compiler.version": "15",
                    "compiler.libcxx": "libstdc++11",
                    "build_type": "Release"
                },
                "conf": {
                    "tools.cmake.cmaketoolchain:generator": "Ninja",
                    "tools.system.package_manager:mode": "install",
                    "tools.system.package_manager:sudo": "True"
                }
            },
            "windows-msvc2022": {
                "settings": {
                    "os": "Windows",
                    "arch": "x86_64",
                    "compiler": "msvc",
                    "compiler.version": "193",
                    "compiler.runtime": "dynamic",
                    "build_type": "Release"
                },
                "conf": {
                    "tools.cmake.cmaketoolchain:generator": "Visual Studio 17 2022"
                }
            },
            "macos-clang14": {
                "settings": {
                    "os": "Macos",
                    "arch": "x86_64",
                    "compiler": "apple-clang",
                    "compiler.version": "14",
                    "compiler.libcxx": "libc++",
                    "build_type": "Release"
                },
                "conf": {
                    "tools.cmake.cmaketoolchain:generator": "Xcode"
                }
            },
            "debug": {
                "settings": {
                    "build_type": "Debug"
                },
                "conf": {
                    "tools.cmake.cmaketoolchain:generator": "Ninja"
                }
            }
        }
        
        for profile_name, profile_config in profiles.items():
            profile_path = self.profiles_dir / f"{profile_name}.profile"
            with open(profile_path, 'w') as f:
                f.write(f"[settings]\n")
                for key, value in profile_config.get("settings", {}).items():
                    f.write(f"{key}={value}\n")
                
                if "conf" in profile_config:
                    f.write(f"\n[conf]\n")
                    for key, value in profile_config["conf"].items():
                        f.write(f"{key}={value}\n")
            
            logger.info(f"📝 Created profile: {profile_name}")
    
    def _setup_cicd_workflows(self):
        """Set up CI/CD workflows for different triggers"""
        workflows = {
            "conan-ci.yml": self._create_branch_compilation_workflow(),
            "conan-pr-tests.yml": self._create_pr_integration_workflow(),
            "conan-release.yml": self._create_release_deployment_workflow(),
            "conan-manual-trigger.yml": self._create_manual_trigger_workflow(),
            "conan-nightly.yml": self._create_nightly_rebuild_workflow(),
        }
        
        for workflow_name, workflow_content in workflows.items():
            workflow_path = self.workflows_dir / workflow_name
            with open(workflow_path, 'w') as f:
                f.write(workflow_content)
            logger.info(f"🔄 Created workflow: {workflow_name}")
    
    def _create_branch_compilation_workflow(self) -> str:
        """Create workflow for branch compilation triggers"""
        return """name: Conan Branch Compilation

on:
  push:
    branches: ['**']
    paths:
      - 'conanfile.py'
      - 'conanfile.txt'
      - 'conan-recipes/**'
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
    runs-on: ubuntu-latest
    strategy:
      matrix:
        profile: [linux-gcc11, linux-clang15]
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install Conan
        run: |
          pip install conan
          conan profile detect --force
      
      - name: Create profile
        run: |
          cp conan-dev/profiles/${{ matrix.profile }}.profile ~/.conan2/profiles/default
      
      - name: Install dependencies
        run: |
          conan install . --profile=${{ matrix.profile }} --build=missing
      
      - name: Build package
        run: |
          conan build . --profile=${{ matrix.profile }}
      
      - name: Upload build artifacts
        uses: actions/upload-artifact@v4
        with:
          name: conan-build-${{ matrix.profile }}
          path: |
            build/
            package/
"""

    def _create_pr_integration_workflow(self) -> str:
        """Create workflow for PR integration tests"""
        return """name: Conan PR Integration Tests

on:
  pull_request:
    branches: [main, master]
    paths:
      - 'conanfile.py'
      - 'conanfile.txt'
      - 'conan-recipes/**'
      - 'src/**'
      - 'include/**'
      - 'test/**'
  workflow_dispatch:

jobs:
  integration-tests:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        include:
          - os: ubuntu-22.04
            profile: linux-gcc11
            compiler: gcc
          - os: ubuntu-22.04
            profile: linux-clang15
            compiler: clang
          - os: windows-2022
            profile: windows-msvc2022
            compiler: msvc
          - os: macos-12
            profile: macos-clang14
            compiler: apple-clang
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install Conan
        run: |
          pip install conan
          conan profile detect --force
      
      - name: Create profile
        run: |
          cp conan-dev/profiles/${{ matrix.profile }}.profile ~/.conan2/profiles/default
      
      - name: Install dependencies
        run: |
          conan install . --profile=${{ matrix.profile }} --build=missing
      
      - name: Build package
        run: |
          conan build . --profile=${{ matrix.profile }}
      
      - name: Run tests
        run: |
          conan test test_package openssl/3.5.0@user/channel --profile=${{ matrix.profile }}
      
      - name: Generate lockfile
        run: |
          conan lock create conanfile.py --profile=${{ matrix.profile }} --lockfile=conan-dev/locks/${{ matrix.profile }}.lock
      
      - name: Upload test results
        uses: actions/upload-artifact@v4
        with:
          name: test-results-${{ matrix.profile }}
          path: |
            test_results/
            conan-dev/locks/${{ matrix.profile }}.lock

  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run security scan
        run: |
          pip install safety bandit
          safety check
          bandit -r src/ -f json -o security-report.json
      
      - name: Upload security report
        uses: actions/upload-artifact@v4
        with:
          name: security-report
          path: security-report.json

  performance-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install Conan
        run: |
          pip install conan
          conan profile detect --force
      
      - name: Performance benchmark
        run: |
          python scripts/conan/performance_benchmark.py
      
      - name: Upload performance results
        uses: actions/upload-artifact@v4
        with:
          name: performance-results
          path: performance_results.json
"""

    def _create_release_deployment_workflow(self) -> str:
        """Create workflow for release and deployment"""
        return """name: Conan Release & Deploy

on:
  push:
    branches: [main, master]
    paths:
      - 'VERSION.dat'
      - 'conanfile.py'
      - 'conanfile.txt'
  workflow_dispatch:
    inputs:
      version:
        description: 'Version to release'
        required: true
        default: 'auto'

jobs:
  prepare-release:
    runs-on: ubuntu-latest
    outputs:
      version: ${{ steps.version.outputs.version }}
      should-release: ${{ steps.version.outputs.should-release }}
    steps:
      - uses: actions/checkout@v4
      
      - name: Determine version
        id: version
        run: |
          if [ "${{ github.event.inputs.version }}" = "auto" ]; then
            VERSION=$(cat VERSION.dat | tr -d '\\n')
          else
            VERSION="${{ github.event.inputs.version }}"
          fi
          
          # Check if this is a new version
          if git tag | grep -q "^v$VERSION$"; then
            echo "should-release=false" >> $GITHUB_OUTPUT
          else
            echo "should-release=true" >> $GITHUB_OUTPUT
          fi
          
          echo "version=$VERSION" >> $GITHUB_OUTPUT
          echo "Version: $VERSION"
          echo "Should release: ${{ steps.version.outputs.should-release }}"

  build-release:
    needs: prepare-release
    if: needs.prepare-release.outputs.should-release == 'true'
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        include:
          - os: ubuntu-22.04
            profile: linux-gcc11
          - os: ubuntu-22.04
            profile: linux-clang15
          - os: windows-2022
            profile: windows-msvc2022
          - os: macos-12
            profile: macos-clang14
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install Conan
        run: |
          pip install conan
          conan profile detect --force
      
      - name: Create profile
        run: |
          cp conan-dev/profiles/${{ matrix.profile }}.profile ~/.conan2/profiles/default
      
      - name: Build release package
        run: |
          conan create . openssl/${{ needs.prepare-release.outputs.version }}@user/channel --profile=${{ matrix.profile }} --build=missing
      
      - name: Upload release artifacts
        uses: actions/upload-artifact@v4
        with:
          name: release-${{ matrix.profile }}
          path: |
            ~/.conan2/p/*/p/

  deploy-release:
    needs: [prepare-release, build-release]
    if: needs.prepare-release.outputs.should-release == 'true'
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4
      
      - name: Download all artifacts
        uses: actions/download-artifact@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install Conan
        run: |
          pip install conan
          conan profile detect --force
      
      - name: Configure remote
        run: |
          conan remote add production ${{ secrets.CONAN_REMOTE_URL }}
          conan user -p ${{ secrets.CONAN_REMOTE_PASSWORD }} -r production ${{ secrets.CONAN_REMOTE_USERNAME }}
      
      - name: Upload to production
        run: |
          conan upload "openssl/${{ needs.prepare-release.outputs.version }}@user/channel" -r=production --all --confirm
      
      - name: Create GitHub release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: v${{ needs.prepare-release.outputs.version }}
          release_name: OpenSSL ${{ needs.prepare-release.outputs.version }}
          body: |
            OpenSSL ${{ needs.prepare-release.outputs.version }} Conan Package
            
            ## Platforms Supported
            - Linux (GCC 11, Clang 15)
            - Windows (MSVC 2022)
            - macOS (Clang 14)
            
            ## Installation
            ```bash
            conan install openssl/${{ needs.prepare-release.outputs.version }}@user/channel
            ```
          draft: false
          prerelease: false
"""

    def _create_manual_trigger_workflow(self) -> str:
        """Create workflow for manual triggers via comments"""
        return """name: Conan Manual Trigger

on:
  issue_comment:
    types: [created]
  workflow_dispatch:
    inputs:
      action:
        description: 'Action to perform'
        required: true
        default: 'build'
        type: choice
        options:
          - build
          - test
          - release
          - clean
      profile:
        description: 'Profile to use'
        required: false
        default: 'linux-gcc11'
        type: choice
        options:
          - linux-gcc11
          - linux-clang15
          - windows-msvc2022
          - macos-clang14

jobs:
  parse-comment:
    runs-on: ubuntu-latest
    if: github.event_name == 'issue_comment'
    outputs:
      action: ${{ steps.parse.outputs.action }}
      profile: ${{ steps.parse.outputs.profile }}
      should-trigger: ${{ steps.parse.outputs.should-trigger }}
    steps:
      - name: Parse comment
        id: parse
        run: |
          COMMENT="${{ github.event.comment.body }}"
          
          if echo "$COMMENT" | grep -q "/conan build"; then
            echo "action=build" >> $GITHUB_OUTPUT
            echo "should-trigger=true" >> $GITHUB_OUTPUT
            
            if echo "$COMMENT" | grep -q "linux-clang15"; then
              echo "profile=linux-clang15" >> $GITHUB_OUTPUT
            elif echo "$COMMENT" | grep -q "windows"; then
              echo "profile=windows-msvc2022" >> $GITHUB_OUTPUT
            elif echo "$COMMENT" | grep -q "macos"; then
              echo "profile=macos-clang14" >> $GITHUB_OUTPUT
            else
              echo "profile=linux-gcc11" >> $GITHUB_OUTPUT
            fi
          elif echo "$COMMENT" | grep -q "/conan test"; then
            echo "action=test" >> $GITHUB_OUTPUT
            echo "should-trigger=true" >> $GITHUB_OUTPUT
            echo "profile=linux-gcc11" >> $GITHUB_OUTPUT
          elif echo "$COMMENT" | grep -q "/conan release"; then
            echo "action=release" >> $GITHUB_OUTPUT
            echo "should-trigger=true" >> $GITHUB_OUTPUT
            echo "profile=linux-gcc11" >> $GITHUB_OUTPUT
          else
            echo "should-trigger=false" >> $GITHUB_OUTPUT
          fi

  manual-build:
    needs: parse-comment
    if: |
      (github.event_name == 'issue_comment' && needs.parse-comment.outputs.should-trigger == 'true' && needs.parse-comment.outputs.action == 'build') ||
      (github.event_name == 'workflow_dispatch' && github.event.inputs.action == 'build')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install Conan
        run: |
          pip install conan
          conan profile detect --force
      
      - name: Set profile
        run: |
          if [ "${{ github.event_name }}" = "issue_comment" ]; then
            PROFILE="${{ needs.parse-comment.outputs.profile }}"
          else
            PROFILE="${{ github.event.inputs.profile }}"
          fi
          echo "PROFILE=$PROFILE" >> $GITHUB_ENV
          cp conan-dev/profiles/$PROFILE.profile ~/.conan2/profiles/default
      
      - name: Build package
        run: |
          conan install . --profile=$PROFILE --build=missing
          conan build . --profile=$PROFILE
      
      - name: Comment result
        if: github.event_name == 'issue_comment'
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '✅ Manual build completed successfully with profile: ${{ env.PROFILE }}'
            })

  manual-test:
    needs: parse-comment
    if: |
      (github.event_name == 'issue_comment' && needs.parse-comment.outputs.should-trigger == 'true' && needs.parse-comment.outputs.action == 'test') ||
      (github.event_name == 'workflow_dispatch' && github.event.inputs.action == 'test')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install Conan
        run: |
          pip install conan
          conan profile detect --force
      
      - name: Set profile
        run: |
          if [ "${{ github.event_name }}" = "issue_comment" ]; then
            PROFILE="${{ needs.parse-comment.outputs.profile }}"
          else
            PROFILE="${{ github.event.inputs.profile }}"
          fi
          echo "PROFILE=$PROFILE" >> $GITHUB_ENV
          cp conan-dev/profiles/$PROFILE.profile ~/.conan2/profiles/default
      
      - name: Run tests
        run: |
          conan install . --profile=$PROFILE --build=missing
          conan build . --profile=$PROFILE
          conan test test_package openssl/3.5.0@user/channel --profile=$PROFILE
      
      - name: Comment result
        if: github.event_name == 'issue_comment'
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '✅ Manual tests completed successfully with profile: ${{ env.PROFILE }}'
            })
"""

    def _create_nightly_rebuild_workflow(self) -> str:
        """Create workflow for nightly rebuilds"""
        return """name: Conan Nightly Rebuild

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC
  workflow_dispatch:

jobs:
  get-changed-branches:
    runs-on: ubuntu-latest
    outputs:
      branches: ${{ steps.branches.outputs.branches }}
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Get changed branches
        id: branches
        run: |
          # Get all branches that have commits in the last 24 hours
          BRANCHES=$(git for-each-ref --format='%(refname:short)' refs/remotes/origin | \
            xargs -I {} git log --since="24 hours ago" --oneline origin/{} | \
            cut -d' ' -f2- | sort -u | tr '\\n' ' ')
          
          echo "branches=$BRANCHES" >> $GITHUB_OUTPUT
          echo "Found branches: $BRANCHES"

  rebuild-branches:
    needs: get-changed-branches
    runs-on: ubuntu-latest
    if: needs.get-changed-branches.outputs.branches != ''
    strategy:
      matrix:
        profile: [linux-gcc11, linux-clang15]
    
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ matrix.branch }}
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install Conan
        run: |
          pip install conan
          conan profile detect --force
      
      - name: Create profile
        run: |
          cp conan-dev/profiles/${{ matrix.profile }}.profile ~/.conan2/profiles/default
      
      - name: Clean previous builds
        run: |
          conan remove "*" --force
          rm -rf build/ package/
      
      - name: Rebuild package
        run: |
          conan install . --profile=${{ matrix.profile }} --build=missing
          conan build . --profile=${{ matrix.profile }}
      
      - name: Run tests
        run: |
          conan test test_package openssl/3.5.0@user/channel --profile=${{ matrix.profile }}
      
      - name: Upload nightly artifacts
        uses: actions/upload-artifact@v4
        with:
          name: nightly-${{ matrix.branch }}-${{ matrix.profile }}
          path: |
            build/
            package/
            test_results/

  cleanup-old-artifacts:
    runs-on: ubuntu-latest
    steps:
      - name: Clean up old artifacts
        run: |
          # This would typically clean up old artifacts from storage
          echo "Cleaning up artifacts older than 30 days..."
          # Add cleanup logic here
"""

    def _create_developer_scripts(self):
        """Create developer-friendly scripts"""
        scripts = {
            "conan-install": self._create_conan_install_script(),
            "conan-build": self._create_conan_build_script(),
            "conan-dev-setup": self._create_dev_setup_script(),
        }
        
        for script_name, script_content in scripts.items():
            script_path = self.scripts_dir / "conan" / script_name
            with open(script_path, 'w') as f:
                f.write(script_content)
            script_path.chmod(0o755)
            logger.info(f"📜 Created script: {script_name}")
    
    def _create_conan_install_script(self) -> str:
        """Create conan install script"""
        return """#!/bin/bash
# Conan Install Script - Developer-friendly wrapper

set -e

# Default values
PROFILE="linux-gcc11"
BUILD_MISSING="--build=missing"
VERBOSE=""
CLEAN=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--profile)
            PROFILE="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE="-v"
            shift
            ;;
        -c|--clean)
            CLEAN="--clean"
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  -p, --profile PROFILE    Conan profile to use (default: linux-gcc11)"
            echo "  -v, --verbose           Verbose output"
            echo "  -c, --clean            Clean before install"
            echo "  -h, --help             Show this help"
            echo ""
            echo "Available profiles:"
            echo "  linux-gcc11, linux-clang15, windows-msvc2022, macos-clang14, debug"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "🚀 Installing Conan dependencies..."
echo "📋 Profile: $PROFILE"

# Check if profile exists
if [ ! -f "conan-dev/profiles/$PROFILE.profile" ]; then
    echo "❌ Profile not found: $PROFILE"
    echo "Available profiles:"
    ls conan-dev/profiles/*.profile | sed 's/.*\\///' | sed 's/\\.profile$//'
    exit 1
fi

# Clean if requested
if [ -n "$CLEAN" ]; then
    echo "🧹 Cleaning previous installation..."
    rm -rf build/ package/
fi

# Install dependencies
echo "📦 Installing dependencies..."
conan install . --profile="$PROFILE" $BUILD_MISSING $VERBOSE $CLEAN

echo "✅ Installation complete!"
echo "💡 Next step: Run './scripts/conan/conan-build' to build the package"
"""

    def _create_conan_build_script(self) -> str:
        """Create conan build script"""
        return """#!/bin/bash
# Conan Build Script - Developer-friendly wrapper

set -e

# Default values
PROFILE="linux-gcc11"
VERBOSE=""
CLEAN=""
TEST=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--profile)
            PROFILE="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE="-v"
            shift
            ;;
        -c|--clean)
            CLEAN="--clean"
            shift
            ;;
        -t|--test)
            TEST="--test"
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  -p, --profile PROFILE    Conan profile to use (default: linux-gcc11)"
            echo "  -v, --verbose           Verbose output"
            echo "  -c, --clean            Clean before build"
            echo "  -t, --test             Run tests after build"
            echo "  -h, --help             Show this help"
            echo ""
            echo "Available profiles:"
            echo "  linux-gcc11, linux-clang15, windows-msvc2022, macos-clang14, debug"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "🔨 Building Conan package..."
echo "📋 Profile: $PROFILE"

# Check if profile exists
if [ ! -f "conan-dev/profiles/$PROFILE.profile" ]; then
    echo "❌ Profile not found: $PROFILE"
    echo "Available profiles:"
    ls conan-dev/profiles/*.profile | sed 's/.*\\///' | sed 's/\\.profile$//'
    exit 1
fi

# Clean if requested
if [ -n "$CLEAN" ]; then
    echo "🧹 Cleaning previous build..."
    rm -rf build/ package/
fi

# Build package
echo "🔨 Building package..."
conan build . --profile="$PROFILE" $VERBOSE $CLEAN

# Run tests if requested
if [ -n "$TEST" ]; then
    echo "🧪 Running tests..."
    conan test test_package openssl/3.5.0@user/channel --profile="$PROFILE" $VERBOSE
fi

echo "✅ Build complete!"
echo "📁 Build artifacts: build/ and package/ directories"
"""

    def _create_dev_setup_script(self) -> str:
        """Create development setup script"""
        return """#!/bin/bash
# Conan Development Setup Script

set -e

echo "🚀 Setting up Conan development environment..."

# Check if we're in the right directory
if [ ! -f "conanfile.py" ]; then
    echo "❌ conanfile.py not found. Please run this script from the project root."
    exit 1
fi

# Install Conan if not present
if ! command -v conan &> /dev/null; then
    echo "📦 Installing Conan..."
    pip install conan
else
    echo "✅ Conan already installed"
fi

# Create symlinks for easy access
echo "🔗 Creating symlinks..."
ln -sf "$(pwd)/scripts/conan/conan-install" /usr/local/bin/conan-install 2>/dev/null || true
ln -sf "$(pwd)/scripts/conan/conan-build" /usr/local/bin/conan-build 2>/dev/null || true

# Set up default profile
echo "⚙️ Setting up default profile..."
conan profile detect --force

# Install dependencies
echo "📦 Installing dependencies..."
./scripts/conan/conan-install

echo "✅ Development environment ready!"
echo ""
echo "🎯 Quick commands:"
echo "  conan-install    - Install dependencies"
echo "  conan-build      - Build package"
echo "  conan-install -p linux-clang15  - Use specific profile"
echo "  conan-build -t   - Build and test"
echo ""
echo "📚 For more options, use: conan-install --help or conan-build --help"
"""

    def _create_configuration_files(self):
        """Create configuration files"""
        configs = {
            "conan.conf": self._create_conan_config(),
            "remotes.txt": self._create_remotes_config(),
            "ci-config.yml": self._create_ci_config(),
        }
        
        for config_name, config_content in configs.items():
            config_path = self.conan_dir / config_name
            with open(config_path, 'w') as f:
                f.write(config_content)
            logger.info(f"⚙️ Created config: {config_name}")
    
    def _create_conan_config(self) -> str:
        """Create Conan configuration"""
        return """[storage]
path = ~/.conan2/data

[remotes]
conancenter = https://center.conan.io

[log]
level = info

[tools]
cmake.cmaketoolchain:generator = Ninja
system.package_manager:mode = install
system.package_manager:sudo = True

[cache]
no_locks = False
"""

    def _create_remotes_config(self) -> str:
        """Create remotes configuration"""
        return """# Conan Remotes Configuration
# Add your custom remotes here

# Default ConanCenter
conancenter = https://center.conan.io

# Example: Custom Artifactory
# myartifactory = https://artifactory.company.com/artifactory/api/conan/conan-local

# Example: Local development
# local = http://localhost:9300
"""

    def _create_ci_config(self) -> str:
        """Create CI configuration"""
        return """# CI/CD Configuration
# This file configures the CI/CD workflows

# Build matrix
profiles:
  - linux-gcc11
  - linux-clang15
  - windows-msvc2022
  - macos-clang14

# Test configuration
test:
  coverage_threshold: 80
  timeout: 300

# Security scanning
security:
  enabled: true
  tools:
    - safety
    - bandit
    - semgrep

# Performance testing
performance:
  enabled: true
  benchmarks:
    - crypto_operations
    - memory_usage
    - build_time

# Release configuration
release:
  auto_tag: true
  create_github_release: true
  upload_to_remote: true
"""

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Set up Conan development environment")
    parser.add_argument("--project-root", type=Path, default=Path.cwd(),
                       help="Project root directory")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Set up environment
    env = ConanDevEnvironment(args.project_root)
    success = env.setup_environment()
    
    if success:
        print("\n🎉 Conan development environment setup complete!")
        print("\n📋 Next steps:")
        print("1. Run: ./scripts/conan/conan-dev-setup")
        print("2. Use: conan-install and conan-build commands")
        print("3. Check: .github/workflows/ for CI/CD automation")
        sys.exit(0)
    else:
        print("\n❌ Setup failed. Check the logs above.")
        sys.exit(1)

if __name__ == "__main__":
    main()