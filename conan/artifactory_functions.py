#!/usr/bin/env python3
"""
OpenSSL Tools Artifactory Functions
Based on openssl-tools patterns for Conan Artifactory integration
"""

from .conan_functions import get_default_conan
from ..openssl_tools.util.execute_command import execute_command

# Configuration will be loaded from YAML files
artifactory_configuration = None


def setup_artifactory_remote():
    """Setup Artifactory as Conan remote following openssl-tools patterns"""
    try:
        # Clean existing remotes
        execute_command(f'{get_default_conan()} remote clean')

        # Add Artifactory remote
        execute_command(f'{get_default_conan()} remote add {artifactory_configuration.conan_name}'
                        f' {artifactory_configuration.conan_url}')

        # Authenticate with Artifactory
        execute_command(f'{get_default_conan()} user -p {artifactory_configuration.password} '
                        f'-r {artifactory_configuration.conan_name} '
                        f'{artifactory_configuration.user}')
        
        logging.info(f"Artifactory remote configured: {artifactory_configuration.conan_name}")
    except Exception as e:
        logging.error(f"Failed to setup Artifactory remote: {e}")
        raise


def enable_conan_remote():
    """Enable Artifactory remote"""
    execute_command(f'{get_default_conan()} remote enable {artifactory_configuration.conan_name}')


def disable_conan_remote():
    """Disable Artifactory remote"""
    execute_command(f'{get_default_conan()} remote disable {artifactory_configuration.conan_name}')