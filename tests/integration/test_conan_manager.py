#!/usr/bin/env python3
"""
Tests for Conan remote management.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
import subprocess

from conan_remote_manager import ConanRemoteManager


class TestConanRemoteManager:
    """Test cases for ConanRemoteManager."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = ConanRemoteManager(
            github_token="test_token",
            username="test_user"
        )
        
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
        
    def test_init(self):
        """Test ConanRemoteManager initialization."""
        assert self.manager.github_token == "test_token"
        assert self.manager.username == "test_user"
        assert self.manager.remote_name == "github-packages"
        assert "nuget.pkg.github.com" in self.manager.github_packages_url
        
    @patch('subprocess.run')
    def test_setup_github_packages_remote_success(self, mock_run):
        """Test successful GitHub Packages remote setup."""
        # Mock successful subprocess calls
        mock_run.return_value = MagicMock(returncode=0)
        
        with patch.object(self.manager, '_verify_remote_connection') as mock_verify:
            mock_verify.return_value = True
            
            result = self.manager.setup_github_packages_remote()
            assert result is True
            
    @patch('subprocess.run')
    def test_setup_github_packages_remote_failure(self, mock_run):
        """Test GitHub Packages remote setup failure."""
        # Mock failed subprocess call
        mock_run.side_effect = subprocess.CalledProcessError(1, "conan")
        
        result = self.manager.setup_github_packages_remote()
        assert result is False
        
    def test_setup_github_packages_remote_no_token(self):
        """Test GitHub Packages remote setup without token."""
        manager = ConanRemoteManager(github_token=None)
        result = manager.setup_github_packages_remote()
        assert result is False
        
    @patch('subprocess.run')
    def test_list_remotes(self, mock_run):
        """Test listing Conan remotes."""
        # Mock conan remote list output
        mock_output = "conan-center: https://center.conan.io\ngithub-packages: https://nuget.pkg.github.com/sparesparrow/index.json\n"
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=mock_output
        )
        
        remotes = self.manager.list_remotes()
        
        assert "conan-center" in remotes
        assert "github-packages" in remotes
        assert remotes["conan-center"] == "https://center.conan.io"
        
    @patch('subprocess.run')
    def test_list_remotes_failure(self, mock_run):
        """Test listing remotes failure."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "conan")
        
        remotes = self.manager.list_remotes()
        assert remotes == {}
        
    @patch('subprocess.run')
    def test_upload_packages_success(self, mock_run):
        """Test successful package upload."""
        mock_run.return_value = MagicMock(returncode=0)
        
        result = self.manager.upload_packages(["test-package/1.0@user/channel"])
        assert result is True
        
    @patch('subprocess.run')
    def test_upload_packages_failure(self, mock_run):
        """Test package upload failure."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "conan")
        
        result = self.manager.upload_packages(["test-package/1.0@user/channel"])
        assert result is False
        
    @patch('subprocess.run')
    def test_download_packages_success(self, mock_run):
        """Test successful package download."""
        mock_run.return_value = MagicMock(returncode=0)
        
        result = self.manager.download_packages(["test-package/1.0@user/channel"])
        assert result is True
        
    @patch('subprocess.run')
    def test_download_packages_failure(self, mock_run):
        """Test package download failure."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "conan")
        
        result = self.manager.download_packages(["test-package/1.0@user/channel"])
        assert result is False
        
    @patch('subprocess.run')
    def test_search_packages(self, mock_run):
        """Test package search."""
        mock_output = "openssl/1.1.1@sparesparrow/stable\nopenssl/3.0.0@sparesparrow/stable\n"
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=mock_output
        )
        
        packages = self.manager.search_packages("openssl")
        
        assert len(packages) == 2
        assert packages[0]["name"] == "openssl"
        assert packages[0]["version"] == "1.1.1"
        
    @patch('subprocess.run')
    def test_create_package_success(self, mock_run):
        """Test successful package creation."""
        mock_run.return_value = MagicMock(returncode=0)
        
        recipe_path = Path(self.temp_dir) / "conanfile.py"
        recipe_path.write_text("from conans import ConanFile\nclass TestConan(ConanFile): pass")
        
        result = self.manager.create_package(
            recipe_path,
            "test-package",
            "1.0"
        )
        assert result is True
        
    @patch('subprocess.run')
    def test_install_package_success(self, mock_run):
        """Test successful package installation."""
        mock_run.return_value = MagicMock(returncode=0)
        
        result = self.manager.install_package("test-package/1.0@user/channel")
        assert result is True
        
    @patch('subprocess.run')
    def test_get_package_info(self, mock_run):
        """Test getting package information."""
        mock_output = "name: test-package\nversion: 1.0\ndescription: Test package\n"
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=mock_output
        )
        
        info = self.manager.get_package_info("test-package/1.0@user/channel")
        
        assert info is not None
        assert info["name"] == "test-package"
        assert info["version"] == "1.0"
        
    @patch('requests.get')
    def test_test_connection_success(self, mock_get):
        """Test successful connection test."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"login": "test_user"}
        mock_get.return_value = mock_response
        
        result = self.manager.test_connection()
        assert result is True
        
    @patch('requests.get')
    def test_test_connection_failure(self, mock_get):
        """Test connection test failure."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response
        
        result = self.manager.test_connection()
        assert result is False
        
    def test_test_connection_no_token(self):
        """Test connection test without token."""
        manager = ConanRemoteManager(github_token=None)
        result = manager.test_connection()
        assert result is False


@pytest.mark.integration
class TestConanRemoteIntegration:
    """Integration tests for Conan remote management."""
    
    def setup_method(self):
        """Set up integration test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """Clean up integration test fixtures."""
        shutil.rmtree(self.temp_dir)
        
    @pytest.mark.slow
    def test_conan_availability(self):
        """Test if Conan is available in the system."""
        try:
            result = subprocess.run(
                ["conan", "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            assert "Conan" in result.stdout
        except (subprocess.CalledProcessError, FileNotFoundError):
            pytest.skip("Conan not available")
            
    @pytest.mark.slow
    def test_conan_remote_operations(self):
        """Test basic Conan remote operations."""
        try:
            # Test if conan command works
            subprocess.run(["conan", "--version"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            pytest.skip("Conan not available")
            
        manager = ConanRemoteManager()
        
        # Test listing remotes (should work even without GitHub token)
        remotes = manager.list_remotes()
        assert isinstance(remotes, dict)
        
        # Test search (should work with default remote)
        packages = manager.search_packages("*")
        assert isinstance(packages, list)