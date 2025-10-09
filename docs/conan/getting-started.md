# Conan Getting Started Guide

This guide will help you get started with using Conan package management for OpenSSL builds.

## Prerequisites

Before you begin, ensure you have:

- **Python 3.8+** (we support 3.8, 3.9, 3.10, 3.11, 3.12)
- **Conan 2.x** installed
- **Git** for version control
- **Basic command-line knowledge**

## Quick Start (5 minutes)

### 1. Install Conan

```bash
# Install Conan 2.x
pip install conan

# Verify installation
conan --version
```

### 2. Configure Conan

```bash
# Configure Conan with our settings
conan config install conan/

# Verify configuration
conan config list
```

### 3. Create Your First Package

```bash
# Create a basic OpenSSL package
conan create . --profile=conan-profiles/linux-gcc-release.profile

# Or install dependencies only
conan install . --build=missing
```

### 4. Test the Package

```bash
# Run the test package
conan test test_package openssl/3.5.0@openssl/stable

# Or use the test package directly
cd test_package
conan install . --build=missing
conan build .
```

## Available Profiles

OpenSSL Tools includes several pre-configured profiles for different use cases:

### Production Profiles

**Linux GCC Release** (`linux-gcc-release.profile`):
```bash
conan create . --profile=conan-profiles/linux-gcc-release.profile
```
- Optimized for performance (`-O3 -march=native`)
- FIPS disabled, shared libraries
- Tests skipped for faster builds

**Windows MSVC** (`windows-msvc.profile`):
```bash
conan create . --profile=conan-profiles/windows-msvc.profile
```
- Visual Studio 2022 integration
- Windows-specific optimizations
- Platform-specific system libraries

**macOS Clang** (`macos-clang.profile`):
```bash
conan create . --profile=conan-profiles/macos-clang.profile
```
- ARM64 optimized
- macOS deployment target 12.0+
- Clang-specific optimizations

### Development Profiles

**Linux GCC Debug** (`linux-gcc-debug.profile`):
```bash
conan create . --profile=conan-profiles/linux-gcc-debug.profile
```
- Debug symbols enabled (`-g -O0`)
- Unit tests enabled
- Demos and tracing enabled
- Crypto memory debugging

### FIPS Profiles

**Linux FIPS** (`linux-fips.profile`):
```bash
conan create . --profile=conan-profiles/linux-fips.profile
```
- **CRITICAL**: Separate cache key to prevent contamination
- FIPS mode enabled with compliance checks
- Restricted algorithms (no MD2, RC5, RC4, DES)
- Unit tests enabled for validation

## Basic Usage Examples

### Package Creation

```bash
# Create package with default profile
conan create . --profile=conan-profiles/linux-gcc-release.profile

# Create package with specific options
conan create . --profile=conan-profiles/linux-gcc-release.profile \
    -o openssl:shared=True \
    -o openssl:fips=False

# Create debug package
conan create . --profile=conan-profiles/linux-gcc-debug.profile
```

### FIPS Build

```bash
# Create FIPS-compliant package
conan create . --profile=conan-profiles/linux-fips.profile

# Verify FIPS mode
conan create . --profile=conan-profiles/linux-fips.profile \
    -o openssl:enable_unit_test=True
```

### Cross-Platform Builds

```bash
# Windows build
conan create . --profile=conan-profiles/windows-msvc.profile

# macOS build
conan create . --profile=conan-profiles/macos-clang.profile

# Linux build
conan create . --profile=conan-profiles/linux-gcc-release.profile
```

## Understanding the Conanfile

The OpenSSL Conan recipe (`conanfile.py`) provides comprehensive build options:

### Key Options

```python
options = {
    "shared": [True, False],           # Build shared libraries
    "fips": [True, False],             # Enable FIPS mode
    "no_asm": [True, False],           # Disable assembly optimizations
    "no_threads": [True, False],       # Disable threading support
    "no_stdio": [True, False],         # Disable stdio support
    "enable_unit_test": [True, False], # Enable unit tests
    "enable_crypto_mdebug": [True, False], # Enable crypto memory debugging
    # ... and many more
}
```

### Using Options

```bash
# Build with specific options
conan create . --profile=conan-profiles/linux-gcc-release.profile \
    -o openssl:shared=True \
    -o openssl:no_asm=False \
    -o openssl:enable_unit_test=True

# Build static libraries
conan create . --profile=conan-profiles/linux-gcc-release.profile \
    -o openssl:shared=False

# Build with assembly optimizations disabled
conan create . --profile=conan-profiles/linux-gcc-release.profile \
    -o openssl:no_asm=True
```

## Package Management

### Installing Packages

```bash
# Install OpenSSL package
conan install openssl/3.5.0@openssl/stable

# Install with specific profile
conan install openssl/3.5.0@openssl/stable \
    --profile=conan-profiles/linux-gcc-release.profile

# Install with options
conan install openssl/3.5.0@openssl/stable \
    --profile=conan-profiles/linux-gcc-release.profile \
    -o openssl:shared=True
```

### Searching Packages

```bash
# Search for OpenSSL packages
conan search openssl

# Search in specific remote
conan search openssl --remote=github-packages

# Search with pattern
conan search "openssl/*"
```

### Managing Remotes

```bash
# List remotes
conan remote list

# Add remote
conan remote add github-packages https://maven.pkg.github.com/sparesparrow/index.json

# Remove remote
conan remote remove github-packages
```

## Integration with Your Project

### Using in CMake

Create a `conanfile.txt` in your project:

```ini
[requires]
openssl/3.5.0@openssl/stable

[generators]
CMakeDeps
CMakeToolchain

[options]
openssl:shared=True
```

Then use in your CMake:

```cmake
find_package(OpenSSL REQUIRED)
target_link_libraries(your_target OpenSSL::SSL OpenSSL::Crypto)
```

### Using in Conan

Create a `conanfile.py` in your project:

```python
from conan import ConanFile

class YourProjectConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    requires = "openssl/3.5.0@openssl/stable"
    
    def configure(self):
        self.options["openssl"].shared = True
```

## Best Practices

### Profile Management

- Use platform-specific profiles
- Keep profiles minimal and focused
- Document profile purposes
- Version control all profiles

### Build Options

- Use appropriate optimization levels
- Enable tests for development builds
- Disable unnecessary features for production
- Use FIPS profiles only when required

### Package Versioning

- Use semantic versioning
- Tag releases properly
- Maintain compatibility
- Document breaking changes

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

1. **Check Documentation**: Browse the [Conan documentation](https://docs.conan.io/)
2. **Search Issues**: Look for similar issues in [GitHub Issues](https://github.com/sparesparrow/openssl-tools/issues)
3. **Ask Questions**: Create a [GitHub Discussion](https://github.com/sparesparrow/openssl-tools/discussions)

## Next Steps

Now that you understand the basics:

1. **Learn More**: Read [Profiles](profiles.md) for detailed profile information
2. **Build OpenSSL**: See [Building](building.md) for comprehensive build guide
3. **Configure Repository**: Check [Artifactory](artifactory.md) for package repository setup
4. **Optimize Performance**: Explore [Caching](caching.md) for build optimization

## Related Documentation

- [Profiles](profiles.md) - Detailed profile guide
- [Building](building.md) - Comprehensive build guide
- [Testing](testing.md) - Test package usage
- [Troubleshooting Guide](../how-to/troubleshooting.md)

---

**Need Help?** Check the [Troubleshooting Guide](../how-to/troubleshooting.md) or [ask the community](https://github.com/sparesparrow/openssl-tools/discussions).
