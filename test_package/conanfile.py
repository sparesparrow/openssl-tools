from conan import ConanFile
from conan.tools.build import can_run
import os

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        """Run basic tests for openssl-tools"""
        if can_run(self):
            # Test Python module import
            self.run("python3 -c \"from openssl_tools.foundation import version_manager; print('Import successful')\"", env="conanrun")

            # Test environment variables
            self.run("python3 -c \"import os; print('OPENSSL_TOOLS_VERSION:', os.environ.get('OPENSSL_TOOLS_VERSION', 'Not set'))\"", env="conanrun")
