"""
Version management for OpenSSL builds
"""

import os
from pathlib import Path


class VersionManager:
    """Manages OpenSSL version detection and formatting"""

    @staticmethod
    def get_version(conanfile):
        """Get version from VERSION.dat or other sources"""
        # Check for VERSION.dat in recipe folder
        version_file = os.path.join(conanfile.recipe_folder, "VERSION.dat")
        if os.path.exists(version_file):
            return VersionManager._parse_version_file(version_file)

        # Check for VERSION.dat in source folder
        version_file = os.path.join(conanfile.source_folder, "VERSION.dat")
        if os.path.exists(version_file):
            return VersionManager._parse_version_file(version_file)

        # Fallback version
        return "4.0.0-dev"

    @staticmethod
    def _parse_version_file(version_file):
        """Parse VERSION.dat file format"""
        version_parts = {}

        try:
            with open(version_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if '=' in line:
                        key, value = line.split('=', 1)
                        version_parts[key] = value.strip('"')
        except Exception:
            # If parsing fails, return default
            return "4.0.0-dev"

        # Construct version string: MAJOR.MINOR.PATCH-PRE_RELEASE_TAG
        major = version_parts.get('MAJOR', '4')
        minor = version_parts.get('MINOR', '0')
        patch = version_parts.get('PATCH', '0')
        pre_release = version_parts.get('PRE_RELEASE_TAG', '')

        version = f"{major}.{minor}.{patch}"
        if pre_release:
            version += f"-{pre_release}"

        return version


# Create global instance for easy access
version_manager = VersionManager()
