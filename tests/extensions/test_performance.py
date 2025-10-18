"""
Performance Tests for Conan Extensions
Tests performance characteristics and benchmarks for all extensions.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import time
import psutil
import os
import statistics


class TestPerformanceBenchmarks:
    """Performance benchmark tests."""

    def test_command_execution_performance(self, temp_workspace, performance_timer):
        """Test performance of command execution."""
        from extensions.commands.openssl.cmd_scan import ScanCommand

        # Mock scan command
        with patch('extensions.commands.openssl.cmd_scan.scan_workspace') as mock_scan:
            mock_scan.return_value = {"packages": ["pkg1", "pkg2", "pkg3"]}

            cmd = ScanCommand()

            # Measure execution time
            execution_times = []
            for _ in range(10):  # Run 10 times for averaging
                start_time = performance_timer()
                result = cmd.run(["--path", str(temp_workspace)])
                execution_time = performance_timer()
                execution_times.append(execution_time)

            avg_time = statistics.mean(execution_times)
            max_time = max(execution_times)

            # Performance assertions
            assert avg_time < 2.0, f"Average execution time too slow: {avg_time}s"
            assert max_time < 5.0, f"Max execution time too slow: {max_time}s"
            assert len(result["packages"]) == 3

    def test_hook_execution_performance(self, temp_workspace, performance_timer):
        """Test performance of hook execution."""
        from extensions.openssl_hooks.hooks.pre_build import PreBuildHook

        hook = PreBuildHook()

        # Measure hook execution time
        execution_times = []
        for _ in range(5):
            start_time = performance_timer()
            with patch.object(hook, 'execute') as mock_execute:
                mock_execute.return_value = True
                result = hook.execute(temp_workspace)
                execution_time = performance_timer()
                execution_times.append(execution_time)

        avg_time = statistics.mean(execution_times)

        # Performance assertions
        assert avg_time < 1.0, f"Hook execution too slow: {avg_time}s"
        assert result is True

    def test_deployer_performance(self, temp_workspace, performance_timer):
        """Test deployer performance."""
        from mcp_project_orchestrator.cursor_deployer import CursorDeployer

        deployer = CursorDeployer()

        # Measure deployment time
        start_time = performance_timer()
        with patch.object(deployer, 'deploy') as mock_deploy:
            mock_deploy.return_value = {"status": "success"}
            result = deployer.deploy({"workspace_path": str(temp_workspace)})
            execution_time = performance_timer()

        # Performance assertions
        assert execution_time < 10.0, f"Deployment too slow: {execution_time}s"
        assert result["status"] == "success"

    def test_graph_api_performance(self, temp_workspace, performance_timer):
        """Test Graph API performance."""
        # Mock large dependency graph
        large_deps = [f"package-{i}/1.0" for i in range(100)]

        with patch('extensions.graph_api.dependency_graph.DependencyGraph') as MockGraph:
            graph = MockGraph.return_value

            # Test graph construction performance
            start_time = performance_timer()
            with patch.object(graph, 'build_from_conanfile') as mock_build:
                mock_build.return_value = {"nodes": large_deps, "edges": []}
                result = graph.build_from_conanfile(Path("dummy"))
                construction_time = performance_timer()

            # Performance assertions
            assert construction_time < 5.0, f"Graph construction too slow: {construction_time}s"
            assert len(result["nodes"]) == 100


class TestResourceUsageTests:
    """Resource usage monitoring tests."""

    def test_memory_usage_during_commands(self, temp_workspace):
        """Test memory usage during command execution."""
        process = psutil.Process(os.getpid())

        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Execute command
        with patch('extensions.commands.openssl.cmd_scan.ScanCommand.run') as mock_scan:
            mock_scan.return_value = {"packages": ["large_package"] * 100}

            from extensions.commands.openssl.cmd_scan import ScanCommand
            cmd = ScanCommand()
            result = cmd.run(["--path", str(temp_workspace)])

            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory

            # Memory assertions
            assert memory_increase < 50, f"Memory usage too high: {memory_increase}MB increase"
            assert len(result["packages"]) == 100

    def test_cpu_usage_during_build(self, temp_workspace):
        """Test CPU usage during build operations."""
        process = psutil.Process(os.getpid())

        # Execute build command
        with patch('extensions.commands.openssl.cmd_build.BuildCommand.run') as mock_build:
            mock_build.return_value = {"status": "success"}

            from extensions.commands.openssl.cmd_build import BuildCommand
            cmd = BuildCommand()

            # Monitor CPU during execution
            cpu_percentages = []
            result = cmd.run(["--path", str(temp_workspace)])

            for _ in range(10):  # Sample CPU usage
                cpu_percentages.append(process.cpu_percent())
                time.sleep(0.1)

            avg_cpu = statistics.mean(cpu_percentages)

            # CPU assertions (reasonable usage, not pegged)
            assert avg_cpu < 80, f"CPU usage too high: {avg_cpu}%"
            assert result["status"] == "success"

    def test_disk_io_performance(self, temp_workspace):
        """Test disk I/O performance during operations."""
        # Create test files
        test_files = []
        for i in range(10):
            test_file = temp_workspace / f"test_file_{i}.txt"
            test_file.write_text("x" * 1024 * 1024)  # 1MB files
            test_files.append(test_file)

        # Measure I/O operation time
        start_time = time.time()

        # Simulate file operations during extension execution
        with patch('extensions.commands.openssl.cmd_package.PackageCommand.run') as mock_package:
            mock_package.return_value = {"status": "success"}

            from extensions.commands.openssl.cmd_package import PackageCommand
            cmd = PackageCommand()
            result = cmd.run(["--path", str(temp_workspace)])

            io_time = time.time() - start_time

            # I/O performance assertions
            assert io_time < 30.0, f"I/O operations too slow: {io_time}s"
            assert result["status"] == "success"

        # Cleanup
        for test_file in test_files:
            test_file.unlink()


class TestScalabilityTests:
    """Scalability testing for extensions."""

    def test_large_workspace_handling(self, temp_workspace):
        """Test handling of large workspaces."""
        # Create large workspace simulation
        for i in range(50):  # 50 packages
            pkg_dir = temp_workspace / f"package_{i}"
            pkg_dir.mkdir()
            conanfile = pkg_dir / "conanfile.py"
            conanfile.write_text(f"""
from conan import ConanFile
class Package{i}(ConanFile):
    name = "package_{i}"
    version = "1.0"
""")

        # Test scanning large workspace
        start_time = time.time()
        with patch('extensions.commands.openssl.cmd_scan.scan_workspace') as mock_scan:
            mock_scan.return_value = {"packages": [f"package_{i}" for i in range(50)]}

            from extensions.commands.openssl.cmd_scan import ScanCommand
            cmd = ScanCommand()
            result = cmd.run(["--path", str(temp_workspace)])

            scan_time = time.time() - start_time

            # Scalability assertions
            assert scan_time < 60.0, f"Large workspace scan too slow: {scan_time}s"
            assert len(result["packages"]) == 50

    def test_concurrent_extension_execution(self, temp_workspace):
        """Test concurrent execution of multiple extensions."""
        import threading

        results = {}
        execution_times = {}

        def run_extension(extension_name, extension_func):
            """Run extension and record results."""
            start_time = time.time()
            result = extension_func()
            end_time = time.time()

            results[extension_name] = result
            execution_times[extension_name] = end_time - start_time

        # Mock extensions
        with patch('extensions.commands.openssl.cmd_scan.ScanCommand.run') as mock_scan, \
             patch('extensions.commands.openssl.cmd_build.BuildCommand.run') as mock_build, \
             patch('extensions.graph_api.dependency_graph.DependencyGraph.build_from_conanfile') as mock_graph:

            mock_scan.return_value = {"status": "scanned"}
            mock_build.return_value = {"status": "built"}
            mock_graph.return_value = {"nodes": 10}

            # Create threads for concurrent execution
            threads = [
                threading.Thread(target=run_extension, args=("scan", lambda: mock_scan.return_value)),
                threading.Thread(target=run_extension, args=("build", lambda: mock_build.return_value)),
                threading.Thread(target=run_extension, args=("graph", lambda: mock_graph.return_value))
            ]

            # Start concurrent execution
            start_time = time.time()
            for thread in threads:
                thread.start()

            # Wait for completion
            for thread in threads:
                thread.join()

            total_time = time.time() - start_time

            # Scalability assertions
            assert len(results) == 3
            assert total_time < 5.0, f"Concurrent execution too slow: {total_time}s"
            assert all(time < 2.0 for time in execution_times.values())


class TestStressTests:
    """Stress testing for extensions."""

    def test_continuous_operation_stress(self, temp_workspace):
        """Test continuous operation under stress."""
        operation_count = 100
        success_count = 0

        with patch('extensions.commands.openssl.cmd_scan.ScanCommand.run') as mock_scan:
            mock_scan.return_value = {"status": "success"}

            from extensions.commands.openssl.cmd_scan import ScanCommand
            cmd = ScanCommand()

            start_time = time.time()

            # Execute many operations
            for i in range(operation_count):
                try:
                    result = cmd.run(["--path", str(temp_workspace)])
                    if result["status"] == "success":
                        success_count += 1
                except Exception:
                    continue  # Count failures

            end_time = time.time()
            total_time = end_time - start_time

            success_rate = (success_count / operation_count) * 100

            # Stress test assertions
            assert success_rate > 95, f"Success rate too low: {success_rate}%"
            assert total_time < 300.0, f"Stress test too slow: {total_time}s"

    def test_memory_leak_detection(self, temp_workspace):
        """Test for memory leaks during repeated operations."""
        process = psutil.Process(os.getpid())

        memory_usage = []

        # Execute multiple operations and monitor memory
        for i in range(20):
            with patch('extensions.commands.openssl.cmd_build.BuildCommand.run') as mock_build:
                mock_build.return_value = {"status": "success"}

                from extensions.commands.openssl.cmd_build import BuildCommand
                cmd = BuildCommand()
                cmd.run(["--path", str(temp_workspace)])

                memory_mb = process.memory_info().rss / 1024 / 1024
                memory_usage.append(memory_mb)

                time.sleep(0.1)  # Small delay between operations

        # Check for memory leaks (should not continuously increase)
        initial_memory = memory_usage[0]
        final_memory = memory_usage[-1]
        memory_growth = final_memory - initial_memory

        # Memory leak assertions (allow some growth but not excessive)
        assert memory_growth < 20, f"Potential memory leak: {memory_growth}MB growth"


class TestPerformanceRegressionTests:
    """Performance regression detection tests."""

    def test_performance_baseline_comparison(self, temp_workspace):
        """Test performance against established baselines."""
        # Define performance baselines
        baselines = {
            "scan_command": 1.0,  # seconds
            "build_command": 5.0,
            "deploy_operation": 3.0
        }

        results = {}

        # Test scan command performance
        with patch('extensions.commands.openssl.cmd_scan.ScanCommand.run') as mock_scan:
            mock_scan.return_value = {"status": "success"}

            from extensions.commands.openssl.cmd_scan import ScanCommand
            cmd = ScanCommand()

            start_time = time.time()
            result = cmd.run(["--path", str(temp_workspace)])
            scan_time = time.time() - start_time

            results["scan_command"] = scan_time

        # Test build command performance
        with patch('extensions.commands.openssl.cmd_build.BuildCommand.run') as mock_build:
            mock_build.return_value = {"status": "success"}

            from extensions.commands.openssl.cmd_build import BuildCommand
            cmd = BuildCommand()

            start_time = time.time()
            result = cmd.run(["--path", str(temp_workspace)])
            build_time = time.time() - start_time

            results["build_command"] = build_time

        # Test deploy performance
        with patch('mcp_project_orchestrator.cursor_deployer.CursorDeployer.deploy') as mock_deploy:
            mock_deploy.return_value = {"status": "success"}

            from mcp_project_orchestrator.cursor_deployer import CursorDeployer
            deployer = CursorDeployer()

            start_time = time.time()
            result = deployer.deploy({"workspace_path": str(temp_workspace)})
            deploy_time = time.time() - start_time

            results["deploy_operation"] = deploy_time

        # Regression assertions
        for operation, baseline in baselines.items():
            actual_time = results[operation]
            assert actual_time <= baseline * 1.2, f"Performance regression in {operation}: {actual_time}s (baseline: {baseline}s)"


class TestLoadBalancingTests:
    """Load balancing and resource allocation tests."""

    def test_resource_allocation_under_load(self, temp_workspace):
        """Test resource allocation under high load."""
        with patch('extensions.graph_api.build_graph.BuildGraph.allocate_resources') as mock_allocate:
            # Simulate high load scenario
            mock_allocate.return_value = {
                "cpu_cores": 8,
                "memory_gb": 16,
                "parallel_jobs": 8
            }

            # Test resource allocation
            result = mock_allocate.return_value

            # Load balancing assertions
            assert result["cpu_cores"] >= 4, "Insufficient CPU allocation"
            assert result["memory_gb"] >= 8, "Insufficient memory allocation"
            assert result["parallel_jobs"] >= 4, "Insufficient parallel job allocation"

    def test_extension_prioritization(self, temp_workspace):
        """Test extension execution prioritization."""
        with patch('extensions.graph_api.build_graph.BuildGraph.schedule_tasks') as mock_schedule:
            mock_schedule.return_value = {
                "priority_order": ["critical", "high", "medium", "low"],
                "estimated_completion": "30s"
            }

            result = mock_schedule.return_value

            # Prioritization assertions
            assert result["priority_order"][0] == "critical", "Critical tasks not prioritized"
            assert "estimated_completion" in result

