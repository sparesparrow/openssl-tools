import os
import json
from pathlib import Path

def deploy(graph, output_folder: str, **kwargs):
    """Enhanced deployer s SBOM generation a FIPS artifacts"""
    conanfile = graph.root.conanfile
    
    # Deploy all packages
    for dep in graph.dependencies.values():
        _deploy_package(dep, output_folder)
    
    # Generate SBOM
    sbom_path = _generate_sbom(graph, output_folder)
    conanfile.output.info(f"SBOM: {sbom_path}")
    
    # FIPS artifacts
    if _is_fips_enabled(graph):
        _deploy_fips_artifacts(graph, output_folder)

def _deploy_package(dep, output_folder):
    from conan.tools.files import copy
    target = os.path.join(
        output_folder, "full_deploy", "host",
        dep.ref.name, str(dep.ref.version)
    )
    copy(dep.conanfile, "*", src=dep.package_folder, dst=target)

def _generate_sbom(graph, output_folder):
    sbom = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.4",
        "components": [
            {
                "type": "library",
                "name": dep.ref.name,
                "version": str(dep.ref.version),
                "purl": f"pkg:conan/{dep.ref.name}@{dep.ref.version}"
            }
            for dep in graph.dependencies.values()
        ]
    }
    sbom_path = os.path.join(output_folder, "sbom.json")
    with open(sbom_path, "w") as f:
        json.dump(sbom, f, indent=2)
    return sbom_path

def _is_fips_enabled(graph):
    return any(
        hasattr(dep.conanfile, "options") and 
        dep.conanfile.options.get_safe("enable_fips")
        for dep in graph.dependencies.values()
    )

def _deploy_fips_artifacts(graph, output_folder):
    from conan.tools.files import copy
    fips_folder = os.path.join(output_folder, "fips")
    os.makedirs(fips_folder, exist_ok=True)
    
    for dep in graph.dependencies.values():
        if dep.ref.name == "openssl":
            copy(dep.conanfile, "fipsmodule.cnf",
                 src=os.path.join(dep.package_folder, "ssl"),
                 dst=fips_folder)



