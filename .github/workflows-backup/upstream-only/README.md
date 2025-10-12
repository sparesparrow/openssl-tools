# OpenSSL Upstream-Only Workflows

This directory contains GitHub Actions workflows that are specifically designed for the OpenSSL source repository (`openssl/openssl`) and are not suitable for the `openssl-tools` repository.

## Archived Workflows

These workflows have been moved here because they:

1. **Reference OpenSSL source files** that don't exist in openssl-tools:
   - `Configure`, `config`, `VERSION.dat`
   - `crypto/`, `ssl/`, `apps/` directories
   - OpenSSL-specific build scripts

2. **Are designed for OpenSSL development** rather than package management:
   - Cross-compilation for various platforms
   - OpenSSL-specific testing and validation
   - Documentation deployment to openssl.org
   - Backport management for OpenSSL releases

3. **Use OpenSSL-specific CI patterns**:
   - Direct `./config` and `make` commands
   - OpenSSL test suite execution
   - OpenSSL-specific environment setup

## Workflows in this Archive

- `backport.yml` - Backports CI for different OpenSSL releases
- `ci.yml` - Main OpenSSL CI/CD Pipeline
- `core-ci.yml` - Core OpenSSL CI with comprehensive testing
- `cross-compiles.yml` - Cross-compilation for various architectures
- `deploy-docs-openssl-org.yml` - Documentation deployment to openssl.org
- `disable-upstream-workflows.yml` - Workflow to disable upstream workflows
- `openssl-build-test.yml` - OpenSSL build testing
- `openssl-integration.yml` - OpenSSL integration testing
- `openssl-ci-dispatcher.yml` - OpenSSL CI dispatcher
- `os-zoo.yml` - OS distribution testing
- `weekly-exhaustive.yml` - Weekly comprehensive testing
- `windows.yml` - Windows-specific OpenSSL builds
- `windows_comp.yml` - Windows compiler testing
- `windows-override.yml` - Windows build overrides

## Usage

These workflows should **NOT** be enabled in the openssl-tools repository. They are kept here for reference and potential future adaptation if needed.

If you need similar functionality for openssl-tools, consider:
1. Using the enabled workflows in `.github/workflows/`
2. Adapting these workflows to work with Conan and the openssl-tools structure
3. Creating new workflows specifically designed for package management

## Migration Notes

When adapting these workflows for openssl-tools:
1. Replace OpenSSL source references with Conan package references
2. Use `conanfile.py` instead of `Configure`/`config`
3. Use `conan-profiles/` instead of OpenSSL-specific build configurations
4. Focus on package building and publishing rather than source compilation
