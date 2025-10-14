#!/usr/bin/env python3
"""
OpenSSL Artifactory Functions Tests
Test suite for OpenSSL Artifactory functions
"""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the scripts directory to the path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from openssl_conan.conan.artifactory_functions import (
    ArtifactoryConfiguration,
    setup_artifactory_remote,
    enable_conan_remote,
    disable_conan_remote,
    list_remotes,
    add_remote,
    remove_remote,
    update_remote,
    set_remote_credentials,
    configure_artifactory_for_openssl,
    search_packages_in_remote,
    upload_package_to_remote,
    download_package_from_remote,
    get_remote_info,
    setup_openssl_remotes,
    configure_for_ci_environment
)


class TestArtifactoryFunctions(unittest.TestCase):
    """Test cases for Artifactory functions"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.original_env = os.environ.copy()
        
        # Set up test environment
        os.environ['CONAN_USER_HOME'] = str(self.temp_dir)
        os.environ['CONAN_REMOTE_NAME'] = 'test-remote'
        os.environ['CONAN_REMOTE_URL'] = 'https://test.example.com'
        os.environ['CONAN_USER'] = 'testuser'
        os.environ['CONAN_PASSWORD'] = 'testpass'
    
    def tearDown(self):
        """Clean up test environment"""
        os.environ.clear()
        os.environ.update(self.original_env)
        
        # Clean up temp directory
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_artifactory_configuration(self):
        """Test Artifactory configuration"""
        config = ArtifactoryConfiguration()
        
        self.assertEqual(config.nga_conan_name, 'test-remote')
        self.assertEqual(config.nga_conan_url, 'https://test.example.com')
        self.assertEqual(config.user, 'testuser')
        self.assertEqual(config.password, 'testpass')
    
    def test_artifactory_configuration_defaults(self):
        """Test Artifactory configuration with defaults"""
        # Clear environment variables
        for key in ['CONAN_REMOTE_NAME', 'CONAN_REMOTE_URL', 'CONAN_USER', 'CONAN_PASSWORD']:
            if key in os.environ:
                del os.environ[key]
        
        config = ArtifactoryConfiguration()
        
        self.assertEqual(config.nga_conan_name, 'conancenter')
        self.assertEqual(config.nga_conan_url, 'https://center.conan.io')
        self.assertEqual(config.user, '')
        self.assertEqual(config.password, '')
    
    @patch('ngapy.conan.artifactory_functions.execute_command')
    def test_setup_artifactory_remote(self, mock_execute):
        """Test setting up Artifactory remote"""
        mock_execute.return_value = (0, ['Success'])
        
        setup_artifactory_remote()
        
        # Verify that remote clean was called
        mock_execute.assert_any_call('conan remote clean')
        
        # Verify that remote add was called
        mock_execute.assert_any_call('conan remote add test-remote https://test.example.com')
        
        # Verify that user was set
        mock_execute.assert_any_call('conan user -p testpass -r test-remote testuser')
    
    @patch('ngapy.conan.artifactory_functions.execute_command')
    def test_enable_conan_remote(self, mock_execute):
        """Test enabling Conan remote"""
        mock_execute.return_value = (0, ['Success'])
        
        enable_conan_remote()
        
        mock_execute.assert_called_once_with('conan remote enable test-remote')
    
    @patch('ngapy.conan.artifactory_functions.execute_command')
    def test_disable_conan_remote(self, mock_execute):
        """Test disabling Conan remote"""
        mock_execute.return_value = (0, ['Success'])
        
        disable_conan_remote()
        
        mock_execute.assert_called_once_with('conan remote disable test-remote')
    
    @patch('ngapy.conan.artifactory_functions.execute_command')
    def test_list_remotes(self, mock_execute):
        """Test listing remotes"""
        mock_output = [
            'conancenter: https://center.conan.io [Verify SSL: True]',
            'test-remote: https://test.example.com [Verify SSL: True]'
        ]
        mock_execute.return_value = (0, mock_output)
        
        output = list_remotes()
        
        self.assertEqual(output, mock_output)
        mock_execute.assert_called_once_with('conan remote list')
    
    @patch('ngapy.conan.artifactory_functions.execute_command')
    def test_add_remote(self, mock_execute):
        """Test adding a remote"""
        mock_execute.return_value = (0, ['Success'])
        
        add_remote('new-remote', 'https://new.example.com', 'user', 'pass')
        
        # Verify remote add was called
        mock_execute.assert_any_call('conan remote add new-remote https://new.example.com')
        
        # Verify user was set
        mock_execute.assert_any_call('conan user -p pass -r new-remote user')
    
    @patch('ngapy.conan.artifactory_functions.execute_command')
    def test_remove_remote(self, mock_execute):
        """Test removing a remote"""
        mock_execute.return_value = (0, ['Success'])
        
        remove_remote('test-remote')
        
        mock_execute.assert_called_once_with('conan remote remove test-remote')
    
    @patch('ngapy.conan.artifactory_functions.execute_command')
    def test_update_remote(self, mock_execute):
        """Test updating a remote"""
        mock_execute.return_value = (0, ['Success'])
        
        update_remote('test-remote', 'https://updated.example.com')
        
        mock_execute.assert_called_once_with('conan remote update test-remote https://updated.example.com')
    
    @patch('ngapy.conan.artifactory_functions.execute_command')
    def test_set_remote_credentials(self, mock_execute):
        """Test setting remote credentials"""
        mock_execute.return_value = (0, ['Success'])
        
        set_remote_credentials('test-remote', 'user', 'pass')
        
        mock_execute.assert_called_once_with('conan user -p pass -r test-remote user')
    
    @patch('ngapy.conan.artifactory_functions.execute_command')
    def test_search_packages_in_remote(self, mock_execute):
        """Test searching packages in remote"""
        mock_output = ['openssl/1.1.1', 'openssl/3.0.0', 'openssl/3.1.0']
        mock_execute.return_value = (0, mock_output)
        
        output = search_packages_in_remote('test-remote', 'openssl/*')
        
        self.assertEqual(output, mock_output)
        mock_execute.assert_called_once_with('conan search openssl/* -r test-remote')
    
    @patch('ngapy.conan.artifactory_functions.execute_command')
    def test_upload_package_to_remote(self, mock_execute):
        """Test uploading package to remote"""
        mock_execute.return_value = (0, ['Success'])
        
        result = upload_package_to_remote('openssl/3.0.0', 'test-remote')
        
        self.assertTrue(result)
        mock_execute.assert_called_once_with('conan upload openssl/3.0.0 -r test-remote --confirm')
    
    @patch('ngapy.conan.artifactory_functions.execute_command')
    def test_download_package_from_remote(self, mock_execute):
        """Test downloading package from remote"""
        mock_execute.return_value = (0, ['Success'])
        
        result = download_package_from_remote('openssl/3.0.0', 'test-remote')
        
        self.assertTrue(result)
        mock_execute.assert_called_once_with('conan download openssl/3.0.0 -r test-remote')
    
    @patch('ngapy.conan.artifactory_functions.execute_command')
    def test_get_remote_info(self, mock_execute):
        """Test getting remote info"""
        mock_output = [
            'conancenter: https://center.conan.io [Verify SSL: True]',
            'test-remote: https://test.example.com [Verify SSL: True]'
        ]
        mock_execute.return_value = (0, mock_output)
        
        info = get_remote_info('test-remote')
        
        self.assertIn('test-remote', info)
        mock_execute.assert_called_once_with('conan remote list')
    
    @patch('ngapy.conan.artifactory_functions.execute_command')
    def test_setup_openssl_remotes(self, mock_execute):
        """Test setting up OpenSSL remotes"""
        mock_execute.return_value = (0, ['Success'])
        
        setup_openssl_remotes()
        
        # Verify that remotes were added
        mock_execute.assert_any_call('conan remote add conancenter https://center.conan.io')
        mock_execute.assert_any_call('conan remote add bincrafters https://bincrafters.jfrog.io/artifactory/api/conan/public-conan')
    
    @patch('ngapy.conan.artifactory_functions.execute_command')
    def test_configure_for_ci_environment(self, mock_execute):
        """Test configuring for CI environment"""
        mock_execute.return_value = (0, ['Success'])
        
        configure_for_ci_environment()
        
        # Verify that remotes were set up
        mock_execute.assert_any_call('conan remote add conancenter https://center.conan.io')
        
        # Verify that parallel downloads were configured
        mock_execute.assert_any_call('conan config set general.parallel_download=4')


if __name__ == '__main__':
    unittest.main()