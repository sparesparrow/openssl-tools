"""
OpenSSL Tools - Comprehensive OpenSSL Development and CI/CD Toolkit

This package provides a comprehensive set of tools for OpenSSL development,
following the Zen of Python principles for beautiful, explicit, and simple code.

The package is organized into clear domains:
- automation: Workflow management, CI/CD, and AI agents
- development: Build system and package management
- foundation: Core utilities and command-line interfaces
- security: Security analysis and compliance tools
- testing: Testing frameworks and quality assurance
- monitoring: System monitoring and observability

Modules:
    automation.workflow_management: GitHub Actions workflow management and monitoring
    automation.continuous_integration: CI/CD automation and deployment
    automation.ai_agents: Model Context Protocol server implementations
    development.build_system: Build optimization and performance analysis
    development.package_management: Conan package management and orchestration
    foundation.utilities: Utility functions and helpers
    foundation.command_line: Command-line interfaces
"""

__version__ = "1.0.0"
__author__ = "OpenSSL Tools Team"
__email__ = "openssl-tools@example.com"

# Import main classes for easy access
from .automation.workflow_management import WorkflowManager, UnifiedWorkflowManager
from .development.build_system import BuildCacheManager, BuildOptimizer
from .development.package_management import ConanRemoteManager, ConanOrchestrator
from .automation.continuous_integration import ConanAutomation, DeploymentManager

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