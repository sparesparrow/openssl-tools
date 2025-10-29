"""
OpenSSL Build Orchestrator - Advanced build management for OpenSSL
Based on reference project patterns with enhanced error handling and monitoring
"""

import os
import subprocess
from typing import Dict, List, Optional, Any
from pathlib import Path
from .version_manager import get_openssl_version

class OpenSSLBuildOrchestrator:
    """Advanced OpenSSL build orchestrator with multi-platform support"""

    def __init__(self, conanfile):
        self.conanfile = conanfile
        self.source_folder = conanfile.source_folder
        self.package_folder = conanfile.package_folder

    def configure_and_build(self):
        """Orchestrate OpenSSL build process"""
        self._setup_environment()
        self._configure_openssl()
        self._build_openssl()

    def _setup_environment(self):
        """Setup build environment variables"""
        # Set up environment similar to reference project patterns
        self.conanfile.output.info("Setting up OpenSSL build environment")

    def _configure_openssl(self):
        """Configure OpenSSL build"""
        with os.chdir(self.source_folder):
            # Platform-specific Configure target
            target_map = {
                ("Linux", "x86_64"): "linux-x86_64",
                ("Linux", "x86"): "linux-x86",
                ("Windows", "x86_64"): "VC-WIN64A",
                ("Windows", "x86"): "VC-WIN32",
                ("Macos", "armv8"): "darwin64-arm64-cc",
                ("Macos", "x86_64"): "darwin64-x86_64-cc",
            }
            target = target_map.get(
                (str(self.conanfile.settings.os), str(self.conanfile.settings.arch)),
                "linux-x86_64"
            )

            # Build Configure command
            # CRITICAL FIX: Use final runtime prefix, NOT package_folder
            # This prevents hardcoding build paths into OpenSSL binaries
            runtime_prefix = "/"  # Root prefix for relocatable packages
            if self.conanfile.settings.os == "Windows":
                runtime_prefix = "C:/Program Files/OpenSSL"
            
            configure_args = [
                "./Configure",
                target,
                f"--prefix={runtime_prefix}",
                f"--openssldir={runtime_prefix}/ssl",
            ]

            # Add options based on conanfile settings
            if hasattr(self.conanfile.options, 'fips') and self.conanfile.options.fips:
                configure_args.append("enable-fips")

            if hasattr(self.conanfile.options, 'shared') and not self.conanfile.options.shared:
                configure_args.append("no-shared")

            if hasattr(self.conanfile.options, 'no_threads') and self.conanfile.options.no_threads:
                configure_args.append("no-threads")

            if hasattr(self.conanfile.options, 'no_asm') and self.conanfile.options.no_asm:
                configure_args.append("no-asm")

            # Set environment variables for Configure
            env_vars = {
                "PERL": "perl",  # Use system Perl
                "OPENSSL_CONF_INCLUDE": os.path.join(self.source_folder, 'Configurations'),
            }

            # Run Configure
            self.conanfile.output.info(f"Running Configure with target: {target}")
            self.conanfile.run(configure_args, env=env_vars)

    def _build_openssl(self):
        """Build OpenSSL"""
        with os.chdir(self.source_folder):
            # Build with make (official OpenSSL backend)
            cpu_count = self._get_optimal_cpu_count()

            self.conanfile.output.info(f"Building OpenSSL with {cpu_count} parallel jobs")
            self.conanfile.run(f"make -j{cpu_count}")

    def install_and_package(self):
        """Install OpenSSL and handle post-install packaging"""
        self.install_openssl()
        # Additional packaging steps can be added here if needed

    def install_openssl(self):
        """Install OpenSSL using DESTDIR staging"""
        with os.chdir(self.source_folder):
            self.conanfile.output.info("Installing OpenSSL using DESTDIR staging")
            # CRITICAL FIX: Use DESTDIR for staging, not direct install
            # This preserves the runtime prefix paths in OpenSSL binaries
            self.conanfile.run(f"make install_sw DESTDIR={self.package_folder}")

    def _get_optimal_cpu_count(self):
        """Get optimal CPU count for build parallelism"""
        import multiprocessing
        import os

        total_cpus = multiprocessing.cpu_count() or 1

        # In CI environments, use all available cores
        if os.getenv('CI') or os.getenv('GITHUB_ACTIONS'):
            return total_cpus

        # Locally, reserve some cores for system responsiveness
        # Use at least 1 core, at most total_cpus - 1 (or total_cpus if only 1 core)
        reserved = 1 if total_cpus > 2 else 0
        return max(1, total_cpus - reserved)
