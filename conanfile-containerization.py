"""
OpenSSL Containerization Package
Provides Docker and containerization support for OpenSSL deployments
"""

import os
from conan import ConanFile
from conan.tools.files import copy
from conan.tools.layout import basic_layout


class OpenSSLContainerizationConan(ConanFile):
    name = "openssl-containerization"
    version = "3.5.2"
    description = "OpenSSL Docker and containerization deployment tools"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/openssl-tools"
    homepage = "https://github.com/sparesparrow/openssl-tools"
    topics = ("openssl", "docker", "containerization", "deployment", "kubernetes")

    # Package settings
    settings = "os", "arch", "compiler", "build_type"
    package_type = "python-require"

    # Containerization options
    options = {
        "container_runtime": ["docker", "podman", "containerd"],
        "base_image": ["ubuntu", "alpine", "centos", "debian", "fedora"],
        "include_fips": [True, False],
        "include_providers": [True, False],
        "enable_multiarch": [True, False],
        "generate_kubernetes": [True, False],
        "generate_helm": [True, False],
        "enable_security_hardening": [True, False],
    }
    default_options = {
        "container_runtime": "docker",
        "base_image": "ubuntu",
        "include_fips": False,
        "include_providers": True,
        "enable_multiarch": False,
        "generate_kubernetes": False,
        "generate_helm": False,
        "enable_security_hardening": True,
    }

    # Export sources
    exports_sources = (
        "openssl_tools/containerization/*",
        "docker/*",
        "kubernetes/*",
        "helm/*",
        "container/*",
        "*.md"
    )

    def init(self):
        """Initialize with proper channel"""
        if not os.getenv("CONAN_CHANNEL"):
            self.user = "sparesparrow"
            self.channel = "stable"

    def requirements(self):
        """Containerization package depends on foundation and automation"""
        self.requires("openssl-base/1.0.1@sparesparrow/stable")
        self.requires("openssl-automation/1.0.0@sparesparrow/stable")

    def layout(self):
        """Define package layout"""
        basic_layout(self)

    def package(self):
        """Package containerization components"""
        # Copy containerization modules
        copy(self, "*", src=os.path.join(self.source_folder, "openssl_tools/containerization"),
             dst=os.path.join(self.package_folder, "openssl_tools/containerization"), keep_path=True)

        # Copy Docker configurations
        copy(self, "*", src=os.path.join(self.source_folder, "docker"),
             dst=os.path.join(self.package_folder, "docker"), keep_path=True)

        # Copy Kubernetes manifests
        copy(self, "*", src=os.path.join(self.source_folder, "kubernetes"),
             dst=os.path.join(self.package_folder, "kubernetes"), keep_path=True)

        # Copy Helm charts
        copy(self, "*", src=os.path.join(self.source_folder, "helm"),
             dst=os.path.join(self.package_folder, "helm"), keep_path=True)

        # Copy container templates
        copy(self, "*", src=os.path.join(self.source_folder, "container"),
             dst=os.path.join(self.package_folder, "container"), keep_path=True)

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
        self.runenv_info.define("OPENSSL_CONTAINER_ROOT", self.package_folder)
        self.runenv_info.define("OPENSSL_CONTAINER_RUNTIME", self.options.container_runtime)
        self.runenv_info.define("OPENSSL_BASE_IMAGE", self.options.base_image)
        self.runenv_info.define("OPENSSL_CONTAINER_VERSION", self.version)

        # Feature flags
        if self.options.include_fips:
            self.runenv_info.define("OPENSSL_CONTAINER_FIPS", "1")
        if self.options.include_providers:
            self.runenv_info.define("OPENSSL_CONTAINER_PROVIDERS", "1")
        if self.options.enable_multiarch:
            self.runenv_info.define("OPENSSL_MULTIARCH", "1")
        if self.options.generate_kubernetes:
            self.runenv_info.define("OPENSSL_KUBERNETES", "1")
        if self.options.generate_helm:
            self.runenv_info.define("OPENSSL_HELM", "1")
        if self.options.enable_security_hardening:
            self.runenv_info.define("OPENSSL_SECURITY_HARDENING", "1")

        # Python path for containerization modules
        self.runenv_info.prepend_path("PYTHONPATH", os.path.join(self.package_folder, "openssl_tools/containerization"))

        # PATH for containerization scripts
        self.env_info.PATH.append(os.path.join(self.package_folder, "docker"))

    def package_id(self):
        """Package ID mode for containerization packages"""
        self.info.clear()
