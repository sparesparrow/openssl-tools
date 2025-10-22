"""
OpenSSL High Availability Package
Clustering, load balancing, and high availability tools
"""

import os
from conan import ConanFile
from conan.tools.files import copy
from conan.tools.layout import basic_layout


class OpenSSLHighAvailabilityConan(ConanFile):
    name = "openssl-high-availability"
    version = "3.5.2"
    description = "OpenSSL clustering, load balancing, and high availability tools"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/openssl-tools"
    homepage = "https://github.com/sparesparrow/openssl-tools"
    topics = ("openssl", "high-availability", "clustering", "load-balancing", "scaling")

    # Package settings
    settings = "os", "arch", "compiler", "build_type"
    package_type = "python-require"

    # High availability options
    options = {
        "enable_clustering": [True, False],
        "enable_load_balancing": [True, False],
        "enable_failover": [True, False],
        "enable_health_monitoring": [True, False],
        "enable_state_synchronization": [True, False],
        "enable_auto_scaling": [True, False],
        "generate_cluster_configs": [True, False],
        "validate_ha_setup": [True, False],
    }
    default_options = {
        "enable_clustering": False,
        "enable_load_balancing": False,
        "enable_failover": False,
        "enable_health_monitoring": True,
        "enable_state_synchronization": False,
        "enable_auto_scaling": False,
        "generate_cluster_configs": True,
        "validate_ha_setup": True,
    }

    # Export sources
    exports_sources = (
        "openssl_tools/high_availability/*",
        "cluster/*",
        "load-balancer/*",
        "failover/*",
        "health/*",
        "scaling/*",
        "*.md"
    )

    def init(self):
        """Initialize with proper channel"""
        if not os.getenv("CONAN_CHANNEL"):
            self.user = "sparesparrow"
            self.channel = "stable"

    def requirements(self):
        """High availability depends on foundation and monitoring"""
        self.requires("openssl-base/1.0.1@sparesparrow/stable")
        self.requires("openssl-monitoring/3.5.2@sparesparrow/stable")

    def layout(self):
        """Define package layout"""
        basic_layout(self)

    def package(self):
        """Package high availability components"""
        # Copy high availability modules
        copy(self, "*", src=os.path.join(self.source_folder, "openssl_tools/high_availability"),
             dst=os.path.join(self.package_folder, "openssl_tools/high_availability"), keep_path=True)

        # Copy clustering configurations
        copy(self, "*", src=os.path.join(self.source_folder, "cluster"),
             dst=os.path.join(self.package_folder, "cluster"), keep_path=True)

        # Copy load balancer configurations
        copy(self, "*", src=os.path.join(self.source_folder, "load-balancer"),
             dst=os.path.join(self.package_folder, "load-balancer"), keep_path=True)

        # Copy failover configurations
        copy(self, "*", src=os.path.join(self.source_folder, "failover"),
             dst=os.path.join(self.package_folder, "failover"), keep_path=True)

        # Copy health monitoring configurations
        copy(self, "*", src=os.path.join(self.source_folder, "health"),
             dst=os.path.join(self.package_folder, "health"), keep_path=True)

        # Copy scaling configurations
        copy(self, "*", src=os.path.join(self.source_folder, "scaling"),
             dst=os.path.join(self.package_folder, "scaling"), keep_path=True)

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
        self.runenv_info.define("OPENSSL_HA_ROOT", self.package_folder)
        self.runenv_info.define("OPENSSL_HA_VERSION", self.version)

        # High availability flags
        if self.options.enable_clustering:
            self.runenv_info.define("OPENSSL_CLUSTERING", "1")
        if self.options.enable_load_balancing:
            self.runenv_info.define("OPENSSL_LOAD_BALANCING", "1")
        if self.options.enable_failover:
            self.runenv_info.define("OPENSSL_FAILOVER", "1")
        if self.options.enable_health_monitoring:
            self.runenv_info.define("OPENSSL_HEALTH_MONITORING", "1")
        if self.options.enable_state_synchronization:
            self.runenv_info.define("OPENSSL_STATE_SYNC", "1")
        if self.options.enable_auto_scaling:
            self.runenv_info.define("OPENSSL_AUTO_SCALING", "1")
        if self.options.generate_cluster_configs:
            self.runenv_info.define("OPENSSL_CLUSTER_CONFIGS", "1")
        if self.options.validate_ha_setup:
            self.runenv_info.define("OPENSSL_HA_VALIDATION", "1")

        # Python path for high availability modules
        self.runenv_info.prepend_path("PYTHONPATH", os.path.join(self.package_folder, "openssl_tools/high_availability"))

        # PATH for high availability scripts
        self.env_info.PATH.append(os.path.join(self.package_folder, "cluster"))

    def package_id(self):
        """Package ID mode for high availability packages"""
        self.info.clear()
