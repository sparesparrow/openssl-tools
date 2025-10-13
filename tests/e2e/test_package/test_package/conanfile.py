from conans import ConanFile, tools
import os

class OpenSSLToolsTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "virtualenv"
    requires = "openssl-tools/1.0.0@"
    
    def build(self):
        pass
    
    def test(self):
        # Test that openssl-tools is available
        self.run("python -c 'import openssl_tools; print(openssl_tools.__version__)'", run_environment=True)
        
        # Test that tools are available
        self.run("python -c 'from openssl_tools import review_tools, release_tools, statistics; print("Tools imported successfully")'", run_environment=True)
        
        # Test environment variables
        openssl_tools_root = os.environ.get("OPENSSL_TOOLS_ROOT")
        if not openssl_tools_root:
            raise Exception("OPENSSL_TOOLS_ROOT environment variable not set")
        
        print(f"OpenSSL Tools Root: {openssl_tools_root}")
        print("Test package executed successfully!")
