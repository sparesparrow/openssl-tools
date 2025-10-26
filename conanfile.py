from conan import ConanFile
from conan.tools.files import copy
import os
from pathlib import Path

class OpenSSLToolsConan(ConanFile):
    name = "openssl-tools"
    version = "2.2.2"
    description = "OpenSSL build tools, automation scripts, and infrastructure components"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/openssl-tools"
    homepage = "https://github.com/sparesparrow/openssl-tools"
    topics = ("openssl", "build-tools", "automation", "ci-cd")

    # Package settings
    package_type = "python-require"
    # Note: python-require packages should not have settings (binary-agnostic)

    # Export sources
    exports_sources = (
        "scripts/*",
        "templates/*",
        "openssl_tools/**",
        "src/*",
        "*.md",
        "pyproject.toml"
    )

    python_requires = "openssl-base/1.0.0"

    def init(self):
        """Initialize with version fallback logic."""
        # Implement version fallback for OpenSSL 4.0.0 → 3.6.0 compatibility
        self._setup_version_fallback()

    def _setup_version_fallback(self):
        """Set up version compatibility matrix with fallback logic."""
        # Version compatibility matrix
        self._version_matrix = {
            "4.0.0": ["4.0.0", "3.6.0"],  # Try 4.0.0 first, fallback to 3.6.0
            "3.6.0": ["3.6.0"],           # Only 3.6.0
            "3.4.1": ["3.4.1"],           # Only 3.4.1
        }

        # Set default version to latest available
        self._default_versions = ["4.0.0", "3.6.0", "3.4.1"]

    def _get_available_version(self):
        """Get the best available OpenSSL version based on fallback logic."""
        try:
            # Try to import version manager from python_requires
            VersionManager = self.python_requires["openssl-base"].module.VersionManager
            version_manager = VersionManager()

            # Check version availability in order of preference
            for target_version in self._default_versions:
                if version_manager.is_version_available(target_version):
                    return target_version

            # Fallback to hardcoded version if version manager fails
            return "3.6.0"
        except Exception as e:
            self.output.warning(f"Version detection failed: {e}, using fallback 3.6.0")
            return "3.6.0"

    def package(self):
        """Package orchestration components"""

        # Copy the Python package
        copy(self, "openssl_tools/*",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "python"))

        # Copy Python script replacements
        copy(self, "src/*",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "python"))

        # Copy license and readme
        copy(self, "LICENSE*",
             src=self.source_folder,
             dst=self.package_folder,
             keep_path=False)
        copy(self, "README*",
             src=self.source_folder,
             dst=self.package_folder,
             keep_path=False)

        # Track in database
        try:
            from openssl_tools.database.openssl_schema_validator import OpenSSLSchemaValidator
            validator = OpenSSLSchemaValidator(Path.cwd())
            package_info = {
                "name": self.name,
                "version": self.version,
                "user": "sparesparrow",
                "channel": "stable",
                "package_id": str(self.info.package_id()),
                "config": {"package_type": self.package_type}
            }
            validator.track_package_in_cache(package_info, "tooling")
        except Exception as e:
            self.output.warning(f"Package tracking failed: {e}")

    def package_info(self):
        """Package information for consumers"""
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.includedirs = []

        python_path = os.path.join(self.package_folder, "python")
        self.runenv_info.define("PYTHONPATH", python_path)
        self.cpp_info.set_property("pkg_config_name", "openssl-tools")
        self.runenv_info.define("OPENSSL_TOOLS_VERSION", self.version)
        self.runenv_info.define("OPENSSL_TOOLS_ROOT", self.package_folder)
