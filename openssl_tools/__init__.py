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
    "statistics"
]

__version__ = "1.2.0"

# Import key modules for easy access
from . import foundation
from . import security
from . import automation
from . import testing
from . import statistics
