#!/usr/bin/env python3
"""
OpenSSL Tools - Main CLI Entry Point

This is the main command-line interface for OpenSSL development tools.
It provides access to all major functionality through a unified CLI.
"""

import argparse
import sys
from pathlib import Path

# Add the parent directory to the path to import openssl_tools
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from openssl_tools.workflows import WorkflowManager, UnifiedWorkflowManager
from openssl_tools.build import BuildCacheManager, BuildOptimizer
from openssl_tools.conan import ConanRemoteManager, ConanOrchestrator
# from openssl_tools.utils import validate_mcp_config


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="OpenSSL Tools - Comprehensive OpenSSL Development Toolkit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s workflow analyze --repo sparesparrow/openssl-tools
  %(prog)s build optimize --cache-dir ~/.openssl-cache
  %(prog)s conan setup-remote --token $GITHUB_TOKEN
  %(prog)s validate mcp-config
        """
    )
    
    parser.add_argument(
        "--version", 
        action="version", 
        version="OpenSSL Tools 1.0.0"
    )
    
    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands",
        required=True
    )
    
    # Workflow management commands
    workflow_parser = subparsers.add_parser(
        "workflow",
        help="Workflow management commands"
    )
    workflow_subparsers = workflow_parser.add_subparsers(
        dest="workflow_action",
        help="Workflow actions",
        required=True
    )
    
    # Workflow analyze
    analyze_parser = workflow_subparsers.add_parser(
        "analyze",
        help="Analyze workflow failures"
    )
    analyze_parser.add_argument("--repo", required=True, help="Repository in format 'owner/repo'")
    analyze_parser.add_argument("--limit", type=int, default=20, help="Maximum workflow runs to analyze")
    analyze_parser.add_argument("--unified", action="store_true", help="Use unified MCP-powered analysis")
    
    # Workflow monitor
    monitor_parser = workflow_subparsers.add_parser(
        "monitor",
        help="Monitor workflow status"
    )
    monitor_parser.add_argument("--repo", required=True, help="Repository in format 'owner/repo'")
    monitor_parser.add_argument("--hours", type=int, default=24, help="Hours to look back")
    
    # Build optimization commands
    build_parser = subparsers.add_parser(
        "build",
        help="Build optimization commands"
    )
    build_subparsers = build_parser.add_subparsers(
        dest="build_action",
        help="Build actions",
        required=True
    )
    
    # Build optimize
    optimize_parser = build_subparsers.add_parser(
        "optimize",
        help="Optimize build configuration"
    )
    optimize_parser.add_argument("--cache-dir", help="Build cache directory")
    optimize_parser.add_argument("--max-size", type=int, default=10, help="Maximum cache size in GB")
    
    # Conan management commands
    conan_parser = subparsers.add_parser(
        "conan",
        help="Conan package management commands"
    )
    conan_subparsers = conan_parser.add_subparsers(
        dest="conan_action",
        help="Conan actions",
        required=True
    )
    
    # Conan setup-remote
    setup_remote_parser = conan_subparsers.add_parser(
        "setup-remote",
        help="Setup Conan remote for GitHub Packages"
    )
    setup_remote_parser.add_argument("--token", help="GitHub token")
    setup_remote_parser.add_argument("--username", help="GitHub username")
    
    # Validation commands
    validate_parser = subparsers.add_parser(
        "validate",
        help="Validation commands"
    )
    validate_subparsers = validate_parser.add_subparsers(
        dest="validate_action",
        help="Validation actions",
        required=True
    )
    
    # Validate MCP config
    mcp_config_parser = validate_subparsers.add_parser(
        "mcp-config",
        help="Validate MCP configuration"
    )
    mcp_config_parser.add_argument("--quiet", action="store_true", help="Quiet mode")
    
    args = parser.parse_args()
    
    try:
        if args.command == "workflow":
            handle_workflow_command(args)
        elif args.command == "build":
            handle_build_command(args)
        elif args.command == "conan":
            handle_conan_command(args)
        elif args.command == "validate":
            handle_validate_command(args)
        else:
            parser.print_help()
            sys.exit(1)
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def handle_workflow_command(args):
    """Handle workflow management commands."""
    if args.workflow_action == "analyze":
        if args.unified:
            import asyncio
            manager = UnifiedWorkflowManager(args.repo)
            result = asyncio.run(manager.analyze_workflows(args.limit))
            print(result)
        else:
            repo_owner, repo_name = args.repo.split('/', 1)
            manager = WorkflowManager(repo_owner, repo_name)
            result = manager.check_status()
            print(result)
    elif args.workflow_action == "monitor":
        repo_owner, repo_name = args.repo.split('/', 1)
        manager = WorkflowManager(repo_owner, repo_name)
        result = manager.check_status(args.hours)
        print(result)


def handle_build_command(args):
    """Handle build optimization commands."""
    if args.build_action == "optimize":
        cache_dir = Path(args.cache_dir) if args.cache_dir else None
        optimizer = BuildCacheManager(cache_dir, max_cache_size_gb=args.max_size)
        result = optimizer.optimize_cache()
        print(f"Build optimization completed: {result}")


def handle_conan_command(args):
    """Handle Conan management commands."""
    if args.conan_action == "setup-remote":
        manager = ConanRemoteManager(args.token, args.username)
        success = manager.setup_github_packages_remote()
        if success:
            print("✅ GitHub Packages remote setup successfully")
        else:
            print("❌ Failed to setup GitHub Packages remote")
            sys.exit(1)


def handle_validate_command(args):
    """Handle validation commands."""
    if args.validate_action == "mcp-config":
        # Import the validation script directly
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        from openssl_tools.utils.validation import MCPConfigValidator
        validator = MCPConfigValidator()
        success = validator.validate_all()
        if not args.quiet:
            validator.print_summary()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
