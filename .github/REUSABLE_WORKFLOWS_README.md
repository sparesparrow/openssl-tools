# Reusable CI/CD Workflows for OpenSSL

This directory contains reusable GitHub Actions workflows and composite actions designed for building, testing, and publishing OpenSSL packages with comprehensive quality gates and security scanning.

## Overview

The reusable workflows provide:
- **Build OpenSSL**: Compiles OpenSSL with configurable options (version, platform, FIPS mode)
- **Integration Testing**: Matrixed validation across multiple OSes and configurations
- **Cloudsmith Publishing**: OIDC-authenticated package publishing with metadata
- **Quality Gates**: SBOM generation, vulnerability scanning, and security validation

## Workflows

### 1. Build OpenSSL (`build-openssl.yml`)

Compiles OpenSSL with configurable version, platform, and FIPS support.

**Inputs:**
- `version` (required): OpenSSL version to build
- `platform` (required): Target platform (ubuntu-latest, windows-latest, macos-latest)
- `fips` (optional): Enable FIPS mode (default: false)
- `build-type` (optional): Build type - Debug, Release, RelWithDebInfo (default: Release)
- `enable-tests` (optional): Run tests during build (default: true)
- `conan-profile` (optional): Conan profile to use (default: default)
- `cloudsmith-org` (optional): Cloudsmith organization (default: openssl)
- `cloudsmith-repo` (optional): Cloudsmith repository (default: openssl-packages)

**Outputs:**
- `artifact-url`: URL of the uploaded artifact
- `artifact-name`: Name of the generated artifact
- `build-hash`: Build hash for tracking

**Secrets:**
- `CLOUDSMITH_API_KEY` (optional): For publishing to Cloudsmith
- `ARTIFACTORY_API_KEY` (optional): For publishing to Artifactory

**Example Usage:**
```yaml
jobs:
  build:
    uses: ./.github/workflows/build-openssl.yml@v1
    with:
      version: '3.1.4'
      platform: 'ubuntu-latest'
      fips: true
      build-type: 'Release'
      conan-profile: 'ci-linux-gcc'
    secrets:
      CLOUDSMITH_API_KEY: ${{ secrets.CLOUDSMITH_API_KEY }}
```

### 2. Integration Testing (`test-integration.yml`)

Runs comprehensive integration tests across multiple platforms and configurations.

**Inputs:**
- `openssl-version` (required): OpenSSL version to test
- `test-matrix` (optional): JSON string defining test matrix
- `test-suites` (optional): Comma-separated test suites (unit, integration, performance, security)
- `fips-mode` (optional): Enable FIPS mode testing (default: false)
- `conan-profiles` (optional): Comma-separated Conan profiles to test
- `test-timeout` (optional): Test timeout in minutes (default: 30)
- `parallel-jobs` (optional): Number of parallel test jobs (default: 4)

**Outputs:**
- `test-results-url`: URL to test results
- `test-summary`: Test summary JSON
- `coverage-report`: Coverage report URL

**Secrets:**
- `TEST_DATABASE_URL` (optional): Test database connection string
- `CLOUDSMITH_API_KEY` (optional): For downloading test artifacts

**Example Usage:**
```yaml
jobs:
  test:
    uses: ./.github/workflows/test-integration.yml@v1
    with:
      openssl-version: '3.1.4'
      test-suites: 'unit,integration,performance,security'
      fips-mode: true
      conan-profiles: 'ci-linux-gcc,ci-linux-clang,ci-windows-msvc'
      test-timeout: 45
      parallel-jobs: 8
    secrets:
      CLOUDSMITH_API_KEY: ${{ secrets.CLOUDSMITH_API_KEY }}
```

### 3. Cloudsmith Publishing (`publish-cloudsmith.yml`)

Publishes packages to Cloudsmith with OIDC authentication and comprehensive metadata.

**Inputs:**
- `package-name` (required): Name of the package
- `package-version` (required): Version of the package
- `package-format` (required): Package format (raw, conan, maven, npm, etc.)
- `repository` (required): Cloudsmith repository name
- `organization` (required): Cloudsmith organization name
- `artifact-path` (required): Path to the artifact to publish
- `distribution` (optional): Distribution name for raw packages (default: any)
- `architecture` (optional): Architecture for raw packages (default: any)
- `tags` (optional): Comma-separated list of tags
- `description` (optional): Package description
- `license` (optional): Package license (default: MIT)
- `homepage` (optional): Package homepage URL
- `documentation-url` (optional): Documentation URL
- `source-url` (optional): Source code URL
- `changelog` (optional): Changelog content
- `publish-now` (optional): Publish immediately vs. stage for review (default: true)
- `replace-existing` (optional): Replace existing package version (default: false)

**Outputs:**
- `package-url`: URL of the published package
- `package-id`: Cloudsmith package ID
- `publish-status`: Publishing status

**Secrets:**
- `CLOUDSMITH_API_KEY` (required): Cloudsmith API key

**Example Usage:**
```yaml
jobs:
  publish:
    uses: ./.github/workflows/publish-cloudsmith.yml@v1
    with:
      package-name: 'openssl-3.1.4'
      package-version: '3.1.4-abc123'
      package-format: 'raw'
      repository: 'openssl-packages'
      organization: 'openssl'
      artifact-path: './artifacts'
      distribution: 'ubuntu-latest'
      architecture: 'x64'
      tags: 'openssl,3.1.4,ubuntu-latest,fips'
      description: 'OpenSSL 3.1.4 build for Ubuntu'
      license: 'Apache-2.0'
      homepage: 'https://www.openssl.org/'
      source-url: 'https://github.com/openssl/openssl'
      publish-now: true
    secrets:
      CLOUDSMITH_API_KEY: ${{ secrets.CLOUDSMITH_API_KEY }}
```

## Composite Actions

### Cloudsmith Publish Action (`actions/cloudsmith-publish/action.yml`)

A composite action for publishing packages to Cloudsmith with OIDC authentication.

**Key Features:**
- Support for multiple package formats (raw, conan, maven, npm, pypi, etc.)
- Comprehensive metadata support
- Dry-run capability
- Input validation
- Detailed logging and error handling

**Example Usage:**
```yaml
- name: Publish to Cloudsmith
  uses: ./.github/actions/cloudsmith-publish
  with:
    api-key: ${{ secrets.CLOUDSMITH_API_KEY }}
    organization: 'openssl'
    repository: 'openssl-packages'
    package-format: 'raw'
    artifact-path: './artifacts'
    package-name: 'openssl-3.1.4'
    package-version: '3.1.4-abc123'
    distribution: 'ubuntu-latest'
    architecture: 'x64'
    tags: 'openssl,3.1.4,ubuntu-latest'
    description: 'OpenSSL 3.1.4 build for Ubuntu'
    publish-now: 'true'
```

## Quality Gates

All workflows include comprehensive quality gates:

### Security Scanning
- **Trivy**: Vulnerability scanning with configurable severity levels
- **SBOM Generation**: Software Bill of Materials using Anchore Syft
- **High-severity vulnerability blocking**: Builds fail on CRITICAL/HIGH vulnerabilities

### Build Validation
- **Input validation**: Comprehensive input parameter validation
- **Artifact verification**: Ensures artifacts are properly generated
- **Metadata generation**: Rich metadata for tracking and compliance

### Testing
- **Matrix testing**: Cross-platform validation
- **Multiple test suites**: Unit, integration, performance, security tests
- **FIPS validation**: Specialized FIPS mode testing
- **Coverage reporting**: Code coverage analysis and reporting

## Complete Example

Here's a complete example that demonstrates using all workflows together:

```yaml
name: Complete OpenSSL Build Pipeline

on:
  workflow_dispatch:
    inputs:
      openssl-version:
        description: 'OpenSSL version to build'
        required: true
        type: string
        default: '3.1.4'
      enable-fips:
        description: 'Enable FIPS mode'
        required: false
        type: boolean
        default: false

jobs:
  # Build OpenSSL
  build:
    uses: ./.github/workflows/build-openssl.yml@v1
    with:
      version: ${{ inputs.openssl-version }}
      platform: ubuntu-latest
      fips: ${{ inputs.enable-fips }}
      build-type: 'Release'
      conan-profile: 'ci-linux-gcc'
    secrets:
      CLOUDSMITH_API_KEY: ${{ secrets.CLOUDSMITH_API_KEY }}

  # Run integration tests
  test:
    needs: build
    uses: ./.github/workflows/test-integration.yml@v1
    with:
      openssl-version: ${{ inputs.openssl-version }}
      test-suites: 'unit,integration,performance,security'
      fips-mode: ${{ inputs.enable-fips }}
      conan-profiles: 'ci-linux-gcc,ci-linux-clang,ci-windows-msvc'
    secrets:
      CLOUDSMITH_API_KEY: ${{ secrets.CLOUDSMITH_API_KEY }}

  # Publish to Cloudsmith
  publish:
    needs: [build, test]
    if: success()
    uses: ./.github/workflows/publish-cloudsmith.yml@v1
    with:
      package-name: 'openssl-${{ inputs.openssl-version }}'
      package-version: '${{ inputs.openssl-version }}-${{ needs.build.outputs.build-hash }}'
      package-format: 'raw'
      repository: 'openssl-packages'
      organization: 'openssl'
      artifact-path: './artifacts'
      distribution: 'ubuntu-latest'
      architecture: 'x64'
      tags: 'openssl,${{ inputs.openssl-version }},ubuntu-latest,${{ inputs.enable-fips && "fips" || "" }}'
      description: 'OpenSSL ${{ inputs.openssl-version }} build for Ubuntu'
      license: 'Apache-2.0'
      homepage: 'https://www.openssl.org/'
      source-url: 'https://github.com/openssl/openssl'
      publish-now: true
    secrets:
      CLOUDSMITH_API_KEY: ${{ secrets.CLOUDSMITH_API_KEY }}
```

## Versioning

All workflows are tagged with `@v1` for versioned calls. This ensures:
- Stable API across different repositories
- Backward compatibility
- Clear versioning strategy

## Security Considerations

- **OIDC Authentication**: Uses GitHub OIDC for secure Cloudsmith authentication
- **Secret Management**: All sensitive data passed through GitHub secrets
- **Vulnerability Scanning**: Comprehensive security scanning with blocking on high-severity issues
- **SBOM Generation**: Complete software bill of materials for compliance

## Troubleshooting

### Common Issues

1. **Build Failures**: Check Conan profiles and platform compatibility
2. **Test Failures**: Verify test database connectivity and artifact availability
3. **Publishing Failures**: Ensure Cloudsmith API key has proper permissions
4. **Vulnerability Blocking**: Review Trivy scan results and update dependencies

### Debug Mode

Enable debug logging by setting the `ACTIONS_STEP_DEBUG` secret to `true` in your repository settings.

## Contributing

When modifying these workflows:
1. Update version tags appropriately
2. Maintain backward compatibility
3. Update this documentation
4. Test changes thoroughly
5. Consider impact on dependent repositories

## Support

For issues or questions:
- Check GitHub Actions logs for detailed error messages
- Review workflow inputs and outputs
- Verify secret permissions and values
- Consult Cloudsmith documentation for publishing issues