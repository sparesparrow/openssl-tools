#!/usr/bin/env python3
"""
SBOM Generator for C/C++ Projects with Conan
Generates CycloneDX and SPDX format SBOMs with vulnerability data
"""

import json
import uuid
import hashlib
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


class SBOMGenerator:
    """Generate Software Bill of Materials for Conan packages"""
    
    def __init__(self, conanfile_path: str = "conanfile.py"):
        self.conanfile_path = conanfile_path
        self.project_root = Path(conanfile_path).parent
        
    def generate_cyclone_dx(self, output_path: str = "sbom-cyclonedx.json") -> Dict[str, Any]:
        """Generate CycloneDX format SBOM"""
        
        # Get dependency information from Conan
        deps_info = self._get_conan_dependencies()
        main_component = self._get_main_component()
        
        sbom = {
            "bomFormat": "CycloneDX",
            "specVersion": "1.4",
            "serialNumber": f"urn:uuid:{uuid.uuid4()}",
            "version": 1,
            "metadata": {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "tools": [
                    {
                        "vendor": "Conan",
                        "name": "conan",
                        "version": self._get_conan_version()
                    }
                ],
                "component": main_component
            },
            "components": deps_info["components"],
            "dependencies": deps_info["dependencies"]
        }
        
        # Add vulnerability data if available
        vulns = self._get_vulnerability_data()
        if vulns:
            sbom["vulnerabilities"] = vulns
            
        # Save SBOM
        with open(output_path, 'w') as f:
            json.dump(sbom, f, indent=2)
            
        return sbom
    
    def generate_spdx(self, output_path: str = "sbom-spdx.json") -> Dict[str, Any]:
        """Generate SPDX format SBOM"""
        
        deps_info = self._get_conan_dependencies()
        
        sbom = {
            "spdxVersion": "SPDX-2.3",
            "dataLicense": "CC0-1.0",
            "SPDXID": "SPDXRef-DOCUMENT",
            "documentName": self._get_project_name(),
            "documentNamespace": f"https://example.com/sbom/{uuid.uuid4()}",
            "creationInfo": {
                "created": datetime.utcnow().isoformat() + "Z",
                "creators": [
                    "Tool: conan-sbom-generator"
                ]
            },
            "packages": self._convert_to_spdx_packages(deps_info["components"]),
            "relationships": self._convert_to_spdx_relationships(deps_info["dependencies"])
        }
        
        with open(output_path, 'w') as f:
            json.dump(sbom, f, indent=2)
            
        return sbom
    
    def _get_conan_dependencies(self) -> Dict[str, Any]:
        """Extract dependency information from Conan"""
        
        try:
            # Get dependency graph
            result = subprocess.run([
                'conan', 'graph', 'info', self.conanfile_path, 
                '--format=json'
            ], capture_output=True, text=True, check=True)
            
            graph_data = json.loads(result.stdout)
            
            components = []
            dependencies = []
            
            for node_id, node in graph_data.get("graph", {}).items():
                if node_id == "0":  # Skip root node (our project)
                    continue
                    
                ref = node.get("ref", "")
                if not ref:
                    continue
                    
                # Parse reference (name/version@user/channel)
                parts = ref.split("/")
                if len(parts) < 2:
                    continue
                    
                name = parts[0]
                version = parts[1].split("@")[0]
                
                # Create component
                component = {
                    "type": "library",
                    "bom-ref": f"pkg:conan/{name}@{version}",
                    "name": name,
                    "version": version,
                    "purl": f"pkg:conan/{name}@{version}",
                    "scope": "required"
                }
                
                # Add hashes if available
                package_id = node.get("package_id")
                if package_id:
                    component["hashes"] = [{
                        "alg": "SHA-256",
                        "content": package_id
                    }]
                
                # Add license information if available
                license_info = self._get_package_license(name, version)
                if license_info:
                    component["licenses"] = license_info
                
                components.append(component)
                
                # Create dependency relationships
                requires = node.get("requires", [])
                for req in requires:
                    dependencies.append({
                        "ref": f"pkg:conan/{name}@{version}",
                        "dependsOn": [req]
                    })
            
            return {
                "components": components,
                "dependencies": dependencies
            }
            
        except subprocess.CalledProcessError as e:
            print(f"Error getting Conan dependencies: {e}")
            return {"components": [], "dependencies": []}
    
    def _get_main_component(self) -> Dict[str, Any]:
        """Get information about the main project component"""
        
        project_name = self._get_project_name()
        project_version = self._get_project_version()
        
        component = {
            "type": "application",
            "name": project_name,
            "version": project_version,
            "purl": f"pkg:generic/{project_name}@{project_version}"
        }
        
        # Add source code hash
        source_hash = self._calculate_source_hash()
        if source_hash:
            component["hashes"] = [{
                "alg": "SHA-256", 
                "content": source_hash
            }]
        
        # Add license
        license_file = self._find_license_file()
        if license_file:
            component["licenses"] = [{
                "license": {"name": self._detect_license(license_file)}
            }]
        
        return component
    
    def _get_vulnerability_data(self) -> Optional[List[Dict[str, Any]]]:
        """Get vulnerability data using security scanning tools"""
        
        vulns = []
        
        # Try to use Trivy for vulnerability scanning
        try:
            result = subprocess.run([
                'trivy', 'config', '--format', 'json', 
                '--exit-code', '0', self.conanfile_path
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                trivy_data = json.loads(result.stdout)
                
                for result_item in trivy_data.get("Results", []):
                    for vuln in result_item.get("Vulnerabilities", []):
                        vuln_entry = {
                            "id": vuln.get("VulnerabilityID"),
                            "source": {
                                "name": "trivy",
                                "url": "https://trivy.dev"
                            },
                            "ratings": [{
                                "source": {
                                    "name": vuln.get("Severity", "").lower()
                                },
                                "severity": vuln.get("Severity", "unknown").upper()
                            }],
                            "description": vuln.get("Description", ""),
                            "affects": [{
                                "ref": f"pkg:conan/{vuln.get('PkgName')}@{vuln.get('InstalledVersion')}"
                            }]
                        }
                        
                        if vuln.get("FixedVersion"):
                            vuln_entry["recommendation"] = f"Upgrade to version {vuln['FixedVersion']}"
                        
                        vulns.append(vuln_entry)
                        
        except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError):
            # Trivy not available or failed
            pass
        
        return vulns if vulns else None
    
    def _get_conan_version(self) -> str:
        """Get Conan version"""
        try:
            result = subprocess.run(['conan', '--version'], 
                                  capture_output=True, text=True, check=True)
            return result.stdout.strip().split()[-1]
        except subprocess.CalledProcessError:
            return "unknown"
    
    def _get_project_name(self) -> str:
        """Extract project name from conanfile"""
        try:
            with open(self.conanfile_path, 'r') as f:
                content = f.read()
                
            # Look for name = "..." pattern
            import re
            match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                return match.group(1)
                
        except FileNotFoundError:
            pass
        
        # Fallback to directory name
        return self.project_root.name
    
    def _get_project_version(self) -> str:
        """Extract project version"""
        try:
            with open(self.conanfile_path, 'r') as f:
                content = f.read()
                
            # Look for version = "..." pattern
            import re
            match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                return match.group(1)
                
        except FileNotFoundError:
            pass
        
        return "0.1.0"
    
    def _calculate_source_hash(self) -> Optional[str]:
        """Calculate hash of source files"""
        
        hash_sha256 = hashlib.sha256()
        source_files = []
        
        # Find source files
        for pattern in ['**/*.cpp', '**/*.c', '**/*.h', '**/*.hpp']:
            source_files.extend(self.project_root.glob(pattern))
        
        # Sort for reproducible hash
        source_files.sort()
        
        for file_path in source_files:
            try:
                with open(file_path, 'rb') as f:
                    hash_sha256.update(f.read())
            except (IOError, OSError):
                continue
        
        return hash_sha256.hexdigest() if source_files else None
    
    def _find_license_file(self) -> Optional[Path]:
        """Find license file in project"""
        
        license_names = ['LICENSE', 'LICENSE.txt', 'LICENSE.md', 'COPYING']
        
        for name in license_names:
            license_path = self.project_root / name
            if license_path.exists():
                return license_path
        
        return None
    
    def _detect_license(self, license_file: Path) -> str:
        """Detect license type from file content"""
        
        try:
            with open(license_file, 'r', encoding='utf-8') as f:
                content = f.read().upper()
                
            # Simple license detection
            if 'MIT' in content:
                return 'MIT'
            elif 'APACHE' in content:
                return 'Apache-2.0'
            elif 'GPL' in content:
                if 'VERSION 3' in content:
                    return 'GPL-3.0'
                elif 'VERSION 2' in content:
                    return 'GPL-2.0'
                else:
                    return 'GPL'
            elif 'BSD' in content:
                return 'BSD'
                
        except (IOError, UnicodeDecodeError):
            pass
        
        return 'Unknown'
    
    def _get_package_license(self, name: str, version: str) -> Optional[List[Dict[str, Any]]]:
        """Get license information for a package"""
        
        # This would typically query a package registry or database
        # For now, return None (could be enhanced with actual license lookup)
        return None
    
    def _convert_to_spdx_packages(self, components: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert CycloneDX components to SPDX packages"""
        
        packages = []
        
        for component in components:
            package = {
                "SPDXID": f"SPDXRef-{component['name']}-{component['version']}",
                "name": component["name"],
                "downloadLocation": "NOASSERTION",
                "filesAnalyzed": False,
                "copyrightText": "NOASSERTION"
            }
            
            if "version" in component:
                package["versionInfo"] = component["version"]
            
            if "licenses" in component:
                package["licenseConcluded"] = component["licenses"][0]["license"]["name"]
            
            packages.append(package)
        
        return packages
    
    def _convert_to_spdx_relationships(self, dependencies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert dependency relationships to SPDX format"""
        
        relationships = []
        
        for dep in dependencies:
            relationship = {
                "spdxElementId": "SPDXRef-DOCUMENT",
                "relationshipType": "DEPENDS_ON",
                "relatedSpdxElement": f"SPDXRef-{dep['ref']}"
            }
            relationships.append(relationship)
        
        return relationships


def main():
    """Command line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate SBOM for C/C++ projects with Conan")
    parser.add_argument("--conanfile", default="conanfile.py", 
                       help="Path to conanfile.py")
    parser.add_argument("--format", choices=["cyclonedx", "spdx", "both"], 
                       default="both", help="SBOM format to generate")
    parser.add_argument("--output-dir", default=".", 
                       help="Output directory for SBOM files")
    
    args = parser.parse_args()
    
    generator = SBOMGenerator(args.conanfile)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    if args.format in ["cyclonedx", "both"]:
        cyclonedx_path = output_dir / "sbom-cyclonedx.json"
        sbom_cyclonedx = generator.generate_cyclone_dx(str(cyclonedx_path))
        print(f"Generated CycloneDX SBOM: {cyclonedx_path}")
        print(f"  Components: {len(sbom_cyclonedx.get('components', []))}")
        if sbom_cyclonedx.get('vulnerabilities'):
            print(f"  Vulnerabilities: {len(sbom_cyclonedx['vulnerabilities'])}")
    
    if args.format in ["spdx", "both"]:
        spdx_path = output_dir / "sbom-spdx.json"
        sbom_spdx = generator.generate_spdx(str(spdx_path))
        print(f"Generated SPDX SBOM: {spdx_path}")
        print(f"  Packages: {len(sbom_spdx.get('packages', []))}")


if __name__ == "__main__":
    main()