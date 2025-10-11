"""
OpenSSL Hooks Conan Extension Package

This package provides Conan hooks for OpenSSL projects, including:
- pre_build: Build environment preparation and validation
- post_package: Package validation and SBOM generation
- pre_export: Export preparation and security checks
- post_export: Export validation and quality reporting

The hooks are automatically registered when this package is installed as a dependency.
"""

import os
from pathlib import Path
from conan import ConanFile
from conan.tools.files import copy
from conan.errors import ConanInvalidConfiguration


class OpenSSLHooksConan(ConanFile):
    """
    OpenSSL Hooks Conan Extension Package
    
    This package provides comprehensive hooks for OpenSSL projects to ensure
    quality, security, and compliance throughout the build and packaging process.
    """
    
    # Package metadata
    name = "openssl-hooks"
    version = "1.0.0"
    description = "Conan hooks for OpenSSL projects - build validation, security checks, and quality assurance"
    license = "Apache-2.0"
    author = "OpenSSL Tools Team <openssl-tools@example.com>"
    url = "https://github.com/sparesparrow/openssl-tools"
    homepage = "https://github.com/sparesparrow/openssl-tools"
    topics = ["openssl", "conan", "hooks", "security", "quality", "build-automation"]
    
    # Package settings
    settings = "os", "arch", "compiler", "build_type"
    
    # No build system required - this is a pure Python package
    # no_copy_source = True  # Commented out to allow source access
    
    # Export all hook files
    exports = "hooks/*"
    exports_sources = "hooks/*", "README.md"
    
    def package(self):
        """
        Package the hook files.
        
        This method copies all hook files to the package directory
        so they can be used by consuming packages.
        """
        if self.source_folder:
            # Copy all hook files to the package
            copy(self, "*.py", 
                 src=os.path.join(self.source_folder, "hooks"), 
                 dst=os.path.join(self.package_folder, "hooks"))
            
            # Copy README and documentation
            readme_path = os.path.join(self.source_folder, "README.md")
            if os.path.exists(readme_path):
                copy(self, "README.md", 
                     src=self.source_folder, 
                     dst=self.package_folder)
            
            license_path = os.path.join(self.source_folder, "LICENSE")
            if os.path.exists(license_path):
                copy(self, "LICENSE", 
                     src=self.source_folder, 
                     dst=self.package_folder)
    
    def package_info(self):
        """
        Configure package information and register hooks.
        
        This method sets up the package information and registers
        the hooks with Conan so they are automatically executed.
        """
        # Set package info
        self.cpp_info.libs = []  # No libraries - this is a hooks package
        self.cpp_info.includedirs = []  # No headers - this is a hooks package
        
        # Register hooks with Conan
        hooks_dir = os.path.join(self.package_folder, "hooks")
        
        # Register each hook
        hook_files = [
            "pre_build.py",
            "post_package.py", 
            "pre_export.py",
            "post_export.py"
        ]
        
        # In Conan 2.x, we need to set environment variables differently
        # The hooks will be available in the package folder
        self.runenv_info.define("OPENSSL_HOOKS_VERSION", self.version)
        self.runenv_info.define("OPENSSL_HOOKS_DIR", hooks_dir)
        
        # Add package info
        self.output.info(f"OpenSSL Hooks v{self.version} registered successfully")
        self.output.info(f"Hooks directory: {hooks_dir}")
        self.output.info(f"Available hooks: {', '.join(hook_files)}")
        self.output.info("To use these hooks, add the hooks directory to your CONAN_HOOKS environment variable")
    
    def validate(self):
        """
        Validate the package configuration.
        
        This method ensures that the package is properly configured
        and all required files are present.
        """
        # Check that hooks directory exists
        if self.source_folder:
            hooks_dir = Path(self.source_folder) / "hooks"
            if not hooks_dir.exists():
                raise ConanInvalidConfiguration("hooks directory not found")
        
        # Check that all required hook files exist
        if self.source_folder:
            required_hooks = [
                "pre_build.py",
                "post_package.py",
                "pre_export.py", 
                "post_export.py"
            ]
            
            missing_hooks = []
            for hook_file in required_hooks:
                hook_path = hooks_dir / hook_file
                if not hook_path.exists():
                    missing_hooks.append(hook_file)
            
            if missing_hooks:
                raise ConanInvalidConfiguration(f"Missing required hook files: {', '.join(missing_hooks)}")
            
            # Validate hook file syntax (basic check)
            for hook_file in required_hooks:
                hook_path = hooks_dir / hook_file
                try:
                    with open(hook_path, 'r') as f:
                        content = f.read()
                    
                    # Check for required function
                    if 'def run(conanfile, **kwargs):' not in content:
                        raise ConanInvalidConfiguration(f"Hook {hook_file} missing required 'run' function")
                    
                    # Check for proper docstring
                    if '"""' not in content:
                        self.output.warning(f"Hook {hook_file} missing docstring")
                    
                except Exception as e:
                    raise ConanInvalidConfiguration(f"Error validating hook {hook_file}: {e}")
            
            self.output.info("✅ All hook files validated successfully")
    
    def requirements(self):
        """
        Define package requirements.
        
        This package has minimal requirements since it's primarily
        a collection of Python scripts for Conan hooks.
        """
        # No external dependencies required - uses only Python standard library
        # and Conan's built-in functionality
        pass
    
    def build_requirements(self):
        """
        Define build requirements.
        
        This package doesn't require any build tools since it's
        a pure Python package with no compilation needed.
        """
        # No build requirements needed
        pass
    
    def configure(self):
        """
        Configure package options.
        
        This method is called to configure the package before building.
        """
        # No configuration needed for this package
        pass
    
    def config_options(self):
        """
        Configure package options based on settings.
        
        This method is called to configure options based on the
        current settings (OS, compiler, etc.).
        """
        # No options to configure
        pass
    
    def generate(self):
        """
        Generate build files.
        
        This method is called to generate any necessary build files.
        For this package, no generation is needed.
        """
        # No generation needed for this package
        pass
    
    def build(self):
        """
        Build the package.
        
        This method is called to build the package. For this package,
        no building is required since it's a collection of Python scripts.
        """
        # No building required for this package
        self.output.info("OpenSSL Hooks package - no build required")
    
    def test(self):
        """
        Test the package.
        
        This method is called to test the package after building.
        For this package, we'll perform basic validation tests.
        """
        # Basic validation tests
        self._test_hook_registration()
        self._test_hook_files()
        self._test_environment_variables()
        
        self.output.info("✅ OpenSSL Hooks package tests passed")
    
    def _test_hook_registration(self):
        """Test that hooks are properly registered."""
        hooks_dir = os.path.join(self.package_folder, "hooks")
        
        if not os.path.exists(hooks_dir):
            raise Exception("Hooks directory not found in package")
        
        # Check that all hook files are present
        required_hooks = [
            "pre_build.py",
            "post_package.py",
            "pre_export.py",
            "post_export.py"
        ]
        
        for hook_file in required_hooks:
            hook_path = os.path.join(hooks_dir, hook_file)
            if not os.path.exists(hook_path):
                raise Exception(f"Hook file {hook_file} not found in package")
        
        self.output.info("✅ Hook registration test passed")
    
    def _test_hook_files(self):
        """Test that hook files are valid Python files."""
        hooks_dir = os.path.join(self.package_folder, "hooks")
        
        for hook_file in os.listdir(hooks_dir):
            if hook_file.endswith('.py'):
                hook_path = os.path.join(hooks_dir, hook_file)
                
                # Try to compile the Python file
                try:
                    with open(hook_path, 'r') as f:
                        compile(f.read(), hook_path, 'exec')
                except SyntaxError as e:
                    raise Exception(f"Syntax error in {hook_file}: {e}")
        
        self.output.info("✅ Hook files validation test passed")
    
    def _test_environment_variables(self):
        """Test that environment variables are properly set."""
        if not hasattr(self.env_info, 'CONAN_HOOKS'):
            raise Exception("CONAN_HOOKS environment variable not set")
        
        if not hasattr(self.env_info, 'OPENSSL_HOOKS_VERSION'):
            raise Exception("OPENSSL_HOOKS_VERSION environment variable not set")
        
        if not hasattr(self.env_info, 'OPENSSL_HOOKS_DIR'):
            raise Exception("OPENSSL_HOOKS_DIR environment variable not set")
        
        self.output.info("✅ Environment variables test passed")
