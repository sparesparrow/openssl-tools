#!/usr/bin/env python3
"""
Environment setup script for MCP GitHub Workflow Fixer Server
"""

import os
import sys
from pathlib import Path

def setup_environment():
    """Set up the environment for the MCP server"""

    print("🔧 MCP GitHub Workflow Fixer Server - Environment Setup")
    print("=" * 60)

    # Check Python version
    python_version = sys.version_info
    if python_version < (3, 8):
        print(f"❌ Python {python_version.major}.{python_version.minor} is not supported. Please use Python 3.8+")
        return False

    print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro} detected")

    # Check if virtual environment is active
    venv_path = os.environ.get('VIRTUAL_ENV')
    if venv_path:
        print(f"✅ Virtual environment active: {venv_path}")
    else:
        print("⚠️  No virtual environment detected. Consider using one for isolation.")

    # Check required environment variables
    github_token = os.environ.get('GITHUB_TOKEN')
    if github_token:
        print("✅ GITHUB_TOKEN environment variable is set")
        # Don't print the actual token for security
    else:
        print("❌ GITHUB_TOKEN environment variable not set")
        print()
        print("To set up your GitHub token:")
        print("1. Go to https://github.com/settings/tokens")
        print("2. Generate a new Personal Access Token with 'repo' and 'workflow' permissions")
        print("3. Set the environment variable:")
        print("   export GITHUB_TOKEN='your_token_here'")
        print("   # or add it to your ~/.bashrc or ~/.zshrc")
        print()

    # Check required packages
    required_packages = [
        ('mcp', 'mcp'),
        ('fastmcp', 'fastmcp'),
        ('httpx', 'httpx'),
        ('pydantic', 'pydantic'),
        ('pyyaml', 'yaml'),
        ('jinja2', 'jinja2'),
        ('tenacity', 'tenacity')
    ]

    missing_packages = []
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
            print(f"✅ {package_name} is installed")
        except ImportError:
            missing_packages.append(package_name)
            print(f"❌ {package_name} is missing")

    if missing_packages:
        print()
        print("To install missing packages, run:")
        print(f"pip install {' '.join(missing_packages)}")
        print("Or install all requirements:")
        print("pip install -r scripts/mcp/requirements.txt")
        return False

    # Check if server file exists
    server_file = Path(__file__).parent / "github_workflow_fixer.py"
    if server_file.exists():
        print(f"✅ MCP server file found: {server_file}")
    else:
        print(f"❌ MCP server file not found: {server_file}")
        return False

    # Test basic import
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from github_workflow_fixer import GitHubWorkflowFixer
        print("✅ MCP server imports successfully")
    except ImportError as e:
        print(f"❌ Failed to import MCP server: {e}")
        return False

    print()
    print("🎉 Environment setup complete!")
    print()
    print("To test the server (requires GITHUB_TOKEN):")
    print("python scripts/mcp/test_server.py")
    print()
    print("To run the MCP server:")
    print("python scripts/mcp/github_workflow_fixer.py")
    print()
    print("For Cursor integration, the .cursor/mcp.json is already configured.")

    return True

if __name__ == "__main__":
    success = setup_environment()
    sys.exit(0 if success else 1)
