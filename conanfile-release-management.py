"""
OpenSSL Release Management Package
Automated release, versioning, and deployment tools
"""

import os
from conan import ConanFile
from conan.tools.files import copy
from conan.tools.layout import basic_layout


class OpenSSLReleaseManagementConan(ConanFile):
    name = "openssl-release-management"
    version = "3.5.2"
    description = "OpenSSL automated release and deployment management tools"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/openssl-tools"
    homepage = "https://github.com/sparesparrow/openssl-tools"
    topics = ("openssl", "release", "deployment", "versioning", "automation")

    # Package settings
    settings = "os", "arch", "compiler", "build_type"
    package_type = "python-require"

    # Release management options
    options = {
        "release_type": ["patch", "minor", "major", "prerelease"],
        "generate_changelog": [True, False],
        "create_git_tags": [True, False],
        "publish_artifacts": [True, False],
        "notify_stakeholders": [True, False],
        "create_release_notes": [True, False],
        "validate_release": [True, False],
        "rollback_support": [True, False],
    }
    default_options = {
        "release_type": "patch",
        "generate_changelog": True,
        "create_git_tags": True,
        "publish_artifacts": True,
        "notify_stakeholders": False,
        "create_release_notes": True,
        "validate_release": True,
        "rollback_support": True,
    }

    # Export sources
    exports_sources = (
        "openssl_tools/release_management/*",
        "scripts/release/*",
        "templates/release/*",
        "changelog/*",
        "release-notes/*",
        "*.md"
    )

    def init(self):
        """Initialize with proper channel"""
        if not os.getenv("CONAN_CHANNEL"):
            self.user = "sparesparrow"
            self.channel = "stable"

    def requirements(self):
        """Release management depends on foundation and automation"""
        self.requires("openssl-base/1.0.1@sparesparrow/stable")
        self.requires("openssl-automation/1.0.0@sparesparrow/stable")

    def layout(self):
        """Define package layout"""
        basic_layout(self)

    def package(self):
        """Package release management components"""
        # Copy release management modules
        copy(self, "*", src=os.path.join(self.source_folder, "openssl_tools/release_management"),
             dst=os.path.join(self.package_folder, "openssl_tools/release_management"), keep_path=True)

        # Copy release scripts
        copy(self, "*", src=os.path.join(self.source_folder, "scripts/release"),
             dst=os.path.join(self.package_folder, "scripts/release"), keep_path=True)

        # Copy release templates
        copy(self, "*", src=os.path.join(self.source_folder, "templates/release"),
             dst=os.path.join(self.package_folder, "templates/release"), keep_path=True)

        # Copy changelog tools
        copy(self, "*", src=os.path.join(self.source_folder, "changelog"),
             dst=os.path.join(self.package_folder, "changelog"), keep_path=True)

        # Copy release notes
        copy(self, "*", src=os.path.join(self.source_folder, "release-notes"),
             dst=os.path.join(self.package_folder, "release-notes"), keep_path=True)

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
        self.runenv_info.define("OPENSSL_RELEASE_ROOT", self.package_folder)
        self.runenv_info.define("OPENSSL_RELEASE_TYPE", self.options.release_type)
        self.runenv_info.define("OPENSSL_RELEASE_VERSION", self.version)

        # Feature flags
        if self.options.generate_changelog:
            self.runenv_info.define("OPENSSL_GENERATE_CHANGELOG", "1")
        if self.options.create_git_tags:
            self.runenv_info.define("OPENSSL_CREATE_GIT_TAGS", "1")
        if self.options.publish_artifacts:
            self.runenv_info.define("OPENSSL_PUBLISH_ARTIFACTS", "1")
        if self.options.notify_stakeholders:
            self.runenv_info.define("OPENSSL_NOTIFY_STAKEHOLDERS", "1")
        if self.options.create_release_notes:
            self.runenv_info.define("OPENSSL_CREATE_RELEASE_NOTES", "1")
        if self.options.validate_release:
            self.runenv_info.define("OPENSSL_VALIDATE_RELEASE", "1")
        if self.options.rollback_support:
            self.runenv_info.define("OPENSSL_ROLLBACK_SUPPORT", "1")

        # Python path for release management modules
        self.runenv_info.prepend_path("PYTHONPATH", os.path.join(self.package_folder, "openssl_tools/release_management"))

        # PATH for release scripts
        self.env_info.PATH.append(os.path.join(self.package_folder, "scripts/release"))

    def package_id(self):
        """Package ID mode for release management packages"""
        self.info.clear()
