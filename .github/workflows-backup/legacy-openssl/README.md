# Legacy OpenSSL Workflows

This directory contains workflows from upstream openssl/tools that are incompatible with the Conan 2.0 modernization approach used in openssl-tools.

## Why These Workflows Are Archived

### Incompatible Build System
- **Traditional OpenSSL build**: Uses `Configure`, `config`, `VERSION.dat`
- **Source-based approach**: Expects OpenSSL source directory structure
- **Make-based builds**: Uses `make` commands instead of Conan
- **Platform-specific configs**: OpenSSL-specific configuration files

### Missing Dependencies
- **OpenSSL source files**: `crypto/`, `ssl/`, `apps/` directories
- **Build scripts**: OpenSSL-specific build and test scripts
- **Configuration files**: `Configure`, `config`, `VERSION.dat`
- **Test suites**: OpenSSL-specific test frameworks

### Different Purpose
- **Source development**: Designed for OpenSSL source repository
- **Package management**: Not designed for Conan package management
- **Cross-compilation**: OpenSSL-specific cross-compilation patterns
- **Documentation**: OpenSSL.org specific deployment

## Workflows in This Archive

### Core CI Workflows
- `backport.yml` - Backports CI for different OpenSSL releases
- `ci.yml` - Main OpenSSL CI/CD Pipeline  
- `core-ci.yml` - Core OpenSSL CI with comprehensive testing
- `openssl-build-test.yml` - OpenSSL build testing
- `openssl-integration.yml` - OpenSSL integration testing

### Cross-Platform Workflows
- `cross-compiles.yml` - Cross-compilation for various architectures
- `os-zoo.yml` - OS distribution testing
- `windows.yml` - Windows-specific OpenSSL builds
- `windows_comp.yml` - Windows compiler testing
- `windows-override.yml` - Windows build overrides

### Specialized Workflows
- `deploy-docs-openssl-org.yml` - Documentation deployment to openssl.org
- `weekly-exhaustive.yml` - Weekly comprehensive testing
- `openssl-ci-dispatcher.yml` - OpenSSL CI dispatcher

## Adaptation Guidelines

If you need to adapt these workflows for openssl-tools:

### 1. Replace OpenSSL Source References
```yaml
# OLD (Legacy)
- name: Configure OpenSSL
  run: ./config --prefix=/usr/local

# NEW (Conan)
- name: Install dependencies
  run: conan install . --profile=linux-gcc11 --build=missing
```

### 2. Use Conan Instead of Make
```yaml
# OLD (Legacy)
- name: Build OpenSSL
  run: make -j$(nproc)

# NEW (Conan)
- name: Build package
  run: conan build . --profile=linux-gcc11
```

### 3. Replace Platform-Specific Configs
```yaml
# OLD (Legacy)
- name: Configure for platform
  run: ./Configure linux-x86_64

# NEW (Conan)
- name: Use Conan profile
  run: conan create . --profile=linux-gcc11
```

### 4. Adapt Testing Approaches
```yaml
# OLD (Legacy)
- name: Run OpenSSL tests
  run: make test

# NEW (Conan)
- name: Test package
  run: conan test test_package . --profile=linux-gcc11
```

## Key Differences

| Aspect | Legacy OpenSSL | Modern Conan |
|--------|----------------|--------------|
| Build System | Configure + Make | Conan 2.0 |
| Configuration | Platform-specific configs | Conan profiles |
| Dependencies | Manual management | Conan dependency resolution |
| Testing | OpenSSL test suite | Conan test_package |
| Packaging | Manual packaging | Conan package management |
| Cross-compilation | Configure flags | Conan profiles |
| Documentation | OpenSSL.org deployment | Package documentation |

## References

- [OpenSSL Build System](https://www.openssl.org/docs/man3.0/man7/openssl_user_macros.html)
- [Conan 2.0 Documentation](https://docs.conan.io/2.0/)
- [OpenSSL Cross-Compilation](https://wiki.openssl.org/index.php/Compilation_and_Installation)