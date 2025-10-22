"""
OpenSSL Optimization Package
Provides build optimization, performance tuning, and configuration management
"""

import os
from conan import ConanFile
from conan.tools.files import copy
from conan.tools.layout import basic_layout


class OpenSSLOptimizationConan(ConanFile):
    name = "openssl-optimization"
    version = "3.5.2"
    description = "OpenSSL build optimization and performance tuning tools"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/openssl-tools"
    homepage = "https://github.com/sparesparrow/openssl-tools"
    topics = ("openssl", "optimization", "performance", "build", "tuning")

    # Package settings
    settings = "os", "arch", "compiler", "build_type"
    package_type = "python-require"

    # Optimization options
    options = {
        "enable_lto": [True, False],  # Link-time optimization
        "enable_pgo": [True, False],  # Profile-guided optimization
        "enable_asan": [True, False],  # Address sanitizer
        "enable_ubsan": [True, False],  # Undefined behavior sanitizer
        "optimization_level": ["none", "size", "speed", "max"],
        "vector_instructions": ["none", "sse2", "avx2", "avx512"],
    }
    default_options = {
        "enable_lto": False,
        "enable_pgo": False,
        "enable_asan": False,
        "enable_ubsan": False,
        "optimization_level": "speed",
        "vector_instructions": "avx2",
    }

    # Export sources
    exports_sources = (
        "openssl_tools/optimization/*",
        "scripts/optimization/*",
        "templates/optimization/*",
        "profiles/optimization/*",
        "*.md"
    )

    def init(self):
        """Initialize with proper channel"""
        if not os.getenv("CONAN_CHANNEL"):
            self.user = "sparesparrow"
            self.channel = "stable"

    def requirements(self):
        """Optimization package depends on foundation"""
        self.requires("openssl-base/1.0.1@sparesparrow/stable")

    def layout(self):
        """Define package layout"""
        basic_layout(self)

    def package(self):
        """Package optimization components"""
        # Copy optimization modules
        copy(self, "*", src=os.path.join(self.source_folder, "openssl_tools/optimization"),
             dst=os.path.join(self.package_folder, "openssl_tools/optimization"), keep_path=True)

        # Copy optimization scripts
        copy(self, "*", src=os.path.join(self.source_folder, "scripts/optimization"),
             dst=os.path.join(self.package_folder, "scripts/optimization"), keep_path=True)

        # Copy optimization templates
        copy(self, "*", src=os.path.join(self.source_folder, "templates/optimization"),
             dst=os.path.join(self.package_folder, "templates/optimization"), keep_path=True)

        # Copy optimization profiles
        copy(self, "*", src=os.path.join(self.source_folder, "profiles/optimization"),
             dst=os.path.join(self.package_folder, "profiles/optimization"), keep_path=True)

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
        self.runenv_info.define("OPENSSL_OPTIMIZATION_ROOT", self.package_folder)
        self.runenv_info.define("OPENSSL_OPTIMIZATION_LEVEL", self.options.optimization_level)
        self.runenv_info.define("OPENSSL_VECTOR_INSTRUCTIONS", self.options.vector_instructions)

        # Optimization flags
        if self.options.enable_lto:
            self.runenv_info.define("OPENSSL_ENABLE_LTO", "1")
        if self.options.enable_pgo:
            self.runenv_info.define("OPENSSL_ENABLE_PGO", "1")
        if self.options.enable_asan:
            self.runenv_info.define("OPENSSL_ENABLE_ASAN", "1")
        if self.options.enable_ubsan:
            self.runenv_info.define("OPENSSL_ENABLE_UBSAN", "1")

        # Python path for optimization modules
        self.runenv_info.prepend_path("PYTHONPATH", os.path.join(self.package_folder, "openssl_tools/optimization"))

        # PATH for optimization scripts
        self.env_info.PATH.append(os.path.join(self.package_folder, "scripts/optimization"))

    def package_id(self):
        """Package ID mode for optimization packages"""
        self.info.clear()
