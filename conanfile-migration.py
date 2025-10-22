"""
OpenSSL Migration Package
Tools for migrating from older OpenSSL versions to 3.5.2 with provider architecture
"""

import os
from conan import ConanFile
from conan.tools.files import copy
from conan.tools.layout import basic_layout


class OpenSSLMigrationConan(ConanFile):
    name = "openssl-migration"
    version = "3.5.2"
    description = "OpenSSL migration tools for upgrading to 3.5.2 provider architecture"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/openssl-tools"
    homepage = "https://github.com/sparesparrow/openssl-tools"
    topics = ("openssl", "migration", "upgrade", "3.5.2", "providers", "legacy")

    # Package settings
    settings = "os", "arch", "compiler", "build_type"
    package_type = "python-require"

    # Migration options
    options = {
        "migrate_from_version": ["1.1.1", "3.0", "3.1", "3.2", "3.3", "3.4"],
        "generate_compatibility_layer": [True, False],
        "create_migration_guide": [True, False],
        "validate_migration": [True, False],
        "backup_existing_config": [True, False],
        "enable_deprecation_warnings": [True, False],
    }
    default_options = {
        "migrate_from_version": "3.0",
        "generate_compatibility_layer": True,
        "create_migration_guide": True,
        "validate_migration": True,
        "backup_existing_config": True,
        "enable_deprecation_warnings": False,
    }

    # Export sources
    exports_sources = (
        "openssl_tools/migration/*",
        "scripts/migration/*",
        "templates/migration/*",
        "compatibility/*",
        "migration-guides/*",
        "*.md"
    )

    def init(self):
        """Initialize with proper channel"""
        if not os.getenv("CONAN_CHANNEL"):
            self.user = "sparesparrow"
            self.channel = "stable"

    def requirements(self):
        """Migration package depends on foundation and validation"""
        self.requires("openssl-base/1.0.1@sparesparrow/stable")
        self.requires("openssl-validation/1.0.0@sparesparrow/stable")

    def layout(self):
        """Define package layout"""
        basic_layout(self)

    def package(self):
        """Package migration components"""
        # Copy migration modules
        copy(self, "*", src=os.path.join(self.source_folder, "openssl_tools/migration"),
             dst=os.path.join(self.package_folder, "openssl_tools/migration"), keep_path=True)

        # Copy migration scripts
        copy(self, "*", src=os.path.join(self.source_folder, "scripts/migration"),
             dst=os.path.join(self.package_folder, "scripts/migration"), keep_path=True)

        # Copy migration templates
        copy(self, "*", src=os.path.join(self.source_folder, "templates/migration"),
             dst=os.path.join(self.package_folder, "templates/migration"), keep_path=True)

        # Copy compatibility layers
        copy(self, "*", src=os.path.join(self.source_folder, "compatibility"),
             dst=os.path.join(self.package_folder, "compatibility"), keep_path=True)

        # Copy migration guides
        copy(self, "*", src=os.path.join(self.source_folder, "migration-guides"),
             dst=os.path.join(self.package_folder, "migration-guides"), keep_path=True)

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
        self.runenv_info.define("OPENSSL_MIGRATION_ROOT", self.package_folder)
        self.runenv_info.define("OPENSSL_MIGRATE_FROM_VERSION", self.options.migrate_from_version)
        self.runenv_info.define("OPENSSL_MIGRATION_VERSION", self.version)

        # Feature flags
        if self.options.generate_compatibility_layer:
            self.runenv_info.define("OPENSSL_COMPATIBILITY_LAYER", "1")
        if self.options.create_migration_guide:
            self.runenv_info.define("OPENSSL_MIGRATION_GUIDE", "1")
        if self.options.validate_migration:
            self.runenv_info.define("OPENSSL_MIGRATION_VALIDATION", "1")
        if self.options.backup_existing_config:
            self.runenv_info.define("OPENSSL_BACKUP_CONFIG", "1")
        if self.options.enable_deprecation_warnings:
            self.runenv_info.define("OPENSSL_DEPRECATION_WARNINGS", "1")

        # Python path for migration modules
        self.runenv_info.prepend_path("PYTHONPATH", os.path.join(self.package_folder, "openssl_tools/migration"))

        # PATH for migration scripts
        self.env_info.PATH.append(os.path.join(self.package_folder, "scripts/migration"))

    def package_id(self):
        """Package ID mode for migration packages"""
        self.info.clear()
