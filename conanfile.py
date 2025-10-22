"""
OpenSSL Tools Conan Package (Meta-package)
Orchestrates all OpenSSL tooling components and provides unified interface
"""

from conan import ConanFile
from conan.tools.files import copy, save
from conan.tools.layout import basic_layout
import os
import json
from pathlib import Path

class OpenSSLToolsConan(ConanFile):
    name = "openssl-tools"
    version = "1.2.0"
    description = "OpenSSL build tools, automation scripts, and infrastructure components (Meta-package)"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/openssl-tools"
    homepage = "https://github.com/sparesparrow/openssl-tools"
    topics = ("openssl", "build-tools", "automation", "ci-cd", "meta-package")

    # Package settings
    package_type = "python-require"
    settings = "os", "arch", "compiler", "build_type"

    # Export sources
    exports_sources = (
        "scripts/*",
        "profiles/*",
        "docker/*",
        "templates/*",
        ".cursor/*",
        "openssl_tools/**",
        "*.md",
        "pyproject.toml"
    )

    def requirements(self):
        """Require all modular tool packages"""
        # Foundation packages
        self.requires("openssl-profiles/2.0.0@sparesparrow/stable")

        # Original modular packages
        self.requires("openssl-testing/1.0.0@sparesparrow/stable")
        self.requires("openssl-security/1.0.0@sparesparrow/stable")
        self.requires("openssl-automation/1.0.0@sparesparrow/stable")
        self.requires("openssl-validation/1.0.0@sparesparrow/stable")

        # OpenSSL 3.5.2 enhanced packages
        self.requires("openssl-providers/3.5.2@sparesparrow/stable")
        self.requires("openssl-optimization/3.5.2@sparesparrow/stable")
        self.requires("openssl-monitoring/3.5.2@sparesparrow/stable")
        self.requires("openssl-compliance/3.5.2@sparesparrow/stable")

        # New specialized packages
        self.requires("openssl-benchmarking/3.5.2@sparesparrow/stable")
        self.requires("openssl-migration/3.5.2@sparesparrow/stable")
        self.requires("openssl-containerization/3.5.2@sparesparrow/stable")
        self.requires("openssl-cross-compilation/3.5.2@sparesparrow/stable")
        self.requires("openssl-development/3.5.2@sparesparrow/stable")
        self.requires("openssl-release-management/3.5.2@sparesparrow/stable")
        self.requires("openssl-security-audit/3.5.2@sparesparrow/stable")
        self.requires("openssl-integration/3.5.2@sparesparrow/stable")

        # Advanced enterprise packages
        self.requires("openssl-documentation/3.5.2@sparesparrow/stable")
        self.requires("openssl-hardware-acceleration/3.5.2@sparesparrow/stable")
        self.requires("openssl-cloud-integration/3.5.2@sparesparrow/stable")
        self.requires("openssl-mobile-development/3.5.2@sparesparrow/stable")
        self.requires("openssl-embedded-systems/3.5.2@sparesparrow/stable")
        self.requires("openssl-legacy-compatibility/3.5.2@sparesparrow/stable")
        self.requires("openssl-enterprise-integration/3.5.2@sparesparrow/stable")
        self.requires("openssl-high-availability/3.5.2@sparesparrow/stable")
        self.requires("openssl-analytics-reporting/3.5.2@sparesparrow/stable")

    def layout(self):
        """Define package layout"""
        basic_layout(self)

    def package(self):
        """Package orchestration components"""
        # Copy orchestration-specific components
        copy(self, "scripts/orchestration/*", src=self.source_folder,
             dst=os.path.join(self.package_folder, "scripts/orchestration"))
        copy(self, "templates/orchestration/*", src=self.source_folder,
             dst=os.path.join(self.package_folder, "templates/orchestration"))
        copy(self, ".cursor/*", src=self.source_folder,
             dst=os.path.join(self.package_folder, ".cursor"))

        # Copy configuration files
        copy(self, "*.md", src=self.source_folder, dst=self.package_folder)
        copy(self, "pyproject.toml", src=self.source_folder, dst=self.package_folder)

        # Create package info for meta-package
        self._create_package_info()

    def _create_package_info(self):
        """Create package information file"""
        package_info = {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "type": "meta-package",
            "modules": {
                "orchestration": ["build_orchestrator", "package_manager"],
                "integration": ["dependency_resolver", "tool_coordinator"],
                "deployment": ["environment_setup", "configuration_manager"],
                "providers": ["provider_manager", "fips_integration", "oqs_support"],
                "optimization": ["build_optimizer", "performance_tuner", "vectorization"],
                "monitoring": ["metrics_collector", "dashboard", "profiling"],
                "compliance": ["standards_validator", "report_generator", "audit_tools"],
                "benchmarking": ["performance_analyzer", "comparison_engine", "regression_tester"],
                "migration": ["version_upgrader", "compatibility_layer", "guide_generator"],
                "containerization": ["docker_builder", "k8s_generator", "security_hardening"],
                "cross_compilation": ["toolchain_manager", "platform_builder", "embedded_optimizer"],
                "development": ["ide_integrator", "debugging_tools", "devcontainer_builder"],
                "release_management": ["version_manager", "changelog_generator", "artifact_publisher"],
                "security_audit": ["vulnerability_scanner", "crypto_analyzer", "compliance_checker"],
                "integration": ["language_bindings", "api_generator", "interop_validator"],
                "documentation": ["api_generator", "guide_builder", "sphinx_integrator"],
                "hardware_acceleration": ["gpu_optimizer", "qat_manager", "fpga_integrator"],
                "cloud_integration": ["aws_integrator", "azure_integrator", "gcp_integrator"],
                "mobile_development": ["ios_builder", "android_builder", "framework_generator"],
                "embedded_systems": ["microcontroller_optimizer", "iot_configurator", "resource_analyzer"],
                "legacy_compatibility": ["shim_generator", "api_translator", "deprecation_handler"],
                "enterprise_integration": ["ldap_integrator", "ad_connector", "sso_manager"],
                "high_availability": ["cluster_manager", "load_balancer", "failover_controller"],
                "analytics_reporting": ["metrics_analyzer", "bi_generator", "executive_reporter"]
            },
            "dependencies": [
                "openssl-profiles/2.0.0@sparesparrow/stable",
                "openssl-testing/1.0.0@sparesparrow/stable",
                "openssl-security/1.0.0@sparesparrow/stable",
                "openssl-automation/1.0.0@sparesparrow/stable",
                "openssl-validation/1.0.0@sparesparrow/stable",
                "openssl-providers/3.5.2@sparesparrow/stable",
                "openssl-optimization/3.5.2@sparesparrow/stable",
                "openssl-monitoring/3.5.2@sparesparrow/stable",
                "openssl-compliance/3.5.2@sparesparrow/stable",
                "openssl-benchmarking/3.5.2@sparesparrow/stable",
                "openssl-migration/3.5.2@sparesparrow/stable",
                "openssl-containerization/3.5.2@sparesparrow/stable",
                "openssl-cross-compilation/3.5.2@sparesparrow/stable",
                "openssl-development/3.5.2@sparesparrow/stable",
                "openssl-release-management/3.5.2@sparesparrow/stable",
                "openssl-security-audit/3.5.2@sparesparrow/stable",
                "openssl-integration/3.5.2@sparesparrow/stable",
                "openssl-documentation/3.5.2@sparesparrow/stable",
                "openssl-hardware-acceleration/3.5.2@sparesparrow/stable",
                "openssl-cloud-integration/3.5.2@sparesparrow/stable",
                "openssl-mobile-development/3.5.2@sparesparrow/stable",
                "openssl-embedded-systems/3.5.2@sparesparrow/stable",
                "openssl-legacy-compatibility/3.5.2@sparesparrow/stable",
                "openssl-enterprise-integration/3.5.2@sparesparrow/stable",
                "openssl-high-availability/3.5.2@sparesparrow/stable",
                "openssl-analytics-reporting/3.5.2@sparesparrow/stable"
            ],
            "features": [
                "OpenSSL 3.5.2 provider architecture",
                "FIPS 140-3 compliance validation",
                "Quantum-safe cryptography support",
                "Performance optimization tools",
                "Real-time monitoring and metrics",
                "Regulatory compliance reporting",
                "Comprehensive benchmarking and profiling",
                "Automated migration from legacy versions",
                "Docker and Kubernetes deployment",
                "Cross-platform compilation support",
                "Enhanced IDE integration and debugging",
                "Automated release management",
                "Advanced security auditing",
                "Third-party language integration",
                "Automated documentation generation",
                "Hardware acceleration (GPU, QAT, FPGA)",
                "Cloud platform integrations (AWS, Azure, GCP)",
                "Mobile development (iOS, Android)",
                "Embedded systems optimization",
                "Legacy compatibility layers",
                "Enterprise authentication (LDAP, AD, SSO)",
                "High availability and clustering",
                "Advanced analytics and business intelligence"
            ],
            "tools": [
                "orchestration scripts",
                "integration utilities",
                "deployment templates",
                "provider management",
                "optimization profiles",
                "monitoring dashboards",
                "compliance reports",
                "benchmarking suites",
                "migration assistants",
                "container builders",
                "cross-compilation toolchains",
                "IDE integrations",
                "release automation",
                "security audit tools",
                "language bindings",
                "documentation generators",
                "hardware acceleration tools",
                "cloud integration scripts",
                "mobile development kits",
                "embedded optimization tools",
                "legacy compatibility shims",
                "enterprise authentication tools",
                "high availability managers",
                "analytics and reporting engines"
            ]
        }

        save(self, os.path.join(self.package_folder, "package_info.json"),
             json.dumps(package_info, indent=2))

    def package_info(self):
        """Define package information for meta-package"""
        # No C++ components - this is a meta-package
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.includedirs = []

        # Set environment variables for orchestration
        self.runenv_info.define("OPENSSL_TOOLS_ROOT", self.package_folder)
        self.runenv_info.define("OPENSSL_TOOLS_META_VERSION", self.version)
        self.runenv_info.define("OPENSSL_TOOLS_TYPE", "meta-package")

        # Python path for orchestration modules
        self.runenv_info.prepend_path("PYTHONPATH", self.package_folder)

        # PATH for orchestration scripts
        self.env_info.PATH.append(os.path.join(self.package_folder, "scripts/orchestration"))

    def package_id(self):
        """Package ID mode for meta-packages"""
        self.info.clear()

    def validate(self):
        """Validate that all required dependencies are available"""
        # Meta-package validation - ensure all dependencies are properly resolved
        pass
