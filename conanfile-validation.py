"""
OpenSSL Validation Package
Provides quality assurance, validation, and compliance checking tools
"""

import os
from conan import ConanFile
from conan.tools.files import copy
from conan.tools.layout import basic_layout


class OpenSSLValidationConan(ConanFile):
    name = "openssl-validation"
    version = "1.0.0"
    description = "OpenSSL validation, QA, and compliance checking tools"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/openssl-tools"
    homepage = "https://github.com/sparesparrow/openssl-tools"
    topics = ("openssl", "validation", "qa", "compliance", "quality")

    # Package settings
    settings = "os", "arch", "compiler", "build_type"
    package_type = "python-require"

    # Export sources
    exports_sources = (
        "openssl_tools/validation/*",
        "scripts/validation/*",
        "templates/validation/*",
        "*.md"
    )

    def init(self):
        """Initialize with proper channel"""
        if not os.getenv("CONAN_CHANNEL"):
            self.user = "sparesparrow"
            self.channel = "stable"

    def requirements(self):
        """Validation package depends on foundation and security"""
        self.requires("openssl-base/1.0.1@sparesparrow/stable")
        self.requires("openssl-security/1.0.0@sparesparrow/stable")

    def layout(self):
        """Define package layout"""
        basic_layout(self)

    def package(self):
        """Package validation components"""
        # Copy validation modules
        copy(self, "*", src=os.path.join(self.source_folder, "openssl_tools/validation"),
             dst=os.path.join(self.package_folder, "openssl_tools/validation"), keep_path=True)

        # Copy validation scripts
        copy(self, "*", src=os.path.join(self.source_folder, "scripts/validation"),
             dst=os.path.join(self.package_folder, "scripts/validation"), keep_path=True)

        # Copy validation templates
        copy(self, "*", src=os.path.join(self.source_folder, "templates/validation"),
             dst=os.path.join(self.package_folder, "templates/validation"), keep_path=True)

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
        self.runenv_info.define("OPENSSL_VALIDATION_ROOT", self.package_folder)
        self.runenv_info.define("OPENSSL_VALIDATION_MODULES",
                                os.path.join(self.package_folder, "openssl_tools/validation"))

        # Python path for validation modules
        self.runenv_info.prepend_path("PYTHONPATH", os.path.join(self.package_folder, "openssl_tools/validation"))

        # PATH for validation scripts
        self.env_info.PATH.append(os.path.join(self.package_folder, "scripts/validation"))

    def package_id(self):
        """Package ID mode for validation packages"""
        self.info.clear()
