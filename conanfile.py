#!/usr/bin/env python3
"""
OpenSSL Tools Conan Package Recipe
Python tools for OpenSSL development with Conan 2.x integration
Based on ngapy-dev patterns for proper Python dev/testing environment
"""

from conan import ConanFile
from conan.tools.files import copy, save, load
from conan.tools.scm import Git
from conan.tools.env import VirtualBuildEnv
from conan.tools.gnu import PkgConfigDeps
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain
from conan.errors import ConanInvalidConfiguration
from datetime import datetime, timezone
import os
import glob
import logging
import sys
import json
import uuid
from pathlib import Path


class OpenSSLToolsConan(ConanFile):
    name = "openssl-tools"
    version = "1.0.0"
    
    # Package metadata
    description = "Python tools for OpenSSL development, review, and release management"
    homepage = "https://github.com/sparesparrow/openssl-tools"
    url = "https://github.com/sparesparrow/openssl-tools"
    license = "Apache-2.0"
    topics = ("openssl", "tools", "development", "review", "release")
    
    # Package configuration
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "enable_review_tools": [True, False],
        "enable_release_tools": [True, False],
        "enable_statistics": [True, False],
        "enable_github_integration": [True, False],
        "enable_gitlab_integration": [True, False],
        "enable_api_integration": [True, False],
    }
    
    default_options = {
        "enable_review_tools": True,
        "enable_release_tools": True,
        "enable_statistics": True,
        "enable_github_integration": True,
        "enable_gitlab_integration": False,
        "enable_api_integration": True,
    }
    
    # Python package - no build requirements for Python tools
    def build_requirements(self):
        # Install Python dependencies via pip
        import subprocess
        
        # Core dependencies
        core_deps = ["requests>=2.31.0", "click>=8.1.0", "pyyaml>=6.0.0", "jinja2>=3.1.0"]
        
        # Install optional dependencies based on options
        if self.options.enable_statistics:
            core_deps.extend(["numpy>=1.20.0", "scipy>=1.7.0"])
            
        if self.options.enable_github_integration:
            core_deps.append("pygithub>=1.59.0")
            
        if self.options.enable_gitlab_integration:
            core_deps.append("python-gitlab>=4.0.0")
            
        if self.options.enable_api_integration:
            core_deps.append("httpx>=0.25.0")
        
        # Install dependencies
        for dep in core_deps:
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", dep], check=True)
            except subprocess.CalledProcessError as e:
                self.output.warning(f"Failed to install {dep}: {e}")
    
    # Python dependencies - handled by pip in build_requirements
    def requirements(self):
        # No C++ dependencies for Python tools
        pass

    def set_version(self):
        """Set version from git or default - following ngapy patterns"""
        try:
            git = Git(self)
            # Get version from git describe or use default
            version = git.run("describe --tags --always --dirty")
            if version:
                # Clean up version string
                version = version.strip().replace("v", "")
                self.version = version
            else:
                self.version = "1.0.0"
        except:
            self.version = "1.0.0"

    def system_requirements(self):
        """System requirements - Python 3.8+ required"""
        import sys
        if sys.version_info < (3, 8):
            raise ConanInvalidConfiguration("Python 3.8 or higher is required")

    def configure(self):
        """Configure package options"""
        pass

    def validate(self):
        """Validate configuration"""
        # Validate Python version
        import sys
        if sys.version_info < (3, 8):
            raise ConanInvalidConfiguration("Python 3.8 or higher is required")

    def export_sources(self):
        """Export source files"""
        # Export all source files
        copy(self, "*", src=self.recipe_folder, dst=self.export_sources_folder)
        
    def layout(self):
        """Layout for Python package"""
        # Use basic layout for Python package
        pass
        
    def generate(self):
        """Generate configuration files"""
        # Generate tools configuration
        self._generate_tools_config()
        
    def _generate_tools_config(self):
        """Generate tools configuration file following ngapy patterns"""
        config = {
            "tools": {
                "review_tools": {
                    "enabled": self.options.enable_review_tools,
                    "min_reviewers": 2,
                    "min_otc": 0,
                    "min_omc": 0,
                    "api_endpoint": "https://api.openssl.org"
                },
                "release_tools": {
                    "enabled": self.options.enable_release_tools,
                    "templates_dir": "templates",
                    "output_dir": "releases"
                },
                "statistics": {
                    "enabled": self.options.enable_statistics,
                    "alpha_chi2": 0.95,
                    "alpha_binomial": 0.9999
                },
                "github": {
                    "enabled": self.options.enable_github_integration,
                    "api_endpoint": "https://api.github.com"
                },
                "gitlab": {
                    "enabled": self.options.enable_gitlab_integration,
                    "api_endpoint": "https://gitlab.com/api/v4"
                }
            },
            "conan": {
                "package_name": self.name,
                "version": self.version,
                "build_type": "Release"  # Default for Python tools
            }
        }
        
        config_path = os.path.join(self.build_folder, "tools_config.json")
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        # Convert all options to strings for JSON serialization
        config["conan"]["build_options"] = {k: str(v) for k, v in self.options.items()}
        
        # Ensure all values are JSON serializable
        def make_json_serializable(obj):
            if hasattr(obj, '__dict__'):
                return {k: make_json_serializable(v) for k, v in obj.__dict__.items()}
            elif isinstance(obj, dict):
                return {k: make_json_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [make_json_serializable(item) for item in obj]
            else:
                return str(obj)
        
        config = make_json_serializable(config)
        save(self, config_path, json.dumps(config, indent=2))
        
    def build(self):
        """Build Python tools package with optimization following ngapy patterns"""
        # Set up build optimization
        self._setup_build_optimization()
        
        # Create Python package structure
        self._create_package_structure()
        
        # Convert Perl tools to Python
        if self.options.enable_review_tools:
            self._convert_review_tools()
            
        if self.options.enable_release_tools:
            self._convert_release_tools()
            
        # Integrate existing Python tools
        if self.options.enable_statistics:
            self._integrate_statistics_tools()
    
    def _setup_build_optimization(self):
        """Set up build optimization and caching following ngapy patterns"""
        try:
            from openssl_tools.utils.build_optimizer import BuildOptimizer
            
            # Build configuration
            config = {
                'source_dir': self.source_folder,
                'build_dir': self.build_folder,
                'max_jobs': int(os.environ.get('CONAN_CPU_COUNT', '4')),
                'enable_ccache': True,
                'enable_sccache': False,
                'optimize_build': True,
                'reproducible_builds': True
            }
            
            self.build_optimizer = BuildOptimizer(config)
            self.output.info("Build optimization enabled")
            
        except ImportError:
            self.output.warning("Build optimization not available")
            self.build_optimizer = None
    
    def _create_package_structure(self):
        """Create Python package structure following ngapy patterns"""
        package_dir = os.path.join(self.build_folder, "openssl_tools")
        os.makedirs(package_dir, exist_ok=True)
        
        # Create __init__.py
        init_content = '''"""
OpenSSL Tools Package
Python tools for OpenSSL development, review, and release management
"""

__version__ = "1.0.0"
__author__ = "OpenSSL Tools Team"
__license__ = "Apache-2.0"

# Import main modules
from .review_tools import *
from .release_tools import *
from .statistics import *
from .utils import *
'''
        save(self, os.path.join(package_dir, "__init__.py"), init_content)
        
        # Create subdirectories
        subdirs = ["review_tools", "release_tools", "statistics", "utils", "templates"]
        for subdir in subdirs:
            os.makedirs(os.path.join(package_dir, subdir), exist_ok=True)
            save(self, os.path.join(package_dir, subdir, "__init__.py"), "")
    
    def _convert_review_tools(self):
        """Convert Perl review tools to Python"""
        # This will be implemented in the next step
        pass
        
    def _convert_release_tools(self):
        """Convert release tools to Python"""
        # This will be implemented in the next step
        pass
        
    def _integrate_statistics_tools(self):
        """Integrate existing Python statistics tools"""
        # Copy existing Python tools
        stats_src = os.path.join(self.source_folder, "statistics")
        stats_dst = os.path.join(self.build_folder, "openssl_tools", "statistics")
        
        if os.path.exists(stats_src):
            copy(self, "*", src=stats_src, dst=stats_dst)
    
    def package(self):
        """Package the tools following ngapy patterns"""
        # Copy Python package
        copy(self, "openssl_tools", src=self.build_folder, dst=self.package_folder)
        
        # Copy configuration
        copy(self, "tools_config.json", src=self.build_folder, dst=self.package_folder)
        
        # Copy templates
        if self.options.enable_release_tools:
            templates_src = os.path.join(self.source_folder, "release-tools", "release-aux")
            templates_dst = os.path.join(self.package_folder, "templates")
            if os.path.exists(templates_src):
                copy(self, "*", src=templates_src, dst=templates_dst)
        
        # Copy documentation
        copy(self, "README*", src=self.source_folder, dst=self.package_folder)
        copy(self, "HOWTO-*.md", src=self.source_folder, dst=self.package_folder)
        
        # Generate SBOM
        self._generate_sbom()
        
    def _generate_sbom(self):
        """Generate Software Bill of Materials following ngapy patterns"""
        self.output.info("Generating Software Bill of Materials (SBOM)...")
        
        sbom_data = {
            "bomFormat": "CycloneDX",
            "specVersion": "1.5",
            "serialNumber": f"urn:uuid:{uuid.uuid4()}",
            "version": 1,
            "metadata": {
                "timestamp": str(os.environ.get("SOURCE_DATE_EPOCH", "")),
                "component": {
                    "type": "application",
                    "bom-ref": f"{self.name}@{self.version}",
                    "name": self.name,
                    "version": str(self.version),
                    "description": self.description,
                    "licenses": [{"license": {"id": "Apache-2.0"}}],
                    "externalReferences": [
                        {
                            "type": "website",
                            "url": self.homepage
                        },
                        {
                            "type": "vcs",
                            "url": self.url
                        }
                    ],
                    "properties": [
                        {"name": "package_type", "value": "python-tools"},
                        {"name": "conan_options", "value": json.dumps({k: str(v) for k, v in self.options.items()})},
                        {"name": "build_platform", "value": f"{self.settings.os}-{self.settings.arch}"}
                    ]
                },
                "tools": [
                    {
                        "vendor": "Conan",
                        "name": "conan",
                        "version": "2.0"
                    }
                ]
            },
            "components": [],
            "vulnerabilities": []
        }
        
        # Add dependencies to SBOM
        deps = getattr(self, "deps_cpp_info", None)
        if deps and hasattr(deps, "deps"):
            for dep in deps.deps:
                try:
                    dep_version = str(deps[dep].version) if hasattr(deps[dep], "version") else "unknown"
                    component = {
                        "type": "library",
                        "bom-ref": f"{dep}@{dep_version}",
                        "name": dep,
                        "version": dep_version,
                        "scope": "required",
                        "licenses": []
                    }
                    sbom_data["components"].append(component)
                except Exception as e:
                    self.output.warning(f"Failed to add dependency {dep} to SBOM: {e}")
        
        # Save SBOM
        sbom_path = os.path.join(self.package_folder, "sbom.json")
        save(self, sbom_path, json.dumps(sbom_data, indent=2))
        
    def package_info(self):
        """Package info following ngapy patterns"""
        # Python package info
        self.cpp_info.libs = []
        
        # Set Python paths following ngapy patterns
        self.env_info.PYTHONPATH.append(os.path.join(self.package_folder, "openssl_tools"))
        
        # Set environment variables
        self.env_info.OPENSSL_TOOLS_CONFIG = os.path.join(self.package_folder, "tools_config.json")
        self.env_info.OPENSSL_TOOLS_ROOT = self.package_folder
        
        # Add to PATH for command-line tools
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        
    def package_id(self):
        """Optimize package ID for better caching"""
        # Python tools don't depend on compiler or build_type
        # Only keep os and arch for Python tools
        # For Python packages, we only care about os and arch
        # This method is intentionally simple to avoid Conan API issues
        pass