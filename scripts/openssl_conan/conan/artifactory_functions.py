#!/usr/bin/env python3
"""
OpenSSL Artifactory Functions
Advanced Artifactory functions for OpenSSL project
"""

import os
from pathlib import Path

from .conan_functions import get_default_conan, execute_command


class ArtifactoryConfiguration:
    """Artifactory configuration for OpenSSL project"""
    
    def __init__(self):
        # Default configuration - can be overridden by environment variables
        self.nga_conan_name = os.environ.get('CONAN_REMOTE_NAME', 'conancenter')
        self.nga_conan_url = os.environ.get('CONAN_REMOTE_URL', 'https://center.conan.io')
        self.user = os.environ.get('CONAN_USER', '')
        self.password = os.environ.get('CONAN_PASSWORD', '')


# Global configuration instance
artifactory_configuration = ArtifactoryConfiguration()


def setup_artifactory_remote():
    """Setup Artifactory remote for Conan"""
    # Clean existing remotes
    execute_command(f'{get_default_conan()} remote clean')
    
    # Add the remote
    execute_command(f'{get_default_conan()} remote add {artifactory_configuration.nga_conan_name}'
                    f' {artifactory_configuration.nga_conan_url}')
    
    # Set user credentials if provided
    if artifactory_configuration.user and artifactory_configuration.password:
        execute_command(f'{get_default_conan()} user -p {artifactory_configuration.password} '
                        f'-r {artifactory_configuration.nga_conan_name} '
                        f'{artifactory_configuration.user}')


def enable_conan_remote():
    """Enable Conan remote"""
    execute_command(f'{get_default_conan()} remote enable {artifactory_configuration.nga_conan_name}')


def disable_conan_remote():
    """Disable Conan remote"""
    execute_command(f'{get_default_conan()} remote disable {artifactory_configuration.nga_conan_name}')


def list_remotes():
    """List all Conan remotes"""
    rc, output = execute_command(f'{get_default_conan()} remote list')
    return output


def add_remote(name, url, user=None, password=None):
    """Add a new Conan remote"""
    execute_command(f'{get_default_conan()} remote add {name} {url}')
    
    if user and password:
        execute_command(f'{get_default_conan()} user -p {password} -r {name} {user}')


def remove_remote(name):
    """Remove a Conan remote"""
    execute_command(f'{get_default_conan()} remote remove {name}')


def update_remote(name, url):
    """Update a Conan remote URL"""
    execute_command(f'{get_default_conan()} remote update {name} {url}')


def set_remote_credentials(name, user, password):
    """Set credentials for a remote"""
    execute_command(f'{get_default_conan()} user -p {password} -r {name} {user}')


def configure_artifactory_for_openssl():
    """Configure Artifactory specifically for OpenSSL project"""
    # Set up default Conan Center remote
    setup_artifactory_remote()
    
    # Add additional remotes if needed
    additional_remotes = [
        ('bincrafters', 'https://bincrafters.jfrog.io/artifactory/api/conan/public-conan'),
        ('conan-community', 'https://api.bintray.com/conan/conan-community/conan'),
    ]
    
    for name, url in additional_remotes:
        try:
            add_remote(name, url)
        except Exception as e:
            print(f"Warning: Could not add remote {name}: {e}")


def search_packages_in_remote(remote_name, package_pattern):
    """Search for packages in a specific remote"""
    rc, output = execute_command(f'{get_default_conan()} search {package_pattern} -r {remote_name}')
    return output


def upload_package_to_remote(package_ref, remote_name):
    """Upload package to remote"""
    rc, output = execute_command(f'{get_default_conan()} upload {package_ref} -r {remote_name} --confirm')
    return rc == 0


def download_package_from_remote(package_ref, remote_name):
    """Download package from remote"""
    rc, output = execute_command(f'{get_default_conan()} download {package_ref} -r {remote_name}')
    return rc == 0


def get_remote_info(remote_name):
    """Get information about a remote"""
    rc, output = execute_command(f'{get_default_conan()} remote list')
    for line in output:
        if remote_name in line:
            return line.strip()
    return None


def setup_openssl_remotes():
    """Setup all necessary remotes for OpenSSL development"""
    remotes = [
        ('conancenter', 'https://center.conan.io'),
        ('bincrafters', 'https://bincrafters.jfrog.io/artifactory/api/conan/public-conan'),
    ]
    
    for name, url in remotes:
        try:
            add_remote(name, url)
            print(f"Added remote: {name} -> {url}")
        except Exception as e:
            print(f"Warning: Could not add remote {name}: {e}")


def configure_for_ci_environment():
    """Configure Artifactory for CI environment"""
    # Set up basic remotes
    setup_openssl_remotes()
    
    # Configure parallel downloads
    from .conan_functions import setup_parallel_download
    setup_parallel_download()
    
    # Set up logging
    os.environ['CONAN_LOGGING_LEVEL'] = '10'  # Debug level
    os.environ['CONAN_PRINT_RUN_COMMANDS'] = '1'