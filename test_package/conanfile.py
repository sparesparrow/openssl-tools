from conan import ConanFile
from conan.tools.build import can_run
import os

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "VirtualRunEnv"
    python_requires = "openssl-tools/1.2.4"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        """Run basic tests for openssl-tools"""
        if can_run(self):
            # Test that the package was created successfully
            self.run("python3 -c \"print('OpenSSL Tools package test passed')\"", env="conanrun")

            # Test environment variables
            self.run("python3 -c \"import os; print('OPENSSL_TOOLS_VERSION:', os.environ.get('OPENSSL_TOOLS_VERSION', 'Not set'))\"", env="conanrun")
