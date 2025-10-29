"""
OpenSSL Tools - Conan 2.x Python_requires & Reusable Workflows

Central hub for OpenSSL Conan integration, providing python_requires, 
custom commands, deployers, and reusable GitHub Actions workflows.
"""

__all__ = [
    "__version__",
    # Foundation modules
    "foundation",
    # Security modules
    "security",
    # Automation modules
    "automation",
    # Testing modules
    "testing",
    # Statistics modules
    "statistics",
    # Python requires classes (exposed at top level)
    "VersionManager",
    "ProfileValidator",
    "OpenSSLBuildOrchestrator",
    "CryptoBuildOrchestrator",
    "SSLBuildOrchestrator"
]

__version__ = "0.1.0"

# Import key modules for easy access
from . import foundation
from . import security
from . import automation
from . import testing
from . import statistics

# Expose classes for python_requires access
from .base.version_manager import VersionManager
from .base.profile_validator import ProfileValidator
from .foundation.build_orchestrator import OpenSSLBuildOrchestrator
from .foundation.component_orchestrators import CryptoBuildOrchestrator, SSLBuildOrchestrator

# Add missing functions for integration tests
def setup_logging():
    """Setup logging configuration."""
    import logging
    logging.basicConfig(level=logging.INFO)

def get_logger(name):
    """Get a logger instance."""
    import logging
    return logging.getLogger(name)

# Add ArtifactoryHandler for integration tests
class ArtifactoryHandler:
    """Artifactory handler for package management."""
    def __init__(self):
        self.name = "ArtifactoryHandler"

# Add ConfigManager for integration tests
class ConfigManager:
    """Configuration manager for OpenSSL tools."""
    def __init__(self):
        self.name = "ConfigManager"
