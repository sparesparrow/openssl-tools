#!/usr/bin/env python3
"""
OpenSSL Conan Functions
Advanced Conan functions for OpenSSL project
"""

import logging
import os
import re
import sys
import tempfile
from datetime import datetime, timedelta
from functools import cache
from pathlib import Path

import psutil
import yaml

# Set up logging
log = logging.getLogger(__name__)

# Set Conan environment variables for better output
os.environ['CONAN_COLOR_DISPLAY'] = '1'
os.environ['CLICOLOR_FORCE'] = '1'
os.environ['CLICOLOR'] = '1'


class OpenSSLRuntimeError(Exception):
    """Custom exception for OpenSSL Conan operations"""
    pass


def execute_command(command, cwd=None):
    """Execute a command and return return code and output lines"""
    import subprocess
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False
        )
        output_lines = result.stdout.strip().split('\n') if result.stdout else []
        if result.stderr:
            output_lines.extend(result.stderr.strip().split('\n'))
        return result.returncode, output_lines
    except Exception as e:
        log.error(f"Error executing command '{command}': {e}")
        return 1, [str(e)]


def find_executable_in_path(executable_name):
    """Find executable in PATH"""
    import shutil
    return shutil.which(executable_name)


def find_first_existing_file(paths, filename):
    """Find first existing file in given paths"""
    for path in paths:
        file_path = Path(path) / filename
        if file_path.exists():
            return file_path
    return None


@cache
def get_default_conan() -> Path:
    """Get the default Conan executable path"""
    conan_exe = find_executable_in_path('conan')
    if conan_exe:
        log.debug(f'Default conan found in path: {conan_exe}')
        return Path(conan_exe)
    else:
        raise OpenSSLRuntimeError('Default Conan executable not found, please install it from this URL: '
                                'https://conan.io/downloads.html')


@cache
def get_conan_home():
    """Get Conan home directory"""
    rc, return_string = execute_command(f'{get_default_conan()} config home')
    if 'CONAN_USER_HOME' in os.environ:
        return return_string[-1], os.environ['CONAN_USER_HOME']
    else:
        return return_string[-1], Path.home() / '.conan2'


def get_all_packages_in_cache() -> list:
    """Get all packages in Conan cache"""
    rc, return_string = execute_command(f'{get_default_conan()} search --raw')
    if rc == 0:
        return list(filter(lambda line: not line.startswith('WARN'), return_string))
    else:
        return []


def remove_conan_package_in_cache(package_name):
    """Remove a package from Conan cache"""
    return execute_command(f'{get_default_conan()} remove {package_name} --force')


class ConanJsonLoader:
    """Load and parse Conan JSON information"""
    
    def __init__(self, repository_path):
        import json
        from types import SimpleNamespace
        
        temp_out = tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False)
        
        conan_info_command = f'{get_default_conan()} info {repository_path} --paths -j {temp_out.name}'
        rc, return_string = execute_command(conan_info_command, cwd=repository_path)
        
        if rc == 1:
            log.warning(f'Conan info failed, trying to disable Conan remote')
            (Path(repository_path) / 'graph_info.json').unlink(missing_ok=True)
            # Try again without remote
            execute_command(f'{conan_info_command} -if .', cwd=repository_path)
        
        result_json = json.load(temp_out)
        self.result_munch = json.loads(json.dumps(result_json), object_hook=lambda d: SimpleNamespace(**d))
        temp_out.close()
        os.unlink(temp_out.name)
        self._get_root_node().package_folder = repository_path
    
    def _get_root_node(self):
        """Get the root node from Conan info"""
        for dependency_node in self.result_munch:
            if dependency_node.display_name.startswith('conanfile.py'):
                return dependency_node
    
    def _get_node_with_reference(self, reference):
        """Get node with specific reference"""
        for dependency_node in self.result_munch:
            if dependency_node.reference == reference:
                return dependency_node
    
    @staticmethod
    def get_package_name_version(package):
        """Extract package name and version"""
        _, version = package.display_name.split('/', maxsplit=1)
        version = version.split(')', maxsplit=1)[0]
        name = package.provides[0] if package.provides else package.display_name.split('/')[0]
        return name, version
    
    def filter_skipped(self):
        """Filter out skipped packages"""
        package_dict = {}
        for dependency_node in self.result_munch:
            name, version = self.get_package_name_version(dependency_node)
            if name in package_dict:
                conflict_name, conflict_version = self.get_package_name_version(package_dict[name])
                log.info(f'Conan package conflict: {name}/{version} and {conflict_name}/{conflict_version}')
                if getattr(dependency_node, 'binary', None) == 'Skip':
                    log.info(f'Selecting {conflict_name}/{conflict_version}')
                    continue
                log.info(f'Selecting {name}/{version}')
            package_dict[name] = dependency_node
        return package_dict


class ConanConfigurationTracker:
    """Track Conan package usage and configuration"""
    
    def __init__(self):
        self.expected_version = 1.0
        self.__data = {
            'version': self.expected_version,
            'conan_usage': dict(),
        }
        self.load_config()
    
    @property
    def config_path(self) -> Path:
        """Get configuration file path"""
        return Path(get_conan_home()[0]) / 'conan_tracker.yaml'
    
    @property
    def packages(self) -> dict:
        """Get packages dictionary"""
        return self.__data['conan_usage']
    
    @packages.setter
    def packages(self, value):
        """Set packages dictionary"""
        self.__data['conan_usage'] = value
    
    def load_config(self):
        """Load configuration from file"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as stream:
                try:
                    temp_data = yaml.safe_load(stream)
                    if not temp_data or str(temp_data['version']) != '1.0':
                        self.save_config()
                    else:
                        self.__data = temp_data
                except yaml.YAMLError:
                    pass
    
    def save_config(self):
        """Save configuration to file"""
        with open(self.config_path, 'w') as stream:
            yaml.safe_dump(self.__data, stream)
    
    def remove_old_packages(self, time_delta: timedelta):
        """Remove old packages from cache"""
        all_packages = self.packages
        cached = get_all_packages_in_cache()
        for cached_package in cached:
            if cached_package not in all_packages.keys():
                log.warning(f'Removing because it is not tracked: {cached_package}')
                remove_conan_package_in_cache(cached_package)
            elif all_packages[cached_package]['last_used'] < datetime.now() - time_delta:
                log.warning(f'Removing because it is old: {cached_package}. '
                            f'Last Used: {all_packages[cached_package]["last_used"]}')
                remove_conan_package_in_cache(cached_package)
                del all_packages[cached_package]
            else:
                log.info(f'Not removing, active package: {cached_package}. '
                         f'Last Used: {all_packages[cached_package]["last_used"]}')
        self.save_config()
        log.info('Executing result code: 0: Cleaning of conan packages finished')


class ConanConfiguration:
    """Conan configuration management"""
    
    def __init__(self, conan_tracker=ConanConfigurationTracker()):
        self.conan_tracker = conan_tracker
    
    @staticmethod
    def get_conanfile(repository_path):
        """Get conanfile.py path"""
        conanfile_path = Path(repository_path) / 'conanfile.py'
        if not conanfile_path.exists():
            raise OpenSSLRuntimeError(f'Conanfile.py cannot be located in {repository_path}')
        return conanfile_path
    
    @staticmethod
    def get_conan_lock(repository_path):
        """Get conan.lock file path and existence"""
        conan_lock_file = Path(repository_path) / 'conan.lock'
        return conan_lock_file, conan_lock_file.exists()
    
    def _compute_key(self, **kwargs):
        """Compute configuration key"""
        import hashlib
        repo_path = Path(kwargs['repository_path']).resolve()
        conan_lock, exists = self.get_conan_lock(repo_path)
        if exists:
            conan_lock_hash = hashlib.md5(conan_lock.read_bytes()).hexdigest()
        else:
            conan_lock_hash = None
        conanfile_path = self.get_conanfile(repo_path)
        conanfile_hash = hashlib.md5(conanfile_path.read_bytes()).hexdigest()
        return repo_path, conanfile_hash, conan_lock_hash
    
    def _create_new_configuration(self, **kwargs):
        """Create new configuration"""
        conan_loader = ConanJsonLoader(kwargs['repository_path'])
        packages = conan_loader.filter_skipped().values()
        packages_old = {}
        for package in packages:
            name, version = conan_loader.get_package_name_version(package)
            packages_old[name] = (name, version, Path(package.get('package_folder', '')))
        
        for name, version, _ in packages_old.values():
            self.conan_tracker.packages[f'{name}/{version}'] = {'last_used': datetime.now()}
        self.conan_tracker.save_config()
        return packages_old
    
    def get_configuration(self, **kwargs):
        """Get configuration with caching"""
        key = self._compute_key(**kwargs)
        if not hasattr(self, '_cache'):
            self._cache = {}
        if key not in self._cache:
            self._cache[key] = self._create_new_configuration(**kwargs)
        return self._cache[key]


def get_package_details(repository_path, package_name, options=''):
    """Get detailed information about a package"""
    rc, return_string = execute_command(f'{get_default_conan()} info {repository_path} {options} '
                                        f'--paths --package-filter {package_name}/*', cwd=repository_path)
    package_line = 0
    for line_number, line in reversed(list(enumerate(return_string))):
        if line.startswith(package_name) and 'WARN' not in line:
            package_line = line_number
            break
    package_info = {}
    for line in range(package_line + 1, len(return_string)):
        info = return_string[line].split(':', 1)
        if len(info) == 2:
            package_info[info[0].strip()] = info[1].strip()
    return package_info


def print_package_version(repository_path, package=None):
    """Print package version"""
    packages = ConanConfiguration().get_configuration(repository_path=repository_path)
    if package != "" and package is not None:
        print(f'{packages[package][0]}/{packages[package][1]}')
    else:
        result = list(filter(lambda package_def: package_def[2] == Path(repository_path), packages.values()))
        if result:
            print(f'{result[0][0]}/{result[0][1]}')


def print_package_path(repository_path, package=None):
    """Print package path"""
    packages = ConanConfiguration().get_configuration(repository_path=repository_path)
    if package != "" and package is not None:
        print(packages[package][2])
    else:
        result = list(filter(lambda package_def: package_def[2] == Path(repository_path), packages.values()))
        if result:
            print(result[0][2])


def install_packages_for_repository(repository_path):
    """Install packages for repository"""
    execute_command(f'{get_default_conan()} install {repository_path}', cwd=repository_path)
    return ConanConfiguration().get_configuration(repository_path=repository_path)


def download_package_for_repository(repository_path, package_name) -> Path:
    """Download package for repository"""
    packages = ConanConfiguration().get_configuration(repository_path=repository_path)
    if package_name in packages:
        package_path = packages[package_name][2]
        if not package_path.exists():
            download_package_version(package_name, packages[package_name][1])
        return package_path
    else:
        raise OpenSSLRuntimeError(f'Requested package {package_name} information was not found in {repository_path}.')


def get_info_about_package(package_name, repository_path):
    """Get information about a package"""
    return execute_command(f'{get_default_conan()} info {repository_path} '
                           f'--package-filter {package_name}*', cwd=repository_path)


def create_package_graph(repository_path):
    """Create package dependency graph"""
    repository_path = Path(repository_path)
    execute_command(f'{get_default_conan()} install {repository_path}', cwd=repository_path)
    output_file = repository_path / 'graph.html'
    execute_command(f'{get_default_conan()} info -g {output_file} {repository_path}',
                    cwd=repository_path)
    return output_file


def install_package_version(package, version, opts=''):
    """Install specific package version"""
    if version and package:
        command = f'{get_default_conan()} install {package}/{version}@ {opts}'
    else:
        command = f'{get_default_conan()} install . {opts}'
    rc, return_string = execute_command(command)
    return rc, return_string


def download_package_version(package, version, remote='conancenter', opts='') -> Path:
    """Download specific package version"""
    # Check package is already in local cache
    rc, return_string = execute_command(
        f'{get_default_conan()} info {package}/{version}@ --paths -n package_folder {opts}')
    m = re.search('package_folder: (.*)', '\n'.join(return_string))
    if not m:
        raise OpenSSLRuntimeError(f'Requested package does not exists: {package}/{version}')
    if m and m.group(1) and not Path(m.group(1)).is_dir():
        execute_command(
            f'{get_default_conan()} download {package}/{version}@ '
            f'-r {remote} {opts}')
        rc, return_string = execute_command(
            f'{get_default_conan()} info {package}/{version}@ --paths -n package_folder {opts}')
        m = re.search('package_folder: (.*)', '\n'.join(return_string))
    package_path = Path(m.group(1))
    if package_path.is_dir():
        return package_path
    else:
        raise OpenSSLRuntimeError(f'Requested package does not exists: {package}/{version}.'
                                f'Error message: {return_string}')


def python_version_sort(s):
    """Sort Python versions"""
    rank = 0
    numbers = s.replace('+dev', '.').split('.')
    numbers.reverse()
    position = 1
    for number in numbers:
        rank += int(number) * position
        position *= 100
    return rank


def get_all_package_config_folders(repository_path):
    """Get all package configuration folders"""
    packages = get_configuration_safe(repository_path)
    config_paths = []
    for name, version, package_path in packages.values():
        config_path = package_path / f'Conf'
        if config_path.exists() and not config_path.is_symlink():
            config_paths.append(config_path)
        config_path = package_path / f'_Build/SOURCE/Conf'
        if config_path.exists() and not config_path.is_symlink():
            config_paths.append(config_path)
    return config_paths


def get_configuration_safe(repository_path):
    """Get configuration safely"""
    try:
        packages = ConanConfiguration().get_configuration(repository_path=repository_path)
    except OpenSSLRuntimeError:
        packages = {'None': ['None', 'None', Path(repository_path)]}
    return packages


def setup_parallel_download(download_threads=-1):
    """Setup parallel download configuration"""
    threads = psutil.cpu_count() if download_threads == -1 else download_threads
    execute_command(f'{get_default_conan()} config set general.parallel_download={threads}')


def remove_conan_lock_files(conan_home=None):
    """Remove Conan lock files"""
    if not conan_home:
        conan_home, _ = get_conan_home()
    for path in Path(conan_home).glob('**/_.count'):
        path.unlink(missing_ok=True)
    for path in Path(conan_home).glob('**/_.count.lock'):
        path.unlink(missing_ok=True)


def reinitialize_conan_cache():
    """Reinitialize Conan cache"""
    from .artifactory_functions import setup_artifactory_remote
    conan_home, _ = get_conan_home()
    # Remove cache directory
    import shutil
    if Path(conan_home).exists():
        shutil.rmtree(conan_home)
    # Recreate and setup
    Path(conan_home).mkdir(parents=True, exist_ok=True)
    setup_artifactory_remote()