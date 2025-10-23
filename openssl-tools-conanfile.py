from conan import ConanFile
from conan.tools.files import copy, save, load
from conan.tools.cmake import cmake_layout
import os
import json
import shutil
import subprocess
from pathlib import Path

# Import vcpkg integration modules
try:
    from openssl_tools.vcpkg import VcpkgDetector, VcpkgManager, VcpkgIntegration
    from openssl_tools.build import OpenSSLBuildManager
except ImportError:
    # Fallback if modules not available
    VcpkgDetector = None
    VcpkgManager = None
    VcpkgIntegration = None
    OpenSSLBuildManager = None

class OpenSSLToolsConan(ConanFile):
    name = "openssl-tools"
    version = "1.3.0"  # Updated version
    description = "OpenSSL build tools with vcpkg integration"
    license = "Apache-2.0"
    package_type = "python-require"
    
    # Settings for vcpkg integration detection
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "vcpkg_integration": [True, False],
        "fips_mode": [True, False],
        "prefer_vcpkg": [True, False]
    }
    default_options = {
        "vcpkg_integration": True,
        "fips_mode": False,
        "prefer_vcpkg": False
    }

    exports_sources = (
        "scripts/*",
        "templates/*", 
        "openssl_tools/*",
        "vcpkg/*",        # New vcpkg integration files
        "*.md",
        "pyproject.toml"
    )

    python_requires = "openssl-profiles/2.0.1"

    def layout(self):
        cmake_layout(self)

    def configure(self):
        # Auto-detect vcpkg if available
        if self.options.vcpkg_integration:
            vcpkg_root = self._detect_vcpkg_root()
            if vcpkg_root:
                self.output.info(f"✅ vcpkg detected at: {vcpkg_root}")
                self.options.prefer_vcpkg = True
            else:
                self.output.warning("⚠️ vcpkg not found - using Conan packages")
                self.options.prefer_vcpkg = False

    def _detect_vcpkg_root(self):
        """Detect vcpkg installation root"""
        # Check common vcpkg locations
        possible_paths = [
            os.path.expanduser("~/vcpkg"),
            os.path.expanduser("~/.vcpkg"),
            "/usr/local/vcpkg",
            "/opt/vcpkg",
            "C:/vcpkg",
            "C:/tools/vcpkg"
        ]
        
        # Check VCPKG_ROOT environment variable
        vcpkg_root = os.getenv("VCPKG_ROOT")
        if vcpkg_root and os.path.exists(vcpkg_root):
            return vcpkg_root
            
        # Check VCPKG_INSTALLATION_ROOT environment variable
        vcpkg_root = os.getenv("VCPKG_INSTALLATION_ROOT")
        if vcpkg_root and os.path.exists(vcpkg_root):
            return vcpkg_root
        
        # Check common installation paths
        for path in possible_paths:
            if os.path.exists(path) and os.path.exists(os.path.join(path, "vcpkg")):
                return path
                
        return None

    def _get_vcpkg_triplet(self):
        """Generate vcpkg triplet from Conan settings"""
        os_map = {
            "Windows": "windows",
            "Linux": "linux", 
            "Macos": "osx"
        }
        
        arch_map = {
            "x86_64": "x64",
            "x86": "x86",
            "armv8": "arm64",
            "armv7": "arm"
        }
        
        os_name = os_map.get(str(self.settings.os), "linux")
        arch_name = arch_map.get(str(self.settings.arch), "x64")
        
        # Handle static/shared linking
        if self.settings.os == "Windows":
            if self.settings.build_type == "Debug":
                return f"{os_name}-{arch_name}-debug"
            else:
                return f"{os_name}-{arch_name}"
        else:
            return f"{os_name}-{arch_name}"

    def _generate_vcpkg_manifest(self):
        """Generate vcpkg.json manifest for OpenSSL dependencies"""
        manifest = {
            "name": "openssl-tools-deps",
            "version": "1.0.0",
            "description": "OpenSSL build dependencies via vcpkg",
            "dependencies": [
                {
                    "name": "openssl",
                    "features": ["tools"]
                },
                {
                    "name": "zlib"
                }
            ]
        }
        
        # Add FIPS-specific dependencies if enabled
        if self.options.fips_mode:
            manifest["dependencies"].extend([
                {
                    "name": "openssl",
                    "features": ["fips"]
                }
            ])
        
        return manifest

    def _setup_vcpkg_environment(self):
        """Setup vcpkg environment variables and paths"""
        vcpkg_root = self._detect_vcpkg_root()
        if not vcpkg_root:
            return {}
            
        triplet = self._get_vcpkg_triplet()
        
        env_vars = {
            "VCPKG_ROOT": vcpkg_root,
            "VCPKG_DEFAULT_TRIPLET": triplet,
            "VCPKG_DEFAULT_HOST_TRIPLET": triplet,
            "CMAKE_TOOLCHAIN_FILE": os.path.join(vcpkg_root, "scripts", "buildsystems", "vcpkg.cmake")
        }
        
        # Add vcpkg to PATH
        vcpkg_bin = os.path.join(vcpkg_root, "vcpkg")
        if os.path.exists(vcpkg_bin):
            current_path = os.environ.get("PATH", "")
            env_vars["PATH"] = f"{os.path.dirname(vcpkg_bin)}:{current_path}"
            
        return env_vars

    def _install_vcpkg_dependencies(self):
        """Install OpenSSL dependencies via vcpkg"""
        vcpkg_root = self._detect_vcpkg_root()
        if not vcpkg_root:
            self.output.warning("vcpkg not available - skipping vcpkg installation")
            return False
            
        try:
            # Generate manifest
            manifest = self._generate_vcpkg_manifest()
            manifest_path = os.path.join(self.build_folder, "vcpkg.json")
            with open(manifest_path, 'w') as f:
                json.dump(manifest, f, indent=2)
            
            # Install dependencies
            triplet = self._get_vcpkg_triplet()
            vcpkg_cmd = [
                os.path.join(vcpkg_root, "vcpkg"),
                "install",
                f"--triplet={triplet}",
                "--manifest-root", self.build_folder
            ]
            
            self.output.info(f"Installing vcpkg dependencies: {' '.join(vcpkg_cmd)}")
            result = subprocess.run(vcpkg_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.output.info("✅ vcpkg dependencies installed successfully")
                return True
            else:
                self.output.warning(f"vcpkg installation failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.output.warning(f"vcpkg installation error: {e}")
            return False

    def build(self):
        """Build OpenSSL tools with vcpkg integration"""
        if self.options.vcpkg_integration and self.options.prefer_vcpkg:
            # Try vcpkg first
            if self._install_vcpkg_dependencies():
                self.output.info("Using vcpkg for OpenSSL dependencies")
                self._setup_vcpkg_build()
            else:
                self.output.info("Falling back to Conan packages")
                self._setup_conan_build()
        else:
            self._setup_conan_build()

    def _setup_vcpkg_build(self):
        """Setup build environment for vcpkg integration"""
        env_vars = self._setup_vcpkg_environment()
        
        # Save environment for use in package_info
        self._vcpkg_env = env_vars
        self._vcpkg_triplet = self._get_vcpkg_triplet()
        
        # Generate vcpkg integration scripts
        self._generate_vcpkg_integration_scripts()

    def _setup_conan_build(self):
        """Setup build environment for Conan packages"""
        # Standard Conan build setup
        self._vcpkg_env = {}
        self._vcpkg_triplet = None

    def _generate_vcpkg_integration_scripts(self):
        """Generate helper scripts for vcpkg integration"""
        scripts_dir = os.path.join(self.package_folder, "scripts", "vcpkg")
        os.makedirs(scripts_dir, exist_ok=True)
        
        # Generate CMake integration script
        cmake_script = f"""# vcpkg integration for OpenSSL
set(VCPKG_ROOT "{self._detect_vcpkg_root()}")
set(VCPKG_DEFAULT_TRIPLET "{self._vcpkg_triplet}")
set(CMAKE_TOOLCHAIN_FILE "${{VCPKG_ROOT}}/scripts/buildsystems/vcpkg.cmake")

# Find OpenSSL via vcpkg
find_package(OpenSSL REQUIRED)
"""
        
        with open(os.path.join(scripts_dir, "vcpkg-openssl.cmake"), 'w') as f:
            f.write(cmake_script)
        
        # Generate environment setup script
        env_script = f"""#!/bin/bash
# vcpkg environment setup for OpenSSL
export VCPKG_ROOT="{self._detect_vcpkg_root()}"
export VCPKG_DEFAULT_TRIPLET="{self._vcpkg_triplet}"
export CMAKE_TOOLCHAIN_FILE="${{VCPKG_ROOT}}/scripts/buildsystems/vcpkg.cmake"
"""
        
        env_script_path = os.path.join(scripts_dir, "setup-vcpkg-env.sh")
        with open(env_script_path, 'w') as f:
            f.write(env_script)
        
        # Make executable
        os.chmod(env_script_path, 0o755)

    def package(self):
        """Package OpenSSL tools with vcpkg integration"""
        # Copy Python package
        if os.path.exists("openssl_tools"):
            copy(self, "openssl_tools/*", src=".", dst=self.package_folder)
        
        # Copy scripts
        if os.path.exists("scripts"):
            copy(self, "scripts/*", src=".", dst=self.package_folder)
        
        # Copy templates
        if os.path.exists("templates"):
            copy(self, "templates/*", src=".", dst=self.package_folder)
        
        # Copy vcpkg integration files
        if os.path.exists("vcpkg"):
            copy(self, "vcpkg/*", src=".", dst=self.package_folder)
        
        # Generate vcpkg integration if enabled
        if self.options.vcpkg_integration:
            self._generate_vcpkg_integration_scripts()
        
        # Save configuration
        config = {
            "vcpkg_integration": bool(self.options.vcpkg_integration),
            "fips_mode": bool(self.options.fips_mode),
            "prefer_vcpkg": bool(self.options.prefer_vcpkg),
            "vcpkg_root": self._detect_vcpkg_root(),
            "vcpkg_triplet": self._vcpkg_triplet
        }
        
        config_path = os.path.join(self.package_folder, "openssl_tools_config.json")
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

    def package_info(self):
        """Configure package information for vcpkg integration"""
        # Set environment variables for vcpkg integration
        if self.options.vcpkg_integration and hasattr(self, '_vcpkg_env'):
            for key, value in self._vcpkg_env.items():
                self.env_info.define(key, value)
        
        # Set Python path for openssl_tools
        self.env_info.PYTHONPATH.append(os.path.join(self.package_folder, "openssl_tools"))
        
        # Set build system information
        self.user_info.vcpkg_integration = str(self.options.vcpkg_integration)
        self.user_info.fips_mode = str(self.options.fips_mode)
        self.user_info.prefer_vcpkg = str(self.options.prefer_vcpkg)
        
        if hasattr(self, '_vcpkg_triplet') and self._vcpkg_triplet:
            self.user_info.vcpkg_triplet = self._vcpkg_triplet