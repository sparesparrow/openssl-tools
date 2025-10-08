#!/usr/bin/env python3
"""
Rebuild Analysis Tool for Conan Dependencies
Analyzes why packages are being rebuilt and provides optimization suggestions
"""

import json
import hashlib
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class PackageInfo:
    """Information about a package and its rebuild reasons"""
    name: str
    version: str
    package_id: str
    settings: Dict[str, Any]
    options: Dict[str, Any]
    requires: List[str]
    build_requires: List[str]
    rebuild_reasons: List[str]
    last_built: Optional[datetime] = None
    cache_available: bool = False


class RebuildAnalyzer:
    """Analyzes Conan dependency graphs to identify rebuild causes"""
    
    def __init__(self, conanfile_path: str = "conanfile.py"):
        self.conanfile_path = conanfile_path
        self.packages: Dict[str, PackageInfo] = {}
        self.rebuild_stats = {
            "total_packages": 0,
            "rebuilt_packages": 0,
            "cache_hits": 0,
            "rebuild_reasons": {}
        }
    
    def analyze_dependency_graph(self, profile_path: str) -> Dict[str, Any]:
        """Analyze the dependency graph and identify rebuild reasons"""
        
        print(f"Analyzing dependency graph with profile: {profile_path}")
        
        # Get dependency graph
        graph_data = self._get_dependency_graph(profile_path)
        if not graph_data:
            return {}
        
        # Analyze each package
        for node_id, node in graph_data.get("graph", {}).items():
            if node_id == "0":  # Skip root node
                continue
                
            package_info = self._analyze_package_node(node)
            if package_info:
                self.packages[package_info.name] = package_info
        
        # Generate analysis report
        return self._generate_analysis_report()
    
    def _get_dependency_graph(self, profile_path: str) -> Optional[Dict[str, Any]]:
        """Get dependency graph from Conan"""
        
        try:
            cmd = [
                'conan', 'graph', 'info', self.conanfile_path,
                f'--profile={profile_path}',
                '--format=json'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return json.loads(result.stdout)
            
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            print(f"Error getting dependency graph: {e}")
            return None
    
    def _analyze_package_node(self, node: Dict[str, Any]) -> Optional[PackageInfo]:
        """Analyze a single package node"""
        
        ref = node.get("ref", "")
        if not ref or "/" not in ref:
            return None
        
        # Parse reference
        name, version_part = ref.split("/", 1)
        version = version_part.split("@")[0]
        
        # Extract package information
        settings = node.get("settings", {})
        options = node.get("options", {})
        package_id = node.get("package_id", "")
        requires = node.get("requires", [])
        build_requires = node.get("build_requires", [])
        
        # Check if package is available in cache
        cache_available = self._check_cache_availability(name, version, package_id)
        
        # Determine rebuild reasons
        rebuild_reasons = self._determine_rebuild_reasons(
            name, version, settings, options, requires, cache_available
        )
        
        return PackageInfo(
            name=name,
            version=version,
            package_id=package_id,
            settings=settings,
            options=options,
            requires=requires,
            build_requires=build_requires,
            rebuild_reasons=rebuild_reasons,
            cache_available=cache_available
        )
    
    def _check_cache_availability(self, name: str, version: str, package_id: str) -> bool:
        """Check if package is available in cache"""
        
        try:
            cmd = ['conan', 'list', f'{name}/{version}:', '--package-id', package_id]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0 and package_id in result.stdout
        except subprocess.CalledProcessError:
            return False
    
    def _determine_rebuild_reasons(self, name: str, version: str, settings: Dict[str, Any], 
                                 options: Dict[str, Any], requires: List[str], 
                                 cache_available: bool) -> List[str]:
        """Determine why a package needs to be rebuilt"""
        
        reasons = []
        
        if not cache_available:
            reasons.append("package_not_in_cache")
        
        # Check for settings that commonly cause rebuilds
        if settings.get("compiler.version") and self._is_uncommon_compiler_version(settings["compiler.version"]):
            reasons.append("uncommon_compiler_version")
        
        if settings.get("build_type") == "Debug":
            reasons.append("debug_build_type")
        
        # Check for options that affect package ID
        if options:
            for option, value in options.items():
                if value != self._get_default_option_value(name, option):
                    reasons.append(f"non_default_option_{option}")
        
        # Check for dependency changes
        if self._has_dependency_changes(requires):
            reasons.append("dependency_changes")
        
        # Check for recent source changes
        if self._has_recent_source_changes(name):
            reasons.append("recent_source_changes")
        
        return reasons or ["unknown"]
    
    def _is_uncommon_compiler_version(self, version: str) -> bool:
        """Check if compiler version is uncommon"""
        
        # Common versions that usually have good cache coverage
        common_versions = {
            "gcc": ["9", "10", "11", "12"],
            "clang": ["12", "13", "14", "15"],
            "msvc": ["191", "192", "193"]
        }
        
        for compiler, versions in common_versions.items():
            if version in versions:
                return False
        
        return True
    
    def _get_default_option_value(self, package_name: str, option: str) -> Any:
        """Get default value for a package option"""
        
        # This would typically query the package recipe
        # For now, return common defaults
        common_defaults = {
            "shared": False,
            "fPIC": True,
            "header_only": False
        }
        
        return common_defaults.get(option, None)
    
    def _has_dependency_changes(self, requires: List[str]) -> bool:
        """Check if dependencies have changed recently"""
        
        # This would typically compare against a baseline
        # For now, assume no changes
        return False
    
    def _has_recent_source_changes(self, package_name: str) -> bool:
        """Check if package has recent source changes"""
        
        # This would typically check git history or package timestamps
        # For now, assume no recent changes
        return False
    
    def _generate_analysis_report(self) -> Dict[str, Any]:
        """Generate comprehensive analysis report"""
        
        # Update statistics
        self.rebuild_stats["total_packages"] = len(self.packages)
        self.rebuild_stats["cache_hits"] = sum(1 for p in self.packages.values() if p.cache_available)
        self.rebuild_stats["rebuilt_packages"] = self.rebuild_stats["total_packages"] - self.rebuild_stats["cache_hits"]
        
        # Count rebuild reasons
        reason_counts = {}
        for package in self.packages.values():
            for reason in package.rebuild_reasons:
                reason_counts[reason] = reason_counts.get(reason, 0) + 1
        
        self.rebuild_stats["rebuild_reasons"] = reason_counts
        
        # Generate recommendations
        recommendations = self._generate_recommendations()
        
        # Create detailed package analysis
        package_analysis = {}
        for name, package in self.packages.items():
            package_analysis[name] = {
                "version": package.version,
                "package_id": package.package_id,
                "cache_available": package.cache_available,
                "rebuild_reasons": package.rebuild_reasons,
                "settings": package.settings,
                "options": package.options,
                "optimization_potential": self._assess_optimization_potential(package)
            }
        
        return {
            "analysis_timestamp": datetime.now().isoformat(),
            "summary": self.rebuild_stats,
            "packages": package_analysis,
            "recommendations": recommendations,
            "optimization_score": self._calculate_optimization_score()
        }
    
    def _generate_recommendations(self) -> List[Dict[str, str]]:
        """Generate optimization recommendations"""
        
        recommendations = []
        
        # Cache hit rate recommendations
        cache_hit_rate = self.rebuild_stats["cache_hits"] / max(self.rebuild_stats["total_packages"], 1)
        
        if cache_hit_rate < 0.5:
            recommendations.append({
                "type": "cache_optimization",
                "priority": "high",
                "title": "Low cache hit rate detected",
                "description": f"Only {cache_hit_rate:.1%} of packages found in cache",
                "action": "Review package ID strategy and remote configuration"
            })
        
        # Compiler version recommendations
        reason_counts = self.rebuild_stats["rebuild_reasons"]
        if reason_counts.get("uncommon_compiler_version", 0) > 0:
            recommendations.append({
                "type": "compiler_standardization",
                "priority": "medium",
                "title": "Uncommon compiler versions detected",
                "description": f"{reason_counts['uncommon_compiler_version']} packages using uncommon compiler versions",
                "action": "Standardize on common compiler versions for better cache reuse"
            })
        
        # Debug build recommendations
        if reason_counts.get("debug_build_type", 0) > 0:
            recommendations.append({
                "type": "build_type_optimization",
                "priority": "low",
                "title": "Debug builds detected",
                "description": f"{reason_counts['debug_build_type']} packages built in Debug mode",
                "action": "Consider using Release builds for dependencies in CI"
            })
        
        # Non-default options recommendations
        non_default_options = sum(1 for reason in reason_counts.keys() if reason.startswith("non_default_option_"))
        if non_default_options > 0:
            recommendations.append({
                "type": "option_standardization", 
                "priority": "medium",
                "title": "Non-default options detected",
                "description": f"{non_default_options} packages using non-default options",
                "action": "Review option usage and consider using defaults for better cache reuse"
            })
        
        return recommendations
    
    def _assess_optimization_potential(self, package: PackageInfo) -> str:
        """Assess optimization potential for a package"""
        
        if package.cache_available:
            return "none"
        
        # High potential if commonly used settings
        if (package.settings.get("build_type") == "Release" and 
            package.settings.get("compiler") in ["gcc", "clang"] and
            not any(reason.startswith("non_default_option_") for reason in package.rebuild_reasons)):
            return "high"
        
        # Medium potential if some issues can be addressed
        if len(package.rebuild_reasons) <= 2:
            return "medium"
        
        return "low"
    
    def _calculate_optimization_score(self) -> float:
        """Calculate overall optimization score (0-100)"""
        
        if self.rebuild_stats["total_packages"] == 0:
            return 100.0
        
        cache_hit_rate = self.rebuild_stats["cache_hits"] / self.rebuild_stats["total_packages"]
        
        # Base score from cache hit rate
        score = cache_hit_rate * 70
        
        # Bonus points for good practices
        reason_counts = self.rebuild_stats["rebuild_reasons"]
        total_reasons = sum(reason_counts.values())
        
        if total_reasons > 0:
            # Penalty for problematic reasons
            problematic_reasons = ["uncommon_compiler_version", "dependency_changes"]
            problematic_count = sum(reason_counts.get(reason, 0) for reason in problematic_reasons)
            penalty = (problematic_count / total_reasons) * 20
            score -= penalty
        
        # Bonus for high optimization potential packages
        high_potential_count = sum(1 for p in self.packages.values() 
                                 if self._assess_optimization_potential(p) == "high")
        if high_potential_count > 0:
            score += min(high_potential_count * 2, 10)
        
        return max(0, min(100, score))
    
    def print_summary_report(self, analysis: Dict[str, Any]):
        """Print a human-readable summary report"""
        
        print("\n" + "="*60)
        print("CONAN REBUILD ANALYSIS REPORT")
        print("="*60)
        
        summary = analysis["summary"]
        print(f"\n📊 SUMMARY:")
        print(f"   Total packages: {summary['total_packages']}")
        print(f"   Cache hits: {summary['cache_hits']}")
        print(f"   Rebuilt packages: {summary['rebuilt_packages']}")
        
        if summary['total_packages'] > 0:
            cache_rate = summary['cache_hits'] / summary['total_packages']
            print(f"   Cache hit rate: {cache_rate:.1%}")
        
        print(f"\n🎯 Optimization Score: {analysis['optimization_score']:.1f}/100")
        
        print(f"\n🔍 REBUILD REASONS:")
        for reason, count in summary['rebuild_reasons'].items():
            print(f"   {reason}: {count}")
        
        print(f"\n💡 RECOMMENDATIONS:")
        for i, rec in enumerate(analysis['recommendations'], 1):
            priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
            emoji = priority_emoji.get(rec['priority'], "ℹ️")
            print(f"   {i}. {emoji} [{rec['priority'].upper()}] {rec['title']}")
            print(f"      {rec['description']}")
            print(f"      Action: {rec['action']}\n")
        
        print(f"📦 PACKAGE DETAILS:")
        for name, details in analysis['packages'].items():
            cache_status = "✅ CACHED" if details['cache_available'] else "🔨 REBUILD"
            opt_potential = details['optimization_potential'].upper()
            print(f"   {name} {details['version']}: {cache_status} (Opt: {opt_potential})")
            if details['rebuild_reasons']:
                print(f"      Reasons: {', '.join(details['rebuild_reasons'])}")


def main():
    """Command line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze Conan rebuild patterns")
    parser.add_argument("--conanfile", default="conanfile.py", 
                       help="Path to conanfile.py")
    parser.add_argument("--profile", required=True,
                       help="Conan profile to analyze")
    parser.add_argument("--output", help="Output JSON file for detailed analysis")
    parser.add_argument("--summary-only", action="store_true",
                       help="Show only summary report")
    
    args = parser.parse_args()
    
    analyzer = RebuildAnalyzer(args.conanfile)
    analysis = analyzer.analyze_dependency_graph(args.profile)
    
    if not analysis:
        print("❌ Failed to analyze dependency graph")
        sys.exit(1)
    
    # Print summary report
    analyzer.print_summary_report(analysis)
    
    # Save detailed analysis if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(analysis, f, indent=2)
        print(f"\n📄 Detailed analysis saved to: {args.output}")
    
    # Exit with error code if optimization score is low
    if analysis['optimization_score'] < 50:
        print(f"\n⚠️  Low optimization score detected. Consider implementing recommendations.")
        sys.exit(1)


if __name__ == "__main__":
    main()