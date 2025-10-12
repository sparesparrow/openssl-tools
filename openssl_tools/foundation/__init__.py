"""
Foundation Module

This module provides foundational utilities and interfaces for OpenSSL development tools,
including core utilities and command-line interfaces.

Submodules:
    utilities: Core utility functions and helpers
    command_line: Command-line interfaces and CLI tools
"""

from .utilities import setup_logging, ConfigManager
from .command_line import MainCLI

__all__ = [
    "setup_logging",
    "ConfigManager",
    "MainCLI",
]
