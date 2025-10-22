"""
OpenSSL Benchmarking Package
Provides comprehensive performance benchmarking and analysis tools
"""

import os
from conan import ConanFile
from conan.tools.files import copy
from conan.tools.layout import basic_layout


class OpenSSLBenchmarkingConan(ConanFile):
    name = "openssl-benchmarking"
    version = "3.5.2"
    description = "OpenSSL performance benchmarking and analysis tools"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/openssl-tools"
    homepage = "https://github.com/sparesparrow/openssl-tools"
    topics = ("openssl", "benchmarking", "performance", "analysis", "profiling")

    # Package settings
    settings = "os", "arch", "compiler", "build_type"
    package_type = "python-require"

    # Benchmarking options
    options = {
        "enable_detailed_profiling": [True, False],
        "enable_comparison_mode": [True, False],
        "enable_regression_testing": [True, False],
        "enable_visual_reports": [True, False],
        "benchmark_format": ["json", "csv", "html", "prometheus"],
        "profile_memory": [True, False],
        "profile_cpu": [True, False],
        "profile_io": [True, False],
    }
    default_options = {
        "enable_detailed_profiling": True,
        "enable_comparison_mode": True,
        "enable_regression_testing": False,
        "enable_visual_reports": True,
        "benchmark_format": "json",
        "profile_memory": True,
        "profile_cpu": True,
        "profile_io": False,
    }

    # Export sources
    exports_sources = (
        "openssl_tools/benchmarking/*",
        "scripts/benchmarking/*",
        "templates/benchmarking/*",
        "benchmarks/*",
        "*.md"
    )

    def init(self):
        """Initialize with proper channel"""
        if not os.getenv("CONAN_CHANNEL"):
            self.user = "sparesparrow"
            self.channel = "stable"

    def requirements(self):
        """Benchmarking package depends on foundation and monitoring"""
        self.requires("openssl-base/1.0.1@sparesparrow/stable")
        self.requires("openssl-monitoring/3.5.2@sparesparrow/stable")

    def layout(self):
        """Define package layout"""
        basic_layout(self)

    def package(self):
        """Package benchmarking components"""
        # Copy benchmarking modules
        copy(self, "*", src=os.path.join(self.source_folder, "openssl_tools/benchmarking"),
             dst=os.path.join(self.package_folder, "openssl_tools/benchmarking"), keep_path=True)

        # Copy benchmarking scripts
        copy(self, "*", src=os.path.join(self.source_folder, "scripts/benchmarking"),
             dst=os.path.join(self.package_folder, "scripts/benchmarking"), keep_path=True)

        # Copy benchmarking templates
        copy(self, "*", src=os.path.join(self.source_folder, "templates/benchmarking"),
             dst=os.path.join(self.package_folder, "templates/benchmarking"), keep_path=True)

        # Copy benchmark data
        copy(self, "*", src=os.path.join(self.source_folder, "benchmarks"),
             dst=os.path.join(self.package_folder, "benchmarks"), keep_path=True)

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
        self.runenv_info.define("OPENSSL_BENCHMARKING_ROOT", self.package_folder)
        self.runenv_info.define("OPENSSL_BENCHMARK_FORMAT", self.options.benchmark_format)
        self.runenv_info.define("OPENSSL_BENCHMARK_VERSION", self.version)

        # Feature flags
        if self.options.enable_detailed_profiling:
            self.runenv_info.define("OPENSSL_DETAILED_PROFILING", "1")
        if self.options.enable_comparison_mode:
            self.runenv_info.define("OPENSSL_COMPARISON_MODE", "1")
        if self.options.enable_regression_testing:
            self.runenv_info.define("OPENSSL_REGRESSION_TESTING", "1")
        if self.options.enable_visual_reports:
            self.runenv_info.define("OPENSSL_VISUAL_REPORTS", "1")
        if self.options.profile_memory:
            self.runenv_info.define("OPENSSL_PROFILE_MEMORY", "1")
        if self.options.profile_cpu:
            self.runenv_info.define("OPENSSL_PROFILE_CPU", "1")
        if self.options.profile_io:
            self.runenv_info.define("OPENSSL_PROFILE_IO", "1")

        # Python path for benchmarking modules
        self.runenv_info.prepend_path("PYTHONPATH", os.path.join(self.package_folder, "openssl_tools/benchmarking"))

        # PATH for benchmarking scripts
        self.env_info.PATH.append(os.path.join(self.package_folder, "scripts/benchmarking"))

    def package_id(self):
        """Package ID mode for benchmarking packages"""
        self.info.clear()
