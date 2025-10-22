from conan.api.conan_api import ConanAPI
from conan.cli.command import conan_command
import json

@conan_command(group="OpenSSL")
def graph(conan_api: ConanAPI, parser, *args):
    """
    Analyze OpenSSL dependency graph
    
    Usage:
        conan openssl:graph [--json]
    
    Examples:
        conan openssl:graph
        conan openssl:graph --json > graph.json
    """
    parser.add_argument("--json", action="store_true",
                       help="Output in JSON format")
    
    args = parser.parse_args(*args)
    
    # Simple analysis without complex graph loading
    try:
        # Try to get basic dependency info from conanfile.txt
        import os
        if os.path.exists("conanfile.txt"):
            with open("conanfile.txt", "r") as f:
                content = f.read()
                # Simple parsing for requires
                requires = []
                in_requires = False
                for line in content.split('\n'):
                    line = line.strip()
                    if line == "[requires]":
                        in_requires = True
                        continue
                    elif line.startswith('[') and line != "[requires]":
                        in_requires = False
                        continue
                    elif in_requires and line and not line.startswith('#'):
                        requires.append(line)
                
                results = {
                    "total_deps": len(requires),
                    "dependencies": [{"name": req.split('/')[0], "version": req.split('/')[1] if '/' in req else "unknown"} for req in requires],
                    "fips_enabled": []
                }
        else:
            results = {
                "total_deps": 0,
                "dependencies": [],
                "fips_enabled": [],
                "message": "No conanfile.txt found in current directory"
            }
    except Exception as e:
        results = {
            "total_deps": 0,
            "dependencies": [],
            "fips_enabled": [],
            "error": str(e)
        }
    
    # Output
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(f"📊 Total dependencies: {results['total_deps']}")
        if "fips_enabled" in results and results["fips_enabled"]:
            print(f"🔒 FIPS enabled: {', '.join(results['fips_enabled'])}")
        if "dependencies" in results and results["dependencies"]:
            print("Dependencies:")
            for dep in results["dependencies"]:
                print(f"  - {dep['name']}/{dep['version']}")
        if "message" in results:
            print(f"ℹ️  {results['message']}")
        if "error" in results:
            print(f"❌ Error: {results['error']}")

    conan_api.graph.load_graph_consumer(".", requires=["openssl/[>=3.0]"])      

def analyze_dependencies(graph):
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
