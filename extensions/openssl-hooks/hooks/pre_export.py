"""
OpenSSL Pre-Export Hook

This hook runs before the package is exported to a Conan remote and prepares
the export by validating the recipe, checking dependencies, and preparing metadata.
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional


def run(conanfile, **kwargs) -> None:
    """
    Pre-export hook for OpenSSL packages.
    
    This hook:
    1. Validates the Conan recipe
    2. Checks recipe dependencies
    3. Validates package metadata
    4. Prepares export metadata
    5. Validates license compliance
    6. Checks for security issues in recipe
    
    Args:
        conanfile: The ConanFile instance
        **kwargs: Additional keyword arguments
    """
    conanfile.output.info("📤 OpenSSL Pre-Export Hook: Starting export preparation...")
    
    try:
        # Validate Conan recipe
        _validate_conan_recipe(conanfile)
        
        # Check recipe dependencies
        _check_recipe_dependencies(conanfile)
        
        # Validate package metadata
        _validate_package_metadata(conanfile)
        
        # Prepare export metadata
        _prepare_export_metadata(conanfile)
        
        # Validate license compliance
        _validate_license_compliance(conanfile)
        
        # Check for security issues in recipe
        _check_recipe_security(conanfile)
        
        conanfile.output.info("✅ OpenSSL Pre-Export Hook: Export preparation completed successfully")
        
    except Exception as e:
        conanfile.output.error(f"❌ OpenSSL Pre-Export Hook failed: {str(e)}")
        raise


def _validate_conan_recipe(conanfile) -> None:
    """Validate the Conan recipe structure and content."""
    conanfile.output.info("📋 Validating Conan recipe...")
    
    # Check required recipe attributes
    required_attributes = ["name", "version"]
    missing_attributes = []
    
    for attr in required_attributes:
        if not hasattr(conanfile, attr):
            missing_attributes.append(attr)
    
    if missing_attributes:
        raise RuntimeError(f"Missing required recipe attributes: {', '.join(missing_attributes)}")
    
    # Validate name format
    name = conanfile.name
    if not name or not isinstance(name, str):
        raise RuntimeError("Package name must be a non-empty string")
    
    if not name.replace("-", "").replace("_", "").isalnum():
        raise RuntimeError("Package name must contain only alphanumeric characters, hyphens, and underscores")
    
    # Validate version format
    version = conanfile.version
    if not version or not isinstance(version, str):
        raise RuntimeError("Package version must be a non-empty string")
    
    # Check for semantic versioning
    if not _is_semantic_version(version):
        conanfile.output.warning(f"⚠️ Version '{version}' does not follow semantic versioning (e.g., 1.2.3)")
    
    # Validate description
    description = getattr(conanfile, 'description', '')
    if not description:
        conanfile.output.warning("⚠️ No description provided for the package")
    elif len(description) < 10:
        conanfile.output.warning("⚠️ Description is very short, consider providing more details")
    
    # Validate license
    license_info = getattr(conanfile, 'license', '')
    if not license_info:
        conanfile.output.warning("⚠️ No license information provided")
    elif not _is_valid_license(license_info):
        conanfile.output.warning(f"⚠️ License '{license_info}' may not be a standard SPDX identifier")
    
    conanfile.output.info("✅ Conan recipe validation completed")


def _is_semantic_version(version: str) -> bool:
    """Check if version follows semantic versioning."""
    import re
    pattern = r'^\d+\.\d+\.\d+(-[a-zA-Z0-9.-]+)?(\+[a-zA-Z0-9.-]+)?$'
    return bool(re.match(pattern, version))


def _is_valid_license(license_info: str) -> bool:
    """Check if license is a valid SPDX identifier."""
    # Common SPDX license identifiers
    valid_licenses = [
        "MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "GPL-2.0", "GPL-3.0",
        "LGPL-2.1", "LGPL-3.0", "MPL-2.0", "ISC", "Unlicense", "Zlib"
    ]
    
    # Check for exact match or expression
    if license_info in valid_licenses:
        return True
    
    # Check for license expressions (e.g., "MIT OR Apache-2.0")
    if " OR " in license_info or " AND " in license_info:
        return True
    
    return False


def _check_recipe_dependencies(conanfile) -> None:
    """Check recipe dependencies for compatibility and security."""
    conanfile.output.info("🔍 Checking recipe dependencies...")
    
    # Check build requirements
    if hasattr(conanfile, 'build_requires') and conanfile.build_requires:
        conanfile.output.info(f"📦 Build requirements: {len(conanfile.build_requires)}")
        for req in conanfile.build_requires:
            conanfile.output.info(f"  - {req}")
    
    # Check runtime requirements
    if hasattr(conanfile, 'requires') and conanfile.requires:
        conanfile.output.info(f"📦 Runtime requirements: {len(conanfile.requires)}")
        for req in conanfile.requires:
            conanfile.output.info(f"  - {req}")
    
    # Check for known problematic dependencies
    problematic_deps = _check_problematic_dependencies(conanfile)
    if problematic_deps:
        conanfile.output.warning(f"⚠️ Potentially problematic dependencies: {', '.join(problematic_deps)}")
    
    # Check for version pinning
    _check_version_pinning(conanfile)
    
    conanfile.output.info("✅ Recipe dependencies check completed")


def _check_problematic_dependencies(conanfile) -> List[str]:
    """Check for known problematic dependencies."""
    problematic = []
    
    # Check for dependencies without version constraints
    if hasattr(conanfile, 'requires') and conanfile.requires:
        for req in conanfile.requires:
            req_str = str(req)
            if "@" not in req_str or "[" not in req_str:
                problematic.append(req_str)
    
    return problematic


def _check_version_pinning(conanfile) -> None:
    """Check for proper version pinning in dependencies."""
    if hasattr(conanfile, 'requires') and conanfile.requires:
        for req in conanfile.requires:
            req_str = str(req)
            if "[" in req_str:
                # Check for loose version constraints
                if ">=" in req_str and "<" not in req_str:
                    conanfile.output.warning(f"⚠️ Loose upper bound for dependency: {req_str}")
                elif "~" in req_str:
                    conanfile.output.info(f"📌 Compatible version constraint: {req_str}")


def _validate_package_metadata(conanfile) -> None:
    """Validate package metadata completeness."""
    conanfile.output.info("📊 Validating package metadata...")
    
    # Check for required metadata
    metadata_checks = {
        "name": hasattr(conanfile, 'name') and conanfile.name,
        "version": hasattr(conanfile, 'version') and conanfile.version,
        "description": hasattr(conanfile, 'description') and conanfile.description,
        "license": hasattr(conanfile, 'license') and conanfile.license,
        "author": hasattr(conanfile, 'author') and conanfile.author,
        "url": hasattr(conanfile, 'url') and conanfile.url,
        "homepage": hasattr(conanfile, 'homepage') and conanfile.homepage
    }
    
    missing_metadata = [key for key, present in metadata_checks.items() if not present]
    
    if missing_metadata:
        conanfile.output.warning(f"⚠️ Missing metadata: {', '.join(missing_metadata)}")
    
    # Validate URL format
    url = getattr(conanfile, 'url', '')
    if url and not _is_valid_url(url):
        conanfile.output.warning(f"⚠️ Invalid URL format: {url}")
    
    # Validate homepage URL
    homepage = getattr(conanfile, 'homepage', '')
    if homepage and not _is_valid_url(homepage):
        conanfile.output.warning(f"⚠️ Invalid homepage URL format: {homepage}")
    
    conanfile.output.info("✅ Package metadata validation completed")


def _is_valid_url(url: str) -> bool:
    """Check if URL has valid format."""
    import re
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return bool(re.match(pattern, url))


def _prepare_export_metadata(conanfile) -> None:
    """Prepare metadata for export."""
    conanfile.output.info("📋 Preparing export metadata...")
    
    # Create export metadata
    export_metadata = {
        "export_info": {
            "name": conanfile.name,
            "version": conanfile.version,
            "description": getattr(conanfile, 'description', ''),
            "license": getattr(conanfile, 'license', ''),
            "author": getattr(conanfile, 'author', ''),
            "url": getattr(conanfile, 'url', ''),
            "homepage": getattr(conanfile, 'homepage', ''),
            "topics": getattr(conanfile, 'topics', [])
        },
        "build_info": {
            "os": str(conanfile.settings.os) if hasattr(conanfile.settings, 'os') else 'any',
            "arch": str(conanfile.settings.arch) if hasattr(conanfile.settings, 'arch') else 'any',
            "compiler": str(conanfile.settings.compiler) if hasattr(conanfile.settings, 'compiler') else 'any',
            "build_type": str(conanfile.settings.build_type) if hasattr(conanfile.settings, 'build_type') else 'any'
        },
        "dependencies": {
            "build_requires": [str(req) for req in conanfile.build_requires] if hasattr(conanfile, 'build_requires') else [],
            "requires": [str(req) for req in conanfile.requires] if hasattr(conanfile, 'requires') else []
        },
        "export_timestamp": _get_timestamp()
    }
    
    # Save export metadata
    export_metadata_file = Path("export_metadata.json")
    with open(export_metadata_file, 'w') as f:
        json.dump(export_metadata, f, indent=2)
    
    conanfile.output.info(f"📋 Export metadata saved to: {export_metadata_file}")
    conanfile.output.info("✅ Export metadata preparation completed")


def _get_timestamp() -> str:
    """Get current timestamp in ISO format."""
    from datetime import datetime
    return datetime.utcnow().isoformat() + "Z"


def _validate_license_compliance(conanfile) -> None:
    """Validate license compliance for export."""
    conanfile.output.info("⚖️ Validating license compliance...")
    
    license_info = getattr(conanfile, 'license', '')
    if not license_info:
        conanfile.output.warning("⚠️ No license information - export may be restricted")
        return
    
    # Check for permissive licenses (generally safe for export)
    permissive_licenses = ["MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "ISC", "Unlicense", "Zlib"]
    
    # Check for copyleft licenses (may have restrictions)
    copyleft_licenses = ["GPL-2.0", "GPL-3.0", "LGPL-2.1", "LGPL-3.0", "AGPL-3.0"]
    
    if license_info in permissive_licenses:
        conanfile.output.info(f"✅ Permissive license detected: {license_info}")
    elif license_info in copyleft_licenses:
        conanfile.output.warning(f"⚠️ Copyleft license detected: {license_info} - ensure compliance")
    else:
        conanfile.output.warning(f"⚠️ Unknown license: {license_info} - verify compliance requirements")
    
    # Check for license expressions
    if " OR " in license_info:
        conanfile.output.info("📋 License expression detected - multiple license options available")
    elif " AND " in license_info:
        conanfile.output.warning("⚠️ License expression with AND - all licenses must be satisfied")
    
    conanfile.output.info("✅ License compliance validation completed")


def _check_recipe_security(conanfile) -> None:
    """Check for security issues in the recipe."""
    conanfile.output.info("🔒 Checking recipe security...")
    
    # Check for hardcoded credentials or sensitive information
    recipe_file = Path("conanfile.py")
    if recipe_file.exists():
        _check_hardcoded_secrets(recipe_file, conanfile)
    
    # Check for unsafe operations in recipe methods
    _check_unsafe_operations(conanfile)
    
    # Check for external downloads without verification
    _check_external_downloads(conanfile)
    
    conanfile.output.info("✅ Recipe security check completed")


def _check_hardcoded_secrets(file_path: Path, conanfile) -> None:
    """Check for hardcoded secrets in recipe file."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Patterns that might indicate hardcoded secrets
        suspicious_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'key\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']'
        ]
        
        import re
        for pattern in suspicious_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                conanfile.output.warning(f"⚠️ Potential hardcoded secret found: {matches[0]}")
    
    except Exception as e:
        conanfile.output.warning(f"⚠️ Could not check for hardcoded secrets: {e}")


def _check_unsafe_operations(conanfile) -> None:
    """Check for unsafe operations in recipe methods."""
    unsafe_methods = [
        'system', 'popen', 'exec', 'eval', 'execfile', '__import__'
    ]
    
    # Check if any unsafe methods are used in the recipe
    recipe_file = Path("conanfile.py")
    if recipe_file.exists():
        try:
            with open(recipe_file, 'r') as f:
                content = f.read()
            
            for method in unsafe_methods:
                if method in content:
                    conanfile.output.warning(f"⚠️ Potentially unsafe operation detected: {method}")
        
        except Exception as e:
            conanfile.output.warning(f"⚠️ Could not check for unsafe operations: {e}")


def _check_external_downloads(conanfile) -> None:
    """Check for external downloads without verification."""
    # This would typically check for downloads in source() method
    # that don't verify checksums or signatures
    
    if hasattr(conanfile, 'source') and callable(conanfile.source):
        conanfile.output.info("📥 Source method detected - ensure downloads are verified")
    
    # Check for common download patterns without verification
    recipe_file = Path("conanfile.py")
    if recipe_file.exists():
        try:
            with open(recipe_file, 'r') as f:
                content = f.read()
            
            # Look for download patterns
            download_patterns = [
                'download', 'wget', 'curl', 'urllib', 'requests.get'
            ]
            
            for pattern in download_patterns:
                if pattern in content.lower():
                    conanfile.output.info(f"📥 Download operation detected: {pattern}")
                    # Check if verification is present
                    if 'sha256' not in content.lower() and 'checksum' not in content.lower():
                        conanfile.output.warning(f"⚠️ Download without verification detected: {pattern}")
        
        except Exception as e:
            conanfile.output.warning(f"⚠️ Could not check for external downloads: {e}")
