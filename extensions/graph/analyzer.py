def analyze_dependencies(graph):
    """Analyzuje dependency graph"""
    results = {
        "total_deps": len(graph.dependencies),
        "conflicts": [],
        "outdated": [],
        "fips_enabled": []
    }
    
    for dep in graph.dependencies.values():
        # Detekce FIPS
        if hasattr(dep.conanfile, "options") and \
           dep.conanfile.options.get_safe("enable_fips"):
            results["fips_enabled"].append(str(dep.ref))
    
    return results

