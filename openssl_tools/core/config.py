#!/usr/bin/env python3
"""
OpenSSL Tools Configuration Management
Based on ngapy-dev patterns for YAML-based configuration system
"""

import logging
import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from functools import cache
import hashlib


class ConfigurationBase:
    """Base configuration class following ngapy-dev patterns"""
    
    def __init__(self):
        self._cache = {}
        self._config_files = []
    
    def _compute_key(self, **kwargs) -> Tuple:
        """Compute cache key for configuration"""
        # This should be implemented by subclasses
        raise NotImplementedError("Subclasses must implement _compute_key")
    
    def _create_new_configuration(self, **kwargs) -> Any:
        """Create new configuration instance"""
        # This should be implemented by subclasses
        raise NotImplementedError("Subclasses must implement _create_new_configuration")
    
    def get_configuration(self, **kwargs) -> Any:
        """Get configuration with caching"""
        key = self._compute_key(**kwargs)
        
        if key in self._cache:
            return self._cache[key]
        
        config = self._create_new_configuration(**kwargs)
        self._cache[key] = config
        return config


class ConfigLoaderManager(ConfigurationBase):
    """Configuration loader manager following ngapy-dev patterns"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        super().__init__()
        self.config_dir = config_dir or Path(__file__).parent.parent.parent / 'conf'
        self._config_files = self._find_config_files()
    
    def _find_config_files(self) -> List[Path]:
        """Find all configuration files in config directory"""
        config_files = []
        
        if not self.config_dir.exists():
            logging.warning(f"Configuration directory does not exist: {self.config_dir}")
            return config_files
        
        # Find YAML files with priority naming
        for pattern in ['*.yaml', '*.yml']:
            config_files.extend(self.config_dir.glob(pattern))
        
        # Sort by priority (1_*, 2_*, etc.)
        def priority_key(path: Path) -> Tuple[int, str]:
            name = path.stem
            if '_' in name:
                try:
                    priority = int(name.split('_')[0])
                    return (priority, name)
                except ValueError:
                    return (999, name)
            return (999, name)
        
        config_files.sort(key=priority_key)
        return config_files
    
    def _compute_key(self, **kwargs) -> Tuple:
        """Compute cache key based on config files and arguments"""
        # Get file hashes for cache invalidation
        file_hashes = []
        for config_file in self._config_files:
            if config_file.exists():
                try:
                    with open(config_file, 'rb') as f:
                        content = f.read()
                        file_hash = hashlib.md5(content).hexdigest()
                        file_hashes.append((str(config_file), file_hash))
                except Exception as e:
                    logging.warning(f"Failed to hash config file {config_file}: {e}")
                    file_hashes.append((str(config_file), "error"))
        
        return (
            tuple(file_hashes),
            tuple(sorted(kwargs.items()))
        )
    
    def _create_new_configuration(self, **kwargs) -> 'ConfigLoaderInstance':
        """Create new configuration instance"""
        return ConfigLoaderInstance(self._config_files, **kwargs)
    
    def reload_config(self) -> None:
        """Reload configuration from files"""
        self._cache.clear()
        self._config_files = self._find_config_files()
        logging.info("Configuration reloaded")


class ConfigLoaderInstance:
    """Configuration loader instance following ngapy-dev patterns"""
    
    def __init__(self, config_files: List[Path], **kwargs):
        self.config_files = config_files
        self.kwargs = kwargs
        self._config_data = {}
        self._load_all_configs()
    
    def _load_all_configs(self) -> None:
        """Load all configuration files"""
        for config_file in self.config_files:
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f) or {}
                    self._config_data.update(config_data)
                    logging.debug(f"Loaded config from {config_file}")
            except Exception as e:
                logging.warning(f"Failed to load config file {config_file}: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key"""
        return self._config_data.get(key, default)
    
    def __getattr__(self, name: str) -> Any:
        """Get configuration section as attribute"""
        if name in self._config_data:
            value = self._config_data[name]
            if isinstance(value, dict):
                return ConfigSection(value)
            return value
        raise AttributeError(f"Configuration section '{name}' not found")
    
    def __contains__(self, key: str) -> bool:
        """Check if configuration key exists"""
        return key in self._config_data
    
    def __iter__(self):
        """Iterate over configuration keys"""
        return iter(self._config_data)
    
    def keys(self):
        """Get configuration keys"""
        return self._config_data.keys()
    
    def values(self):
        """Get configuration values"""
        return self._config_data.values()
    
    def items(self):
        """Get configuration items"""
        return self._config_data.items()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return self._config_data.copy()
    
    def save_config(self, config_file: Path, section: str = None) -> bool:
        """Save configuration to file"""
        try:
            if section:
                # Save specific section
                config_data = {section: self._config_data.get(section, {})}
            else:
                # Save all configuration
                config_data = self._config_data
            
            # Ensure directory exists
            config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config_data, f, default_flow_style=False, sort_keys=False)
            
            logging.info(f"Configuration saved to {config_file}")
            return True
        except Exception as e:
            logging.error(f"Failed to save configuration to {config_file}: {e}")
            return False


class ConfigSection:
    """Configuration section wrapper following ngapy-dev patterns"""
    
    def __init__(self, data: Dict[str, Any]):
        self._data = data
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key"""
        return self._data.get(key, default)
    
    def __getattr__(self, name: str) -> Any:
        """Get configuration value as attribute"""
        if name in self._data:
            value = self._data[name]
            if isinstance(value, dict):
                return ConfigSection(value)
            return value
        raise AttributeError(f"Configuration key '{name}' not found")
    
    def __contains__(self, key: str) -> bool:
        """Check if configuration key exists"""
        return key in self._data
    
    def __iter__(self):
        """Iterate over configuration keys"""
        return iter(self._data)
    
    def keys(self):
        """Get configuration keys"""
        return self._data.keys()
    
    def values(self):
        """Get configuration values"""
        return self._data.values()
    
    def items(self):
        """Get configuration items"""
        return self._data.items()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert section to dictionary"""
        return self._data.copy()


@cache
def get_config_loader() -> ConfigLoaderManager:
    """Get cached configuration loader instance"""
    return ConfigLoaderManager()


def load_configuration(config_dir: Optional[Path] = None) -> ConfigLoaderInstance:
    """Load configuration from files"""
    loader = ConfigLoaderManager(config_dir)
    return loader.get_configuration()


def get_config_value(key: str, default: Any = None, config_dir: Optional[Path] = None) -> Any:
    """Get configuration value by key"""
    config = load_configuration(config_dir)
    return config.get(key, default)


def get_config_section(section: str, config_dir: Optional[Path] = None) -> ConfigSection:
    """Get configuration section"""
    config = load_configuration(config_dir)
    return getattr(config, section, ConfigSection({}))


def save_configuration(config_data: Dict[str, Any], 
                      config_file: Path,
                      section: Optional[str] = None) -> bool:
    """Save configuration to file"""
    config = ConfigLoaderInstance([], **config_data)
    return config.save_config(config_file, section)


def merge_configurations(*configs: ConfigLoaderInstance) -> ConfigLoaderInstance:
    """Merge multiple configurations"""
    merged_data = {}
    
    for config in configs:
        merged_data.update(config.to_dict())
    
    return ConfigLoaderInstance([], **merged_data)


def validate_configuration(config: ConfigLoaderInstance, 
                          required_keys: List[str],
                          logger: Optional[logging.Logger] = None) -> bool:
    """Validate configuration has required keys"""
    if logger is None:
        logger = logging.getLogger('openssl_tools.config')
    
    missing_keys = []
    
    for key in required_keys:
        if key not in config:
            missing_keys.append(key)
    
    if missing_keys:
        logger.error(f"Missing required configuration keys: {missing_keys}")
        return False
    
    logger.info("Configuration validation passed")
    return True


def get_environment_config() -> Dict[str, Any]:
    """Get configuration from environment variables"""
    env_config = {}
    
    # Common environment variables
    env_mappings = {
        'OPENSSL_TOOLS_CONFIG_DIR': 'config_dir',
        'OPENSSL_TOOLS_LOG_LEVEL': 'logging.level',
        'OPENSSL_TOOLS_ARTIFACTORY_URL': 'artifactory.root',
        'OPENSSL_TOOLS_ARTIFACTORY_USER': 'artifactory.user',
        'OPENSSL_TOOLS_ARTIFACTORY_PASSWORD': 'artifactory.password',
        'OPENSSL_TOOLS_BUILD_JOBS': 'build.max_jobs',
        'OPENSSL_TOOLS_ENABLE_CCACHE': 'build.enable_ccache',
        'OPENSSL_TOOLS_ENABLE_SCCACHE': 'build.enable_sccache',
    }
    
    for env_var, config_key in env_mappings.items():
        value = os.environ.get(env_var)
        if value is not None:
            # Convert string values to appropriate types
            if value.lower() in ('true', 'false'):
                value = value.lower() == 'true'
            elif value.isdigit():
                value = int(value)
            
            # Set nested configuration value
            keys = config_key.split('.')
            current = env_config
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]
            current[keys[-1]] = value
    
    return env_config


def create_default_config(config_dir: Path) -> None:
    """Create default configuration files"""
    config_dir.mkdir(parents=True, exist_ok=True)
    
    # Default artifactory configuration
    artifactory_config = {
        'artifactory': {
            'schema_version': '1.0',
            'root': 'https://artifactory.example.com:443/artifactory',
            'user': 'openssl-tools-user',
            'password': '${ARTIFACTORY_PASSWORD}',
            'conan_url': 'https://artifactory.example.com/artifactory/api/conan/openssl-tools-local',
            'conan_name': 'openssl-tools',
            'conan_paths': [
                '/usr/local/bin/conan',
                '/opt/conan/bin/conan',
                '/home/sparrow/.local/bin/conan'
            ]
        }
    }
    
    artifactory_file = config_dir / '1_artifactory.yaml'
    with open(artifactory_file, 'w') as f:
        yaml.dump(artifactory_config, f, default_flow_style=False)
    
    # Default build configuration
    build_config = {
        'build': {
            'schema_version': '1.0',
            'max_jobs': 4,
            'enable_ccache': True,
            'enable_sccache': False,
            'optimize_build': True,
            'reproducible_builds': True,
            'parallel_download': True,
            'download_threads': -1
        }
    }
    
    build_file = config_dir / '1_build.yaml'
    with open(build_file, 'w') as f:
        yaml.dump(build_config, f, default_flow_style=False)
    
    # Default logging configuration
    logging_config = {
        'logging': {
            'schema_version': '1.0',
            'level': 'INFO',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'handlers': [
                {'type': 'console'},
                {'type': 'file', 'filename': 'openssl_tools.log', 'max_bytes': 10485760, 'backup_count': 5}
            ]
        }
    }
    
    logging_file = config_dir / '1_logging.yaml'
    with open(logging_file, 'w') as f:
        yaml.dump(logging_config, f, default_flow_style=False)
    
    # Default launcher configuration
    launcher_config = {
        'launcher': {
            'version': '2.0',
            'git_repository': '',
            'remote_setup': '',
            'conan_home': '',
            'python_interpreter': '',
            'build_optimization': True,
            'parallel_downloads': True,
            'cache_cleanup': True
        }
    }
    
    launcher_file = config_dir / 'launcher.yaml'
    with open(launcher_file, 'w') as f:
        yaml.dump(launcher_config, f, default_flow_style=False)
    
    logging.info(f"Created default configuration files in {config_dir}")


def get_config_file_path(config_name: str, config_dir: Optional[Path] = None) -> Path:
    """Get configuration file path by name"""
    if config_dir is None:
        config_dir = Path(__file__).parent.parent.parent / 'conf'
    
    # Try different extensions
    for ext in ['.yaml', '.yml']:
        config_file = config_dir / f"{config_name}{ext}"
        if config_file.exists():
            return config_file
    
    # Return default path
    return config_dir / f"{config_name}.yaml"


def list_config_files(config_dir: Optional[Path] = None) -> List[Path]:
    """List all configuration files"""
    if config_dir is None:
        config_dir = Path(__file__).parent.parent.parent / 'conf'
    
    config_files = []
    for pattern in ['*.yaml', '*.yml']:
        config_files.extend(config_dir.glob(pattern))
    
    return sorted(config_files)


def backup_config_file(config_file: Path, backup_suffix: str = '.bak') -> Optional[Path]:
    """Backup configuration file"""
    if not config_file.exists():
        return None
    
    backup_file = config_file.with_suffix(config_file.suffix + backup_suffix)
    
    try:
        import shutil
        shutil.copy2(config_file, backup_file)
        logging.info(f"Backed up configuration file: {config_file} -> {backup_file}")
        return backup_file
    except Exception as e:
        logging.error(f"Failed to backup configuration file: {e}")
        return None