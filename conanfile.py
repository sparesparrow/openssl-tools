from conan import ConanFile
from conan.tools.files import copy
import os
from pathlib import Path

class OpenSSLToolsConan(ConanFile):
    name = "openssl-tools"
    version = "2.2.0"
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
        "*.md",
        "pyproject.toml"
    )

    python_requires = "openssl-base/1.0.0@sparesparrow/stable"

    def package(self):
        """Package orchestration components"""

        # Copy the Python package
        copy(self, "openssl_tools/*",
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
