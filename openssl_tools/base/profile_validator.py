"""
Profile validation for OpenSSL builds
"""

from conan.errors import ConanInvalidConfiguration


class ProfileValidator:
    """Validates OpenSSL configuration options"""

    def __init__(self, conanfile):
        self.conanfile = conanfile

    def validate_all(self):
        """Validate all configuration options"""

        # FIPS validation
        if hasattr(self.conanfile.options, 'fips') and self.conanfile.options.fips:
            if hasattr(self.conanfile.options, 'shared') and self.conanfile.options.shared:
                raise ConanInvalidConfiguration(
                    "FIPS mode requires static linking for security compliance. "
                    "Set 'shared=False' or disable FIPS mode."
                )

        # Thread validation
        if hasattr(self.conanfile.options, 'no_threads') and self.conanfile.options.no_threads:
            if hasattr(self.conanfile.options, 'shared') and self.conanfile.options.shared:
                raise ConanInvalidConfiguration(
                    "no_threads option requires static linking to avoid threading issues. "
                    "Set 'shared=False' or disable no_threads."
                )

        # ASM validation
        if hasattr(self.conanfile.options, 'no_asm') and self.conanfile.options.no_asm:
            if hasattr(self.conanfile.options, 'shared') and self.conanfile.options.shared:
                raise ConanInvalidConfiguration(
                    "no_asm option requires static linking for cross-platform compatibility. "
                    "Set 'shared=False' or disable no_asm."
                )

        # Auto-enable fPIC for static libraries
        if hasattr(self.conanfile.options, 'shared') and not self.conanfile.options.shared:
            self.conanfile.options.fPIC = True
