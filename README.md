# OpenSSL Tools - Conan 2.x Python_requires & Extensions

Comprehensive Conan 2.x tooling for OpenSSL build orchestration, including custom commands and deployers.

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/sparesparrow/openssl-tools.git
cd openssl-tools

# Install extensions
./install-extensions.sh
```

This installs:
- Custom commands: `openssl:build`, `openssl:graph`
- Enhanced deployer: `full_deploy_enhanced`
- Python_requires: `openssl-tools/1.2.0`

## Usage

#### Simplified Build

```bash
# Basic build
conan openssl:build

# With FIPS
conan openssl:build --fips --profile=linux-gcc11-fips

# Custom output folder
conan openssl:build --deployer-folder=./my-artifacts
```

#### Dependency Analysis

```bash
# Human-readable output
conan openssl:graph

# JSON output
conan openssl:graph --json > dependencies.json
```

#### Using as python_requires

```python
# your_project/conanfile.py
from conan import ConanFile

class YourApp(ConanFile):
    name = "your-app"
    python_requires = "openssl-tools/1.2.0"
    
    def requirements(self):
        self.requires("openssl/3.6.0")
    
    def build(self):
        # Use build orchestration from python_requires
        python_req = self.python_requires["openssl-tools"]
        python_req.module.build_openssl(self)
```

## Architecture

```
openssl-tools/
├── conanfile.py                      # Python_requires package
├── extensions/
│   ├── commands/
│   │   └── openssl/
│   │       ├── __init__.py
│   │       ├── cmd_build.py          # conan openssl:build
│   │       └── cmd_graph.py          # conan openssl:graph
│   ├── deployers/
│   │   └── full_deploy_enhanced.py   # Enhanced deployer with SBOM
│   └── graph/
│       └── analyzer.py               # Graph analysis utilities
├── install-extensions.sh             # Installation script
└── test_package/
    └── conanfile.py
```

## Features

### Custom Commands

#### `conan openssl:build`
- Simplified OpenSSL build orchestration
- FIPS mode support via `--fips` flag
- Automatic deployer integration
- SBOM generation included

#### `conan openssl:graph`
- Dependency graph analysis
- FIPS detection
- JSON export support

### Enhanced Deployer

`full_deploy_enhanced` provides:
- Standard `full_deploy` functionality
- Automatic SBOM generation (CycloneDX format)
- FIPS artifact collection
- Dependency metadata

### Python_requires

Reusable build logic for:
- Platform-specific configuration
- Ninja/Make detection
- FIPS module setup
- Cross-compilation support

## Uninstallation

```bash
# Remove extensions
rm -rf ~/.conan2/extensions/commands/openssl
rm -f ~/.conan2/extensions/deployers/full_deploy_enhanced.py
rm -rf ~/.conan2/extensions/graph

# Remove python_requires
conan remove "openssl-tools/*" -c
```

## Development

### Testing Extensions Locally

```bash
# Install in editable mode (changes reflect immediately)
conan editable add . openssl-tools/1.2.0

# Test commands
conan openssl:build --help

# Remove editable
conan editable remove openssl-tools/1.2.0
```

### Running Tests

```bash
# Unit tests
python -m pytest test/

# Integration tests
./test_package/test.sh
```

## Troubleshooting

### Command not found: `conan openssl:build`

Extensions not installed. Run:
```bash
./install-extensions.sh
```

### ImportError in graph analyzer

Graph utilities not found. Reinstall:
```bash
./install-extensions.sh
```

### FIPS self-test failed

Check module hash:
```bash
openssl dgst -sha256 -provider fips /path/to/fips.so
```

Compare with expected hash in `openssl-fips-policy/fips/expected_module_hash.txt`.

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for development workflow.

## License

Apache-2.0 (same as OpenSSL)

## Reusable GitHub Actions Workflows

This repository provides comprehensive reusable GitHub Actions workflows for OpenSSL development, including build, test, security scanning, and publishing capabilities.

### Core Reusable Workflows

| Workflow | Description | Key Features |
|----------|-------------|--------------|
| `build-openssl.yml` | OpenSSL build with version/platform/FIPS support | Multi-platform builds, SBOM generation, artifact uploads |
| `test-integration.yml` | Matrixed integration testing across OSes | Cross-platform testing, FIPS validation, flaky test management |
| `publish-cloudsmith.yml` | OIDC-authenticated Cloudsmith publishing | Conan & raw package formats, OIDC/API key auth |
| `quality-gates.yml` | Comprehensive security scanning & SBOM generation | Syft SBOM, Trivy scans, SARIF uploads |

### Composite Actions

| Action | Description | Key Features |
|--------|-------------|--------------|
| `cloudsmith-publish/` | OIDC-authenticated package publishing | Multi-format support, verification, timeout handling |

### Legacy Workflows

| Workflow | Description | Status |
|----------|-------------|--------|
| `reusable-conan-build.yml` | Legacy Conan build workflow | Deprecated - use `build-openssl.yml` |
| `reusable-security-scan.yml` | Legacy security scanning | Deprecated - use `quality-gates.yml` |
| `reusable-fips-validation.yml` | FIPS 140-3 compliance validation | Available |

## Usage Examples

### Complete OpenSSL Build Pipeline

```yaml
# .github/workflows/openssl-pipeline.yml
name: OpenSSL Build Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    name: 🔨 Build OpenSSL
    uses: ./.github/workflows/build-openssl.yml
    with:
      version: '3.6.0'
      platform: 'ubuntu-latest'
      fips: true
      shared: false
      enable-sbom: true
    secrets:
      CLOUDSMITH_API_KEY: ${{ secrets.CLOUDSMITH_API_KEY }}

  test:
    name: 🧪 Integration Tests
    uses: ./.github/workflows/test-integration.yml
    needs: build
    with:
      test-matrix: |
        {
          "os": ["ubuntu-latest", "windows-latest", "macos-latest"],
          "profiles": ["default"],
          "versions": ["3.6.0"]
        }
      enable-fips-tests: true
      enable-cross-platform: true

  quality-gates:
    name: 🛡️ Quality Gates
    uses: ./.github/workflows/quality-gates.yml
    needs: build
    with:
      artifact-path: ${{ needs.build.outputs.build-path }}
      artifact-name: ${{ needs.build.outputs.artifact-name }}
      enable-sbom: true
      enable-trivy: true
      fail-on-severity: 'HIGH,CRITICAL'

  publish:
    name: 📦 Publish to Cloudsmith
    uses: ./.github/workflows/publish-cloudsmith.yml
    needs: [build, test, quality-gates]
    if: github.ref == 'refs/heads/main' && needs.quality-gates.outputs.scan-passed == 'true'
    with:
      package-reference: 'openssl/3.6.0'
      artifact-path: ${{ needs.build.outputs.build-path }}
      publish-raw-artifacts: true
      tags: 'openssl,conan,ci,production'
    secrets:
      CLOUDSMITH_API_KEY: ${{ secrets.CLOUDSMITH_API_KEY }}
```

### Build OpenSSL Workflow

```yaml
# .github/workflows/build.yml
name: Build OpenSSL

on: [push, pull_request]

jobs:
  build:
    uses: ./.github/workflows/build-openssl.yml
    with:
      version: '3.6.0'
      platform: 'ubuntu-latest'
      fips: true
      shared: false
      profile: 'linux-gcc11-fips'
      enable-sbom: true
      enable-tests: true
    secrets:
      CLOUDSMITH_API_KEY: ${{ secrets.CLOUDSMITH_API_KEY }}
```

### Integration Testing Workflow

```yaml
# .github/workflows/test.yml
name: Integration Tests

on: [push, pull_request]

jobs:
  test:
    uses: ./.github/workflows/test-integration.yml
    with:
      test-matrix: |
        {
          "os": ["ubuntu-latest", "windows-latest", "macos-latest"],
          "profiles": ["default", "linux-gcc11-fips"],
          "versions": ["3.6.0"]
        }
      test-suite: 'integration'
      enable-fips-tests: true
      enable-cross-platform: true
      max-retries: 2
      timeout-minutes: 60
```

### Security Scanning Workflow

```yaml
# .github/workflows/security.yml
name: Security Scan

on: [push, pull_request]

jobs:
  security:
    uses: ./.github/workflows/quality-gates.yml
    with:
      artifact-path: './artifacts'
      artifact-name: 'openssl-build'
      enable-sbom: true
      enable-trivy: true
      fail-on-severity: 'HIGH,CRITICAL'
      upload-sarif: true
      upload-artifacts: true
```

### Cloudsmith Publishing Workflow

```yaml
# .github/workflows/publish.yml
name: Publish to Cloudsmith

on:
  push:
    tags: ['v*']

jobs:
  publish:
    uses: ./.github/workflows/publish-cloudsmith.yml
    with:
      package-reference: 'openssl/3.6.0'
      artifact-path: './artifacts'
      package-format: 'conan'
      publish-raw-artifacts: true
      tags: 'openssl,conan,release'
      description: 'OpenSSL 3.6.0 release package'
    secrets:
      CLOUDSMITH_API_KEY: ${{ secrets.CLOUDSMITH_API_KEY }}
```

### Using Composite Actions

```yaml
# .github/workflows/custom-publish.yml
name: Custom Publish

on: [workflow_dispatch]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Publish with OIDC
        uses: ./.github/actions/cloudsmith-publish
        with:
          package-reference: 'openssl/3.6.0'
          package-format: 'conan'
          use-oidc: 'true'
          oidc-token: ${{ secrets.OIDC_TOKEN }}
          verify-upload: 'true'
```

## Workflow Input Schemas

### build-openssl.yml

| Input | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `version` | string | ✅ | - | OpenSSL version to build (e.g., 3.6.0) |
| `platform` | string | ✅ | - | Target platform (ubuntu-latest, windows-latest, macos-latest) |
| `fips` | boolean | ❌ | false | Enable FIPS 140-3 mode |
| `shared` | boolean | ❌ | false | Build shared libraries |
| `profile` | string | ❌ | 'default' | Conan profile to use |
| `conan-options` | string | ❌ | '' | Additional Conan options |
| `enable-tests` | boolean | ❌ | true | Enable unit tests during build |
| `enable-sbom` | boolean | ❌ | true | Generate SBOM during build |

### test-integration.yml

| Input | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `test-matrix` | string | ❌ | JSON matrix | JSON string defining test matrix (OS, profiles, versions) |
| `test-suite` | string | ❌ | 'integration' | Test suite to run (unit, integration, fuzz, all) |
| `max-retries` | number | ❌ | 2 | Maximum number of retries for flaky tests |
| `timeout-minutes` | number | ❌ | 60 | Timeout for test execution in minutes |
| `enable-fips-tests` | boolean | ❌ | true | Enable FIPS-specific tests |
| `enable-cross-platform` | boolean | ❌ | true | Enable cross-platform compatibility tests |

### publish-cloudsmith.yml

| Input | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `package-reference` | string | ✅ | - | Package reference to publish (e.g., openssl/3.6.0) |
| `repository` | string | ❌ | 'openssl-conan' | Cloudsmith repository name |
| `owner` | string | ❌ | 'sparesparrow-conan' | Cloudsmith repository owner |
| `package-format` | string | ❌ | 'conan' | Package format (conan, raw, generic) |
| `distribution` | string | ❌ | 'main' | Distribution name for the package |
| `tags` | string | ❌ | 'openssl,conan,ci' | Comma-separated list of tags |
| `publish-raw-artifacts` | boolean | ❌ | true | Publish raw build artifacts in addition to Conan package |

### quality-gates.yml

| Input | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `artifact-path` | string | ✅ | - | Path to artifacts to scan |
| `artifact-name` | string | ❌ | 'unknown' | Name of the artifact being scanned |
| `scan-type` | string | ❌ | 'fs' | Type of scan to perform (fs, image, repo) |
| `fail-on-severity` | string | ❌ | 'HIGH,CRITICAL' | Severity levels to fail on |
| `enable-sbom` | boolean | ❌ | true | Generate SBOM for the artifacts |
| `enable-trivy` | boolean | ❌ | true | Run Trivy vulnerability scan |
| `enable-syft` | boolean | ❌ | true | Use Syft for SBOM generation |
| `sbom-format` | string | ❌ | 'cyclonedx-json' | SBOM format (cyclonedx-json, spdx-json, table) |

## Workflow Outputs

### build-openssl.yml

| Output | Description |
|--------|-------------|
| `artifact-url` | URL of uploaded artifact |
| `artifact-name` | Name of the build artifact |
| `build-path` | Path to build artifacts |
| `sbom-generated` | Whether SBOM was generated |

### test-integration.yml

| Output | Description |
|--------|-------------|
| `test-results` | Overall test results summary |
| `flaky-detected` | Whether flaky tests were detected |
| `total-tests` | Total number of test runs |
| `passed-tests` | Number of passed test runs |
| `failed-tests` | Number of failed test runs |

### publish-cloudsmith.yml

| Output | Description |
|--------|-------------|
| `package-url` | URL of the published package |
| `package-id` | ID of the published package |
| `upload-success` | Whether the upload was successful |

### quality-gates.yml

| Output | Description |
|--------|-------------|
| `sbom-generated` | Whether SBOM was successfully generated |
| `vulnerabilities-found` | Number of vulnerabilities found |
| `scan-passed` | Whether quality gates passed |
| `high-severity-count` | Number of high severity vulnerabilities |
| `critical-severity-count` | Number of critical severity vulnerabilities |

## Testing Workflows

Use the test workflow to validate all reusable workflows:

```bash
# Test all workflows
gh workflow run test-reusable-workflows.yml -f test-workflow=all

# Test specific workflow
gh workflow run test-reusable-workflows.yml -f test-workflow=build-openssl
```

## Workflow Integration

For complete CI/CD integration, see:
- [Track A Security Pipeline Documentation](../openssl-devenv/TRACK-A-SECURITY-PIPELINE.md)
- [Verification Scripts Documentation](../openssl-devenv/docs/verification.md)

### Workflow Integration

For complete CI/CD integration, see:
- [Track A Security Pipeline Documentation](../openssl-devenv/TRACK-A-SECURITY-PIPELINE.md)
- [Verification Scripts Documentation](../openssl-devenv/docs/verification.md)

## Related Repositories

- [openssl-conan-base](https://github.com/sparesparrow/openssl-conan-base) - Profiles and production CI/CD
- [openssl](https://github.com/sparesparrow/openssl) - Minimal fork for testing
- [openssl-fips-policy](https://github.com/sparesparrow/openssl-fips-policy) - FIPS configuration
- [openssl-devenv](https://github.com/sparesparrow/openssl-devenv) - Developer onboarding