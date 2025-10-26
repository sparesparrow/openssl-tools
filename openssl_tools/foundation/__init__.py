"""
OpenSSL Tools Foundation Module

Core foundation utilities for OpenSSL Conan ecosystem.
"""

from .version_manager import get_openssl_version, parse_openssl_version
from .profile_deployer import deploy_openssl_profiles, list_openssl_profiles
from .build_orchestrator import OpenSSLBuildOrchestrator
from .base_recipe import OpenSSLRecipeBase

# Import base classes for recipe extension
from ..base.profile_validator import ProfileValidator
from ..base.sbom_generator import SbomGenerator
from ..base.database_tracker import DatabaseTracker
from ..base.version_manager import VersionManager

__all__ = [
    'get_openssl_version',
    'parse_openssl_version',
    'deploy_openssl_profiles',
    'list_openssl_profiles',
    'OpenSSLBuildOrchestrator',
    'OpenSSLRecipeBase',
    'ProfileValidator',
    'SbomGenerator',
    'DatabaseTracker',
    'VersionManager'
]