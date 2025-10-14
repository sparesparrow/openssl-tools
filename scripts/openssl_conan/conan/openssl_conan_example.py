#!/usr/bin/env python3
"""
OpenSSL Conan Integration Example
Demonstrates how to use the ngapy Conan integration for OpenSSL development
"""

import os
import sys
from pathlib import Path

# Add the scripts directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from openssl_conan.conan.conan_functions import (
    get_default_conan,
    get_conan_home,
    ConanConfiguration,
    ConanConfigurationTracker,
    install_packages_for_repository,
    download_package_for_repository,
    create_package_graph,
    setup_parallel_download,
    remove_conan_lock_files
)
from openssl_conan.conan.artifactory_functions import (
    setup_artifactory_remote,
    configure_artifactory_for_openssl,
    search_packages_in_remote,
    setup_openssl_remotes
)
from openssl_conan.conan.client_config import get_client_config, setup_openssl_environment
from openssl_conan.conan.conan_artifactory_search import search_openssl_packages


def example_basic_setup():
    """Example: Basic setup and configuration"""
    print("=== Basic Setup Example ===")
    
    # Get client configuration
    config = get_client_config()
    config.print_config()
    
    # Setup environment
    if setup_openssl_environment():
        print("✓ Environment setup successful!")
    else:
        print("✗ Environment setup failed!")
        return False
    
    # Setup Conan remotes
    configure_artifactory_for_openssl()
    print("✓ Conan remotes configured!")
    
    return True


def example_package_management():
    """Example: Package management operations"""
    print("\n=== Package Management Example ===")
    
    # Get Conan executable
    conan_exe = get_default_conan()
    print(f"Using Conan: {conan_exe}")
    
    # Get Conan home
    conan_home, conan_home_short = get_conan_home()
    print(f"Conan home: {conan_home}")
    
    # Setup parallel downloads
    setup_parallel_download()
    print("✓ Parallel downloads configured!")
    
    # Search for OpenSSL packages
    print("\nSearching for OpenSSL packages...")
    search_openssl_packages()
    
    return True


def example_repository_operations(repo_path: str):
    """Example: Repository operations"""
    print(f"\n=== Repository Operations Example ({repo_path}) ===")
    
    repo_path = Path(repo_path)
    if not repo_path.exists():
        print(f"Repository path does not exist: {repo_path}")
        return False
    
    # Check if conanfile.py exists
    conanfile_path = repo_path / 'conanfile.py'
    if not conanfile_path.exists():
        print(f"No conanfile.py found in {repo_path}")
        return False
    
    print(f"Found conanfile.py: {conanfile_path}")
    
    # Install packages for repository
    print("Installing packages for repository...")
    try:
        packages = install_packages_for_repository(str(repo_path))
        print(f"✓ Installed {len(packages)} packages")
        
        for name, (pkg_name, version, path) in packages.items():
            print(f"  - {pkg_name}/{version} -> {path}")
    
    except Exception as e:
        print(f"✗ Failed to install packages: {e}")
        return False
    
    # Create package dependency graph
    print("\nCreating package dependency graph...")
    try:
        graph_file = create_package_graph(str(repo_path))
        print(f"✓ Dependency graph created: {graph_file}")
    except Exception as e:
        print(f"✗ Failed to create dependency graph: {e}")
    
    return True


def example_remote_operations():
    """Example: Remote operations"""
    print("\n=== Remote Operations Example ===")
    
    # Setup OpenSSL remotes
    setup_openssl_remotes()
    print("✓ OpenSSL remotes configured!")
    
    # Search packages in remote
    print("\nSearching for OpenSSL packages in conancenter...")
    try:
        results = search_packages_in_remote('conancenter', 'openssl/*')
        if results:
            print("Found OpenSSL packages:")
            for result in results[:5]:  # Show first 5
                print(f"  - {result}")
        else:
            print("No OpenSSL packages found")
    except Exception as e:
        print(f"✗ Failed to search packages: {e}")
    
    return True


def example_cache_management():
    """Example: Cache management operations"""
    print("\n=== Cache Management Example ===")
    
    # Get Conan home
    conan_home, _ = get_conan_home()
    print(f"Conan home: {conan_home}")
    
    # Remove lock files
    print("Removing Conan lock files...")
    remove_conan_lock_files()
    print("✓ Lock files removed!")
    
    # Get all packages in cache
    from ngapy.conan.conan_functions import get_all_packages_in_cache
    packages = get_all_packages_in_cache()
    print(f"Packages in cache: {len(packages)}")
    
    if packages:
        print("Cached packages:")
        for package in packages[:10]:  # Show first 10
            print(f"  - {package}")
    
    return True


def example_configuration_tracking():
    """Example: Configuration tracking"""
    print("\n=== Configuration Tracking Example ===")
    
    # Create configuration tracker
    tracker = ConanConfigurationTracker()
    print(f"Configuration file: {tracker.config_path}")
    
    # Add some test packages
    tracker.packages['openssl/3.0.0'] = {'last_used': '2023-01-01'}
    tracker.packages['cmake/3.25.0'] = {'last_used': '2023-01-02'}
    tracker.save_config()
    print("✓ Test packages added to tracker")
    
    # Load configuration
    new_tracker = ConanConfigurationTracker()
    print(f"Tracked packages: {len(new_tracker.packages)}")
    
    for package, info in new_tracker.packages.items():
        print(f"  - {package}: {info}")
    
    return True


def main():
    """Main example function"""
    print("OpenSSL Conan Integration Example")
    print("=" * 50)
    
    # Example 1: Basic setup
    if not example_basic_setup():
        print("Basic setup failed, exiting...")
        return 1
    
    # Example 2: Package management
    if not example_package_management():
        print("Package management failed, continuing...")
    
    # Example 3: Repository operations (if we're in a repository)
    current_dir = Path.cwd()
    if (current_dir / 'conanfile.py').exists():
        if not example_repository_operations(str(current_dir)):
            print("Repository operations failed, continuing...")
    else:
        print("No conanfile.py found in current directory, skipping repository operations")
    
    # Example 4: Remote operations
    if not example_remote_operations():
        print("Remote operations failed, continuing...")
    
    # Example 5: Cache management
    if not example_cache_management():
        print("Cache management failed, continuing...")
    
    # Example 6: Configuration tracking
    if not example_configuration_tracking():
        print("Configuration tracking failed, continuing...")
    
    print("\n" + "=" * 50)
    print("Example completed!")
    return 0


if __name__ == '__main__':
    sys.exit(main())