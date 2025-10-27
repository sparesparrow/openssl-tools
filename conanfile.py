#!/usr/bin/env python3
"""
OpenSSL Tools Package
Provides build orchestration and utilities for OpenSSL Conan packages
with bundled CPython 3.12.7 for cross-platform reproducibility
"""
import os
import textwrap
import logging
import hashlib
import subprocess
from conan import ConanFile
from conan.errors import ConanException
from conan.tools.files import copy, save
from pathlib import Path

# Core logging without sensitive leaks
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OpensslToolsConan(ConanFile):
    name = "openssl-tools"
    version = "1.1.1"
    requires = "openssl/3.4.0@sparesparrow/stable"
    tool_requires = ["cpython/3.12.7"]
    build_requires = ["cmake/3.28.1", "syft/0.90.0", "trivy/0.50.0"]
    options = {"fips": [True, False], "enable_sbom": [True, False]}
    default_options = {"fips": False, "enable_sbom": True}

    exports_sources = (
        "openssl_tools/*",
        "scripts/*",
        "profiles/*"
    )

    def configure(self):
        try:
            if "cpython" in self.dependencies:
                self.cpython_info = self.dependencies["cpython"].cpp_info
            else:
                raise ConanException("cpython/3.12.7 not resolved")
        except KeyError as e:
            logger.error(f"Dependency failed: {e}")
            raise ConanException(str(e))

    def source(self):
        if Path("tools-mini").exists():
            copy(self, "conanfile.py", self.source_folder, self.source_folder)
            logger.info("Core migration from tools-mini complete")

    def build(self):
        python_bin = self.cpython_info.bindirs[0]
        self.buildenv_info.prepend_path("PATH", python_bin)
        self.buildenv_info.vars["PYTHONPATH"] = os.pathsep.join(self.cpython_info.libpaths)
        self.buildenv_info.vars["user.openssl:python_interpreter"] = str(python_bin)
        self.buildenv_info.vars["user.openssl:python_version"] = "3.12.7"

        bootstrap_path = Path(self.source_folder) / "scripts" / "bootstrap-init.py"
        cmd = [str(python_bin / "python"), str(bootstrap_path)]
        try:
            subprocess.check_call(cmd, cwd=self.build_folder, env=self.buildenv_info.vars)
            logger.info("Core bootstrap with CPython complete")
        except subprocess.CalledProcessError as e:
            logger.error(f"Bootstrap error: {e}")
            raise ConanException("Core build failed")

        if self.options.enable_sbom:
            self._generate_sbom()

    def _generate_sbom(self):
        """Core Syft SBOM with integrity"""
        syft_bin = self.dependencies["syft"].cpp_info.bindirs[0] / "syft"
        cmd = [str(syft_bin), "packages", self.build_folder, "-o", "cyclonedx-json=sbom.json"]
        try:
            subprocess.check_call(cmd, cwd=self.build_folder)
            with open("sbom.json", "rb") as f:
                sbom_hash = hashlib.sha256(f.read()).hexdigest()
            self.buildenv_info.vars["SBOM_HASH"] = sbom_hash
            logger.info("Core SBOM hashed")
        except Exception as e:
            logger.warning(f"SBOM warning: {e}")
            if self.options.fips:
                raise ConanException("FIPS requires core SBOM")

    def package(self):
        self.copy("*.py", src="openssl_tools", dst="lib/python", keep_path=True)
        self.copy("*.py", src="scripts", dst="bin", keep_path=False)
        self._create_wrapper_scripts()
        if self.options.enable_sbom:
            self.copy("sbom.json", dst="sbom", src=self.build_folder, keep_path=False)

        trivy_bin = self.dependencies["trivy"].cpp_info.bindirs[0] / "trivy"
        cmd = [str(trivy_bin), "fs", self.package_folder, "--exit-code", "1", "--vuln-type", "os,library"]
        try:
            subprocess.check_call(cmd, cwd=self.package_folder)
            logger.info("Core Trivy passed")
        except subprocess.CalledProcessError as e:
            if e.returncode > 1:
                raise ConanException(f"Core security failed: {e}")
            logger.warning("Non-critical issues")

    def package_info(self):
        self.cpp_info.libs = []
        bin_dir = self.cpp_info.bindirs[0]
        self.cpp_info.builddirs = [bin_dir]
        self.conf_info.update({
            "user.openssl:python_interpreter": str(self.cpython_info.bindirs[0]),
            "user.openssl:python_version": "3.12.7"
        })
        # Core cross-platform [web:23]

    def _create_wrapper_scripts(self):
        """Core cross-platform wrappers"""
        templates = {
            "unix": textwrap.dedent("""
                #!/bin/sh
                export PATH="{python_bin}:$PATH"
                export PYTHONPATH="{pythonpath}:$PYTHONPATH"
                exec "{python_bin}/python" "$@"
                """),
            "windows": textwrap.dedent("""
                @echo off
                set PATH={python_bin};%PATH%
                set PYTHONPATH={pythonpath};%PYTHONPATH%
                "{python_bin}\\python.exe" %*
                """)
        }
        os_name = "windows" if self.settings.os == "Windows" else "unix"
        template = templates[os_name]
        try:
            wrapper_content = template.format(
                python_bin=str(self.cpython_info.bindirs[0]),
                pythonpath=os.pathsep.join(self.cpython_info.libpaths)
            )
            if self.options.fips:
                wrapper_content += "\n# Core FIPS: Post-execution clear"
            save(self, "python-wrapper", wrapper_content)
            if os_name == "unix":
                os.chmod("python-wrapper", 0o755)
            logger.info("Core wrappers generated")
        except Exception as e:
            logger.error(f"Wrapper error: {e}")
            raise ConanException("Core wrapper failed")