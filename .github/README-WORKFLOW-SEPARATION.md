# Workflow Separation Documentation

## Overview
This document explains the enhanced workflow separation implemented to resolve CI/CD failures and optimize the development workflow for the openssl-tools repository.

## Repository Architecture

The openssl-tools repository is part of a multi-repository OpenSSL ecosystem:

### Primary Repositories
- **openssl** (`sparesparrow/openssl`): Main C source code for OpenSSL library
- **openssl-tools** (`sparesparrow/openssl-tools`): Python tooling, Conan packages, Artifactory integration, build optimization, signing
- **fuzz-corpora** (`sparesparrow/fuzz-corpora`): Fuzzing test data and corpora

## Workflow Categorization

### Active Workflows (openssl-tools specific)
These workflows remain active and are tailored for openssl-tools responsibilities:

- **Conan Build and Test** (`conan-ci-enhanced.yml`, `conan-manual-trigger.yml`, `conan-nightly.yml`, `conan-release.yml`, `conan-ci.yml`, `conan-pr-tests.yml`)
  - Multi-platform package building
  - Dependency caching optimization
  - Artifactory integration
  
- **Security Scanning** (`jfrog-artifactory.yml`)
  - Daily vulnerability scans using Conan Audit
  - Dependency review for PRs
  - SBOM generation
  
- **Workflow Dispatcher** (`openssl-ci-dispatcher.yml`)
  - Manual workflow triggering
  - Environment-specific deployments
  
- **Python Environment** (`python-environment-package.yml`)
  - Python interpreter management
  - Virtual environment setup
  - Package signing workflows

- **Migration Framework** (`migration-controller.yml`)
  - OpenSSL migration automation
  - Build system modernization

- **Documentation** (`deploy-docs-openssl-org.yml`)
  - Documentation deployment
  - Agent loop improvements

### Disabled Workflows (upstream OpenSSL)
These workflows have been moved to `.github/workflows-upstream-disabled/`:

- **baseline-ci.yml**: Upstream OpenSSL baseline CI tests
- **main.yml**: Upstream OpenSSL main CI pipeline
- **trigger-tools.yml**: Upstream OpenSSL tools triggering
- **windows.yml**: Upstream OpenSSL Windows-specific tests
- **fips-label.yml**: Upstream OpenSSL FIPS labeling

## Modern CI/CD Best Practices Implemented

### 1. Modular Workflow Design
- Separated concerns between repositories
- Independent component testing
- Reduced cross-dependencies

### 2. Matrix Minimization
- Targeted matrix jobs for impacted components
- Platform-specific optimization
- Resource-efficient builds

### 3. Pipeline Transparency
- Clear workflow definitions
- Traceable test failures
- Comprehensive logging

### 4. Automated Artifact Management
- First-class artifact creation in CD
- SBOM generation
- Secure artifact signing

### 5. Security Integration
- SAST/DAST integrated into pipeline
- Conan Audit for vulnerability scanning
- CodeQL analysis

### 6. Fail-Fast Implementation
- Independent early-stage checks
- Downstream build cancellation on upper-layer failures
- Resource optimization

## Performance Improvements

### Expected Metrics
- **Workflow Execution Time**: 60-80% reduction
- **Resource Usage**: Optimized through separation
- **Developer Feedback**: Faster cycle times
- **Maintenance Overhead**: Reduced complexity

### Caching Strategy
- Conan package caching
- Build artifact reuse
- Dependency optimization

## Rollback Instructions

If workflow separation needs to be reverted:

```bash
# Restore upstream workflows
mv .github/workflows-upstream-disabled/* .github/workflows/

# Remove separation documentation
rm .github/README-WORKFLOW-SEPARATION.md

# Commit changes
git add -A
git commit -m "revert: restore upstream workflows"
git push
```

## Troubleshooting

### Common Issues
1. **Missing Dependencies**: Check Conan cache and profiles
2. **Authentication Failures**: Verify Artifactory tokens
3. **Platform-Specific Failures**: Review matrix configuration

### Debug Commands
```bash
# Check Conan configuration
conan profile show default

# Verify workflow syntax
gh workflow list

# Monitor workflow runs
gh run list --limit 10
```

## Contact and Support

- **Repository Owner**: sparesparrow
- **Issues**: Create GitHub issues for workflow-related problems
- **Documentation**: This file is maintained as workflows evolve

## Change Log

- **v1.0** - Initial workflow separation implementation
- **v1.1** - Enhanced Conan integration and security scanning
- **v1.2** - Performance optimization and monitoring improvements