"""
OpenSSL 3.5.2 Complete Package
Comprehensive OpenSSL 3.5.2 with all enhanced features and provider architecture
"""

import os
from conan import ConanFile
from conan.tools.files import copy
from conan.tools.layout import basic_layout


class OpenSSL35CompleteConan(ConanFile):
    name = "openssl-3.5.2-complete"
    version = "3.5.2"
    description = "OpenSSL 3.5.2 Complete - Full provider architecture with all enhancements"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/openssl-tools"
    homepage = "https://github.com/sparesparrow/openssl-tools"
    topics = ("openssl", "3.5.2", "providers", "fips", "quantum-safe", "enterprise")

    # Package settings
    settings = "os", "arch", "compiler", "build_type"
    package_type = "library"

    # Comprehensive options for all OpenSSL 3.5.2 features
    options = {
        # Core features
        "shared": [True, False],
        "fPIC": [True, False],

        # Provider architecture
        "enable_providers": [True, False],
        "enable_fips": [True, False],
        "enable_oqs": [True, False],  # Quantum-safe
        "enable_pkcs11": [True, False],
        "enable_tpm2": [True, False],

        # Performance optimization
        "enable_lto": [True, False],  # Link-time optimization
        "enable_pgo": [True, False],  # Profile-guided optimization
        "vector_instructions": ["none", "sse2", "avx2", "avx512"],
        "optimization_level": ["none", "size", "speed", "max"],

        # Security features
        "enable_asan": [True, False],  # Address sanitizer
        "enable_ubsan": [True, False],  # Undefined behavior sanitizer

        # Testing and validation
        "enable_tests": [True, False],
        "enable_comprehensive_tests": [True, False],

        # Monitoring
        "enable_metrics": [True, False],
        "enable_dashboard": [True, False],
    }

    default_options = {
        # Core defaults
        "shared": True,
        "fPIC": True,

        # Provider defaults (most common enterprise setup)
        "enable_providers": True,
        "enable_fips": True,
        "enable_oqs": False,
        "enable_pkcs11": False,
        "enable_tpm2": False,

        # Performance defaults (balanced)
        "enable_lto": False,
        "enable_pgo": False,
        "vector_instructions": "avx2",
        "optimization_level": "speed",

        # Security defaults (development)
        "enable_asan": False,
        "enable_ubsan": False,

        # Testing defaults
        "enable_tests": True,
        "enable_comprehensive_tests": False,

        # Monitoring defaults
        "enable_metrics": True,
        "enable_dashboard": False,
    }

    # All dependencies for complete functionality
    requires = [
        "openssl-base/1.0.1@sparesparrow/stable",
        "openssl-fips-data/140-3.2@sparesparrow/stable",
        "openssl-providers/3.5.2@sparesparrow/stable",
        "openssl-optimization/3.5.2@sparesparrow/stable",
        "openssl-monitoring/3.5.2@sparesparrow/stable",
        "openssl-compliance/3.5.2@sparesparrow/stable",
    ]

    def init(self):
        """Initialize with proper channel"""
        if not os.getenv("CONAN_CHANNEL"):
            self.user = "sparesparrow"
            self.channel = "stable"

    def layout(self):
        """Define package layout"""
        basic_layout(self)

    def configure(self):
        """Configure package options"""
        # Static builds need fPIC
        if not self.options.shared:
            self.options.fPIC = True

        # FIPS requires providers
        if self.options.enable_fips:
            self.options.enable_providers = True

        # Quantum-safe requires providers
        if self.options.enable_oqs:
            self.options.enable_providers = True

    def requirements(self):
        """Require all enhanced components"""
        # Core dependencies already defined in class attribute
        pass

    def build(self):
        """Build OpenSSL 3.5.2 with complete feature set"""
        self.output.info("Building OpenSSL 3.5.2 Complete with full provider architecture")

        # Import all enhanced build tools
        from openssl_tools.automation.build_orchestrator import OpenSSLBuildOrchestrator
        from openssl_tools.providers.provider_manager import OpenSSLProviderManager
        from openssl_tools.optimization.build_optimizer import OpenSSLBuildOptimizer
        from openssl_tools.monitoring.metrics_collector import MetricsCollector
        from openssl_tools.compliance.standards_validator import StandardsValidator

        # Initialize all components
        orchestrator = OpenSSLBuildOrchestrator(self)
        provider_manager = OpenSSLProviderManager(self)
        optimizer = OpenSSLBuildOptimizer(self)
        metrics = MetricsCollector(self)
        validator = StandardsValidator(self)

        # Get base configuration
        configure_args = orchestrator.get_configure_args()

        # Add provider architecture
        if self.options.enable_providers:
            provider_args = provider_manager.get_provider_args()
            configure_args.extend(provider_args)
            self.output.info("Complete provider architecture enabled")

        # Add quantum-safe support
        if self.options.enable_oqs:
            configure_args.extend(["enable-oqs", "enable-oqs-provider"])
            self.output.info("Quantum-safe cryptography enabled")

        # Add PKCS11 support
        if self.options.enable_pkcs11:
            configure_args.extend(["enable-pkcs11", "enable-pkcs11-provider"])
            self.output.info("PKCS11 provider enabled")

        # Add TPM2 support
        if self.options.enable_tpm2:
            configure_args.extend(["enable-tpm2", "enable-tpm2-provider"])
            self.output.info("TPM2 provider enabled")

        # Add FIPS support
        if self.options.enable_fips:
            configure_args.append("enable-fips")
            self.output.info("FIPS 140-3 mode enabled - certificate #4985")

        # Add optimization flags
        optimization_args = optimizer.get_optimization_args()
        configure_args.extend(optimization_args)

        # Configure OpenSSL 3.5.2 with all features
        configure_cmd = f"./Configure {' '.join(configure_args)}"
        self.run(configure_cmd, cwd=self.source_folder)

        # Build with monitoring
        metrics.start_build_monitoring()
        orchestrator.build()
        metrics.end_build_monitoring()

        # Run comprehensive tests if enabled
        if self.options.enable_tests:
            self.output.info("Running OpenSSL 3.5.2 comprehensive tests")
            if self.options.enable_comprehensive_tests:
                orchestrator.run_comprehensive_tests()
            else:
                orchestrator.run_tests()

        # Validate compliance
        if self.options.enable_fips:
            validator.validate_fips_compliance()
        validator.validate_standards_compliance()

    def package(self):
        """Package OpenSSL 3.5.2 Complete"""
        # Use enhanced packaging from tools
        from openssl_tools.automation.package_manager import OpenSSLPackageManager

        package_manager = OpenSSLPackageManager(self)
        package_manager.create_enhanced_package()

    def package_info(self):
        """Complete package information for OpenSSL 3.5.2"""
        self.cpp_info.set_property("cmake_file_name", "OpenSSL")
        self.cpp_info.set_property("cmake_target_name", "OpenSSL::OpenSSL")

        # Set OpenSSL 3.5.2 version properties
        self.cpp_info.set_property("openssl_version", "3.5.2")
        self.cpp_info.set_property("openssl_provider_architecture", "true")
        self.cpp_info.set_property("openssl_enhanced_features", "true")

        # Libraries with complete feature set
        self.cpp_info.libs = ["ssl", "crypto"]

        # Add provider libraries
        if self.options.enable_fips:
            self.cpp_info.libs.append("fips")
        if self.options.enable_oqs:
            self.cpp_info.libs.append("oqs")
        if self.options.enable_pkcs11:
            self.cpp_info.libs.append("pkcs11")

        # Enhanced paths
        self.cpp_info.bindirs = ["bin"]
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.libdirs = ["lib"]

        # Provider module paths
        if self.options.enable_providers:
            self.cpp_info.libdirs.append("lib/ossl-modules")
            self.cpp_info.libdirs.append("lib/providers")

        # System dependencies
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["dl", "pthread"])
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["ws2_32", "gdi32", "advapi32", "crypt32", "user32"])
        elif self.settings.os == "Macos":
            self.cpp_info.frameworks.append("Security")

        # Enhanced environment configuration
        self.runenv_info.prepend_path("PATH", os.path.join(self.package_folder, "bin"))

        # Provider configuration
        if self.options.enable_fips:
            self.runenv_info.define("OPENSSL_CONF", os.path.join(self.package_folder, "ssl", "openssl.cnf"))
            self.runenv_info.define("OPENSSL_MODULES", os.path.join(self.package_folder, "lib", "ossl-modules"))

        # Optimization information
        self.runenv_info.define("OPENSSL_OPTIMIZATION_LEVEL", self.options.optimization_level)
        self.runenv_info.define("OPENSSL_VECTOR_INSTRUCTIONS", self.options.vector_instructions)

        # Feature flags for applications
        self.cpp_info.set_property("fips_enabled", str(self.options.enable_fips))
        self.cpp_info.set_property("providers_enabled", str(self.options.enable_providers))
        self.cpp_info.set_property("oqs_enabled", str(self.options.enable_oqs))
        self.cpp_info.set_property("quantum_safe_ready", str(self.options.enable_oqs))
        self.cpp_info.set_property("enterprise_ready", "true")

        # Monitoring configuration
        if self.options.enable_metrics:
            self.runenv_info.define("OPENSSL_METRICS_ENABLED", "1")
        if self.options.enable_dashboard:
            self.runenv_info.define("OPENSSL_DASHBOARD_PORT", "8080")

    def package_id(self):
        """Package ID for OpenSSL 3.5.2 Complete"""
        # Include all options in package ID for precise builds
        pass

    def validate(self):
        """Validate OpenSSL 3.5.2 Complete configuration"""
        # Ensure at least basic provider support for 3.5.2
        if not self.options.enable_providers:
            self.output.warn("OpenSSL 3.5.2 should have provider support enabled for full functionality")

        # Validate feature combinations
        if self.options.enable_oqs and not self.options.enable_providers:
            raise Exception("Quantum-safe (OQS) requires provider architecture")

        if self.options.enable_fips and not self.options.enable_providers:
            raise Exception("FIPS mode requires provider architecture")
