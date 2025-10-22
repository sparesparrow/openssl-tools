"""
OpenSSL Cloud Integration Package
AWS, Azure, and GCP specific integrations and optimizations
"""

import os
from conan import ConanFile
from conan.tools.files import copy
from conan.tools.layout import basic_layout


class OpenSSLCloudIntegrationConan(ConanFile):
    name = "openssl-cloud-integration"
    version = "3.5.2"
    description = "OpenSSL cloud platform integrations and optimizations"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/openssl-tools"
    homepage = "https://github.com/sparesparrow/openssl-tools"
    topics = ("openssl", "cloud", "aws", "azure", "gcp", "integration")

    # Package settings
    settings = "os", "arch", "compiler", "build_type"
    package_type = "python-require"

    # Cloud integration options
    options = {
        "integrate_aws": [True, False],
        "integrate_azure": [True, False],
        "integrate_gcp": [True, False],
        "enable_cloud_hsm": [True, False],
        "enable_key_management": [True, False],
        "enable_cloud_logging": [True, False],
        "generate_cloud_templates": [True, False],
        "optimize_for_cloud": [True, False],
    }
    default_options = {
        "integrate_aws": False,
        "integrate_azure": False,
        "integrate_gcp": False,
        "enable_cloud_hsm": False,
        "enable_key_management": True,
        "enable_cloud_logging": True,
        "generate_cloud_templates": True,
        "optimize_for_cloud": True,
    }

    # Export sources
    exports_sources = (
        "openssl_tools/cloud_integration/*",
        "cloud/*",
        "aws/*",
        "azure/*",
        "gcp/*",
        "templates/cloud/*",
        "*.md"
    )

    def init(self):
        """Initialize with proper channel"""
        if not os.getenv("CONAN_CHANNEL"):
            self.user = "sparesparrow"
            self.channel = "stable"

    def requirements(self):
        """Cloud integration depends on foundation and security"""
        self.requires("openssl-base/1.0.1@sparesparrow/stable")
        self.requires("openssl-security/1.0.0@sparesparrow/stable")

    def layout(self):
        """Define package layout"""
        basic_layout(self)

    def package(self):
        """Package cloud integration components"""
        # Copy cloud integration modules
        copy(self, "*", src=os.path.join(self.source_folder, "openssl_tools/cloud_integration"),
             dst=os.path.join(self.package_folder, "openssl_tools/cloud_integration"), keep_path=True)

        # Copy cloud platform configs
        copy(self, "*", src=os.path.join(self.source_folder, "cloud"),
             dst=os.path.join(self.package_folder, "cloud"), keep_path=True)

        # Copy AWS specific configurations
        copy(self, "*", src=os.path.join(self.source_folder, "aws"),
             dst=os.path.join(self.package_folder, "aws"), keep_path=True)

        # Copy Azure specific configurations
        copy(self, "*", src=os.path.join(self.source_folder, "azure"),
             dst=os.path.join(self.package_folder, "azure"), keep_path=True)

        # Copy GCP specific configurations
        copy(self, "*", src=os.path.join(self.source_folder, "gcp"),
             dst=os.path.join(self.package_folder, "gcp"), keep_path=True)

        # Copy cloud templates
        copy(self, "*", src=os.path.join(self.source_folder, "templates/cloud"),
             dst=os.path.join(self.package_folder, "templates/cloud"), keep_path=True)

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
        self.runenv_info.define("OPENSSL_CLOUD_ROOT", self.package_folder)
        self.runenv_info.define("OPENSSL_CLOUD_VERSION", self.version)

        # Cloud platform flags
        if self.options.integrate_aws:
            self.runenv_info.define("OPENSSL_INTEGRATE_AWS", "1")
        if self.options.integrate_azure:
            self.runenv_info.define("OPENSSL_INTEGRATE_AZURE", "1")
        if self.options.integrate_gcp:
            self.runenv_info.define("OPENSSL_INTEGRATE_GCP", "1")
        if self.options.enable_cloud_hsm:
            self.runenv_info.define("OPENSSL_CLOUD_HSM", "1")
        if self.options.enable_key_management:
            self.runenv_info.define("OPENSSL_KEY_MANAGEMENT", "1")
        if self.options.enable_cloud_logging:
            self.runenv_info.define("OPENSSL_CLOUD_LOGGING", "1")
        if self.options.generate_cloud_templates:
            self.runenv_info.define("OPENSSL_CLOUD_TEMPLATES", "1")
        if self.options.optimize_for_cloud:
            self.runenv_info.define("OPENSSL_OPTIMIZE_CLOUD", "1")

        # Python path for cloud integration modules
        self.runenv_info.prepend_path("PYTHONPATH", os.path.join(self.package_folder, "openssl_tools/cloud_integration"))

        # PATH for cloud integration scripts
        self.env_info.PATH.append(os.path.join(self.package_folder, "cloud"))

    def package_id(self):
        """Package ID mode for cloud integration packages"""
        self.info.clear()
