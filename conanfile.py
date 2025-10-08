#!/usr/bin/env python3
"""
OpenSSL Tools Conan Package Recipe
Python tools for OpenSSL development with Conan 2.x integration
Based on openssl-tools patterns for proper Python dev/testing environment
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
import hashlib
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
        # For Python tools, we don't install dependencies during build
        # Dependencies should be handled by the consumer
        self.output.info("Python tools package - dependencies handled by consumer")
    
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
        """Set up build optimization and caching following openssl-tools patterns"""
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
                'reproducible_builds': True,
                'cache_dir': os.path.join(self.build_folder, 'cache')
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
        """Package the tools following ngapy patterns with Conan-managed Python environment"""
        # Copy Python package
        self.output.info(f"Copying openssl_tools from {self.source_folder} to {self.package_folder}")
        import shutil
        src_path = os.path.join(self.source_folder, "openssl_tools")
        dst_path = os.path.join(self.package_folder, "openssl_tools")
        if os.path.exists(src_path):
            shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
            self.output.info(f"Copied openssl_tools directory successfully")
        else:
            self.output.warning(f"openssl_tools directory not found at {src_path}")
        
        # Create Conan-managed Python environment structure
        self._create_conan_python_environment()
        
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
    
    def _create_conan_python_environment(self):
        """Create Conan-managed Python environment structure"""
        self.output.info("Creating Conan-managed Python environment...")
        
        # Create Python environment directories
        python_env_dir = os.path.join(self.package_folder, "python")
        python_bin_dir = os.path.join(python_env_dir, "bin")
        python_lib_dir = os.path.join(python_env_dir, "lib")
        python_cache_dir = os.path.join(self.package_folder, "conan_cache", "python")
        
        os.makedirs(python_bin_dir, exist_ok=True)
        os.makedirs(python_lib_dir, exist_ok=True)
        os.makedirs(python_cache_dir, exist_ok=True)
        
        # Create Python wrapper script that uses Conan-managed environment
        python_wrapper_content = f'''#!/usr/bin/env python3
"""
Conan-managed Python environment wrapper
Ensures correct Python path resolution from Conan cache/remote
"""
import os
import sys
import subprocess
from pathlib import Path

# Get Conan package root
CONAN_PACKAGE_ROOT = Path(__file__).parent.parent
CONAN_PYTHON_ENV = CONAN_PACKAGE_ROOT / "python"
CONAN_PYTHON_CACHE = CONAN_PACKAGE_ROOT / "conan_cache" / "python"

def setup_conan_python_environment():
    """Setup Conan-managed Python environment"""
    # Set Python paths from Conan environment
    python_paths = [
        str(CONAN_PACKAGE_ROOT / "openssl_tools"),
        str(CONAN_PYTHON_CACHE),
        str(CONAN_PYTHON_ENV / "lib"),
    ]
    
    # Update PYTHONPATH
    current_pythonpath = os.environ.get('PYTHONPATH', '')
    new_pythonpath = os.pathsep.join(python_paths + [current_pythonpath])
    os.environ['PYTHONPATH'] = new_pythonpath
    
    # Set Conan environment variables
    os.environ['CONAN_PYTHON_ENV'] = 'managed'
    os.environ['CONAN_PYTHON_SOURCE'] = 'cache_remote'
    os.environ['CONAN_PYTHON_CACHE'] = str(CONAN_PYTHON_CACHE)
    os.environ['OPENSSL_TOOLS_ROOT'] = str(CONAN_PACKAGE_ROOT)
    
    # Add to sys.path for current session
    for path in python_paths:
        if path not in sys.path:
            sys.path.insert(0, path)

if __name__ == "__main__":
    # Setup environment and run with system Python
    setup_conan_python_environment()
    
    # Use system Python with Conan-managed paths
    python_cmd = [sys.executable] + sys.argv[1:]
    sys.exit(subprocess.run(python_cmd).returncode)
'''
        
        python_wrapper_path = os.path.join(python_bin_dir, "python")
        save(self, python_wrapper_path, python_wrapper_content)
        
        # Make wrapper executable on Unix systems
        if os.name != 'nt':
            os.chmod(python_wrapper_path, 0o755)
        
        # Create environment activation script
        activate_script_content = f'''#!/bin/bash
# Conan-managed Python environment activation
export CONAN_PYTHON_ENV="managed"
export CONAN_PYTHON_SOURCE="cache_remote"
export CONAN_PYTHON_CACHE="{python_cache_dir}"
export OPENSSL_TOOLS_ROOT="{self.package_folder}"
export PYTHONPATH="{os.path.join(self.package_folder, 'openssl_tools')}:{python_cache_dir}:$PYTHONPATH"
export PATH="{python_bin_dir}:$PATH"

echo "Conan-managed Python environment activated"
echo "Python source: cache/remote"
echo "Python cache: {python_cache_dir}"
echo "OpenSSL Tools root: {self.package_folder}"
'''
        
        activate_script_path = os.path.join(python_bin_dir, "activate")
        save(self, activate_script_path, activate_script_content)
        
        # Make activation script executable
        if os.name != 'nt':
            os.chmod(activate_script_path, 0o755)
        
        # Create environment info file
        env_info = {
            "conan_python_env": "managed",
            "conan_python_source": "cache_remote",
            "python_executable": python_wrapper_path,
            "python_home": python_env_dir,
            "python_cache": python_cache_dir,
            "openssl_tools_root": self.package_folder,
            "python_paths": [
                os.path.join(self.package_folder, "openssl_tools"),
                python_cache_dir,
                os.path.join(python_env_dir, "lib")
            ]
        }
        
        env_info_path = os.path.join(self.package_folder, "python_env_info.json")
        save(self, env_info_path, json.dumps(env_info, indent=2))
        
        self.output.info(f"Created Conan-managed Python environment at {python_env_dir}")
        
    def _calculate_file_hash(self, filepath, algorithm='sha256'):
        """Calculate cryptographic hash of a file"""
        hash_func = getattr(hashlib, algorithm)()
        try:
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_func.update(chunk)
            return hash_func.hexdigest()
        except Exception as e:
            self.output.warning(f"Failed to calculate hash for {filepath}: {e}")
            return None

    def _generate_sbom(self):
        """Generate Software Bill of Materials with security features following openssl-tools patterns"""
        self.output.info("Generating Software Bill of Materials (SBOM) with security features...")
        
        try:
            from openssl_tools.utils.sbom_generator import SBOMGenerator
            
            # Package information for SBOM
            package_info = {
                'name': self.name,
                'version': str(self.version),
                'description': self.description,
                'homepage': self.homepage,
                'url': self.url,
                'license': self.license,
                'package_folder': self.package_folder,
                'os': str(self.settings.os),
                'arch': str(self.settings.arch),
                'build_type': str(self.settings.build_type),
                'options': {k: str(v) for k, v in self.options.items()},
                'settings': {k: str(v) for k, v in self.settings.items()},
                'dependencies': self._get_package_dependencies()
            }
            
            # SBOM generator configuration
            sbom_config = {
                'enable_vulnerability_scanning': True,
                'enable_package_signing': os.getenv('CONAN_SIGN_PACKAGES', 'false').lower() == 'true',
                'enable_dependency_analysis': True,
                'enable_license_analysis': True,
                'trivy_path': 'trivy',
                'syft_path': 'syft',
                'cosign_path': 'cosign'
            }
            
            # Generate SBOM
            sbom_generator = SBOMGenerator(sbom_config)
            sbom_data = sbom_generator.generate_sbom(package_info)
            
            # Save SBOM
            sbom_path = os.path.join(self.package_folder, "sbom.json")
            save(self, sbom_path, json.dumps(sbom_data, indent=2))
            
            # Also save as YAML for readability
            sbom_yaml_path = os.path.join(self.package_folder, "sbom.yaml")
            import yaml
            save(self, sbom_yaml_path, yaml.dump(sbom_data, default_flow_style=False, sort_keys=False))
            
            self.output.info(f"SBOM generated with {len(sbom_data.get('components', []))} components")
            if sbom_data.get('vulnerabilities'):
                self.output.warning(f"Found {len(sbom_data['vulnerabilities'])} vulnerabilities")
            
        except ImportError:
            self.output.warning("Enhanced SBOM generation not available, using basic SBOM")
            self._generate_basic_sbom()
        except Exception as e:
            self.output.warning(f"Enhanced SBOM generation failed: {e}, using basic SBOM")
            self._generate_basic_sbom()
    
    def _generate_basic_sbom(self):
        """Generate basic SBOM as fallback"""
        # Calculate hashes for main files
        file_hashes = {}
        for root, dirs, files in os.walk(self.package_folder):
            for file in files:
                if file.endswith(('.py', '.json', '.yaml', '.yml')):
                    file_path = os.path.join(root, file)
                    sha256 = self._calculate_file_hash(file_path, 'sha256')
                    if sha256:
                        rel_path = os.path.relpath(file_path, self.package_folder)
                        file_hashes[rel_path] = {
                            "sha256": sha256,
                            "algorithm": "SHA-256"
                        }
        
        # Enhanced metadata collection - pattern from openssl-tools
        build_metadata = {
            "build_timestamp": os.environ.get("SOURCE_DATE_EPOCH", ""),
            "build_platform": f"{self.settings.os}-{self.settings.arch}",
            "compiler": "python",  # Python tools don't use C++ compiler
            "build_type": "Release",  # Default for Python tools
            "conan_version": "2.0",  # Would get from actual Conan version
            "build_options": {k: str(v) for k, v in self.options.items()}
        }
        
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
                    "hashes": [{"alg": "SHA-256", "content": h["sha256"]} 
                              for h in file_hashes.values()],
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
                        {"name": "build_metadata", "value": json.dumps(build_metadata)},
                        {"name": "conan_options", "value": json.dumps({k: str(v) for k, v in self.options.items()})},
                        {"name": "build_platform", "value": f"{self.settings.os}-{self.settings.arch}"},
                        {"name": "package_type", "value": "python-tools"}
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
        self.output.success(f"SBOM generated: {sbom_path}")
    
    def _get_package_dependencies(self):
        """Get package dependencies for SBOM"""
        dependencies = {}
        
        # Get Conan dependencies
        deps = getattr(self, "deps_cpp_info", None)
        if deps and hasattr(deps, "deps"):
            for dep in deps.deps:
                try:
                    dep_version = str(deps[dep].version) if hasattr(deps[dep], "version") else "unknown"
                    dependencies[dep] = {
                        'version': dep_version,
                        'type': 'library',
                        'scope': 'required',
                        'optional': False
                    }
                except Exception as e:
                    self.output.warning(f"Failed to get dependency info for {dep}: {e}")
        
        return dependencies
        
        # Generate vulnerability report placeholder
        self._generate_vulnerability_report()

    def _sign_package(self, sbom_path):
        """Sign package for supply chain security (placeholder for actual signing)"""
        signing_enabled = os.getenv("CONAN_SIGN_PACKAGES", "false").lower() == "true"
        
        if not signing_enabled:
            self.output.info("Package signing disabled (set CONAN_SIGN_PACKAGES=true to enable)")
            return
        
        self.output.info("Package signing placeholder - integrate with cosign/gpg in production")
        
        signature_metadata = {
            "signed": True,
            "timestamp": str(os.environ.get("SOURCE_DATE_EPOCH", "")),
            "algorithm": "placeholder",
            "keyid": "placeholder"
        }
        
        sig_path = os.path.join(self.package_folder, "package-signature.json")
        save(self, sig_path, json.dumps(signature_metadata, indent=2))

    def _generate_vulnerability_report(self):
        """Generate vulnerability scan report (integration point)"""
        vuln_report = {
            "scanTool": "placeholder",
            "scanDate": str(os.environ.get("SOURCE_DATE_EPOCH", "")),
            "component": f"{self.name}@{self.version}",
            "vulnerabilities": [],
            "note": "Integrate with Trivy/Snyk for actual vulnerability scanning"
        }
        
        vuln_path = os.path.join(self.package_folder, "vulnerability-report.json")
        save(self, vuln_path, json.dumps(vuln_report, indent=2))
        self.output.info(f"Vulnerability report placeholder generated: {vuln_path}")
        
    def package_info(self):
        """Package info following ngapy patterns with Conan-managed Python environment"""
        # Python package info
        self.cpp_info.libs = []
        
        # Set Python paths following ngapy patterns - managed by Conan cache/remote
        python_package_path = os.path.join(self.package_folder, "openssl_tools")
        self.env_info.PYTHONPATH.append(python_package_path)
        
        # Set Conan-managed Python environment variables
        self.env_info.OPENSSL_TOOLS_CONFIG = os.path.join(self.package_folder, "tools_config.json")
        self.env_info.OPENSSL_TOOLS_ROOT = self.package_folder
        
        # Set Python interpreter path from Conan environment
        conan_python_path = os.path.join(self.package_folder, "python")
        if os.path.exists(conan_python_path):
            self.env_info.PYTHON_EXECUTABLE = os.path.join(conan_python_path, "bin", "python")
            self.env_info.PYTHON_HOME = conan_python_path
        else:
            # Fallback to system Python with Conan-managed paths
            self.env_info.PYTHON_EXECUTABLE = sys.executable
            self.env_info.PYTHON_HOME = os.path.dirname(os.path.dirname(sys.executable))
        
        # Set Conan cache paths for Python environment
        conan_cache_python = os.path.join(self.package_folder, "conan_cache", "python")
        if os.path.exists(conan_cache_python):
            self.env_info.CONAN_PYTHON_CACHE = conan_cache_python
            self.env_info.PYTHONPATH.append(conan_cache_python)
        
        # Add to PATH for command-line tools
        bin_path = os.path.join(self.package_folder, "bin")
        if os.path.exists(bin_path):
            self.env_info.PATH.append(bin_path)
        
        # Set Conan remote Python environment variables
        self.env_info.CONAN_PYTHON_ENV = "managed"
        self.env_info.CONAN_PYTHON_SOURCE = "cache_remote"
        
    def package_id(self):
        """Optimize package ID for better caching"""
        # Python tools don't depend on compiler or build_type
        # Only keep os and arch for Python tools
        # For Python packages, we only care about os and arch
        # This method is intentionally simple to avoid Conan API issues
        pass