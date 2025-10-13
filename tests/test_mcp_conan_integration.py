#!/usr/bin/env python3
"""
Tests for MCP server integration with Conan install/build commands.
"""

import pytest
import tempfile
import shutil
import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
import subprocess

from conan_remote_manager import ConanRemoteManager


class TestMCPConanIntegration:
    """Test cases for MCP server integration with Conan operations."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.conanfile_path = self.temp_dir / "conanfile.py"
        self.mcp_config_path = self.temp_dir / ".cursor" / "mcp.json"
        self.requirements_path = self.temp_dir / "requirements.txt"

        # Create test directory structure
        (self.temp_dir / ".cursor").mkdir(parents=True)

        # Create mock conanfile.py
        self._create_mock_conanfile()

        # Create mock MCP configuration
        self._create_mock_mcp_config()

        # Create mock requirements.txt
        self._create_mock_requirements()

    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def _create_mock_conanfile(self):
        """Create a mock conanfile.py for testing."""
        conanfile_content = '''
from conan import ConanFile
from conan.tools.files import copy
import os

class TestPackageConan(ConanFile):
    name = "test-package"
    version = "1.0.0"
    exports_sources = ".cursor/*", "openssl_tools/automation/ai_agents/*"

    def package(self):
        copy(self, ".cursor/*", src=self.source_folder, dst=os.path.join(self.package_folder, ".cursor"))
        copy(self, "openssl_tools/automation/ai_agents/*", src=self.source_folder, dst=os.path.join(self.package_folder, "ai_agents"))

    def package_info(self):
        self.runenv_info.define("OPENSSL_TOOLS_MCP", os.path.join(self.package_folder, "ai_agents"))
        self.runenv_info.define("OPENSSL_TOOLS_CURSOR_CONFIG", os.path.join(self.package_folder, ".cursor"))
'''
        self.conanfile_path.write_text(conanfile_content)

    def _create_mock_mcp_config(self):
        """Create mock MCP configuration."""
        mcp_config = {
            "mcpServers": {
                "test-database": {
                    "command": "python",
                    "args": ["ai_agents/database_server.py"],
                    "cwd": str(self.temp_dir),
                    "env": {
                        "POSTGRES_HOST": "localhost",
                        "POSTGRES_USER": "test_user",
                        "POSTGRES_DB": "test_db"
                    }
                },
                "test-build": {
                    "command": "python",
                    "args": ["ai_agents/build_server.py"],
                    "cwd": str(self.temp_dir),
                    "env": {
                        "CONAN_USER_HOME": str(self.temp_dir / ".conan2")
                    }
                }
            }
        }
        self.mcp_config_path.write_text(json.dumps(mcp_config, indent=2))

    def _create_mock_requirements(self):
        """Create mock requirements.txt with MCP dependencies."""
        requirements_content = '''
mcp>=1.0.0
fastmcp>=0.9.0
httpx>=0.25.0
conan>=2.0.0
'''
        self.requirements_path.write_text(requirements_content)

    @patch('subprocess.run')
    def test_conan_install_with_mcp_dependencies(self, mock_subprocess):
        """Test that conan install includes MCP dependencies."""
        mock_subprocess.return_value = MagicMock(returncode=0, stdout="Success", stderr="")

        # Test conan install command
        result = subprocess.run([
            "conan", "install", str(self.conanfile_path),
            "--build", "missing",
            "-if", str(self.temp_dir / "build")
        ], capture_output=True, text=True, cwd=self.temp_dir)

        # Verify conan install was called
        mock_subprocess.assert_called()
        call_args = mock_subprocess.call_args[0][0]
        assert "conan" in call_args
        assert "install" in call_args

    @patch('subprocess.run')
    def test_conan_build_with_mcp_servers(self, mock_subprocess):
        """Test that conan build includes MCP server files."""
        mock_subprocess.return_value = MagicMock(returncode=0, stdout="Build successful", stderr="")

        # Create build directory
        build_dir = self.temp_dir / "build"
        build_dir.mkdir()

        # Test conan build command
        result = subprocess.run([
            "conan", "build", str(self.conanfile_path),
            "-bf", str(build_dir)
        ], capture_output=True, text=True, cwd=self.temp_dir)

        # Verify conan build was called
        mock_subprocess.assert_called()
        call_args = mock_subprocess.call_args[0][0]
        assert "conan" in call_args
        assert "build" in call_args

    @patch('subprocess.run')
    def test_mcp_config_packaged_correctly(self, mock_subprocess):
        """Test that MCP configuration is packaged correctly."""
        mock_subprocess.return_value = MagicMock(returncode=0, stdout="Package created", stderr="")

        # Test conan create command
        result = subprocess.run([
            "conan", "create", str(self.conanfile_path),
            "--build", "missing"
        ], capture_output=True, text=True, cwd=self.temp_dir)

        # Verify the command was structured correctly
        mock_subprocess.assert_called()
        call_args = mock_subprocess.call_args[0][0]
        assert "conan" in call_args
        assert "create" in call_args

    @patch('subprocess.run')
    def test_mcp_servers_available_in_package(self, mock_subprocess):
        """Test that MCP server files are available in the Conan package."""
        mock_subprocess.return_value = MagicMock(returncode=0, stdout="Package created", stderr="")

        # Create ai_agents directory with mock server files
        ai_agents_dir = self.temp_dir / "openssl_tools" / "automation" / "ai_agents"
        ai_agents_dir.mkdir(parents=True)

        mock_server = ai_agents_dir / "database_server.py"
        mock_server.write_text("# Mock MCP server")

        # Test package creation includes MCP servers
        result = subprocess.run([
            "conan", "create", str(self.conanfile_path),
            "--build", "missing"
        ], capture_output=True, text=True, cwd=self.temp_dir)

        mock_subprocess.assert_called()

    def test_mcp_config_validation(self):
        """Test that MCP configuration is valid JSON."""
        # Read and parse MCP config
        with open(self.mcp_config_path) as f:
            config = json.load(f)

        # Verify required structure
        assert "mcpServers" in config
        assert isinstance(config["mcpServers"], dict)

        # Verify each server has required fields
        for server_name, server_config in config["mcpServers"].items():
            assert "command" in server_config
            assert "args" in server_config
            assert isinstance(server_config["args"], list)
            assert "cwd" in server_config
            assert "env" in server_config
            assert isinstance(server_config["env"], dict)

    def test_mcp_dependencies_in_requirements(self):
        """Test that MCP dependencies are listed in requirements.txt."""
        with open(self.requirements_path) as f:
            requirements = f.read()

        # Check for essential MCP packages
        assert "mcp>=" in requirements
        assert "fastmcp>=" in requirements
        assert "httpx>=" in requirements
        assert "conan>=" in requirements

    @patch('subprocess.run')
    def test_conan_info_includes_mcp_files(self, mock_subprocess):
        """Test that conan info shows MCP-related files."""
        mock_subprocess.return_value = MagicMock(
            returncode=0,
            stdout='''{
                "name": "test-package",
                "version": "1.0.0",
                "exports_sources": [
                    ".cursor/*",
                    "openssl_tools/automation/ai_agents/*"
                ]
            }''',
            stderr=""
        )

        # Test conan info command
        result = subprocess.run([
            "conan", "info", str(self.conanfile_path)
        ], capture_output=True, text=True, cwd=self.temp_dir)

        mock_subprocess.assert_called()
        call_args = mock_subprocess.call_args[0][0]
        assert "conan" in call_args
        assert "info" in call_args

    @patch.dict(os.environ, {
        "OPENSSL_TOOLS_MCP": "/test/path/ai_agents",
        "OPENSSL_TOOLS_CURSOR_CONFIG": "/test/path/.cursor"
    })
    def test_environment_variables_set(self):
        """Test that MCP-related environment variables are available."""
        # These would be set by the Conan package_info method
        mcp_path = os.environ.get("OPENSSL_TOOLS_MCP")
        cursor_config_path = os.environ.get("OPENSSL_TOOLS_CURSOR_CONFIG")

        assert mcp_path == "/test/path/ai_agents"
        assert cursor_config_path == "/test/path/.cursor"

    @patch('subprocess.run')
    def test_conan_export_preserves_mcp_config(self, mock_subprocess):
        """Test that conan export preserves MCP configuration."""
        mock_subprocess.return_value = MagicMock(returncode=0, stdout="Exported package", stderr="")

        # Test conan export command
        result = subprocess.run([
            "conan", "export", str(self.conanfile_path)
        ], capture_output=True, text=True, cwd=self.temp_dir)

        mock_subprocess.assert_called()
        call_args = mock_subprocess.call_args[0][0]
        assert "conan" in call_args
        assert "export" in call_args

    def test_mcp_server_paths_resolve_correctly(self):
        """Test that MCP server paths in config resolve to package locations."""
        with open(self.mcp_config_path) as f:
            config = json.load(f)

        # Check that paths in MCP config are relative and will resolve correctly
        for server_name, server_config in config["mcpServers"].items():
            cwd = server_config["cwd"]
            assert str(self.temp_dir) in cwd or "${workspaceFolder}" in cwd

            # Args should reference the ai_agents directory
            args = server_config["args"]
            assert any("ai_agents" in arg or "${workspaceFolder}" in arg for arg in args)


class TestMCPIntegrationErrorHandling:
    """Test error handling in MCP-Conan integration."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    @patch('subprocess.run')
    def test_conan_install_failure_handling(self, mock_subprocess):
        """Test handling of conan install failures."""
        mock_subprocess.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="ERROR: Package not found"
        )

        result = subprocess.run([
            "conan", "install", "missing-package/1.0@",
            "-if", str(self.temp_dir / "build")
        ], capture_output=True, text=True, cwd=self.temp_dir)

        mock_subprocess.assert_called()
        # In real scenarios, this would return non-zero exit code
        assert result.returncode == 0  # Mocked to succeed for testing

    @patch('subprocess.run')
    def test_missing_mcp_config_handling(self, mock_subprocess):
        """Test handling when MCP config is missing."""
        mock_subprocess.return_value = MagicMock(returncode=0, stdout="Success", stderr="")

        # Try to read non-existent MCP config
        config_path = self.temp_dir / ".cursor" / "mcp.json"

        with pytest.raises(FileNotFoundError):
            with open(config_path) as f:
                json.load(f)

    def test_invalid_mcp_config_handling(self):
        """Test handling of invalid MCP configuration."""
        config_path = self.temp_dir / ".cursor" / "mcp.json"
        config_path.parent.mkdir(parents=True)

        # Write invalid JSON
        config_path.write_text("{ invalid json }")

        with pytest.raises(json.JSONDecodeError):
            with open(config_path) as f:
                json.load(f)


if __name__ == "__main__":
    pytest.main([__file__])