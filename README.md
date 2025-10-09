# OpenSSL Tools

> Build orchestration, CI/CD automation, and package management for OpenSSL

[![CI Status](https://github.com/sparesparrow/openssl-tools/workflows/CI/badge.svg)](https://github.com/sparesparrow/openssl-tools/actions)
[![Conan Package](https://img.shields.io/badge/conan-openssl%2F3.5.0-green.svg)](https://conan.io/center/openssl)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## What is This?

**Companion repository** for [OpenSSL](https://github.com/sparesparrow/openssl) providing:
- GitHub Actions workflows for multi-platform CI/CD  
- Conan package management integration
- Build optimization and caching
- Performance benchmarking tools

**This repository does NOT contain OpenSSL source code.**  
It provides the **build infrastructure** that tests and packages OpenSSL.

## Repository Separation

### OpenSSL Repository
- **Purpose**: OpenSSL source code and core functionality
- **Location**: [sparesparrow/openssl](https://github.com/sparesparrow/openssl)
- **Contains**: Cryptographic algorithms, SSL/TLS implementation, core features
- **CI/CD**: Basic validation + triggers builds in openssl-tools

### OpenSSL Tools Repository (This Repository)
- **Purpose**: Build infrastructure and development tooling
- **Location**: [sparesparrow/openssl-tools](https://github.com/sparesparrow/openssl-tools)
- **Contains**: CI/CD workflows, build scripts, package management, testing tools
- **CI/CD**: Comprehensive builds, testing, and package distribution

See [Repository Separation Explained](docs/explanation/repo-separation.md) for details.

## Quick Start

### Prerequisites
- Python 3.8+ (we support 3.8, 3.9, 3.10, 3.11, 3.12)
- Git
- Basic command-line knowledge

### Setup (5 minutes)

```bash
# Clone the repository
git clone https://github.com/sparesparrow/openssl-tools.git
cd openssl-tools

# Set up Python environment
python setup_python_env.py --versions 3.11

# Configure Conan (optional)
export GITHUB_TOKEN="your_token"
python conan_remote_manager.py --setup

# Verify installation
python -m pytest tests/ -v
```

### First Build

```bash
# Create OpenSSL package
conan create . --profile=conan-profiles/linux-gcc-release.profile

# Or use our orchestration script
python scripts/conan/conan_orchestrator.py --action create --profile linux-gcc-release
```

## Key Features

### 🚀 Performance
- **60% faster builds** with intelligent caching
- **>70% cache hit rate** with optimized strategies
- **90% reduction** in CI checks (202 → ~25)
- **Parallel execution** with CPU core detection

### 🔒 Security
- **Package signing** with cosign for supply chain security
- **Vulnerability scanning** with Trivy integration
- **SBOM generation** in CycloneDX format
- **FIPS support** with separate cache keys

### 🛠️ Developer Experience
- **Multi-version Python** support (3.8-3.12)
- **Cross-platform** builds (Linux, macOS, Windows)
- **Comprehensive testing** with automated validation
- **Clear documentation** with organized structure

### 🔄 CI/CD Integration
- **Cross-repository triggers** from OpenSSL repo
- **Smart change detection** - only relevant builds run
- **Status reporting** back to OpenSSL PRs
- **Artifact sharing** between repositories

## Documentation

### 📖 [Documentation Hub](docs/)
Complete documentation organized by purpose and role.

### 🎓 Learning
- [Getting Started](docs/tutorials/getting-started.md) - Quick setup guide
- [First Build](docs/tutorials/first-build.md) - Trigger OpenSSL build
- [Local Development](docs/tutorials/local-development.md) - Development workflow

### 🛠️ Practical Tasks
- [Setup Artifactory](docs/how-to/setup-artifactory.md) - Configure package repository
- [Manage Secrets](docs/how-to/manage-secrets.md) - GitHub secrets configuration
- [Troubleshooting](docs/how-to/troubleshooting.md) - Common issues and solutions
- [Performance Tuning](docs/how-to/performance-tuning.md) - Optimization guide

### 📚 Reference
- [Workflows](docs/reference/workflows.md) - All GitHub Actions workflows
- [Scripts](docs/reference/scripts.md) - All Python tools and utilities
- [Configuration](docs/reference/configuration.md) - Configuration options

### 💡 Understanding
- [Repository Separation](docs/explanation/repo-separation.md) - Why two repos?
- [Architecture](docs/explanation/architecture.md) - System design and components
- [CI/CD Patterns](docs/explanation/cicd-patterns.md) - Design patterns and best practices
- [Security](docs/explanation/security.md) - Security approach and compliance

### 📦 Conan Package Management
- [Conan Documentation](docs/conan/) - Complete Conan guide

## Project Status

- **Status**: Production Ready ✅
- **Version**: 1.2.0
- **Last Updated**: October 2024
- **Maintainer**: OpenSSL Tools Team

See [STATUS.md](STATUS.md) for detailed capabilities, metrics, and roadmap.

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Development setup and guidelines
- Code style and testing requirements
- PR process and review guidelines
- Community guidelines and support

### Quick Contribution Guide

1. **Fork** the repository
2. **Create** a feature branch
3. **Make** your changes
4. **Test** thoroughly
5. **Submit** a pull request

## Related Repositories

- **OpenSSL Source**: [sparesparrow/openssl](https://github.com/sparesparrow/openssl)
- **This Repository**: Build infrastructure and tooling

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

### Getting Help
- **Documentation**: Browse the [documentation hub](docs/)
- **Issues**: [GitHub Issues](https://github.com/sparesparrow/openssl-tools/issues)
- **Discussions**: [GitHub Discussions](https://github.com/sparesparrow/openssl-tools/discussions)
- **Community**: Open source community support

### Resources
- [Changelog](CHANGELOG.md) - Version history and changes
- [Project Status](STATUS.md) - Current capabilities and metrics
- [Contributing Guide](CONTRIBUTING.md) - How to contribute

---

**OpenSSL Tools** - Making OpenSSL development more efficient and reliable for everyone.

[![GitHub stars](https://img.shields.io/github/stars/sparesparrow/openssl-tools.svg?style=social&label=Star)](https://github.com/sparesparrow/openssl-tools)
[![GitHub forks](https://img.shields.io/github/forks/sparesparrow/openssl-tools.svg?style=social&label=Fork)](https://github.com/sparesparrow/openssl-tools/fork)