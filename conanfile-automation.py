"""
OpenSSL Automation Package
Provides CI/CD automation, build orchestration, and deployment tools
"""

import os
from conan import ConanFile
from conan.tools.files import copy
from conan.tools.layout import basic_layout


class OpenSSLAutomationConan(ConanFile):
    name = "openssl-automation"
    version = "1.0.0"
    description = "OpenSSL CI/CD automation, build orchestration, and deployment tools"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/openssl-tools"
    homepage = "https://github.com/sparesparrow/openssl-tools"
    topics = ("openssl", "automation", "ci-cd", "deployment", "build")

    # Package settings
    settings = "os", "arch", "compiler", "build_type"
    package_type = "python-require"

    # Export sources
    exports_sources = (
        "openssl_tools/automation/*",
        "scripts/automation/*",
        "templates/automation/*",
        "docker/*",
        "*.md"
    )

    def init(self):
        """Initialize with proper channel"""
        if not os.getenv("CONAN_CHANNEL"):
            self.user = "sparesparrow"
            self.channel = "stable"

    def requirements(self):
        """Automation package depends on foundation"""
        self.requires("openssl-base/1.0.1@sparesparrow/stable")

    def layout(self):
        """Define package layout"""
        basic_layout(self)

    def package(self):
        """Package automation components"""
        # Copy automation modules
        copy(self, "*", src=os.path.join(self.source_folder, "openssl_tools/automation"),
             dst=os.path.join(self.package_folder, "openssl_tools/automation"), keep_path=True)

        # Copy automation scripts
        copy(self, "*", src=os.path.join(self.source_folder, "scripts/automation"),
             dst=os.path.join(self.package_folder, "scripts/automation"), keep_path=True)

        # Copy automation templates
        copy(self, "*", src=os.path.join(self.source_folder, "templates/automation"),
             dst=os.path.join(self.package_folder, "templates/automation"), keep_path=True)

        # Copy Docker configurations
        copy(self, "*", src=os.path.join(self.source_folder, "docker"),
             dst=os.path.join(self.package_folder, "docker"), keep_path=True)

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
        self.runenv_info.define("OPENSSL_AUTOMATION_ROOT", self.package_folder)
        self.runenv_info.define("OPENSSL_AUTOMATION_MODULES",
                                os.path.join(self.package_folder, "openssl_tools/automation"))

        # Python path for automation modules
        self.runenv_info.prepend_path("PYTHONPATH", os.path.join(self.package_folder, "openssl_tools/automation"))

        # PATH for automation scripts
        self.env_info.PATH.append(os.path.join(self.package_folder, "scripts/automation"))

    def package_id(self):
        """Package ID mode for automation packages"""
        self.info.clear()
