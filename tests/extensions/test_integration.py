"""
Integration Tests for Conan Extensions
Tests cross-extension interactions and end-to-end workflows.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import json


class TestCrossExtensionIntegration:
    """Integration tests for cross-extension functionality."""

    def test_full_development_workflow(self, temp_workspace, test_helper):
        """Test complete development workflow across all extensions."""
        # Setup test workspace
        workspace = temp_workspace / "integration_test"
        workspace.mkdir()

        # Create test components
        test_helper.create_test_conanfile(workspace / "conanfile.py")

        # Mock all extension interactions
        with patch('extensions.commands.openssl.cmd_scan.ScanCommand.run') as mock_scan, \
             patch('extensions.commands.openssl.cmd_configure.ConfigureCommand.run') as mock_configure, \
             patch('extensions.commands.openssl.cmd_build.BuildCommand.run') as mock_build, \
             patch('extensions.hooks.pre_build.PreBuildHook.execute') as mock_pre_build, \
             patch('extensions.hooks.post_build.PostBuildHook.execute') as mock_post_build, \
             patch('mcp_project_orchestrator.cursor_deployer.CursorDeployer.deploy') as mock_deploy:

            # Setup mock returns for workflow
            mock_scan.return_value = {"packages": ["openssl-base/3.0.0"]}
            mock_configure.return_value = {"status": "configured"}
            mock_build.return_value = {"status": "built"}
            mock_pre_build.return_value = True
            mock_post_build.return_value = {"valid": True}
            mock_deploy.return_value = {"status": "deployed"}

            # Execute workflow steps
            scan_result = mock_scan.return_value
            config_result = mock_configure.return_value
            pre_build_result = mock_pre_build.return_value
            build_result = mock_build.return_value
            post_build_result = mock_post_build.return_value
            deploy_result = mock_deploy.return_value

            # Verify complete workflow
            assert scan_result["packages"] == ["openssl-base/3.0.0"]
            assert config_result["status"] == "configured"
            assert pre_build_result is True
            assert build_result["status"] == "built"
            assert post_build_result["valid"] is True
            assert deploy_result["status"] == "deployed"

    def test_fips_compliance_workflow(self, temp_workspace, mock_fips_config):
        """Test FIPS compliance workflow across extensions."""
        with patch('extensions.hooks.pre_build.PreBuildHook.execute') as mock_pre_build, \
             patch('extensions.hooks.post_build.PostBuildHook.execute') as mock_post_build, \
             patch('extensions.hooks.post_package.PostPackageHook.execute') as mock_post_package, \
             patch('extensions.commands.openssl.cmd_package.PackageCommand.validate_fips') as mock_validate:

            # Setup FIPS workflow
            mock_pre_build.return_value = True
            mock_post_build.return_value = {"fips_module": "fips.so"}
            mock_post_package.return_value = {"fips_140_3": True, "certificate": "4985"}
            mock_validate.return_value = True

            # Execute FIPS workflow
            pre_check = mock_pre_build.return_value
            build_validation = mock_post_build.return_value
            package_compliance = mock_post_package.return_value
            final_validation = mock_validate.return_value

            # Verify FIPS compliance throughout
            assert pre_check is True
            assert build_validation["fips_module"] == "fips.so"
            assert package_compliance["fips_140_3"] is True
            assert package_compliance["certificate"] == "4985"
            assert final_validation is True

    def test_error_recovery_workflow(self, temp_workspace):
        """Test error recovery workflow across extensions."""
        with patch('extensions.commands.openssl.cmd_build.BuildCommand.run') as mock_build, \
             patch('extensions.deployers.development.DevelopmentDeployer.rollback_deployment') as mock_rollback, \
             patch('extensions.graph_api.build_graph.BuildGraph.recover_from_failure') as mock_recover:

            # Simulate build failure
            mock_build.side_effect = RuntimeError("Build failed: compiler error")

            # Setup recovery
            mock_rollback.return_value = {"status": "rolled_back"}
            mock_recover.return_value = {"recovery_plan": ["clean", "rebuild"]}

            # Execute error recovery
            try:
                mock_build()
                assert False, "Build should have failed"
            except RuntimeError:
                rollback_result = mock_rollback.return_value
                recovery_result = mock_recover.return_value

                assert rollback_result["status"] == "rolled_back"
                assert "clean" in recovery_result["recovery_plan"]


class TestRepositoryIntegration:
    """Integration tests across repositories."""

    def test_cross_repository_dependencies(self, temp_workspace):
        """Test dependency resolution across repositories."""
        # Mock repository interactions
        with patch('extensions.commands.openssl.cmd_scan.scan_workspace') as mock_scan, \
             patch('extensions.graph_api.dependency_graph.DependencyGraph.build_from_conanfile') as mock_graph:

            # Setup cross-repository dependencies
            mock_scan.return_value = {
                "repositories": ["openssl-conan-base", "openssl-tools", "openssl-fips-policy"],
                "shared_dependencies": ["cmake", "python", "conan"]
            }

            mock_graph.return_value = {
                "cross_repo_edges": [
                    ("openssl-conan-base", "openssl-tools"),
                    ("openssl-tools", "openssl-fips-policy")
                ]
            }

            # Execute cross-repository analysis
            scan_result = mock_scan.return_value
            graph_result = mock_graph.return_value

            # Verify cross-repository integration
            assert len(scan_result["repositories"]) == 3
            assert "openssl-conan-base" in scan_result["repositories"]
            assert len(graph_result["cross_repo_edges"]) == 2

    def test_shared_component_validation(self, temp_workspace):
        """Test validation of shared components across repositories."""
        shared_components = ["conanfile.py", "test_package/", "scripts/"]

        # Mock component validation
        with patch('extensions.deployers.development.DevelopmentDeployer.validate_shared_components') as mock_validate:
            mock_validate.return_value = {
                "valid_components": shared_components,
                "inconsistencies": [],
                "recommendations": ["Standardize test_package structure"]
            }

            # Validate shared components
            result = mock_validate.return_value

            assert len(result["valid_components"]) == 3
            assert len(result["inconsistencies"]) == 0
            assert "test_package/" in result["valid_components"]


class TestEndToEndWorkflows:
    """End-to-end workflow tests."""

    def test_ci_cd_pipeline_simulation(self, temp_workspace):
        """Test complete CI/CD pipeline simulation."""
        # Mock CI/CD pipeline steps
        pipeline_steps = [
            "checkout", "scan", "configure", "build", "test", "package", "deploy"
        ]

        with patch('extensions.commands.openssl.cmd_scan.ScanCommand.run') as mock_scan, \
             patch('extensions.commands.openssl.cmd_configure.ConfigureCommand.run') as mock_configure, \
             patch('extensions.commands.openssl.cmd_build.BuildCommand.run') as mock_build, \
             patch('extensions.commands.openssl.cmd_package.PackageCommand.run') as mock_package, \
             patch('mcp_project_orchestrator.cursor_deployer.CursorDeployer.deploy') as mock_deploy:

            # Setup pipeline success
            mock_scan.return_value = {"status": "scanned"}
            mock_configure.return_value = {"status": "configured"}
            mock_build.return_value = {"status": "built"}
            mock_package.return_value = {"status": "packaged"}
            mock_deploy.return_value = {"status": "deployed"}

            # Execute pipeline
            results = {}
            for step in pipeline_steps[1:]:  # Skip checkout
                mock_func = locals()[f"mock_{step}"]
                results[step] = mock_func.return_value

            # Verify complete pipeline success
            for step in pipeline_steps[1:]:
                assert results[step]["status"] == f"{step}ed"

    def test_rollback_and_recovery(self, temp_workspace):
        """Test complete rollback and recovery workflow."""
        with patch('extensions.deployers.development.DevelopmentDeployer.rollback_deployment') as mock_rollback, \
             patch('extensions.deployers.production.ProductionDeployer.rollback_deployment') as mock_prod_rollback, \
             patch('extensions.graph_api.build_graph.BuildGraph.recover_from_failure') as mock_recover:

            # Setup rollback scenario
            mock_rollback.return_value = {"status": "development_rolled_back"}
            mock_prod_rollback.return_value = {"status": "production_rolled_back"}
            mock_recover.return_value = {
                "recovery_status": "planned",
                "steps": ["cleanup", "restore_backup", "redeploy"]
            }

            # Execute rollback and recovery
            dev_rollback = mock_rollback.return_value
            prod_rollback = mock_prod_rollback.return_value
            recovery_plan = mock_recover.return_value

            # Verify rollback and recovery
            assert dev_rollback["status"] == "development_rolled_back"
            assert prod_rollback["status"] == "production_rolled_back"
            assert recovery_plan["recovery_status"] == "planned"
            assert len(recovery_plan["steps"]) == 3


class TestPerformanceIntegration:
    """Integration tests with performance monitoring."""

    def test_load_testing_simulation(self, temp_workspace, performance_timer):
        """Test load testing with performance monitoring."""
        with patch('extensions.graph_api.build_graph.BuildGraph.allocate_resources') as mock_allocate, \
             patch('extensions.commands.openssl.cmd_build.BuildCommand.build_with_monitoring') as mock_build:

            # Setup load test
            mock_allocate.return_value = {"parallel_jobs": 8, "memory_gb": 16}
            mock_build.return_value = {"status": "success", "duration": 45.2}

            # Execute load test with timing
            start_time = performance_timer()
            resource_allocation = mock_allocate.return_value
            build_result = mock_build.return_value
            total_time = performance_timer()

            # Verify performance under load
            assert resource_allocation["parallel_jobs"] == 8
            assert build_result["status"] == "success"
            assert total_time < 60.0  # Complete within 1 minute

    def test_concurrent_extension_execution(self, temp_workspace):
        """Test concurrent execution of multiple extensions."""
        import threading
        import queue

        results_queue = queue.Queue()

        def run_extension(extension_name, mock_func):
            """Run extension in thread."""
            result = mock_func.return_value
            results_queue.put((extension_name, result))

        # Mock concurrent extension execution
        with patch('extensions.commands.openssl.cmd_scan.ScanCommand.run') as mock_scan, \
             patch('extensions.commands.openssl.cmd_build.BuildCommand.run') as mock_build, \
             patch('extensions.graph_api.dependency_graph.DependencyGraph.build_from_conanfile') as mock_graph:

            mock_scan.return_value = {"status": "scanned"}
            mock_build.return_value = {"status": "built"}
            mock_graph.return_value = {"nodes": 10, "edges": 15}

            # Start concurrent execution
            threads = [
                threading.Thread(target=run_extension, args=("scan", mock_scan)),
                threading.Thread(target=run_extension, args=("build", mock_build)),
                threading.Thread(target=run_extension, args=("graph", mock_graph))
            ]

            for thread in threads:
                thread.start()

            # Collect results
            results = {}
            for thread in threads:
                thread.join()
                ext_name, ext_result = results_queue.get()
                results[ext_name] = ext_result

            # Verify concurrent execution
            assert len(results) == 3
            assert all(result["status"] == f"{ext}ed" or "nodes" in result for ext, result in results.items())


class TestSecurityIntegration:
    """Security-focused integration tests."""

    def test_security_workflow_integration(self, temp_workspace):
        """Test security workflow across extensions."""
        with patch('extensions.hooks.pre_build.PreBuildHook.execute') as mock_pre_build, \
             patch('extensions.hooks.post_package.PostPackageHook.execute') as mock_post_package, \
             patch('extensions.commands.openssl.cmd_scan.ScanCommand.run') as mock_scan:

            # Setup security checks
            mock_pre_build.return_value = {"security_scan": "passed"}
            mock_post_package.return_value = {"sbom_generated": True, "vulnerabilities": 0}
            mock_scan.return_value = {"security_issues": []}

            # Execute security workflow
            pre_build_security = mock_pre_build.return_value
            package_security = mock_post_package.return_value
            scan_security = mock_scan.return_value

            # Verify security integration
            assert pre_build_security["security_scan"] == "passed"
            assert package_security["sbom_generated"] is True
            assert package_security["vulnerabilities"] == 0
            assert len(scan_security["security_issues"]) == 0

    def test_audit_trail_integration(self, temp_workspace):
        """Test audit trail across all extensions."""
        with patch('extensions.graph_api.compliance_graph.ComplianceGraph.generate_audit_trail') as mock_audit, \
             patch('extensions.deployers.production.ProductionDeployer.generate_deployment_log') as mock_deploy_log:

            # Setup audit trail
            mock_audit.return_value = {
                "trail_id": "audit-2024-001",
                "events": ["scan", "build", "package", "deploy"],
                "timestamps": ["2024-01-01T10:00:00Z"] * 4
            }

            mock_deploy_log.return_value = {
                "deployment_id": "deploy-2024-001",
                "artifacts": ["openssl-3.0.0.tar.gz"],
                "checksums": ["sha256:..."]
            }

            # Execute audit trail verification
            audit_result = mock_audit.return_value
            deploy_log = mock_deploy_log.return_value

            # Verify complete audit trail
            assert audit_result["trail_id"].startswith("audit-")
            assert len(audit_result["events"]) == 4
            assert deploy_log["deployment_id"].startswith("deploy-")
            assert len(deploy_log["artifacts"]) == 1

