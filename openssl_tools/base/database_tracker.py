"""
Database tracking for OpenSSL packages
"""

from pathlib import Path


class DatabaseTracker:
    """Tracks OpenSSL packages in the database"""

    def __init__(self, conanfile):
        self.conanfile = conanfile

    def track_package(self):
        """Track package in database"""
        try:
            from ..database.openssl_schema_validator import OpenSSLSchemaValidator

            validator = OpenSSLSchemaValidator(Path.cwd())
            package_info = {
                "name": self.conanfile.name,
                "version": self.conanfile.version,
                "user": "sparesparrow",
                "channel": "stable",
                "package_id": self.conanfile.info.package_id,
                "config": {
                    "shared": bool(getattr(self.conanfile.options, 'shared', True)),
                    "fips": bool(getattr(self.conanfile.options, 'fips', False)),
                    "no_asm": bool(getattr(self.conanfile.options, 'no_asm', False)),
                    "deployment_target": "fips-government" if getattr(self.conanfile.options, 'fips', False) else "general"
                }
            }
            validator.track_package_in_cache(package_info, "domain")
        except Exception as e:
            self.conanfile.output.warning(f"Package tracking failed: {e}")
