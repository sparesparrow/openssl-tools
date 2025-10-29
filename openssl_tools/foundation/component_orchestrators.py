"""
OpenSSL Component Build Orchestrators - Specialized build management for libcrypto and libssl

Provides component-specific build orchestration for the modular OpenSSL architecture.
"""

import os
import subprocess
from typing import Dict, List, Optional, Any
from pathlib import Path
from .build_orchestrator import OpenSSLBuildOrchestrator


class CryptoBuildOrchestrator:
    """Build orchestrator specifically for libcrypto component"""

    def __init__(self, conanfile):
        self.conanfile = conanfile
        self.source_folder = conanfile.source_folder
        self.package_folder = conanfile.package_folder
        # Use the main orchestrator for common functionality
        self.main_orchestrator = OpenSSLBuildOrchestrator(conanfile)

    def build_crypto_library(self):
        """Build the libcrypto library specifically"""
        self.conanfile.output.info("Building libcrypto component...")

        # Change to crypto subdirectory
        crypto_dir = Path(self.source_folder) / "crypto"
        if not crypto_dir.exists():
            raise RuntimeError(f"crypto directory not found: {crypto_dir}")

        with os.chdir(crypto_dir):
            # Build crypto-specific objects
            self._build_crypto_objects()

            # Create libcrypto archive
            self._create_crypto_library()

    def _build_crypto_objects(self):
        """Build crypto object files"""
        # Get optimal CPU count
        cpu_count = self.main_orchestrator._get_optimal_cpu_count()

        # Build crypto objects using make
        self.conanfile.output.info(f"Building crypto objects with {cpu_count} parallel jobs")
        self.conanfile.run(f"make -j{cpu_count} build_crypto")

    def _create_crypto_library(self):
        """Create libcrypto static/shared library"""
        if self.conanfile.options.shared:
            # Create shared library
            self.conanfile.run("make libcrypto.so")
        else:
            # Create static library
            self.conanfile.run("make libcrypto.a")

    def package_crypto_library(self):
        """Package the built libcrypto artifacts"""
        self.conanfile.output.info("Packaging libcrypto artifacts...")

        # Copy library files
        lib_dir = Path(self.package_folder) / "lib"
        lib_dir.mkdir(parents=True, exist_ok=True)

        crypto_dir = Path(self.source_folder) / "crypto"
        if self.conanfile.options.shared:
            # Copy shared library
            self._copy_file(crypto_dir / "libcrypto.so", lib_dir / "libcrypto.so")
        else:
            # Copy static library
            self._copy_file(crypto_dir / "libcrypto.a", lib_dir / "libcrypto.a")

        # Copy headers
        include_dir = Path(self.package_folder) / "include"
        include_dir.mkdir(parents=True, exist_ok=True)

        # Copy crypto headers
        crypto_include = Path(self.source_folder) / "include" / "openssl"
        if crypto_include.exists():
            for header in crypto_include.glob("*.h"):
                self._copy_file(header, include_dir / "openssl" / header.name)

    def _copy_file(self, src: Path, dst: Path):
        """Copy a file with error handling"""
        try:
            if src.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)
                import shutil
                shutil.copy2(src, dst)
                self.conanfile.output.info(f"Copied {src} -> {dst}")
            else:
                self.conanfile.output.warning(f"Source file not found: {src}")
        except Exception as e:
            self.conanfile.output.warning(f"Failed to copy {src} -> {dst}: {e}")


class SSLBuildOrchestrator:
    """Build orchestrator specifically for libssl component"""

    def __init__(self, conanfile):
        self.conanfile = conanfile
        self.source_folder = conanfile.source_folder
        self.package_folder = conanfile.package_folder
        # Use the main orchestrator for common functionality
        self.main_orchestrator = OpenSSLBuildOrchestrator(conanfile)

    def build_ssl_library(self):
        """Build the libssl library specifically"""
        self.conanfile.output.info("Building libssl component...")

        # Change to ssl subdirectory
        ssl_dir = Path(self.source_folder) / "ssl"
        if not ssl_dir.exists():
            raise RuntimeError(f"ssl directory not found: {ssl_dir}")

        with os.chdir(ssl_dir):
            # Build ssl-specific objects
            self._build_ssl_objects()

            # Create libssl archive
            self._create_ssl_library()

    def _build_ssl_objects(self):
        """Build ssl object files"""
        # Get optimal CPU count
        cpu_count = self.main_orchestrator._get_optimal_cpu_count()

        # Build ssl objects using make
        self.conanfile.output.info(f"Building ssl objects with {cpu_count} parallel jobs")
        self.conanfile.run(f"make -j{cpu_count} build_ssl")

    def _create_ssl_library(self):
        """Create libssl static/shared library"""
        if self.conanfile.options.shared:
            # Create shared library
            self.conanfile.run("make libssl.so")
        else:
            # Create static library
            self.conanfile.run("make libssl.a")

    def package_ssl_library(self):
        """Package the built libssl artifacts"""
        self.conanfile.output.info("Packaging libssl artifacts...")

        # Copy library files
        lib_dir = Path(self.package_folder) / "lib"
        lib_dir.mkdir(parents=True, exist_ok=True)

        ssl_dir = Path(self.source_folder) / "ssl"
        if self.conanfile.options.shared:
            # Copy shared library
            self._copy_file(ssl_dir / "libssl.so", lib_dir / "libssl.so")
        else:
            # Copy static library
            self._copy_file(ssl_dir / "libssl.a", lib_dir / "libssl.a")

        # Copy headers (libssl typically uses crypto headers)
        include_dir = Path(self.package_folder) / "include"
        include_dir.mkdir(parents=True, exist_ok=True)

        # Copy ssl-specific headers if any
        ssl_include = Path(self.source_folder) / "include" / "openssl"
        if ssl_include.exists():
            for header in ssl_include.glob("ssl*.h"):
                self._copy_file(header, include_dir / "openssl" / header.name)

    def _copy_file(self, src: Path, dst: Path):
        """Copy a file with error handling"""
        try:
            if src.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)
                import shutil
                shutil.copy2(src, dst)
                self.conanfile.output.info(f"Copied {src} -> {dst}")
            else:
                self.conanfile.output.warning(f"Source file not found: {src}")
        except Exception as e:
            self.conanfile.output.warning(f"Failed to copy {src} -> {dst}: {e}")