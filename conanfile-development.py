"""
OpenSSL Development Tools Package
Enhanced developer productivity and development environment tools
"""

import os
from conan import ConanFile
from conan.tools.files import copy
from conan.tools.layout import basic_layout


class OpenSSLDevelopmentConan(ConanFile):
    name = "openssl-development"
    version = "3.5.2"
    description = "OpenSSL development productivity and environment tools"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/openssl-tools"
    homepage = "https://github.com/sparesparrow/openssl-tools"
    topics = ("openssl", "development", "productivity", "ide", "debugging")

    # Package settings
    settings = "os", "arch", "compiler", "build_type"
    package_type = "python-require"

    # Development options
    options = {
        "ide_integration": ["vscode", "clion", "vim", "emacs"],
        "enable_debugging_tools": [True, False],
        "enable_profiling_tools": [True, False],
        "enable_code_coverage": [True, False],
        "generate_cmake_presets": [True, False],
        "enable_hot_reload": [True, False],
        "create_devcontainer": [True, False],
    }
    default_options = {
        "ide_integration": "vscode",
        "enable_debugging_tools": True,
        "enable_profiling_tools": True,
        "enable_code_coverage": False,
        "generate_cmake_presets": True,
        "enable_hot_reload": False,
        "create_devcontainer": True,
    }

    # Export sources
    exports_sources = (
        "openssl_tools/development/*",
        "scripts/development/*",
        "templates/development/*",
        ".vscode/*",
        ".devcontainer/*",
        "cmake/*",
        "*.md"
    )

    def init(self):
        """Initialize with proper channel"""
        if not os.getenv("CONAN_CHANNEL"):
            self.user = "sparesparrow"
            self.channel = "stable"

    def requirements(self):
        """Development package depends on foundation"""
        self.requires("openssl-base/1.0.1@sparesparrow/stable")

    def layout(self):
        """Define package layout"""
        basic_layout(self)

    def package(self):
        """Package development components"""
        # Copy development modules
        copy(self, "*", src=os.path.join(self.source_folder, "openssl_tools/development"),
             dst=os.path.join(self.package_folder, "openssl_tools/development"), keep_path=True)

        # Copy development scripts
        copy(self, "*", src=os.path.join(self.source_folder, "scripts/development"),
             dst=os.path.join(self.package_folder, "scripts/development"), keep_path=True)

        # Copy development templates
        copy(self, "*", src=os.path.join(self.source_folder, "templates/development"),
             dst=os.path.join(self.package_folder, "templates/development"), keep_path=True)

        # Copy IDE configurations
        copy(self, "*", src=os.path.join(self.source_folder, ".vscode"),
             dst=os.path.join(self.package_folder, ".vscode"), keep_path=True)

        # Copy devcontainer configurations
        copy(self, "*", src=os.path.join(self.source_folder, ".devcontainer"),
             dst=os.path.join(self.package_folder, ".devcontainer"), keep_path=True)

        # Copy CMake configurations
        copy(self, "*", src=os.path.join(self.source_folder, "cmake"),
             dst=os.path.join(self.package_folder, "cmake"), keep_path=True)

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
        self.runenv_info.define("OPENSSL_DEVELOPMENT_ROOT", self.package_folder)
        self.runenv_info.define("OPENSSL_IDE_INTEGRATION", self.options.ide_integration)
        self.runenv_info.define("OPENSSL_DEVELOPMENT_VERSION", self.version)

        # Feature flags
        if self.options.enable_debugging_tools:
            self.runenv_info.define("OPENSSL_DEBUGGING_TOOLS", "1")
        if self.options.enable_profiling_tools:
            self.runenv_info.define("OPENSSL_PROFILING_TOOLS", "1")
        if self.options.enable_code_coverage:
            self.runenv_info.define("OPENSSL_CODE_COVERAGE", "1")
        if self.options.generate_cmake_presets:
            self.runenv_info.define("OPENSSL_CMAKE_PRESETS", "1")
        if self.options.enable_hot_reload:
            self.runenv_info.define("OPENSSL_HOT_RELOAD", "1")
        if self.options.create_devcontainer:
            self.runenv_info.define("OPENSSL_DEVCONTAINER", "1")

        # Python path for development modules
        self.runenv_info.prepend_path("PYTHONPATH", os.path.join(self.package_folder, "openssl_tools/development"))

        # PATH for development scripts
        self.env_info.PATH.append(os.path.join(self.package_folder, "scripts/development"))

    def package_id(self):
        """Package ID mode for development packages"""
        self.info.clear()
