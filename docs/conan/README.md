# Conan Package Management Guide

This section provides comprehensive documentation for using Conan package management with OpenSSL Tools.

## Overview

Conan is used to manage OpenSSL packages, dependencies, and build configurations. OpenSSL Tools provides a complete Conan integration with:

- **Package Recipe**: Complete `conanfile.py` with all OpenSSL options
- **Build Profiles**: Platform-specific build configurations
- **Test Package**: Validation and smoke testing
- **CI/CD Integration**: Automated package building and testing

## Quick Start

### Basic Usage

```bash
# Create OpenSSL package
conan create . --profile=conan-profiles/linux-gcc-release.profile

# Install OpenSSL package
conan install openssl/3.5.0@openssl/stable

# Use in your project
conan install . --build=missing
```

### Available Profiles

```bash
# List all profiles
ls conan-profiles/

# Use specific profile
conan create . --profile=conan-profiles/linux-gcc-release.profile
conan create . --profile=conan-profiles/linux-fips.profile
conan create . --profile=conan-profiles/macos-clang.profile
```

## Documentation Structure

### Getting Started
- [Getting Started](getting-started.md) - Quick setup and basic usage
- [Profiles](profiles.md) - Understanding and using build profiles
- [Building](building.md) - Building OpenSSL with Conan

### Configuration
- [Artifactory](artifactory.md) - Package repository setup
- [Caching](caching.md) - Build cache optimization
- [Testing](testing.md) - Test package usage

### Advanced Topics
- [Custom Profiles](advanced/custom-profiles.md) - Creating custom build profiles
- [FIPS Builds](advanced/fips-builds.md) - FIPS-compliant builds
- [Performance Tuning](advanced/performance-tuning.md) - Build optimization
- [CI Integration](advanced/ci-integration.md) - CI/CD integration

### Reference
- [Conanfile API](reference/conanfile-api.md) - Complete conanfile.py reference
- [Options](reference/options.md) - All available build options
- [Commands](reference/commands.md) - Common Conan commands

## Key Features

### Comprehensive Options

The OpenSSL Conan recipe supports all major OpenSSL build options:

```python
options = {
    "shared": [True, False],
    "fips": [True, False],
    "no_asm": [True, False],
    "no_threads": [True, False],
    "no_stdio": [True, False],
    "enable_unit_test": [True, False],
    "enable_crypto_mdebug": [True, False],
    # ... and many more
}
```

### Platform Support

- **Linux**: GCC, Clang with various versions
- **macOS**: Clang with Apple Silicon and Intel support
- **Windows**: MSVC with Visual Studio integration

### Security Features

- **FIPS Support**: Separate cache keys to prevent contamination
- **Package Signing**: Integration with cosign for supply chain security
- **Vulnerability Scanning**: Automated security scanning
- **SBOM Generation**: Software Bill of Materials

## Common Workflows

### Development Workflow

```bash
# 1. Set up environment
python setup_python_env.py --versions 3.11

# 2. Configure Conan
conan config install conan/

# 3. Create package
conan create . --profile=conan-profiles/linux-gcc-debug.profile

# 4. Test package
conan test test_package openssl/3.5.0@openssl/stable
```

### CI/CD Workflow

```bash
# 1. Install dependencies
conan install . --build=missing

# 2. Build package
conan build .

# 3. Test package
conan test test_package openssl/3.5.0@openssl/stable

# 4. Upload package
conan upload "*" -r=github-packages --confirm
```

### Production Workflow

```bash
# 1. Create production package
conan create . --profile=conan-profiles/linux-gcc-release.profile

# 2. Sign package
python package_signer.py --sign-dir ./packages

# 3. Upload to registry
conan upload "*" -r=production-registry --confirm

# 4. Generate SBOM
python scripts/generate_sbom.py
```

## Integration Points

### With OpenSSL Repository

- **Cross-repo triggers**: OpenSSL changes trigger Conan builds
- **Status reporting**: Build results reported back to OpenSSL PRs
- **Artifact sharing**: Built packages available to OpenSSL repo

### With CI/CD

- **GitHub Actions**: Automated package building and testing
- **Artifactory**: Package storage and distribution
- **Security scanning**: Automated vulnerability detection

### With Development Tools

- **Build optimization**: Intelligent caching and parallel builds
- **Performance monitoring**: Build time and resource tracking
- **Quality gates**: Automated testing and validation

## Best Practices

### Profile Management

- Use platform-specific profiles
- Keep profiles minimal and focused
- Document profile purposes
- Version control all profiles

### Package Versioning

- Use semantic versioning
- Tag releases properly
- Maintain compatibility
- Document breaking changes

### Security

- Sign all packages
- Scan for vulnerabilities
- Use secure defaults
- Rotate keys regularly

## Troubleshooting

### Common Issues

**Build Failures**:
```bash
# Check build logs
cat build.log

# Clean build directory
rm -rf build/

# Rebuild from scratch
conan create . --profile=conan-profiles/linux-gcc-release.profile --build=missing
```

**Profile Issues**:
```bash
# List available profiles
conan profile list

# Show profile details
conan profile show conan-profiles/linux-gcc-release.profile

# Validate profile
conan profile validate conan-profiles/linux-gcc-release.profile
```

**Cache Issues**:
```bash
# Check cache status
conan cache path

# Clean cache
conan cache clean

# Remove specific package
conan remove openssl/3.5.0@openssl/stable
```

### Getting Help

1. **Check Documentation**: Browse the specific guides above
2. **Search Issues**: Look for similar issues in [GitHub Issues](https://github.com/sparesparrow/openssl-tools/issues)
3. **Ask Questions**: Create a [GitHub Discussion](https://github.com/sparesparrow/openssl-tools/discussions)
4. **Conan Documentation**: Check [Conan Documentation](https://docs.conan.io/)

## Related Documentation

- [Getting Started Guide](../tutorials/getting-started.md)
- [Architecture Overview](../explanation/architecture.md)
- [CI/CD Patterns](../explanation/cicd-patterns.md)
- [Troubleshooting Guide](../how-to/troubleshooting.md)

---

**Need Help?** Check the specific guides above or [ask the community](https://github.com/sparesparrow/openssl-tools/discussions).
