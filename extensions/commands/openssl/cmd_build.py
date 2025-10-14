#!/usr/bin/env python3
"""
OpenSSL Build Command for Conan Extension
Builds OpenSSL with Conan integration and database tracking
"""

from conan.api.conan_api import ConanAPI
from conan.api.output import ConanOutput
from conan.cli.command import conan_command
import argparse
import os
import sys
from pathlib import Path


@conan_command(group="openssl")
def build(conan_api: ConanAPI, parser, *args):
    """
    Build OpenSSL with Conan integration.
    
    This command builds OpenSSL using the configured environment and integrates
    with the database tracking system for build metrics and status reporting.
    """
    parser.add_argument("--profile", "-p", help="Conan profile to use for build")
    parser.add_argument("--config-dir", help="Configuration directory (from configure command)")
    parser.add_argument("--openssl-dir", help="OpenSSL source directory (default: openssl-source)")
    parser.add_argument("--jobs", "-j", type=int, help="Number of parallel jobs")
    parser.add_argument("--clean", action="store_true", help="Clean build before building")
    parser.add_argument("--install", action="store_true", help="Install after building")
    parser.add_argument("--test", action="store_true", help="Run tests after building")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--track-db", action="store_true", default=True, 
                       help="Track build in database (default: True)")
    
    args = parser.parse_args(*args)
    
    try:
        # Import the OpenSSL builder script
        openssl_tools_root = Path(__file__).parent.parent.parent.parent
        sys.path.insert(0, str(openssl_tools_root / "scripts" / "conan"))
        
        from openssl_builder import OpenSSLBuilder
        
        # Create builder instance
        builder = OpenSSLBuilder(
            conan_api=conan_api,
            profile=args.profile,
            config_dir=args.config_dir,
            openssl_dir=args.openssl_dir,
            jobs=args.jobs,
            clean=args.clean,
            install=args.install,
            test=args.test,
            verbose=args.verbose,
            track_db=args.track_db
        )
        
        # Execute build
        result = builder.build()
        
        if result.success:
            ConanOutput().info("✅ OpenSSL build completed successfully")
            ConanOutput().info(f"Build directory: {result.build_dir}")
            ConanOutput().info(f"Build time: {result.build_time:.2f} seconds")
            if result.test_results:
                ConanOutput().info(f"Tests: {result.test_results.passed}/{result.test_results.total} passed")
            if args.track_db and result.db_id:
                ConanOutput().info(f"Database tracking ID: {result.db_id}")
        else:
            ConanOutput().error(f"❌ OpenSSL build failed: {result.error}")
            return 1
            
    except ImportError as e:
        ConanOutput().error(f"❌ Failed to import OpenSSL builder module: {e}")
        ConanOutput().info("Make sure you're running from the openssl-tools repository")
        return 1
    except Exception as e:
        ConanOutput().error(f"❌ Unexpected error during build: {e}")
        return 1
    
    return 0
