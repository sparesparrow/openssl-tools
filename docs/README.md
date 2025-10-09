# OpenSSL Tools Documentation

## What is OpenSSL Tools?

Companion repository providing **build infrastructure** for [OpenSSL](https://github.com/sparesparrow/openssl):
- CI/CD workflows that trigger on openssl repo changes
- Conan package management
- Build optimization and caching
- Performance benchmarking

**Not included**: OpenSSL source code, OpenSSL feature documentation  
**See**: [Repository Separation Explained](explanation/repo-separation.md)

## By Purpose

### 🎓 Learning
- [Getting Started](tutorials/getting-started.md) - Setup openssl-tools
- [First Build](tutorials/first-build.md) - Trigger OpenSSL build
- [Local Development](tutorials/local-development.md) - Development workflow

### 🛠️ Practical Tasks  
- [Setup Artifactory](how-to/setup-artifactory.md) - Configure package repository
- [Manage Secrets](how-to/manage-secrets.md) - GitHub secrets configuration
- [Troubleshooting](how-to/troubleshooting.md) - Common issues and solutions
- [Performance Tuning](how-to/performance-tuning.md) - Optimization guide

### 📚 Reference
- [Workflows](reference/workflows.md) - All GitHub Actions workflows
- [Scripts](reference/scripts.md) - All Python tools and utilities
- [Configuration](reference/configuration.md) - Configuration options

### 💡 Understanding
- [Repository Separation](explanation/repo-separation.md) - Why two repos?
- [Architecture](explanation/architecture.md) - System design and components
- [CI/CD Patterns](explanation/cicd-patterns.md) - Design patterns and best practices
- [Security](explanation/security.md) - Security approach and compliance
- [Design Decisions](explanation/design-decisions.md) - Key architectural decisions

### 📦 Conan Package Management
- [Conan Documentation](conan/) - Complete Conan guide

## By Role

### OpenSSL Contributor (coding in openssl repo)
- **Primary focus**: [OpenSSL repository](https://github.com/sparesparrow/openssl)
- **Understanding CI**: [Repository Separation](explanation/repo-separation.md)
- **Build triggers**: [First Build](tutorials/first-build.md)

### Tools Developer (improving openssl-tools)
- **Getting started**: [Getting Started](tutorials/getting-started.md) → [Local Development](tutorials/local-development.md)
- **Script development**: [Scripts Reference](reference/scripts.md)
- **Architecture**: [Architecture](explanation/architecture.md)

### DevOps Engineer (managing builds)
- **Setup**: [Setup Artifactory](how-to/setup-artifactory.md) → [Manage Secrets](how-to/manage-secrets.md)
- **Conan**: [Conan Documentation](conan/)
- **Patterns**: [CI/CD Patterns](explanation/cicd-patterns.md)

### Project Maintainer
- **Overview**: [Architecture](explanation/architecture.md) → [Design Decisions](explanation/design-decisions.md)
- **Reference**: [Workflows](reference/workflows.md) → [Configuration](reference/configuration.md)
- **Security**: [Security](explanation/security.md)

## Quick Navigation

### I want to...
- **Set up openssl-tools**: [Getting Started](tutorials/getting-started.md)
- **Understand the architecture**: [Repository Separation](explanation/repo-separation.md) → [Architecture](explanation/architecture.md)
- **Configure CI/CD**: [Setup Artifactory](how-to/setup-artifactory.md) → [Workflows](reference/workflows.md)
- **Use Conan**: [Conan Documentation](conan/)
- **Troubleshoot issues**: [Troubleshooting](how-to/troubleshooting.md)
- **Optimize performance**: [Performance Tuning](how-to/performance-tuning.md)
- **Contribute code**: [Contributing Guide](../CONTRIBUTING.md)

### Common Tasks
- **First-time setup**: [Getting Started](tutorials/getting-started.md)
- **Trigger OpenSSL build**: [First Build](tutorials/first-build.md)
- **Configure package repository**: [Setup Artifactory](how-to/setup-artifactory.md)
- **Debug build issues**: [Troubleshooting](how-to/troubleshooting.md)
- **Understand build process**: [Architecture](explanation/architecture.md)

## Documentation Standards

### Writing Guidelines
- **Clear and concise**: Use simple language, avoid jargon
- **Examples**: Provide code examples and practical scenarios
- **Links**: Link to related documentation and external resources
- **Structure**: Use consistent headings and formatting

### Maintenance
- **Keep current**: Update documentation with code changes
- **Test examples**: Verify all code examples work
- **Review regularly**: Quarterly documentation review
- **Feedback welcome**: Report issues or suggest improvements

## Related Resources

### External Documentation
- [OpenSSL Documentation](https://www.openssl.org/docs/)
- [Conan Documentation](https://docs.conan.io/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

### Project Resources
- [Project Status](../STATUS.md) - Current capabilities and metrics
- [Changelog](../CHANGELOG.md) - Version history and changes
- [Contributing Guide](../CONTRIBUTING.md) - How to contribute

### Support
- [GitHub Issues](https://github.com/sparesparrow/openssl-tools/issues) - Bug reports and feature requests
- [GitHub Discussions](https://github.com/sparesparrow/openssl-tools/discussions) - Questions and community support

---

**Last Updated**: October 2024  
**Maintainer**: OpenSSL Tools Team
