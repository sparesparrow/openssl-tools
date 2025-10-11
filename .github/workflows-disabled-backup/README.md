# Disabled Backup Workflows

This directory contains GitHub Actions workflows that were moved from `.github/workflows-backup/` to prevent them from being executed by GitHub Actions.

## Why These Were Moved

GitHub Actions executes any `.yml` file in any `.github/workflows/` subdirectory, including backup directories. These workflows were causing failures in pull requests because they contain upstream OpenSSL test workflows that don't apply to the openssl-tools repository.

## Contents

- **`legacy-openssl/`**: Legacy OpenSSL CI workflows
- **`experimental/`**: Experimental workflows including upstream OpenSSL test workflows
- **`upstream-only/`**: Workflows designed only for upstream OpenSSL repository

## Upstream OpenSSL Test Workflows

The following workflows were causing PR failures and have been disabled:

- `run-checker-ci.yml` - OpenSSL source code compilation tests
- `fuzz-checker.yml` - OpenSSL source code fuzz testing
- `perl-minimal-checker.yml` - OpenSSL Perl configuration tests
- `windows-github-ci.yml` - Windows-specific OpenSSL source testing
- `coding-style.yml` - OpenSSL source code style checks

## Repository Separation

This is part of the two-repository architecture:

- **[OpenSSL Repository](https://github.com/sparesparrow/openssl)**: Source code and core functionality
- **[OpenSSL Tools Repository](https://github.com/sparesparrow/openssl-tools)**: Build infrastructure and tooling

The openssl-tools repository contains build orchestration and tooling, not OpenSSL source code. Therefore, upstream OpenSSL test workflows are not applicable here.

## Active Workflows

The following workflows remain active and are appropriate for openssl-tools:

- `automation-triggers.yml` - Triggers automation workflows
- `security-review.yml` - Security review workflows
- `workflow-dispatcher.yml` - Workflow dispatch management
- `development-workflow-orchestrator.yml` - Development workflow orchestration
- `conan-ci.yml` - Conan package management CI
- `openssl-build-publish.yml` - OpenSSL build and publish workflows

## Related Documentation

- [Repository Separation Guide](../docs/explanation/repo-separation.md)
- [Python Structure Improvements](../docs/python-structure-improved.md)
