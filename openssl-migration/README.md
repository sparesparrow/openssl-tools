# OpenSSL Migration Framework

A comprehensive framework for migrating OpenSSL utility repositories from shell/Perl scripts to modern Python implementations using `subprocess`, `pathlib`, and `click` libraries.

## 🎯 Overview

The OpenSSL Migration Framework follows the **Way of Python** principles:
- **Beautiful**: Clean, readable code
- **Explicit**: Clear intent and purpose  
- **Simple**: Straightforward implementation

This framework provides tools to migrate scripts from:
- `openssl/installer` → Python installation scripts
- `openssl/tools` → Python build and release tools
- `openssl/perftools` → Python performance benchmarks
- `openssl/release-metadata` → Python metadata generators
- `openssl/openssl-docs` + `openssl/openssl-book` → Python documentation pipelines
- `openssl/general-policies` + `openssl/technical-policies` → Python compliance tools

## 🚀 Features

### Core Migration Capabilities
- **Multi-format Support**: Shell, Perl, and Python script migration
- **Intelligent Analysis**: Automatic script type detection and complexity analysis
- **Modern Python**: Uses `subprocess`, `pathlib`, and `click` libraries
- **Structure Preservation**: Maintains original directory structure
- **Comprehensive Testing**: Generates test files for migrated scripts
- **Documentation**: Auto-generates documentation and examples

### Advanced Features
- **Conan Integration**: Package manager integration for OpenSSL
- **Docker Support**: Containerized installation and build options
- **Performance Optimization**: Parallel processing and caching
- **Error Handling**: Comprehensive error handling and logging
- **CLI Interface**: Full command-line interface with click
- **Batch Processing**: Migrate multiple repositories at once

## 📦 Installation

### Prerequisites
- Python 3.8+
- pip or conda package manager

### Install from Source
```bash
git clone https://github.com/sparesparrow/openssl-tools.git
cd openssl-tools/openssl-migration
pip install -e .
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

## 🛠️ Usage

### Command Line Interface

#### Analyze a Repository
```bash
# Analyze scripts in a repository
openssl-migrate analyze /path/to/openssl/installer

# Save analysis report
openssl-migrate analyze /path/to/openssl/tools --output analysis.json --format json
```

#### Migrate Scripts
```bash
# Migrate all scripts in a repository
openssl-migrate migrate /path/to/openssl/installer --target migrated-installer

# Migrate specific script types
openssl-migrate migrate /path/to/openssl/tools --script-types shell perl

# Dry run to see what would be migrated
openssl-migrate migrate /path/to/openssl/perftools --dry-run
```

#### Convert Single Script
```bash
# Convert a shell script to Python
openssl-migrate convert install.sh --script-type shell --output install.py

# Convert a Perl script to Python
openssl-migrate convert configure.pl --script-type perl --output configure.py
```

#### Generate New Scripts
```bash
# Generate a new installer script
openssl-migrate generate installer --name openssl_installer --output install.py

# Generate a build tool script
openssl-migrate generate build_tool --name openssl_builder --output build.py
```

#### Specialized Installer Migration
```bash
# Migrate OpenSSL installer with modern features
openssl-migrate migrate-installer /path/to/openssl/installer \
    --target migrated-installer \
    --add-modern-features \
    --use-conan-integration \
    --add-docker-support \
    --create-package
```

#### Batch Migration
```bash
# Migrate multiple repositories
openssl-migrate migrate-all \
    --repos /path/to/openssl/installer /path/to/openssl/tools \
    --target-base migrated-repos \
    --parallel 4
```

### Python API

#### Basic Migration
```python
from openssl_migration.core.migration_framework import MigrationFramework, MigrationConfig

# Create configuration
config = MigrationConfig(
    source_repo="/path/to/openssl/installer",
    target_dir="/path/to/migrated",
    script_types=['shell', 'perl'],
    use_click=True,
    use_pathlib=True,
    use_subprocess=True
)

# Initialize framework
framework = MigrationFramework(config)

# Analyze repository
scripts = framework.analyze_repository("/path/to/openssl/installer")

# Migrate scripts
results = framework.migrate_all()
```

#### Installer Migration
```python
from openssl_migration.installer.migrator import OpenSSLInstallerMigrator, InstallerConfig

# Create installer configuration
config = InstallerConfig(
    source_repo="/path/to/openssl/installer",
    target_dir="/path/to/migrated-installer",
    add_modern_features=True,
    use_conan_integration=True,
    add_docker_support=True
)

# Initialize migrator
migrator = OpenSSLInstallerMigrator(config)

# Migrate installer scripts
results = migrator.migrate_installer_scripts()

# Generate modern installer
migrator.generate_modern_installer(Path("openssl_installer.py"))
```

## 📁 Project Structure

```
openssl-migration/
├── __init__.py                 # Package initialization
├── cli.py                      # Command-line interface
├── README.md                   # This file
├── requirements.txt            # Python dependencies
├── core/                       # Core migration framework
│   ├── migration_framework.py  # Main migration framework
│   ├── script_converter.py     # Script conversion logic
│   └── python_generator.py     # Python code generation
├── installer/                  # Installer-specific migration
│   └── migrator.py            # Installer migrator
├── tools/                      # Tools migration (future)
├── perftools/                  # Performance tools migration (future)
├── release-metadata/           # Metadata migration (future)
├── docs/                       # Documentation migration (future)
├── compliance/                 # Compliance migration (future)
└── examples/                   # Usage examples
    └── migrate_openssl_repos.py # Example migration script
```

## 🔧 Configuration

### Migration Configuration
```python
@dataclass
class MigrationConfig:
    source_repo: str                    # Source repository path
    target_dir: Path                    # Target directory
    script_types: List[str]             # Script types to migrate
    preserve_structure: bool = True     # Preserve directory structure
    add_tests: bool = True              # Add test files
    add_documentation: bool = True      # Add documentation
    use_click: bool = True              # Use click for CLI
    use_pathlib: bool = True            # Use pathlib for files
    use_subprocess: bool = True         # Use subprocess for commands
    output_format: str = "modern"       # Output format style
```

### Installer Configuration
```python
@dataclass
class InstallerConfig:
    source_repo: str                           # Source repository
    target_dir: Path                           # Target directory
    preserve_perl_compatibility: bool = False  # Preserve Perl compatibility
    add_modern_features: bool = True           # Add modern features
    use_conan_integration: bool = True         # Use Conan integration
    add_docker_support: bool = True            # Add Docker support
```

## 🧪 Testing

### Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=openssl_migration

# Run specific test file
pytest tests/test_migration_framework.py
```

### Test Migration
```bash
# Test migration on sample scripts
openssl-migrate migrate tests/sample-scripts --target test-migrated --dry-run
```

## 📊 Migration Examples

### Shell Script Migration

**Original Shell Script:**
```bash
#!/bin/bash
# Install OpenSSL
PREFIX="/usr/local"
echo "Installing OpenSSL to $PREFIX"
cd openssl-source
./Configure --prefix=$PREFIX
make
make install
echo "Installation complete"
```

**Migrated Python Script:**
```python
#!/usr/bin/env python3
"""
OpenSSL Installer

Migrated from shell script.
"""

import os
import sys
import subprocess
from pathlib import Path
import click
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_command(command, check=True):
    """Run a command using subprocess."""
    logger.debug(f"Running command: {command}")
    return subprocess.run(command, check=check, shell=True)

@click.command()
@click.option('--prefix', default='/usr/local', help='Installation prefix')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def main(prefix, verbose):
    """Install OpenSSL to the specified prefix."""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info(f"Installing OpenSSL to {prefix}")
    
    try:
        # Change to source directory
        os.chdir('openssl-source')
        
        # Configure OpenSSL
        run_command(f'./Configure --prefix={prefix}')
        
        # Build OpenSSL
        run_command('make')
        
        # Install OpenSSL
        run_command('make install')
        
        logger.info("Installation complete")
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Installation failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
```

### Perl Script Migration

**Original Perl Script:**
```perl
#!/usr/bin/perl
use strict;
use warnings;

my $prefix = "/usr/local";
print "Installing OpenSSL to $prefix\n";

chdir "openssl-source" or die "Cannot change directory: $!";
system("./Configure --prefix=$prefix") == 0 or die "Configure failed";
system("make") == 0 or die "Make failed";
system("make install") == 0 or die "Install failed";

print "Installation complete\n";
```

**Migrated Python Script:**
```python
#!/usr/bin/env python3
"""
OpenSSL Installer

Migrated from Perl script.
"""

import os
import sys
import subprocess
from pathlib import Path
import click
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_command(command, check=True):
    """Run a command using subprocess."""
    logger.debug(f"Running command: {command}")
    return subprocess.run(command, check=check, shell=True)

@click.command()
@click.option('--prefix', default='/usr/local', help='Installation prefix')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def main(prefix, verbose):
    """Install OpenSSL to the specified prefix."""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info(f"Installing OpenSSL to {prefix}")
    
    try:
        # Change to source directory
        source_dir = Path("openssl-source")
        if not source_dir.exists():
            raise FileNotFoundError(f"Source directory not found: {source_dir}")
        
        os.chdir(source_dir)
        
        # Configure OpenSSL
        run_command(f'./Configure --prefix={prefix}')
        
        # Build OpenSSL
        run_command('make')
        
        # Install OpenSSL
        run_command('make install')
        
        logger.info("Installation complete")
        
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        logger.error(f"Installation failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
```

## 🎨 Code Generation Templates

The framework includes templates for generating modern Python scripts:

### Installer Template
- System information gathering
- Dependency checking
- File download and extraction
- Installation with error handling
- Verification and testing

### Build Tool Template
- Parallel build support
- Configuration management
- Test execution
- Clean build options
- Progress reporting

### Performance Tool Template
- Benchmark execution
- Statistical analysis
- Result reporting
- JSON output
- Performance metrics

## 🔍 Analysis and Reporting

### Migration Analysis
The framework provides comprehensive analysis of scripts:
- **Complexity Scoring**: Based on functions, conditionals, loops, and dependencies
- **Dependency Mapping**: Identifies external commands and libraries
- **Function Extraction**: Lists all functions and subroutines
- **Effort Estimation**: Calculates migration effort based on complexity

### Migration Reports
Generated reports include:
- **Summary Statistics**: Total scripts, by type, estimated effort
- **Detailed Script Information**: Size, lines, functions, dependencies
- **Migration Status**: Completed, failed, skipped scripts
- **Recommendations**: Best practices and improvements

## 🚀 Advanced Features

### Conan Integration
- Package manager integration for OpenSSL
- Profile management and configuration
- Dependency resolution and installation
- Build system integration

### Docker Support
- Containerized installation options
- Multi-platform support
- Build environment isolation
- Deployment automation

### Performance Optimization
- Parallel script processing
- Intelligent caching
- Progress reporting
- Resource management

## 🤝 Contributing

### Development Setup
```bash
# Clone repository
git clone https://github.com/sparesparrow/openssl-tools.git
cd openssl-tools/openssl-migration

# Install in development mode
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install
```

### Code Style
- **Formatting**: Black with line length 88
- **Import Sorting**: isort with black profile
- **Linting**: flake8 with max line length 88
- **Type Checking**: mypy with strict mode

### Testing
- **Framework**: pytest with >80% coverage
- **Test Structure**: Unit tests for all components
- **Integration Tests**: End-to-end migration tests
- **Performance Tests**: Large repository migration tests

## 📚 Documentation

### API Documentation
- **Migration Framework**: Core migration functionality
- **Script Converter**: Script conversion logic
- **Python Generator**: Code generation templates
- **CLI Interface**: Command-line usage

### Migration Guides
- **Shell to Python**: Step-by-step conversion guide
- **Perl to Python**: Perl-specific migration patterns
- **Best Practices**: Migration recommendations
- **Troubleshooting**: Common issues and solutions

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- **OpenSSL Project**: For providing the original utility scripts
- **Python Community**: For excellent libraries and tools
- **Conan Team**: For package management integration
- **Docker Team**: For containerization support

## 🔗 Links

- **Repository**: [sparesparrow/openssl-tools](https://github.com/sparesparrow/openssl-tools)
- **Documentation**: [OpenSSL Tools Documentation](https://openssl-tools.readthedocs.io)
- **Issues**: [GitHub Issues](https://github.com/sparesparrow/openssl-tools/issues)
- **Discussions**: [GitHub Discussions](https://github.com/sparesparrow/openssl-tools/discussions)

---

**The Way of Python**: *Beautiful is better than ugly. Explicit is better than implicit. Simple is better than complex.*
