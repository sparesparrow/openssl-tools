#!/usr/bin/env python3
"""
OpenSSL Tools SBOM Generator
Enhanced SBOM generation with security features following ngapy-dev patterns
"""

import json
import logging
import os
import uuid
import hashlib
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import yaml


class SBOMGenerator:
    """SBOM generator with security features following ngapy-dev patterns"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger('openssl_tools.sbom_generator')
        
        # SBOM configuration
        self.bom_format = "CycloneDX"
        self.spec_version = "1.5"
        self.serial_number = f"urn:uuid:{uuid.uuid4()}"
        self.version = 1
        
        # Security features
        self.enable_vulnerability_scanning = self.config.get('enable_vulnerability_scanning', True)
        self.enable_package_signing = self.config.get('enable_package_signing', False)
        self.enable_dependency_analysis = self.config.get('enable_dependency_analysis', True)
        self.enable_license_analysis = self.config.get('enable_license_analysis', True)
        
        # External tools
        self.trivy_path = self.config.get('trivy_path', 'trivy')
        self.syft_path = self.config.get('syft_path', 'syft')
        self.cosign_path = self.config.get('cosign_path', 'cosign')
    
    def generate_sbom(self, package_info: Dict[str, Any], 
                     output_path: Optional[Path] = None) -> Dict[str, Any]:
        """Generate comprehensive SBOM following ngapy-dev patterns"""
        self.logger.info("Generating Software Bill of Materials (SBOM)...")
        
        # Create base SBOM structure
        sbom_data = self._create_base_sbom(package_info)
        
        # Add components
        components = self._analyze_components(package_info)
        sbom_data['components'] = components
        
        # Add dependencies
        if self.enable_dependency_analysis:
            dependencies = self._analyze_dependencies(package_info)
            sbom_data['dependencies'] = dependencies
        
        # Add vulnerabilities
        if self.enable_vulnerability_scanning:
            vulnerabilities = self._scan_vulnerabilities(package_info)
            sbom_data['vulnerabilities'] = vulnerabilities
        
        # Add metadata
        metadata = self._generate_metadata(package_info)
        sbom_data['metadata'] = metadata
        
        # Add security features
        if self.enable_package_signing:
            signatures = self._generate_package_signatures(package_info)
            sbom_data['signatures'] = signatures
        
        # Save SBOM
        if output_path:
            self._save_sbom(sbom_data, output_path)
        
        self.logger.info("SBOM generation completed")
        return sbom_data
    
    def _create_base_sbom(self, package_info: Dict[str, Any]) -> Dict[str, Any]:
        """Create base SBOM structure"""
        return {
            "bomFormat": self.bom_format,
            "specVersion": self.spec_version,
            "serialNumber": self.serial_number,
            "version": self.version,
            "metadata": {},
            "components": [],
            "dependencies": [],
            "vulnerabilities": []
        }
    
    def _analyze_components(self, package_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze package components"""
        components = []
        
        # Main package component
        main_component = {
            "type": "application",
            "bom-ref": f"{package_info['name']}@{package_info['version']}",
            "name": package_info['name'],
            "version": str(package_info['version']),
            "description": package_info.get('description', ''),
            "licenses": self._analyze_licenses(package_info),
            "hashes": self._calculate_hashes(package_info),
            "externalReferences": self._get_external_references(package_info),
            "properties": self._get_component_properties(package_info)
        }
        components.append(main_component)
        
        # Add dependency components
        if 'dependencies' in package_info:
            for dep_name, dep_info in package_info['dependencies'].items():
                dep_component = {
                    "type": "library",
                    "bom-ref": f"{dep_name}@{dep_info.get('version', 'unknown')}",
                    "name": dep_name,
                    "version": str(dep_info.get('version', 'unknown')),
                    "scope": dep_info.get('scope', 'required'),
                    "licenses": self._analyze_dependency_licenses(dep_name, dep_info),
                    "hashes": self._calculate_dependency_hashes(dep_name, dep_info),
                    "properties": self._get_dependency_properties(dep_name, dep_info)
                }
                components.append(dep_component)
        
        return components
    
    def _analyze_licenses(self, package_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze package licenses"""
        licenses = []
        
        # Get license from package info
        package_license = package_info.get('license', 'Unknown')
        if isinstance(package_license, str):
            licenses.append({"license": {"id": package_license}})
        elif isinstance(package_license, list):
            for lic in package_license:
                if isinstance(lic, str):
                    licenses.append({"license": {"id": lic}})
                elif isinstance(lic, dict):
                    licenses.append({"license": lic})
        
        # Add license analysis if enabled
        if self.enable_license_analysis:
            license_file = self._find_license_file(package_info)
            if license_file:
                detected_licenses = self._detect_licenses_from_file(license_file)
                licenses.extend(detected_licenses)
        
        return licenses if licenses else [{"license": {"id": "Unknown"}}]
    
    def _analyze_dependency_licenses(self, dep_name: str, dep_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze dependency licenses"""
        licenses = []
        
        # Get license from dependency info
        dep_license = dep_info.get('license', 'Unknown')
        if isinstance(dep_license, str):
            licenses.append({"license": {"id": dep_license}})
        elif isinstance(dep_license, list):
            for lic in dep_license:
                if isinstance(lic, str):
                    licenses.append({"license": {"id": lic}})
                elif isinstance(lic, dict):
                    licenses.append({"license": lic})
        
        return licenses if licenses else [{"license": {"id": "Unknown"}}]
    
    def _find_license_file(self, package_info: Dict[str, Any]) -> Optional[Path]:
        """Find license file in package"""
        package_dir = Path(package_info.get('package_folder', '.'))
        
        # Common license file names
        license_files = [
            'LICENSE', 'LICENSE.txt', 'LICENSE.md',
            'COPYING', 'COPYING.txt',
            'LICENCE', 'LICENCE.txt', 'LICENCE.md'
        ]
        
        for license_file in license_files:
            license_path = package_dir / license_file
            if license_path.exists():
                return license_path
        
        return None
    
    def _detect_licenses_from_file(self, license_file: Path) -> List[Dict[str, Any]]:
        """Detect licenses from license file"""
        try:
            with open(license_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read().lower()
            
            # Simple license detection based on keywords
            detected_licenses = []
            
            if 'apache' in content and 'license' in content:
                detected_licenses.append({"license": {"id": "Apache-2.0"}})
            elif 'mit' in content and 'license' in content:
                detected_licenses.append({"license": {"id": "MIT"}})
            elif 'gnu general public license' in content:
                if 'version 3' in content:
                    detected_licenses.append({"license": {"id": "GPL-3.0"}})
                elif 'version 2' in content:
                    detected_licenses.append({"license": {"id": "GPL-2.0"}})
            elif 'bsd' in content and 'license' in content:
                detected_licenses.append({"license": {"id": "BSD-3-Clause"}})
            elif 'mozilla public license' in content:
                detected_licenses.append({"license": {"id": "MPL-2.0"}})
            
            return detected_licenses
        except Exception as e:
            self.logger.warning(f"Failed to detect licenses from {license_file}: {e}")
            return []
    
    def _calculate_hashes(self, package_info: Dict[str, Any]) -> List[Dict[str, str]]:
        """Calculate package hashes"""
        hashes = []
        package_dir = Path(package_info.get('package_folder', '.'))
        
        if package_dir.exists():
            # Calculate directory hash
            dir_hash = self._calculate_directory_hash(package_dir)
            if dir_hash:
                hashes.append({"alg": "SHA-256", "content": dir_hash})
        
        return hashes
    
    def _calculate_dependency_hashes(self, dep_name: str, dep_info: Dict[str, Any]) -> List[Dict[str, str]]:
        """Calculate dependency hashes"""
        hashes = []
        
        # Get dependency path
        dep_path = dep_info.get('path')
        if dep_path and Path(dep_path).exists():
            dep_hash = self._calculate_directory_hash(Path(dep_path))
            if dep_hash:
                hashes.append({"alg": "SHA-256", "content": dep_hash})
        
        return hashes
    
    def _calculate_directory_hash(self, directory: Path) -> Optional[str]:
        """Calculate SHA-256 hash of directory contents"""
        try:
            hasher = hashlib.sha256()
            
            for file_path in sorted(directory.rglob('*')):
                if file_path.is_file():
                    # Add file path and content to hash
                    hasher.update(str(file_path.relative_to(directory)).encode())
                    with open(file_path, 'rb') as f:
                        for chunk in iter(lambda: f.read(4096), b""):
                            hasher.update(chunk)
            
            return hasher.hexdigest()
        except Exception as e:
            self.logger.warning(f"Failed to calculate directory hash for {directory}: {e}")
            return None
    
    def _get_external_references(self, package_info: Dict[str, Any]) -> List[Dict[str, str]]:
        """Get external references"""
        references = []
        
        # Homepage
        if 'homepage' in package_info:
            references.append({
                "type": "website",
                "url": package_info['homepage']
            })
        
        # Repository URL
        if 'url' in package_info:
            references.append({
                "type": "vcs",
                "url": package_info['url']
            })
        
        # Issue tracker
        if 'issues_url' in package_info:
            references.append({
                "type": "issue-tracker",
                "url": package_info['issues_url']
            })
        
        return references
    
    def _get_component_properties(self, package_info: Dict[str, Any]) -> List[Dict[str, str]]:
        """Get component properties"""
        properties = [
            {"name": "package_type", "value": "python-tools"},
            {"name": "build_platform", "value": f"{package_info.get('os', 'unknown')}-{package_info.get('arch', 'unknown')}"},
            {"name": "build_type", "value": package_info.get('build_type', 'Release')},
            {"name": "conan_options", "value": json.dumps(package_info.get('options', {}))},
            {"name": "conan_settings", "value": json.dumps(package_info.get('settings', {}))},
            {"name": "generated_at", "value": datetime.now(timezone.utc).isoformat()},
            {"name": "generator_version", "value": "1.0.0"}
        ]
        
        return properties
    
    def _get_dependency_properties(self, dep_name: str, dep_info: Dict[str, Any]) -> List[Dict[str, str]]:
        """Get dependency properties"""
        properties = [
            {"name": "dependency_type", "value": dep_info.get('type', 'library')},
            {"name": "scope", "value": dep_info.get('scope', 'required')},
            {"name": "optional", "value": str(dep_info.get('optional', False))}
        ]
        
        return properties
    
    def _analyze_dependencies(self, package_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze package dependencies"""
        dependencies = []
        
        if 'dependencies' in package_info:
            for dep_name, dep_info in package_info['dependencies'].items():
                dep_ref = f"{dep_name}@{dep_info.get('version', 'unknown')}"
                dependencies.append({
                    "ref": dep_ref,
                    "dependsOn": []
                })
        
        return dependencies
    
    def _scan_vulnerabilities(self, package_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scan for vulnerabilities using external tools"""
        vulnerabilities = []
        
        # Use Trivy for vulnerability scanning
        if self._is_tool_available(self.trivy_path):
            trivy_vulns = self._scan_with_trivy(package_info)
            vulnerabilities.extend(trivy_vulns)
        
        # Use Syft for additional vulnerability data
        if self._is_tool_available(self.syft_path):
            syft_vulns = self._scan_with_syft(package_info)
            vulnerabilities.extend(syft_vulns)
        
        return vulnerabilities
    
    def _is_tool_available(self, tool_path: str) -> bool:
        """Check if external tool is available"""
        try:
            result = subprocess.run([tool_path, '--version'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def _scan_with_trivy(self, package_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scan vulnerabilities with Trivy"""
        vulnerabilities = []
        
        try:
            package_dir = Path(package_info.get('package_folder', '.'))
            if not package_dir.exists():
                return vulnerabilities
            
            # Run Trivy scan
            result = subprocess.run([
                self.trivy_path, 'fs', '--format', 'json', str(package_dir)
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                trivy_data = json.loads(result.stdout)
                
                for result_item in trivy_data.get('Results', []):
                    for vuln in result_item.get('Vulnerabilities', []):
                        vulnerability = {
                            "id": vuln.get('VulnerabilityID', ''),
                            "source": {
                                "name": "trivy",
                                "url": "https://github.com/aquasecurity/trivy"
                            },
                            "ratings": [{
                                "score": vuln.get('Score', 0),
                                "severity": vuln.get('Severity', 'UNKNOWN'),
                                "method": "CVSSv3"
                            }],
                            "description": vuln.get('Description', ''),
                            "references": [{
                                "url": vuln.get('PrimaryURL', '')
                            }] if vuln.get('PrimaryURL') else []
                        }
                        vulnerabilities.append(vulnerability)
            
        except Exception as e:
            self.logger.warning(f"Trivy vulnerability scan failed: {e}")
        
        return vulnerabilities
    
    def _scan_with_syft(self, package_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scan vulnerabilities with Syft"""
        vulnerabilities = []
        
        try:
            package_dir = Path(package_info.get('package_folder', '.'))
            if not package_dir.exists():
                return vulnerabilities
            
            # Run Syft scan
            result = subprocess.run([
                self.syft_path, 'packages', '--format', 'json', str(package_dir)
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                syft_data = json.loads(result.stdout)
                
                # Syft provides package information, not direct vulnerabilities
                # This would need to be combined with vulnerability databases
                self.logger.debug(f"Syft found {len(syft_data.get('artifacts', []))} packages")
            
        except Exception as e:
            self.logger.warning(f"Syft scan failed: {e}")
        
        return vulnerabilities
    
    def _generate_metadata(self, package_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate SBOM metadata"""
        metadata = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "component": {
                "type": "application",
                "bom-ref": f"{package_info['name']}@{package_info['version']}",
                "name": package_info['name'],
                "version": str(package_info['version']),
                "description": package_info.get('description', ''),
                "licenses": self._analyze_licenses(package_info),
                "hashes": self._calculate_hashes(package_info),
                "externalReferences": self._get_external_references(package_info),
                "properties": self._get_component_properties(package_info)
            },
            "tools": [
                {
                    "vendor": "OpenSSL Tools",
                    "name": "sbom-generator",
                    "version": "1.0.0"
                }
            ]
        }
        
        return metadata
    
    def _generate_package_signatures(self, package_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate package signatures for supply chain security"""
        signatures = []
        
        if not self.enable_package_signing:
            return signatures
        
        try:
            # Use cosign for signing
            if self._is_tool_available(self.cosign_path):
                signature = self._sign_with_cosign(package_info)
                if signature:
                    signatures.append(signature)
        except Exception as e:
            self.logger.warning(f"Package signing failed: {e}")
        
        return signatures
    
    def _sign_with_cosign(self, package_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Sign package with cosign"""
        try:
            package_dir = Path(package_info.get('package_folder', '.'))
            if not package_dir.exists():
                return None
            
            # Create signature
            signature = {
                "algorithm": "cosign",
                "keyid": "placeholder",
                "signature": "placeholder",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # In a real implementation, this would use cosign to sign the package
            self.logger.info("Package signing with cosign (placeholder)")
            
            return signature
        except Exception as e:
            self.logger.warning(f"Cosign signing failed: {e}")
            return None
    
    def _save_sbom(self, sbom_data: Dict[str, Any], output_path: Path) -> None:
        """Save SBOM to file"""
        try:
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save as JSON
            with open(output_path, 'w') as f:
                json.dump(sbom_data, f, indent=2, ensure_ascii=False)
            
            # Also save as YAML for readability
            yaml_path = output_path.with_suffix('.yaml')
            with open(yaml_path, 'w') as f:
                yaml.dump(sbom_data, f, default_flow_style=False, sort_keys=False)
            
            self.logger.info(f"SBOM saved to {output_path} and {yaml_path}")
        except Exception as e:
            self.logger.error(f"Failed to save SBOM: {e}")
            raise
    
    def validate_sbom(self, sbom_path: Path) -> bool:
        """Validate SBOM format and content"""
        try:
            with open(sbom_path, 'r') as f:
                sbom_data = json.load(f)
            
            # Check required fields
            required_fields = ['bomFormat', 'specVersion', 'serialNumber', 'version', 'metadata', 'components']
            for field in required_fields:
                if field not in sbom_data:
                    self.logger.error(f"Missing required field: {field}")
                    return False
            
            # Validate format
            if sbom_data['bomFormat'] != self.bom_format:
                self.logger.error(f"Invalid BOM format: {sbom_data['bomFormat']}")
                return False
            
            # Validate components
            if not isinstance(sbom_data['components'], list):
                self.logger.error("Components must be a list")
                return False
            
            self.logger.info("SBOM validation passed")
            return True
        except Exception as e:
            self.logger.error(f"SBOM validation failed: {e}")
            return False