"""
OpenSSL Integration Package
Third-party system integration and interoperability tools
"""

import os
from conan import ConanFile
from conan.tools.files import copy
from conan.tools.layout import basic_layout


class OpenSSLIntegrationConan(ConanFile):
    name = "openssl-integration"
    version = "3.5.2"
    description = "OpenSSL third-party integration and interoperability tools"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/openssl-tools"
    homepage = "https://github.com/sparesparrow/openssl-tools"
    topics = ("openssl", "integration", "interoperability", "third-party", "api")

    # Package settings
    settings = "os", "arch", "compiler", "build_type"
    package_type = "python-require"

    # Integration options
    options = {
        "integrate_with_curl": [True, False],
        "integrate_with_python": [True, False],
        "integrate_with_java": [True, False],
        "integrate_with_dotnet": [True, False],
        "integrate_with_nodejs": [True, False],
        "generate_bindings": [True, False],
        "create_examples": [True, False],
        "validate_interoperability": [True, False],
    }
    default_options = {
        "integrate_with_curl": True,
        "integrate_with_python": True,
        "integrate_with_java": False,
        "integrate_with_dotnet": False,
        "integrate_with_nodejs": False,
        "generate_bindings": True,
        "create_examples": True,
        "validate_interoperability": True,
    }

    # Export sources
    exports_sources = (
        "openssl_tools/integration/*",
        "scripts/integration/*",
        "templates/integration/*",
        "bindings/*",
        "examples/*",
        "interop/*",
        "*.md"
    )

    def init(self):
        """Initialize with proper channel"""
        if not os.getenv("CONAN_CHANNEL"):
            self.user = "sparesparrow"
            self.channel = "stable"

    def requirements(self):
        """Integration package depends on foundation"""
        self.requires("openssl-base/1.0.1@sparesparrow/stable")

    def layout(self):
        """Define package layout"""
        basic_layout(self)

    def package(self):
        """Package integration components"""
        # Copy integration modules
        copy(self, "*", src=os.path.join(self.source_folder, "openssl_tools/integration"),
             dst=os.path.join(self.package_folder, "openssl_tools/integration"), keep_path=True)

        # Copy integration scripts
        copy(self, "*", src=os.path.join(self.source_folder, "scripts/integration"),
             dst=os.path.join(self.package_folder, "scripts/integration"), keep_path=True)

        # Copy integration templates
        copy(self, "*", src=os.path.join(self.source_folder, "templates/integration"),
             dst=os.path.join(self.package_folder, "templates/integration"), keep_path=True)

        # Copy language bindings
        copy(self, "*", src=os.path.join(self.source_folder, "bindings"),
             dst=os.path.join(self.package_folder, "bindings"), keep_path=True)

        # Copy integration examples
        copy(self, "*", src=os.path.join(self.source_folder, "examples"),
             dst=os.path.join(self.package_folder, "examples"), keep_path=True)

        # Copy interoperability tests
        copy(self, "*", src=os.path.join(self.source_folder, "interop"),
             dst=os.path.join(self.package_folder, "interop"), keep_path=True)

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
        self.runenv_info.define("OPENSSL_INTEGRATION_ROOT", self.package_folder)
        self.runenv_info.define("OPENSSL_INTEGRATION_VERSION", self.version)
        self.runenv_info.define("OPENSSL_BINDINGS_PATH",
                                os.path.join(self.package_folder, "bindings"))

        # Feature flags
        if self.options.integrate_with_curl:
            self.runenv_info.define("OPENSSL_INTEGRATE_CURL", "1")
        if self.options.integrate_with_python:
            self.runenv_info.define("OPENSSL_INTEGRATE_PYTHON", "1")
        if self.options.integrate_with_java:
            self.runenv_info.define("OPENSSL_INTEGRATE_JAVA", "1")
        if self.options.integrate_with_dotnet:
            self.runenv_info.define("OPENSSL_INTEGRATE_DOTNET", "1")
        if self.options.integrate_with_nodejs:
            self.runenv_info.define("OPENSSL_INTEGRATE_NODEJS", "1")
        if self.options.generate_bindings:
            self.runenv_info.define("OPENSSL_GENERATE_BINDINGS", "1")
        if self.options.create_examples:
            self.runenv_info.define("OPENSSL_CREATE_EXAMPLES", "1")
        if self.options.validate_interoperability:
            self.runenv_info.define("OPENSSL_VALIDATE_INTEROP", "1")

        # Python path for integration modules
        self.runenv_info.prepend_path("PYTHONPATH", os.path.join(self.package_folder, "openssl_tools/integration"))

        # PATH for integration scripts
        self.env_info.PATH.append(os.path.join(self.package_folder, "scripts/integration"))

    def package_id(self):
        """Package ID mode for integration packages"""
        self.info.clear()
