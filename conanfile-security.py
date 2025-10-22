"""
OpenSSL Security Tools Package
Provides SBOM generation, security scanning, and compliance tools
"""

import os
from conan import ConanFile
from conan.tools.files import copy
from conan.tools.layout import basic_layout


class OpenSSLSecurityConan(ConanFile):
    name = "openssl-security"
    version = "1.0.0"
    description = "OpenSSL security tools, SBOM generation, and compliance utilities"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/openssl-tools"
    homepage = "https://github.com/sparesparrow/openssl-tools"
    topics = ("openssl", "security", "sbom", "compliance", "fips", "scanning")

    # Package settings
    settings = "os", "arch", "compiler", "build_type"
    package_type = "python-require"

    # Export sources
    exports_sources = (
        "openssl_tools/security/*",
        "scripts/security/*",
        "templates/security/*",
        "*.md"
    )

    def init(self):
        """Initialize with proper channel"""
        if not os.getenv("CONAN_CHANNEL"):
            self.user = "sparesparrow"
            self.channel = "stable"

    def requirements(self):
        """Security package depends on foundation"""
        self.requires("openssl-base/1.0.1@sparesparrow/stable")

    def layout(self):
        """Define package layout"""
        basic_layout(self)

    def package(self):
        """Package security components"""
        # Copy security modules
        copy(self, "*", src=os.path.join(self.source_folder, "openssl_tools/security"),
             dst=os.path.join(self.package_folder, "openssl_tools/security"), keep_path=True)

        # Copy security scripts
        copy(self, "*", src=os.path.join(self.source_folder, "scripts/security"),
             dst=os.path.join(self.package_folder, "scripts/security"), keep_path=True)

        # Copy security templates
        copy(self, "*", src=os.path.join(self.source_folder, "templates/security"),
             dst=os.path.join(self.package_folder, "templates/security"), keep_path=True)

        # Copy documentation
        copy(self, "README.md", src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "LICENSE*", src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        """Define package information"""
        # No C++ components
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.includedirs = []

        # Environment variables
        self.runenv_info.define("OPENSSL_SECURITY_ROOT", self.package_folder)
        self.runenv_info.define("OPENSSL_SECURITY_MODULES",
                                os.path.join(self.package_folder, "openssl_tools/security"))

        # Python path for security modules
        self.runenv_info.prepend_path("PYTHONPATH", os.path.join(self.package_folder, "openssl_tools/security"))

        # PATH for security scripts
        self.env_info.PATH.append(os.path.join(self.package_folder, "scripts/security"))

    def package_id(self):
        """Package ID mode for security packages"""
        self.info.clear()
