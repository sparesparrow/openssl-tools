"""
OpenSSL Pre-Build Hook

This hook runs before the build process starts and prepares the OpenSSL build environment.
It validates dependencies, sets up build configurations, and ensures all prerequisites are met.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional


def run(conanfile, **kwargs) -> None:
    """
    Pre-build hook for OpenSSL packages.
    
    This hook:
    1. Validates OpenSSL source structure
    2. Checks build dependencies
    3. Sets up build environment
    4. Validates Conan profiles
    5. Prepares build configuration
    
    Args:
        conanfile: The ConanFile instance
        **kwargs: Additional keyword arguments
    """
    conanfile.output.info("🔨 OpenSSL Pre-Build Hook: Starting build preparation...")
    
    try:
        # Validate OpenSSL source structure
        _validate_openssl_source(conanfile)
        
        # Check build dependencies
        _check_build_dependencies(conanfile)
        
        # Setup build environment
        _setup_build_environment(conanfile)
        
        # Validate Conan profiles
        _validate_conan_profiles(conanfile)
        
        # Prepare build configuration
        _prepare_build_configuration(conanfile)
        
        conanfile.output.info("✅ OpenSSL Pre-Build Hook: Build preparation completed successfully")
        
    except Exception as e:
        conanfile.output.error(f"❌ OpenSSL Pre-Build Hook failed: {str(e)}")
        raise


def _validate_openssl_source(conanfile) -> None:
    """Validate that OpenSSL source structure is correct."""
    conanfile.output.info("📁 Validating OpenSSL source structure...")
    
    source_folder = getattr(conanfile, 'source_folder', None)
    if not source_folder:
        conanfile.output.warning("⚠️ No source_folder found, skipping source validation")
        return
    
    source_path = Path(source_folder)
    
    # Check for essential OpenSSL files
    essential_files = [
        "VERSION.dat",
        "Configure",
        "config",
        "include/openssl/opensslv.h"
    ]
    
    missing_files = []
    for file_path in essential_files:
        if not (source_path / file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        raise RuntimeError(f"Missing essential OpenSSL files: {', '.join(missing_files)}")
    
    # Check for build system files
    build_systems = ["Makefile", "CMakeLists.txt", "configure"]
    has_build_system = any((source_path / bs).exists() for bs in build_systems)
    
    if not has_build_system:
        raise RuntimeError("No build system found (Makefile, CMakeLists.txt, or configure)")
    
    conanfile.output.info("✅ OpenSSL source structure validation passed")


def _check_build_dependencies(conanfile) -> None:
    """Check that all required build dependencies are available."""
    conanfile.output.info("🔍 Checking build dependencies...")
    
    # Check for required tools
    required_tools = {
        "make": "Make build system",
        "gcc": "GCC compiler",
        "clang": "Clang compiler (alternative)",
        "perl": "Perl interpreter (required for OpenSSL Configure)"
    }
    
    missing_tools = []
    for tool, description in required_tools.items():
        if not _is_tool_available(tool):
            missing_tools.append(f"{tool} ({description})")
    
    if missing_tools:
        conanfile.output.warning(f"⚠️ Missing build tools: {', '.join(missing_tools)}")
        conanfile.output.warning("Some build configurations may not work properly")
    
    # Check Python version for Conan
    python_version = sys.version_info
    if python_version < (3, 7):
        raise RuntimeError(f"Python {python_version.major}.{python_version.minor} is too old. "
                          "OpenSSL Tools requires Python 3.7+")
    
    conanfile.output.info("✅ Build dependencies check completed")


def _is_tool_available(tool_name: str) -> bool:
    """Check if a tool is available in the system PATH."""
    try:
        subprocess.run([tool_name, "--version"], 
                      capture_output=True, 
                      check=True, 
                      timeout=5)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _setup_build_environment(conanfile) -> None:
    """Setup the build environment with necessary variables."""
    conanfile.output.info("🌍 Setting up build environment...")
    
    # Set OpenSSL-specific environment variables
    env_vars = {
        "OPENSSL_CONF": "/dev/null",  # Disable default OpenSSL config
        "OPENSSL_ENGINES": "",        # Clear engines path
        "OPENSSL_MODULES": "",        # Clear modules path
    }
    
    for var, value in env_vars.items():
        os.environ[var] = value
        conanfile.output.info(f"Set {var}={value}")
    
    # Set build-specific environment variables
    if conanfile.settings.os == "Windows":
        # Windows-specific setup
        os.environ["OPENSSL_CONF"] = "NUL"
    elif conanfile.settings.os == "Macos":
        # macOS-specific setup
        os.environ["OPENSSL_CONF"] = "/dev/null"
    
    conanfile.output.info("✅ Build environment setup completed")


def _validate_conan_profiles(conanfile) -> None:
    """Validate Conan profile settings for OpenSSL builds."""
    conanfile.output.info("📋 Validating Conan profile settings...")
    
    # Check required settings
    required_settings = ["os", "arch", "compiler", "build_type"]
    missing_settings = []
    
    for setting in required_settings:
        if not hasattr(conanfile.settings, setting):
            missing_settings.append(setting)
    
    if missing_settings:
        raise RuntimeError(f"Missing required Conan settings: {', '.join(missing_settings)}")
    
    # Validate compiler settings
    compiler = str(conanfile.settings.compiler)
    compiler_version = str(conanfile.settings.compiler.version)
    
    conanfile.output.info(f"Using compiler: {compiler} {compiler_version}")
    
    # Check for supported compiler combinations
    supported_combinations = {
        "Linux": ["gcc", "clang"],
        "Windows": ["msvc", "gcc"],
        "Macos": ["clang", "apple-clang"]
    }
    
    os_name = str(conanfile.settings.os)
    if os_name in supported_combinations:
        if compiler not in supported_combinations[os_name]:
            conanfile.output.warning(f"⚠️ Compiler {compiler} may not be fully supported on {os_name}")
    
    conanfile.output.info("✅ Conan profile validation completed")


def _prepare_build_configuration(conanfile) -> None:
    """Prepare build configuration based on Conan settings."""
    conanfile.output.info("⚙️ Preparing build configuration...")
    
    # Determine build configuration
    build_type = str(conanfile.settings.build_type)
    os_name = str(conanfile.settings.os)
    arch = str(conanfile.settings.arch)
    
    # Set build flags based on configuration
    if build_type == "Debug":
        conanfile.output.info("🔧 Configuring for Debug build")
        os.environ["CFLAGS"] = os.environ.get("CFLAGS", "") + " -g -O0"
    elif build_type == "Release":
        conanfile.output.info("🚀 Configuring for Release build")
        os.environ["CFLAGS"] = os.environ.get("CFLAGS", "") + " -O3 -DNDEBUG"
    elif build_type == "RelWithDebInfo":
        conanfile.output.info("🔍 Configuring for RelWithDebInfo build")
        os.environ["CFLAGS"] = os.environ.get("CFLAGS", "") + " -O2 -g -DNDEBUG"
    
    # Platform-specific configuration
    if os_name == "Windows":
        conanfile.output.info("🪟 Configuring for Windows platform")
        os.environ["CFLAGS"] = os.environ.get("CFLAGS", "") + " -DWIN32_LEAN_AND_MEAN"
    elif os_name == "Linux":
        conanfile.output.info("🐧 Configuring for Linux platform")
        os.environ["CFLAGS"] = os.environ.get("CFLAGS", "") + " -D_GNU_SOURCE"
    elif os_name == "Macos":
        conanfile.output.info("🍎 Configuring for macOS platform")
        os.environ["CFLAGS"] = os.environ.get("CFLAGS", "") + " -D_DARWIN_C_SOURCE"
    
    # Architecture-specific configuration
    if arch == "x86_64":
        conanfile.output.info("🏗️ Configuring for x86_64 architecture")
    elif arch == "armv8":
        conanfile.output.info("🏗️ Configuring for ARM64 architecture")
    
    conanfile.output.info("✅ Build configuration preparation completed")
