#!/usr/bin/env python3
"""
OpenSSL Documentation Command for Conan Extension
Generates and formats OpenSSL documentation from sources
"""

from conan.api.conan_api import ConanAPI
from conan.api.output import ConanOutput
from conan.cli.command import conan_command
import argparse
import os
import sys
from pathlib import Path


@conan_command(group="openssl")
def docs(conan_api: ConanAPI, parser, *args):
    """
    Generate OpenSSL documentation from sources.
    
    This command extracts and formats OpenSSL documentation from source files,
    including POD manpages, API documentation, and user guides.
    """
    parser.add_argument("--openssl-dir", help="OpenSSL source directory (default: openssl-source)")
    parser.add_argument("--output-dir", help="Documentation output directory")
    parser.add_argument("--format", choices=["html", "pdf", "man", "markdown"], 
                       default="html", help="Output format")
    parser.add_argument("--sections", nargs="+", 
                       choices=["man", "api", "guide", "faq", "all"], 
                       default=["all"], help="Documentation sections to generate")
    parser.add_argument("--language", default="en", help="Documentation language")
    parser.add_argument("--template", help="Custom template directory")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args(*args)
    
    try:
        # Import the OpenSSL documentation generator script
        openssl_tools_root = Path(__file__).parent.parent.parent.parent
        sys.path.insert(0, str(openssl_tools_root / "scripts" / "conan"))
        
        from openssl_docs_generator import OpenSSLDocsGenerator
        
        # Create generator instance
        generator = OpenSSLDocsGenerator(
            conan_api=conan_api,
            openssl_dir=args.openssl_dir,
            output_dir=args.output_dir,
            format=args.format,
            sections=args.sections,
            language=args.language,
            template=args.template,
            verbose=args.verbose
        )
        
        # Execute documentation generation
        result = generator.generate()
        
        if result.success:
            ConanOutput().info("✅ OpenSSL documentation generation completed successfully")
            ConanOutput().info(f"Output directory: {result.output_dir}")
            ConanOutput().info(f"Generated files: {len(result.generated_files)}")
            if args.verbose:
                for file in result.generated_files:
                    ConanOutput().info(f"  - {file}")
        else:
            ConanOutput().error(f"❌ OpenSSL documentation generation failed: {result.error}")
            return 1
            
    except ImportError as e:
        ConanOutput().error(f"❌ Failed to import OpenSSL documentation generator module: {e}")
        ConanOutput().info("Make sure you're running from the openssl-tools repository")
        return 1
    except Exception as e:
        ConanOutput().error(f"❌ Unexpected error during documentation generation: {e}")
        return 1
    
    return 0
