from conan import ConanFile
from conan.tools.files import copy
import os
import subprocess
import re

class OpenSSLToolsConan(ConanFile):
    name = "openssl-tools"

    def set_version(self):
        """Dynamic version management from git tags"""
        try:
            git_version = subprocess.check_output(
                ['git', 'describe', '--tags', '--always'],
                cwd=self.recipe_folder
            ).decode().strip()

            if '-' in git_version:
                # Format: v1.2.6-3-g1234567 -> 1.2.6.3
                base_version = git_version.split('-')[0].lstrip('v')
                commit_count = git_version.split('-')[1]
                self.version = f"{base_version}.{commit_count}"
            else:
                # Clean tag: v1.2.6 -> 1.2.6
                self.version = git_version.lstrip('v')
        except subprocess.CalledProcessError:
            self.version = "1.2.7-dev"
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

    # Base dependency for shared functionality
    python_requires = "openssl-base/1.0.1@sparesparrow/stable"

    def export(self):
        """Export Python modules for python_requires consumers"""
        # Export conan utility functions
        copy(self, "scripts/conan/*.py",
             src=self.source_folder,
             dst=os.path.join(self.export_folder, "scripts/conan"))

        # Export logging utilities
        copy(self, "openssl_tools/util/*.py",
             src=self.source_folder,
             dst=os.path.join(self.export_folder, "openssl_tools/util"))

        # Export artifactory handlers
        copy(self, "openssl_tools/core/*.py",
             src=self.source_folder,
             dst=os.path.join(self.export_folder, "openssl_tools/core"))

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

        # Python path for imports
        self.runenv_info.prepend_path("PYTHONPATH", self.package_folder)

        # Expose key modules for python_requires consumers
        self.python_requires_info.modules = {
            "conan_functions": "scripts.conan.conan_functions",
            "logging_setup": "openssl_tools.util.custom_logging",
            "artifactory": "openssl_tools.core.artifactory_handler"
        }
