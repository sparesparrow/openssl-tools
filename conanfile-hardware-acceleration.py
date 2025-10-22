"""
OpenSSL Hardware Acceleration Package
GPU and hardware-accelerated cryptography tools and optimizations
"""

import os
from conan import ConanFile
from conan.tools.files import copy
from conan.tools.layout import basic_layout


class OpenSSLHardwareAccelerationConan(ConanFile):
    name = "openssl-hardware-acceleration"
    version = "3.5.2"
    description = "OpenSSL hardware-accelerated cryptography and GPU optimization tools"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/openssl-tools"
    homepage = "https://github.com/sparesparrow/openssl-tools"
    topics = ("openssl", "hardware", "acceleration", "gpu", "crypto", "optimization")

    # Package settings
    settings = "os", "arch", "compiler", "build_type"
    package_type = "python-require"

    # Hardware acceleration options
    options = {
        "enable_gpu_acceleration": [True, False],
        "enable_intel_qat": [True, False],
        "enable_nvidia_gpu": [True, False],
        "enable_amd_gpu": [True, False],
        "enable_fpga_acceleration": [True, False],
        "enable_asic_optimization": [True, False],
        "hardware_benchmarking": [True, False],
        "auto_detect_hardware": [True, False],
    }
    default_options = {
        "enable_gpu_acceleration": False,
        "enable_intel_qat": False,
        "enable_nvidia_gpu": False,
        "enable_amd_gpu": False,
        "enable_fpga_acceleration": False,
        "enable_asic_optimization": False,
        "hardware_benchmarking": True,
        "auto_detect_hardware": True,
    }

    # Export sources
    exports_sources = (
        "openssl_tools/hardware_acceleration/*",
        "hardware/*",
        "gpu/*",
        "acceleration/*",
        "benchmarks/hardware/*",
        "*.md"
    )

    def init(self):
        """Initialize with proper channel"""
        if not os.getenv("CONAN_CHANNEL"):
            self.user = "sparesparrow"
            self.channel = "stable"

    def requirements(self):
        """Hardware acceleration depends on foundation and benchmarking"""
        self.requires("openssl-base/1.0.1@sparesparrow/stable")
        self.requires("openssl-benchmarking/3.5.2@sparesparrow/stable")

    def layout(self):
        """Define package layout"""
        basic_layout(self)

    def package(self):
        """Package hardware acceleration components"""
        # Copy hardware acceleration modules
        copy(self, "*", src=os.path.join(self.source_folder, "openssl_tools/hardware_acceleration"),
             dst=os.path.join(self.package_folder, "openssl_tools/hardware_acceleration"), keep_path=True)

        # Copy hardware configurations
        copy(self, "*", src=os.path.join(self.source_folder, "hardware"),
             dst=os.path.join(self.package_folder, "hardware"), keep_path=True)

        # Copy GPU acceleration configs
        copy(self, "*", src=os.path.join(self.source_folder, "gpu"),
             dst=os.path.join(self.package_folder, "gpu"), keep_path=True)

        # Copy acceleration optimizations
        copy(self, "*", src=os.path.join(self.source_folder, "acceleration"),
             dst=os.path.join(self.package_folder, "acceleration"), keep_path=True)

        # Copy hardware benchmarks
        copy(self, "*", src=os.path.join(self.source_folder, "benchmarks/hardware"),
             dst=os.path.join(self.package_folder, "benchmarks/hardware"), keep_path=True)

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
        self.runenv_info.define("OPENSSL_HARDWARE_ROOT", self.package_folder)
        self.runenv_info.define("OPENSSL_HARDWARE_VERSION", self.version)

        # Hardware acceleration flags
        if self.options.enable_gpu_acceleration:
            self.runenv_info.define("OPENSSL_GPU_ACCELERATION", "1")
        if self.options.enable_intel_qat:
            self.runenv_info.define("OPENSSL_INTEL_QAT", "1")
        if self.options.enable_nvidia_gpu:
            self.runenv_info.define("OPENSSL_NVIDIA_GPU", "1")
        if self.options.enable_amd_gpu:
            self.runenv_info.define("OPENSSL_AMD_GPU", "1")
        if self.options.enable_fpga_acceleration:
            self.runenv_info.define("OPENSSL_FPGA_ACCELERATION", "1")
        if self.options.enable_asic_optimization:
            self.runenv_info.define("OPENSSL_ASIC_OPTIMIZATION", "1")
        if self.options.hardware_benchmarking:
            self.runenv_info.define("OPENSSL_HARDWARE_BENCHMARKING", "1")
        if self.options.auto_detect_hardware:
            self.runenv_info.define("OPENSSL_AUTO_DETECT_HARDWARE", "1")

        # Python path for hardware acceleration modules
        self.runenv_info.prepend_path("PYTHONPATH", os.path.join(self.package_folder, "openssl_tools/hardware_acceleration"))

        # PATH for hardware acceleration scripts
        self.env_info.PATH.append(os.path.join(self.package_folder, "hardware"))

    def package_id(self):
        """Package ID mode for hardware acceleration packages"""
        self.info.clear()
