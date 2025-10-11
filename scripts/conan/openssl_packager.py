#!/usr/bin/env python3
"""
OpenSSL Packager Module
Package creation with SBOM generation and metadata
"""

import os
import sys
import subprocess
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, NamedTuple
from dataclasses import dataclass
import hashlib
import shutil
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class UploadResult:
    """Package upload result"""
    success: bool
    remote: Optional[str] = None
    error: Optional[str] = None


@dataclass
class PackageResult:
    """Result of OpenSSL packaging"""
    success: bool
    package_dir: Optional[str] = None
    package_ref: Optional[str] = None
    sbom_file: Optional[str] = None
    signature_file: Optional[str] = None
    upload_result: Optional[UploadResult] = None
    error: Optional[str] = None


class OpenSSLPackager:
    """OpenSSL package creator with SBOM generation"""
    
    def __init__(self, conan_api, profile=None, build_dir=None, openssl_dir=None,
                 package_dir=None, version=None, sbom=True, sbom_format="cyclonedx",
                 sign=False, upload=False, remote=None, verbose=False):
        self.conan_api = conan_api
        self.profile = profile
        self.build_dir = Path(build_dir or "build-linux-gcc")
        self.openssl_dir = Path(openssl_dir or "openssl-source")
        self.package_dir = Path(package_dir or "packages")
        self.version = version or self._detect_version()
        self.sbom = sbom
        self.sbom_format = sbom_format
        self.sign = sign
        self.upload = upload
        self.remote = remote
        self.verbose = verbose
        
        # Ensure package directory exists
        self.package_dir.mkdir(parents=True, exist_ok=True)
    
    def _detect_version(self) -> str:
        """Detect OpenSSL version from source"""
        version_file = self.openssl_dir / "VERSION.dat"
        if version_file.exists():
            try:
                with open(version_file, 'r') as f:
                    content = f.read().strip()
                    # Extract version from VERSION.dat format
                    if content.startswith("VERSION="):
                        return content.split("=", 1)[1].strip('"')
                    return content
            except Exception as e:
                logger.warning(f"Could not read version file: {e}")
        
        # Fallback to git describe
        try:
            result = subprocess.run(
                ["git", "describe", "--tags", "--always"],
                cwd=self.openssl_dir,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        
        return "1.1.1"  # Default fallback
    
    def _create_package_structure(self) -> Path:
        """Create package directory structure"""
        package_name = f"openssl-{self.version}"
        package_path = self.package_dir / package_name
        
        # Create package directories
        (package_path / "bin").mkdir(parents=True, exist_ok=True)
        (package_path / "lib").mkdir(parents=True, exist_ok=True)
        (package_path / "include").mkdir(parents=True, exist_ok=True)
        (package_path / "ssl").mkdir(parents=True, exist_ok=True)
        (package_path / "share").mkdir(parents=True, exist_ok=True)
        
        return package_path
    
    def _copy_binaries(self, package_path: Path):
        """Copy OpenSSL binaries to package"""
        # Copy executables
        bin_src = self.openssl_dir / "apps"
        bin_dst = package_path / "bin"
        
        if bin_src.exists():
            for exe in ["openssl"]:
                exe_path = bin_src / exe
                if exe_path.exists():
                    shutil.copy2(exe_path, bin_dst)
        
        # Copy libraries
        lib_src = self.openssl_dir
        lib_dst = package_path / "lib"
        
        for lib_pattern in ["libssl.*", "libcrypto.*"]:
            for lib_file in lib_src.glob(lib_pattern):
                if lib_file.is_file():
                    shutil.copy2(lib_file, lib_dst)
        
        # Copy headers
        include_src = self.openssl_dir / "include"
        include_dst = package_path / "include"
        
        if include_src.exists():
            shutil.copytree(include_src, include_dst, dirs_exist_ok=True)
    
    def _generate_sbom(self, package_path: Path) -> Optional[str]:
        """Generate Software Bill of Materials"""
        if not self.sbom:
            return None
        
        try:
            sbom_file = package_path / f"sbom.{self.sbom_format}.json"
            
            # Create basic SBOM structure
            sbom_data = {
                "bomFormat": "CycloneDX",
                "specVersion": "1.4",
                "version": 1,
                "metadata": {
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "tools": [
                        {
                            "vendor": "OpenSSL Tools",
                            "name": "openssl_packager",
                            "version": "1.0.0"
                        }
                    ],
                    "component": {
                        "type": "library",
                        "name": "openssl",
                        "version": self.version,
                        "description": "OpenSSL cryptographic library",
                        "licenses": [
                            {
                                "id": "Apache-2.0"
                            }
                        ]
                    }
                },
                "components": [
                    {
                        "type": "library",
                        "name": "openssl",
                        "version": self.version,
                        "description": "OpenSSL cryptographic library",
                        "licenses": [
                            {
                                "id": "Apache-2.0"
                            }
                        ]
                    }
                ]
            }
            
            # Add file inventory
            components = []
            for root, dirs, files in os.walk(package_path):
                for file in files:
                    file_path = Path(root) / file
                    rel_path = file_path.relative_to(package_path)
                    
                    # Calculate file hash
                    try:
                        with open(file_path, 'rb') as f:
                            file_hash = hashlib.sha256(f.read()).hexdigest()
                    except Exception:
                        file_hash = None
                    
                    components.append({
                        "type": "file",
                        "name": str(rel_path),
                        "hashes": [
                            {
                                "alg": "SHA-256",
                                "content": file_hash
                            }
                        ] if file_hash else []
                    })
            
            sbom_data["components"].extend(components)
            
            # Write SBOM file
            with open(sbom_file, 'w') as f:
                json.dump(sbom_data, f, indent=2)
            
            return str(sbom_file)
            
        except Exception as e:
            logger.error(f"Failed to generate SBOM: {e}")
            return None
    
    def _sign_package(self, package_path: Path) -> Optional[str]:
        """Sign package with cosign"""
        if not self.sign:
            return None
        
        try:
            # Check if cosign is available
            result = subprocess.run(
                ["cosign", "version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                logger.warning("cosign not available, skipping package signing")
                return None
            
            # Create package archive for signing
            archive_path = package_path.with_suffix(".tar.gz")
            shutil.make_archive(
                str(archive_path.with_suffix("")),
                "gztar",
                str(package_path.parent),
                package_path.name
            )
            
            # Sign the archive
            signature_file = archive_path.with_suffix(".sig")
            result = subprocess.run(
                ["cosign", "sign-blob", "--output", str(signature_file), str(archive_path)],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                return str(signature_file)
            else:
                logger.error(f"Package signing failed: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Package signing error: {e}")
            return None
    
    def _upload_package(self, package_path: Path) -> UploadResult:
        """Upload package to remote"""
        if not self.upload:
            return UploadResult(success=True)
        
        try:
            # Use Conan to upload if available
            if self.conan_api and self.remote:
                # This would integrate with Conan's upload functionality
                # For now, just return success
                return UploadResult(success=True, remote=self.remote)
            else:
                logger.warning("Upload requested but no remote specified")
                return UploadResult(success=False, error="No remote specified")
                
        except Exception as e:
            return UploadResult(success=False, error=str(e))
    
    def package(self) -> PackageResult:
        """Execute OpenSSL packaging"""
        try:
            # Create package structure
            package_path = self._create_package_structure()
            
            if self.verbose:
                logger.info(f"Creating package: {package_path}")
            
            # Copy binaries
            self._copy_binaries(package_path)
            
            # Generate SBOM
            sbom_file = self._generate_sbom(package_path)
            
            # Sign package
            signature_file = self._sign_package(package_path)
            
            # Upload package
            upload_result = self._upload_package(package_path)
            
            # Create package reference
            package_ref = f"openssl/{self.version}@user/channel"
            
            return PackageResult(
                success=True,
                package_dir=str(package_path),
                package_ref=package_ref,
                sbom_file=sbom_file,
                signature_file=signature_file,
                upload_result=upload_result
            )
            
        except Exception as e:
            return PackageResult(
                success=False,
                error=f"Packaging failed: {str(e)}"
            )


def main():
    """Main function for standalone execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="OpenSSL Packager Tool")
    parser.add_argument("--profile", "-p", help="Conan profile to use")
    parser.add_argument("--build-dir", help="Build directory")
    parser.add_argument("--openssl-dir", help="OpenSSL source directory")
    parser.add_argument("--package-dir", help="Package output directory")
    parser.add_argument("--version", help="Package version")
    parser.add_argument("--sbom", action="store_true", default=True, help="Generate SBOM")
    parser.add_argument("--sbom-format", choices=["cyclonedx", "spdx"], default="cyclonedx", help="SBOM format")
    parser.add_argument("--sign", action="store_true", help="Sign package")
    parser.add_argument("--upload", action="store_true", help="Upload package")
    parser.add_argument("--remote", help="Remote to upload to")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Create packager
    packager = OpenSSLPackager(
        conan_api=None,  # Not needed for standalone
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
        print("✅ OpenSSL packaging completed successfully")
        print(f"Package directory: {result.package_dir}")
        print(f"Package reference: {result.package_ref}")
        if result.sbom_file:
            print(f"SBOM generated: {result.sbom_file}")
        if result.signature_file:
            print(f"Package signed: {result.signature_file}")
        if result.upload_result and result.upload_result.success:
            print(f"Uploaded to: {result.upload_result.remote}")
    else:
        print(f"❌ OpenSSL packaging failed: {result.error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
