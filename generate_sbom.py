#!/usr/bin/env python3
"""
Mock SBOM Generator
Simulates syft SBOM generation when syft is not available
"""

import json
import os
from pathlib import Path
from datetime import datetime

def generate_mock_sbom(output_file):
    """Generate a mock SBOM in SPDX JSON format"""
    sbom = {
        "spdxVersion": "SPDX-2.3",
        "dataLicense": "CC0-1.0",
        "SPDXID": "SPDXRef-DOCUMENT",
        "name": "openssl-tools-SBOM",
        "creationInfo": {
            "created": datetime.utcnow().isoformat() + "Z",
            "creators": ["Tool: mock-sbom-generator-1.0.0"],
            "licenseListVersion": "3.16"
        },
        "packages": [
            {
                "SPDXID": "SPDXRef-Package-openssl-tools",
                "name": "openssl-tools",
                "versionInfo": "0.1.0",
                "downloadLocation": "NOASSERTION",
                "filesAnalyzed": False,
                "supplier": "Organization: sparesparrow",
                "originator": "Organization: sparesparrow",
                "copyrightText": "Apache-2.0",
                "licenseConcluded": "Apache-2.0",
                "licenseDeclared": "Apache-2.0",
                "description": "OpenSSL development and build tools with Python environment management"
            },
            {
                "SPDXID": "SPDXRef-Package-python",
                "name": "python",
                "versionInfo": "3.8+",
                "downloadLocation": "NOASSERTION",
                "filesAnalyzed": False,
                "supplier": "Organization: Python Software Foundation",
                "licenseConcluded": "Python-2.0",
                "licenseDeclared": "Python-2.0"
            },
            {
                "SPDXID": "SPDXRef-Package-conan",
                "name": "conan",
                "versionInfo": "2.0.17",
                "downloadLocation": "NOASSERTION",
                "filesAnalyzed": False,
                "supplier": "Organization: JFrog",
                "licenseConcluded": "MIT",
                "licenseDeclared": "MIT"
            }
        ],
        "relationships": [
            {
                "spdxElementId": "SPDXRef-DOCUMENT",
                "relatedSpdxElement": "SPDXRef-Package-openssl-tools",
                "relationshipType": "DESCRIBES"
            }
        ]
    }

    with open(output_file, 'w') as f:
        json.dump(sbom, f, indent=2)

    print(f"✅ Mock SBOM generated: {output_file}")

def main():
    """Main function to generate SBOM"""
    output_file = "sbom-tools.json"

    # Try to use real syft if available
    try:
        import subprocess
        result = subprocess.run(
            ["syft", "packages", "dir:.", "-o", "spdx-json"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            with open(output_file, 'w') as f:
                f.write(result.stdout)
            print(f"✅ Real SBOM generated using syft: {output_file}")
            return
        else:
            print("⚠️  syft command failed, using mock SBOM")
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        print("ℹ️  syft not available, using mock SBOM")

    # Generate mock SBOM
    generate_mock_sbom(output_file)

if __name__ == "__main__":
    main()