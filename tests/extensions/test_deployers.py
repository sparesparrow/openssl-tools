"""
Test Conan Deployers Extensions
Tests for OpenSSL-specific deployers in Conan extensions.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import json


class TestCursorDeployer:
    """Test suite for Cursor deployer."""

    def test_cursor_deployer_initialization(self, temp_workspace):
        """Test Cursor deployer initialization."""
        from mcp_project_orchestrator.cursor_deployer import CursorDeployer

        deployer = CursorDeployer()

        # Test initialization
        assert deployer.name == "cursor"
        assert hasattr(deployer, 'deploy')
        assert hasattr(deployer, 'validate_deployment')

    def test_cursor_deployer_deployment(self, temp_workspace):
        """Test Cursor deployer deployment functionality."""
        from mcp_project_orchestrator.cursor_deployer import CursorDeployer

        deployer = CursorDeployer()

        # Mock deployment configuration
        config = {
            "workspace_path": str(temp_workspace),
            "cursor_config": {
                "rules": ["ddd-rules.mdc"],
                "templates": ["openssl-template.json"],
                "extensions": ["openssl-tools"]
            }
        }

        with patch('mcp_project_orchestrator.cursor_deployer.deploy_cursor_config') as mock_deploy:
            mock_deploy.return_value = {
                "status": "success",
                "files_deployed": ["rules.mdc", "templates.json"],
                "extensions_installed": ["openssl-tools"]
            }

            result = deployer.deploy(config)

            assert result["status"] == "success"
            assert len(result["files_deployed"]) == 2
            assert "openssl-tools" in result["extensions_installed"]
            mock_deploy.assert_called_once_with(config)

    def test_cursor_deployer_validation(self, temp_workspace):
        """Test Cursor deployer validation."""
        from mcp_project_orchestrator.cursor_deployer import CursorDeployer

        deployer = CursorDeployer()

        with patch('mcp_project_orchestrator.cursor_deployer.validate_cursor_setup') as mock_validate:
            mock_validate.return_value = {
                "valid": True,
                "rules_loaded": 5,
                "templates_available": 3,
                "extensions_active": ["openssl-tools", "mcp-orchestrator"]
            }

            result = deployer.validate_deployment(temp_workspace)

            assert result["valid"] is True
            assert result["rules_loaded"] == 5
            assert len(result["extensions_active"]) == 2
            mock_validate.assert_called_once_with(temp_workspace)

    def test_cursor_deployer_error_handling(self, temp_workspace):
        """Test Cursor deployer error handling."""
        from mcp_project_orchestrator.cursor_deployer import CursorDeployer

        deployer = CursorDeployer()

        # Test deployment failure
        with patch('mcp_project_orchestrator.cursor_deployer.deploy_cursor_config') as mock_deploy:
            mock_deploy.side_effect = RuntimeError("Deployment failed")

            with pytest.raises(RuntimeError, match="Deployment failed"):
                config = {"workspace_path": str(temp_workspace)}
                deployer.deploy(config)


class TestDevelopmentDeployer:
    """Test suite for development environment deployer."""

    def test_development_deployer_setup(self, temp_workspace):
        """Test development deployer environment setup."""
        # Mock development deployer (assuming it exists)
        with patch('extensions.deployers.development.DevelopmentDeployer') as MockDeployer:
            deployer = MockDeployer.return_value

            config = {
                "python_version": "3.9",
                "venv_path": str(temp_workspace / ".venv"),
                "requirements": ["conan", "pytest", "black"]
            }

            with patch.object(deployer, 'setup_environment') as mock_setup:
                mock_setup.return_value = {
                    "status": "success",
                    "python_version": "3.9.7",
                    "packages_installed": 15
                }

                result = deployer.setup_environment(config)

                assert result["status"] == "success"
                assert result["python_version"].startswith("3.9")
                mock_setup.assert_called_once_with(config)

    def test_development_deployer_validation(self, temp_workspace):
        """Test development deployer validation."""
        with patch('extensions.deployers.development.DevelopmentDeployer') as MockDeployer:
            deployer = MockDeployer.return_value

            with patch.object(deployer, 'validate_environment') as mock_validate:
                mock_validate.return_value = {
                    "valid": True,
                    "conan_version": "2.0.5",
                    "cmake_version": "3.25.0",
                    "openssl_available": True
                }

                result = deployer.validate_environment(temp_workspace)

                assert result["valid"] is True
                assert "conan_version" in result
                assert result["openssl_available"] is True
                mock_validate.assert_called_once_with(temp_workspace)


class TestProductionDeployer:
    """Test suite for production deployment deployer."""

    def test_production_deployer_build(self, temp_workspace):
        """Test production deployer build process."""
        with patch('extensions.deployers.production.ProductionDeployer') as MockDeployer:
            deployer = MockDeployer.return_value

            config = {
                "build_type": "Release",
                "fips_enabled": True,
                "optimization_level": "O3"
            }

            with patch.object(deployer, 'build_production') as mock_build:
                mock_build.return_value = {
                    "status": "success",
                    "artifacts": ["openssl-3.0.0.tar.gz", "fips.so"],
                    "fips_certified": True
                }

                result = deployer.build_production(temp_workspace, config)

                assert result["status"] == "success"
                assert len(result["artifacts"]) == 2
                assert result["fips_certified"] is True
                mock_build.assert_called_once_with(temp_workspace, config)

    def test_production_deployer_distribution(self, temp_workspace):
        """Test production deployer distribution."""
        with patch('extensions.deployers.production.ProductionDeployer') as MockDeployer:
            deployer = MockDeployer.return_value

            with patch.object(deployer, 'create_distribution') as mock_distribute:
                mock_distribute.return_value = {
                    "status": "success",
                    "distribution_id": "openssl-3.0.0-prod-001",
                    "checksums": {"sha256": "abc123...", "md5": "def456..."}
                }

                result = deployer.create_distribution(temp_workspace)

                assert result["status"] == "success"
                assert "distribution_id" in result
                assert "checksums" in result
                mock_distribute.assert_called_once_with(temp_workspace)


class TestDeployersIntegration:
    """Integration tests for deployers."""

    def test_full_deployment_pipeline(self, temp_workspace):
        """Test complete deployment pipeline across all deployers."""
        # Mock all deployers
        with patch('mcp_project_orchestrator.cursor_deployer.CursorDeployer') as MockCursor, \
             patch('extensions.deployers.development.DevelopmentDeployer') as MockDev, \
             patch('extensions.deployers.production.ProductionDeployer') as MockProd:

            cursor_deployer = MockCursor.return_value
            dev_deployer = MockDev.return_value
            prod_deployer = MockProd.return_value

            # Setup mock returns for pipeline
            cursor_deployer.deploy.return_value = {"status": "success"}
            dev_deployer.setup_environment.return_value = {"status": "success"}
            prod_deployer.build_production.return_value = {"status": "success"}

            # Execute deployment pipeline
            cursor_result = cursor_deployer.deploy({"workspace_path": str(temp_workspace)})
            dev_result = dev_deployer.setup_environment({"python_version": "3.9"})
            prod_result = prod_deployer.build_production(temp_workspace, {"fips_enabled": True})

            # Verify pipeline completion
            assert cursor_result["status"] == "success"
            assert dev_result["status"] == "success"
            assert prod_result["status"] == "success"

    def test_deployer_rollback_procedures(self, temp_workspace):
        """Test deployer rollback procedures."""
        from mcp_project_orchestrator.cursor_deployer import CursorDeployer

        deployer = CursorDeployer()

        # Test successful rollback
        with patch.object(deployer, 'rollback_deployment') as mock_rollback:
            mock_rollback.return_value = {
                "status": "rolled_back",
                "files_removed": ["config.mdc", "template.json"],
                "extensions_uninstalled": ["openssl-tools"]
            }

            result = deployer.rollback_deployment(temp_workspace)

            assert result["status"] == "rolled_back"
            assert len(result["files_removed"]) == 2
            mock_rollback.assert_called_once_with(temp_workspace)

    def test_deployer_health_checks(self, temp_workspace):
        """Test deployer health checks."""
        with patch('extensions.deployers.development.DevelopmentDeployer') as MockDeployer:
            deployer = MockDeployer.return_value

            with patch.object(deployer, 'health_check') as mock_health:
                mock_health.return_value = {
                    "status": "healthy",
                    "checks": {
                        "python": "ok",
                        "conan": "ok",
                        "cmake": "ok",
                        "openssl": "ok"
                    }
                }

                result = deployer.health_check(temp_workspace)

                assert result["status"] == "healthy"
                assert all(status == "ok" for status in result["checks"].values())
                mock_health.assert_called_once_with(temp_workspace)


class TestDeployersPerformance:
    """Performance tests for deployers."""

    def test_deployer_execution_performance(self, temp_workspace, performance_timer):
        """Test deployer execution performance."""
        from mcp_project_orchestrator.cursor_deployer import CursorDeployer

        deployer = CursorDeployer()

        with patch.object(deployer, 'deploy') as mock_deploy:
            mock_deploy.return_value = {"status": "success"}

            # Measure deployment time
            start_time = performance_timer()
            result = deployer.deploy({"workspace_path": str(temp_workspace)})
            execution_time = performance_timer()

            assert result["status"] == "success"
            # Deployment should complete within reasonable time
            assert execution_time < 30.0  # 30 seconds max
            mock_deploy.assert_called_once()

    def test_deployer_resource_usage(self, temp_workspace):
        """Test deployer resource usage."""
        import psutil
        import os

        from mcp_project_orchestrator.cursor_deployer import CursorDeployer

        deployer = CursorDeployer()

        # Get initial resource usage
        process = psutil.Process(os.getpid())
        initial_cpu = process.cpu_percent()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        with patch.object(deployer, 'validate_deployment') as mock_validate:
            mock_validate.return_value = {"valid": True}

            # Execute validation
            result = deployer.validate_deployment(temp_workspace)

            # Check resource usage
            final_cpu = process.cpu_percent()
            final_memory = process.memory_info().rss / 1024 / 1024  # MB

            assert result["valid"] is True
            # Resource usage should be reasonable
            assert final_memory - initial_memory < 100  # Less than 100MB increase
            mock_validate.assert_called_once_with(temp_workspace)

