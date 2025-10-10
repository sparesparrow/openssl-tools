#!/usr/bin/env python3
"""
OpenSSL Conan Package Recipe - Integration Test Version
Simplified version for testing basic OpenSSL build integration
"""

from conan import ConanFile
from conan.tools.gnu import AutotoolsToolchain, AutotoolsDeps, Autotools
from conan.tools.files import copy, save, load, chdir
from conan.tools.scm import Git
from conan.tools.system import package_manager
from conan.errors import ConanInvalidConfiguration
import os
import re
import json


class OpenSSLConan(ConanFile):
    name = "openssl"
    version = None  # Dynamically determined from VERSION.dat
    
    # Package metadata
    description = "OpenSSL is a robust, commercial-grade, full-featured toolkit for TLS and SSL protocols"
    homepage = "https://www.openssl.org"
    url = "https://github.com/openssl/openssl"
    license = "Apache-2.0"
    topics = ("ssl", "tls", "cryptography", "security")
    
    # Package configuration - minimal options for testing
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "fips": [True, False],
        "no_asm": [True, False],
        "no_threads": [True, False],
    }
    
    default_options = {
        "shared": True,
        "fPIC": True,
        "fips": False,
        "no_asm": False,
        "no_threads": False,
    }
    
    def set_version(self):
        """Extract version from VERSION.dat"""
        try:
            version_file = os.path.join(self.recipe_folder, "VERSION.dat")
            if os.path.exists(version_file):
                with open(version_file, 'r') as f:
                    content = f.read()
                    # Simple version extraction
                    version_match = re.search(r'MAJOR=(\d+)\s+MINOR=(\d+)\s+PATCH=(\d+)', content)
                    if version_match:
                        major, minor, patch = version_match.groups()
                        self.version = f"{major}.{minor}.{patch}"
                    else:
                        self.version = "3.5.0"  # fallback
            else:
                self.version = "3.5.0"  # fallback
        except Exception as e:
            self.output.warning(f"Could not determine version: {e}")
            self.version = "3.5.0"  # fallback
    
    def configure(self):
        """Configure build options"""
        if not self.options.shared:
            del self.options.fPIC
    
    def build_requirements(self):
        """Specify build requirements"""
        if self.settings.os == "Windows":
            self.tool_requires("nasm/2.16.01")
            self.tool_requires("strawberryperl/5.32.1.1")
        else:
            # Use system perl for Unix-like systems
            pass
    
    def source(self):
        """Source is already available in recipe_folder"""
        pass
    
    def generate(self):
        """Generate build files"""
        tc = AutotoolsToolchain(self)
        tc.generate()
        
        deps = AutotoolsDeps(self)
        deps.generate()
    
    def build(self):
        """Build OpenSSL"""
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()
    
    def package(self):
        """Package OpenSSL"""
        autotools = Autotools(self)
        autotools.install()
    
    def package_info(self):
        """Define package information"""
        self.cpp_info.libs = ["ssl", "crypto"]
        
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["dl", "pthread"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32", "gdi32", "advapi32", "crypt32", "user32"]
        elif self.settings.os == "Macos":
            self.cpp_info.frameworks = ["Security", "CoreFoundation"]