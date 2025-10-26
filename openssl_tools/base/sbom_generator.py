"""
Enhanced SBOM generation for OpenSSL packages with SPDX 2.3 support
"""

import json
import os
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class SbomGenerator:
    """Generates CycloneDX and SPDX SBOMs for OpenSSL packages"""

    def __init__(self, conanfile):
        self.conanfile = conanfile
        self.package_folder = Path(conanfile.package_folder)

    def generate_and_save(self, format: str = "cyclonedx"):
        """Generate and save SBOM in specified format"""
        try:
            if format.lower() == "spdx":
                sbom_data = self._generate_spdx_sbom()
                sbom_path = self.package_folder / "sbom.spdx.json"
            else:
                sbom_data = self._generate_cyclonedx_sbom()
                sbom_path = self.package_folder / "sbom.json"

            with open(sbom_path, 'w') as f:
                json.dump(sbom_data, f, indent=2)

            self.conanfile.output.info(f"Generated {format.upper()} SBOM at {sbom_path}")

            # Also generate SPDX for compliance (dual format)
            if format.lower() != "spdx":
                spdx_data = self._generate_spdx_sbom()
                spdx_path = self.package_folder / "sbom.spdx.json"
                with open(spdx_path, 'w') as f:
                    json.dump(spdx_data, f, indent=2)
                self.conanfile.output.info(f"Generated SPDX SBOM at {spdx_path}")

        except Exception as e:
            self.conanfile.output.warning(f"SBOM generation failed: {e}")

    def _generate_cyclonedx_sbom(self) -> Dict[str, Any]:
        """Generate CycloneDX SBOM data"""
        components = []

        # Add main package component
        components.append({
            "type": "library",
            "name": self.conanfile.name,
            "version": self.conanfile.version,
            "purl": f"pkg:conan/{self.conanfile.name}@{self.conanfile.version}",
            "scope": "required",
            "properties": [
                {
                    "name": "supplier",
                    "value": "Organization: sparesparrow"
                },
                {
                    "name": "originator",
                    "value": "Organization: sparesparrow"
                }
            ]
        })

        # Add dependencies
        if hasattr(self.conanfile, 'dependencies'):
            for dep_name, dep_info in self.conanfile.dependencies.items():
                components.append({
                    "type": "library",
                    "name": dep_name,
                    "version": getattr(dep_info, 'version', 'unknown'),
                    "purl": f"pkg:conan/{dep_name}@{getattr(dep_info, 'version', 'unknown')}",
                    "scope": "required"
                })

        # Determine FIPS certificate if applicable
        fips_cert = None
        if hasattr(self.conanfile.options, 'fips') and self.conanfile.options.fips:
            fips_cert = "FIPS 140-3 Certificate #4985"

        return {
            "bomFormat": "CycloneDX",
            "specVersion": "1.5",
            "serialNumber": f"urn:uuid:openssl-{self.conanfile.version}",
            "version": 1,
            "metadata": {
                "timestamp": self._get_timestamp(),
                "tools": [{
                    "vendor": "sparesparrow",
                    "name": "openssl-tools",
                    "version": "2.1.0"
                }],
                "component": {
                    "type": "library",
                    "name": self.conanfile.name,
                    "version": self.conanfile.version,
                    "purl": f"pkg:conan/{self.conanfile.name}@{self.conanfile.version}",
                    "properties": [
                        {
                            "name": "fips_enabled",
                            "value": str(getattr(self.conanfile.options, 'fips', False))
                        },
                        {
                            "name": "license_concluded",
                            "value": "Apache-2.0"
                        }
                    ]
                }
            },
            "components": components
        }

    def _generate_spdx_sbom(self) -> Dict[str, Any]:
        """Generate SPDX 2.3 SBOM data"""
        # Create SPDX document
        doc_namespace = f"https://github.com/sparesparrow/openssl/sbom/{self.conanfile.name}/{self.conanfile.version}"
        doc_id = f"SPDXRef-DOCUMENT"

        # Main package
        main_package_id = "SPDXRef-Package-openssl"
        main_package = {
            "SPDXID": main_package_id,
            "name": self.conanfile.name,
            "downloadLocation": "NOASSERTION",
            "filesAnalyzed": False,  # For conan packages, we don't analyze individual files
            "licenseConcluded": "Apache-2.0",
            "licenseDeclared": "Apache-2.0",
            "copyrightText": "Copyright (c) sparesparrow",
            "originator": "Organization: sparesparrow",
            "supplier": "Organization: sparesparrow",
            "versionInfo": self.conanfile.version
        }

        packages = [main_package]
        relationships = [
            {
                "spdxElementId": doc_id,
                "relationshipType": "DESCRIBES",
                "relatedSpdxElement": main_package_id
            }
        ]

        # Add dependencies as packages
        if hasattr(self.conanfile, 'dependencies'):
            for i, (dep_name, dep_info) in enumerate(self.conanfile.dependencies.items(), 1):
                dep_id = f"SPDXRef-Package-{dep_name.lower()}-{i}"
                dep_package = {
                    "SPDXID": dep_id,
                    "name": dep_name,
                    "downloadLocation": "NOASSERTION",
                    "filesAnalyzed": False,
                    "licenseConcluded": "NOASSERTION",
                    "licenseDeclared": "NOASSERTION",
                    "copyrightText": "NOASSERTION",
                    "versionInfo": getattr(dep_info, 'version', 'unknown')
                }
                packages.append(dep_package)

                # Add relationship
                relationships.append({
                    "spdxElementId": main_package_id,
                    "relationshipType": "DEPENDS_ON",
                    "relatedSpdxElement": dep_id
                })

        return {
            "spdxVersion": "SPDX-2.3",
            "dataLicense": "CC0-1.0",
            "SPDXID": doc_id,
            "name": f"{self.conanfile.name}-{self.conanfile.version}",
            "documentNamespace": doc_namespace,
            "creationInfo": {
                "created": self._get_timestamp(),
                "creators": [
                    "Tool: openssl-tools-2.1.0",
                    "Organization: sparesparrow"
                ],
                "licenseListVersion": "3.22"
            },
            "packages": packages,
            "relationships": relationships
        }

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        return datetime.utcnow().isoformat() + "Z"

    def _calculate_file_hash(self, file_path: Path) -> Optional[str]:
        """Calculate SHA-256 hash of a file"""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception:
            return None
