"""
Base recipe class for OpenSSL Conan recipes
"""

from conan import ConanFile


class OpenSSLRecipeBase:
    """Base class providing common functionality for OpenSSL recipes"""

    def __init__(self, conanfile: ConanFile):
        self.conanfile = conanfile

    @property
    def version_manager(self):
        """Access to version management functionality"""
        from ..base.version_manager import version_manager
        return version_manager
