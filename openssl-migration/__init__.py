"""
OpenSSL Migration Framework

This package provides tools for migrating OpenSSL utility repositories
from shell/Perl scripts to modern Python implementations using:
- subprocess: For running external commands
- pathlib: For file system operations
- click: For command-line interfaces

Migrated repositories:
- openssl/installer → Python installation scripts
- openssl/tools → Python build and release tools
- openssl/perftools → Python performance benchmarks
- openssl/release-metadata → Python metadata generators
- openssl/openssl-docs + openssl/openssl-book → Python documentation pipelines
- openssl/general-policies + openssl/technical-policies → Python compliance tools
"""

__version__ = "1.0.0"
__author__ = "OpenSSL Tools Team"
__email__ = "openssl-tools@example.com"

from .core.migration_framework import MigrationFramework
from .core.script_converter import ScriptConverter
from .core.python_generator import PythonGenerator

__all__ = [
    "MigrationFramework",
    "ScriptConverter", 
    "PythonGenerator"
]
