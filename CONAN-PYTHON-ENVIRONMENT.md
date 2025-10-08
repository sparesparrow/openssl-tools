# Conan-Managed Python Environment

This document describes how the OpenSSL Tools project uses Conan cache/remote to provide Python environment management with proper environmental variables for correct Python path resolution.

## Overview

The Python environment is now managed through Conan cache/remote instead of traditional virtual environments. This approach provides:

- **Centralized Management**: Python environment managed by Conan package system
- **Cache Efficiency**: Shared Python environment across projects
- **Remote Distribution**: Python environment can be distributed via Conan remotes
- **Environment Variables**: Proper setup of Python paths and environment variables
- **Fallback Support**: Graceful fallback to system Python when needed

## Architecture

### 1. Conan Package Structure

The `conanfile.py` creates a Python environment structure:

```
package_folder/
├── openssl_tools/           # Main Python package
├── python/                  # Conan-managed Python environment
│   ├── bin/
│   │   ├── python          # Python wrapper script
│   │   └── activate        # Environment activation script
│   └── lib/                # Python libraries
├── conan_cache/
│   └── python/             # Python cache directory
├── python_env_info.json    # Environment information
└── tools_config.json       # Tools configuration
```

### 2. Environment Variables

The system sets up these key environment variables:

- `CONAN_PYTHON_ENV=managed` - Indicates Conan-managed Python environment
- `CONAN_PYTHON_SOURCE=cache_remote` - Source of Python environment
- `CONAN_PYTHON_CACHE=<path>` - Path to Python cache directory
- `OPENSSL_TOOLS_ROOT=<path>` - Root directory of OpenSSL Tools
- `PYTHONPATH` - Updated with Conan-managed Python paths
- `PATH` - Updated with Conan Python binary paths

### 3. Python Path Resolution

The system follows this priority order for Python interpreter selection:

1. **Conan Package Python Wrapper** - Custom wrapper with environment setup
2. **Conan Cache Python** - Python from Conan cache directory
3. **Virtual Environment Python** - Traditional venv (fallback)
4. **System Python** - System-wide Python installation

## Implementation Details

### 1. Conan Package (`conanfile.py`)

The `conanfile.py` includes:

- **`_create_conan_python_environment()`**: Creates Python environment structure
- **`package_info()`**: Sets up environment variables for consumers
- **Python wrapper script**: Ensures correct environment setup
- **Activation script**: Bash script for environment activation

### 2. Environment Management (`util/conan_python_env.py`)

The `ConanPythonEnvironment` class provides:

- **Environment setup**: Configures all necessary environment variables
- **Python interpreter detection**: Finds the best available Python
- **Path management**: Manages PYTHONPATH and PATH variables
- **Validation**: Validates environment setup
- **Information gathering**: Provides debugging information

### 3. Launcher Integration (`launcher/conan_launcher.py`)

The launcher system:

- **Uses Conan-managed Python**: Prioritizes Conan environment
- **Sets up environment**: Configures all necessary variables
- **Provides fallbacks**: Graceful degradation to system Python
- **Logs environment info**: Provides visibility into Python selection

### 4. Configuration Files

Updated configuration files:

- **`conan-dev/activate`**: Enhanced activation script
- **`conan-dev/conan.conf`**: Python environment settings
- **`conan-dev/global.conf`**: Global Python environment settings

## Usage

### 1. Environment Activation

```bash
# Activate Conan-managed Python environment
source conan-dev/activate

# Or use the Python utility directly
python util/conan_python_env.py --validate
```

### 2. Python Script Execution

```bash
# Using the launcher (recommended)
python launcher/conan_launcher.py -p script.py

# Using the utility directly
python util/conan_python_env.py --info
```

### 3. Environment Validation

```bash
# Validate environment setup
python util/conan_python_env.py --validate

# Show environment information
python util/conan_python_env.py --info

# Save environment info to file
python util/conan_python_env.py --save-info
```

## Environment Variables Reference

### Core Variables

| Variable | Description | Example Value |
|----------|-------------|---------------|
| `CONAN_PYTHON_ENV` | Indicates Conan-managed environment | `managed` |
| `CONAN_PYTHON_SOURCE` | Source of Python environment | `cache_remote` |
| `CONAN_PYTHON_CACHE` | Path to Python cache | `/path/to/conan-dev/cache/python` |
| `OPENSSL_TOOLS_ROOT` | Root directory | `/path/to/openssl-tools` |

### Path Variables

| Variable | Description | Example Value |
|----------|-------------|---------------|
| `PYTHONPATH` | Python module search paths | `/path/to/openssl_tools:/path/to/cache` |
| `PATH` | Binary search paths | `/path/to/python/bin:/usr/bin` |

### Conan Variables

| Variable | Description | Example Value |
|----------|-------------|---------------|
| `CONAN_USER_HOME` | Conan user home directory | `/path/to/conan-dev` |
| `CONAN_PYTHON_EXECUTABLE` | Python executable path | `/path/to/python/bin/python` |
| `CONAN_PYTHON_HOME` | Python home directory | `/path/to/python` |

## Troubleshooting

### 1. Python Not Found

**Problem**: Python interpreter not found

**Solution**:
```bash
# Check available Python interpreters
python util/conan_python_env.py --info

# Validate environment
python util/conan_python_env.py --validate
```

### 2. Module Import Errors

**Problem**: Cannot import OpenSSL Tools modules

**Solution**:
```bash
# Check PYTHONPATH
echo $PYTHONPATH

# Re-activate environment
source conan-dev/activate

# Check environment info
python util/conan_python_env.py --info
```

### 3. Environment Variables Not Set

**Problem**: Required environment variables missing

**Solution**:
```bash
# Re-run environment setup
python util/conan_python_env.py

# Check configuration files
cat conan-dev/conan.conf
cat conan-dev/global.conf
```

### 4. Cache Issues

**Problem**: Python cache not working properly

**Solution**:
```bash
# Clear Conan cache
conan cache clean

# Rebuild package
conan create . --profile=default

# Check cache directory
ls -la conan-dev/cache/python/
```

## Development Workflow

### 1. Initial Setup

```bash
# Clone repository
git clone <repository-url>
cd openssl-tools

# Setup Conan environment
source conan-dev/activate

# Validate setup
python util/conan_python_env.py --validate
```

### 2. Development

```bash
# Activate environment
source conan-dev/activate

# Run scripts
python launcher/conan_launcher.py -p script.py

# Check environment
python util/conan_python_env.py --info
```

### 3. Testing

```bash
# Run tests with Conan-managed Python
python launcher/conan_launcher.py -p tests/test_script.py

# Validate environment before testing
python util/conan_python_env.py --validate
```

## Benefits

### 1. Centralized Management

- Single source of truth for Python environment
- Consistent environment across different machines
- Easy environment replication

### 2. Cache Efficiency

- Shared Python environment reduces disk usage
- Faster environment setup
- Better resource utilization

### 3. Remote Distribution

- Python environment can be distributed via Conan remotes
- Consistent environment across team members
- Easy deployment to different environments

### 4. Environment Isolation

- Proper environment variable management
- Isolated Python paths
- No conflicts with system Python

### 5. Fallback Support

- Graceful degradation to system Python
- Multiple fallback options
- Robust error handling

## Migration Guide

### From Virtual Environment

If you're migrating from a traditional virtual environment:

1. **Backup current environment**:
   ```bash
   pip freeze > requirements_backup.txt
   ```

2. **Activate Conan environment**:
   ```bash
   source conan-dev/activate
   ```

3. **Validate setup**:
   ```bash
   python util/conan_python_env.py --validate
   ```

4. **Test functionality**:
   ```bash
   python launcher/conan_launcher.py -p your_script.py
   ```

### From System Python

If you're migrating from system Python:

1. **Check current Python**:
   ```bash
   which python
   python --version
   ```

2. **Setup Conan environment**:
   ```bash
   source conan-dev/activate
   ```

3. **Verify environment**:
   ```bash
   python util/conan_python_env.py --info
   ```

## Best Practices

### 1. Environment Activation

Always activate the Conan environment before development:

```bash
source conan-dev/activate
```

### 2. Environment Validation

Regularly validate your environment:

```bash
python util/conan_python_env.py --validate
```

### 3. Environment Information

Keep environment information for debugging:

```bash
python util/conan_python_env.py --save-info
```

### 4. Script Execution

Use the launcher for script execution:

```bash
python launcher/conan_launcher.py -p script.py
```

### 5. Configuration Management

Keep configuration files updated:

- `conan-dev/conan.conf`
- `conan-dev/global.conf`
- `conan-dev/activate`

## Conclusion

The Conan-managed Python environment provides a robust, efficient, and maintainable solution for Python environment management in the OpenSSL Tools project. It ensures correct Python path resolution through proper environmental variable management while providing fallback support and comprehensive tooling for environment validation and debugging.
