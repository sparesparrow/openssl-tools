"""
OpenSSL Analytics and Reporting Package
Advanced metrics, business intelligence, and reporting tools
"""

import os
from conan import ConanFile
from conan.tools.files import copy
from conan.tools.layout import basic_layout


class OpenSSLAnalyticsReportingConan(ConanFile):
    name = "openssl-analytics-reporting"
    version = "3.5.2"
    description = "OpenSSL advanced analytics, metrics, and business intelligence tools"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/openssl-tools"
    homepage = "https://github.com/sparesparrow/openssl-tools"
    topics = ("openssl", "analytics", "reporting", "metrics", "business-intelligence")

    # Package settings
    settings = "os", "arch", "compiler", "build_type"
    package_type = "python-require"

    # Analytics and reporting options
    options = {
        "enable_real_time_analytics": [True, False],
        "enable_business_intelligence": [True, False],
        "enable_performance_dashboards": [True, False],
        "enable_compliance_reporting": [True, False],
        "enable_security_analytics": [True, False],
        "generate_executive_reports": [True, False],
        "analytics_data_retention": ["1d", "7d", "30d", "90d", "1y"],
        "report_format": ["pdf", "html", "excel", "json", "xml"],
    }
    default_options = {
        "enable_real_time_analytics": True,
        "enable_business_intelligence": False,
        "enable_performance_dashboards": True,
        "enable_compliance_reporting": True,
        "enable_security_analytics": True,
        "generate_executive_reports": False,
        "analytics_data_retention": "30d",
        "report_format": "pdf",
    }

    # Export sources
    exports_sources = (
        "openssl_tools/analytics_reporting/*",
        "analytics/*",
        "reports/*",
        "dashboards/*",
        "bi/*",
        "metrics/*",
        "*.md"
    )

    def init(self):
        """Initialize with proper channel"""
        if not os.getenv("CONAN_CHANNEL"):
            self.user = "sparesparrow"
            self.channel = "stable"

    def requirements(self):
        """Analytics reporting depends on foundation and monitoring"""
        self.requires("openssl-base/1.0.1@sparesparrow/stable")
        self.requires("openssl-monitoring/3.5.2@sparesparrow/stable")

    def layout(self):
        """Define package layout"""
        basic_layout(self)

    def package(self):
        """Package analytics and reporting components"""
        # Copy analytics reporting modules
        copy(self, "*", src=os.path.join(self.source_folder, "openssl_tools/analytics_reporting"),
             dst=os.path.join(self.package_folder, "openssl_tools/analytics_reporting"), keep_path=True)

        # Copy analytics configurations
        copy(self, "*", src=os.path.join(self.source_folder, "analytics"),
             dst=os.path.join(self.package_folder, "analytics"), keep_path=True)

        # Copy report templates
        copy(self, "*", src=os.path.join(self.source_folder, "reports"),
             dst=os.path.join(self.package_folder, "reports"), keep_path=True)

        # Copy dashboard configurations
        copy(self, "*", src=os.path.join(self.source_folder, "dashboards"),
             dst=os.path.join(self.package_folder, "dashboards"), keep_path=True)

        # Copy business intelligence tools
        copy(self, "*", src=os.path.join(self.source_folder, "bi"),
             dst=os.path.join(self.package_folder, "bi"), keep_path=True)

        # Copy metrics configurations
        copy(self, "*", src=os.path.join(self.source_folder, "metrics"),
             dst=os.path.join(self.package_folder, "metrics"), keep_path=True)

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
        self.runenv_info.define("OPENSSL_ANALYTICS_ROOT", self.package_folder)
        self.runenv_info.define("OPENSSL_ANALYTICS_RETENTION", self.options.analytics_data_retention)
        self.runenv_info.define("OPENSSL_REPORT_FORMAT", self.options.report_format)
        self.runenv_info.define("OPENSSL_ANALYTICS_VERSION", self.version)

        # Analytics and reporting flags
        if self.options.enable_real_time_analytics:
            self.runenv_info.define("OPENSSL_REAL_TIME_ANALYTICS", "1")
        if self.options.enable_business_intelligence:
            self.runenv_info.define("OPENSSL_BUSINESS_INTELLIGENCE", "1")
        if self.options.enable_performance_dashboards:
            self.runenv_info.define("OPENSSL_PERFORMANCE_DASHBOARDS", "1")
        if self.options.enable_compliance_reporting:
            self.runenv_info.define("OPENSSL_COMPLIANCE_REPORTING", "1")
        if self.options.enable_security_analytics:
            self.runenv_info.define("OPENSSL_SECURITY_ANALYTICS", "1")
        if self.options.generate_executive_reports:
            self.runenv_info.define("OPENSSL_EXECUTIVE_REPORTS", "1")

        # Python path for analytics reporting modules
        self.runenv_info.prepend_path("PYTHONPATH", os.path.join(self.package_folder, "openssl_tools/analytics_reporting"))

        # PATH for analytics and reporting scripts
        self.env_info.PATH.append(os.path.join(self.package_folder, "analytics"))

    def package_id(self):
        """Package ID mode for analytics reporting packages"""
        self.info.clear()
