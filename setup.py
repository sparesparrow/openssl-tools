#!/usr/bin/env python3
"""
OpenSSL Tools - Setup Script
Compatibility setup script for older Python environments
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return "OpenSSL development and build tools with Python environment management, Conan integration, and fuzzing support"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(requirements_path):
        with open(requirements_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return []

setup(
    name="openssl-tools",
    version="1.2.6",
    description="OpenSSL development and build tools with Python environment management, Conan integration, and fuzzing support",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="sparesparrow",
    author_email="sparesparrow@example.com",
    url="https://github.com/sparesparrow/openssl-tools",
    project_urls={
        "Homepage": "https://github.com/sparesparrow/openssl-tools",
        "Documentation": "https://openssl-tools.readthedocs.io",
        "Repository": "https://github.com/sparesparrow/openssl-tools.git",
        "Issues": "https://github.com/sparesparrow/openssl-tools/issues",
        "Changelog": "https://github.com/sparesparrow/openssl-tools/blob/main/CHANGELOG.md",
    },
    packages=find_packages(where=".", include=["openssl_tools*"]),
    package_dir={"": "."},
    include_package_data=True,
    package_data={
        "openssl_tools": ["*.py", "*.yml", "*.yaml", "*.json", "*.md"],
    },
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pre-commit>=2.20.0",
            "isort>=5.10.0",
            "pylint>=2.15.0",
            "pytest-xdist>=2.5.0",
            "pytest-mock>=3.8.0",
            "pytest-benchmark>=4.0.0",
            "coverage>=6.5.0",
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
            "myst-parser>=0.18.0",
            "jupyter>=1.0.0",
            "ipykernel>=6.15.0",
            "types-requests>=2.28.0",
            "types-cryptography>=3.4.0",
        ],
        "fuzzing": [
            "atheris>=2.0.0",
            "hypothesis>=6.0.0",
            "fuzzingbook>=1.0.0",
        ],
        "security": [
            "bandit>=1.7.0",
            "safety>=2.0.0",
            "semgrep>=1.0.0",
        ],
        "performance": [
            "pyperf>=2.0.0",
            "psutil>=5.9.0",
            "memory-profiler>=0.60.0",
            "line-profiler>=4.0.0",
            "py-spy>=0.3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "openssl-tools=openssl_tools.foundation.command_line.main:main",
            "openssl-env=openssl_tools.environment.setup:main",
            "openssl-workflow=openssl_tools.automation.workflow_management.manager:main",
            "openssl-build=openssl_tools.development.build_system.optimizer:main",
            "openssl-conan=openssl_tools.development.package_management.remote_manager:main",
            "openssl-validate=openssl_tools.foundation.utilities.validation:main",
            "openssl-security=openssl_tools.security.build_validation:main",
            "openssl-test=openssl_tools.testing.test_harness:main",
            "openssl-monitor=openssl_tools.monitoring.status_reporter:main",
            "openssl-sbom=openssl_tools.security.sbom_generator:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Security :: Cryptography",
        "Topic :: Software Development :: Testing",
    ],
    keywords="openssl cryptography build-tools conan fuzzing python",
    zip_safe=False,
)