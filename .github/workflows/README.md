# Reusable CI/CD Workflows

This directory contains reusable GitHub Actions workflows for OpenSSL builds, testing, and publishing. These workflows are designed to be called from other repositories and provide consistent, standardized CI/CD processes.

## Available Workflows

### 1. Build OpenSSL (`build-openssl.yml`)

A reusable workflow for building OpenSSL with support for multiple platforms, FIPS mode, and quality gates.

#### Inputs

| Input | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `version` | string | ✅ | - | OpenSSL version to build |
| `platform` | string | ✅ | - | Target platform (ubuntu-latest, windows-latest, macos-latest) |
| `fips` | boolean | ❌ | false | Enable FIPS mode |
| `build_type` | string | ❌ | 'Release' | Build type (Release, Debug, RelWithDebInfo) |
| `conan_profile` | string | ❌ | 'default' | Conan profile to use for build |
| `upload_artifacts` | boolean | ❌ | true | Upload build artifacts |

#### Outputs

| Output | Description |
|--------|-------------|
| `artifact-url` | URL of uploaded artifact |
| `build-success` | Build success status |
| `sbom-url` | URL of generated SBOM |

#### Secrets

| Secret | Required | Description |
|--------|----------|-------------|
| `CLOUDSMITH_API_KEY` | ❌ | Cloudsmith API key for publishing |
| `CLOUDSMITH_REPOSITORY` | ❌ | Cloudsmith repository name |

#### Usage Example

```yaml
jobs:
  build:
    uses: ./.github/workflows/build-openssl.yml@v1
    with:
      version: '3.1.4'
      platform: 'ubuntu-latest'
      fips: true
      build_type: 'Release'
    secrets:
      CLOUDSMITH_API_KEY: ${{ secrets.CLOUDSMITH_API_KEY }}
      CLOUDSMITH_REPOSITORY: 'my-repo'
```

### 2. Integration Tests (`test-integration.yml`)

A reusable workflow for running comprehensive integration tests across multiple platforms and configurations.

#### Inputs

| Input | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `openssl_version` | string | ✅ | - | OpenSSL version to test |
| `test_matrix` | string | ❌ | See default | JSON string defining test matrix |
| `test_suite` | string | ❌ | 'integration' | Test suite to run (unit, integration, fuzz, performance) |
| `fips_mode` | boolean | ❌ | false | Enable FIPS mode testing |
| `conan_profile` | string | ❌ | 'default' | Conan profile to use for testing |
| `upload_results` | boolean | ❌ | true | Upload test results as artifacts |

#### Outputs

| Output | Description |
|--------|-------------|
| `test-results-url` | URL of uploaded test results |
| `test-success` | Overall test success status |
| `coverage-url` | URL of coverage report |

#### Usage Example

```yaml
jobs:
  test:
    uses: ./.github/workflows/test-integration.yml@v1
    with:
      openssl_version: '3.1.4'
      test_matrix: '{"os": ["ubuntu-latest", "windows-latest"], "compiler": ["gcc", "clang"], "arch": ["x64"]}'
      test_suite: 'all'
      fips_mode: true
```

### 3. Publish to Cloudsmith (`publish-cloudsmith.yml`)

A reusable workflow for publishing packages to Cloudsmith with OIDC authentication and support for multiple package types.

#### Inputs

| Input | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `package_name` | string | ✅ | - | Name of the package to publish |
| `package_version` | string | ✅ | - | Version of the package |
| `package_path` | string | ✅ | - | Path to the package files |
| `package_type` | string | ✅ | - | Type of package (raw, conan, maven, npm, etc.) |
| `repository` | string | ✅ | - | Cloudsmith repository name |
| `distribution` | string | ❌ | 'any' | Distribution name (e.g., ubuntu, centos, debian) |
| `component` | string | ❌ | 'main' | Component name (e.g., main, contrib) |
| `architecture` | string | ❌ | 'any' | Package architecture |
| `tags` | string | ❌ | '' | Comma-separated list of tags |
| `description` | string | ❌ | '' | Package description |
| `publish` | boolean | ❌ | true | Whether to actually publish (vs just upload) |

#### Outputs

| Output | Description |
|--------|-------------|
| `package-url` | URL of the published package |
| `upload-success` | Upload success status |
| `package-id` | Cloudsmith package ID |

#### Secrets

| Secret | Required | Description |
|--------|----------|-------------|
| `CLOUDSMITH_API_KEY` | ✅ | Cloudsmith API key for authentication |
| `CLOUDSMITH_NAMESPACE` | ✅ | Cloudsmith namespace/organization |

#### Usage Example

```yaml
jobs:
  publish:
    uses: ./.github/workflows/publish-cloudsmith.yml@v1
    with:
      package_name: 'openssl'
      package_version: '3.1.4'
      package_path: './artifacts'
      package_type: 'raw'
      repository: 'my-repo'
      description: 'OpenSSL 3.1.4 build'
      tags: 'openssl,ssl,tls'
    secrets:
      CLOUDSMITH_API_KEY: ${{ secrets.CLOUDSMITH_API_KEY }}
      CLOUDSMITH_NAMESPACE: ${{ secrets.CLOUDSMITH_NAMESPACE }}
```

## Composite Actions

### Cloudsmith Publish Action (`cloudsmith-publish`)

A composite action for publishing packages to Cloudsmith with OIDC authentication and support for multiple package types.

#### Inputs

| Input | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `api-key` | string | ✅ | - | Cloudsmith API key for authentication |
| `namespace` | string | ✅ | - | Cloudsmith namespace/organization |
| `repository` | string | ✅ | - | Cloudsmith repository name |
| `package-name` | string | ✅ | - | Name of the package to publish |
| `package-version` | string | ✅ | - | Version of the package |
| `package-path` | string | ✅ | - | Path to the package files |
| `package-type` | string | ✅ | - | Type of package (raw, conan, maven, npm, etc.) |
| `distribution` | string | ❌ | 'any' | Distribution name |
| `component` | string | ❌ | 'main' | Component name |
| `architecture` | string | ❌ | 'any' | Package architecture |
| `tags` | string | ❌ | '' | Comma-separated list of tags |
| `description` | string | ❌ | '' | Package description |
| `publish` | string | ❌ | 'true' | Whether to actually publish |
| `conan-username` | string | ❌ | '' | Conan username (for Conan packages) |
| `conan-channel` | string | ❌ | 'stable' | Conan channel (for Conan packages) |

#### Usage Example

```yaml
steps:
  - name: Publish to Cloudsmith
    uses: ./.github/actions/cloudsmith-publish@v1
    with:
      api-key: ${{ secrets.CLOUDSMITH_API_KEY }}
      namespace: ${{ secrets.CLOUDSMITH_NAMESPACE }}
      repository: 'my-repo'
      package-name: 'openssl'
      package-version: '3.1.4'
      package-path: './artifacts'
      package-type: 'raw'
      description: 'OpenSSL 3.1.4 build'
      tags: 'openssl,ssl,tls'
```

## Quality Gates

All workflows include built-in quality gates:

### Security Scanning
- **Trivy**: Scans for vulnerabilities in built binaries
- **SBOM Generation**: Generates Software Bill of Materials using Syft
- **Fails on high-severity vulnerabilities**: Workflows will fail if critical or high-severity vulnerabilities are found

### Code Quality
- **Test Coverage**: Generates coverage reports for test suites
- **Build Validation**: Ensures builds complete successfully
- **Artifact Verification**: Validates uploaded artifacts

## Testing the Workflows

A test workflow (`test-reusable-workflows.yml`) is provided to validate all reusable workflows:

```yaml
on:
  workflow_dispatch:
    inputs:
      openssl_version:
        description: 'OpenSSL version to test'
        required: true
        type: string
        default: '3.1.4'
      test_platform:
        description: 'Platform to test on'
        required: true
        type: choice
        options:
          - ubuntu-latest
          - windows-latest
          - macos-latest
        default: 'ubuntu-latest'
      enable_fips:
        description: 'Enable FIPS mode'
        required: false
        type: boolean
        default: false
      test_publish:
        description: 'Test publishing to Cloudsmith'
        required: false
        type: boolean
        default: false
```

## Versioning

Workflows are versioned using Git tags. Use `@v1` to reference the latest version:

```yaml
uses: ./.github/workflows/build-openssl.yml@v1
```

## Dependencies

### Required Tools
- **Conan**: Package manager for C/C++
- **Syft**: SBOM generation tool
- **Trivy**: Security vulnerability scanner
- **Cloudsmith CLI**: Package publishing tool

### Required Secrets
- `CLOUDSMITH_API_KEY`: Cloudsmith API key
- `CLOUDSMITH_NAMESPACE`: Cloudsmith namespace/organization
- `CLOUDSMITH_REPOSITORY`: Cloudsmith repository name (optional)

## Contributing

When modifying these workflows:

1. Update version numbers in workflow files
2. Update this documentation
3. Test changes using the test workflow
4. Create a new Git tag for the version
5. Update callers to use the new version

## Support

For issues or questions about these workflows:

1. Check the workflow logs for detailed error messages
2. Verify all required inputs and secrets are provided
3. Ensure the target platform supports the requested configuration
4. Check Cloudsmith repository permissions and API key validity