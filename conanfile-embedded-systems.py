"""
OpenSSL Embedded Systems Package
Microcontroller and IoT specific tools and optimizations
"""

import os
from conan import ConanFile
from conan.tools.files import copy
from conan.tools.layout import basic_layout


class OpenSSLEmbeddedSystemsConan(ConanFile):
    name = "openssl-embedded-systems"
    version = "3.5.2"
    description = "OpenSSL embedded systems and IoT development tools"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/openssl-tools"
    homepage = "https://github.com/sparesparrow/openssl-tools"
    topics = ("openssl", "embedded", "iot", "microcontroller", "resource-constrained")

    # Package settings
    settings = "os", "arch", "compiler", "build_type"
    package_type = "python-require"

    # Embedded systems options
    options = {
        "target_microcontroller": ["none", "arm-cortex-m", "riscv", "esp32", "arduino"],
        "memory_optimization": [True, False],
        "minimal_crypto": [True, False],
        "enable_rom_optimization": [True, False],
        "enable_flash_optimization": [True, False],
        "generate_embedded_docs": [True, False],
        "validate_resource_usage": [True, False],
        "max_memory_footprint": ["1KB", "4KB", "16KB", "64KB", "256KB"],
    }
    default_options = {
        "target_microcontroller": "none",
        "memory_optimization": True,
        "minimal_crypto": False,
        "enable_rom_optimization": True,
        "enable_flash_optimization": True,
        "generate_embedded_docs": True,
        "validate_resource_usage": True,
        "max_memory_footprint": "64KB",
    }

    # Export sources
    exports_sources = (
        "openssl_tools/embedded_systems/*",
        "embedded/*",
        "microcontroller/*",
        "iot/*",
        "resource-optimization/*",
        "*.md"
    )

    def init(self):
        """Initialize with proper channel"""
        if not os.getenv("CONAN_CHANNEL"):
            self.user = "sparesparrow"
            self.channel = "stable"

    def requirements(self):
        """Embedded systems depend on foundation and cross-compilation"""
        self.requires("openssl-base/1.0.1@sparesparrow/stable")
        self.requires("openssl-cross-compilation/3.5.2@sparesparrow/stable")

    def layout(self):
        """Define package layout"""
        basic_layout(self)

    def package(self):
        """Package embedded systems components"""
        # Copy embedded systems modules
        copy(self, "*", src=os.path.join(self.source_folder, "openssl_tools/embedded_systems"),
             dst=os.path.join(self.package_folder, "openssl_tools/embedded_systems"), keep_path=True)

        # Copy embedded configurations
        copy(self, "*", src=os.path.join(self.source_folder, "embedded"),
             dst=os.path.join(self.package_folder, "embedded"), keep_path=True)

        # Copy microcontroller support
        copy(self, "*", src=os.path.join(self.source_folder, "microcontroller"),
             dst=os.path.join(self.package_folder, "microcontroller"), keep_path=True)

        # Copy IoT configurations
        copy(self, "*", src=os.path.join(self.source_folder, "iot"),
             dst=os.path.join(self.package_folder, "iot"), keep_path=True)

        # Copy resource optimization tools
        copy(self, "*", src=os.path.join(self.source_folder, "resource-optimization"),
             dst=os.path.join(self.package_folder, "resource-optimization"), keep_path=True)

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
        self.runenv_info.define("OPENSSL_EMBEDDED_ROOT", self.package_folder)
        self.runenv_info.define("OPENSSL_EMBEDDED_MC", self.options.target_microcontroller)
        self.runenv_info.define("OPENSSL_MEMORY_FOOTPRINT", self.options.max_memory_footprint)
        self.runenv_info.define("OPENSSL_EMBEDDED_VERSION", self.version)

        # Feature flags
        if self.options.memory_optimization:
            self.runenv_info.define("OPENSSL_MEMORY_OPTIMIZATION", "1")
        if self.options.minimal_crypto:
            self.runenv_info.define("OPENSSL_MINIMAL_CRYPTO", "1")
        if self.options.enable_rom_optimization:
            self.runenv_info.define("OPENSSL_ROM_OPTIMIZATION", "1")
        if self.options.enable_flash_optimization:
            self.runenv_info.define("OPENSSL_FLASH_OPTIMIZATION", "1")
        if self.options.generate_embedded_docs:
            self.runenv_info.define("OPENSSL_EMBEDDED_DOCS", "1")
        if self.options.validate_resource_usage:
            self.runenv_info.define("OPENSSL_RESOURCE_VALIDATION", "1")

        # Python path for embedded systems modules
        self.runenv_info.prepend_path("PYTHONPATH", os.path.join(self.package_folder, "openssl_tools/embedded_systems"))

        # PATH for embedded systems scripts
        self.env_info.PATH.append(os.path.join(self.package_folder, "embedded"))

    def package_id(self):
        """Package ID mode for embedded systems packages"""
        self.info.clear()
