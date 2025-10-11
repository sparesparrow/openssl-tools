#!/usr/bin/env python3
"""
OpenSSL SBOM (Software Bill of Materials) Generator
Generates CycloneDX SBOM for OpenSSL builds and artifacts
"""

import json
import argparse
import hashlib
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

class OpenSSLSBOMGenerator:
    """Generate SBOM for OpenSSL builds"""
    
    def __init__(self):
        self.sbom_data = {
            "bomFormat": "CycloneDX",
            "specVersion": "1.4",
            "version": 1,
            "metadata": {},
            "components": [],
            "dependencies": []
        }
    
    def load_build_info(self, build_info_path: str) -> Dict[str, Any]:
        """Load build information from JSON file"""
        with open(build_info_path, 'r') as f:
            return json.load(f)
    
    def generate_component_hash(self, file_path: str) -> str:
        """Generate SHA256 hash for a file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def add_openssl_component(self, build_info: Dict[str, Any], artifacts_dir: str) -> None:
        """Add OpenSSL as the main component"""
        version = build_info.get("version", "unknown")
        platform = build_info.get("platform", "unknown")
        
        # Find OpenSSL binary
        openssl_binary = None
        for root, dirs, files in os.walk(artifacts_dir):
            for file in files:
                if file == "openssl":
                    openssl_binary = os.path.join(root, file)
                    break
        
        component = {
            "type": "library",
            "name": "openssl",
            "version": version,
            "description": f"OpenSSL cryptographic library for {platform}",
            "purl": f"pkg:generic/openssl@{version}?platform={platform}",
            "properties": [
                {
                    "name": "platform",
                    "value": platform
                },
                {
                    "name": "build_type",
                    "value": build_info.get("package_type", "unknown")
                },
                {
                    "name": "commit_sha",
                    "value": build_info.get("commit_sha", "unknown")
                },
                {
                    "name": "build_date",
                    "value": build_info.get("build_date", "unknown")
                }
            ]
        }
        
        if openssl_binary and os.path.exists(openssl_binary):
            file_hash = self.generate_component_hash(openssl_binary)
            component["hashes"] = [
                {
                    "alg": "SHA-256",
                    "content": file_hash
                }
            ]
        
        self.sbom_data["components"].append(component)
    
    def add_dependencies(self, artifacts_dir: str) -> None:
        """Add dependency components"""
        # Common OpenSSL dependencies
        dependencies = [
            {
                "name": "zlib",
                "version": "1.2.13",
                "type": "library",
                "description": "Compression library"
            },
            {
                "name": "perl",
                "version": "5.34.0",
                "type": "application",
                "description": "Perl programming language"
            },
            {
                "name": "gcc",
                "version": "11.4.0",
                "type": "application",
                "description": "GNU Compiler Collection"
            }
        ]
        
        for dep in dependencies:
            component = {
                "type": dep["type"],
                "name": dep["name"],
                "version": dep["version"],
                "description": dep["description"],
                "purl": f"pkg:generic/{dep['name']}@{dep['version']}"
            }
            self.sbom_data["components"].append(component)
    
    def add_metadata(self, build_info: Dict[str, Any]) -> None:
        """Add metadata to SBOM"""
        self.sbom_data["metadata"] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "tools": [
                {
                    "vendor": "OpenSSL Tools",
                    "name": "SBOM Generator",
                    "version": "1.0.0"
                }
            ],
            "component": {
                "type": "application",
                "name": "openssl-build",
                "version": build_info.get("version", "unknown"),
                "description": f"OpenSSL build artifacts for {build_info.get('platform', 'unknown')}"
            }
        }
    
    def generate_sbom(self, build_info_path: str, artifacts_dir: str, output_path: str) -> None:
        """Generate complete SBOM"""
        print(f"🔍 Generating SBOM for {build_info_path}")
        
        # Load build information
        build_info = self.load_build_info(build_info_path)
        
        # Add metadata
        self.add_metadata(build_info)
        
        # Add OpenSSL component
        self.add_openssl_component(build_info, artifacts_dir)
        
        # Add dependencies
        self.add_dependencies(artifacts_dir)
        
        # Write SBOM
        with open(output_path, 'w') as f:
            json.dump(self.sbom_data, f, indent=2)
        
        print(f"✅ SBOM generated: {output_path}")
        print(f"📊 Components: {len(self.sbom_data['components'])}")

def main():
    parser = argparse.ArgumentParser(description="Generate OpenSSL SBOM")
    parser.add_argument("--build-info", required=True, help="Path to BUILD_INFO.json")
    parser.add_argument("--artifacts-dir", required=True, help="Path to artifacts directory")
    parser.add_argument("--output", required=True, help="Output SBOM file path")
    
    args = parser.parse_args()
    
    # Validate inputs
    if not os.path.exists(args.build_info):
        print(f"❌ Build info file not found: {args.build_info}")
        sys.exit(1)
    
    if not os.path.exists(args.artifacts_dir):
        print(f"❌ Artifacts directory not found: {args.artifacts_dir}")
        sys.exit(1)
    
    # Generate SBOM
    generator = OpenSSLSBOMGenerator()
    generator.generate_sbom(args.build_info, args.artifacts_dir, args.output)

if __name__ == "__main__":
    main()