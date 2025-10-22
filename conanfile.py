"""
OpenSSL Tools Conan Package
Build orchestration and Python utilities for OpenSSL ecosystem
"""

from conan import ConanFile
from conan.tools.files import copy
import os

class OpenSSLToolsConan(ConanFile):
    name = "openssl-tools"
    version = "1.2.4"
    description = "OpenSSL build tools, automation scripts, and infrastructure components"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/openssl-tools"
    homepage = "https://github.com/sparesparrow/openssl-tools"
    topics = ("openssl", "build-tools", "automation", "ci-cd")

    # Package settings
    package_type = "python-require"
    settings = "os", "arch", "compiler", "build_type"

    # Export sources
    exports_sources = (
        "scripts/*",
        "profiles/*",
        "templates/*",
        "openssl_tools/**",
        "*.md",
        "pyproject.toml"
    )

    def requirements(self):
        """Require foundation packages only"""
        # Foundation packages
        self.requires("openssl-profiles/2.0.0")

    def package(self):
        """Package orchestration components"""
        # Copy Python tools
        copy(self, "*.py", src="openssl_tools", dst=os.path.join(self.package_folder, "openssl_tools"))

        # Copy scripts
        copy(self, "*.sh", src="scripts", dst=os.path.join(self.package_folder, "scripts"))
        copy(self, "*.py", src="scripts", dst=os.path.join(self.package_folder, "scripts"))

        # Copy profiles
        copy(self, "*.profile", src="profiles", dst=os.path.join(self.package_folder, "profiles"))

        # Copy templates
        copy(self, "*", src="templates", dst=os.path.join(self.package_folder, "templates"))

    def package_info(self):
        """Package information for consumers"""
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        # Environment variables
        self.runenv_info.define("OPENSSL_TOOLS_VERSION", self.version)
        self.runenv_info.define("OPENSSL_TOOLS_ROOT", self.package_folder)

        # Python path
        self.runenv_info.prepend_path("PYTHONPATH", self.package_folder)
