"""
OpenSSL Security Audit Package
Advanced security analysis, vulnerability assessment, and audit tools
"""

import os
from conan import ConanFile
from conan.tools.files import copy
from conan.tools.layout import basic_layout


class OpenSSLSecurityAuditConan(ConanFile):
    name = "openssl-security-audit"
    version = "3.5.2"
    description = "OpenSSL advanced security auditing and vulnerability assessment tools"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/openssl-tools"
    homepage = "https://github.com/sparesparrow/openssl-tools"
    topics = ("openssl", "security", "audit", "vulnerability", "assessment", "pentest")

    # Package settings
    settings = "os", "arch", "compiler", "build_type"
    package_type = "python-require"

    # Security audit options
    options = {
        "scan_vulnerabilities": [True, False],
        "analyze_crypto_strength": [True, False],
        "check_compliance": [True, False],
        "generate_audit_reports": [True, False],
        "enable_continuous_monitoring": [True, False],
        "audit_providers": [True, False],
        "check_side_channels": [True, False],
        "validate_certificates": [True, False],
    }
    default_options = {
        "scan_vulnerabilities": True,
        "analyze_crypto_strength": True,
        "check_compliance": True,
        "generate_audit_reports": True,
        "enable_continuous_monitoring": False,
        "audit_providers": True,
        "check_side_channels": False,
        "validate_certificates": True,
    }

    # Export sources
    exports_sources = (
        "openssl_tools/security_audit/*",
        "scripts/security_audit/*",
        "templates/security_audit/*",
        "audit-rules/*",
        "vulnerability-db/*",
        "*.md"
    )

    def init(self):
        """Initialize with proper channel"""
        if not os.getenv("CONAN_CHANNEL"):
            self.user = "sparesparrow"
            self.channel = "stable"

    def requirements(self):
        """Security audit depends on foundation and security"""
        self.requires("openssl-base/1.0.1@sparesparrow/stable")
        self.requires("openssl-security/1.0.0@sparesparrow/stable")

    def layout(self):
        """Define package layout"""
        basic_layout(self)

    def package(self):
        """Package security audit components"""
        # Copy security audit modules
        copy(self, "*", src=os.path.join(self.source_folder, "openssl_tools/security_audit"),
             dst=os.path.join(self.package_folder, "openssl_tools/security_audit"), keep_path=True)

        # Copy security audit scripts
        copy(self, "*", src=os.path.join(self.source_folder, "scripts/security_audit"),
             dst=os.path.join(self.package_folder, "scripts/security_audit"), keep_path=True)

        # Copy security audit templates
        copy(self, "*", src=os.path.join(self.source_folder, "templates/security_audit"),
             dst=os.path.join(self.package_folder, "templates/security_audit"), keep_path=True)

        # Copy audit rules
        copy(self, "*", src=os.path.join(self.source_folder, "audit-rules"),
             dst=os.path.join(self.package_folder, "audit-rules"), keep_path=True)

        # Copy vulnerability database
        copy(self, "*", src=os.path.join(self.source_folder, "vulnerability-db"),
             dst=os.path.join(self.package_folder, "vulnerability-db"), keep_path=True)

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
        self.runenv_info.define("OPENSSL_SECURITY_AUDIT_ROOT", self.package_folder)
        self.runenv_info.define("OPENSSL_SECURITY_AUDIT_VERSION", self.version)
        self.runenv_info.define("OPENSSL_VULNERABILITY_DB",
                                os.path.join(self.package_folder, "vulnerability-db"))

        # Feature flags
        if self.options.scan_vulnerabilities:
            self.runenv_info.define("OPENSSL_SCAN_VULNERABILITIES", "1")
        if self.options.analyze_crypto_strength:
            self.runenv_info.define("OPENSSL_ANALYZE_CRYPTO_STRENGTH", "1")
        if self.options.check_compliance:
            self.runenv_info.define("OPENSSL_CHECK_COMPLIANCE", "1")
        if self.options.generate_audit_reports:
            self.runenv_info.define("OPENSSL_GENERATE_AUDIT_REPORTS", "1")
        if self.options.enable_continuous_monitoring:
            self.runenv_info.define("OPENSSL_CONTINUOUS_MONITORING", "1")
        if self.options.audit_providers:
            self.runenv_info.define("OPENSSL_AUDIT_PROVIDERS", "1")
        if self.options.check_side_channels:
            self.runenv_info.define("OPENSSL_CHECK_SIDE_CHANNELS", "1")
        if self.options.validate_certificates:
            self.runenv_info.define("OPENSSL_VALIDATE_CERTIFICATES", "1")

        # Python path for security audit modules
        self.runenv_info.prepend_path("PYTHONPATH", os.path.join(self.package_folder, "openssl_tools/security_audit"))

        # PATH for security audit scripts
        self.env_info.PATH.append(os.path.join(self.package_folder, "scripts/security_audit"))

    def package_id(self):
        """Package ID mode for security audit packages"""
        self.info.clear()
