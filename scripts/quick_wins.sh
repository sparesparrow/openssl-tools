#!/bin/bash
# Quick wins: Disable upstream OpenSSL workflows

set -euo pipefail

# Workflows that are for upstream OpenSSL source code testing, not openssl-tools
WORKFLOWS_TO_DISABLE=(
  "run-checker.yml"
  "run-checker-merge.yml"
  "fuzz-checker.yml"
  "perl-minimal-checker.yml"
  "windows-github-ci.yml"
  "optimized-ci.yml"
  "provider-compatibility.yml"
  "coding-style.yml"
)

echo "🔧 Applying quick wins: Disabling upstream OpenSSL test workflows"

# Create directory for disabled upstream workflows
mkdir -p .github/workflows-disabled-upstream

# Move workflows to disabled directory
for workflow in "${WORKFLOWS_TO_DISABLE[@]}"; do
  if [[ -f ".github/workflows/$workflow" ]]; then
    echo "Moving $workflow to workflows-disabled-upstream/"
    git mv ".github/workflows/$workflow" ".github/workflows-disabled-upstream/"
  else
    echo "Workflow $workflow not found, skipping"
  fi
done

# Create README for disabled workflows
cat > .github/workflows-disabled-upstream/README.md << 'EOF'
# Disabled Upstream OpenSSL Workflows

This directory contains GitHub Actions workflows that were designed for testing OpenSSL source code changes in the upstream OpenSSL repository. These workflows are not applicable to the openssl-tools repository, which focuses on build infrastructure and tooling.

## Why These Are Disabled

The openssl-tools repository contains:
- Build orchestration and CI/CD infrastructure
- Package management and distribution tools
- Performance testing and benchmarking
- Development tooling and automation

It does NOT contain:
- OpenSSL source code (crypto/, ssl/, apps/, etc.)
- Cryptographic implementations
- SSL/TLS protocol code

## Workflows in This Directory

- `run-checker.yml` - Tests OpenSSL source code compilation
- `run-checker-merge.yml` - Tests OpenSSL source code on merge
- `fuzz-checker.yml` - Fuzz testing for OpenSSL source code
- `perl-minimal-checker.yml` - Perl configuration testing for OpenSSL
- `windows-github-ci.yml` - Windows-specific OpenSSL source testing
- `optimized-ci.yml` - Optimized CI for OpenSSL source code
- `provider-compatibility.yml` - Provider compatibility testing for OpenSSL
- `coding-style.yml` - Coding style checks for OpenSSL source code

## Active Workflows for openssl-tools

The following workflows remain active and are appropriate for this repository:

- `automation-triggers.yml` - Triggers automation workflows
- `security-review.yml` - Security review workflows
- `workflow-dispatcher.yml` - Workflow dispatch management
- `migration-controller.yml` - Migration control workflows

## Repository Separation

This is part of the two-repository architecture:

- **[OpenSSL Repository](https://github.com/sparesparrow/openssl)**: Source code and core functionality
- **[OpenSSL Tools Repository](https://github.com/sparesparrow/openssl-tools)**: Build infrastructure and tooling

For more information, see [Repository Separation Documentation](../docs/explanation/repo-separation.md).
EOF

# Stage changes
git add .github/workflows-disabled-upstream/

echo "✅ Quick wins applied successfully"
echo "📝 Created README explaining why workflows were disabled"
echo "🚀 Ready to commit changes"
