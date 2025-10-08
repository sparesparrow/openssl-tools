#!/usr/bin/env python3
"""
OpenSSL Tools Python Environment Manager
Based on ngapy-dev patterns for Python environment management and interpreter handling
"""

import logging
import os
import subprocess
import sys
import tempfile
import venv
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import json
import shutil


class PythonEnvironmentManager:
    """Python environment manager following ngapy-dev patterns"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger('openssl_tools.python_env_manager')
        
        # Configuration
        self.python_versions = self.config.get('python_versions', ['3.8', '3.9', '3.10', '3.11', '3.12'])
        self.default_version = self.config.get('default_version', '3.11')
        self.venv_dir = Path(self.config.get('venv_dir', '.venv'))
        self.requirements_file = Path(self.config.get('requirements_file', 'requirements.txt'))
        self.pip_index_url = self.config.get('pip_index_url', 'https://pypi.org/simple')
        
        # Environment detection
        self.available_pythons = self._detect_available_pythons()
        self.current_python = self._get_current_python()
    
    def _detect_available_pythons(self) -> Dict[str, Path]:
        """Detect available Python interpreters following ngapy-dev patterns"""
        available = {}
        
        # Check system PATH
        for version in self.python_versions:
            for cmd in [f'python{version}', f'python{version.replace(".", "")}']:
                try:
                    result = subprocess.run([cmd, '--version'], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        # Extract version from output
                        version_output = result.stdout.strip()
                        if version in version_output:
                            available[version] = shutil.which(cmd)
                            self.logger.debug(f"Found Python {version}: {available[version]}")
                except (FileNotFoundError, subprocess.TimeoutExpired):
                    continue
        
        # Check common installation paths
        common_paths = [
            '/usr/bin',
            '/usr/local/bin',
            '/opt/python/bin',
            '/home/sparrow/.local/bin',
            '/opt/homebrew/bin',  # macOS Homebrew
            '/usr/local/opt/python/bin'  # macOS Homebrew
        ]
        
        for base_path in common_paths:
            base_path = Path(base_path)
            if base_path.exists():
                for version in self.python_versions:
                    for cmd in [f'python{version}', f'python{version.replace(".", "")}']:
                        python_path = base_path / cmd
                        if python_path.exists() and python_path.is_file():
                            try:
                                result = subprocess.run([str(python_path), '--version'], 
                                                      capture_output=True, text=True, timeout=5)
                                if result.returncode == 0 and version in result.stdout:
                                    available[version] = str(python_path)
                                    self.logger.debug(f"Found Python {version}: {python_path}")
                            except (subprocess.TimeoutExpired, PermissionError):
                                continue
        
        self.logger.info(f"Detected {len(available)} Python versions: {list(available.keys())}")
        return available
    
    def _get_current_python(self) -> Dict[str, Any]:
        """Get current Python interpreter information"""
        python_path = Path(sys.executable)
        version_info = sys.version_info
        
        return {
            'path': str(python_path),
            'version': f"{version_info.major}.{version_info.minor}.{version_info.micro}",
            'version_info': version_info,
            'is_venv': hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix),
            'prefix': sys.prefix,
            'base_prefix': getattr(sys, 'base_prefix', sys.prefix)
        }
    
    def get_python_info(self, version: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get Python interpreter information for specific version"""
        if version is None:
            return self.current_python
        
        if version not in self.available_pythons:
            self.logger.warning(f"Python {version} not available")
            return None
        
        python_path = Path(self.available_pythons[version])
        
        try:
            result = subprocess.run([str(python_path), '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                version_output = result.stdout.strip()
                
                # Get more detailed info
                info_result = subprocess.run([str(python_path), '-c', 
                                           'import sys; print(sys.version_info.major, sys.version_info.minor, sys.version_info.micro)'],
                                          capture_output=True, text=True, timeout=5)
                
                if info_result.returncode == 0:
                    major, minor, micro = map(int, info_result.stdout.strip().split())
                    
                    return {
                        'path': str(python_path),
                        'version': f"{major}.{minor}.{micro}",
                        'version_info': (major, minor, micro),
                        'is_venv': False,  # System Python
                        'prefix': str(python_path.parent.parent),
                        'base_prefix': str(python_path.parent.parent)
                    }
        except Exception as e:
            self.logger.warning(f"Failed to get Python info for {version}: {e}")
        
        return None
    
    def create_virtual_environment(self, version: Optional[str] = None, 
                                 venv_path: Optional[Path] = None,
                                 system_site_packages: bool = False) -> Optional[Path]:
        """Create virtual environment following ngapy-dev patterns"""
        if version is None:
            version = self.default_version
        
        if version not in self.available_pythons:
            self.logger.error(f"Python {version} not available for virtual environment")
            return None
        
        if venv_path is None:
            venv_path = self.venv_dir / f"python{version.replace('.', '')}"
        
        python_path = self.available_pythons[version]
        
        try:
            # Create virtual environment
            venv.create(venv_path, 
                       system_site_packages=system_site_packages,
                       clear=True,
                       with_pip=True)
            
            self.logger.info(f"Created virtual environment: {venv_path}")
            
            # Install/upgrade pip
            self._upgrade_pip_in_venv(venv_path, python_path)
            
            return venv_path
        except Exception as e:
            self.logger.error(f"Failed to create virtual environment: {e}")
            return None
    
    def _upgrade_pip_in_venv(self, venv_path: Path, python_path: str) -> None:
        """Upgrade pip in virtual environment"""
        try:
            if os.name == 'nt':
                pip_path = venv_path / 'Scripts' / 'pip.exe'
                python_exe = venv_path / 'Scripts' / 'python.exe'
            else:
                pip_path = venv_path / 'bin' / 'pip'
                python_exe = venv_path / 'bin' / 'python'
            
            # Upgrade pip
            subprocess.run([str(python_exe), '-m', 'pip', 'install', '--upgrade', 'pip'],
                          check=True, timeout=60)
            
            self.logger.debug(f"Upgraded pip in {venv_path}")
        except Exception as e:
            self.logger.warning(f"Failed to upgrade pip in virtual environment: {e}")
    
    def activate_virtual_environment(self, venv_path: Path) -> Dict[str, str]:
        """Get environment variables for activating virtual environment"""
        if os.name == 'nt':
            # Windows
            venv_python = venv_path / 'Scripts' / 'python.exe'
            venv_scripts = venv_path / 'Scripts'
        else:
            # Unix-like
            venv_python = venv_path / 'bin' / 'python'
            venv_scripts = venv_path / 'bin'
        
        env_vars = {
            'VIRTUAL_ENV': str(venv_path),
            'PATH': f"{venv_scripts}{os.pathsep}{os.environ.get('PATH', '')}",
            'PYTHONPATH': str(venv_path),
            'PYTHON_EXECUTABLE': str(venv_python)
        }
        
        return env_vars
    
    def install_requirements(self, venv_path: Path, 
                           requirements_file: Optional[Path] = None,
                           upgrade: bool = False) -> bool:
        """Install requirements in virtual environment"""
        if requirements_file is None:
            requirements_file = self.requirements_file
        
        if not requirements_file.exists():
            self.logger.warning(f"Requirements file not found: {requirements_file}")
            return False
        
        try:
            if os.name == 'nt':
                pip_path = venv_path / 'Scripts' / 'pip.exe'
            else:
                pip_path = venv_path / 'bin' / 'pip'
            
            cmd = [str(pip_path), 'install', '-r', str(requirements_file)]
            if upgrade:
                cmd.append('--upgrade')
            
            # Add index URL if specified
            if self.pip_index_url:
                cmd.extend(['-i', self.pip_index_url])
            
            result = subprocess.run(cmd, check=True, timeout=300)
            
            self.logger.info(f"Installed requirements from {requirements_file}")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to install requirements: {e}")
            return False
        except subprocess.TimeoutExpired:
            self.logger.error("Requirements installation timed out")
            return False
    
    def install_package(self, venv_path: Path, package: str, 
                       version: Optional[str] = None,
                       editable: bool = False) -> bool:
        """Install package in virtual environment"""
        try:
            if os.name == 'nt':
                pip_path = venv_path / 'Scripts' / 'pip.exe'
            else:
                pip_path = venv_path / 'bin' / 'pip'
            
            cmd = [str(pip_path), 'install']
            
            if editable:
                cmd.append('-e')
            
            if version:
                cmd.append(f"{package}=={version}")
            else:
                cmd.append(package)
            
            # Add index URL if specified
            if self.pip_index_url:
                cmd.extend(['-i', self.pip_index_url])
            
            result = subprocess.run(cmd, check=True, timeout=60)
            
            self.logger.info(f"Installed package: {package}")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to install package {package}: {e}")
            return False
        except subprocess.TimeoutExpired:
            self.logger.error(f"Package installation timed out: {package}")
            return False
    
    def get_installed_packages(self, venv_path: Path) -> List[Dict[str, str]]:
        """Get list of installed packages in virtual environment"""
        try:
            if os.name == 'nt':
                pip_path = venv_path / 'Scripts' / 'pip.exe'
            else:
                pip_path = venv_path / 'bin' / 'pip'
            
            result = subprocess.run([str(pip_path), 'list', '--format=json'], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                packages = json.loads(result.stdout)
                return packages
            else:
                self.logger.warning("Failed to get installed packages")
                return []
        except Exception as e:
            self.logger.warning(f"Failed to get installed packages: {e}")
            return []
    
    def run_script_in_venv(self, venv_path: Path, script_path: Path, 
                          args: List[str] = None) -> subprocess.CompletedProcess:
        """Run script in virtual environment"""
        if args is None:
            args = []
        
        if os.name == 'nt':
            python_path = venv_path / 'Scripts' / 'python.exe'
        else:
            python_path = venv_path / 'bin' / 'python'
        
        cmd = [str(python_path), str(script_path)] + args
        
        # Set environment variables
        env = os.environ.copy()
        env.update(self.activate_virtual_environment(venv_path))
        
        return subprocess.run(cmd, env=env)
    
    def create_requirements_from_venv(self, venv_path: Path, 
                                    output_file: Optional[Path] = None) -> Optional[Path]:
        """Create requirements.txt from virtual environment"""
        if output_file is None:
            output_file = Path('requirements.txt')
        
        try:
            if os.name == 'nt':
                pip_path = venv_path / 'Scripts' / 'pip.exe'
            else:
                pip_path = venv_path / 'bin' / 'pip'
            
            result = subprocess.run([str(pip_path), 'freeze'], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                with open(output_file, 'w') as f:
                    f.write(result.stdout)
                
                self.logger.info(f"Created requirements file: {output_file}")
                return output_file
            else:
                self.logger.error("Failed to create requirements file")
                return None
        except Exception as e:
            self.logger.error(f"Failed to create requirements file: {e}")
            return None
    
    def cleanup_old_venvs(self, max_age_days: int = 30) -> int:
        """Clean up old virtual environments"""
        cleaned_count = 0
        current_time = time.time()
        max_age_seconds = max_age_days * 24 * 3600
        
        for venv_dir in self.venv_dir.iterdir():
            if venv_dir.is_dir():
                try:
                    # Check if it's a virtual environment
                    if (venv_dir / 'pyvenv.cfg').exists():
                        # Check age
                        venv_age = current_time - venv_dir.stat().st_mtime
                        if venv_age > max_age_seconds:
                            shutil.rmtree(venv_dir)
                            cleaned_count += 1
                            self.logger.info(f"Cleaned old virtual environment: {venv_dir}")
                except Exception as e:
                    self.logger.warning(f"Failed to clean virtual environment {venv_dir}: {e}")
        
        self.logger.info(f"Cleaned {cleaned_count} old virtual environments")
        return cleaned_count
    
    def get_venv_info(self, venv_path: Path) -> Optional[Dict[str, Any]]:
        """Get virtual environment information"""
        if not venv_path.exists():
            return None
        
        try:
            # Read pyvenv.cfg
            config_file = venv_path / 'pyvenv.cfg'
            if not config_file.exists():
                return None
            
            config = {}
            with open(config_file, 'r') as f:
                for line in f:
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        config[key.strip()] = value.strip()
            
            # Get Python info
            python_info = self.get_python_info()
            
            # Get installed packages
            packages = self.get_installed_packages(venv_path)
            
            return {
                'path': str(venv_path),
                'config': config,
                'python_info': python_info,
                'packages': packages,
                'package_count': len(packages),
                'created_at': venv_path.stat().st_ctime,
                'modified_at': venv_path.stat().st_mtime
            }
        except Exception as e:
            self.logger.warning(f"Failed to get virtual environment info: {e}")
            return None
    
    def list_virtual_environments(self) -> List[Dict[str, Any]]:
        """List all virtual environments"""
        venvs = []
        
        if not self.venv_dir.exists():
            return venvs
        
        for venv_dir in self.venv_dir.iterdir():
            if venv_dir.is_dir() and (venv_dir / 'pyvenv.cfg').exists():
                venv_info = self.get_venv_info(venv_dir)
                if venv_info:
                    venvs.append(venv_info)
        
        return venvs
    
    def export_environment(self, venv_path: Path, 
                          output_file: Optional[Path] = None) -> Optional[Path]:
        """Export virtual environment for sharing"""
        if output_file is None:
            output_file = Path(f"environment_{venv_path.name}.json")
        
        try:
            venv_info = self.get_venv_info(venv_path)
            if not venv_info:
                return None
            
            # Create export data
            export_data = {
                'python_version': venv_info['config'].get('version'),
                'python_path': venv_info['config'].get('home'),
                'packages': venv_info['packages'],
                'created_at': venv_info['created_at'],
                'exported_at': time.time()
            }
            
            with open(output_file, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            self.logger.info(f"Exported environment to {output_file}")
            return output_file
        except Exception as e:
            self.logger.error(f"Failed to export environment: {e}")
            return None
    
    def import_environment(self, export_file: Path, 
                          venv_path: Optional[Path] = None) -> Optional[Path]:
        """Import virtual environment from export file"""
        try:
            with open(export_file, 'r') as f:
                export_data = json.load(f)
            
            python_version = export_data.get('python_version')
            if not python_version:
                self.logger.error("No Python version specified in export file")
                return None
            
            # Create virtual environment
            if venv_path is None:
                venv_path = self.venv_dir / f"imported_{int(time.time())}"
            
            created_venv = self.create_virtual_environment(python_version, venv_path)
            if not created_venv:
                return None
            
            # Install packages
            packages = export_data.get('packages', [])
            for package in packages:
                package_name = package.get('name', '')
                package_version = package.get('version', '')
                
                if package_name:
                    self.install_package(created_venv, package_name, package_version)
            
            self.logger.info(f"Imported environment to {created_venv}")
            return created_venv
        except Exception as e:
            self.logger.error(f"Failed to import environment: {e}")
            return None


# Convenience functions
def get_python_manager(config: Optional[Dict[str, Any]] = None) -> PythonEnvironmentManager:
    """Get Python environment manager instance"""
    return PythonEnvironmentManager(config)


def create_python_venv(version: str, venv_path: Optional[Path] = None) -> Optional[Path]:
    """Create Python virtual environment"""
    manager = get_python_manager()
    return manager.create_virtual_environment(version, venv_path)


def activate_python_venv(venv_path: Path) -> Dict[str, str]:
    """Get activation environment variables for virtual environment"""
    manager = get_python_manager()
    return manager.activate_virtual_environment(venv_path)