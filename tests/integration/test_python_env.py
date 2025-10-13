#!/usr/bin/env python3
"""
Tests for Python environment management.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
import subprocess

from setup_python_env import PythonEnvironmentManager


class TestPythonEnvironmentManager:
    """Test cases for PythonEnvironmentManager."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.base_path = Path(self.temp_dir) / "test-envs"
        self.manager = PythonEnvironmentManager(
            python_versions=["3.11"],
            base_path=self.base_path
        )
        
    def teardown_method(self):
        """Clean up test fixtures."""
        if self.base_path.exists():
            shutil.rmtree(self.base_path)
        shutil.rmtree(self.temp_dir)
        
    def test_init(self):
        """Test PythonEnvironmentManager initialization."""
        assert self.manager.versions == ["3.11"]
        assert self.manager.base_path == self.base_path
        assert self.manager.config_file == self.base_path / "config.json"
        
    @patch('subprocess.run')
    def test_setup_single_environment_success(self, mock_run):
        """Test successful environment setup."""
        # Mock successful subprocess calls
        mock_run.return_value = MagicMock(returncode=0)
        
        # Mock file existence checks
        with patch.object(Path, 'exists') as mock_exists:
            mock_exists.return_value = True
            
            # Mock pip path
            with patch.object(Path, 'read_bytes') as mock_read_bytes:
                mock_read_bytes.return_value = b"test content"
                
                result = self.manager._setup_single_environment("3.11", False)
                assert result is True
                
    @patch('subprocess.run')
    def test_setup_single_environment_failure(self, mock_run):
        """Test environment setup failure."""
        # Mock failed subprocess call
        mock_run.side_effect = subprocess.CalledProcessError(1, "python")
        
        result = self.manager._setup_single_environment("3.11", False)
        assert result is False
        
    def test_calculate_build_hash(self):
        """Test build hash calculation."""
        # Create temporary test files
        test_file1 = self.base_path / "test1.txt"
        test_file2 = self.base_path / "test2.txt"
        
        test_file1.write_text("content1")
        test_file2.write_text("content2")
        
        build_options = {"debug": True, "optimize": False}
        dependencies = ["openssl", "crypto"]
        compiler_info = {"gcc": "11.0"}
        
        hash1 = self.manager.calculate_build_hash(
            [test_file1, test_file2],
            build_options,
            dependencies,
            compiler_info
        )
        
        # Same inputs should produce same hash
        hash2 = self.manager.calculate_build_hash(
            [test_file1, test_file2],
            build_options,
            dependencies,
            compiler_info
        )
        
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA256 hex length
        
    def test_get_environment_path(self):
        """Test getting environment path."""
        # Environment doesn't exist
        path = self.manager.get_environment_path("3.11")
        assert path is None
        
        # Create environment directory
        env_path = self.base_path / "python3.11"
        env_path.mkdir(parents=True)
        
        path = self.manager.get_environment_path("3.11")
        assert path == env_path
        
    def test_save_and_load_config(self):
        """Test configuration save and load."""
        # Save config
        self.manager._save_config()
        
        # Load config
        config = self.manager.load_config()
        
        assert "versions" in config
        assert "base_path" in config
        assert "environments" in config
        
    def test_list_environments(self):
        """Test listing environments."""
        # No environments initially
        environments = self.manager.list_environments()
        assert environments == {}
        
        # Add mock environment to config
        self.manager.build_index = {
            "3.11": {
                "path": str(self.base_path / "python3.11"),
                "python_exe": str(self.base_path / "python3.11" / "bin" / "python")
            }
        }
        self.manager._save_config()
        
        environments = self.manager.list_environments()
        assert "3.11" in environments
        
    def test_cleanup_environment(self):
        """Test environment cleanup."""
        # Create environment directory
        env_path = self.base_path / "python3.11"
        env_path.mkdir(parents=True)
        
        # Add to config
        self.manager.build_index = {"3.11": {"path": str(env_path)}}
        self.manager._save_config()
        
        # Cleanup
        result = self.manager.cleanup_environment("3.11")
        assert result is True
        assert not env_path.exists()
        
    def test_cleanup_all_environments(self):
        """Test cleanup of all environments."""
        # Create base directory
        self.base_path.mkdir(parents=True)
        
        # Cleanup all
        result = self.manager.cleanup_all_environments()
        assert result is True
        assert not self.base_path.exists()


@pytest.mark.integration
class TestPythonEnvironmentIntegration:
    """Integration tests for Python environment management."""
    
    def setup_method(self):
        """Set up integration test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.base_path = Path(self.temp_dir) / "integration-envs"
        
    def teardown_method(self):
        """Clean up integration test fixtures."""
        if self.base_path.exists():
            shutil.rmtree(self.base_path)
        shutil.rmtree(self.temp_dir)
        
    @pytest.mark.slow
    def test_full_environment_setup(self):
        """Test complete environment setup process."""
        manager = PythonEnvironmentManager(
            python_versions=["3.11"],
            base_path=self.base_path
        )
        
        # This test requires actual Python installation
        # Skip if Python 3.11 is not available
        try:
            subprocess.run(["python3.11", "--version"], 
                         check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            pytest.skip("Python 3.11 not available")
            
        # Set up environment
        result = manager.setup_environments()
        
        # Check if setup was successful
        if result:
            # Verify environment exists
            env_path = manager.get_environment_path("3.11")
            assert env_path is not None
            assert env_path.exists()
            
            # Verify Python executable exists
            python_exe = manager.get_python_executable("3.11")
            assert python_exe is not None
            assert python_exe.exists()
            
            # Verify configuration was saved
            config = manager.load_config()
            assert "3.11" in config.get("environments", {})