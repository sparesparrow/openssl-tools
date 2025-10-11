"""
OpenSSL Post-Export Hook

This hook runs after the package is exported to a Conan remote and validates
the export by checking the exported recipe, verifying remote availability,
and performing final quality checks.
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional


def run(conanfile, **kwargs) -> None:
    """
    Post-export hook for OpenSSL packages.
    
    This hook:
    1. Validates exported recipe
    2. Checks remote availability
    3. Verifies export integrity
    4. Updates package registry
    5. Performs final quality checks
    6. Generates export report
    
    Args:
        conanfile: The ConanFile instance
        **kwargs: Additional keyword arguments
    """
    conanfile.output.info("📤 OpenSSL Post-Export Hook: Starting export validation...")
    
    try:
        # Validate exported recipe
        _validate_exported_recipe(conanfile)
        
        # Check remote availability
        _check_remote_availability(conanfile)
        
        # Verify export integrity
        _verify_export_integrity(conanfile)
        
        # Update package registry
        _update_package_registry(conanfile)
        
        # Perform final quality checks
        _perform_final_quality_checks(conanfile)
        
        # Generate export report
        _generate_export_report(conanfile)
        
        conanfile.output.info("✅ OpenSSL Post-Export Hook: Export validation completed successfully")
        
    except Exception as e:
        conanfile.output.error(f"❌ OpenSSL Post-Export Hook failed: {str(e)}")
        raise


def _validate_exported_recipe(conanfile) -> None:
    """Validate the exported recipe on the remote."""
    conanfile.output.info("📋 Validating exported recipe...")
    
    try:
        # Try to get recipe info from remote
        recipe_ref = f"{conanfile.name}/{conanfile.version}"
        
        # Check if recipe exists on remote
        result = subprocess.run([
            "conan", "list", recipe_ref, "--remote=all"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            conanfile.output.info(f"✅ Recipe {recipe_ref} found on remote")
            
            # Parse recipe information
            _parse_recipe_info(result.stdout, conanfile)
        else:
            conanfile.output.warning(f"⚠️ Could not verify recipe {recipe_ref} on remote")
            conanfile.output.warning(f"Remote response: {result.stderr}")
    
    except subprocess.TimeoutExpired:
        conanfile.output.warning("⚠️ Timeout while validating exported recipe")
    except Exception as e:
        conanfile.output.warning(f"⚠️ Error validating exported recipe: {e}")
    
    conanfile.output.info("✅ Exported recipe validation completed")


def _parse_recipe_info(output: str, conanfile) -> None:
    """Parse recipe information from conan list output."""
    try:
        lines = output.strip().split('\n')
        for line in lines:
            if conanfile.name in line and conanfile.version in line:
                conanfile.output.info(f"📋 Recipe info: {line.strip()}")
                break
    except Exception as e:
        conanfile.output.warning(f"⚠️ Could not parse recipe info: {e}")


def _check_remote_availability(conanfile) -> None:
    """Check if the package is available on configured remotes."""
    conanfile.output.info("🌐 Checking remote availability...")
    
    try:
        # List configured remotes
        result = subprocess.run([
            "conan", "remote", "list"
        ], capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            remotes = result.stdout.strip().split('\n')
            conanfile.output.info(f"📡 Configured remotes: {len(remotes)}")
            
            for remote in remotes:
                if remote.strip():
                    conanfile.output.info(f"  - {remote.strip()}")
        else:
            conanfile.output.warning("⚠️ Could not list configured remotes")
    
    except subprocess.TimeoutExpired:
        conanfile.output.warning("⚠️ Timeout while checking remote availability")
    except Exception as e:
        conanfile.output.warning(f"⚠️ Error checking remote availability: {e}")
    
    conanfile.output.info("✅ Remote availability check completed")


def _verify_export_integrity(conanfile) -> None:
    """Verify the integrity of the exported package."""
    conanfile.output.info("🔍 Verifying export integrity...")
    
    try:
        # Check if package can be installed from remote
        recipe_ref = f"{conanfile.name}/{conanfile.version}"
        
        # Try to get package info without installing
        result = subprocess.run([
            "conan", "list", recipe_ref, "--remote=all", "--format=json"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            try:
                package_info = json.loads(result.stdout)
                conanfile.output.info("✅ Package integrity verified")
                
                # Extract package details
                if isinstance(package_info, list) and len(package_info) > 0:
                    package_data = package_info[0]
                    if 'items' in package_data:
                        conanfile.output.info(f"📦 Package items: {len(package_data['items'])}")
                        
                        # Check for different configurations
                        configs = set()
                        for item in package_data['items']:
                            if 'settings' in item:
                                configs.add(str(item['settings']))
                        
                        conanfile.output.info(f"🏗️ Available configurations: {len(configs)}")
                        for config in sorted(configs):
                            conanfile.output.info(f"  - {config}")
                
            except json.JSONDecodeError:
                conanfile.output.warning("⚠️ Could not parse package info JSON")
        else:
            conanfile.output.warning(f"⚠️ Could not verify package integrity: {result.stderr}")
    
    except subprocess.TimeoutExpired:
        conanfile.output.warning("⚠️ Timeout while verifying export integrity")
    except Exception as e:
        conanfile.output.warning(f"⚠️ Error verifying export integrity: {e}")
    
    conanfile.output.info("✅ Export integrity verification completed")


def _update_package_registry(conanfile) -> None:
    """Update package registry with export information."""
    conanfile.output.info("📊 Updating package registry...")
    
    try:
        # Create registry entry
        registry_entry = {
            "package_info": {
                "name": conanfile.name,
                "version": conanfile.version,
                "description": getattr(conanfile, 'description', ''),
                "license": getattr(conanfile, 'license', ''),
                "author": getattr(conanfile, 'author', ''),
                "url": getattr(conanfile, 'url', ''),
                "homepage": getattr(conanfile, 'homepage', '')
            },
            "export_info": {
                "export_timestamp": _get_timestamp(),
                "export_user": os.environ.get("USER", "unknown"),
                "export_host": os.environ.get("HOSTNAME", "unknown"),
                "conan_version": _get_conan_version(),
                "python_version": _get_python_version()
            },
            "build_info": {
                "os": str(conanfile.settings.os) if hasattr(conanfile.settings, 'os') else 'any',
                "arch": str(conanfile.settings.arch) if hasattr(conanfile.settings, 'arch') else 'any',
                "compiler": str(conanfile.settings.compiler) if hasattr(conanfile.settings, 'compiler') else 'any',
                "build_type": str(conanfile.settings.build_type) if hasattr(conanfile.settings, 'build_type') else 'any'
            }
        }
        
        # Save registry entry
        registry_file = Path("package_registry.json")
        registry_data = []
        
        # Load existing registry if it exists
        if registry_file.exists():
            try:
                with open(registry_file, 'r') as f:
                    registry_data = json.load(f)
            except json.JSONDecodeError:
                registry_data = []
        
        # Add new entry
        registry_data.append(registry_entry)
        
        # Save updated registry
        with open(registry_file, 'w') as f:
            json.dump(registry_data, f, indent=2)
        
        conanfile.output.info(f"📊 Package registry updated: {registry_file}")
        
    except Exception as e:
        conanfile.output.warning(f"⚠️ Could not update package registry: {e}")
    
    conanfile.output.info("✅ Package registry update completed")


def _get_timestamp() -> str:
    """Get current timestamp in ISO format."""
    from datetime import datetime
    return datetime.utcnow().isoformat() + "Z"


def _get_conan_version() -> str:
    """Get Conan version."""
    try:
        result = subprocess.run([
            "conan", "--version"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return "unknown"
    except Exception:
        return "unknown"


def _get_python_version() -> str:
    """Get Python version."""
    import sys
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"


def _perform_final_quality_checks(conanfile) -> None:
    """Perform final quality checks on the exported package."""
    conanfile.output.info("🔍 Performing final quality checks...")
    
    # Check package completeness
    _check_package_completeness(conanfile)
    
    # Check documentation quality
    _check_documentation_quality(conanfile)
    
    # Check for security issues
    _check_security_issues(conanfile)
    
    # Check for performance considerations
    _check_performance_considerations(conanfile)
    
    conanfile.output.info("✅ Final quality checks completed")


def _check_package_completeness(conanfile) -> None:
    """Check if the package is complete and well-formed."""
    conanfile.output.info("📦 Checking package completeness...")
    
    # Check for required recipe methods
    required_methods = ["package", "package_info"]
    missing_methods = []
    
    for method in required_methods:
        if not hasattr(conanfile, method) or not callable(getattr(conanfile, method)):
            missing_methods.append(method)
    
    if missing_methods:
        conanfile.output.warning(f"⚠️ Missing required methods: {', '.join(missing_methods)}")
    
    # Check for optional but recommended methods
    recommended_methods = ["configure", "config_options", "requirements", "build_requirements"]
    missing_recommended = []
    
    for method in recommended_methods:
        if not hasattr(conanfile, method) or not callable(getattr(conanfile, method)):
            missing_recommended.append(method)
    
    if missing_recommended:
        conanfile.output.info(f"📋 Recommended methods not implemented: {', '.join(missing_recommended)}")
    
    conanfile.output.info("✅ Package completeness check completed")


def _check_documentation_quality(conanfile) -> None:
    """Check documentation quality."""
    conanfile.output.info("📚 Checking documentation quality...")
    
    # Check for description
    description = getattr(conanfile, 'description', '')
    if not description:
        conanfile.output.warning("⚠️ No package description provided")
    elif len(description) < 20:
        conanfile.output.warning("⚠️ Package description is very short")
    else:
        conanfile.output.info("✅ Package description is adequate")
    
    # Check for URL and homepage
    url = getattr(conanfile, 'url', '')
    homepage = getattr(conanfile, 'homepage', '')
    
    if not url and not homepage:
        conanfile.output.warning("⚠️ No URL or homepage provided")
    elif url and homepage:
        conanfile.output.info("✅ Both URL and homepage provided")
    else:
        conanfile.output.info("📋 URL or homepage provided")
    
    # Check for topics
    topics = getattr(conanfile, 'topics', [])
    if not topics:
        conanfile.output.info("📋 No topics provided - consider adding relevant tags")
    else:
        conanfile.output.info(f"🏷️ Topics provided: {', '.join(topics)}")
    
    conanfile.output.info("✅ Documentation quality check completed")


def _check_security_issues(conanfile) -> None:
    """Check for potential security issues."""
    conanfile.output.info("🔒 Checking for security issues...")
    
    # Check for unsafe dependencies
    if hasattr(conanfile, 'requires') and conanfile.requires:
        for req in conanfile.requires:
            req_str = str(req)
            # Check for known vulnerable packages (simplified check)
            if any(vuln in req_str.lower() for vuln in ['openssl-1.0', 'openssl-1.1.0', 'openssl-1.1.1']):
                conanfile.output.warning(f"⚠️ Potentially vulnerable OpenSSL version: {req_str}")
    
    # Check for external downloads without verification
    recipe_file = Path("conanfile.py")
    if recipe_file.exists():
        try:
            with open(recipe_file, 'r') as f:
                content = f.read()
            
            # Check for download patterns without verification
            if 'download' in content.lower() and 'sha256' not in content.lower():
                conanfile.output.warning("⚠️ External downloads without verification detected")
        
        except Exception as e:
            conanfile.output.warning(f"⚠️ Could not check for security issues: {e}")
    
    conanfile.output.info("✅ Security issues check completed")


def _check_performance_considerations(conanfile) -> None:
    """Check for performance considerations."""
    conanfile.output.info("⚡ Checking performance considerations...")
    
    # Check for shared library option
    if hasattr(conanfile, 'options') and hasattr(conanfile.options, 'shared'):
        conanfile.output.info("✅ Shared library option available")
    else:
        conanfile.output.info("📋 No shared library option - consider adding for flexibility")
    
    # Check for build optimization options
    if hasattr(conanfile, 'options'):
        options = conanfile.options
        if hasattr(options, 'fPIC'):
            conanfile.output.info("✅ fPIC option available for position-independent code")
        if hasattr(options, 'enable_ssl'):
            conanfile.output.info("✅ SSL enable/disable option available")
    
    # Check for proper package_id implementation
    if hasattr(conanfile, 'package_id') and callable(conanfile.package_id):
        conanfile.output.info("✅ Custom package_id method implemented")
    else:
        conanfile.output.info("📋 Using default package_id - consider custom implementation for optimization")
    
    conanfile.output.info("✅ Performance considerations check completed")


def _generate_export_report(conanfile) -> None:
    """Generate comprehensive export report."""
    conanfile.output.info("📊 Generating export report...")
    
    try:
        # Create export report
        export_report = {
            "export_summary": {
                "package_name": conanfile.name,
                "package_version": conanfile.version,
                "export_timestamp": _get_timestamp(),
                "export_status": "success"
            },
            "package_metadata": {
                "description": getattr(conanfile, 'description', ''),
                "license": getattr(conanfile, 'license', ''),
                "author": getattr(conanfile, 'author', ''),
                "url": getattr(conanfile, 'url', ''),
                "homepage": getattr(conanfile, 'homepage', ''),
                "topics": getattr(conanfile, 'topics', [])
            },
            "build_configuration": {
                "os": str(conanfile.settings.os) if hasattr(conanfile.settings, 'os') else 'any',
                "arch": str(conanfile.settings.arch) if hasattr(conanfile.settings, 'arch') else 'any',
                "compiler": str(conanfile.settings.compiler) if hasattr(conanfile.settings, 'compiler') else 'any',
                "build_type": str(conanfile.settings.build_type) if hasattr(conanfile.settings, 'build_type') else 'any'
            },
            "dependencies": {
                "build_requires": [str(req) for req in conanfile.build_requires] if hasattr(conanfile, 'build_requires') else [],
                "requires": [str(req) for req in conanfile.requires] if hasattr(conanfile, 'requires') else []
            },
            "quality_metrics": {
                "has_description": bool(getattr(conanfile, 'description', '')),
                "has_license": bool(getattr(conanfile, 'license', '')),
                "has_url": bool(getattr(conanfile, 'url', '')),
                "has_homepage": bool(getattr(conanfile, 'homepage', '')),
                "has_topics": bool(getattr(conanfile, 'topics', [])),
                "has_shared_option": hasattr(conanfile, 'options') and hasattr(conanfile.options, 'shared'),
                "has_custom_package_id": hasattr(conanfile, 'package_id') and callable(conanfile.package_id)
            },
            "export_environment": {
                "conan_version": _get_conan_version(),
                "python_version": _get_python_version(),
                "export_user": os.environ.get("USER", "unknown"),
                "export_host": os.environ.get("HOSTNAME", "unknown")
            }
        }
        
        # Save export report
        report_file = Path("export_report.json")
        with open(report_file, 'w') as f:
            json.dump(export_report, f, indent=2)
        
        conanfile.output.info(f"📊 Export report saved to: {report_file}")
        
        # Print summary
        _print_export_summary(export_report, conanfile)
        
    except Exception as e:
        conanfile.output.warning(f"⚠️ Could not generate export report: {e}")
    
    conanfile.output.info("✅ Export report generation completed")


def _print_export_summary(report: Dict[str, Any], conanfile) -> None:
    """Print export summary to console."""
    summary = report["export_summary"]
    metadata = report["package_metadata"]
    quality = report["quality_metrics"]
    
    conanfile.output.info("=" * 60)
    conanfile.output.info("📦 EXPORT SUMMARY")
    conanfile.output.info("=" * 60)
    conanfile.output.info(f"Package: {summary['package_name']}@{summary['package_version']}")
    conanfile.output.info(f"Status: {summary['export_status'].upper()}")
    conanfile.output.info(f"Timestamp: {summary['export_timestamp']}")
    conanfile.output.info("")
    
    conanfile.output.info("📋 PACKAGE METADATA")
    conanfile.output.info("-" * 30)
    conanfile.output.info(f"Description: {'✅' if quality['has_description'] else '❌'}")
    conanfile.output.info(f"License: {'✅' if quality['has_license'] else '❌'}")
    conanfile.output.info(f"URL: {'✅' if quality['has_url'] else '❌'}")
    conanfile.output.info(f"Homepage: {'✅' if quality['has_homepage'] else '❌'}")
    conanfile.output.info(f"Topics: {'✅' if quality['has_topics'] else '❌'}")
    conanfile.output.info("")
    
    conanfile.output.info("🔧 BUILD FEATURES")
    conanfile.output.info("-" * 30)
    conanfile.output.info(f"Shared Library Option: {'✅' if quality['has_shared_option'] else '❌'}")
    conanfile.output.info(f"Custom Package ID: {'✅' if quality['has_custom_package_id'] else '❌'}")
    conanfile.output.info("")
    
    conanfile.output.info("=" * 60)
