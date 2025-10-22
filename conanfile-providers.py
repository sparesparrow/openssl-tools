"""
OpenSSL Providers Package
Manages OpenSSL provider architecture for enhanced cryptographic capabilities
"""

import os
from conan import ConanFile
from conan.tools.files import copy
from conan.tools.layout import basic_layout


class OpenSSLProvidersConan(ConanFile):
    name = "openssl-providers"
    version = "3.5.2"
    description = "OpenSSL provider management and integration tools"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/openssl-tools"
    homepage = "https://github.com/sparesparrow/openssl-tools"
    topics = ("openssl", "providers", "crypto", "fips", "quantum-safe", "pkcs11")

    # Package settings
    settings = "os", "arch", "compiler", "build_type"
    package_type = "python-require"

    # Available providers
    options = {
        "enable_fips": [True, False],
        "enable_oqs": [True, False],  # Quantum-safe
        "enable_pkcs11": [True, False],
        "enable_tpm2": [True, False],
    }
    default_options = {
        "enable_fips": True,
        "enable_oqs": False,
        "enable_pkcs11": False,
        "enable_tpm2": False,
    }

    # Export sources
    exports_sources = (
        "openssl_tools/providers/*",
        "scripts/providers/*",
        "templates/providers/*",
        "*.md"
    )

    def init(self):
        """Initialize with proper channel"""
        if not os.getenv("CONAN_CHANNEL"):
            self.user = "sparesparrow"
            self.channel = "stable"

    def requirements(self):
        """Providers package depends on foundation and security"""
        self.requires("openssl-base/1.0.1@sparesparrow/stable")
        self.requires("openssl-security/1.0.0@sparesparrow/stable")

    def layout(self):
        """Define package layout"""
        basic_layout(self)

    def package(self):
        """Package provider components"""
        # Copy provider modules
        copy(self, "*", src=os.path.join(self.source_folder, "openssl_tools/providers"),
             dst=os.path.join(self.package_folder, "openssl_tools/providers"), keep_path=True)

        # Copy provider scripts
        copy(self, "*", src=os.path.join(self.source_folder, "scripts/providers"),
             dst=os.path.join(self.package_folder, "scripts/providers"), keep_path=True)

        # Copy provider templates
        copy(self, "*", src=os.path.join(self.source_folder, "templates/providers"),
             dst=os.path.join(self.package_folder, "templates/providers"), keep_path=True)

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
        self.runenv_info.define("OPENSSL_PROVIDERS_ROOT", self.package_folder)
        self.runenv_info.define("OPENSSL_PROVIDERS_VERSION", self.version)

        # Provider-specific environment
        if self.options.enable_fips:
            self.runenv_info.define("OPENSSL_FIPS_PROVIDER", "fips")
        if self.options.enable_oqs:
            self.runenv_info.define("OPENSSL_OQS_PROVIDER", "oqs")
        if self.options.enable_pkcs11:
            self.runenv_info.define("OPENSSL_PKCS11_PROVIDER", "pkcs11")
        if self.options.enable_tpm2:
            self.runenv_info.define("OPENSSL_TPM2_PROVIDER", "tpm2")

        # Python path for provider modules
        self.runenv_info.prepend_path("PYTHONPATH", os.path.join(self.package_folder, "openssl_tools/providers"))

        # PATH for provider scripts
        self.env_info.PATH.append(os.path.join(self.package_folder, "scripts/providers"))

    def package_id(self):
        """Package ID mode for provider packages"""
        self.info.clear()

    def validate(self):
        """Validate provider configuration"""
        # At least one provider should be enabled for meaningful package
        enabled_providers = [
            self.options.enable_fips,
            self.options.enable_oqs,
            self.options.enable_pkcs11,
            self.options.enable_tpm2
        ]

        if not any(enabled_providers):
            self.output.warn("No providers enabled - consider enabling at least one provider")
