#!/usr/bin/env python3
"""
OpenSSL Conan Functions Tests
Test suite for OpenSSL Conan functions
"""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the scripts directory to the path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from openssl_conan.conan.conan_functions import (
    get_default_conan,
    get_conan_home,
    get_all_packages_in_cache,
    ConanConfiguration,
    ConanConfigurationTracker,
    execute_command,
    OpenSSLRuntimeError
)


class TestConanFunctions(unittest.TestCase):
    """Test cases for Conan functions"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.original_env = os.environ.copy()
        
        # Set up test environment
        os.environ['CONAN_USER_HOME'] = str(self.temp_dir)
        os.environ['CONAN_COLOR_DISPLAY'] = '1'
        os.environ['CLICOLOR_FORCE'] = '1'
        os.environ['CLICOLOR'] = '1'
    
    def tearDown(self):
        """Clean up test environment"""
        os.environ.clear()
        os.environ.update(self.original_env)
        
        # Clean up temp directory
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_get_default_conan(self):
        """Test getting default Conan executable"""
        conan_path = get_default_conan()
        self.assertIsInstance(conan_path, Path)
        self.assertTrue(conan_path.exists())
    
    def test_get_conan_home(self):
        """Test getting Conan home directory"""
        conan_home, conan_home_short = get_conan_home()
        self.assertIsInstance(conan_home, str)
        self.assertIsInstance(conan_home_short, str)
    
    def test_execute_command_success(self):
        """Test successful command execution"""
        rc, output = execute_command('echo "test"')
        self.assertEqual(rc, 0)
        self.assertIn('test', output)
    
    def test_execute_command_failure(self):
        """Test failed command execution"""
        rc, output = execute_command('nonexistentcommand12345')
        self.assertNotEqual(rc, 0)
    
    def test_conan_configuration_tracker(self):
        """Test Conan configuration tracker"""
        tracker = ConanConfigurationTracker()
        
        # Test properties
        self.assertIsInstance(tracker.config_path, Path)
        self.assertIsInstance(tracker.packages, dict)
        
        # Test package tracking
        tracker.packages['test/1.0.0'] = {'last_used': '2023-01-01'}
        self.assertEqual(tracker.packages['test/1.0.0']['last_used'], '2023-01-01')
    
    def test_conan_configuration(self):
        """Test Conan configuration"""
        config = ConanConfiguration()
        
        # Test conanfile detection
        test_conanfile = self.temp_dir / 'conanfile.py'
        test_conanfile.write_text('from conan import ConanFile\nclass Test(ConanFile): pass')
        
        conanfile_path = config.get_conanfile(str(self.temp_dir))
        self.assertEqual(conanfile_path, test_conanfile)
        
        # Test conanfile not found
        with self.assertRaises(OpenSSLRuntimeError):
            config.get_conanfile('/nonexistent/path')
    
    def test_conan_configuration_tracker_file_operations(self):
        """Test Conan configuration tracker file operations"""
        tracker = ConanConfigurationTracker()
        
        # Test save and load
        tracker.packages['test/1.0.0'] = {'last_used': '2023-01-01'}
        tracker.save_config()
        
        # Create new tracker and load
        new_tracker = ConanConfigurationTracker()
        self.assertIn('test/1.0.0', new_tracker.packages)
    
    @patch('ngapy.conan.conan_functions.execute_command')
    def test_get_all_packages_in_cache(self, mock_execute):
        """Test getting all packages in cache"""
        mock_execute.return_value = (0, ['package1/1.0.0', 'package2/2.0.0', 'WARN: warning'])
        
        packages = get_all_packages_in_cache()
        self.assertEqual(len(packages), 2)
        self.assertIn('package1/1.0.0', packages)
        self.assertIn('package2/2.0.0', packages)
        self.assertNotIn('WARN: warning', packages)
    
    @patch('ngapy.conan.conan_functions.execute_command')
    def test_get_all_packages_in_cache_failure(self, mock_execute):
        """Test getting all packages in cache with failure"""
        mock_execute.return_value = (1, ['Error: failed'])
        
        packages = get_all_packages_in_cache()
        self.assertEqual(len(packages), 0)


class TestConanJsonLoader(unittest.TestCase):
    """Test cases for ConanJsonLoader"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.original_env = os.environ.copy()
        
        # Set up test environment
        os.environ['CONAN_USER_HOME'] = str(self.temp_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        os.environ.clear()
        os.environ.update(self.original_env)
        
        # Clean up temp directory
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    @patch('ngapy.conan.conan_functions.execute_command')
    def test_conan_json_loader(self, mock_execute):
        """Test ConanJsonLoader"""
        # Mock conan info output
        mock_output = [
            'conanfile.py (test/1.0.0)',
            '  ID: 1234567890abcdef',
            '  BuildID: None',
            '  Context: host',
            '  Binary: Missing',
            '  Binary remote: None',
            '  Creation date: 2023-01-01 00:00:00',
            '  Shared folder: /tmp/shared',
            '  Package folder: /tmp/package',
            '  Build folder: /tmp/build',
            '  Source folder: /tmp/source',
            '  Download folder: /tmp/download',
            '  Recipe: /tmp/recipe',
            '  Cache: /tmp/cache',
            '  Remote: None',
            '  URL: None',
            '  Homepage: None',
            '  License: None',
            '  Author: None',
            '  Topics: None',
            '  Revision: None',
            '  Package ID: 1234567890abcdef',
            '  Package revision: None',
            '  Recipe revision: None',
            '  Requires:',
            '    other/2.0.0',
            '  Build requires:',
            '    cmake/3.25.0',
            '  Python requires:',
            '  Provides:',
            '    test',
            '  Depends on:',
            '    other/2.0.0',
            '  Depends on (build):',
            '    cmake/3.25.0',
            '  Depends on (python):',
        ]
        mock_execute.return_value = (0, mock_output)
        
        # Create a temporary JSON file
        import json
        temp_json = self.temp_dir / 'temp.json'
        with open(temp_json, 'w') as f:
            json.dump([{
                'display_name': 'conanfile.py (test/1.0.0)',
                'reference': 'test/1.0.0',
                'provides': ['test'],
                'package_folder': '/tmp/package'
            }], f)
        
        # Mock the tempfile creation
        with patch('tempfile.NamedTemporaryFile') as mock_temp:
            mock_temp.return_value.__enter__.return_value.name = str(temp_json)
            
            from ngapy.conan.conan_functions import ConanJsonLoader
            loader = ConanJsonLoader(str(self.temp_dir))
            
            # Test root node
            root_node = loader._get_root_node()
            self.assertIsNotNone(root_node)
            self.assertEqual(root_node.display_name, 'conanfile.py (test/1.0.0)')
            
            # Test package name version
            name, version = loader.get_package_name_version(root_node)
            self.assertEqual(name, 'test')
            self.assertEqual(version, '1.0.0')


if __name__ == '__main__':
    unittest.main()