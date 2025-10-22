"""
OpenSSL Legacy Compatibility Package
Backward compatibility layers and deprecated API support
"""

import os
from conan import ConanFile
from conan.tools.files import copy
from conan.tools.layout import basic_layout


class OpenSSLLegacyCompatibilityConan(ConanFile):
    name = "openssl-legacy-compatibility"
    version = "3.5.2"
    description = "OpenSSL legacy compatibility layers and deprecated API support"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/openssl-tools"
    homepage = "https://github.com/sparesparrow/openssl-tools"
    topics = ("openssl", "legacy", "compatibility", "deprecated", "migration")

    # Package settings
    settings = "os", "arch", "compiler", "build_type"
    package_type = "python-require"

    # Legacy compatibility options
    options = {
        "support_openssl_1_1": [True, False],
        "support_openssl_1_0": [True, False],
        "support_openssl_0_9": [True, False],
        "generate_shim_libraries": [True, False],
        "enable_deprecated_warnings": [True, False],
        "create_compatibility_report": [True, False],
        "validate_compatibility": [True, False],
        "legacy_api_version": ["1.1.1", "1.0.2", "0.9.8"],
    }
    default_options = {
        "support_openssl_1_1": True,
        "support_openssl_1_0": False,
        "support_openssl_0_9": False,
        "generate_shim_libraries": True,
        "enable_deprecated_warnings": True,
        "create_compatibility_report": True,
        "validate_compatibility": True,
        "legacy_api_version": "1.1.1",
    }

    # Export sources
    exports_sources = (
        "openssl_tools/legacy_compatibility/*",
        "compatibility/*",
        "shims/*",
        "legacy/*",
        "deprecated/*",
        "*.md"
    )

    def init(self):
        """Initialize with proper channel"""
        if not os.getenv("CONAN_CHANNEL"):
            self.user = "sparesparrow"
            self.channel = "stable"

    def requirements(self):
        """Legacy compatibility depends on foundation and migration"""
        self.requires("openssl-base/1.0.1@sparesparrow/stable")
        self.requires("openssl-migration/3.5.2@sparesparrow/stable")

    def layout(self):
        """Define package layout"""
        basic_layout(self)

    def package(self):
        """Package legacy compatibility components"""
        # Copy legacy compatibility modules
        copy(self, "*", src=os.path.join(self.source_folder, "openssl_tools/legacy_compatibility"),
             dst=os.path.join(self.package_folder, "openssl_tools/legacy_compatibility"), keep_path=True)

        # Copy compatibility layers
        copy(self, "*", src=os.path.join(self.source_folder, "compatibility"),
             dst=os.path.join(self.package_folder, "compatibility"), keep_path=True)

        # Copy shim libraries
        copy(self, "*", src=os.path.join(self.source_folder, "shims"),
             dst=os.path.join(self.package_folder, "shims"), keep_path=True)

        # Copy legacy API implementations
        copy(self, "*", src=os.path.join(self.source_folder, "legacy"),
             dst=os.path.join(self.package_folder, "legacy"), keep_path=True)

        # Copy deprecated API support
        copy(self, "*", src=os.path.join(self.source_folder, "deprecated"),
             dst=os.path.join(self.package_folder, "deprecated"), keep_path=True)

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
        self.runenv_info.define("OPENSSL_LEGACY_ROOT", self.package_folder)
        self.runenv_info.define("OPENSSL_LEGACY_VERSION", self.version)
        self.runenv_info.define("OPENSSL_LEGACY_API", self.options.legacy_api_version)

        # Legacy support flags
        if self.options.support_openssl_1_1:
            self.runenv_info.define("OPENSSL_SUPPORT_1_1", "1")
        if self.options.support_openssl_1_0:
            self.runenv_info.define("OPENSSL_SUPPORT_1_0", "1")
        if self.options.support_openssl_0_9:
            self.runenv_info.define("OPENSSL_SUPPORT_0_9", "1")
        if self.options.generate_shim_libraries:
            self.runenv_info.define("OPENSSL_SHIM_LIBRARIES", "1")
        if self.options.enable_deprecated_warnings:
            self.runenv_info.define("OPENSSL_DEPRECATED_WARNINGS", "1")
        if self.options.create_compatibility_report:
            self.runenv_info.define("OPENSSL_COMPATIBILITY_REPORT", "1")
        if self.options.validate_compatibility:
            self.runenv_info.define("OPENSSL_COMPATIBILITY_VALIDATION", "1")

        # Python path for legacy compatibility modules
        self.runenv_info.prepend_path("PYTHONPATH", os.path.join(self.package_folder, "openssl_tools/legacy_compatibility"))

        # PATH for legacy compatibility scripts
        self.env_info.PATH.append(os.path.join(self.package_folder, "legacy"))

    def package_id(self):
        """Package ID mode for legacy compatibility packages"""
        self.info.clear()
