# Experimental Workflows

This directory contains workflows from PR #6 development iterations and experimental approaches that were tried during the CI modernization process.

## Development History

These workflows represent the evolution of the CI system from traditional OpenSSL builds to modern Conan 2.0 package management.

### Phase 1: Initial Modernization
- **Nuclear success approach**: Attempted to solve all CI issues at once
- **Minimal success**: Tried to create the simplest possible working CI
- **Simple overrides**: Various override approaches to fix specific issues

### Phase 2: Optimization Attempts
- **Fast lane CI**: Attempted to speed up CI execution
- **Incremental patches**: Tried to fix issues incrementally
- **Optimized approaches**: Various optimization strategies

### Phase 3: Consolidation
- **Consolidated CI**: Attempted to consolidate multiple workflows
- **Enhanced approaches**: Tried to enhance existing workflows
- **Comprehensive overrides**: Comprehensive override strategies

## Workflow Categories

### Success Approaches
- `nuclear-success.yml` - Nuclear approach to CI success
- `minimal-success.yml` - Minimal CI approach
- `simple-success-override.yml` - Simple success override
- `ci-success.yml` - CI success approach

### Optimization Attempts
- `optimized-basic-ci.yml` - Optimized basic CI
- `optimized-ci.yml` - Optimized CI approach
- `fast-lane-ci.yml` - Fast lane CI
- `incremental-ci-patch.yml` - Incremental CI patches

### Consolidation Attempts
- `consolidated-ci.yml` - Consolidated CI approach
- `consolidated-ci-simple.yml` - Simplified consolidated CI
- `comprehensive-override.yml` - Comprehensive override approach

### Specialized Approaches
- `binary-first-ci.yml` - Binary-first CI approach
- `migration-controller.yml` - Migration controller
- `flaky-test-manager.yml` - Flaky test management
- `fuzz-checker.yml` - Fuzz testing checker

### Conan-Specific Experiments
- `conan-ci-enhanced.yml` - Enhanced Conan CI
- `conan-manual-trigger.yml` - Manual Conan triggers
- `conan-nightly.yml` - Nightly Conan builds
- `conan-pr-tests.yml` - Conan PR tests
- `conan-release.yml` - Conan release workflow

### Platform-Specific Experiments
- `windows-override.yml` - Windows-specific overrides
- `windows_comp.yml` - Windows compiler testing
- `os-zoo.yml` - OS distribution testing
- `compiler-zoo.yml` - Compiler testing

### Integration Experiments
- `basic-integration-test.yml` - Basic integration testing
- `basic-openssl-integration.yml` - Basic OpenSSL integration
- `cross-repository-integration.yml` - Cross-repository integration
- `interop-tests.yml` - Interoperability tests

### Cache and Performance
- `build-cache.yml` - Build caching strategies
- `cache-warmup.yml` - Cache warmup approaches
- `package-artifacts-upload.yml` - Artifact upload strategies

### Security and Quality
- `fips-checksums.yml` - FIPS checksum validation
- `fips-label.yml` - FIPS labeling
- `prov-compat-label.yml` - Provider compatibility labeling
- `provider-compatibility.yml` - Provider compatibility testing

### Documentation and Deployment
- `deploy-docs-openssl-org.yml` - Documentation deployment
- `make-release.yml` - Release management
- `package-artifacts-upload.yml` - Package artifact upload

## Lessons Learned

### What Worked
1. **Conan 2.0 approach**: Modern package management was the right direction
2. **Reusable workflows**: Breaking down workflows into reusable components
3. **Change detection**: Using path filters to optimize builds
4. **Matrix strategies**: Multi-platform builds with matrix strategies

### What Didn't Work
1. **Nuclear approach**: Trying to fix everything at once was too complex
2. **Minimal approach**: Too minimal didn't provide enough functionality
3. **Complex overrides**: Overly complex override systems were hard to maintain
4. **Platform-specific hacks**: Platform-specific workarounds were fragile

### Key Insights
1. **Gradual migration**: Incremental changes work better than big bangs
2. **Clear separation**: Separate concerns into different workflows
3. **Proper testing**: Test each change thoroughly before proceeding
4. **Documentation**: Document decisions and rationale

## Current Status

All experimental workflows have been superseded by the current production workflows:

- **Production workflows**: Located in `.github/workflows/`
- **Reusable components**: Located in `.github/workflows/reusable/`
- **Templates**: Located in `.github/workflow-templates/`

## Usage Guidelines

### When to Reference Experimental Workflows
1. **Understanding evolution**: See how the CI system evolved
2. **Learning from mistakes**: Understand what approaches didn't work
3. **Finding patterns**: Look for patterns that might be useful
4. **Troubleshooting**: Reference when debugging similar issues

### When NOT to Use Experimental Workflows
1. **Direct activation**: Never enable these workflows directly
2. **Production use**: These are not suitable for production
3. **Copy-paste**: Don't copy without understanding the context
4. **Current development**: Use current production workflows instead

## File Count

- **Total experimental workflows**: ~66 files
- **Success approaches**: ~4 files
- **Optimization attempts**: ~8 files
- **Conan-specific**: ~12 files
- **Platform-specific**: ~8 files
- **Integration experiments**: ~6 files
- **Other specialized**: ~28 files

## Maintenance

- **Archive organization**: Keep workflows organized by category
- **Documentation**: Maintain clear documentation of approaches
- **Cleanup**: Remove truly obsolete workflows periodically
- **Reference updates**: Update references when production workflows change