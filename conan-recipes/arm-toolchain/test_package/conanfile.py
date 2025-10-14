from io import StringIO
import os
from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeToolchain", "VirtualBuildEnv"

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not self.settings.os == "Linux":
            return
        if self.settings.arch in ["armv6", "armv7", "armv7hf"]:
            triplet = "arm-none-linux-gnueabihf"
        else:
            triplet = "aarch64-none-linux-gnu"
        # Verify toolchain is available and prints version
        self.run(f"{triplet}-gcc --version")
        # Verify built binary exists and ELF bitness matches
        test_bin = os.path.join(self.cpp.build.bindirs[0], "test_package")
        out = StringIO()
        self.run(f"file {test_bin}", stdout=out)
        if triplet == "aarch64-none-linux-gnu":
            assert "ELF 64-bit" in out.getvalue()
        else:
            assert "ELF 32-bit" in out.getvalue()
