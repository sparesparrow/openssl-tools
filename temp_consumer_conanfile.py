"""
Temporary Consumer Conanfile
Tests importing openssl-tools/0.1.0 as python_requires
"""

from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake
from conan.tools.layout import basic_layout

# Import shared utilities from openssl-tools
python_requires = "openssl-tools/0.1.0"

class TempConsumerConan(ConanFile):
    name = "temp-consumer"
    version = "1.0.0"
    description = "Temporary consumer to test openssl-tools python_requires"
    license = "MIT"
    topics = ("test", "consumer", "python-requires")

    settings = "os", "compiler", "build_type", "arch"

    def configure(self):
        """Configure the consumer"""
        # Test that we can access shared utilities
        try:
            # Import the shared utilities that should be available via python_requires
            from openssl_tools import setup_logging, ConfigManager, ArtifactoryHandler
            print("✅ Successfully imported shared utilities from openssl-tools")

            # Test logging setup
            logger = setup_logging("INFO")
            logger.info("Logging setup successful")

            # Test ConfigManager
            config = ConfigManager()
            print("✅ ConfigManager instantiated successfully")

            # Test ArtifactoryHandler (will fail without config, but import should work)
            print("✅ ArtifactoryHandler import successful")

        except ImportError as e:
            self.output.error(f"Failed to import shared utilities: {e}")
            raise

    def layout(self):
        basic_layout(self)

    def generate(self):
        """Generate build files"""
        # Test that python_requires utilities are available during generation
        try:
            from openssl_tools import get_logger
            logger = get_logger("consumer")
            logger.info("Python requires utilities available in generate()")
        except ImportError as e:
            self.output.warn(f"Utilities not available in generate(): {e}")

    def build(self):
        """Build the consumer"""
        # Test utilities during build
        try:
            from openssl_tools import __version__
            self.output.info(f"Using openssl-tools version: {__version__}")
        except ImportError as e:
            self.output.warn(f"Version info not available: {e}")

    def package_info(self):
        """Package info"""
        self.output.info("Consumer package_info executed successfully")

if __name__ == "__main__":
    # Test direct execution
    print("🧪 Testing python_requires import...")
    try:
        from openssl_tools import setup_logging, ConfigManager
        print("✅ Direct import successful")
    except ImportError as e:
        print(f"❌ Direct import failed: {e}")
        print("Note: This is expected when python_requires is not resolved by Conan")