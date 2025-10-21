"""
OpenSSL Tools Conan Package
Provides build tools, automation scripts, and infrastructure components
"""

from conan import ConanFile
from conan.tools.files import copy, save
from conan.tools.layout import basic_layout
import os
import json
from pathlib import Path

class OpenSSLToolsConan(ConanFile):
    name = "openssl-tools"
    version = "1.2.0"
    description = "OpenSSL build tools, automation scripts, and infrastructure components"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/openssl-tools"
    homepage = "https://github.com/sparesparrow/openssl-tools"
    topics = ("openssl", "build-tools", "automation", "ci-cd")
    
    # Package settings
    package_type = "python-require"
    settings = "os", "arch", "compiler", "build_type"

    # Export Python package sources for python_requires
    exports_sources = "scripts/*", "profiles/*", "docker/*", "templates/*", ".cursor/*", "openssl_tools/**"
    
    def requirements(self):
        # Add foundation dependencies if needed
        pass
    
    def layout(self):
        basic_layout(self)
    
    def package(self):
        # Copy all tools and scripts
        copy(self, "scripts/*", src=self.source_folder, dst=os.path.join(self.package_folder, "scripts"))
        copy(self, "profiles/*", src=self.source_folder, dst=os.path.join(self.package_folder, "profiles"))
        copy(self, "docker/*", src=self.source_folder, dst=os.path.join(self.package_folder, "docker"))
        copy(self, "templates/*", src=self.source_folder, dst=os.path.join(self.package_folder, "templates"))
        copy(self, ".cursor/*", src=self.source_folder, dst=os.path.join(self.package_folder, ".cursor"))
        copy(self, "openssl_tools/**", src=self.source_folder, dst=os.path.join(self.package_folder, "openssl_tools"))
        
        # Copy configuration files
        copy(self, "*.md", src=self.source_folder, dst=self.package_folder)
        copy(self, "pyproject.toml", src=self.source_folder, dst=self.package_folder)
        
        # Create package info
        self._create_package_info()
    
    def _create_package_info(self):
        """Create package information file"""
        package_info = {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "modules": {
                "foundation": ["version_manager", "profile_deployer"],
                "security": ["sbom_generator"],
                "automation": ["conan_orchestrator"],
                "testing": ["quality_manager", "fuzz_manager"],
                "statistics": ["bn_rand_range"],
                "core": ["artifactory_handler"]
            },
            "tools": [
                "docker-build-and-upload.sh",
                "cursor-agents-coordinator.sh",
                "validate-artifactory-packages.sh",
                "generate_sbom.py",
                "dev-setup.sh"
            ],
            "profiles": [
                "linux-gcc11.profile",
                "linux-clang15.profile",
                "windows-msvc2022.profile",
                "macos-arm64.profile",
                "macos-x86_64.profile"
            ]
        }
        
        save(self, os.path.join(self.package_folder, "package_info.json"), 
             json.dumps(package_info, indent=2))
    
    def package_info(self):
        """Define package information for consumers"""
        self.cpp_info.bindirs = ["scripts"]
        self.cpp_info.libdirs = []
        self.cpp_info.includedirs = []
        
        # Set environment variables for tools
        self.runenv_info.define("OPENSSL_TOOLS_ROOT", self.package_folder)
        self.runenv_info.define("OPENSSL_TOOLS_SCRIPTS", os.path.join(self.package_folder, "scripts"))
        self.runenv_info.define("OPENSSL_TOOLS_PROFILES", os.path.join(self.package_folder, "profiles"))
        self.runenv_info.define("OPENSSL_TOOLS_DOCKER", os.path.join(self.package_folder, "docker"))
        self.runenv_info.define("OPENSSL_TOOLS_MODULES", os.path.join(self.package_folder, "openssl_tools"))
        
        # Add to PATH
        self.env_info.PATH.append(os.path.join(self.package_folder, "scripts"))
    
    def build_openssl(self, conanfile):
        """Main build orchestration method"""
        settings = conanfile.settings
        options = conanfile.options
        
        # Platform-specific configure
        config_args = self._get_configure_args(settings, options)
        
        # FIPS support
        if options.get_safe("enable_fips"):
            config_args.append("enable-fips")
        
        conanfile.run(f"perl Configure {' '.join(config_args)}")
        
        # Ninja nebo make
        if self._has_ninja(conanfile):
            conanfile.run("ninja -j")
        else:
            from conan.tools.gnu import Autotools
            autotools = Autotools(conanfile)
            autotools.make(args=["-j"])
    
    def _get_configure_args(self, settings, options):
        args = []
        if settings.os == "Windows":
            args.append("VC-WIN64A" if settings.arch == "x86_64" else "VC-WIN32")
        elif settings.os == "Linux":
            args.append(f"linux-{settings.arch}")
            if options.get_safe("fPIC", True):
                args.append("-fPIC")
        elif settings.os == "Macos":
            args.append(f"darwin64-{settings.arch}")
        return args
    
    def _has_ninja(self, conanfile):
        try:
            conanfile.run("ninja --version", capture=True)
            return True
        except:
            return False