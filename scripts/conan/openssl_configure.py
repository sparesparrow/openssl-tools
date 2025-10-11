#!/usr/bin/env python3
"""
OpenSSL Configuration Module
Wraps OpenSSL Configure with Conan profile integration and platform detection
"""

import os
import sys
import subprocess
import platform
import logging
from pathlib import Path
from typing import Optional, Dict, Any, NamedTuple
from dataclasses import dataclass
import json
import yaml

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ConfigureResult:
    """Result of OpenSSL configuration"""
    success: bool
    config_dir: Optional[str] = None
    profile_used: Optional[str] = None
    configure_command: Optional[str] = None
    error: Optional[str] = None


class OpenSSLConfigurator:
    """OpenSSL configuration manager with Conan integration"""
    
    def __init__(self, conan_api, profile=None, platform=None, compiler=None, 
                 arch=None, build_type="Release", fips=False, shared=True, 
                 static=False, openssl_dir=None, output_dir=None, verbose=False):
        self.conan_api = conan_api
        self.profile = profile
        self.platform = platform or self._detect_platform()
        self.compiler = compiler or self._detect_compiler()
        self.arch = arch or self._detect_arch()
        self.build_type = build_type
        self.fips = fips
        self.shared = shared
        self.static = static
        self.openssl_dir = Path(openssl_dir or "openssl-source")
        self.output_dir = Path(output_dir or f"build-{self.platform}-{self.compiler}")
        self.verbose = verbose
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _detect_platform(self) -> str:
        """Detect the current platform"""
        system = platform.system().lower()
        if system == "linux":
            return "linux"
        elif system == "windows":
            return "windows"
        elif system == "darwin":
            return "macos"
        else:
            return "unknown"
    
    def _detect_compiler(self) -> str:
        """Detect the current compiler"""
        if self.platform == "windows":
            return "msvc"
        elif self.platform == "macos":
            return "clang"
        else:  # linux
            # Try to detect GCC or Clang
            try:
                result = subprocess.run(["gcc", "--version"], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    return "gcc"
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
            
            try:
                result = subprocess.run(["clang", "--version"], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    return "clang"
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
            
            return "gcc"  # Default fallback
    
    def _detect_arch(self) -> str:
        """Detect the current architecture"""
        machine = platform.machine().lower()
        if machine in ["x86_64", "amd64"]:
            return "x86_64"
        elif machine in ["aarch64", "arm64"]:
            return "arm64"
        elif machine in ["armv7l", "armv7"]:
            return "armv7"
        else:
            return machine
    
    def _get_conan_profile(self) -> Optional[str]:
        """Get Conan profile based on platform and compiler"""
        if self.profile:
            return self.profile
        
        # Try to find a matching profile
        profile_dir = Path("conan-profiles")
        if not profile_dir.exists():
            profile_dir = Path("profiles/conan")
        
        if profile_dir.exists():
            # Look for platform-specific profiles
            profile_patterns = [
                f"ci-{self.platform}-{self.compiler}.profile",
                f"{self.platform}-{self.compiler}.profile",
                f"ci-{self.platform}.profile",
                f"{self.platform}.profile"
            ]
            
            for pattern in profile_patterns:
                profile_path = profile_dir / pattern
                if profile_path.exists():
                    return str(profile_path)
        
        return None
    
    def _build_configure_command(self) -> str:
        """Build the OpenSSL Configure command"""
        cmd_parts = []
        
        # Base configure command
        if self.platform == "windows":
            if self.arch == "x86_64":
                cmd_parts.append("perl Configure VC-WIN64A")
            else:
                cmd_parts.append("perl Configure VC-WIN32")
        else:
            # Linux/macOS
            if self.platform == "linux":
                if self.arch == "x86_64":
                    cmd_parts.append("./Configure linux-x86_64")
                elif self.arch == "arm64":
                    cmd_parts.append("./Configure linux-aarch64")
                else:
                    cmd_parts.append(f"./Configure linux-{self.arch}")
            elif self.platform == "macos":
                if self.arch == "x86_64":
                    cmd_parts.append("./Configure darwin64-x86_64-cc")
                elif self.arch == "arm64":
                    cmd_parts.append("./Configure darwin64-arm64-cc")
                else:
                    cmd_parts.append(f"./Configure darwin-{self.arch}-cc")
        
        # Add configuration options
        options = []
        
        # Installation prefix
        prefix = self.output_dir / "install"
        options.append(f"--prefix={prefix}")
        options.append(f"--openssldir={prefix}/ssl")
        
        # Shared/static libraries
        if self.shared:
            options.append("shared")
        if self.static:
            options.append("no-shared")
        
        # Build type specific options
        if self.build_type == "Debug":
            options.append("-g")
            options.append("-O0")
        elif self.build_type == "Release":
            options.append("-O3")
        
        # FIPS mode
        if self.fips:
            options.append("enable-fips")
        
        # Add common options
        options.extend([
            "zlib",
            "no-ssl3",
            "no-weak-ssl-ciphers"
        ])
        
        cmd_parts.extend(options)
        
        return " ".join(cmd_parts)
    
    def configure(self) -> ConfigureResult:
        """Execute OpenSSL configuration"""
        try:
            # Check if OpenSSL source exists
            if not self.openssl_dir.exists():
                return ConfigureResult(
                    success=False,
                    error=f"OpenSSL source directory not found: {self.openssl_dir}"
                )
            
            # Check for Configure script
            configure_script = self.openssl_dir / "Configure"
            if not configure_script.exists():
                return ConfigureResult(
                    success=False,
                    error=f"OpenSSL Configure script not found: {configure_script}"
                )
            
            # Get Conan profile
            profile_path = self._get_conan_profile()
            if profile_path and self.verbose:
                logger.info(f"Using Conan profile: {profile_path}")
            
            # Build configure command
            configure_cmd = self._build_configure_command()
            
            if self.verbose:
                logger.info(f"Configure command: {configure_cmd}")
            
            # Change to OpenSSL source directory
            original_cwd = os.getcwd()
            os.chdir(self.openssl_dir)
            
            try:
                # Execute configure command
                result = subprocess.run(
                    configure_cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
                
                if result.returncode != 0:
                    return ConfigureResult(
                        success=False,
                        error=f"Configure failed: {result.stderr}"
                    )
                
                # Create configuration summary
                config_summary = {
                    "platform": self.platform,
                    "compiler": self.compiler,
                    "arch": self.arch,
                    "build_type": self.build_type,
                    "fips": self.fips,
                    "shared": self.shared,
                    "static": self.static,
                    "configure_command": configure_cmd,
                    "profile_used": profile_path,
                    "output_dir": str(self.output_dir),
                    "openssl_dir": str(self.openssl_dir)
                }
                
                # Save configuration summary
                config_file = self.output_dir / "config.json"
                with open(config_file, 'w') as f:
                    json.dump(config_summary, f, indent=2)
                
                return ConfigureResult(
                    success=True,
                    config_dir=str(self.output_dir),
                    profile_used=profile_path,
                    configure_command=configure_cmd
                )
                
            finally:
                os.chdir(original_cwd)
                
        except subprocess.TimeoutExpired:
            return ConfigureResult(
                success=False,
                error="Configure command timed out after 5 minutes"
            )
        except Exception as e:
            return ConfigureResult(
                success=False,
                error=f"Unexpected error during configuration: {str(e)}"
            )


def main():
    """Main function for standalone execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="OpenSSL Configuration Tool")
    parser.add_argument("--profile", "-p", help="Conan profile to use")
    parser.add_argument("--platform", help="Target platform")
    parser.add_argument("--compiler", help="Compiler to use")
    parser.add_argument("--arch", help="Target architecture")
    parser.add_argument("--build-type", default="Release", help="Build type")
    parser.add_argument("--fips", action="store_true", help="Enable FIPS mode")
    parser.add_argument("--shared", action="store_true", default=True, help="Build shared libraries")
    parser.add_argument("--static", action="store_true", help="Build static libraries")
    parser.add_argument("--openssl-dir", help="OpenSSL source directory")
    parser.add_argument("--output-dir", help="Output directory")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Create configurator
    configurator = OpenSSLConfigurator(
        conan_api=None,  # Not needed for standalone
        profile=args.profile,
        platform=args.platform,
        compiler=args.compiler,
        arch=args.arch,
        build_type=args.build_type,
        fips=args.fips,
        shared=args.shared,
        static=args.static,
        openssl_dir=args.openssl_dir,
        output_dir=args.output_dir,
        verbose=args.verbose
    )
    
    # Execute configuration
    result = configurator.configure()
    
    if result.success:
        print("✅ OpenSSL configuration completed successfully")
        print(f"Configuration directory: {result.config_dir}")
        if result.profile_used:
            print(f"Profile used: {result.profile_used}")
        if args.verbose and result.configure_command:
            print(f"Configure command: {result.configure_command}")
    else:
        print(f"❌ OpenSSL configuration failed: {result.error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
