"""
OpenSSL Monitoring Package
Provides monitoring, observability, and performance analysis tools
"""

import os
from conan import ConanFile
from conan.tools.files import copy
from conan.tools.layout import basic_layout


class OpenSSLMonitoringConan(ConanFile):
    name = "openssl-monitoring"
    version = "3.5.2"
    description = "OpenSSL monitoring, observability, and performance analysis tools"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/openssl-tools"
    homepage = "https://github.com/sparesparrow/openssl-tools"
    topics = ("openssl", "monitoring", "observability", "performance", "analysis")

    # Package settings
    settings = "os", "arch", "compiler", "build_type"
    package_type = "python-require"

    # Monitoring options
    options = {
        "enable_metrics": [True, False],
        "enable_tracing": [True, False],
        "enable_profiling": [True, False],
        "enable_dashboard": [True, False],
        "metrics_format": ["prometheus", "json", "graphite"],
    }
    default_options = {
        "enable_metrics": True,
        "enable_tracing": False,
        "enable_profiling": False,
        "enable_dashboard": True,
        "metrics_format": "prometheus",
    }

    # Export sources
    exports_sources = (
        "openssl_tools/monitoring/*",
        "scripts/monitoring/*",
        "templates/monitoring/*",
        "dashboard/*",
        "*.md"
    )

    def init(self):
        """Initialize with proper channel"""
        if not os.getenv("CONAN_CHANNEL"):
            self.user = "sparesparrow"
            self.channel = "stable"

    def requirements(self):
        """Monitoring package depends on foundation"""
        self.requires("openssl-base/1.0.1@sparesparrow/stable")

    def layout(self):
        """Define package layout"""
        basic_layout(self)

    def package(self):
        """Package monitoring components"""
        # Copy monitoring modules
        copy(self, "*", src=os.path.join(self.source_folder, "openssl_tools/monitoring"),
             dst=os.path.join(self.package_folder, "openssl_tools/monitoring"), keep_path=True)

        # Copy monitoring scripts
        copy(self, "*", src=os.path.join(self.source_folder, "scripts/monitoring"),
             dst=os.path.join(self.package_folder, "scripts/monitoring"), keep_path=True)

        # Copy monitoring templates
        copy(self, "*", src=os.path.join(self.source_folder, "templates/monitoring"),
             dst=os.path.join(self.package_folder, "templates/monitoring"), keep_path=True)

        # Copy dashboard components
        copy(self, "*", src=os.path.join(self.source_folder, "dashboard"),
             dst=os.path.join(self.package_folder, "dashboard"), keep_path=True)

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
        self.runenv_info.define("OPENSSL_MONITORING_ROOT", self.package_folder)
        self.runenv_info.define("OPENSSL_METRICS_FORMAT", self.options.metrics_format)
        self.runenv_info.define("OPENSSL_DASHBOARD_PORT", "8080")

        # Feature flags
        if self.options.enable_metrics:
            self.runenv_info.define("OPENSSL_ENABLE_METRICS", "1")
        if self.options.enable_tracing:
            self.runenv_info.define("OPENSSL_ENABLE_TRACING", "1")
        if self.options.enable_profiling:
            self.runenv_info.define("OPENSSL_ENABLE_PROFILING", "1")
        if self.options.enable_dashboard:
            self.runenv_info.define("OPENSSL_ENABLE_DASHBOARD", "1")

        # Python path for monitoring modules
        self.runenv_info.prepend_path("PYTHONPATH", os.path.join(self.package_folder, "openssl_tools/monitoring"))

        # PATH for monitoring scripts
        self.env_info.PATH.append(os.path.join(self.package_folder, "scripts/monitoring"))

    def package_id(self):
        """Package ID mode for monitoring packages"""
        self.info.clear()
