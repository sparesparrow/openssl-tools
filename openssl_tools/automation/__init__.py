"""
Automation Module

This module provides comprehensive automation capabilities for OpenSSL development,
including workflow management, continuous integration, and AI-powered agents.

Submodules:
    workflow_management: GitHub Actions workflow management and monitoring
    continuous_integration: CI/CD automation and deployment
    ai_agents: Model Context Protocol server implementations
"""

from .workflow_management import WorkflowManager, UnifiedWorkflowManager
from .continuous_integration import ConanAutomation, DeploymentManager
from .ai_agents import GitHubWorkflowFixer

__all__ = [
    "WorkflowManager",
    "UnifiedWorkflowManager",
    "ConanAutomation", 
    "DeploymentManager",
    "GitHubWorkflowFixer",
]
