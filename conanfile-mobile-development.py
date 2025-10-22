"""
OpenSSL Mobile Development Package
iOS and Android specific development tools and optimizations
"""

import os
from conan import ConanFile
from conan.tools.files import copy
from conan.tools.layout import basic_layout


class OpenSSLMobileDevelopmentConan(ConanFile):
    name = "openssl-mobile-development"
    version = "3.5.2"
    description = "OpenSSL mobile development tools for iOS and Android"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/openssl-tools"
    homepage = "https://github.com/sparesparrow/openssl-tools"
    topics = ("openssl", "mobile", "ios", "android", "cross-compilation")

    # Package settings
    settings = "os", "arch", "compiler", "build_type"
    package_type = "python-require"

    # Mobile development options
    options = {
        "target_ios": [True, False],
        "target_android": [True, False],
        "enable_bitcode": [True, False],
        "enable_mobile_optimization": [True, False],
        "generate_frameworks": [True, False],
        "generate_aar": [True, False],
        "enable_mobile_security": [True, False],
        "mobile_architectures": ["armv7", "arm64", "x86", "x86_64"],
    }
    default_options = {
        "target_ios": False,
        "target_android": False,
        "enable_bitcode": False,
        "enable_mobile_optimization": True,
        "generate_frameworks": False,
        "generate_aar": False,
        "enable_mobile_security": True,
        "mobile_architectures": "arm64",
    }

    # Export sources
    exports_sources = (
        "openssl_tools/mobile_development/*",
        "mobile/*",
        "ios/*",
        "android/*",
        "frameworks/*",
        "*.md"
    )

    def init(self):
        """Initialize with proper channel"""
        if not os.getenv("CONAN_CHANNEL"):
            self.user = "sparesparrow"
            self.channel = "stable"

    def requirements(self):
        """Mobile development depends on foundation and cross-compilation"""
        self.requires("openssl-base/1.0.1@sparesparrow/stable")
        self.requires("openssl-cross-compilation/3.5.2@sparesparrow/stable")

    def layout(self):
        """Define package layout"""
        basic_layout(self)

    def package(self):
        """Package mobile development components"""
        # Copy mobile development modules
        copy(self, "*", src=os.path.join(self.source_folder, "openssl_tools/mobile_development"),
             dst=os.path.join(self.package_folder, "openssl_tools/mobile_development"), keep_path=True)

        # Copy mobile configurations
        copy(self, "*", src=os.path.join(self.source_folder, "mobile"),
             dst=os.path.join(self.package_folder, "mobile"), keep_path=True)

        # Copy iOS specific configurations
        copy(self, "*", src=os.path.join(self.source_folder, "ios"),
             dst=os.path.join(self.package_folder, "ios"), keep_path=True)

        # Copy Android specific configurations
        copy(self, "*", src=os.path.join(self.source_folder, "android"),
             dst=os.path.join(self.package_folder, "android"), keep_path=True)

        # Copy framework templates
        copy(self, "*", src=os.path.join(self.source_folder, "frameworks"),
             dst=os.path.join(self.package_folder, "frameworks"), keep_path=True)

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
        self.runenv_info.define("OPENSSL_MOBILE_ROOT", self.package_folder)
        self.runenv_info.define("OPENSSL_MOBILE_ARCH", self.options.mobile_architectures)
        self.runenv_info.define("OPENSSL_MOBILE_VERSION", self.version)

        # Mobile platform flags
        if self.options.target_ios:
            self.runenv_info.define("OPENSSL_TARGET_IOS", "1")
        if self.options.target_android:
            self.runenv_info.define("OPENSSL_TARGET_ANDROID", "1")
        if self.options.enable_bitcode:
            self.runenv_info.define("OPENSSL_BITCODE", "1")
        if self.options.enable_mobile_optimization:
            self.runenv_info.define("OPENSSL_MOBILE_OPTIMIZATION", "1")
        if self.options.generate_frameworks:
            self.runenv_info.define("OPENSSL_GENERATE_FRAMEWORKS", "1")
        if self.options.generate_aar:
            self.runenv_info.define("OPENSSL_GENERATE_AAR", "1")
        if self.options.enable_mobile_security:
            self.runenv_info.define("OPENSSL_MOBILE_SECURITY", "1")

        # Python path for mobile development modules
        self.runenv_info.prepend_path("PYTHONPATH", os.path.join(self.package_folder, "openssl_tools/mobile_development"))

        # PATH for mobile development scripts
        self.env_info.PATH.append(os.path.join(self.package_folder, "mobile"))

    def package_id(self):
        """Package ID mode for mobile development packages"""
        self.info.clear()
