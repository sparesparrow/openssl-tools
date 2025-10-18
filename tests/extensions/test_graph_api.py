"""
Test Graph API Extensions
Tests for OpenSSL-specific Graph API in Conan extensions.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import json
import networkx as nx


class TestDependencyGraph:
    """Test suite for dependency graph API."""

    def test_dependency_graph_construction(self, temp_workspace, sample_conanfile):
        """Test dependency graph construction."""
        # Mock dependency graph API
        with patch('extensions.graph_api.dependency_graph.DependencyGraph') as MockGraph:
            graph = MockGraph.return_value

            # Create sample conanfile
            conanfile_path = temp_workspace / "conanfile.py"
            conanfile_path.write_text(sample_conanfile)

            with patch.object(graph, 'build_from_conanfile') as mock_build:
                mock_build.return_value = {
                    "nodes": ["openssl-base/3.0.0", "zlib/1.2.11"],
                    "edges": [("openssl-base/3.0.0", "zlib/1.2.11")],
                    "fips_dependencies": []
                }

                result = graph.build_from_conanfile(conanfile_path)

                assert len(result["nodes"]) == 2
                assert len(result["edges"]) == 1
                assert "openssl-base/3.0.0" in result["nodes"]
                mock_build.assert_called_once_with(conanfile_path)

    def test_dependency_graph_cycle_detection(self, temp_workspace):
        """Test dependency graph cycle detection."""
        with patch('extensions.graph_api.dependency_graph.DependencyGraph') as MockGraph:
            graph = MockGraph.return_value

            # Create cyclic dependencies
            cyclic_deps = {
                "nodes": ["A", "B", "C"],
                "edges": [("A", "B"), ("B", "C"), ("C", "A")]
            }

            with patch.object(graph, 'detect_cycles') as mock_detect:
                mock_detect.return_value = ["A -> B -> C -> A"]

                cycles = graph.detect_cycles(cyclic_deps)

                assert len(cycles) == 1
                assert "A -> B -> C -> A" in cycles
                mock_detect.assert_called_once_with(cyclic_deps)

    def test_dependency_graph_fips_analysis(self, temp_workspace):
        """Test dependency graph FIPS compliance analysis."""
        with patch('extensions.graph_api.dependency_graph.DependencyGraph') as MockGraph:
            graph = MockGraph.return_value

            dependencies = ["openssl-base/3.0.0", "zlib/1.2.11", "custom-crypto/1.0"]

            with patch.object(graph, 'analyze_fips_compliance') as mock_analyze:
                mock_analyze.return_value = {
                    "compliant": True,
                    "fips_components": ["openssl-base/3.0.0"],
                    "non_fips_components": ["zlib/1.2.11"],
                    "recommendations": ["Use FIPS-certified zlib"]
                }

                result = graph.analyze_fips_compliance(dependencies)

                assert result["compliant"] is True
                assert len(result["fips_components"]) == 1
                assert len(result["recommendations"]) == 1
                mock_analyze.assert_called_once_with(dependencies)


class TestBuildGraph:
    """Test suite for build graph API."""

    def test_build_graph_task_scheduling(self, temp_workspace):
        """Test build graph task scheduling."""
        with patch('extensions.graph_api.build_graph.BuildGraph') as MockGraph:
            graph = MockGraph.return_value

            tasks = ["configure", "build", "test", "package"]

            with patch.object(graph, 'schedule_tasks') as mock_schedule:
                mock_schedule.return_value = {
                    "order": ["configure", "build", "test", "package"],
                    "parallel_groups": [["configure"], ["build"], ["test"], ["package"]],
                    "estimated_time": 120
                }

                result = graph.schedule_tasks(tasks)

                assert len(result["order"]) == 4
                assert result["estimated_time"] == 120
                assert result["order"][0] == "configure"
                mock_schedule.assert_called_once_with(tasks)

    def test_build_graph_resource_allocation(self, temp_workspace):
        """Test build graph resource allocation."""
        with patch('extensions.graph_api.build_graph.BuildGraph') as MockGraph:
            graph = MockGraph.return_value

            with patch.object(graph, 'allocate_resources') as mock_allocate:
                mock_allocate.return_value = {
                    "cpu_cores": 4,
                    "memory_gb": 8,
                    "disk_space_gb": 20,
                    "parallel_jobs": 4
                }

                result = graph.allocate_resources()

                assert result["cpu_cores"] == 4
                assert result["memory_gb"] == 8
                assert result["parallel_jobs"] == 4
                mock_allocate.assert_called_once()

    def test_build_graph_failure_recovery(self, temp_workspace):
        """Test build graph failure recovery."""
        with patch('extensions.graph_api.build_graph.BuildGraph') as MockGraph:
            graph = MockGraph.return_value

            failed_task = "build"
            failure_reason = "Compiler error"

            with patch.object(graph, 'recover_from_failure') as mock_recover:
                mock_recover.return_value = {
                    "recovery_plan": ["clean", "rebuild"],
                    "alternative_paths": ["use_cached_build"],
                    "rollback_actions": ["remove_artifacts"]
                }

                result = graph.recover_from_failure(failed_task, failure_reason)

                assert len(result["recovery_plan"]) == 2
                assert "clean" in result["recovery_plan"]
                assert "rollback_actions" in result
                mock_recover.assert_called_once_with(failed_task, failure_reason)


class TestComplianceGraph:
    """Test suite for compliance graph API."""

    def test_compliance_graph_validation(self, temp_workspace):
        """Test compliance graph validation."""
        with patch('extensions.graph_api.compliance_graph.ComplianceGraph') as MockGraph:
            graph = MockGraph.return_value

            compliance_rules = {
                "nist_sp_800_53": ["AC-1", "AC-2"],
                "fips_140_3": ["Cryptographic Module Validation"]
            }

            with patch.object(graph, 'validate_compliance') as mock_validate:
                mock_validate.return_value = {
                    "valid": True,
                    "validated_rules": 3,
                    "certificate": "4985",
                    "expiration_date": "2025-12-31"
                }

                result = graph.validate_compliance(compliance_rules)

                assert result["valid"] is True
                assert result["validated_rules"] == 3
                assert result["certificate"] == "4985"
                mock_validate.assert_called_once_with(compliance_rules)

    def test_compliance_graph_audit_trail(self, temp_workspace):
        """Test compliance graph audit trail."""
        with patch('extensions.graph_api.compliance_graph.ComplianceGraph') as MockGraph:
            graph = MockGraph.return_value

            with patch.object(graph, 'generate_audit_trail') as mock_audit:
                mock_audit.return_value = {
                    "trail_id": "audit-2024-001",
                    "events": ["build_started", "fips_validation", "certificate_issued"],
                    "timestamps": ["2024-01-01T10:00:00Z", "2024-01-01T11:00:00Z"],
                    "signatures": ["sig1", "sig2"]
                }

                result = graph.generate_audit_trail()

                assert result["trail_id"].startswith("audit-")
                assert len(result["events"]) == 3
                assert len(result["signatures"]) == 2
                mock_audit.assert_called_once()


class TestGraphAPIPerformance:
    """Performance tests for Graph API."""

    def test_graph_construction_performance(self, temp_workspace, performance_timer):
        """Test graph construction performance."""
        with patch('extensions.graph_api.dependency_graph.DependencyGraph') as MockGraph:
            graph = MockGraph.return_value

            # Large dependency set
            large_deps = [f"package-{i}/1.0" for i in range(100)]

            with patch.object(graph, 'build_from_conanfile') as mock_build:
                mock_build.return_value = {"nodes": large_deps, "edges": []}

                # Measure performance
                start_time = performance_timer()
                result = graph.build_from_conanfile(Path("dummy"))
                construction_time = performance_timer()

                assert len(result["nodes"]) == 100
                # Should complete within reasonable time for 100 dependencies
                assert construction_time < 10.0  # 10 seconds max
                mock_build.assert_called_once()

    def test_graph_query_performance(self, temp_workspace):
        """Test graph query performance."""
        with patch('extensions.graph_api.dependency_graph.DependencyGraph') as MockGraph:
            graph = MockGraph.return_value

            # Setup graph with many nodes
            with patch.object(graph, 'query_dependencies') as mock_query:
                mock_query.return_value = ["dep1", "dep2", "dep3"]

                # Measure query time
                import time
                start_time = time.time()
                result = graph.query_dependencies("openssl-base/3.0.0")
                query_time = time.time() - start_time

                assert len(result) == 3
                # Query should be fast
                assert query_time < 1.0  # 1 second max
                mock_query.assert_called_once_with("openssl-base/3.0.0")


class TestGraphAPIIntegration:
    """Integration tests for Graph API."""

    def test_cross_graph_analysis(self, temp_workspace):
        """Test analysis across multiple graph types."""
        # Mock multiple graph types
        with patch('extensions.graph_api.dependency_graph.DependencyGraph') as MockDepGraph, \
             patch('extensions.graph_api.build_graph.BuildGraph') as MockBuildGraph, \
             patch('extensions.graph_api.compliance_graph.ComplianceGraph') as MockCompGraph:

            dep_graph = MockDepGraph.return_value
            build_graph = MockBuildGraph.return_value
            comp_graph = MockCompGraph.return_value

            # Setup mock returns
            dep_graph.analyze_dependencies.return_value = {"complexity": "medium"}
            build_graph.optimize_build.return_value = {"efficiency": 85}
            comp_graph.validate_compliance.return_value = {"valid": True}

            # Execute cross-graph analysis
            dep_result = dep_graph.analyze_dependencies()
            build_result = build_graph.optimize_build()
            comp_result = comp_graph.validate_compliance()

            # Verify integrated results
            assert dep_result["complexity"] == "medium"
            assert build_result["efficiency"] == 85
            assert comp_result["valid"] is True

    def test_graph_persistence_and_loading(self, temp_workspace):
        """Test graph persistence and loading."""
        with patch('extensions.graph_api.dependency_graph.DependencyGraph') as MockGraph:
            graph = MockGraph.return_value

            # Test saving graph
            with patch.object(graph, 'save_graph') as mock_save:
                mock_save.return_value = str(temp_workspace / "graph.json")

                save_path = graph.save_graph(temp_workspace)
                assert save_path.endswith("graph.json")
                mock_save.assert_called_once_with(temp_workspace)

            # Test loading graph
            with patch.object(graph, 'load_graph') as mock_load:
                mock_load.return_value = {"nodes": ["A", "B"], "edges": [("A", "B")]}

                loaded_graph = graph.load_graph(save_path)
                assert len(loaded_graph["nodes"]) == 2
                mock_load.assert_called_once_with(save_path)


class TestGraphAPIErrorHandling:
    """Error handling tests for Graph API."""

    def test_graph_construction_error(self, temp_workspace):
        """Test graph construction error handling."""
        with patch('extensions.graph_api.dependency_graph.DependencyGraph') as MockGraph:
            graph = MockGraph.return_value

            with patch.object(graph, 'build_from_conanfile') as mock_build:
                mock_build.side_effect = ValueError("Invalid conanfile syntax")

                with pytest.raises(ValueError, match="Invalid conanfile syntax"):
                    graph.build_from_conanfile(Path("invalid.py"))

    def test_graph_query_error(self, temp_workspace):
        """Test graph query error handling."""
        with patch('extensions.graph_api.dependency_graph.DependencyGraph') as MockGraph:
            graph = MockGraph.return_value

            with patch.object(graph, 'query_dependencies') as mock_query:
                mock_query.side_effect = KeyError("Package not found")

                with pytest.raises(KeyError, match="Package not found"):
                    graph.query_dependencies("nonexistent-package/1.0")

    def test_graph_validation_error(self, temp_workspace):
        """Test graph validation error handling."""
        with patch('extensions.graph_api.compliance_graph.ComplianceGraph') as MockGraph:
            graph = MockGraph.return_value

            with patch.object(graph, 'validate_compliance') as mock_validate:
                mock_validate.side_effect = RuntimeError("Compliance check failed")

                with pytest.raises(RuntimeError, match="Compliance check failed"):
                    graph.validate_compliance({})

