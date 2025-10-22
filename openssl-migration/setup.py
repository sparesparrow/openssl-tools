"""
Setup script for OpenSSL Migration Framework.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README file
readme_path = Path(__file__).parent / 'README.md'
long_description = readme_path.read_text(encoding='utf-8') if readme_path.exists() else ''

# Read requirements
requirements_path = Path(__file__).parent / 'requirements.txt'
requirements = []
if requirements_path.exists():
    with open(requirements_path, 'r', encoding='utf-8') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='openssl-migration',
    version='1.0.0',
    description='Framework for migrating OpenSSL utility repositories to modern Python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='OpenSSL Tools Team',
    author_email='openssl-tools@example.com',
    url='https://github.com/sparesparrow/openssl-tools',
    packages=find_packages(),
    python_requires='>=3.8',
    install_requires=[
        'click>=8.0.0',
        'pathlib2>=2.3.0; python_version < "3.4"',
    ],
    extras_require={
        'docker': ['docker>=6.0.0'],
        'conan': ['conan>=2.0.0'],
        'yaml': ['pyyaml>=6.0'],
        'requests': ['requests>=2.28.0'],
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'black>=22.0.0',
            'isort>=5.0.0',
            'flake8>=5.0.0',
            'mypy>=1.0.0',
            'pre-commit>=2.20.0',
        ],
        'docs': [
            'sphinx>=5.0.0',
            'sphinx-rtd-theme>=1.0.0',
            'myst-parser>=0.18.0',
        ],
        'all': [
            'docker>=6.0.0',
            'conan>=2.0.0',
            'pyyaml>=6.0',
            'requests>=2.28.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'openssl-migrate=openssl_migration.cli:cli',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Software Development :: Build Tools',
        'Topic :: System :: Installation/Setup',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='openssl migration python shell perl automation',
    project_urls={
        'Bug Reports': 'https://github.com/sparesparrow/openssl-tools/issues',
        'Source': 'https://github.com/sparesparrow/openssl-tools',
        'Documentation': 'https://openssl-tools.readthedocs.io',
    },
)
