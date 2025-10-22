"""
OpenSSL Cross-Compilation Package
Enhanced cross-platform compilation tools and configurations
"""

import os
from conan import ConanFile
from conan.tools.files import copy
from conan.tools.layout import basic_layout


class OpenSSLCrossCompilationConan(ConanFile):
    name = "openssl-cross-compilation"
    version = "3.5.2"
    description = "OpenSSL cross-platform compilation and toolchain management"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/openssl-tools"
    homepage = "https://github.com/sparesparrow/openssl-tools"
    topics = ("openssl", "cross-compilation", "toolchain", "multiplatform", "embedded")

    # Package settings
    settings = "os", "arch", "compiler", "build_type"
    package_type = "python-require"

    # Cross-compilation options
    options = {
        "target_architectures": ["armv7", "armv8", "x86", "x86_64", "mips", "powerpc"],
        "target_os": ["linux", "windows", "macos", "android", "ios", "baremetal"],
        "enable_embedded": [True, False],
        "generate_toolchains": [True, False],
        "enable_static_analysis": [True, False],
        "optimize_for_size": [True, False],
        "enable_debug_symbols": [True, False],
    }
    default_options = {
        "target_architectures": "x86_64",
        "target_os": "linux",
        "enable_embedded": False,
        "generate_toolchains": True,
        "enable_static_analysis": True,
        "optimize_for_size": False,
        "enable_debug_symbols": True,
    }

    # Export sources
    exports_sources = (
        "openssl_tools/cross_compilation/*",
        "toolchains/*",
        "cross-profiles/*",
        "embedded/*",
        "*.md"
    )

    def init(self):
        """Initialize with proper channel"""
        if not os.getenv("CONAN_CHANNEL"):
            self.user = "sparesparrow"
            self.channel = "stable"

    def requirements(self):
        """Cross-compilation package depends on foundation and optimization"""
        self.requires("openssl-base/1.0.1@sparesparrow/stable")
        self.requires("openssl-optimization/3.5.2@sparesparrow/stable")

    def layout(self):
        """Define package layout"""
        basic_layout(self)

    def package(self):
        """Package cross-compilation components"""
        # Copy cross-compilation modules
        copy(self, "*", src=os.path.join(self.source_folder, "openssl_tools/cross_compilation"),
             dst=os.path.join(self.package_folder, "openssl_tools/cross_compilation"), keep_path=True)

        # Copy toolchains
        copy(self, "*", src=os.path.join(self.source_folder, "toolchains"),
             dst=os.path.join(self.package_folder, "toolchains"), keep_path=True)

        # Copy cross-compilation profiles
        copy(self, "*", src=os.path.join(self.source_folder, "cross-profiles"),
             dst=os.path.join(self.package_folder, "cross-profiles"), keep_path=True)

        # Copy embedded configurations
        copy(self, "*", src=os.path.join(self.source_folder, "embedded"),
             dst=os.path.join(self.package_folder, "embedded"), keep_path=True)

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
        self.runenv_info.define("OPENSSL_CROSS_ROOT", self.package_folder)
        self.runenv_info.define("OPENSSL_TARGET_ARCH", self.options.target_architectures)
        self.runenv_info.define("OPENSSL_TARGET_OS", self.options.target_os)
        self.runenv_info.define("OPENSSL_CROSS_VERSION", self.version)

        # Feature flags
        if self.options.enable_embedded:
            self.runenv_info.define("OPENSSL_EMBEDDED", "1")
        if self.options.generate_toolchains:
            self.runenv_info.define("OPENSSL_GENERATE_TOOLCHAINS", "1")
        if self.options.enable_static_analysis:
            self.runenv_info.define("OPENSSL_STATIC_ANALYSIS", "1")
        if self.options.optimize_for_size:
            self.runenv_info.define("OPENSSL_OPTIMIZE_SIZE", "1")
        if self.options.enable_debug_symbols:
            self.runenv_info.define("OPENSSL_DEBUG_SYMBOLS", "1")

        # Python path for cross-compilation modules
        self.runenv_info.prepend_path("PYTHONPATH", os.path.join(self.package_folder, "openssl_tools/cross_compilation"))

        # PATH for cross-compilation scripts
        self.env_info.PATH.append(os.path.join(self.package_folder, "toolchains"))

    def package_id(self):
        """Package ID mode for cross-compilation packages"""
        self.info.clear()
