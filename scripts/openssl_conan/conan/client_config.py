#!/usr/bin/env python3
"""
OpenSSL Client Configuration
Configuration storage for OpenSSL Conan integration
"""

import os
from pathlib import Path


class ClientConfig:
    """Client configuration for OpenSSL Conan integration"""
    
    # Application settings
    APP_NAME = 'openssl_conan_launcher'
    COMPANY_NAME = 'OpenSSL'
    
    # HTTP settings
    HTTP_TIMEOUT = 30
    MAX_DOWNLOAD_RETRIES = 3
    
    # Conan settings
    CONAN_USER_HOME = os.environ.get('CONAN_USER_HOME', str(Path.home() / '.conan2'))
    CONAN_REMOTE_NAME = os.environ.get('CONAN_REMOTE_NAME', 'conancenter')
    CONAN_REMOTE_URL = os.environ.get('CONAN_REMOTE_URL', 'https://center.conan.io')
    
    # OpenSSL specific settings
    OPENSSL_VERSION = os.environ.get('OPENSSL_VERSION', '3.5.0')
    OPENSSL_BUILD_TYPE = os.environ.get('OPENSSL_BUILD_TYPE', 'Release')
    
    # Build settings
    PARALLEL_JOBS = int(os.environ.get('CONAN_CPU_COUNT', '4'))
    ENABLE_FIPS = os.environ.get('OPENSSL_FIPS', 'False').lower() == 'true'
    ENABLE_DEMOS = os.environ.get('OPENSSL_DEMOS', 'True').lower() == 'true'
    
    # Cache settings
    CACHE_DIR = os.environ.get('CONAN_CACHE_DIR', str(Path.home() / '.conan2' / 'cache'))
    ENABLE_CACHE = os.environ.get('CONAN_ENABLE_CACHE', 'True').lower() == 'true'
    
    # Logging settings
    LOG_LEVEL = os.environ.get('CONAN_LOG_LEVEL', 'INFO')
    ENABLE_VERBOSE = os.environ.get('CONAN_VERBOSE', 'False').lower() == 'true'
    
    # Security settings
    ENABLE_SECURITY_SCAN = os.environ.get('CONAN_SECURITY_SCAN', 'True').lower() == 'true'
    ENABLE_VULNERABILITY_CHECK = os.environ.get('CONAN_VULNERABILITY_CHECK', 'True').lower() == 'true'
    
    # Update URLs (for future use)
    UPDATE_URLS = [
        "https://github.com/openssl/openssl/releases",
        "https://conan.io/center/openssl",
    ]
    
    @classmethod
    def get_conan_home(cls):
        """Get Conan home directory"""
        return Path(cls.CONAN_USER_HOME)
    
    @classmethod
    def get_cache_dir(cls):
        """Get cache directory"""
        return Path(cls.CACHE_DIR)
    
    @classmethod
    def get_build_dir(cls):
        """Get build directory"""
        return Path(cls.CONAN_USER_HOME) / 'build'
    
    @classmethod
    def get_package_dir(cls):
        """Get package directory"""
        return Path(cls.CONAN_USER_HOME) / 'packages'
    
    @classmethod
    def get_remotes_config(cls):
        """Get remotes configuration"""
        return {
            'conancenter': {
                'url': cls.CONAN_REMOTE_URL,
                'enabled': True
            }
        }
    
    @classmethod
    def get_build_options(cls):
        """Get build options for OpenSSL"""
        return {
            'shared': False,
            'fPIC': True,
            'fips': cls.ENABLE_FIPS,
            'enable_demos': cls.ENABLE_DEMOS,
            'enable_quic': True,
            'no_deprecated': False,
            'no_legacy': False,
            'enable_asan': False,
            'enable_ubsan': False,
            'enable_msan': False,
            'enable_tsan': False,
        }
    
    @classmethod
    def get_environment_variables(cls):
        """Get environment variables for Conan"""
        return {
            'CONAN_USER_HOME': cls.CONAN_USER_HOME,
            'CONAN_COLOR_DISPLAY': '1',
            'CLICOLOR_FORCE': '1',
            'CLICOLOR': '1',
            'CONAN_LOGGING_LEVEL': str(10 if cls.ENABLE_VERBOSE else 20),
            'CONAN_PRINT_RUN_COMMANDS': '1' if cls.ENABLE_VERBOSE else '0',
            'CONAN_CPU_COUNT': str(cls.PARALLEL_JOBS),
        }
    
    @classmethod
    def setup_environment(cls):
        """Setup environment variables"""
        for key, value in cls.get_environment_variables().items():
            os.environ[key] = value
    
    @classmethod
    def get_openssl_config(cls):
        """Get OpenSSL specific configuration"""
        return {
            'version': cls.OPENSSL_VERSION,
            'build_type': cls.OPENSSL_BUILD_TYPE,
            'fips': cls.ENABLE_FIPS,
            'demos': cls.ENABLE_DEMOS,
            'parallel_jobs': cls.PARALLEL_JOBS,
            'security_scan': cls.ENABLE_SECURITY_SCAN,
            'vulnerability_check': cls.ENABLE_VULNERABILITY_CHECK,
        }
    
    @classmethod
    def validate_config(cls):
        """Validate configuration"""
        errors = []
        
        # Check if Conan home exists
        if not cls.get_conan_home().exists():
            errors.append(f"Conan home directory does not exist: {cls.CONAN_USER_HOME}")
        
        # Check parallel jobs
        if cls.PARALLEL_JOBS < 1:
            errors.append(f"Invalid parallel jobs count: {cls.PARALLEL_JOBS}")
        
        # Check log level
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if cls.LOG_LEVEL.upper() not in valid_log_levels:
            errors.append(f"Invalid log level: {cls.LOG_LEVEL}")
        
        return errors
    
    @classmethod
    def print_config(cls):
        """Print current configuration"""
        print("OpenSSL Conan Configuration:")
        print(f"  App Name: {cls.APP_NAME}")
        print(f"  Company: {cls.COMPANY_NAME}")
        print(f"  Conan Home: {cls.CONAN_USER_HOME}")
        print(f"  Remote: {cls.CONAN_REMOTE_NAME} -> {cls.CONAN_REMOTE_URL}")
        print(f"  OpenSSL Version: {cls.OPENSSL_VERSION}")
        print(f"  Build Type: {cls.OPENSSL_BUILD_TYPE}")
        print(f"  Parallel Jobs: {cls.PARALLEL_JOBS}")
        print(f"  FIPS Enabled: {cls.ENABLE_FIPS}")
        print(f"  Demos Enabled: {cls.ENABLE_DEMOS}")
        print(f"  Cache Enabled: {cls.ENABLE_CACHE}")
        print(f"  Log Level: {cls.LOG_LEVEL}")
        print(f"  Verbose: {cls.ENABLE_VERBOSE}")
        print(f"  Security Scan: {cls.ENABLE_SECURITY_SCAN}")
        print(f"  Vulnerability Check: {cls.ENABLE_VULNERABILITY_CHECK}")


def get_client_config():
    """Get client configuration instance"""
    return ClientConfig()


def setup_openssl_environment():
    """Setup OpenSSL environment"""
    config = get_client_config()
    config.setup_environment()
    
    # Validate configuration
    errors = config.validate_config()
    if errors:
        print("Configuration errors:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    return True


if __name__ == '__main__':
    # Print configuration when run directly
    config = get_client_config()
    config.print_config()
    
    # Setup environment
    if setup_openssl_environment():
        print("\nEnvironment setup successful!")
    else:
        print("\nEnvironment setup failed!")
        exit(1)