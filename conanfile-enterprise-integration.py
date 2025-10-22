"""
OpenSSL Enterprise Integration Package
LDAP, Active Directory, SSO, and enterprise system integrations
"""

import os
from conan import ConanFile
from conan.tools.files import copy
from conan.tools.layout import basic_layout


class OpenSSLEnterpriseIntegrationConan(ConanFile):
    name = "openssl-enterprise-integration"
    version = "3.5.2"
    description = "OpenSSL enterprise system integrations and authentication tools"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/openssl-tools"
    homepage = "https://github.com/sparesparrow/openssl-tools"
    topics = ("openssl", "enterprise", "ldap", "ad", "sso", "authentication")

    # Package settings
    settings = "os", "arch", "compiler", "build_type"
    package_type = "python-require"

    # Enterprise integration options
    options = {
        "integrate_ldap": [True, False],
        "integrate_active_directory": [True, False],
        "integrate_sso": [True, False],
        "integrate_kerberos": [True, False],
        "integrate_radius": [True, False],
        "enable_certificate_authority": [True, False],
        "generate_enterprise_templates": [True, False],
        "validate_enterprise_security": [True, False],
    }
    default_options = {
        "integrate_ldap": False,
        "integrate_active_directory": False,
        "integrate_sso": False,
        "integrate_kerberos": False,
        "integrate_radius": False,
        "enable_certificate_authority": False,
        "generate_enterprise_templates": True,
        "validate_enterprise_security": True,
    }

    # Export sources
    exports_sources = (
        "openssl_tools/enterprise_integration/*",
        "enterprise/*",
        "ldap/*",
        "ad/*",
        "sso/*",
        "kerberos/*",
        "radius/*",
        "ca/*",
        "*.md"
    )

    def init(self):
        """Initialize with proper channel"""
        if not os.getenv("CONAN_CHANNEL"):
            self.user = "sparesparrow"
            self.channel = "stable"

    def requirements(self):
        """Enterprise integration depends on foundation and security"""
        self.requires("openssl-base/1.0.1@sparesparrow/stable")
        self.requires("openssl-security/1.0.0@sparesparrow/stable")

    def layout(self):
        """Define package layout"""
        basic_layout(self)

    def package(self):
        """Package enterprise integration components"""
        # Copy enterprise integration modules
        copy(self, "*", src=os.path.join(self.source_folder, "openssl_tools/enterprise_integration"),
             dst=os.path.join(self.package_folder, "openssl_tools/enterprise_integration"), keep_path=True)

        # Copy enterprise configurations
        copy(self, "*", src=os.path.join(self.source_folder, "enterprise"),
             dst=os.path.join(self.package_folder, "enterprise"), keep_path=True)

        # Copy LDAP configurations
        copy(self, "*", src=os.path.join(self.source_folder, "ldap"),
             dst=os.path.join(self.package_folder, "ldap"), keep_path=True)

        # Copy Active Directory configurations
        copy(self, "*", src=os.path.join(self.source_folder, "ad"),
             dst=os.path.join(self.package_folder, "ad"), keep_path=True)

        # Copy SSO configurations
        copy(self, "*", src=os.path.join(self.source_folder, "sso"),
             dst=os.path.join(self.package_folder, "sso"), keep_path=True)

        # Copy Kerberos configurations
        copy(self, "*", src=os.path.join(self.source_folder, "kerberos"),
             dst=os.path.join(self.package_folder, "kerberos"), keep_path=True)

        # Copy RADIUS configurations
        copy(self, "*", src=os.path.join(self.source_folder, "radius"),
             dst=os.path.join(self.package_folder, "radius"), keep_path=True)

        # Copy CA configurations
        copy(self, "*", src=os.path.join(self.source_folder, "ca"),
             dst=os.path.join(self.package_folder, "ca"), keep_path=True)

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
        self.runenv_info.define("OPENSSL_ENTERPRISE_ROOT", self.package_folder)
        self.runenv_info.define("OPENSSL_ENTERPRISE_VERSION", self.version)

        # Enterprise integration flags
        if self.options.integrate_ldap:
            self.runenv_info.define("OPENSSL_INTEGRATE_LDAP", "1")
        if self.options.integrate_active_directory:
            self.runenv_info.define("OPENSSL_INTEGRATE_AD", "1")
        if self.options.integrate_sso:
            self.runenv_info.define("OPENSSL_INTEGRATE_SSO", "1")
        if self.options.integrate_kerberos:
            self.runenv_info.define("OPENSSL_INTEGRATE_KERBEROS", "1")
        if self.options.integrate_radius:
            self.runenv_info.define("OPENSSL_INTEGRATE_RADIUS", "1")
        if self.options.enable_certificate_authority:
            self.runenv_info.define("OPENSSL_CERTIFICATE_AUTHORITY", "1")
        if self.options.generate_enterprise_templates:
            self.runenv_info.define("OPENSSL_ENTERPRISE_TEMPLATES", "1")
        if self.options.validate_enterprise_security:
            self.runenv_info.define("OPENSSL_ENTERPRISE_SECURITY", "1")

        # Python path for enterprise integration modules
        self.runenv_info.prepend_path("PYTHONPATH", os.path.join(self.package_folder, "openssl_tools/enterprise_integration"))

        # PATH for enterprise integration scripts
        self.env_info.PATH.append(os.path.join(self.package_folder, "enterprise"))

    def package_id(self):
        """Package ID mode for enterprise integration packages"""
        self.info.clear()
