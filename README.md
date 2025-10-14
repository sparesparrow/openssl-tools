# OpenSSL Tools

Build tools, automation scripts, and infrastructure components for the modernized OpenSSL CI/CD pipeline.

## Quick Start

### Installation

```bash
pip install -e .
```

### Basic Usage

```bash
# Set up development environment
openssl-env --dev

# Run tests
openssl-test

# Build OpenSSL
openssl-build

# Validate setup
openssl-validate
```

## Architecture

This repository implements a **two-repository CI/CD architecture**:

- **[OpenSSL Repository](https://github.com/sparesparrow/openssl)**: Source code and fast validation
- **[OpenSSL-Tools Repository](https://github.com/sparesparrow/openssl-tools)**: Build infrastructure and comprehensive CI/CD

## Configuration

### Cross-Repository Communication

Configure these secrets for full functionality:

```bash
# In OpenSSL repository
gh secret set DISPATCH_TOKEN --repo sparesparrow/openssl --body "$YOUR_GITHUB_TOKEN"

# In OpenSSL-Tools repository  
gh secret set OPENSSL_TOKEN --repo sparesparrow/openssl-tools --body "$YOUR_GITHUB_TOKEN"
```

**Required Token Scopes**: `repo`, `workflow`

### Cloudsmith Publishing

The repository automatically publishes Conan packages to Cloudsmith. Configure the API key:

```bash
# In OpenSSL-Tools repository
gh secret set CLOUDSMITH_API_KEY --repo sparesparrow/openssl-tools --body "$YOUR_CLOUDSMITH_API_KEY"
```

**Enhanced CI/CD Features**:
- ✅ **Conan caching** - Speeds up builds by ~50-70%
- ✅ **SBOM generation** - CycloneDX format for compliance
- ✅ **Security scanning** - CodeQL and Bandit integration
- ✅ **Deployment bundles** - Conan-free artifacts for direct usage
- ✅ **Smart upload** - Recipe-only for PRs, full package for main
- ✅ **Fork protection** - Prevents accidental publishing from forks

See [.github/WORKFLOW_CONFIGURATION.md](.github/WORKFLOW_CONFIGURATION.md) for detailed workflow documentation.

## Workflow Integration

```mermaid
graph TD
    A[OpenSSL PR Created] --> B[Fast Validation]
    B --> C[Trigger openssl-tools Build]
    C --> D[Comprehensive CI/CD]
    D --> E[Report Status Back]
    
    F[OpenSSL Master Merge] --> G[Release Build]
    G --> H[Production Deploy]
    
    I[Nightly Schedule] --> J[Full Test Suite]
    J --> K[Security Scans]
    K --> L[Performance Tests]
```

## Available Commands

- `openssl-env` - Environment setup (--minimal, --full, --dev)
- `openssl-build` - Build optimization and management
- `openssl-conan` - Conan package management
- `openssl-test` - Test execution and validation
- `openssl-security` - Security validation and scanning
- `openssl-monitor` - Status monitoring and reporting
- `openssl-workflow` - Workflow management and automation

## Documentation

- **[Getting Started](docs/README.md)** - Detailed setup guide
- **[Contributing](docs/CONTRIBUTING.md)** - How to contribute
- **[Technical Details](.cursor/docs/)** - Deep technical documentation
- **[AI Agent Rules](.cursor/rules/)** - Cursor AI configuration

## Separate Packages

These packages are being extracted to separate repositories:

- **[openssl-migration](https://github.com/sparesparrow/openssl-migration)** - Migration framework
- **[openssl-crypto](https://github.com/sparesparrow/openssl-crypto)** - Crypto library wrappers  
- **[openssl-ssl](https://github.com/sparesparrow/openssl-ssl)** - SSL/TLS utilities
- **[openssl-query](https://github.com/sparesparrow/openssl-query)** - Perl-based query tool

## License

MIT License - see [LICENSE](LICENSE) for details.