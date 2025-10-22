# Disabled OpenSSL Source Workflows

This directory contains workflows that were designed for the actual OpenSSL source repository, not this tools repository.

## Why These Workflows Were Disabled

This repository (`openssl-tools`) contains:
- OpenSSL build tooling and automation
- Conan package management
- Python extensions and utilities
- CI/CD workflows for OpenSSL development

It does **NOT** contain:
- The actual OpenSSL source code
- OpenSSL's `./config` or `./Configure` scripts
- OpenSSL's build system files
- OpenSSL's test suites

## Disabled Workflows

The following workflows were moved here because they expect OpenSSL source code:

- `basic-*.yml` - Basic OpenSSL build workflows
- `openssl-*.yml` - OpenSSL-specific build and test workflows
- `static-analysis.yml` - OpenSSL source code analysis
- `weekly-exhaustive.yml` - OpenSSL exhaustive testing
- `run-checker*.yml` - OpenSSL test runner workflows
- `fuzz-checker.yml` - OpenSSL fuzzing workflows
- `cross-compiles.yml` - OpenSSL cross-compilation workflows
- `riscv-more-cross-compiles.yml` - RISC-V specific OpenSSL builds

## Active Workflows

The following workflows are active and appropriate for this tools repository:

- `ci-tools.yml` - Main CI workflow for tools
- `workflow-dispatcher-tools.yml` - Workflow dispatcher for tools
- `security-scan-tools.yml` - Security scanning for tools
- `build-openssl.yml` - Reusable OpenSSL build workflow
- `test-integration.yml` - Reusable integration test workflow
- `publish-cloudsmith.yml` - Reusable Cloudsmith publishing workflow
- `quality-gates.yml` - Reusable quality gates workflow

## Usage

If you need to work with the actual OpenSSL source code, use the workflows in the main OpenSSL repository. This repository focuses on providing tooling and automation for OpenSSL development.