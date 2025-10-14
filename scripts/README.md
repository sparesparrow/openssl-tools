# Scripts Directory

This directory contains standalone scripts and utilities that are not part of the main `openssl_tools` package.

## What Remains in scripts/

### Shell Scripts
- `*.sh` - Shell scripts for build automation and setup
- `*.bat` - Windows batch scripts

### Standalone Utilities
- Scripts that are truly standalone and don't fit into the package structure
- Build and deployment scripts that need to remain in scripts/

### Legacy Scripts
- Scripts that are being phased out but kept for backward compatibility

## What Has Moved to openssl_tools/

### Python Modules (Moved to Package Structure)
- **Security**: `openssl_tools/security/` - Security validation, authentication, key management
- **Testing**: `openssl_tools/testing/` - Test harnesses, quality management, fuzz testing
- **Monitoring**: `openssl_tools/monitoring/` - Status reporting, log management
- **Development**: `openssl_tools/development/` - Build system, package management
- **Automation**: `openssl_tools/automation/` - Workflow management, CI/CD, AI agents
- **Foundation**: `openssl_tools/foundation/` - Core utilities, command-line interfaces

### Examples and Demos
- Moved to `examples/` directory for better organization

## How to Use the New Package Structure

### Import from Package
```python
# Instead of importing from scripts/
from openssl_tools.security import BuildValidator
from openssl_tools.testing import TestHarness
from openssl_tools.monitoring import StatusReporter
```

### Use CLI Commands
```bash
# New CLI commands
openssl-tools security validate
openssl-tools test run
openssl-tools monitor status
openssl-sbom --help
```

### Backward Compatibility
Root-level Python files now serve as thin wrappers:
```python
# These still work for backward compatibility
python conan_remote_manager.py --help
python build_optimizer.py --help
```

## Migration Guide

1. **Update Imports**: Change imports from `scripts/` to `openssl_tools.`
2. **Use CLI**: Prefer CLI commands over direct script execution
3. **Check Examples**: Look in `examples/` for usage examples
4. **Read Documentation**: See `docs/python-structure-improved.md` for detailed structure

## Contributing

When adding new scripts:
1. **Library Code**: Add to appropriate `openssl_tools/` package
2. **Standalone Scripts**: Add to `scripts/` if truly standalone
3. **Examples**: Add to `examples/` for demonstration purposes
4. **CLI Commands**: Add entry points to `pyproject.toml`
