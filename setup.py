#!/usr/bin/env python3
"""
Setup script for OpenSSL Tools
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "OpenSSL Tools - Python tools for OpenSSL development"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="openssl-tools",
    version="1.0.0",
    author="OpenSSL Tools Team",
    author_email="openssl-tools@openssl.org",
    description="Python tools for OpenSSL development, review, and release management",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/sparesparrow/openssl-tools",
    project_urls={
        "Bug Tracker": "https://github.com/sparesparrow/openssl-tools/issues",
        "Documentation": "https://github.com/sparesparrow/openssl-tools/blob/main/README.md",
        "Source Code": "https://github.com/sparesparrow/openssl-tools",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Security :: Cryptography",
        "Topic :: Software Development :: Version Control :: Git",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
        "statistics": [
            "numpy>=1.20.0",
            "scipy>=1.7.0",
        ],
        "github": [
            "pygithub>=1.59.0",
        ],
        "gitlab": [
            "python-gitlab>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "addrev=openssl_tools.review_tools.addrev:main",
            "gitaddrev=openssl_tools.review_tools.gitaddrev:main",
            "ghmerge=openssl_tools.review_tools.ghmerge:main",
            "gitlabutil=openssl_tools.review_tools.gitlabutil:main",
            "cherry-checker=openssl_tools.review_tools.cherry_checker:main",
            "stage-release=openssl_tools.release_tools.stage_release:main",
            "copyright-year=openssl_tools.release_tools.copyright_year:main",
            "bn-rand-range=openssl_tools.statistics.bn_rand_range:main",
        ],
    },
    include_package_data=True,
    package_data={
        "openssl_tools": [
            "templates/*",
            "*.json",
        ],
    },
    zip_safe=False,
)