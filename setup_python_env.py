#!/usr/bin/env python3
"""
OpenSSL Tools - Python Environment Manager
Manages isolated Python environments for different versions with Conan integration.
"""

import os
import subprocess
import sys
import logging
from pathlib import Path
from typing import List, Optional
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PythonEnvironmentManager:
    """Manages isolated Python environments for OpenSSL tools development."""
    
    def __init__(self, python_versions: List[str] = None, base_path: Optional[Path] = None):
        self.versions = python_versions or ["3.8", "3.9", "3.10", "3.11", "3.12"]
        self.base_path = base_path or Path.home() / ".openssl-python-envs"
        self.config_file = self.base_path / "config.json"
        
    def setup_environments(self, force_recreate: bool = False) -> bool:
        """
        Set up isolated Python environments for each version.
        
        Args:
            force_recreate: If True, recreate existing environments
            
        Returns:
            bool: True if all environments were set up successfully
        """
        logger.info(f"Setting up Python environments in {self.base_path}")
        
        # Create base directory
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        success_count = 0
        for version in self.versions:
            try:
                if self._setup_single_environment(version, force_recreate):
                    success_count += 1
                    logger.info(f"Successfully set up Python {version}")
                else:
                    logger.error(f"Failed to set up Python {version}")
            except Exception as e:
                logger.error(f"Error setting up Python {version}: {e}")
                
        # Save configuration
        self._save_config()
        
        logger.info(f"Successfully set up {success_count}/{len(self.versions)} environments")
        return success_count == len(self.versions)
        
    def _setup_single_environment(self, version: str, force_recreate: bool) -> bool:
        """Set up a single Python environment."""
        env_path = self.base_path / f"python{version}"
        
        # Check if environment exists and should be recreated
        if env_path.exists() and not force_recreate:
            logger.info(f"Environment for Python {version} already exists, skipping")
            return True
            
        if env_path.exists() and force_recreate:
            logger.info(f"Removing existing environment for Python {version}")
            import shutil
            shutil.rmtree(env_path)
            
        # Create virtual environment
        logger.info(f"Creating virtual environment for Python {version}")
        try:
            # Try to use specific Python version if available
            python_cmd = f"python{version}"
            subprocess.run([python_cmd, "--version"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Fall back to system Python
            python_cmd = sys.executable
            logger.warning(f"Python {version} not found, using system Python: {python_cmd}")
            
        subprocess.run([
            python_cmd, "-m", "venv", str(env_path)
        ], check=True)
        
        # Install dependencies
        pip_path = env_path / "bin" / "pip"
        if not pip_path.exists():
            pip_path = env_path / "Scripts" / "pip.exe"  # Windows
            
        if not pip_path.exists():
            logger.error(f"pip not found in environment for Python {version}")
            return False
            
        # Upgrade pip first
        subprocess.run([
            str(pip_path), "install", "--upgrade", "pip"
        ], check=True)
        
        # Install required packages
        packages = [
            "conan==2.0.17",
            "requests>=2.28.0",
            "cryptography>=3.4.8",
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0"
        ]
        
        logger.info(f"Installing packages for Python {version}")
        subprocess.run([
            str(pip_path), "install"
        ] + packages, check=True)
        
        return True
        
    def get_environment_path(self, version: str) -> Optional[Path]:
        """Get the path to a specific Python environment."""
        env_path = self.base_path / f"python{version}"
        return env_path if env_path.exists() else None
        
    def get_python_executable(self, version: str) -> Optional[Path]:
        """Get the Python executable for a specific version."""
        env_path = self.get_environment_path(version)
        if not env_path:
            return None
            
        python_exe = env_path / "bin" / "python"
        if not python_exe.exists():
            python_exe = env_path / "Scripts" / "python.exe"  # Windows
            
        return python_exe if python_exe.exists() else None
        
    def run_in_environment(self, version: str, command: List[str], cwd: Optional[Path] = None) -> subprocess.CompletedProcess:
        """Run a command in a specific Python environment."""
        python_exe = self.get_python_executable(version)
        if not python_exe:
            raise ValueError(f"Python {version} environment not found")
            
        full_command = [str(python_exe)] + command
        return subprocess.run(full_command, cwd=cwd, check=True)
        
    def _save_config(self):
        """Save configuration to file."""
        config = {
            "versions": self.versions,
            "base_path": str(self.base_path),
            "created_at": str(Path().cwd()),
            "environments": {}
        }
        
        for version in self.versions:
            env_path = self.get_environment_path(version)
            if env_path:
                config["environments"][version] = {
                    "path": str(env_path),
                    "python_exe": str(self.get_python_executable(version))
                }
                
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
            
    def load_config(self) -> dict:
        """Load configuration from file."""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {}
        
    def list_environments(self) -> dict:
        """List all available environments."""
        config = self.load_config()
        return config.get("environments", {})
        
    def cleanup_environment(self, version: str) -> bool:
        """Remove a specific environment."""
        env_path = self.get_environment_path(version)
        if not env_path:
            logger.warning(f"Environment for Python {version} not found")
            return False
            
        import shutil
        shutil.rmtree(env_path)
        logger.info(f"Removed environment for Python {version}")
        
        # Update config
        self._save_config()
        return True
        
    def cleanup_all_environments(self) -> bool:
        """Remove all environments."""
        import shutil
        if self.base_path.exists():
            shutil.rmtree(self.base_path)
            logger.info("Removed all Python environments")
            return True
        return False


def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="OpenSSL Python Environment Manager")
    parser.add_argument("--versions", nargs="+", default=["3.8", "3.9", "3.10", "3.11", "3.12"],
                       help="Python versions to set up")
    parser.add_argument("--base-path", type=Path,
                       help="Base path for environments")
    parser.add_argument("--force", action="store_true",
                       help="Force recreate existing environments")
    parser.add_argument("--list", action="store_true",
                       help="List available environments")
    parser.add_argument("--cleanup", type=str,
                       help="Clean up specific version (or 'all')")
    
    args = parser.parse_args()
    
    manager = PythonEnvironmentManager(
        python_versions=args.versions,
        base_path=args.base_path
    )
    
    if args.list:
        environments = manager.list_environments()
        if environments:
            print("Available environments:")
            for version, info in environments.items():
                print(f"  Python {version}: {info['path']}")
        else:
            print("No environments found")
        return
        
    if args.cleanup:
        if args.cleanup == "all":
            manager.cleanup_all_environments()
        else:
            manager.cleanup_environment(args.cleanup)
        return
        
    # Set up environments
    success = manager.setup_environments(force_recreate=args.force)
    if success:
        print("All Python environments set up successfully!")
    else:
        print("Some environments failed to set up. Check logs for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()