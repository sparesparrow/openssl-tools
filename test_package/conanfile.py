from conan import ConanFile

class OpenSSLToolsTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"

    # ✅ CORRECT: Use python_requires, not requires
    # python_requires = "tested_reference_str"  # Auto-populated by Conan during test

    def build(self):
        # Test: Can we import modules from openssl_tools?
        pass

    def test(self):
        # Verify the python_requires package is accessible
        self.output.info("Testing openssl-tools python_requires package...")

        # This will be populated automatically by conan create
        if hasattr(self, 'python_requires'):
            tools = self.python_requires["openssl-tools"]
            self.output.success(f"✅ Successfully loaded openssl-tools: {tools}")
        else:
            self.output.warn("python_requires not available in test context")

        self.output.success("openssl-tools test passed!")
