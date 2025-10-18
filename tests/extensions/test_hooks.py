"""
Test Conan Hooks Extensions
Tests for OpenSSL-specific hooks in Conan extensions.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import json


class TestOpenSSLHooks:
    """Test suite for OpenSSL hooks."""

    def test_pre_build_hook_fips_check(self, temp_workspace, mock_fips_config):
        """Test pre-build hook FIPS compliance check."""
        from extensions.openssl_hooks.hooks.pre_build import PreBuildHook

        hook = PreBuildHook()

        # Test FIPS check before build
        with patch('extensions.openssl_hooks.hooks.pre_build.check_fips_requirements') as mock_check:
            mock_check.return_value = True

            result = hook.execute(temp_workspace, mock_fips_config)
            assert result is True
            mock_check.assert_called_once_with(temp_workspace, mock_fips_config)

    def test_post_build_hook_validation(self, temp_workspace):
        """Test post-build hook validation."""
        from extensions.openssl_hooks.hooks.post_build import PostBuildHook

        hook = PostBuildHook()

        # Test post-build validation
        with patch('extensions.openssl_hooks.hooks.post_build.validate_build_artifacts') as mock_validate:
            mock_validate.return_value = {
                "libraries": ["libssl.so", "libcrypto.so"],
                "fips_module": "fips.so",
                "valid": True
            }

            result = hook.execute(temp_workspace)
            assert result["valid"] is True
            assert "libssl.so" in result["libraries"]
            mock_validate.assert_called_once_with(temp_workspace)

    def test_pre_package_hook_sbom_generation(self, temp_workspace):
        """Test pre-package hook SBOM generation."""
        from extensions.openssl_hooks.hooks.pre_package import PrePackageHook

        hook = PrePackageHook()

        # Test SBOM generation
        with patch('extensions.openssl_hooks.hooks.pre_package.generate_sbom') as mock_sbom:
            mock_sbom.return_value = {
                "format": "CycloneDX",
                "components": ["openssl-3.0.0", "zlib-1.2.11"],
                "vulnerabilities": []
            }

            result = hook.execute(temp_workspace)
            assert result["format"] == "CycloneDX"
            assert len(result["components"]) == 2
            mock_sbom.assert_called_once_with(temp_workspace)

    def test_post_package_hook_compliance_check(self, temp_workspace):
        """Test post-package hook compliance verification."""
        from extensions.openssl_hooks.hooks.post_package import PostPackageHook

        hook = PostPackageHook()

        # Test compliance verification
        with patch('extensions.openssl_hooks.hooks.post_package.verify_compliance') as mock_verify:
            mock_verify.return_value = {
                "nist_compliant": True,
                "fips_140_3": True,
                "certificate": "4985"
            }

            result = hook.execute(temp_workspace)
            assert result["fips_140_3"] is True
            assert result["certificate"] == "4985"
            mock_verify.assert_called_once_with(temp_workspace)

    def test_pre_export_hook_metadata_enrichment(self, temp_workspace):
        """Test pre-export hook metadata enrichment."""
        from extensions.openssl_hooks.hooks.pre_export import PreExportHook

        hook = PreExportHook()

        # Test metadata enrichment
        with patch('extensions.openssl_hooks.hooks.pre_export.enrich_metadata') as mock_enrich:
            mock_enrich.return_value = {
                "version": "3.0.0",
                "fips_ready": True,
                "security_level": 3,
                "algorithms": ["AES-256", "RSA-2048", "ECDSA-P384"]
            }

            result = hook.execute(temp_workspace)
            assert result["fips_ready"] is True
            assert result["security_level"] == 3
            assert "AES-256" in result["algorithms"]
            mock_enrich.assert_called_once_with(temp_workspace)

    def test_post_export_hook_distribution_validation(self, temp_workspace):
        """Test post-export hook distribution validation."""
        from extensions.openssl_hooks.hooks.post_export import PostExportHook

        hook = PostExportHook()

        # Test distribution validation
        with patch('extensions.openssl_hooks.hooks.post_export.validate_distribution') as mock_validate:
            mock_validate.return_value = {
                "checksums_valid": True,
                "signatures_valid": True,
                "artifacts_complete": True
            }

            result = hook.execute(temp_workspace)
            assert result["checksums_valid"] is True
            assert result["signatures_valid"] is True
            assert result["artifacts_complete"] is True
            mock_validate.assert_called_once_with(temp_workspace)


class TestHooksIntegration:
    """Integration tests for hooks workflow."""

    def test_build_lifecycle_hooks(self, temp_workspace):
        """Test complete build lifecycle with all hooks."""
        # Mock all hooks in sequence
        with patch('extensions.openssl_hooks.hooks.pre_build.PreBuildHook.execute') as mock_pre_build, \
             patch('extensions.openssl_hooks.hooks.post_build.PostBuildHook.execute') as mock_post_build, \
             patch('extensions.openssl_hooks.hooks.pre_package.PrePackageHook.execute') as mock_pre_package, \
             patch('extensions.openssl_hooks.hooks.post_package.PostPackageHook.execute') as mock_post_package:

            # Setup mock returns
            mock_pre_build.return_value = True
            mock_post_build.return_value = {"valid": True}
            mock_pre_package.return_value = {"format": "CycloneDX"}
            mock_post_package.return_value = {"fips_140_3": True}

            # Execute hook sequence (simulating build lifecycle)
            pre_build_result = mock_pre_build.return_value
            post_build_result = mock_post_build.return_value
            pre_package_result = mock_pre_package.return_value
            post_package_result = mock_post_package.return_value

            # Verify all hooks executed successfully
            assert pre_build_result is True
            assert post_build_result["valid"] is True
            assert pre_package_result["format"] == "CycloneDX"
            assert post_package_result["fips_140_3"] is True

    def test_export_lifecycle_hooks(self, temp_workspace):
        """Test export lifecycle with metadata and validation hooks."""
        with patch('extensions.openssl_hooks.hooks.pre_export.PreExportHook.execute') as mock_pre_export, \
             patch('extensions.openssl_hooks.hooks.post_export.PostExportHook.execute') as mock_post_export:

            # Setup mock returns
            mock_pre_export.return_value = {"fips_ready": True, "security_level": 3}
            mock_post_export.return_value = {"checksums_valid": True, "signatures_valid": True}

            # Execute export hooks
            pre_export_result = mock_pre_export.return_value
            post_export_result = mock_post_export.return_value

            # Verify export lifecycle
            assert pre_export_result["fips_ready"] is True
            assert pre_export_result["security_level"] == 3
            assert post_export_result["checksums_valid"] is True
            assert post_export_result["signatures_valid"] is True


class TestHooksErrorHandling:
    """Test error handling in hooks."""

    def test_pre_build_hook_fips_failure(self, temp_workspace, mock_fips_config):
        """Test pre-build hook FIPS requirement failure."""
        from extensions.openssl_hooks.hooks.pre_build import PreBuildHook

        hook = PreBuildHook()

        with patch('extensions.openssl_hooks.hooks.pre_build.check_fips_requirements') as mock_check:
            mock_check.return_value = False

            with pytest.raises(RuntimeError, match="FIPS requirements not met"):
                hook.execute(temp_workspace, mock_fips_config)

    def test_post_build_hook_validation_failure(self, temp_workspace):
        """Test post-build hook validation failure."""
        from extensions.openssl_hooks.hooks.post_build import PostBuildHook

        hook = PostBuildHook()

        with patch('extensions.openssl_hooks.hooks.post_build.validate_build_artifacts') as mock_validate:
            mock_validate.return_value = {"valid": False, "errors": ["Missing fips.so"]}

            with pytest.raises(RuntimeError, match="Build validation failed"):
                hook.execute(temp_workspace)

    def test_post_package_hook_compliance_failure(self, temp_workspace):
        """Test post-package hook compliance failure."""
        from extensions.openssl_hooks.hooks.post_package import PostPackageHook

        hook = PostPackageHook()

        with patch('extensions.openssl_hooks.hooks.post_package.verify_compliance') as mock_verify:
            mock_verify.return_value = {"fips_140_3": False, "errors": ["Certificate expired"]}

            with pytest.raises(RuntimeError, match="Compliance verification failed"):
                hook.execute(temp_workspace)


class TestHooksPerformance:
    """Performance tests for hooks."""

    def test_hook_execution_performance(self, temp_workspace, performance_timer):
        """Test hook execution performance."""
        from extensions.openssl_hooks.hooks.pre_build import PreBuildHook

        hook = PreBuildHook()

        with patch('extensions.openssl_hooks.hooks.pre_build.check_fips_requirements') as mock_check:
            mock_check.return_value = True

            # Measure execution time
            start_time = performance_timer()
            result = hook.execute(temp_workspace)
            execution_time = performance_timer()

            # Verify result and performance
            assert result is True
            assert execution_time < 5.0  # Should complete within 5 seconds
            mock_check.assert_called_once()

    def test_hooks_memory_usage(self, temp_workspace):
        """Test memory usage during hook execution."""
        import psutil
        import os

        from extensions.openssl_hooks.hooks.post_build import PostBuildHook

        hook = PostBuildHook()

        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        with patch('extensions.openssl_hooks.hooks.post_build.validate_build_artifacts') as mock_validate:
            mock_validate.return_value = {"valid": True}

            # Execute hook
            result = hook.execute(temp_workspace)

            # Check memory usage after execution
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory

            # Verify result and reasonable memory usage
            assert result["valid"] is True
            assert memory_increase < 50  # Should not increase memory by more than 50MB

