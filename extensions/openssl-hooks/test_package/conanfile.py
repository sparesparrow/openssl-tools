"""
Test Package for OpenSSL Hooks Extension

This test package validates that the OpenSSL hooks extension is properly
installed and functioning correctly.
"""

import os
from conan import ConanFile
from conan.tools.files import save


class OpenSSLHooksTestConan(ConanFile):
    """
    Test package for OpenSSL Hooks extension.
    
    This package tests the installation and functionality of the
    OpenSSL hooks extension by creating a simple OpenSSL-like package
    and verifying that the hooks execute properly.
    """
    
    # Package settings
    settings = "os", "arch", "compiler", "build_type"
    generators = "VirtualBuildEnv", "VirtualRunEnv"
    test_type = "explicit"
    
    def requirements(self):
        """Require the OpenSSL hooks package for testing."""
        self.requires(self.tested_reference_str)
    
    def build(self):
        """Build the test package."""
        # Create a simple test source structure
        self._create_test_source_structure()
        
        # The hooks should execute during the build process
        self.output.info("✅ Test package build completed")
    
    def test(self):
        """Test the hooks functionality."""
        # Source the environment files to get the environment variables
        self._source_environment()
        
        # Test that hooks are properly registered
        self._test_hook_registration()
        
        # Test that environment variables are set
        self._test_environment_variables()
        
        # Test that hook files are accessible
        self._test_hook_files()
        
        self.output.info("✅ All hook tests passed")
    
    def _source_environment(self):
        """Source the environment files to get environment variables."""
        import subprocess
        
        # Source the conanrun.sh file to get environment variables
        conanrun_file = os.path.join(self.build_folder, "conanrun.sh")
        if os.path.exists(conanrun_file):
            try:
                # Source the environment file
                result = subprocess.run(
                    f"source {conanrun_file} && env",
                    shell=True,
                    capture_output=True,
                    text=True,
                    executable="/bin/bash"
                )
                
                if result.returncode == 0:
                    # Parse environment variables from output
                    for line in result.stdout.split('\n'):
                        if '=' in line and not line.startswith('_'):
                            key, value = line.split('=', 1)
                            os.environ[key] = value
                    
                    self.output.info("✅ Environment sourced successfully")
                else:
                    self.output.warning(f"⚠️ Could not source environment: {result.stderr}")
            
            except Exception as e:
                self.output.warning(f"⚠️ Error sourcing environment: {e}")
    
    def _create_test_source_structure(self):
        """Create a test OpenSSL source structure."""
        # Create test source directory
        source_dir = os.path.join(self.build_folder, "test_source")
        os.makedirs(source_dir, exist_ok=True)
        
        # Create essential OpenSSL files
        essential_files = {
            "VERSION.dat": "3.0.0",
            "Configure": "#!/bin/sh\necho 'OpenSSL Configure script'",
            "config": "#!/bin/sh\necho 'OpenSSL config script'",
            "include/openssl/opensslv.h": """
#ifndef OPENSSL_OPENSSLV_H
#define OPENSSL_OPENSSLV_H

#define OPENSSL_VERSION_NUMBER 0x30000000L
#define OPENSSL_VERSION_TEXT "OpenSSL 3.0.0"
#define OPENSSL_VERSION_STR "3.0.0"

#endif
""",
            "include/openssl/ssl.h": """
#ifndef OPENSSL_SSL_H
#define OPENSSL_SSL_H

#include <openssl/opensslv.h>

#endif
""",
            "include/openssl/crypto.h": """
#ifndef OPENSSL_CRYPTO_H
#define OPENSSL_CRYPTO_H

#include <openssl/opensslv.h>

#endif
"""
        }
        
        for file_path, content in essential_files.items():
            full_path = os.path.join(source_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, 'w') as f:
                f.write(content)
            
            # Make scripts executable
            if file_path in ["Configure", "config"]:
                os.chmod(full_path, 0o755)
        
        self.output.info(f"✅ Test source structure created at: {source_dir}")
    
    def _test_hook_registration(self):
        """Test that hooks are properly registered."""
        # Check that OpenSSL hooks environment variables are set
        hooks_version = os.environ.get('OPENSSL_HOOKS_VERSION', '')
        hooks_dir = os.environ.get('OPENSSL_HOOKS_DIR', '')
        
        if not hooks_version:
            raise Exception("OPENSSL_HOOKS_VERSION environment variable not set")
        
        if not hooks_dir:
            raise Exception("OPENSSL_HOOKS_DIR environment variable not set")
        
        # Check that hooks directory exists
        if not os.path.exists(hooks_dir):
            raise Exception(f"Hooks directory does not exist: {hooks_dir}")
        
        # Check that all required hook files exist
        required_hooks = [
            "pre_build.py",
            "post_package.py",
            "pre_export.py",
            "post_export.py"
        ]
        
        for hook in required_hooks:
            hook_path = os.path.join(hooks_dir, hook)
            if not os.path.exists(hook_path):
                raise Exception(f"Hook file not found: {hook_path}")
        
        self.output.info("✅ Hook registration test passed")
    
    def _test_environment_variables(self):
        """Test that environment variables are properly set."""
        # Check OpenSSL hooks specific environment variables
        required_env_vars = [
            'OPENSSL_HOOKS_VERSION',
            'OPENSSL_HOOKS_DIR'
        ]
        
        for env_var in required_env_vars:
            if not os.environ.get(env_var):
                raise Exception(f"Environment variable {env_var} not set")
        
        # Check that hooks directory exists
        hooks_dir = os.environ.get('OPENSSL_HOOKS_DIR')
        if not os.path.exists(hooks_dir):
            raise Exception(f"Hooks directory does not exist: {hooks_dir}")
        
        # Check version format
        version = os.environ.get('OPENSSL_HOOKS_VERSION')
        if not version or not isinstance(version, str):
            raise Exception("OPENSSL_HOOKS_VERSION must be a non-empty string")
        
        self.output.info("✅ Environment variables test passed")
    
    def _test_hook_files(self):
        """Test that hook files are accessible and valid."""
        hooks_dir = os.environ.get('OPENSSL_HOOKS_DIR')
        if not hooks_dir:
            raise Exception("OPENSSL_HOOKS_DIR not set")
        
        required_hooks = [
            "pre_build.py",
            "post_package.py",
            "pre_export.py",
            "post_export.py"
        ]
        
        for hook_file in required_hooks:
            hook_path = os.path.join(hooks_dir, hook_file)
            if not os.path.exists(hook_path):
                raise Exception(f"Hook file not found: {hook_path}")
            
            # Check that the file is a valid Python file
            try:
                with open(hook_path, 'r') as f:
                    content = f.read()
                
                # Check for required function
                if 'def run(conanfile, **kwargs)' not in content:
                    raise Exception(f"Hook {hook_file} missing required 'run' function")
                
                # Check for proper docstring
                if '"""' not in content:
                    self.output.warning(f"Hook {hook_file} missing docstring")
                
            except Exception as e:
                raise Exception(f"Error validating hook {hook_file}: {e}")
        
        self.output.info("✅ Hook files test passed")
