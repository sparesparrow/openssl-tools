#!/usr/bin/env python3
"""
OpenSSL ngapy Conan Integration Script
Integrates ngapy Conan scripts with OpenSSL project
"""

import os
import sys
from pathlib import Path

# Add the scripts directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from openssl_conan.conan.client_config import get_client_config, setup_openssl_environment
from openssl_conan.conan.artifactory_functions import configure_artifactory_for_openssl, setup_openssl_remotes
from openssl_conan.conan.conan_functions import (
    get_default_conan,
    get_conan_home,
    setup_parallel_download,
    remove_conan_lock_files
)
from openssl_conan.conan.conan_artifactory_search import search_openssl_packages


def check_prerequisites():
    """Check if prerequisites are met"""
    print("Checking prerequisites...")
    
    # Check if Conan is available
    try:
        conan_exe = get_default_conan()
        print(f"✓ Conan found: {conan_exe}")
    except Exception as e:
        print(f"✗ Conan not found: {e}")
        return False
    
    # Check if we're in an OpenSSL repository
    if not (Path.cwd() / 'conanfile.py').exists():
        print("✗ No conanfile.py found in current directory")
        print("  Please run this script from the OpenSSL repository root")
        return False
    
    print("✓ OpenSSL repository detected")
    return True


def setup_environment():
    """Setup the environment for OpenSSL Conan integration"""
    print("\nSetting up environment...")
    
    # Get client configuration
    config = get_client_config()
    print(f"Configuration loaded from: {config.get_conan_home()}")
    
    # Setup environment variables
    if setup_openssl_environment():
        print("✓ Environment variables configured")
    else:
        print("✗ Failed to setup environment")
        return False
    
    # Configure Artifactory
    try:
        configure_artifactory_for_openssl()
        print("✓ Artifactory configured")
    except Exception as e:
        print(f"✗ Failed to configure Artifactory: {e}")
        return False
    
    # Setup OpenSSL remotes
    try:
        setup_openssl_remotes()
        print("✓ OpenSSL remotes configured")
    except Exception as e:
        print(f"✗ Failed to setup remotes: {e}")
        return False
    
    # Setup parallel downloads
    try:
        setup_parallel_download()
        print("✓ Parallel downloads configured")
    except Exception as e:
        print(f"✗ Failed to setup parallel downloads: {e}")
        return False
    
    return True


def test_integration():
    """Test the integration"""
    print("\nTesting integration...")
    
    # Test Conan home
    try:
        conan_home, conan_home_short = get_conan_home()
        print(f"✓ Conan home: {conan_home}")
    except Exception as e:
        print(f"✗ Failed to get Conan home: {e}")
        return False
    
    # Test package search
    try:
        print("Searching for OpenSSL packages...")
        search_openssl_packages()
        print("✓ Package search working")
    except Exception as e:
        print(f"✗ Package search failed: {e}")
        return False
    
    # Test cache management
    try:
        remove_conan_lock_files()
        print("✓ Cache management working")
    except Exception as e:
        print(f"✗ Cache management failed: {e}")
        return False
    
    return True


def create_integration_script():
    """Create a simple integration script for users"""
    script_content = '''#!/usr/bin/env python3
"""
OpenSSL ngapy Conan Integration Helper
Simple script to use ngapy Conan integration
"""

import sys
from pathlib import Path

# Add the scripts directory to the path
sys.path.insert(0, str(Path(__file__).parent / 'scripts'))

from ngapy.conan.openssl_conan_example import main

if __name__ == '__main__':
    sys.exit(main())
'''
    
    script_path = Path.cwd() / 'openssl_conan_helper.py'
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    # Make it executable
    script_path.chmod(0o755)
    
    print(f"✓ Created integration helper script: {script_path}")
    return script_path


def print_usage_instructions():
    """Print usage instructions"""
    print("\n" + "=" * 60)
    print("OpenSSL ngapy Conan Integration Complete!")
    print("=" * 60)
    print("\nUsage Instructions:")
    print("\n1. Basic usage:")
    print("   python scripts/ngapy/conan/openssl_conan_example.py")
    print("\n2. Using the helper script:")
    print("   python openssl_conan_helper.py")
    print("\n3. Import in your own scripts:")
    print("   from ngapy.conan.conan_functions import get_default_conan")
    print("   from ngapy.conan.artifactory_functions import setup_openssl_remotes")
    print("\n4. Configuration:")
    print("   Edit environment variables or use client_config.py")
    print("\n5. Testing:")
    print("   python -m pytest scripts/ngapy/conan/test_*.py -v")
    print("\n6. Documentation:")
    print("   See docs/NGAPY_CONAN_INTEGRATION.md for detailed information")
    print("\n" + "=" * 60)


def main():
    """Main integration function"""
    print("OpenSSL ngapy Conan Integration")
    print("=" * 40)
    
    # Check prerequisites
    if not check_prerequisites():
        print("\nPrerequisites not met. Please install Conan and run from OpenSSL repository root.")
        return 1
    
    # Setup environment
    if not setup_environment():
        print("\nEnvironment setup failed.")
        return 1
    
    # Test integration
    if not test_integration():
        print("\nIntegration test failed.")
        return 1
    
    # Create helper script
    helper_script = create_integration_script()
    
    # Print usage instructions
    print_usage_instructions()
    
    print(f"\nIntegration completed successfully!")
    print(f"Helper script created: {helper_script}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())