"""
OpenSSL Tools Python Requires Package
Provides shared utilities and base classes for OpenSSL development tools
"""

from conan import ConanFile
from conan.tools.files import copy, save
from conan.tools.layout import basic_layout
import os
import json
from pathlib import Path

class OpenSSLToolsConan(ConanFile):
    name = "openssl-tools"
    version = "0.1.0"
    description = "Shared utilities and base classes for OpenSSL development tools"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/openssl-tools"
    homepage = "https://github.com/sparesparrow/openssl-tools"
    topics = ("openssl", "python-requires", "utilities", "ci-cd")

    # Python requires package
    package_type = "python-require"

    # Export Python source code for consumption
    exports_sources = "openssl_tools/foundation/*", "openssl_tools/core/*", "openssl_tools/util/*"
    
    def layout(self):
        basic_layout(self)
    
    def package(self):
        # Copy Python utilities for python_requires consumption
        copy(self, "openssl_tools/foundation/*", src=self.source_folder, dst=os.path.join(self.package_folder, "openssl_tools", "foundation"))
        copy(self, "openssl_tools/core/*", src=self.source_folder, dst=os.path.join(self.package_folder, "openssl_tools", "core"))
        copy(self, "openssl_tools/util/*", src=self.source_folder, dst=os.path.join(self.package_folder, "openssl_tools", "util"))

        # Create package info
        self._create_package_info()
    
    def _create_package_info(self):
        """Create package information file"""
        package_info = {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "tools": [
                "docker-build-and-upload.sh",
                "cursor-agents-coordinator.sh",
                "validate-artifactory-packages.sh",
                "generate_sbom.py",
                "dev-setup.sh"
            ],
            "mcp_servers": [
                "database_server.py",
                "build_server.py",
                "security_server.py",
                "ci_server.py",
                "workflow_fixer.py"
            ],
            "profiles": [
                "ubuntu-20.04.profile",
                "ubuntu-22.04.profile",
                "windows-msvc2022.profile",
                "macos-arm64.profile",
                "macos-x86_64.profile"
            ],
            "docker_services": [
                "ubuntu-20-04-gcc",
                "ubuntu-22-04-clang",
                "windows-2022",
                "macos-x86_64",
                "macos-arm64"
            ],
            "github_actions": [
                "setup-openssl-build",
                "run-openssl-tests"
            ]
        }
        
        save(self, os.path.join(self.package_folder, "package_info.json"), 
             json.dumps(package_info, indent=2))
    
    def package_info(self):
        """Define package information for python_requires consumers"""
        # Add Python modules to Python path for importing
        self.runenv_info.define("PYTHONPATH", self.package_folder)

        # Set environment variables for utilities
        self.runenv_info.define("OPENSSL_TOOLS_ROOT", self.package_folder)
        self.runenv_info.define("OPENSSL_TOOLS_FOUNDATION", os.path.join(self.package_folder, "openssl_tools", "foundation"))
        self.runenv_info.define("OPENSSL_TOOLS_CORE", os.path.join(self.package_folder, "openssl_tools", "core"))
        self.runenv_info.define("OPENSSL_TOOLS_UTIL", os.path.join(self.package_folder, "openssl_tools", "util"))