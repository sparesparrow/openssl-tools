# Migration Guide: Python Structure Enhancement

This guide helps you migrate from the old script-based structure to the new organized package structure.

## Overview of Changes

The Python scripts have been reorganized from a flat `scripts/` directory structure to a domain-driven package structure under `openssl_tools/`.

## Import Path Changes

### Before (Old Structure)
```python
# Old imports from scripts/
from scripts.validation.pre_build_validation import PreBuildValidator
from scripts.conan.test_harness import TestHarness
from scripts.monitoring.status_reporter import StatusReporter
```

### After (New Structure)
```python
# New imports from openssl_tools package
from openssl_tools.security.build_validation import PreBuildValidator
from openssl_tools.testing.test_harness import NgapyTestHarness
from openssl_tools.monitoring.status_reporter import StatusReporter
```

## Domain Mapping

### Security Domain (`openssl_tools/security/`)
| Old Path | New Path | Class Name |
|----------|----------|------------|
| `scripts/validation/artifact-lifecycle-manager.py` | `openssl_tools/security/artifact_lifecycle.py` | `ArtifactLifecycleManager` |
| `scripts/validation/auth-token-manager.py` | `openssl_tools/security/authentication.py` | `AuthTokenManager` |
| `scripts/validation/secure-key-manager.py` | `openssl_tools/security/key_management.py` | `SecureKeyManager` |
| `scripts/validation/pre-build-validation.py` | `openssl_tools/security/build_validation.py` | `PreBuildValidator` |
| `scripts/generate_sbom.py` | `openssl_tools/security/sbom_generator.py` | `OpenSSLSBOMGenerator` |

### Testing Domain (`openssl_tools/testing/`)
| Old Path | New Path | Class Name |
|----------|----------|------------|
| `scripts/conan/code_quality_manager.py` | `openssl_tools/testing/quality_manager.py` | `CodeQualityManager` |
| `scripts/conan/test_harness.py` | `openssl_tools/testing/test_harness.py` | `NgapyTestHarness` |
| `scripts/conan/database_schema_validator.py` | `openssl_tools/testing/schema_validator.py` | `DatabaseSchemaValidator` |
| `scripts/conan/fuzz-corpora-manager.py` | `openssl_tools/testing/fuzz_manager.py` | `FuzzCorporaManager` |

### Monitoring Domain (`openssl_tools/monitoring/`)
| Old Path | New Path | Class Name |
|----------|----------|------------|
| `scripts/status_reporter.py` | `openssl_tools/monitoring/status_reporter.py` | `StatusReporter` |
| `scripts/conan/log_whitelist_manager.py` | `openssl_tools/monitoring/log_manager.py` | `LogWhitelistManager` |

### Development Domain (`openssl_tools/development/`)
| Old Path | New Path | Class Name |
|----------|----------|------------|
| `scripts/conan/build_matrix_manager.py` | `openssl_tools/development/build_system/matrix_manager.py` | `BuildMatrixManager` |
| `scripts/conan/performance_benchmark.py` | `openssl_tools/development/build_system/benchmarking.py` | `PerformanceBenchmark` |
| `scripts/validation/cache-optimization.py` | `openssl_tools/development/build_system/cache_optimization.py` | `CacheOptimizer` |
| `scripts/validation/registry-versioning.py` | `openssl_tools/development/package_management/registry_versioning.py` | `RegistryVersioning` |
| `scripts/conan/package-registry-manager.py` | `openssl_tools/development/package_management/registry_manager.py` | `PackageRegistryManager` |

### Automation Domain (`openssl_tools/automation/`)
| Old Path | New Path | Class Name |
|----------|----------|------------|
| `scripts/upload/multi-registry-upload.py` | `openssl_tools/automation/deployment/multi_registry.py` | `MultiRegistryUploader` |
| `scripts/upload-conan-package.py` | `openssl_tools/automation/deployment/package_upload.py` | `PackageUploader` |
| `scripts/setup-ci-environment.py` | `openssl_tools/automation/deployment/ci_setup.py` | `CISetup` |
| `scripts/setup-conan-python-env.py` | `openssl_tools/automation/deployment/python_env_setup.py` | `PythonEnvSetup` |
| `scripts/setup-github-packages-conan.py` | `openssl_tools/automation/deployment/github_packages_setup.py` | `GitHubPackagesSetup` |
| `scripts/mcp/database-server.py` | `openssl_tools/automation/ai_agents/database_server.py` | `DatabaseServer` |

## CLI Command Changes

### New CLI Commands
```bash
# Security commands
openssl-tools security validate --config security.yml

# Testing commands
openssl-tools test run --suite integration

# Monitoring commands
openssl-tools monitor status --format json

# Individual tool commands
openssl-security --help
openssl-test --help
openssl-monitor --help
openssl-sbom --help
```

### Backward Compatibility
Root-level Python files still work as thin wrappers:
```bash
# These still work for backward compatibility
python conan_remote_manager.py --help
python build_optimizer.py --help
python package_signer.py --help
python fuzz_integration.py --help
```

## Migration Steps

### Step 1: Update Imports
1. Find all imports from `scripts/` in your code
2. Replace with new `openssl_tools.` imports
3. Update class names if they changed (see mapping table above)

### Step 2: Update Script Execution
1. Replace direct script execution with CLI commands where possible
2. Use backward compatibility wrappers for existing scripts
3. Update any CI/CD scripts that call moved scripts

### Step 3: Update Documentation
1. Update any documentation that references old paths
2. Update README files with new CLI commands
3. Update examples to use new import paths

### Step 4: Test Changes
1. Test all imports work correctly
2. Test CLI commands function as expected
3. Test backward compatibility wrappers
4. Run your existing scripts to ensure they still work

## Examples

### Example 1: Security Validation
```python
# Before
from scripts.validation.pre_build_validation import PreBuildValidator
validator = PreBuildValidator()
validator.validate_build_security()

# After
from openssl_tools.security.build_validation import PreBuildValidator
validator = PreBuildValidator()
validator.validate_build_security()

# Or use CLI
# openssl-tools security validate
```

### Example 2: Test Execution
```python
# Before
from scripts.conan.test_harness import TestHarness
harness = TestHarness()
harness.run_tests()

# After
from openssl_tools.testing.test_harness import NgapyTestHarness
harness = NgapyTestHarness()
harness.run_tests()

# Or use CLI
# openssl-tools test run
```

### Example 3: Status Monitoring
```python
# Before
from scripts.status_reporter import StatusReporter
reporter = StatusReporter()
status = reporter.get_system_status()

# After
from openssl_tools.monitoring.status_reporter import StatusReporter
reporter = StatusReporter()
status = reporter.get_system_status()

# Or use CLI
# openssl-tools monitor status
```

## Troubleshooting

### Import Errors
If you get import errors:
1. Check the class name mapping table above
2. Verify the new import path is correct
3. Ensure the package is installed: `pip install -e .`

### CLI Command Not Found
If CLI commands don't work:
1. Reinstall the package: `pip install -e .`
2. Check that entry points are defined in `pyproject.toml`
3. Use the full path: `python -m openssl_tools.foundation.command_line.main`

### Backward Compatibility Issues
If root-level wrappers don't work:
1. Check that the target module exists in the new location
2. Verify the import path in the wrapper file
3. Test the target module directly

## Support

If you encounter issues during migration:
1. Check the [python-structure-improved.md](python-structure-improved.md) documentation
2. Review the [scripts/README.md](../scripts/README.md) for what remains in scripts/
3. Test with the examples provided above
4. Create an issue if you find bugs or need help

## Timeline

- **Phase 1**: Immediate - All new imports work
- **Phase 2**: 3 months - Deprecation warnings for old imports
- **Phase 3**: 6 months - Old imports may be removed

This timeline ensures a smooth transition while maintaining backward compatibility.
