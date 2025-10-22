"""
OpenSSL Compliance Package
Provides compliance validation, standards checking, and regulatory reporting
"""

import os
from conan import ConanFile
from conan.tools.files import copy
from conan.tools.layout import basic_layout


class OpenSSLComplianceConan(ConanFile):
    name = "openssl-compliance"
    version = "3.5.2"
    description = "OpenSSL compliance validation and regulatory reporting tools"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/openssl-tools"
    homepage = "https://github.com/sparesparrow/openssl-tools"
    topics = ("openssl", "compliance", "standards", "fips", "validation", "regulatory")

    # Package settings
    settings = "os", "arch", "compiler", "build_type"
    package_type = "python-require"

    # Compliance standards
    options = {
        "fips_140_3": [True, False],
        "common_criteria": [True, False],
        "nist_standards": [True, False],
        "gdpr_compliance": [True, False],
        "hipaa_compliance": [True, False],
        "sox_compliance": [True, False],
        "generate_reports": [True, False],
    }
    default_options = {
        "fips_140_3": True,
        "common_criteria": False,
        "nist_standards": True,
        "gdpr_compliance": False,
        "hipaa_compliance": False,
        "sox_compliance": False,
        "generate_reports": True,
    }

    # Export sources
    exports_sources = (
        "openssl_tools/compliance/*",
        "scripts/compliance/*",
        "templates/compliance/*",
        "standards/*",
        "*.md"
    )

    def init(self):
        """Initialize with proper channel"""
        if not os.getenv("CONAN_CHANNEL"):
            self.user = "sparesparrow"
            self.channel = "stable"

    def requirements(self):
        """Compliance package depends on foundation and validation"""
        self.requires("openssl-base/1.0.1@sparesparrow/stable")
        self.requires("openssl-validation/1.0.0@sparesparrow/stable")

    def layout(self):
        """Define package layout"""
        basic_layout(self)

    def package(self):
        """Package compliance components"""
        # Copy compliance modules
        copy(self, "*", src=os.path.join(self.source_folder, "openssl_tools/compliance"),
             dst=os.path.join(self.package_folder, "openssl_tools/compliance"), keep_path=True)

        # Copy compliance scripts
        copy(self, "*", src=os.path.join(self.source_folder, "scripts/compliance"),
             dst=os.path.join(self.package_folder, "scripts/compliance"), keep_path=True)

        # Copy compliance templates
        copy(self, "*", src=os.path.join(self.source_folder, "templates/compliance"),
             dst=os.path.join(self.package_folder, "templates/compliance"), keep_path=True)

        # Copy standards definitions
        copy(self, "*", src=os.path.join(self.source_folder, "standards"),
             dst=os.path.join(self.package_folder, "standards"), keep_path=True)

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
        self.runenv_info.define("OPENSSL_COMPLIANCE_ROOT", self.package_folder)
        self.runenv_info.define("OPENSSL_STANDARDS_PATH",
                                os.path.join(self.package_folder, "standards"))

        # Compliance flags
        if self.options.fips_140_3:
            self.runenv_info.define("OPENSSL_FIPS_140_3", "1")
        if self.options.common_criteria:
            self.runenv_info.define("OPENSSL_COMMON_CRITERIA", "1")
        if self.options.nist_standards:
            self.runenv_info.define("OPENSSL_NIST_STANDARDS", "1")
        if self.options.gdpr_compliance:
            self.runenv_info.define("OPENSSL_GDPR_COMPLIANCE", "1")
        if self.options.hipaa_compliance:
            self.runenv_info.define("OPENSSL_HIPAA_COMPLIANCE", "1")
        if self.options.sox_compliance:
            self.runenv_info.define("OPENSSL_SOX_COMPLIANCE", "1")

        # Python path for compliance modules
        self.runenv_info.prepend_path("PYTHONPATH", os.path.join(self.package_folder, "openssl_tools/compliance"))

        # PATH for compliance scripts
        self.env_info.PATH.append(os.path.join(self.package_folder, "scripts/compliance"))

    def package_id(self):
        """Package ID mode for compliance packages"""
        self.info.clear()
