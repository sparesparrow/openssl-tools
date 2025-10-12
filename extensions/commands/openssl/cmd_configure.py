#!/usr/bin/env python3
"""
OpenSSL Configure Command for Conan Extension
Configures OpenSSL build environment with platform detection and Conan profile integration
"""

from conan.api.conan_api import ConanAPI
from conan.api.output import ConanOutput
from conan.cli.command import conan_command
import argparse
import os
import sys
from pathlib import Path


@conan_command(group="openssl")
def configure(conan_api: ConanAPI, parser, *args):
    """
    Configure OpenSSL build environment.
    
    This command sets up the OpenSSL build configuration using Conan profiles
    and platform detection. It integrates with the existing conan_orchestrator.py
    for advanced build management.
    """
    parser.add_argument("--profile", "-p", help="Conan profile to use for configuration")
    parser.add_argument("--platform", help="Target platform (auto-detected if not specified)")
    parser.add_argument("--compiler", help="Compiler to use (auto-detected if not specified)")
    parser.add_argument("--arch", help="Target architecture (auto-detected if not specified)")
    parser.add_argument("--build-type", choices=["Debug", "Release", "RelWithDebInfo", "MinSizeRel"], 
                       default="Release", help="Build type")
    parser.add_argument("--fips", action="store_true", help="Enable FIPS mode")
    parser.add_argument("--shared", action="store_true", default=True, help="Build shared libraries")
    parser.add_argument("--static", action="store_true", help="Build static libraries")
    parser.add_argument("--openssl-dir", help="OpenSSL source directory (default: openssl-source)")
    parser.add_argument("--output-dir", help="Output directory for configuration")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args(*args)
    
    try:
        # Import the OpenSSL configuration script
        openssl_tools_root = Path(__file__).parent.parent.parent.parent
        sys.path.insert(0, str(openssl_tools_root / "scripts" / "conan"))
        
        from openssl_configure import OpenSSLConfigurator
        
        # Create configurator instance
        configurator = OpenSSLConfigurator(
            conan_api=conan_api,
            profile=args.profile,
            platform=args.platform,
            compiler=args.compiler,
            arch=args.arch,
            build_type=args.build_type,
            fips=args.fips,
            shared=args.shared,
            static=args.static,
            openssl_dir=args.openssl_dir,
            output_dir=args.output_dir,
            verbose=args.verbose
        )
        
        # Execute configuration
        result = configurator.configure()
        
        if result.success:
            ConanOutput().info("✅ OpenSSL configuration completed successfully")
            ConanOutput().info(f"Configuration directory: {result.config_dir}")
            ConanOutput().info(f"Profile used: {result.profile_used}")
            if args.verbose:
                ConanOutput().info(f"Configure command: {result.configure_command}")
        else:
            ConanOutput().error(f"❌ OpenSSL configuration failed: {result.error}")
            return 1
            
    except ImportError as e:
        ConanOutput().error(f"❌ Failed to import OpenSSL configuration module: {e}")
        ConanOutput().info("Make sure you're running from the openssl-tools repository")
        return 1
    except Exception as e:
        ConanOutput().error(f"❌ Unexpected error during configuration: {e}")
        return 1
    
    return 0
