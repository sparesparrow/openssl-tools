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
    version = "1.0.0"
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
        self.requires("openssl-base/1.0.0")
        self.requires("openssl-fips-data/140-3.1")
    
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
        copy(self, ".env.template", src=self.source_folder, dst=self.package_folder)
        copy(self, ".devcontainer/*", src=self.source_folder, dst=os.path.join(self.package_folder, ".devcontainer"))
        
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
        """Define package information for consumers"""
        self.cpp_info.bindirs = ["scripts"]
        self.cpp_info.libdirs = []
        self.cpp_info.includedirs = []
        
        # Set environment variables for tools
        self.runenv_info.define("OPENSSL_TOOLS_ROOT", self.package_folder)
        self.runenv_info.define("OPENSSL_TOOLS_SCRIPTS", os.path.join(self.package_folder, "scripts"))
        self.runenv_info.define("OPENSSL_TOOLS_PROFILES", os.path.join(self.package_folder, "profiles"))
        self.runenv_info.define("OPENSSL_TOOLS_DOCKER", os.path.join(self.package_folder, "docker"))
        self.runenv_info.define("OPENSSL_TOOLS_MCP", os.path.join(self.package_folder, "openssl_tools", "automation", "ai_agents"))
        self.runenv_info.define("OPENSSL_TOOLS_CURSOR_CONFIG", os.path.join(self.package_folder, ".cursor"))
        
        # Add to PATH
        self.env_info.PATH.append(os.path.join(self.package_folder, "scripts"))