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
