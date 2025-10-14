#!/usr/bin/env python3
import sys
import json
import argparse
from typing import Any, Dict

try:
    from conan.api.conan_api import ConanAPI
except Exception:
    ConanAPI = None


def analyze(conanfile: str, build_type: str = "Release") -> Dict[str, Any]:
    api = ConanAPI()
    profile_host = None
    graph = api.graph.load_conanfile(
        conanfile_path=conanfile,
        profile_build=None,
        profile_host=profile_host,
        lockfile=None,
        remotes=api.remotes.list(),
        requires=None,
    )

    result = {
        "nodes": [],
        "conflicts": [],
        "outdated": [],
    }

    for node in graph.direct_nodes:
        result["nodes"].append({
            "ref": str(node.ref) if node.ref else None,
            "requires": [str(r.ref) for r in node.requires] if hasattr(node, 'requires') else [],
        })

    # Simple conflict/outdated heuristics (extend as needed)
    seen = {}
    for n in result["nodes"]:
        ref = n["ref"]
        if not ref:
            continue
        name = ref.split("/")[0]
        seen.setdefault(name, set()).add(ref)
    for name, refs in seen.items():
        if len(refs) > 1:
            result["conflicts"].append({"name": name, "versions": sorted(refs)})

    return result


def main():
    parser = argparse.ArgumentParser(description="Analyze Conan dependency graph")
    parser.add_argument("conanfile", help="Path to conanfile.py or conanfile.txt")
    parser.add_argument("--build-type", default="Release")
    parser.add_argument("--fail-on-conflict", action="store_true")
    args = parser.parse_args()

    if ConanAPI is None:
        print("ConanAPI not available; please ensure Conan 2.x is installed", file=sys.stderr)
        sys.exit(2)

    report = analyze(args.conanfile, args.build_type)
    print(json.dumps(report, indent=2))

    if args.fail_on_conflict and report["conflicts"]:
        print("Conflicts detected", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
