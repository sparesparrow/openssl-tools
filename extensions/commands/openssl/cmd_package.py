#!/usr/bin/env python3
"""
OpenSSL Package Command for Conan Extension
Creates OpenSSL packages with SBOM generation and metadata
"""

from conan.api.conan_api import ConanAPI
from conan.api.output import ConanOutput
from conan.cli.command import conan_command
import argparse
import os
import sys
from pathlib import Path


@conan_command(group="openssl")
def package(conan_api: ConanAPI, parser, *args):
    """
    Package OpenSSL with SBOM generation and metadata.
    
    This command creates Conan packages from built OpenSSL binaries and generates
    Software Bill of Materials (SBOM) for supply chain security.
    """
    parser.add_argument("--profile", "-p", help="Conan profile to use for packaging")
    parser.add_argument("--build-dir", help="Build directory (from build command)")
    parser.add_argument("--openssl-dir", help="OpenSSL source directory (default: openssl-source)")
    parser.add_argument("--package-dir", help="Package output directory")
    parser.add_argument("--version", help="Package version (auto-detected if not specified)")
    parser.add_argument("--sbom", action="store_true", default=True, help="Generate SBOM (default: True)")
    parser.add_argument("--sbom-format", choices=["cyclonedx", "spdx"], default="cyclonedx", 
                       help="SBOM format")
    parser.add_argument("--sign", action="store_true", help="Sign package with cosign")
    parser.add_argument("--upload", action="store_true", help="Upload package to remote")
    parser.add_argument("--remote", help="Remote to upload to")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args(*args)
    
    try:
        # Import the OpenSSL packager script
        openssl_tools_root = Path(__file__).parent.parent.parent.parent
        sys.path.insert(0, str(openssl_tools_root / "scripts" / "conan"))
        
        from openssl_packager import OpenSSLPackager
        
        # Create packager instance
        packager = OpenSSLPackager(
            conan_api=conan_api,
            profile=args.profile,
            build_dir=args.build_dir,
            openssl_dir=args.openssl_dir,
            package_dir=args.package_dir,
            version=args.version,
            sbom=args.sbom,
            sbom_format=args.sbom_format,
            sign=args.sign,
            upload=args.upload,
            remote=args.remote,
            verbose=args.verbose
        )
        
        # Execute packaging
        result = packager.package()
        
        if result.success:
            ConanOutput().info("✅ OpenSSL packaging completed successfully")
            ConanOutput().info(f"Package directory: {result.package_dir}")
            ConanOutput().info(f"Package reference: {result.package_ref}")
            if result.sbom_file:
                ConanOutput().info(f"SBOM generated: {result.sbom_file}")
            if result.signature_file:
                ConanOutput().info(f"Package signed: {result.signature_file}")
            if result.upload_result:
                ConanOutput().info(f"Uploaded to: {result.upload_result.remote}")
        else:
            ConanOutput().error(f"❌ OpenSSL packaging failed: {result.error}")
            return 1
            
    except ImportError as e:
        ConanOutput().error(f"❌ Failed to import OpenSSL packager module: {e}")
        ConanOutput().info("Make sure you're running from the openssl-tools repository")
        return 1
    except Exception as e:
        ConanOutput().error(f"❌ Unexpected error during packaging: {e}")
        return 1
    
    return 0
