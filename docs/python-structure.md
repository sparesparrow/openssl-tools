# Python Script Directory Structure - Legacy

⚠️ **This document describes the previous structure. For the current improved structure, see [python-structure-improved.md](python-structure-improved.md)**

This document describes the previous Python script organization in the OpenSSL Tools project, following best practices for maintainability, scalability, and collaboration.

## Overview

The Python scripts have been reorganized into a proper package structure under `openssl_tools/` with clear separation of concerns and modular design.

## Directory Structure

```
openssl_tools/
├── __init__.py                 # Main package initialization
├── workflows/                  # Workflow management and monitoring
│   ├── __init__.py
│   ├── manager.py              # Main workflow manager
│   ├── monitor.py              # Workflow monitoring
│   ├── recovery.py             # Workflow recovery
│   ├── health_check.py         # Health checking
│   └── unified.py              # Unified workflow manager (MCP integration)
├── build/                      # Build optimization and management
│   ├── __init__.py
│   ├── optimizer.py            # Build optimization
│   ├── matrix_generator.py     # Build matrix generation
│   └── performance.py          # Performance analysis
├── conan/                      # Conan package management
│   ├── __init__.py
│   ├── remote_manager.py       # Remote management
│   ├── orchestrator.py         # Conan orchestration
│   └── dependency_manager.py   # Dependency management
├── ci/                         # CI/CD automation
│   ├── __init__.py
│   ├── automation.py           # CI automation
│   ├── deployment.py           # Deployment scripts
│   └── testing.py              # Test harnesses
├── mcp/                        # MCP server implementations
│   ├── __init__.py
│   ├── workflow_fixer.py       # GitHub workflow fixer
│   ├── build_server.py         # Build MCP server
│   ├── ci_server.py            # CI MCP server
│   └── security_server.py      # Security MCP server
├── utils/                      # Utility functions and helpers
│   ├── __init__.py
│   ├── validation.py           # Validation utilities
│   ├── logging.py              # Logging utilities
│   └── config.py               # Configuration management
├── cli/                        # Command-line interfaces
│   ├── __init__.py
│   └── main.py                 # Main CLI entry point
└── tests/                      # Test suite
    ├── __init__.py
    ├── test_workflows.py
    ├── test_build.py
    ├── test_conan.py
    └── test_utils.py
```

## Package Descriptions

### workflows/
Contains all GitHub Actions workflow management functionality:
- **manager.py**: Main workflow management interface
- **monitor.py**: Workflow monitoring and status tracking
- **recovery.py**: Automated workflow recovery and retry logic
- **health_check.py**: Workflow health analysis and recommendations
- **unified.py**: Unified interface combining legacy tools with MCP capabilities

### build/
Contains build optimization and performance analysis tools:
- **optimizer.py**: Build optimization strategies and cache management
- **matrix_generator.py**: Build matrix generation for CI/CD
- **performance.py**: Build performance analysis and benchmarking

### conan/
Contains Conan package management functionality:
- **remote_manager.py**: Conan remote configuration and management
- **orchestrator.py**: Conan build orchestration and coordination
- **dependency_manager.py**: Dependency management and resolution

### ci/
Contains CI/CD automation tools:
- **automation.py**: Conan-specific CI/CD automation
- **deployment.py**: Deployment automation and management
- **testing.py**: Testing framework and test execution

### mcp/
Contains Model Context Protocol server implementations:
- **workflow_fixer.py**: GitHub workflow analysis and fixing MCP server
- **build_server.py**: Build automation MCP server
- **ci_server.py**: CI/CD automation MCP server
- **security_server.py**: Security analysis MCP server

### utils/
Contains utility functions and helpers:
- **validation.py**: Configuration and setup validation utilities
- **logging.py**: Standardized logging configuration
- **config.py**: Configuration management utilities

### cli/
Contains command-line interfaces:
- **main.py**: Main CLI entry point with subcommands

## Usage Examples

### Command Line Interface

```bash
# Main CLI with subcommands
openssl-tools workflow analyze --repo sparesparrow/openssl-tools
openssl-tools build optimize --cache-dir ~/.openssl-cache
openssl-tools conan setup-remote --token $GITHUB_TOKEN
openssl-tools validate mcp-config

# Individual tool CLIs
openssl-workflow monitor --repo sparesparrow/openssl-tools
openssl-build optimize --max-size 20
openssl-conan setup-remote --username sparesparrow
openssl-validate mcp-config --quiet
```

### Python API

```python
# Import main classes
from openssl_tools import WorkflowManager, BuildCacheManager, ConanRemoteManager

# Workflow management
manager = WorkflowManager("sparesparrow", "openssl-tools")
status = manager.check_status()

# Build optimization
optimizer = BuildCacheManager()
result = optimizer.optimize_cache()

# Conan management
conan_manager = ConanRemoteManager()
success = conan_manager.setup_github_packages_remote()
```

### Module-specific imports

```python
# Workflow management
from openssl_tools.workflows import WorkflowMonitor, WorkflowRecovery
from openssl_tools.workflows.unified import UnifiedWorkflowManager

# Build tools
from openssl_tools.build import BuildOptimizer, PerformanceAnalyzer

# Conan tools
from openssl_tools.conan import ConanOrchestrator, DependencyManager

# MCP servers
from openssl_tools.mcp import GitHubWorkflowFixer, BuildServer

# Utilities
from openssl_tools.utils import validate_mcp_config, setup_logging
```

## Benefits of New Structure

### 1. **Clear Separation of Concerns**
- Each module has a specific purpose and responsibility
- Related functionality is grouped together
- Easy to locate and understand code

### 2. **Improved Maintainability**
- Proper package structure with `__init__.py` files
- Standardized imports and exports
- Clear module boundaries

### 3. **Better Scalability**
- Easy to add new modules and functionality
- Modular design allows independent development
- Clear extension points

### 4. **Enhanced Collaboration**
- Consistent naming conventions
- Clear documentation and structure
- Easy onboarding for new developers

### 5. **Professional Package Structure**
- Follows Python packaging best practices
- Proper entry points and CLI commands
- Standardized configuration and testing

## Migration Guide

### For Existing Scripts

1. **Update imports**: Change from dynamic imports to proper package imports
2. **Update entry points**: Use new CLI commands instead of direct script execution
3. **Update configuration**: Use new configuration management utilities

### For New Development

1. **Use package imports**: Import from `openssl_tools` package
2. **Follow naming conventions**: Use snake_case for modules and functions
3. **Add proper documentation**: Include docstrings and type hints
4. **Write tests**: Add tests to the `tests/` directory

## Configuration

The new structure includes standardized configuration management:

```python
from openssl_tools.utils import ConfigManager

config = ConfigManager()
github_token = config.get_github_token()
conan_home = config.get_conan_home()
```

## Testing

Run tests using pytest:

```bash
# Run all tests
pytest

# Run specific test modules
pytest tests/test_workflows.py
pytest tests/test_build.py

# Run with coverage
pytest --cov=openssl_tools
```

## Development

### Adding New Modules

1. Create module in appropriate package directory
2. Add to package `__init__.py` with proper exports
3. Add CLI commands if needed
4. Write tests
5. Update documentation

### Code Style

The project uses:
- **Black** for code formatting
- **isort** for import sorting
- **mypy** for type checking
- **flake8** for linting

Run formatting:

```bash
black openssl_tools/
isort openssl_tools/
mypy openssl_tools/
flake8 openssl_tools/
```

## Future Enhancements

1. **Plugin System**: Add plugin architecture for extensibility
2. **Configuration UI**: Web-based configuration interface
3. **Monitoring Dashboard**: Real-time monitoring and analytics
4. **API Server**: REST API for remote access
5. **Docker Integration**: Containerized deployment options
