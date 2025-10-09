# Repository Separation: OpenSSL vs OpenSSL Tools

## Overview

The OpenSSL project uses a **two-repository architecture** to separate concerns between source code and build infrastructure:

- **[OpenSSL Repository](https://github.com/sparesparrow/openssl)**: Source code and core functionality
- **[OpenSSL Tools Repository](https://github.com/sparesparrow/openssl-tools)**: Build infrastructure and tooling

## Why Two Repositories?

### Separation of Concerns

**OpenSSL Repository** focuses on:
- Cryptographic algorithms and implementations
- SSL/TLS protocol implementation
- Core OpenSSL functionality
- Source code quality and security

**OpenSSL Tools Repository** focuses on:
- Build orchestration and CI/CD
- Package management and distribution
- Performance testing and benchmarking
- Development tooling and automation

### Benefits

1. **Cleaner Development**: OpenSSL contributors focus on cryptography, not build systems
2. **Independent Evolution**: Build infrastructure can evolve without affecting source code
3. **Reduced Complexity**: Each repository has a single, clear purpose
4. **Better Security**: Build infrastructure changes don't require source code review
5. **Faster Iteration**: Tools can be updated independently of OpenSSL releases

## What Belongs Where

### OpenSSL Repository

**Contains**:
- OpenSSL source code (`crypto/`, `ssl/`, `apps/`, etc.)
- Core documentation (`doc/`, `README.md`)
- Basic validation workflow
- Minimal build configuration
- Release management

**Does NOT contain**:
- Complex CI/CD workflows
- Build orchestration scripts
- Package management tools
- Performance testing infrastructure

### OpenSSL Tools Repository

**Contains**:
- CI/CD workflows (`.github/workflows/`)
- Build scripts (`scripts/`)
- Conan package management
- Performance benchmarking
- Security scanning tools
- Documentation for tools usage

**Does NOT contain**:
- OpenSSL source code
- Cryptographic implementations
- SSL/TLS protocol code
- Core OpenSSL functionality

## How They Coordinate

### Cross-Repository Triggers

**OpenSSL → OpenSSL Tools**:
```yaml
# In openssl repo: .github/workflows/trigger-tools.yml
- name: Trigger openssl-tools build
  uses: peter-evans/repository-dispatch@v2
  with:
    token: ${{ secrets.OPENSSL_TOOLS_TOKEN }}
    repository: sparesparrow/openssl-tools
    event-type: openssl-changes
    client-payload: |
      {
        "sha": "${{ github.sha }}",
        "pr_number": "${{ github.event.number }}",
        "changes": ["crypto", "ssl", "apps"]
      }
```

**OpenSSL Tools → OpenSSL**:
```yaml
# In openssl-tools repo: .github/workflows/openssl-ci-dispatcher.yml
- name: Report build status
  uses: actions/github-script@v6
  with:
    script: |
      await github.rest.checks.create({
        owner: 'sparesparrow',
        repo: 'openssl',
        name: 'openssl-tools-build',
        head_sha: '${{ github.event.client_payload.sha }}',
        status: 'completed',
        conclusion: '${{ job.status }}'
      });
```

### Workflow Integration

1. **OpenSSL PR Created**: Triggers basic validation in openssl repo
2. **Validation Passes**: Triggers comprehensive build in openssl-tools
3. **Build Completes**: Results reported back to OpenSSL PR
4. **Status Updates**: OpenSSL PR shows build status from tools repo

### Artifact Sharing

**OpenSSL Tools → OpenSSL**:
- Built packages available via GitHub Packages
- Test results and performance metrics
- Security scan reports
- Build artifacts for download

**OpenSSL → OpenSSL Tools**:
- Source code changes trigger builds
- Version information for package naming
- Release tags for package versioning

## Migration from PR #15

### What Was Moved

**From OpenSSL to OpenSSL Tools**:
- All orchestration scripts (`scripts/`)
- Complex CI workflows (`.github/workflows/`)
- Development profiles (`conan-dev/`, `conan-profiles/`)
- Custom documentation files
- Build optimization tools

**Remained in OpenSSL**:
- `conanfile.py` (complete with all methods)
- Essential profiles (`.conan2/`)
- Basic validation workflow
- Test package (`test_package/`)
- Standard OpenSSL files

### Migration Benefits

1. **Cleaner OpenSSL Repo**: Focus on source code, not build complexity
2. **Specialized Tools Repo**: Dedicated to build infrastructure
3. **Independent Development**: Tools can evolve without affecting OpenSSL
4. **Better Organization**: Clear separation of responsibilities

## Development Workflow

### For OpenSSL Contributors

1. **Make changes** in openssl repository
2. **Create PR** in openssl repository
3. **Basic validation** runs in openssl repository
4. **Comprehensive build** triggers in openssl-tools repository
5. **Build results** reported back to openssl PR
6. **Merge** when both validations pass

### For Tools Contributors

1. **Make changes** in openssl-tools repository
2. **Create PR** in openssl-tools repository
3. **Test changes** with openssl-tools CI
4. **Validate integration** with openssl repository
5. **Merge** when tests pass

### Cross-Repository Testing

**Testing Tools Changes**:
```bash
# In openssl-tools repo
git checkout -b feature/new-build-script
# Make changes
git push origin feature/new-build-script
# Create PR in openssl-tools

# Test with openssl repo
# Create test PR in openssl repo to trigger new workflow
```

## Configuration and Setup

### OpenSSL Repository Setup

**Minimal configuration**:
```yaml
# .github/workflows/basic-validation.yml
name: Basic Validation
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Basic checks
        run: |
          ./config
          make -j$(nproc)
```

**Trigger configuration**:
```yaml
# .github/workflows/trigger-tools.yml
name: Trigger Tools Build
on:
  pull_request:
    types: [opened, synchronize]
jobs:
  trigger:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger openssl-tools
        # ... trigger configuration
```

### OpenSSL Tools Repository Setup

**Comprehensive CI/CD**:
```yaml
# .github/workflows/openssl-ci-dispatcher.yml
name: OpenSSL CI Dispatcher
on:
  repository_dispatch:
    types: [openssl-changes]
jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        platform: [linux, macos, windows]
    steps:
      - uses: actions/checkout@v4
      - name: Build OpenSSL
        # ... comprehensive build process
```

## Best Practices

### Repository Boundaries

**OpenSSL Repository**:
- Keep minimal and focused
- Avoid build complexity
- Maintain clear separation
- Document integration points

**OpenSSL Tools Repository**:
- Comprehensive build coverage
- Robust error handling
- Clear documentation
- Regular maintenance

### Communication

**Between Repositories**:
- Use clear event types
- Include necessary context
- Handle failures gracefully
- Maintain audit trails

**With Contributors**:
- Document the separation clearly
- Provide migration guides
- Explain the benefits
- Offer support during transition

## Troubleshooting

### Common Issues

**Build Not Triggering**:
- Check trigger configuration in openssl repo
- Verify secrets are configured
- Ensure event types match

**Status Not Reporting**:
- Check GitHub token permissions
- Verify repository access
- Review workflow logs

**Artifact Access**:
- Ensure proper package permissions
- Check GitHub Packages configuration
- Verify authentication tokens

### Debugging

**Check Trigger Logs**:
```bash
# In openssl repo
gh run list --repo sparesparrow/openssl
gh run view <run-id> --repo sparesparrow/openssl
```

**Check Build Logs**:
```bash
# In openssl-tools repo
gh run list --repo sparesparrow/openssl-tools
gh run view <run-id> --repo sparesparrow/openssl-tools
```

## Future Evolution

### Planned Improvements

1. **Enhanced Integration**: Better cross-repo communication
2. **Automated Testing**: More comprehensive integration tests
3. **Performance Monitoring**: Real-time build performance tracking
4. **Security Enhancements**: Improved security scanning integration

### Extension Points

1. **Additional Repositories**: Support for more specialized repos
2. **Advanced Triggers**: More sophisticated trigger conditions
3. **Custom Workflows**: User-defined build configurations
4. **Integration APIs**: Programmatic access to build results

## Conclusion

The two-repository architecture provides:

- **Clear separation** of concerns
- **Independent evolution** of components
- **Better maintainability** and organization
- **Improved security** and review processes
- **Enhanced developer experience**

This separation allows both repositories to focus on their core strengths while maintaining tight integration for a seamless development experience.

---

**Related Documentation**:
- [Architecture Overview](architecture.md)
- [CI/CD Patterns](cicd-patterns.md)
- [Getting Started Guide](../tutorials/getting-started.md)
- [Contributing Guide](../../CONTRIBUTING.md)
