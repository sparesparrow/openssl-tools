# OpenSSL Tools Reusable Workflows

This directory contains reusable GitHub Actions workflows that can be called from other repositories in the OpenSSL ecosystem.

## Available Workflows

### `build-component.yml`
Builds OpenSSL components using Conan with support for multiple platforms and configurations.

**Features:**
- Multi-platform support (Linux, Windows, macOS)
- FIPS mode support
- Artifact upload
- Conan package caching

**Usage:**
```yaml
jobs:
  build:
    uses: sparesparrow/openssl-tools/.github/workflows/reusable/build-component.yml@reusable-workflows/v1.0.0
    with:
      component: 'openssl'
      platform: 'linux-gcc11'
      fips-enabled: false
    secrets:
      CONAN_LOGIN_USERNAME: ${{ secrets.CONAN_LOGIN_USERNAME }}
      CONAN_PASSWORD: ${{ secrets.CONAN_PASSWORD }}
```

### `security-scan.yml`
Performs comprehensive security scanning including vulnerability checks, static analysis, and SBOM generation.

**Features:**
- Dependency vulnerability scanning (Safety)
- Static security analysis (Bandit)
- SAST scanning (Semgrep)
- SBOM generation (CycloneDX)
- FIPS compliance checks

**Usage:**
```yaml
jobs:
  security:
    uses: sparesparrow/openssl-tools/.github/workflows/reusable/security-scan.yml@reusable-workflows/v1.0.0
    with:
      component: 'openssl'
      scan-type: 'full'
      generate-sbom: true
    secrets:
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### `upload-registry.yml`
Uploads built packages to artifact registries with OIDC authentication support.

**Features:**
- OIDC authentication for Cloudsmith (recommended)
- Fallback API key authentication
- Multiple registry support (Cloudsmith, Artifactory, GitHub, ConanCenter)
- Upload verification

**Usage:**
```yaml
jobs:
  upload:
    uses: sparesparrow/openssl-tools/.github/workflows/reusable/upload-registry.yml@reusable-workflows/v1.0.0
    with:
      component: 'openssl'
      platform: 'linux-gcc11'
      registry: 'cloudsmith'
```

## Versioning

Workflows are versioned using Git tags with the format `reusable-workflows/v{major}.{minor}.{patch}`.

- **v1.0.0**: Initial release with OIDC support
- **v1.1.0**: Enhanced security scanning and FIPS validation
- **v1.2.0**: Cross-platform build improvements

## Security Features

### OIDC Authentication
All workflows now support OIDC (OpenID Connect) authentication for Cloudsmith publishing, eliminating the need for long-lived API keys.

**Benefits:**
- Enhanced security (no credential sprawl)
- Automatic token rotation
- Audit trail of package uploads
- FIPS compliance

### Required Permissions
```yaml
permissions:
  id-token: write    # Required for OIDC
  contents: read     # Required for checkout
  security-events: write  # Required for security scanning
```

## Migration Guide

### From API Keys to OIDC

1. **Update workflow calls** to use version tags:
   ```yaml
   uses: sparesparrow/openssl-tools/.github/workflows/reusable/upload-registry.yml@reusable-workflows/v1.0.0
   ```

2. **Add OIDC permissions** to calling workflows:
   ```yaml
   permissions:
     id-token: write
     contents: read
   ```

3. **Remove API key secrets** once OIDC is configured in the organization.

### Organization Setup
1. Enable OIDC in GitHub organization settings
2. Configure Cloudsmith OIDC provider with audience `https://cloudsmith.io`
3. Grant appropriate permissions to repositories

## Troubleshooting

### Common Issues

**OIDC Token Request Failed**
- Ensure `permissions: id-token: write` is set
- Verify OIDC is enabled in organization settings
- Check Cloudsmith OIDC provider configuration

**Workflow Not Found**
- Use full repository path: `sparesparrow/openssl-tools`
- Reference specific version tag: `@reusable-workflows/v1.0.0`

**Permission Denied**
- Add required permissions to calling workflow
- Ensure repository has access to reusable workflows

## Contributing

When modifying reusable workflows:

1. Update version tags for breaking changes
2. Test across all supported platforms
3. Update this documentation
4. Ensure backward compatibility where possible

## Support

For issues or questions:
- Check existing GitHub issues
- Review workflow run logs for error details
- Contact the OpenSSL tools team