"""
OpenSSL Tools - Comprehensive OpenSSL Development and CI/CD Toolkit

This package provides a comprehensive set of tools for OpenSSL development,
including workflow management, build optimization, Conan package management,
CI/CD automation, and MCP server implementations.

Modules:
    workflows: GitHub Actions workflow management and monitoring
    build: Build optimization and performance analysis
    conan: Conan package management and orchestration
    ci: CI/CD automation and deployment
    mcp: Model Context Protocol server implementations
    utils: Utility functions and helpers
    cli: Command-line interfaces
"""

__version__ = "1.0.0"
__author__ = "OpenSSL Tools Team"
__email__ = "openssl-tools@example.com"

# Import main classes for easy access
from .workflows import WorkflowManager, UnifiedWorkflowManager
from .build import BuildCacheManager, BuildOptimizer
from .conan import ConanRemoteManager, ConanOrchestrator
from .ci import ConanAutomation, DeploymentManager

__all__ = [
    "WorkflowManager",
    "UnifiedWorkflowManager", 
    "BuildCacheManager",
    "BuildOptimizer",
    "ConanRemoteManager",
    "ConanOrchestrator",
    "ConanAutomation",
    "DeploymentManager",
]
