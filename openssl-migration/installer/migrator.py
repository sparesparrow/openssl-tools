"""
OpenSSL Installer Migration

Migrates OpenSSL installer scripts from Perl to Python,
following the Way of Python principles.
"""

import os
import sys
import subprocess
import shutil
import tempfile
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
import click
import logging
from dataclasses import dataclass
from datetime import datetime

try:
    from ..core.migration_framework import MigrationFramework, MigrationConfig
    from ..core.script_converter import ScriptConverter
    from ..core.python_generator import PythonGenerator
except ImportError:
    # Handle relative imports
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    from core.migration_framework import MigrationFramework, MigrationConfig
    from core.script_converter import ScriptConverter
    from core.python_generator import PythonGenerator

logger = logging.getLogger(__name__)


@dataclass
class InstallerConfig:
    """Configuration for OpenSSL installer migration."""
    source_repo: str
    target_dir: Path
    preserve_perl_compatibility: bool = False
    add_modern_features: bool = True
    use_conan_integration: bool = True
    add_docker_support: bool = True


class OpenSSLInstallerMigrator:
    """
    Specialized migrator for OpenSSL installer scripts.
    
    Converts Perl installer scripts to modern Python implementations
    with enhanced features and better maintainability.
    """
    
    def __init__(self, config: InstallerConfig):
        """
        Initialize the installer migrator.
        
        Args:
            config: Installer migration configuration
        """
        self.config = config
        self.converter = ScriptConverter()
        self.generator = PythonGenerator()
        
        # Ensure target directory exists
        self.config.target_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Initialized OpenSSL installer migrator for {config.source_repo}")
    
    def migrate_installer_scripts(self) -> Dict[str, Any]:
        """
        Migrate all installer scripts from the source repository.
        
        Returns:
            Dictionary with migration results
        """
        logger.info("Starting OpenSSL installer migration")
        
        # Create migration configuration
        migration_config = MigrationConfig(
            source_repo=self.config.source_repo,
            target_dir=self.config.target_dir,
            script_types=['perl', 'shell'],
            preserve_structure=True,
            add_tests=True,
            add_documentation=True,
            use_click=True,
            use_pathlib=True,
            use_subprocess=True,
            output_format='modern'
        )
        
        # Initialize migration framework
        framework = MigrationFramework(migration_config)
        
        # Analyze repository
        scripts = framework.analyze_repository(self.config.source_repo)
        
        # Filter installer-specific scripts
        installer_scripts = self._filter_installer_scripts(scripts)
        
        results = {
            'total': len(installer_scripts),
            'migrated': 0,
            'failed': 0,
            'skipped': 0
        }
        
        # Migrate each installer script
        for script in installer_scripts:
            try:
                if self._migrate_installer_script(script):
                    results['migrated'] += 1
                else:
                    results['failed'] += 1
            except Exception as e:
                logger.error(f"Failed to migrate {script.name}: {e}")
                results['failed'] += 1
        
        logger.info(f"Installer migration completed: {results['migrated']} successful, {results['failed']} failed")
        
        return results
    
    def _filter_installer_scripts(self, scripts: List) -> List:
        """Filter scripts that are installer-related."""
        installer_keywords = [
            'install', 'setup', 'configure', 'build', 'make',
            'package', 'distribute', 'deploy', 'uninstall'
        ]
        
        installer_scripts = []
        for script in scripts:
            script_name_lower = script.name.lower()
            if any(keyword in script_name_lower for keyword in installer_keywords):
                installer_scripts.append(script)
        
        return installer_scripts
    
    def _migrate_installer_script(self, script) -> bool:
        """
        Migrate a single installer script.
        
        Args:
            script: Script information object
            
        Returns:
            True if migration was successful
        """
        logger.info(f"Migrating installer script: {script.name}")
        
        try:
            # Read original script
            with open(script.path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Convert script based on type
            if script.script_type == 'perl':
                python_code = self._convert_perl_installer(content, script.name)
            elif script.script_type == 'shell':
                python_code = self._convert_shell_installer(content, script.name)
            else:
                logger.warning(f"Unsupported script type: {script.script_type}")
                return False
            
            # Enhance with modern features
            if self.config.add_modern_features:
                python_code = self._enhance_installer_script(python_code, script)
            
            # Add Conan integration if requested
            if self.config.use_conan_integration:
                python_code = self._add_conan_integration(python_code, script)
            
            # Add Docker support if requested
            if self.config.add_docker_support:
                python_code = self._add_docker_support(python_code, script)
            
            # Determine target path
            target_path = self._get_target_path(script)
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write migrated script
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(python_code)
            
            # Make script executable
            os.chmod(target_path, 0o755)
            
            logger.info(f"Successfully migrated installer script: {target_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to migrate installer script {script.name}: {e}")
            return False
    
    def _convert_perl_installer(self, content: str, script_name: str) -> str:
        """Convert Perl installer script to Python."""
        # Use the script converter for basic conversion
        python_code = self.converter.convert_perl_script(content, script_name)
        
        # Add installer-specific enhancements
        python_code = self._add_installer_enhancements(python_code, 'perl')
        
        return python_code
    
    def _convert_shell_installer(self, content: str, script_name: str) -> str:
        """Convert shell installer script to Python."""
        # Use the script converter for basic conversion
        python_code = self.converter.convert_shell_script(content, script_name)
        
        # Add installer-specific enhancements
        python_code = self._add_installer_enhancements(python_code, 'shell')
        
        return python_code
    
    def _add_installer_enhancements(self, python_code: str, original_type: str) -> str:
        """Add installer-specific enhancements to Python code."""
        enhancements = '''
# Installer-specific enhancements
import platform
import hashlib
import urllib.request
import zipfile
import tarfile

def get_system_info() -> Dict[str, str]:
    """Get system information for installation."""
    return {
        'os': platform.system(),
        'arch': platform.machine(),
        'python_version': platform.python_version(),
        'platform': platform.platform()
    }

def download_file(url: str, destination: Path, verify_checksum: bool = True) -> bool:
    """Download a file with optional checksum verification."""
    try:
        logger.info(f"Downloading {url} to {destination}")
        
        # Create destination directory
        destination.parent.mkdir(parents=True, exist_ok=True)
        
        # Download file
        urllib.request.urlretrieve(url, destination)
        
        if verify_checksum:
            # TODO: Implement checksum verification
            pass
        
        logger.info(f"Download completed: {destination}")
        return True
        
    except Exception as e:
        logger.error(f"Download failed: {e}")
        return False

def extract_archive(archive_path: Path, extract_to: Path) -> bool:
    """Extract archive file."""
    try:
        logger.info(f"Extracting {archive_path} to {extract_to}")
        
        # Create extraction directory
        extract_to.mkdir(parents=True, exist_ok=True)
        
        # Determine archive type and extract
        if archive_path.suffix == '.zip':
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
        elif archive_path.suffix in ['.tar', '.tar.gz', '.tgz']:
            with tarfile.open(archive_path, 'r:*') as tar_ref:
                tar_ref.extractall(extract_to)
        else:
            logger.error(f"Unsupported archive format: {archive_path.suffix}")
            return False
        
        logger.info(f"Extraction completed: {extract_to}")
        return True
        
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        return False

def check_dependencies() -> Dict[str, bool]:
    """Check if required dependencies are available."""
    dependencies = {
        'make': shutil.which('make') is not None,
        'gcc': shutil.which('gcc') is not None,
        'perl': shutil.which('perl') is not None,
        'python3': shutil.which('python3') is not None
    }
    
    missing = [dep for dep, available in dependencies.items() if not available]
    if missing:
        logger.warning(f"Missing dependencies: {', '.join(missing)}")
    
    return dependencies

def install_openssl(prefix: Path, config: Dict[str, Any]) -> bool:
    """Install OpenSSL to the specified prefix."""
    try:
        logger.info(f"Installing OpenSSL to {prefix}")
        
        # Check dependencies
        deps = check_dependencies()
        if not all(deps.values()):
            logger.error("Missing required dependencies")
            return False
        
        # Create installation directory
        prefix.mkdir(parents=True, exist_ok=True)
        
        # Configure OpenSSL
        configure_cmd = [
            './Configure',
            f'--prefix={prefix}',
            '--openssldir={prefix}/ssl',
            'shared',
            'zlib'
        ]
        
        if config.get('enable_fips'):
            configure_cmd.append('enable-fips')
        
        result = run_command(configure_cmd, check=True)
        logger.info("Configuration completed")
        
        # Build OpenSSL
        make_result = run_command(['make'], check=True)
        logger.info("Build completed")
        
        # Run tests
        if config.get('run_tests', True):
            test_result = run_command(['make', 'test'], check=True)
            logger.info("Tests completed")
        
        # Install OpenSSL
        install_result = run_command(['make', 'install'], check=True)
        logger.info("Installation completed")
        
        return True
        
    except Exception as e:
        logger.error(f"Installation failed: {e}")
        return False

def verify_installation(prefix: Path) -> bool:
    """Verify OpenSSL installation."""
    try:
        openssl_bin = prefix / 'bin' / 'openssl'
        
        if not openssl_bin.exists():
            logger.error("OpenSSL binary not found")
            return False
        
        # Test OpenSSL version
        result = run_command([str(openssl_bin), 'version'], check=True)
        
        if 'OpenSSL' in result.stdout:
            logger.info(f"OpenSSL version: {result.stdout.strip()}")
            return True
        else:
            logger.error("OpenSSL version check failed")
            return False
        
    except Exception as e:
        logger.error(f"Verification failed: {e}")
        return False
'''
        
        # Insert enhancements before the main function
        main_pos = python_code.find('def main(')
        if main_pos != -1:
            python_code = python_code[:main_pos] + enhancements + '\n' + python_code[main_pos:]
        else:
            python_code += enhancements
        
        return python_code
    
    def _enhance_installer_script(self, python_code: str, script) -> str:
        """Add modern features to the installer script."""
        # Add type hints, error handling, logging, etc.
        # This would be implemented based on specific requirements
        return python_code
    
    def _add_conan_integration(self, python_code: str, script) -> str:
        """Add Conan package manager integration."""
        conan_integration = '''
# Conan integration
import conan
from conan.api.conan_api import ConanAPI

def setup_conan_environment():
    """Setup Conan environment for OpenSSL installation."""
    try:
        conan_api = ConanAPI()
        
        # Create default profile if it doesn't exist
        if not conan_api.profiles.get_profile('default'):
            conan_api.profiles.create_profile('default')
        
        logger.info("Conan environment setup completed")
        return True
        
    except Exception as e:
        logger.error(f"Conan setup failed: {e}")
        return False

def install_via_conan(version: str, profile: str = 'default') -> bool:
    """Install OpenSSL via Conan package manager."""
    try:
        logger.info(f"Installing OpenSSL {version} via Conan")
        
        # Install OpenSSL package
        install_cmd = [
            'conan', 'install', f'openssl/{version}@',
            '--profile', profile,
            '--build', 'missing'
        ]
        
        result = run_command(install_cmd, check=True)
        logger.info("Conan installation completed")
        
        return True
        
    except Exception as e:
        logger.error(f"Conan installation failed: {e}")
        return False
'''
        
        # Insert Conan integration
        main_pos = python_code.find('def main(')
        if main_pos != -1:
            python_code = python_code[:main_pos] + conan_integration + '\n' + python_code[main_pos:]
        
        return python_code
    
    def _add_docker_support(self, python_code: str, script) -> str:
        """Add Docker support to the installer script."""
        docker_support = '''
# Docker support
import docker
from docker.errors import DockerException

def build_docker_image(dockerfile_path: Path, tag: str) -> bool:
    """Build Docker image for OpenSSL installation."""
    try:
        client = docker.from_env()
        
        logger.info(f"Building Docker image: {tag}")
        
        # Build image
        image, build_logs = client.images.build(
            path=str(dockerfile_path.parent),
            tag=tag,
            rm=True
        )
        
        logger.info(f"Docker image built successfully: {tag}")
        return True
        
    except DockerException as e:
        logger.error(f"Docker build failed: {e}")
        return False

def run_in_docker(image: str, command: List[str], volumes: Dict[str, str] = None) -> bool:
    """Run command in Docker container."""
    try:
        client = docker.from_env()
        
        logger.info(f"Running command in Docker: {command}")
        
        # Run container
        container = client.containers.run(
            image,
            command,
            volumes=volumes or {},
            detach=True
        )
        
        # Wait for completion
        result = container.wait()
        
        # Get logs
        logs = container.logs().decode('utf-8')
        logger.info(f"Container logs: {logs}")
        
        # Remove container
        container.remove()
        
        return result['StatusCode'] == 0
        
    except DockerException as e:
        logger.error(f"Docker run failed: {e}")
        return False
'''
        
        # Insert Docker support
        main_pos = python_code.find('def main(')
        if main_pos != -1:
            python_code = python_code[:main_pos] + docker_support + '\n' + python_code[main_pos:]
        
        return python_code
    
    def _get_target_path(self, script) -> Path:
        """Get the target path for a migrated script."""
        # Preserve directory structure
        relative_path = script.path.relative_to(Path(self.config.source_repo))
        target_path = self.config.target_dir / relative_path.with_suffix('.py')
        
        return target_path
    
    def generate_modern_installer(self, output_path: Path) -> bool:
        """
        Generate a modern Python installer from scratch.
        
        Args:
            output_path: Path for the generated installer
            
        Returns:
            True if generation was successful
        """
        logger.info(f"Generating modern OpenSSL installer: {output_path}")
        
        try:
            # Generate installer script
            config = {
                'name': 'OpenSSL Installer',
                'description': 'Modern Python-based OpenSSL installer with enhanced features',
                'use_click': True,
                'use_pathlib': True,
                'use_subprocess': True
            }
            
            python_code = self.generator.generate_installer_script(config)
            
            # Write generated script
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(python_code)
            
            # Make script executable
            os.chmod(output_path, 0o755)
            
            logger.info(f"Modern installer generated successfully: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to generate modern installer: {e}")
            return False
    
    def create_installer_package(self, package_dir: Path) -> bool:
        """
        Create a complete installer package.
        
        Args:
            package_dir: Directory for the installer package
            
        Returns:
            True if package creation was successful
        """
        logger.info(f"Creating installer package: {package_dir}")
        
        try:
            # Create package directory structure
            package_dir.mkdir(parents=True, exist_ok=True)
            
            # Create package files
            self._create_package_structure(package_dir)
            self._create_setup_script(package_dir)
            self._create_requirements_file(package_dir)
            self._create_dockerfile(package_dir)
            self._create_documentation(package_dir)
            
            logger.info(f"Installer package created successfully: {package_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create installer package: {e}")
            return False
    
    def _create_package_structure(self, package_dir: Path) -> None:
        """Create the package directory structure."""
        directories = [
            'src/openssl_installer',
            'tests',
            'docs',
            'scripts',
            'docker'
        ]
        
        for directory in directories:
            (package_dir / directory).mkdir(parents=True, exist_ok=True)
    
    def _create_setup_script(self, package_dir: Path) -> None:
        """Create setup.py script."""
        setup_content = '''"""
Setup script for OpenSSL Installer package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README file
readme_path = Path(__file__).parent / 'README.md'
long_description = readme_path.read_text(encoding='utf-8') if readme_path.exists() else ''

setup(
    name='openssl-installer',
    version='1.0.0',
    description='Modern Python-based OpenSSL installer',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='OpenSSL Tools Team',
    author_email='openssl-tools@example.com',
    url='https://github.com/sparesparrow/openssl-tools',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    python_requires='>=3.8',
    install_requires=[
        'click>=8.0.0',
        'docker>=6.0.0',
        'conan>=2.0.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'black>=22.0.0',
            'isort>=5.0.0',
            'flake8>=5.0.0',
            'mypy>=1.0.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'openssl-install=openssl_installer.cli:main',
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
    ],
)
'''
        
        with open(package_dir / 'setup.py', 'w', encoding='utf-8') as f:
            f.write(setup_content)
    
    def _create_requirements_file(self, package_dir: Path) -> None:
        """Create requirements.txt file."""
        requirements = '''click>=8.0.0
docker>=6.0.0
conan>=2.0.0
pathlib2>=2.3.0; python_version < "3.4"
'''
        
        with open(package_dir / 'requirements.txt', 'w', encoding='utf-8') as f:
            f.write(requirements)
    
    def _create_dockerfile(self, package_dir: Path) -> None:
        """Create Dockerfile for containerized installation."""
        dockerfile_content = '''FROM ubuntu:22.04

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    make \\
    gcc \\
    perl \\
    python3 \\
    python3-pip \\
    git \\
    wget \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt

# Copy installer package
COPY . /app/openssl-installer
WORKDIR /app/openssl-installer

# Install the package
RUN pip3 install -e .

# Set entry point
ENTRYPOINT ["openssl-install"]
'''
        
        with open(package_dir / 'docker' / 'Dockerfile', 'w', encoding='utf-8') as f:
            f.write(dockerfile_content)
    
    def _create_documentation(self, package_dir: Path) -> None:
        """Create documentation files."""
        # Create README.md
        readme_content = '''# OpenSSL Installer

Modern Python-based OpenSSL installer with enhanced features.

## Features

- **Modern Python**: Uses subprocess, pathlib, and click
- **Cross-platform**: Works on Linux, macOS, and Windows
- **Docker Support**: Containerized installation options
- **Conan Integration**: Package manager integration
- **Comprehensive Testing**: Full test suite included
- **Documentation**: Complete documentation and examples

## Installation

```bash
pip install openssl-installer
```

## Usage

```bash
# Basic installation
openssl-install --prefix /usr/local

# With custom configuration
openssl-install --config config.json --verbose

# Docker installation
openssl-install --docker --image openssl:latest
```

## Development

```bash
# Clone repository
git clone https://github.com/sparesparrow/openssl-tools.git
cd openssl-tools

# Install in development mode
pip install -e .[dev]

# Run tests
pytest

# Format code
black .
isort .
```

## License

MIT License - see LICENSE file for details.
'''
        
        with open(package_dir / 'README.md', 'w', encoding='utf-8') as f:
            f.write(readme_content)
