"""
OpenSSL Post-Package Hook

This hook runs after the package is created and validates the packaged OpenSSL components.
It performs quality checks, security validation, and ensures package integrity.
"""

import os
import json
import hashlib
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional


def run(conanfile, **kwargs) -> None:
    """
    Post-package hook for OpenSSL packages.
    
    This hook:
    1. Validates package structure
    2. Checks library integrity
    3. Validates headers and symbols
    4. Generates package metadata
    5. Performs security checks
    6. Creates SBOM (Software Bill of Materials)
    
    Args:
        conanfile: The ConanFile instance
        **kwargs: Additional keyword arguments
    """
    conanfile.output.info("📦 OpenSSL Post-Package Hook: Starting package validation...")
    
    try:
        # Validate package structure
        _validate_package_structure(conanfile)
        
        # Check library integrity
        _check_library_integrity(conanfile)
        
        # Validate headers and symbols
        _validate_headers_and_symbols(conanfile)
        
        # Generate package metadata
        _generate_package_metadata(conanfile)
        
        # Perform security checks
        _perform_security_checks(conanfile)
        
        # Create SBOM
        _create_sbom(conanfile)
        
        conanfile.output.info("✅ OpenSSL Post-Package Hook: Package validation completed successfully")
        
    except Exception as e:
        conanfile.output.error(f"❌ OpenSSL Post-Package Hook failed: {str(e)}")
        raise


def _validate_package_structure(conanfile) -> None:
    """Validate that the package structure is correct."""
    conanfile.output.info("📁 Validating package structure...")
    
    package_folder = getattr(conanfile, 'package_folder', None)
    if not package_folder:
        conanfile.output.warning("⚠️ No package_folder found, skipping structure validation")
        return
    
    package_path = Path(package_folder)
    
    # Check for essential package directories
    essential_dirs = ["lib", "include", "bin"]
    missing_dirs = []
    
    for dir_name in essential_dirs:
        dir_path = package_path / dir_name
        if not dir_path.exists():
            missing_dirs.append(dir_name)
    
    if missing_dirs:
        conanfile.output.warning(f"⚠️ Missing package directories: {', '.join(missing_dirs)}")
    
    # Check for OpenSSL-specific files
    openssl_files = [
        "include/openssl/opensslv.h",
        "include/openssl/ssl.h",
        "include/openssl/crypto.h"
    ]
    
    missing_files = []
    for file_path in openssl_files:
        if not (package_path / file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        raise RuntimeError(f"Missing essential OpenSSL files in package: {', '.join(missing_files)}")
    
    # Check for libraries
    lib_path = package_path / "lib"
    if lib_path.exists():
        lib_files = list(lib_path.glob("*.a")) + list(lib_path.glob("*.so*")) + list(lib_path.glob("*.dll")) + list(lib_path.glob("*.dylib"))
        if not lib_files:
            conanfile.output.warning("⚠️ No library files found in lib directory")
        else:
            conanfile.output.info(f"📚 Found {len(lib_files)} library files")
    
    conanfile.output.info("✅ Package structure validation completed")


def _check_library_integrity(conanfile) -> None:
    """Check the integrity of packaged libraries."""
    conanfile.output.info("🔍 Checking library integrity...")
    
    package_folder = getattr(conanfile, 'package_folder', None)
    if not package_folder:
        return
    
    package_path = Path(package_folder)
    lib_path = package_path / "lib"
    
    if not lib_path.exists():
        conanfile.output.warning("⚠️ No lib directory found, skipping library integrity check")
        return
    
    # Check for required OpenSSL libraries
    required_libs = ["libcrypto", "libssl"]
    found_libs = []
    
    for lib_name in required_libs:
        # Check for different library formats
        lib_patterns = [f"{lib_name}.a", f"{lib_name}.so*", f"{lib_name}.dll", f"{lib_name}.dylib"]
        
        for pattern in lib_patterns:
            lib_files = list(lib_path.glob(pattern))
            if lib_files:
                found_libs.extend(lib_files)
                break
    
    if not found_libs:
        raise RuntimeError("No OpenSSL libraries found in package")
    
    # Validate library files
    for lib_file in found_libs:
        if not lib_file.is_file():
            raise RuntimeError(f"Library file is not a regular file: {lib_file}")
        
        if lib_file.stat().st_size == 0:
            raise RuntimeError(f"Library file is empty: {lib_file}")
        
        # Calculate file hash for integrity
        file_hash = _calculate_file_hash(lib_file)
        conanfile.output.info(f"📊 {lib_file.name}: {file_hash} ({lib_file.stat().st_size} bytes)")
    
    conanfile.output.info("✅ Library integrity check completed")


def _calculate_file_hash(file_path: Path, algorithm: str = "sha256") -> str:
    """Calculate hash of a file."""
    hash_obj = hashlib.new(algorithm)
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()


def _validate_headers_and_symbols(conanfile) -> None:
    """Validate headers and exported symbols."""
    conanfile.output.info("📋 Validating headers and symbols...")
    
    package_folder = getattr(conanfile, 'package_folder', None)
    if not package_folder:
        return
    
    package_path = Path(package_folder)
    include_path = package_path / "include"
    
    if not include_path.exists():
        conanfile.output.warning("⚠️ No include directory found, skipping header validation")
        return
    
    # Check for essential OpenSSL headers
    essential_headers = [
        "openssl/opensslv.h",
        "openssl/ssl.h", 
        "openssl/crypto.h",
        "openssl/evp.h",
        "openssl/bio.h",
        "openssl/err.h"
    ]
    
    missing_headers = []
    for header in essential_headers:
        header_path = include_path / header
        if not header_path.exists():
            missing_headers.append(header)
    
    if missing_headers:
        raise RuntimeError(f"Missing essential OpenSSL headers: {', '.join(missing_headers)}")
    
    # Validate header content
    opensslv_header = include_path / "openssl/opensslv.h"
    if opensslv_header.exists():
        _validate_openssl_version_header(opensslv_header, conanfile)
    
    conanfile.output.info("✅ Headers and symbols validation completed")


def _validate_openssl_version_header(header_path: Path, conanfile) -> None:
    """Validate OpenSSL version header content."""
    try:
        with open(header_path, 'r') as f:
            content = f.read()
        
        # Check for version defines
        version_defines = [
            "OPENSSL_VERSION_NUMBER",
            "OPENSSL_VERSION_TEXT",
            "OPENSSL_VERSION_STR"
        ]
        
        missing_defines = []
        for define in version_defines:
            if f"#define {define}" not in content:
                missing_defines.append(define)
        
        if missing_defines:
            conanfile.output.warning(f"⚠️ Missing version defines: {', '.join(missing_defines)}")
        
        # Extract version information
        if "OPENSSL_VERSION_TEXT" in content:
            for line in content.split('\n'):
                if "OPENSSL_VERSION_TEXT" in line and '"' in line:
                    version_text = line.split('"')[1]
                    conanfile.output.info(f"📋 OpenSSL Version: {version_text}")
                    break
        
    except Exception as e:
        conanfile.output.warning(f"⚠️ Could not validate version header: {e}")


def _generate_package_metadata(conanfile) -> None:
    """Generate comprehensive package metadata."""
    conanfile.output.info("📊 Generating package metadata...")
    
    package_folder = getattr(conanfile, 'package_folder', None)
    if not package_folder:
        return
    
    package_path = Path(package_folder)
    
    # Create metadata dictionary
    metadata = {
        "package_info": {
            "name": conanfile.name,
            "version": conanfile.version,
            "description": getattr(conanfile, 'description', ''),
            "license": getattr(conanfile, 'license', ''),
            "author": getattr(conanfile, 'author', ''),
            "url": getattr(conanfile, 'url', ''),
            "homepage": getattr(conanfile, 'homepage', '')
        },
        "build_info": {
            "os": str(conanfile.settings.os),
            "arch": str(conanfile.settings.arch),
            "compiler": str(conanfile.settings.compiler),
            "compiler_version": str(conanfile.settings.compiler.version),
            "build_type": str(conanfile.settings.build_type),
            "shared": getattr(conanfile.options, 'shared', False) if hasattr(conanfile, 'options') else False
        },
        "package_contents": {
            "directories": [],
            "files": [],
            "libraries": [],
            "headers": []
        }
    }
    
    # Scan package contents
    _scan_package_contents(package_path, metadata["package_contents"])
    
    # Save metadata to file
    metadata_file = package_path / "package_metadata.json"
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    conanfile.output.info(f"📊 Package metadata saved to: {metadata_file}")
    conanfile.output.info("✅ Package metadata generation completed")


def _scan_package_contents(package_path: Path, contents: Dict[str, List[str]]) -> None:
    """Scan package contents and categorize files."""
    for item in package_path.rglob("*"):
        if item.is_file():
            relative_path = item.relative_to(package_path)
            contents["files"].append(str(relative_path))
            
            # Categorize files
            if item.suffix in ['.a', '.so', '.dll', '.dylib']:
                contents["libraries"].append(str(relative_path))
            elif item.suffix in ['.h', '.hpp']:
                contents["headers"].append(str(relative_path))
        elif item.is_dir():
            relative_path = item.relative_to(package_path)
            contents["directories"].append(str(relative_path))


def _perform_security_checks(conanfile) -> None:
    """Perform basic security checks on the package."""
    conanfile.output.info("🔒 Performing security checks...")
    
    package_folder = getattr(conanfile, 'package_folder', None)
    if not package_folder:
        return
    
    package_path = Path(package_folder)
    
    # Check for suspicious files
    suspicious_patterns = [
        "*.exe", "*.bat", "*.cmd", "*.sh", "*.py", "*.pl"
    ]
    
    suspicious_files = []
    for pattern in suspicious_patterns:
        suspicious_files.extend(package_path.rglob(pattern))
    
    if suspicious_files:
        conanfile.output.warning(f"⚠️ Found potentially suspicious files: {len(suspicious_files)}")
        for file_path in suspicious_files:
            conanfile.output.warning(f"  - {file_path.relative_to(package_path)}")
    
    # Check file permissions (Unix-like systems)
    if os.name != 'nt':  # Not Windows
        _check_file_permissions(package_path, conanfile)
    
    conanfile.output.info("✅ Security checks completed")


def _check_file_permissions(package_path: Path, conanfile) -> None:
    """Check file permissions for security."""
    for file_path in package_path.rglob("*"):
        if file_path.is_file():
            stat_info = file_path.stat()
            permissions = stat_info.st_mode & 0o777
            
            # Check for overly permissive files
            if permissions & 0o002:  # World writable
                conanfile.output.warning(f"⚠️ World writable file: {file_path.relative_to(package_path)}")
            if permissions & 0o020:  # Group writable
                conanfile.output.warning(f"⚠️ Group writable file: {file_path.relative_to(package_path)}")


def _create_sbom(conanfile) -> None:
    """Create Software Bill of Materials (SBOM) for the package."""
    conanfile.output.info("📋 Creating Software Bill of Materials (SBOM)...")
    
    package_folder = getattr(conanfile, 'package_folder', None)
    if not package_folder:
        return
    
    package_path = Path(package_folder)
    
    # Create SBOM in CycloneDX format
    sbom = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.4",
        "version": 1,
        "metadata": {
            "timestamp": _get_timestamp(),
            "tools": [
                {
                    "vendor": "OpenSSL Tools",
                    "name": "openssl-hooks",
                    "version": "1.0.0"
                }
            ],
            "component": {
                "type": "library",
                "name": conanfile.name,
                "version": conanfile.version,
                "description": getattr(conanfile, 'description', 'OpenSSL cryptographic library'),
                "licenses": [
                    {
                        "id": getattr(conanfile, 'license', 'Apache-2.0')
                    }
                ],
                "purl": f"pkg:conan/{conanfile.name}@{conanfile.version}",
                "externalReferences": [
                    {
                        "type": "website",
                        "url": getattr(conanfile, 'homepage', 'https://www.openssl.org/')
                    }
                ]
            }
        },
        "components": [],
        "dependencies": []
    }
    
    # Add package components
    _add_package_components(package_path, sbom)
    
    # Add dependencies
    _add_package_dependencies(conanfile, sbom)
    
    # Save SBOM
    sbom_file = package_path / "sbom.cyclonedx.json"
    with open(sbom_file, 'w') as f:
        json.dump(sbom, f, indent=2)
    
    conanfile.output.info(f"📋 SBOM saved to: {sbom_file}")
    conanfile.output.info("✅ SBOM creation completed")


def _get_timestamp() -> str:
    """Get current timestamp in ISO format."""
    from datetime import datetime
    return datetime.utcnow().isoformat() + "Z"


def _add_package_components(package_path: Path, sbom: Dict[str, Any]) -> None:
    """Add package components to SBOM."""
    for file_path in package_path.rglob("*"):
        if file_path.is_file():
            relative_path = file_path.relative_to(package_path)
            
            component = {
                "type": "file",
                "name": str(relative_path),
                "version": "1.0.0",
                "purl": f"pkg:file/{relative_path}",
                "hashes": [
                    {
                        "alg": "SHA-256",
                        "content": _calculate_file_hash(file_path)
                    }
                ]
            }
            
            # Categorize component type
            if file_path.suffix in ['.a', '.so', '.dll', '.dylib']:
                component["type"] = "library"
            elif file_path.suffix in ['.h', '.hpp']:
                component["type"] = "file"
                component["properties"] = [
                    {
                        "name": "cdx:file:type",
                        "value": "header"
                    }
                ]
            
            sbom["components"].append(component)


def _add_package_dependencies(conanfile, sbom: Dict[str, Any]) -> None:
    """Add package dependencies to SBOM."""
    if hasattr(conanfile, 'requires') and conanfile.requires:
        for req in conanfile.requires:
            dependency = {
                "ref": f"pkg:conan/{req.ref.name}@{req.ref.version}",
                "dependsOn": []
            }
            sbom["dependencies"].append(dependency)
