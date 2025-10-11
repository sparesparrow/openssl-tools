# OpenSSL CI/CD Reusable Workflows

This directory contains reusable GitHub Actions workflows that can be used by downstream OpenSSL repositories to standardize their CI/CD processes.

## Available Workflows

### `openssl-ci.yaml` - Main CI/CD Pipeline

The primary reusable workflow that provides a comprehensive CI/CD pipeline for OpenSSL projects.

**Features:**
- ✅ Matrix builds across multiple platforms (Ubuntu, Windows, macOS)
- ✅ Multiple build types (Release, Debug, RelWithDebInfo)
- ✅ Security scanning (SAST/DAST) with Trivy, Bandit, Semgrep
- ✅ SBOM generation in CycloneDX format
- ✅ Performance benchmarking
- ✅ Artifact publishing to GitHub Packages and Conan remotes
- ✅ Automated failure analysis with Cursor AI
- ✅ Smart caching for faster builds

## Usage in Downstream Repositories

### Basic Usage

Create a workflow file in your downstream repository (e.g., `.github/workflows/ci.yml`):

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  openssl-ci:
    uses: sparesparrow/openssl-tools/.github/workflows/openssl-ci.yaml@main
    with:
      platforms: 'ubuntu-22.04,windows-2022,macos-12'
      build_types: 'Release,Debug'
      enable_security: true
      enable_sbom: true
      upload_artifacts: true
```

### Advanced Usage with Custom Configuration

```yaml
name: Advanced CI/CD Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  schedule:
    # Weekly security scans
    - cron: '0 2 * * 1'

jobs:
  openssl-ci:
    uses: sparesparrow/openssl-tools/.github/workflows/openssl-ci.yaml@main
    with:
      # Custom platform matrix
      platforms: 'ubuntu-22.04,ubuntu-20.04,windows-2022'
      
      # Multiple build types
      build_types: 'Release,Debug,RelWithDebInfo'
      
      # Enable all features
      enable_security: true
      enable_benchmarks: ${{ github.ref == 'refs/heads/main' }}
      enable_sbom: true
      upload_artifacts: ${{ github.ref == 'refs/heads/main' }}
      
      # Custom Conan profile
      conan_profile: 'ci-linux-gcc'
    secrets:
      # Conan remote credentials
      CONAN_REMOTE_URL: ${{ secrets.CONAN_REMOTE_URL }}
      CONAN_USER: ${{ secrets.CONAN_USER }}
      CONAN_PASSWORD: ${{ secrets.CONAN_PASSWORD }}
      
      # Cursor AI for automated fixes
      CURSOR_API_KEY: ${{ secrets.CURSOR_API_KEY }}
      
      # Database for build tracking
      DATABASE_URL: ${{ secrets.DATABASE_URL }}

  # Additional downstream-specific jobs
  custom-tests:
    needs: openssl-ci
    if: always()
    runs-on: ubuntu-latest
    steps:
      - name: Check CI status
        run: |
          if [[ "${{ needs.openssl-ci.result }}" == "success" ]]; then
            echo "✅ OpenSSL CI passed"
          else
            echo "❌ OpenSSL CI failed"
            exit 1
          fi
      - name: Run custom tests
        run: |
          # Your custom test commands here
```

## Workflow Inputs

| Input | Description | Required | Default | Type |
|-------|-------------|----------|---------|------|
| `platforms` | Comma-separated list of platforms | No | `ubuntu-22.04,windows-2022,macos-12` | string |
| `build_types` | Comma-separated list of build types | No | `Release,Debug` | string |
| `enable_security` | Enable security scanning | No | `true` | boolean |
| `enable_benchmarks` | Enable performance benchmarks | No | `false` | boolean |
| `enable_sbom` | Enable SBOM generation | No | `true` | boolean |
| `upload_artifacts` | Upload build artifacts | No | `true` | boolean |
| `conan_profile` | Conan profile to use | No | `ci-linux-gcc` | string |

## Workflow Secrets

| Secret | Description | Required | Default |
|--------|-------------|----------|---------|
| `CONAN_REMOTE_URL` | Conan remote URL for package uploads | No | GitHub Packages |
| `CONAN_USER` | Conan remote username | No | GitHub actor |
| `CONAN_PASSWORD` | Conan remote password | No | GitHub token |
| `CURSOR_API_KEY` | Cursor AI API key for automated fixes | No | None |
| `DATABASE_URL` | Database URL for build tracking | No | None |

## Supported Platforms

The workflow supports the following platforms:

- **Ubuntu 22.04** - GCC 11, Clang 15
- **Ubuntu 20.04** - GCC 9, Clang 12
- **Windows 2022** - MSVC 2022
- **macOS 12** - Clang 14 (x86_64, ARM64)

## Build Types

- **Release** - Optimized production builds
- **Debug** - Debug builds with symbols
- **RelWithDebInfo** - Release builds with debug info

## Security Scanning

The workflow includes comprehensive security scanning:

- **SAST** - Static Application Security Testing with Semgrep
- **DAST** - Dynamic Application Security Testing with Trivy
- **Dependency Scanning** - Vulnerability scanning with Safety
- **Compliance** - License and policy compliance checks

## SBOM Generation

Software Bill of Materials (SBOM) is generated in CycloneDX format including:

- All dependencies and their versions
- License information
- Vulnerability data
- Build metadata

## Performance Benchmarking

Performance benchmarks include:

- **Speed tests** - Cryptographic operation performance
- **Memory tests** - Memory usage and leaks
- **Crypto tests** - Algorithm-specific benchmarks

## Artifact Publishing

Build artifacts are published to:

- **GitHub Packages** - Primary package registry
- **Conan Remotes** - Configurable Conan remotes
- **Build Artifacts** - GitHub Actions artifacts

## Caching Strategy

The workflow uses intelligent caching:

- **Conan cache** - Package dependencies
- **Compiler cache** - ccache/sccache for faster builds
- **Build cache** - Incremental builds

## Automated Failure Analysis

When enabled with `CURSOR_API_KEY`, the workflow provides:

- Automatic failure analysis
- Suggested fixes
- Automated patch application
- PR comments with analysis

## Examples for Different Repository Types

### OpenSSL Source Repository

```yaml
jobs:
  openssl-ci:
    uses: sparesparrow/openssl-tools/.github/workflows/openssl-ci.yaml@main
    with:
      platforms: 'ubuntu-22.04,ubuntu-20.04,windows-2022,macos-12'
      build_types: 'Release,Debug'
      enable_security: true
      enable_benchmarks: true
      enable_sbom: true
      upload_artifacts: true
```

### OpenSSL Tools Repository

```yaml
jobs:
  openssl-ci:
    uses: sparesparrow/openssl-tools/.github/workflows/openssl-ci.yaml@main
    with:
      platforms: 'ubuntu-22.04,windows-2022'
      build_types: 'Release'
      enable_security: true
      enable_sbom: true
      upload_artifacts: ${{ github.ref == 'refs/heads/main' }}
```

### OpenSSL Documentation Repository

```yaml
jobs:
  openssl-ci:
    uses: sparesparrow/openssl-tools/.github/workflows/openssl-ci.yaml@main
    with:
      platforms: 'ubuntu-22.04'
      build_types: 'Release'
      enable_security: true
      enable_sbom: false
      upload_artifacts: false
```

## Troubleshooting

### Common Issues

1. **Build Failures**
   - Check Conan profiles are available
   - Verify platform compatibility
   - Review build logs for specific errors

2. **Security Scan Failures**
   - Update security tools
   - Review false positives
   - Check scan configuration

3. **SBOM Generation Issues**
   - Verify dependency resolution
   - Check CycloneDX format compliance
   - Review metadata completeness

4. **Artifact Upload Failures**
   - Verify remote credentials
   - Check network connectivity
   - Review package permissions

### Getting Help

- Check the [OpenSSL Tools documentation](../docs/)
- Review [troubleshooting guide](../TROUBLESHOOTING.md)
- Open an issue in the [openssl-tools repository](https://github.com/sparesparrow/openssl-tools)

## Contributing

To contribute to the reusable workflows:

1. Fork the openssl-tools repository
2. Make your changes to the workflow files
3. Test with a downstream repository
4. Submit a pull request

## Versioning

Workflows are versioned using Git tags. Use specific versions in production:

```yaml
uses: sparesparrow/openssl-tools/.github/workflows/openssl-ci.yaml@v1.0.0
```

For development, use the main branch:

```yaml
uses: sparesparrow/openssl-tools/.github/workflows/openssl-ci.yaml@main
```
