from conan import ConanFile

class TestPackage(ConanFile):
    python_requires = "openssl-tools/1.2.0"
    
    def test(self):
        # Ověř, že extensions jsou dostupné
        assert hasattr(self.python_requires["openssl-tools"], "build_openssl")

