from conan import ConanFile
from conan.tools.files import copy
import os

class OpenSSLToolsConan(ConanFile):
    name = "openssl-tools"
    version = "1.2.6"
    description = "OpenSSL build tools, automation scripts, and infrastructure components"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/openssl-tools"
    homepage = "https://github.com/sparesparrow/openssl-tools"
    topics = ("openssl", "build-tools", "automation", "ci-cd")

    # Package settings
    package_type = "python-require"
    # Note: python-require packages should not have settings (binary-agnostic)

    # Export sources
    exports_sources = (
        "scripts/*",
        "templates/*",
        "openssl_tools/**",
        "*.md",
        "pyproject.toml"
    )

    python_requires = "openssl-base/1.0.1@sparesparrow/stable"

    def package(self):
        """Package orchestration components"""
        # Copy Python tools
        copy(self, "**", src=os.path.join(self.source_folder, "openssl_tools"),
             dst=os.path.join(self.package_folder, "openssl_tools"))

        # Copy scripts
        copy(self, "**", src=os.path.join(self.source_folder, "scripts"),
             dst=os.path.join(self.package_folder, "scripts"))

        # Copy templates
        copy(self, "**", src=os.path.join(self.source_folder, "templates"),
             dst=os.path.join(self.package_folder, "templates"))

    def package_info(self):
        """Package information for consumers"""
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        # Environment variables
        self.runenv_info.define("OPENSSL_TOOLS_VERSION", self.version)
        self.runenv_info.define("OPENSSL_TOOLS_ROOT", self.package_folder)

        # Python path
        self.runenv_info.prepend_path("PYTHONPATH", self.package_folder)
