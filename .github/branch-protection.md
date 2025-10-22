# Branch Protection and Quality Gates

This document outlines the branch protection rules and quality gates implemented for the OpenSSL Tools repository to ensure code quality, security, and maintainable development practices.

## Branch Protection Rules

### Main Branch Protection

**Required Status Checks:**
- ✅ **Core CI** - Must pass for all PRs
- ✅ **PR Developer Flow Check** - Validates version bumps and recipe syntax
- ✅ **Security Scan** - Vulnerability scanning and SBOM generation
- ✅ **E2E Tests** - End-to-end validation (Linux and Windows)

**Required Reviews:**
- ✅ **At least 1 approving review** from code owners
- ✅ **Required reviewers** from `@sparesparrow` (repository owner)

**Additional Rules:**
- ✅ **Restrict pushes** - Only repository administrators can push directly to main
- ✅ **Require branches to be up to date** - PRs must be rebased on latest main
- ✅ **Require status checks to pass** - All required checks must pass before merge
- ✅ **Dismiss stale pull request approvals** - Reviews are dismissed if new commits are pushed

### Protected Branches

- `main` - Production branch with full protection
- `master` - Legacy branch (if exists) with same protection as main
- `release/*` - Release branches with similar protection

## Quality Gates

### Pre-Merge Requirements

1. **Code Review**: All changes require approval from designated reviewers
2. **CI Pipeline**: All automated tests and builds must pass
3. **Security Checks**: Vulnerability scans must pass
4. **Version Validation**: Version bumps must be validated for conanfile.py changes
5. **E2E Validation**: End-to-end tests must pass on multiple platforms

### Automated Quality Checks

#### Version Bump Enforcement
- PRs that modify `conanfile.py` must include a version bump
- Automated check validates version changes between base and head
- Provides clear error messages with fix instructions

#### Security Scanning
- Automated vulnerability scanning with Trivy
- SBOM generation for supply chain transparency
- FIPS compliance validation for cryptographic components

#### E2E Testing
- Linux E2E workflow tests complete build/upload cycle
- Windows E2E workflow validates cross-platform compatibility
- Consumer testing validates package usability

## Setup Instructions

### Enabling Branch Protection

1. **Go to Repository Settings** → Branches
2. **Add Rule** for `main` branch
3. **Configure Required Status Checks**:
   - Select: `Core CI`, `PR Developer Flow Check`, `Security Scan`, `E2E Tests`
4. **Set Required Reviews**: At least 1 from code owners
5. **Enable Additional Options**:
   - Restrict pushes that create matching branches
   - Require branches to be up to date before merging
   - Require status checks to pass
   - Dismiss stale pull request approvals when new commits are pushed

### CODEOWNERS Setup

1. **Go to Repository Settings** → CODEOWNERS
2. **Verify CODEOWNERS file** exists and is valid
3. **Enable Required Reviews** in branch protection rules

## Workflow Integration

### Required Workflows for Branch Protection

The following workflows must pass for PRs to be merged:

#### Core CI (`core-ci.yml`)
- **Triggers**: Push to main, PRs
- **Coverage**: Linux, macOS, Windows builds
- **Artifacts**: Build results, SBOMs, security reports

#### PR Developer Flow (`pr-developer-flow.yml`)
- **Triggers**: PRs with conanfile.py changes
- **Checks**: Version bump validation, syntax validation, required files

#### Security Scan (`security-scan` in core-ci.yml)
- **Triggers**: Source code changes
- **Checks**: Vulnerability scanning, SBOM generation

#### E2E Tests (`e2e-linux-openssl.yml`, `e2e-windows-openssl.yml`)
- **Triggers**: Main branch pushes, manual dispatch
- **Coverage**: End-to-end package creation and consumption

## Maintenance

### Regular Reviews

- **Monthly**: Review and update CODEOWNERS as team changes
- **Quarterly**: Audit branch protection effectiveness
- **After Incidents**: Update protection rules based on lessons learned

### Emergency Procedures

**Hotfix Merges**: Repository administrators can bypass branch protection for critical security fixes with documented justification.

**Temporary Disables**: In case of CI/CD issues, temporarily disable specific checks with team approval and documented rollback plan.

## Benefits

1. **Quality Assurance**: Automated checks prevent merging broken code
2. **Security**: Vulnerability scanning prevents security issues
3. **Consistency**: Standardized version bumping and testing
4. **Accountability**: Clear ownership and review requirements
5. **Compliance**: Supports FIPS and security compliance requirements

## Troubleshooting

### Common Issues

**"Required status check not found"**
- Ensure workflow names match exactly in branch protection settings
- Check that workflows are enabled and not failing

**"Version bump required" failures**
- Update version in conanfile.py
- Commit the version change
- Push to trigger re-validation

**"Security scan failed"**
- Review vulnerability report artifacts
- Address high/critical vulnerabilities
- Re-run security scan after fixes

This branch protection setup ensures high-quality, secure, and maintainable code while supporting efficient development workflows.
