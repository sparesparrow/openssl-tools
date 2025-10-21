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

## Conan Extensions Integration

### Graph API Analyzer (`tools/graph_analyzer.py`)
Analyzes Conan dependency graphs for conflicts and outdated versions:

```bash
python tools/graph_analyzer.py path/to/conanfile.py --fail-on-conflict
```

**Features:**
- Dependency tree analysis
- Conflict detection
- Version compatibility checking
- Exit codes for CI integration

### Deploy Consumer (`tools/deploy_dev.py`)
Downloads and activates full_deploy bundles without requiring Conan:

```bash
python tools/deploy_dev.py --url <release_url> --dest .deps
```

**Features:**
- Downloads from GitHub Releases or Cloudsmith
- Extracts to configurable directory
- Sets up environment variables
- No Conan dependency required

## Development Workflow

### With Conan (Standard)
```bash
# Install dependencies
conan install ../openssl-conan-base --build=missing

# Run analysis
python tools/graph_analyzer.py ../openssl/conanfile.py
```

### With Deploy Bundle (No Conan)
```bash
# Download and activate bundle
python tools/deploy_dev.py --url https://github.com/.../releases/download/.../full-deploy-linux-x86_64-Release.zip

# Run analysis
python tools/graph_analyzer.py ../openssl/conanfile.py
```

## Integration

This repository integrates with:
- **openssl-conan-base**: For dependency packages and full_deploy bundles
- **openssl**: For core OpenSSL library testing
- **openssl-fips-policy**: For FIPS compliance validation
- **openssl-devenv**: For workspace orchestration

## Workflow Integration

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

This repository provides reusable GitHub Actions workflows for OpenSSL development:

### Available Workflows

| Workflow | Description | Inputs |
|----------|-------------|--------|
| `reusable-conan-build.yml` | Build & test Conan packages | profile, shared, fips, deploy, upload-to-cloudsmith, package-reference |
| `reusable-security-scan.yml` | SBOM + Trivy + CodeQL scanning | artifact-name, language, sbom-format, trivy-severity, upload-sarif |
| `reusable-fips-validation.yml` | FIPS 140-3 compliance validation | openssl-version, fips-module-version, expected-hash |

### Usage Examples

#### Conan Build Workflow

```yaml
# .github/workflows/build.yml
name: Build OpenSSL Package

on: [push, pull_request]

jobs:
  build:
    uses: sparesparrow/openssl-tools/.github/workflows/reusable-conan-build.yml@v1
    with:
      package-reference: 'openssl/3.6.0'
      profile: 'linux-gcc11-fips'
      fips: true
      deploy: true
      upload-to-cloudsmith: true
    secrets:
      CLOUDSMITH_API_KEY: ${{ secrets.CLOUDSMITH_API_KEY }}
```

#### Security Scanning Workflow

```yaml
# .github/workflows/security.yml
name: Security Scan

on: [push, pull_request]

jobs:
  build:
    uses: sparesparrow/openssl-tools/.github/workflows/reusable-conan-build.yml@v1
    with:
      package-reference: 'openssl/3.6.0'
      deploy: true
  
  security:
    needs: build
    uses: sparesparrow/openssl-tools/.github/workflows/reusable-security-scan.yml@v1
    with:
      artifact-name: 'conan-artifacts-linux-gcc11-fips'
      language: 'cpp'
      upload-sarif: true
```

#### FIPS Validation Workflow

```yaml
# .github/workflows/fips.yml
name: FIPS Validation

on: [push, pull_request]

jobs:
  fips:
    uses: sparesparrow/openssl-tools/.github/workflows/reusable-fips-validation.yml@v1
    with:
      openssl-version: '3.6.0'
      fips-module-version: '3.0.9'
      expected-hash: ${{ vars.FIPS_MODULE_HASH }}
```

### Workflow Integration

For complete CI/CD integration, see:
- [Track A Security Pipeline Documentation](../openssl-devenv/TRACK-A-SECURITY-PIPELINE.md)
- [Verification Scripts Documentation](../openssl-devenv/docs/verification.md)

## Related Repositories

- [openssl-conan-base](https://github.com/sparesparrow/openssl-conan-base) - Profiles and production CI/CD
- [openssl](https://github.com/sparesparrow/openssl) - Minimal fork for testing
- [openssl-fips-policy](https://github.com/sparesparrow/openssl-fips-policy) - FIPS configuration
- [openssl-devenv](https://github.com/sparesparrow/openssl-devenv) - Developer onboarding