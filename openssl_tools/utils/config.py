#!/usr/bin/env python3
"""
OpenSSL Tools Configuration Manager
Manage configuration for OpenSSL tools
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manage configuration for OpenSSL tools"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration manager"""
        self.config_path = config_path or self._find_config_file()
        self.config = self._load_config()
    
    def _find_config_file(self) -> Optional[str]:
        """Find configuration file in standard locations"""
        # Look for config file in current directory and parent directories
        current_dir = Path.cwd()
        
        for parent in [current_dir] + list(current_dir.parents):
            config_file = parent / "tools_config.json"
            if config_file.exists():
                return str(config_file)
        
        # Look in environment variable
        env_config = os.environ.get('OPENSSL_TOOLS_CONFIG')
        if env_config and os.path.exists(env_config):
            return env_config
        
        return None
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if self.config_path and os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load config from {self.config_path}: {e}")
        
        # Return default configuration
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'tools': {
                'review_tools': {
                    'enabled': True,
                    'min_reviewers': 2,
                    'min_otc': 0,
                    'min_omc': 0,
                    'api_endpoint': 'https://api.openssl.org'
                },
                'release_tools': {
                    'enabled': True,
                    'templates_dir': 'templates',
                    'output_dir': 'releases',
                    'backup_dir': 'backups'
                },
                'statistics': {
                    'enabled': True,
                    'alpha_chi2': 0.95,
                    'alpha_binomial': 0.9999
                },
                'github': {
                    'enabled': True,
                    'api_endpoint': 'https://api.github.com'
                },
                'gitlab': {
                    'enabled': False,
                    'api_endpoint': 'https://gitlab.com/api/v4'
                }
            },
            'conan': {
                'package_name': 'openssl-tools',
                'version': '1.0.0'
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value by key"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save(self) -> bool:
        """Save configuration to file"""
        if not self.config_path:
            return False
        
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return False
    
    def get_tool_config(self, tool_name: str) -> Dict[str, Any]:
        """Get configuration for a specific tool"""
        return self.get(f'tools.{tool_name}', {})
    
    def is_tool_enabled(self, tool_name: str) -> bool:
        """Check if a tool is enabled"""
        return self.get(f'tools.{tool_name}.enabled', False)
    
    def get_api_endpoint(self, service: str) -> str:
        """Get API endpoint for a service"""
        return self.get(f'tools.{service}.api_endpoint', '')
    
    def get_review_requirements(self) -> Dict[str, int]:
        """Get review requirements"""
        return {
            'min_reviewers': self.get('tools.review_tools.min_reviewers', 2),
            'min_otc': self.get('tools.review_tools.min_otc', 0),
            'min_omc': self.get('tools.review_tools.min_omc', 0)
        }
    
    def get_release_config(self) -> Dict[str, str]:
        """Get release configuration"""
        return {
            'templates_dir': self.get('tools.release_tools.templates_dir', 'templates'),
            'output_dir': self.get('tools.release_tools.output_dir', 'releases'),
            'backup_dir': self.get('tools.release_tools.backup_dir', 'backups')
        }
    
    def get_statistics_config(self) -> Dict[str, float]:
        """Get statistics configuration"""
        return {
            'alpha_chi2': self.get('tools.statistics.alpha_chi2', 0.95),
            'alpha_binomial': self.get('tools.statistics.alpha_binomial', 0.9999)
        }