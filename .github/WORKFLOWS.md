# OpenSSL Tools Workflows Documentation

This document describes the GitHub Actions workflow structure for the openssl-tools repository.

## Overview

The openssl-tools project uses a modernized CI/CD pipeline built on Conan 2.0, replacing the traditional OpenSSL build system with a package management approach.

## Active Workflows (Production)

### Core Build Workflows

#### `openssl-build-publish.yml`
- **Purpose**: Main CI/CD pipeline for building and publishing OpenSSL packages
- **Triggers**: Push to main/develop, PRs, scheduled weekly builds
- **Features**:
  - Multi-platform builds (Linux, Windows, macOS)
  - Multiple compiler support (GCC, Clang, MSVC)
  - FIPS compliance builds
  - Artifact publishing to Artifactory
  - SBOM generation
- **Matrix**: 5 platforms × 3 components = 15 builds

#### `conan-ci.yml`
- **Purpose**: Conan-specific CI for package validation
- **Triggers**: Changes to conanfile.py, conan-profiles, or source code
- **Features**:
  - Change detection
  - Conan package validation
  - Cross-platform testing
  - Dependency resolution

### Quality Assurance Workflows

#### `static-analysis.yml`
- **Purpose**: Static code analysis and security scanning
- **Triggers**: Daily schedule, push to main/develop, PRs
- **Features**:
  - Coverity static analysis
  - Security vulnerability scanning
  - Code quality metrics
  - FIPS compliance validation

#### `style-checks.yml`
- **Purpose**: Code style and formatting validation
- **Triggers**: Push to main/develop, PRs
- **Features**:
  - Clang-format validation
  - Markdown formatting checks
  - Documentation validation
  - Coding standards enforcement

## Reusable Workflows

### `.github/workflows/reusable/build-component.yml`
Reusable workflow for building individual OpenSSL components.

**Inputs:**
- `component`: Component name (openssl, openssl-fips, openssl-quic)
- `platform`: Platform identifier (linux-gcc11, windows-msvc2022, etc.)
- `build-type`: Build type (Debug, Release, RelWithDebInfo)
- `fips-enabled`: Enable FIPS mode
- `upload-artifacts`: Upload build artifacts

**Usage:**
```yaml
uses: ./.github/workflows/reusable/build-component.yml
with:
  component: 'openssl'
  platform: 'linux-gcc11'
  build-type: 'Release'
  fips-enabled: false
```

### `.github/workflows/reusable/security-scan.yml`
Reusable workflow for security scanning and compliance validation.

**Inputs:**
- `component`: Component name to scan
- `scan-type`: Scan type (quick, full, fips)
- `generate-sbom`: Generate Software Bill of Materials

### `.github/workflows/reusable/upload-registry.yml`
Reusable workflow for uploading packages to various registries.

**Inputs:**
- `component`: Component name to upload
- `platform`: Platform identifier
- `registry`: Target registry (artifactory, github, conancenter)

## Workflow Templates

### `.github/workflow-templates/openssl-build.yml`
Complete OpenSSL build template that can be used as a starting point for new workflows.

**Features:**
- Multi-component support (openssl, openssl-fips, openssl-quic)
- Change detection
- Reusable workflow integration
- Security scanning
- Artifact upload

## Archived Workflows

### Legacy OpenSSL (`.github/workflows-backup/legacy-openssl/`)
Workflows from upstream openssl/tools that are incompatible with the Conan 2.0 modernization:

- `backport.yml` - OpenSSL backport management
- `ci.yml` - Original OpenSSL CI pipeline
- `core-ci.yml` - Core OpenSSL CI with comprehensive testing
- `cross-compiles.yml` - Cross-compilation for various architectures
- `deploy-docs-openssl-org.yml` - Documentation deployment
- `openssl-build-test.yml` - OpenSSL build testing
- `openssl-integration.yml` - OpenSSL integration testing
- `weekly-exhaustive.yml` - Weekly comprehensive testing
- `windows.yml` - Windows-specific OpenSSL builds

**Why archived:** These workflows expect traditional OpenSSL source structure with `Configure`, `config`, `VERSION.dat`, and source directories that don't exist in the openssl-tools package management approach.

### Upstream-Only (`.github/workflows-backup/upstream-only/`)
Workflows specifically designed for the OpenSSL source repository:

- `backport.yml` - Backports CI for different OpenSSL releases
- `ci.yml` - Main OpenSSL CI/CD Pipeline
- `core-ci.yml` - Core OpenSSL CI with comprehensive testing
- `cross-compiles.yml` - Cross-compilation for various architectures
- `deploy-docs-openssl-org.yml` - Documentation deployment to openssl.org
- `openssl-build-test.yml` - OpenSSL build testing
- `openssl-integration.yml` - OpenSSL integration testing
- `os-zoo.yml` - OS distribution testing
- `weekly-exhaustive.yml` - Weekly comprehensive testing
- `windows.yml` - Windows-specific OpenSSL builds

**Why archived:** These workflows are designed for OpenSSL source development rather than package management.

### Experimental (`.github/workflows-backup/experimental/`)
Workflows from PR #6 development iterations and experimental approaches:

- `nuclear-success.yml` - Nuclear approach to CI success
- `minimal-success.yml` - Minimal CI approach
- `simple-success-override.yml` - Simple success override
- `optimized-basic-ci.yml` - Optimized basic CI
- `fast-lane-ci.yml` - Fast lane CI approach
- `incremental-ci-patch.yml` - Incremental CI patches
- Various other experimental workflows

**Why archived:** These were development iterations and experimental approaches that have been superseded by the current production workflows.

## Migration Notes

When adapting archived workflows for openssl-tools:

1. **Replace OpenSSL source references** with Conan package references
2. **Use `conanfile.py`** instead of `Configure`/`config`
3. **Use `conan-profiles/`** instead of OpenSSL-specific build configurations
4. **Focus on package building** and publishing rather than source compilation
5. **Use reusable workflows** for common patterns
6. **Implement proper change detection** to avoid unnecessary builds

## Best Practices

### Workflow Design
- Use reusable workflows for common patterns
- Implement proper change detection to optimize build times
- Use matrix strategies for multi-platform builds
- Implement proper caching for dependencies and build artifacts

### Security
- Generate SBOMs for all packages
- Perform security scanning on all builds
- Validate FIPS compliance when required
- Use secure secrets management

### Performance
- Use intelligent caching strategies
- Implement parallel builds where possible
- Use build artifacts for sharing between jobs
- Optimize dependency resolution

### Maintenance
- Keep workflows simple and focused
- Use clear naming conventions
- Document workflow purposes and triggers
- Regular cleanup of unused workflows

## Troubleshooting

### Common Issues
1. **Build failures**: Check Conan profile configuration and dependencies
2. **Cache issues**: Clear Conan cache and rebuild
3. **Platform-specific issues**: Verify platform-specific configurations
4. **Security scan failures**: Review security reports and update dependencies

### Debugging
- Enable verbose logging in Conan commands
- Check workflow logs for specific error messages
- Verify environment variables and secrets
- Test locally with the same Conan profiles

## Future Improvements

1. **Enhanced security scanning** with additional tools
2. **Performance benchmarking** for build optimization
3. **Automated dependency updates** with security validation
4. **Cross-repository integration** for related projects
5. **Advanced caching strategies** for faster builds

## References

- [Conan 2.0 Documentation](https://docs.conan.io/2.0/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [OpenSSL Documentation](https://www.openssl.org/docs/)
- [FIPS 140-2 Compliance](https://csrc.nist.gov/publications/detail/fips/140/2/final)