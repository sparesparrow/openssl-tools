"""
OpenSSL Documentation Package
Automated documentation generation, API docs, and knowledge base tools
"""

import os
from conan import ConanFile
from conan.tools.files import copy
from conan.tools.layout import basic_layout


class OpenSSLDocumentationConan(ConanFile):
    name = "openssl-documentation"
    version = "3.5.2"
    description = "OpenSSL automated documentation and API reference generation tools"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/openssl-tools"
    homepage = "https://github.com/sparesparrow/openssl-tools"
    topics = ("openssl", "documentation", "api-docs", "knowledge-base", "sphinx")

    # Package settings
    settings = "os", "arch", "compiler", "build_type"
    package_type = "python-require"

    # Documentation options
    options = {
        "generate_api_docs": [True, False],
        "generate_user_guides": [True, False],
        "generate_developer_docs": [True, False],
        "generate_compliance_docs": [True, False],
        "enable_search_index": [True, False],
        "enable_versioned_docs": [True, False],
        "doc_format": ["html", "pdf", "markdown", "rst"],
        "include_examples": [True, False],
    }
    default_options = {
        "generate_api_docs": True,
        "generate_user_guides": True,
        "generate_developer_docs": True,
        "generate_compliance_docs": False,
        "enable_search_index": True,
        "enable_versioned_docs": False,
        "doc_format": "html",
        "include_examples": True,
    }

    # Export sources
    exports_sources = (
        "openssl_tools/documentation/*",
        "docs/*",
        "sphinx/*",
        "templates/docs/*",
        "examples/*",
        "*.md"
    )

    def init(self):
        """Initialize with proper channel"""
        if not os.getenv("CONAN_CHANNEL"):
            self.user = "sparesparrow"
            self.channel = "stable"

    def requirements(self):
        """Documentation package depends on foundation"""
        self.requires("openssl-base/1.0.1@sparesparrow/stable")

    def layout(self):
        """Define package layout"""
        basic_layout(self)

    def package(self):
        """Package documentation components"""
        # Copy documentation modules
        copy(self, "*", src=os.path.join(self.source_folder, "openssl_tools/documentation"),
             dst=os.path.join(self.package_folder, "openssl_tools/documentation"), keep_path=True)

        # Copy documentation templates
        copy(self, "*", src=os.path.join(self.source_folder, "templates/docs"),
             dst=os.path.join(self.package_folder, "templates/docs"), keep_path=True)

        # Copy Sphinx configuration
        copy(self, "*", src=os.path.join(self.source_folder, "sphinx"),
             dst=os.path.join(self.package_folder, "sphinx"), keep_path=True)

        # Copy documentation sources
        copy(self, "*", src=os.path.join(self.source_folder, "docs"),
             dst=os.path.join(self.package_folder, "docs"), keep_path=True)

        # Copy examples for documentation
        copy(self, "*", src=os.path.join(self.source_folder, "examples"),
             dst=os.path.join(self.package_folder, "examples"), keep_path=True)

        # Copy documentation files
        copy(self, "*.md", src=self.source_folder,
             dst=os.path.join(self.package_folder, "docs"))
        copy(self, "LICENSE*", src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        """Define package information"""
        # No C++ components
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.includedirs = []

        # Environment variables
        self.runenv_info.define("OPENSSL_DOCS_ROOT", self.package_folder)
        self.runenv_info.define("OPENSSL_DOCS_FORMAT", self.options.doc_format)
        self.runenv_info.define("OPENSSL_DOCS_VERSION", self.version)

        # Feature flags
        if self.options.generate_api_docs:
            self.runenv_info.define("OPENSSL_GENERATE_API_DOCS", "1")
        if self.options.generate_user_guides:
            self.runenv_info.define("OPENSSL_GENERATE_USER_GUIDES", "1")
        if self.options.generate_developer_docs:
            self.runenv_info.define("OPENSSL_GENERATE_DEV_DOCS", "1")
        if self.options.generate_compliance_docs:
            self.runenv_info.define("OPENSSL_GENERATE_COMPLIANCE_DOCS", "1")
        if self.options.enable_search_index:
            self.runenv_info.define("OPENSSL_ENABLE_SEARCH_INDEX", "1")
        if self.options.enable_versioned_docs:
            self.runenv_info.define("OPENSSL_ENABLE_VERSIONED_DOCS", "1")
        if self.options.include_examples:
            self.runenv_info.define("OPENSSL_INCLUDE_EXAMPLES", "1")

        # Python path for documentation modules
        self.runenv_info.prepend_path("PYTHONPATH", os.path.join(self.package_folder, "openssl_tools/documentation"))

        # PATH for documentation scripts
        self.env_info.PATH.append(os.path.join(self.package_folder, "docs"))

    def package_id(self):
        """Package ID mode for documentation packages"""
        self.info.clear()
