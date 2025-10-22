"""
OpenSSL Testing Tools Package
Provides comprehensive testing utilities and frameworks for OpenSSL ecosystem
"""

import os
from conan import ConanFile
from conan.tools.files import copy
from conan.tools.layout import basic_layout


class OpenSSLTestingConan(ConanFile):
    name = "openssl-testing"
    version = "1.0.0"
    description = "OpenSSL testing utilities, frameworks, and validation tools"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/openssl-tools"
    homepage = "https://github.com/sparesparrow/openssl-tools"
    topics = ("openssl", "testing", "validation", "fips", "crypto")

    # Package settings
    settings = "os", "arch", "compiler", "build_type"
    package_type = "python-require"

    # Export sources
    exports_sources = (
        "openssl_tools/testing/*",
        "scripts/testing/*",
        "tests/*",
        "templates/testing/*",
        "*.md"
    )

    def init(self):
        """Initialize with proper channel"""
        if not os.getenv("CONAN_CHANNEL"):
            self.user = "sparesparrow"
            self.channel = "stable"

    def requirements(self):
        """Testing package depends on foundation"""
        self.requires("openssl-base/1.0.1@sparesparrow/stable")

    def layout(self):
        """Define package layout"""
        basic_layout(self)

    def package(self):
        """Package testing components"""
        # Copy testing modules
        copy(self, "*", src=os.path.join(self.source_folder, "openssl_tools/testing"),
             dst=os.path.join(self.package_folder, "openssl_tools/testing"), keep_path=True)

        # Copy testing scripts
        copy(self, "*", src=os.path.join(self.source_folder, "scripts/testing"),
             dst=os.path.join(self.package_folder, "scripts/testing"), keep_path=True)

        # Copy test templates
        copy(self, "*", src=os.path.join(self.source_folder, "templates/testing"),
             dst=os.path.join(self.package_folder, "templates/testing"), keep_path=True)

        # Copy test files
        copy(self, "*", src=os.path.join(self.source_folder, "tests"),
             dst=os.path.join(self.package_folder, "tests"), keep_path=True)

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
        self.runenv_info.define("OPENSSL_TESTING_ROOT", self.package_folder)
        self.runenv_info.define("OPENSSL_TESTING_MODULES",
                                os.path.join(self.package_folder, "openssl_tools/testing"))

        # Python path for testing modules
        self.runenv_info.prepend_path("PYTHONPATH", os.path.join(self.package_folder, "openssl_tools/testing"))

        # PATH for testing scripts
        self.env_info.PATH.append(os.path.join(self.package_folder, "scripts/testing"))

    def package_id(self):
        """Package ID mode for testing packages"""
        self.info.clear()
