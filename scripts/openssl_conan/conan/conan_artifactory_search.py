#!/usr/bin/env python3
"""
OpenSSL Conan Artifactory Search
Advanced Conan Artifactory search for OpenSSL project
"""

import argparse
import os
import re
import sys
from pathlib import Path

from .conan_functions import get_default_conan, execute_command
from .client_config import get_client_config


def search_package_pattern(package, version_pattern, remote='conancenter'):
    """Search for packages matching a pattern"""
    rc, return_versions = execute_command(
        f'{get_default_conan()} search {package}/{version_pattern}@ -r {remote} --raw')
    return rc, return_versions


def search_package_all(package, remote='conancenter'):
    """Search for all versions of a package"""
    rc, return_versions = execute_command(
        f'{get_default_conan()} search {package} -r {remote} --raw')
    return rc, return_versions


def get_latest_package(package, version_pattern, remote='conancenter'):
    """Get the latest version of a package matching a pattern"""
    rc, return_versions = search_package_pattern(package, version_pattern, remote)
    if rc == 0 and return_versions:
        # Filter out warning lines
        versions = [v for v in return_versions if not v.startswith('WARN')]
        if versions:
            sorted_list = sorted(versions)
            return sorted_list[-1]
    return ''


def search_openssl_packages():
    """Search for OpenSSL related packages"""
    openssl_packages = [
        'openssl',
        'openssl/1.1.1',
        'openssl/3.0',
        'openssl/3.1',
        'openssl/3.2',
        'openssl/3.3',
        'openssl/3.4',
        'openssl/3.5',
    ]
    
    print("Searching for OpenSSL packages...")
    for package in openssl_packages:
        rc, versions = search_package_all(package)
        if rc == 0 and versions:
            print(f"\n{package}:")
            for version in versions[:5]:  # Show first 5 versions
                print(f"  {version}")
        else:
            print(f"\n{package}: No versions found")


def search_dependencies(package_name):
    """Search for dependencies of a package"""
    print(f"Searching for dependencies of {package_name}...")
    rc, output = execute_command(f'{get_default_conan()} info {package_name}@ --graph')
    if rc == 0:
        print("Dependency graph:")
        for line in output:
            print(f"  {line}")
    else:
        print("Could not retrieve dependency information")


def search_packages_by_keyword(keyword):
    """Search for packages by keyword"""
    print(f"Searching for packages containing '{keyword}'...")
    rc, output = execute_command(f'{get_default_conan()} search {keyword} --raw')
    if rc == 0:
        packages = [p for p in output if not p.startswith('WARN')]
        if packages:
            print(f"Found {len(packages)} packages:")
            for package in packages[:10]:  # Show first 10
                print(f"  {package}")
        else:
            print("No packages found")
    else:
        print("Search failed")


class Options:
    """Command line options"""
    conanfile_path = Path()
    patterns = ''
    git_commit = ''
    search_keyword = ''
    show_dependencies = False


def prepare_arguments(args):
    """Prepare command line arguments"""
    parser = argparse.ArgumentParser(
        description='OpenSSL Conan package search and management tool')
    
    parser.add_argument(
        '-c', '--conanfile',
        dest='conanfile_path',
        help='Conanfile Path',
        default=Path(os.getcwd()) / 'conanfile.py'
    )
    
    parser.add_argument(
        '-p', '--patterns',
        dest='patterns',
        help='Package patterns to search (semicolon separated)',
        default=''
    )
    
    parser.add_argument(
        '-k', '--keyword',
        dest='search_keyword',
        help='Search packages by keyword',
        default=''
    )
    
    parser.add_argument(
        '-d', '--dependencies',
        dest='show_dependencies',
        action='store_true',
        help='Show dependencies for a package'
    )
    
    parser.add_argument(
        '--openssl',
        action='store_true',
        help='Search for OpenSSL related packages'
    )
    
    parser.add_argument(
        '--remote',
        dest='remote',
        help='Remote to search in',
        default='conancenter'
    )
    
    parser.add_argument(
        '--latest',
        action='store_true',
        help='Show only latest versions'
    )
    
    options = parser.parse_args(args)
    return options


def update_conanfile_with_latest_packages(conanfile_path, patterns, remote='conancenter'):
    """Update conanfile.py with latest package versions"""
    patterns_list = patterns.split(';')
    new_packages = []
    
    for pattern in patterns_list:
        if '/' in pattern:
            package, version = pattern.split('/')
            latest = get_latest_package(package, version, remote)
            if latest:
                new_packages.append(latest)
                print(f"Latest version of {package}: {latest}")
            else:
                print(f"Could not find latest version for {package}")
        else:
            print(f"Invalid pattern format: {pattern}")
    
    if not new_packages:
        print("No packages to update")
        return
    
    # Read conanfile
    with open(conanfile_path, 'r') as conanfile:
        conanfile_content = conanfile.read()
    
    # Update package versions
    for new_package in new_packages:
        package, version = new_package.split('/')
        # Update in requirements
        conanfile_content = re.sub(
            f"'{package}/[^']+'", 
            f"'{package}/{version}'", 
            conanfile_content
        )
        # Update in build_requires
        conanfile_content = re.sub(
            f'"{package}/[^"]+"', 
            f'"{package}/{version}"', 
            conanfile_content
        )
    
    # Write updated conanfile
    with open(conanfile_path, 'w') as conanfile:
        conanfile.write(conanfile_content)
    
    print(f"Updated {conanfile_path} with latest package versions")


def run(args: list, external_options: Options = None):
    """Main run function"""
    if external_options is None:
        options = prepare_arguments(args)
    else:
        options = external_options
    
    # Setup environment
    config = get_client_config()
    config.setup_environment()
    
    if options.openssl:
        search_openssl_packages()
        return
    
    if options.search_keyword:
        search_packages_by_keyword(options.search_keyword)
        return
    
    if options.show_dependencies and options.patterns:
        patterns = options.patterns.split(';')
        for pattern in patterns:
            if '/' in pattern:
                package, version = pattern.split('/')
                search_dependencies(f"{package}/{version}")
            else:
                search_dependencies(pattern)
        return
    
    if options.patterns:
        if options.latest:
            # Show latest versions
            patterns = options.patterns.split(';')
            for pattern in patterns:
                if '/' in pattern:
                    package, version = pattern.split('/')
                    latest = get_latest_package(package, version, options.remote)
                    if latest:
                        print(f"{package}: {latest}")
                    else:
                        print(f"{package}: No versions found")
                else:
                    print(f"Invalid pattern format: {pattern}")
        else:
            # Update conanfile
            update_conanfile_with_latest_packages(
                options.conanfile_path, 
                options.patterns, 
                options.remote
            )
    else:
        print("No action specified. Use --help for usage information.")


def main():
    """Main entry point"""
    run(sys.argv[1:])


if __name__ == '__main__':
    main()