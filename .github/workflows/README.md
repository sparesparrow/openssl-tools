# Development Workflow Documentation

This directory contains GitHub Actions workflows that implement the development workflow diagram defined in `.cursor/workflows/development-workflow.md`.

## Workflow Overview

The workflows are designed to implement the three main development workflows from the diagram:

1. **Component Development Workflow** - Full development lifecycle
2. **Security Review Workflow** - Security-focused review process
3. **Performance Optimization Workflow** - Performance analysis and optimization

## Automation Rules

The workflows implement the following automation rules from the diagram:

### Rule 1: PR with Crypto/SSL Changes → Security Review
- **Trigger**: Pull request created with changes to `*/crypto/*` or `*/ssl/*` files
- **Workflow**: `security-review.yml`
- **Condition**: `files_changed_match_pattern('*/crypto/*,*/ssl/*')`

### Rule 2: Commit to Main with Successful Build → Component Development
- **Trigger**: Commit pushed to main branch
- **Workflow**: `component-development.yml`
- **Condition**: `build_status_successful`

### Rule 3: Performance Regression Detected → Performance Optimization
- **Trigger**: Performance regression detected
- **Workflow**: `performance-optimization.yml`
- **Condition**: `performance_regression_detected` with `priority=high`

## Workflow Files

### Core Workflows

#### `component-development.yml`
Implements the complete Component Development Workflow:
- **Setup Environment**: Load variables, validate dependencies, start database, verify Conan
- **Code Development**: Create structure, implement functionality, write tests, security analysis, performance validation
- **Integration Testing**: Build component, run tests, validate dependencies, check API compatibility
- **Quality Assurance**: Static analysis, security scan, documentation validation, code coverage
- **Package Preparation**: Create Conan package, generate metadata, create SBOM, sign artifacts
- **Distribution**: Upload to Artifactory, GitHub Packages, update database, generate release notes

#### `security-review.yml`
Implements the Security Review Workflow:
- **Automated Scanning**: SAST tools, dependency vulnerabilities, crypto analysis, input sanitization
- **Manual Review**: Security sensitive code, threat model, compliance, attack surface
- **Penetration Testing**: Automated security tests, fuzzing, side channel resistance, crypto correctness
- **Documentation Review**: Security docs, usage guidelines, vulnerability disclosure, security policies

#### `performance-optimization.yml`
Implements the Performance Optimization Workflow:
- **Baseline Measurement**: Performance benchmarks, CPU profiling, memory analysis, build times
- **Optimization Implementation**: Identify bottlenecks, implement optimizations, validate correctness, measure improvements
- **Validation**: Regression tests, security verification, API compatibility, performance gains confirmation

### Automation Workflows

#### `workflow-dispatcher.yml`
Central dispatcher that analyzes changes and triggers appropriate workflows based on the automation rules.

#### `automation-rules.yml`
Implements the automation rules engine that evaluates conditions and triggers workflows.

#### `automation-triggers.yml`
Handles the specific trigger conditions for each automation rule.

#### `development-workflow-orchestrator.yml`
Main orchestrator that combines all workflows and implements the complete automation logic.

### Supporting Workflows

#### `security-scan.yml`
Enhanced security scanning workflow with:
- CodeQL analysis
- Dependency review
- SAST scanning with Bandit
- SBOM generation
- FIPS validation

#### `complete-development-workflow.yml`
Comprehensive workflow that combines all three main workflows into a single reusable workflow.

## Usage

### Manual Trigger
```bash
# Trigger specific workflow
gh workflow run component-development.yml
gh workflow run security-review.yml
gh workflow run performance-optimization.yml

# Trigger orchestrator with specific workflow type
gh workflow run development-workflow-orchestrator.yml -f workflow_type=security-review
```

### Automatic Triggers

#### PR with Crypto/SSL Changes
```yaml
# Automatically triggers security-review.yml
on:
  pull_request:
    paths:
      - '**/crypto/**'
      - '**/ssl/**'
```

#### Commit to Main
```yaml
# Automatically triggers component-development.yml
on:
  push:
    branches: [main, master]
```

#### Performance Regression
```yaml
# Automatically triggers performance-optimization.yml
on:
  workflow_dispatch:
    inputs:
      trigger_reason: 'regression_detected'
```

## Workflow Dependencies

The workflows are designed to work together:

1. **Development Workflow Orchestrator** → Analyzes triggers and calls appropriate workflows
2. **Component Development** → Full development lifecycle
3. **Security Review** → Security-focused analysis
4. **Performance Optimization** → Performance analysis and optimization
5. **Automation Rules** → Implements the automation logic from the diagram

## Configuration

### Environment Variables
- `CONAN_REMOTE_URL`: Conan remote repository URL
- `ARTIFACTORY_URL`: JFrog Artifactory URL
- `COVERITY_TOKEN`: Coverity scan token (for static analysis)

### Secrets
- `CONAN_PASSWORD`: Conan remote password
- `ARTIFACTORY_PASSWORD`: Artifactory password
- `GITHUB_TOKEN`: GitHub token for API access

## Monitoring

Each workflow generates a summary report that includes:
- Trigger analysis
- Workflow execution results
- Automation rules applied
- Performance metrics
- Security scan results

## Troubleshooting

### Common Issues

1. **Workflow not triggering**: Check the path filters and branch conditions
2. **Build failures**: Verify environment setup and dependencies
3. **Security scan failures**: Check for sensitive data in code
4. **Performance regression**: Review recent changes and optimization opportunities

### Debug Mode
Enable debug logging by setting the `ACTIONS_STEP_DEBUG` environment variable to `true`.

## Contributing

When adding new workflows:
1. Follow the naming convention: `workflow-name.yml`
2. Include comprehensive documentation
3. Add appropriate triggers and conditions
4. Test with manual dispatch first
5. Update this README with the new workflow information
