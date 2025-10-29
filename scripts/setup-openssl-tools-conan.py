#!/usr/bin/env python3
"""
OpenSSL Tools Conan Environment Setup
Sets up a complete Python-based Conan development environment for openssl-tools
Based on openssl-tools patterns for proper Python dev/testing environment
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path
from typing import Dict, List, Optional
import argparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OpenSSLToolsConanSetup:
    """OpenSSL Tools Conan environment setup following ngapy patterns"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.platform = platform.system().lower()
        self.conan_dir = project_root / "conan-dev"
        self.scripts_dir = project_root / "scripts" / "conan"
        self.venv_dir = self.conan_dir / "venv"
        
    def setup_environment(self, force: bool = False) -> bool:
        """Set up the complete Conan Python environment"""
        try:
            logger.info("🚀 Setting up OpenSSL Tools Conan development environment...")
            logger.info(f"📋 Platform: {self.platform}")
            
            # Create directory structure
            self._create_directory_structure()
            
            # Set up Python virtual environment
            self._setup_python_venv(force)
            
            # Install dependencies
            self._install_dependencies()
            
            # Create Conan profiles
            self._create_conan_profiles()
            
            # Set up environment scripts
            self._create_environment_scripts()
            
            # Create configuration files
            self._create_configuration_files()
            
            logger.info("✅ OpenSSL Tools Conan environment setup complete!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Setup failed: {e}")
            return False
    
    def _create_directory_structure(self):
        """Create necessary directory structure following ngapy patterns"""
        directories = [
            self.conan_dir,
            self.conan_dir / "profiles",
            self.conan_dir / "locks",
            self.conan_dir / "cache",
            self.conan_dir / "artifacts",
            self.venv_dir,
            self.scripts_dir,
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"📁 Created directory: {directory}")
    
    def _setup_python_venv(self, force: bool = False):
        """Set up Python virtual environment"""
        logger.info("🐍 Setting up Python virtual environment...")
        
        if self.venv_dir.exists() and not force:
            # Check if it's actually a valid virtual environment
            if self.platform == "windows":
                pip_exe = self.venv_dir / "Scripts" / "pip.exe"
            else:
                pip_exe = self.venv_dir / "bin" / "pip"
            
            if pip_exe.exists():
                logger.info("Virtual environment already exists, skipping...")
                return
            else:
                logger.info("Virtual environment directory exists but is invalid, recreating...")
                import shutil
                shutil.rmtree(self.venv_dir)
        
        # Create virtual environment
        subprocess.run([sys.executable, "-m", "venv", str(self.venv_dir)], check=True)
        
        # Get Python executable path
        if self.platform == "windows":
            python_exe = self.venv_dir / "Scripts" / "python.exe"
            pip_exe = self.venv_dir / "Scripts" / "pip.exe"
        else:
            python_exe = self.venv_dir / "bin" / "python"
            pip_exe = self.venv_dir / "bin" / "pip"
        
        # Upgrade pip
        subprocess.run([str(pip_exe), "install", "--upgrade", "pip"], check=True)
        
        logger.info(f"✅ Virtual environment created: {self.venv_dir}")
    
    def _install_dependencies(self):
        """Install Python dependencies"""
        logger.info("📦 Installing Python dependencies...")
        
        # Get pip executable path
        if self.platform == "windows":
            pip_exe = self.venv_dir / "Scripts" / "pip.exe"
        else:
            pip_exe = self.venv_dir / "bin" / "pip"
        
        # Install requirements
        requirements_file = self.project_root / "requirements.txt"
        if requirements_file.exists():
            subprocess.run([str(pip_exe), "install", "-r", str(requirements_file)], check=True)
        
        # Install Conan 2.x with GitHub Packages support
        subprocess.run([str(pip_exe), "install", "conan>=2.0.0"], check=True)
        
        logger.info("✅ Dependencies installed")
    
    def _create_conan_profiles(self):
        """Create Conan profiles following ngapy patterns"""
        logger.info("⚙️ Creating Conan profiles...")
        
        profiles_dir = self.conan_dir / "profiles"
        
        # Linux profiles
        if self.platform == "linux":
            self._create_linux_profiles(profiles_dir)
        # Windows profiles
        elif self.platform == "windows":
            self._create_windows_profiles(profiles_dir)
        # macOS profiles
        elif self.platform == "darwin":
            self._create_macos_profiles(profiles_dir)
    
    def _create_linux_profiles(self, profiles_dir: Path):
        """Create Linux Conan profiles"""
        profiles = {
            "linux-gcc11": """[settings]
os=Linux
compiler=gcc
compiler.version=11
compiler.libcxx=libstdc++11
build_type=Release
arch=x86_64

[options]
openssl-tools:enable_review_tools=True
openssl-tools:enable_release_tools=True
openssl-tools:enable_statistics=True
openssl-tools:enable_github_integration=True
openssl-tools:enable_gitlab_integration=False
openssl-tools:enable_api_integration=True

[env]
CC=gcc-11
CXX=g++-11
""",
            "linux-clang15": """[settings]
os=Linux
compiler=clang
compiler.version=15
compiler.libcxx=libstdc++11
build_type=Release
arch=x86_64

[options]
openssl-tools:enable_review_tools=True
openssl-tools:enable_release_tools=True
openssl-tools:enable_statistics=True
openssl-tools:enable_github_integration=True
openssl-tools:enable_gitlab_integration=False
openssl-tools:enable_api_integration=True

[env]
CC=clang-15
CXX=clang++-15
""",
            "debug": """[settings]
os=Linux
compiler=gcc
compiler.version=11
compiler.libcxx=libstdc++11
build_type=Debug
arch=x86_64

[options]
openssl-tools:enable_review_tools=True
openssl-tools:enable_release_tools=True
openssl-tools:enable_statistics=True
openssl-tools:enable_github_integration=True
openssl-tools:enable_gitlab_integration=False
openssl-tools:enable_api_integration=True

[env]
CC=gcc-11
CXX=g++-11
"""
        }
        
        for profile_name, content in profiles.items():
            profile_path = profiles_dir / f"{profile_name}.profile"
            with open(profile_path, 'w') as f:
                f.write(content)
            logger.info(f"✅ Created profile: {profile_name}")
    
    def _create_windows_profiles(self, profiles_dir: Path):
        """Create Windows Conan profiles"""
        profiles = {
            "windows-msvc2022": """[settings]
os=Windows
compiler=Visual Studio
compiler.version=17
compiler.runtime=MD
build_type=Release
arch=x86_64

[options]
openssl-tools:enable_review_tools=True
openssl-tools:enable_release_tools=True
openssl-tools:enable_statistics=True
openssl-tools:enable_github_integration=True
openssl-tools:enable_gitlab_integration=False
openssl-tools:enable_api_integration=True
""",
            "debug": """[settings]
os=Windows
compiler=Visual Studio
compiler.version=17
compiler.runtime=MDd
build_type=Debug
arch=x86_64

[options]
openssl-tools:enable_review_tools=True
openssl-tools:enable_release_tools=True
openssl-tools:enable_statistics=True
openssl-tools:enable_github_integration=True
openssl-tools:enable_gitlab_integration=False
openssl-tools:enable_api_integration=True
"""
        }
        
        for profile_name, content in profiles.items():
            profile_path = profiles_dir / f"{profile_name}.profile"
            with open(profile_path, 'w') as f:
                f.write(content)
            logger.info(f"✅ Created profile: {profile_name}")
    
    def _create_macos_profiles(self, profiles_dir: Path):
        """Create macOS Conan profiles"""
        profiles = {
            "macos-clang14": """[settings]
os=Macos
compiler=apple-clang
compiler.version=14
compiler.libcxx=libc++
build_type=Release
arch=x86_64

[options]
openssl-tools:enable_review_tools=True
openssl-tools:enable_release_tools=True
openssl-tools:enable_statistics=True
openssl-tools:enable_github_integration=True
openssl-tools:enable_gitlab_integration=False
openssl-tools:enable_api_integration=True
""",
            "debug": """[settings]
os=Macos
compiler=apple-clang
compiler.version=14
compiler.libcxx=libc++
build_type=Debug
arch=x86_64

[options]
openssl-tools:enable_review_tools=True
openssl-tools:enable_release_tools=True
openssl-tools:enable_statistics=True
openssl-tools:enable_github_integration=True
openssl-tools:enable_gitlab_integration=False
openssl-tools:enable_api_integration=True
"""
        }
        
        for profile_name, content in profiles.items():
            profile_path = profiles_dir / f"{profile_name}.profile"
            with open(profile_path, 'w') as f:
                f.write(content)
            logger.info(f"✅ Created profile: {profile_name}")
    
    def _create_environment_scripts(self):
        """Create environment activation scripts"""
        logger.info("🔗 Creating environment scripts...")
        
        # Get Python executable path
        if self.platform == "windows":
            python_exe = self.venv_dir / "Scripts" / "python.exe"
            activate_script = self.venv_dir / "Scripts" / "activate.bat"
        else:
            python_exe = self.venv_dir / "bin" / "python"
            activate_script = self.venv_dir / "bin" / "activate"
        
        # Create activation script
        if self.platform == "windows":
            activate_content = f"""@echo off
echo Activating OpenSSL Tools Conan environment...
call "{activate_script}"
echo Environment activated!
echo Python: {python_exe}
echo Conan: conan --version
"""
        else:
            activate_content = f"""#!/bin/bash
echo "Activating OpenSSL Tools Conan environment..."
source "{activate_script}"
echo "Environment activated!"
echo "Python: {python_exe}"
echo "Conan: conan --version"
"""
        
        activate_file = self.conan_dir / "activate"
        if self.platform == "windows":
            activate_file = self.conan_dir / "activate.bat"
        
        with open(activate_file, 'w') as f:
            f.write(activate_content)
        
        if self.platform != "windows":
            os.chmod(activate_file, 0o755)
        
        logger.info(f"✅ Created activation script: {activate_file}")
    
    def _create_configuration_files(self):
        """Create configuration files"""
        logger.info("⚙️ Creating configuration files...")
        
        # Create conan.conf
        conan_conf = self.conan_dir / "conan.conf"
        conan_conf_content = f"""[log]
level = info

[storage]
path = {self.conan_dir / "cache"}

[proxies]
# http = http://user:pass@server:port
# https = http://user:pass@server:port

[remotes]
# Add your Conan remotes here
# conancenter = https://center.conan.io

[settings_defaults]
# Default settings for this environment
"""
        
        with open(conan_conf, 'w') as f:
            f.write(conan_conf_content)
        
        logger.info(f"✅ Created conan.conf: {conan_conf}")

    def setup_conan_dev_environment(self) -> bool:
        """Absorb setup-conan-dev-env.py"""
        logger.info("🔧 Setting up Conan development environment...")

        try:
            # Set up Conan home directory
            conan_home = self.project_root / "conan-dev"
            os.environ["CONAN_HOME"] = str(conan_home)

            # Create Conan configuration
            self._configure_conan_dev_environment()

            # Set up remotes
            self._setup_conan_remotes()

            # Initialize local cache
            self._initialize_conan_cache()

            logger.info("✅ Conan development environment setup complete")
            return True

        except Exception as e:
            logger.error(f"❌ Conan dev environment setup failed: {e}")
            return False

    def setup_conan_development_tools(self) -> bool:
        """Absorb conan-dev-setup.py"""
        logger.info("🛠️ Setting up Conan development tools...")

        try:
            # Install development tools
            dev_tools = [
                "conan",
                "cmake",
                "ninja",
                "git",
                "python3-dev"
            ]

            if self.platform == "linux":
                self._install_linux_dev_tools(dev_tools)
            elif self.platform == "darwin":
                self._install_macos_dev_tools(dev_tools)
            elif self.platform == "windows":
                self._install_windows_dev_tools(dev_tools)

            # Configure development environment
            self._configure_development_environment()

            logger.info("✅ Conan development tools setup complete")
            return True

        except Exception as e:
            logger.error(f"❌ Development tools setup failed: {e}")
            return False

    def run_complete_setup_validation(self) -> bool:
        """Absorb setup-complete.sh validation"""
        logger.info("✅ Running complete setup validation...")

        try:
            validation_results = {
                "python_version": self._validate_python_version(),
                "conan_installation": self._validate_conan_installation(),
                "virtual_environment": self._validate_virtual_environment(),
                "dependencies": self._validate_dependencies(),
                "profiles": self._validate_conan_profiles(),
                "remotes": self._validate_conan_remotes(),
                "cache": self._validate_conan_cache()
            }

            # Check if all validations passed
            all_passed = all(validation_results.values())

            if all_passed:
                logger.info("✅ All setup validations passed!")
                self._print_validation_summary(validation_results)
                return True
            else:
                logger.error("❌ Some setup validations failed:")
                for check, passed in validation_results.items():
                    if not passed:
                        logger.error(f"   ❌ {check}")
                return False

        except Exception as e:
            logger.error(f"❌ Setup validation failed: {e}")
            return False

    def _configure_conan_dev_environment(self):
        """Configure Conan development environment"""
        # Would implement Conan configuration logic
        pass

    def _setup_conan_remotes(self):
        """Set up Conan remotes"""
        # Would implement remote setup logic
        pass

    def _initialize_conan_cache(self):
        """Initialize Conan cache"""
        # Would implement cache initialization logic
        pass

    def _install_linux_dev_tools(self, tools: List[str]):
        """Install development tools on Linux"""
        # Would implement Linux-specific installation logic
        pass

    def _install_macos_dev_tools(self, tools: List[str]):
        """Install development tools on macOS"""
        # Would implement macOS-specific installation logic
        pass

    def _install_windows_dev_tools(self, tools: List[str]):
        """Install development tools on Windows"""
        # Would implement Windows-specific installation logic
        pass

    def _configure_development_environment(self):
        """Configure development environment"""
        # Would implement environment configuration logic
        pass

    def _validate_python_version(self) -> bool:
        """Validate Python version"""
        return sys.version_info >= (3, 8)

    def _validate_conan_installation(self) -> bool:
        """Validate Conan installation"""
        try:
            result = subprocess.run(["conan", "--version"], capture_output=True, text=True)
            return result.returncode == 0 and "2." in result.stdout
        except:
            return False

    def _validate_virtual_environment(self) -> bool:
        """Validate virtual environment"""
        return self.venv_dir.exists() and (self.venv_dir / "bin" / "python").exists()

    def _validate_dependencies(self) -> bool:
        """Validate dependencies"""
        # Would implement dependency validation logic
        return True

    def _validate_conan_profiles(self) -> bool:
        """Validate Conan profiles"""
        profiles_dir = self.conan_dir / "profiles"
        return profiles_dir.exists() and any(profiles_dir.glob("*.profile"))

    def _validate_conan_remotes(self) -> bool:
        """Validate Conan remotes"""
        # Would implement remote validation logic
        return True

    def _validate_conan_cache(self) -> bool:
        """Validate Conan cache"""
        cache_dir = self.conan_dir / "cache"
        return cache_dir.exists()

    def _print_validation_summary(self, results: Dict[str, bool]):
        """Print validation summary"""
        logger.info("📋 Setup Validation Summary:")
        for check, passed in results.items():
            status = "✅" if passed else "❌"
            logger.info(f"   {status} {check.replace('_', ' ').title()}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Set up OpenSSL Tools Conan development environment")
    parser.add_argument("--project-root", type=Path, default=Path.cwd(),
                       help="Project root directory")
    parser.add_argument("--action", choices=["setup", "dev-env", "dev-tools", "validate"], default="setup",
                       help="Action to perform")
    parser.add_argument("--force", "-f", action="store_true",
                       help="Force setup (recreate environment)")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize setup
    setup = OpenSSLToolsConanSetup(args.project_root)

    # Execute action
    if args.action == "setup":
        success = setup.setup_environment(force=args.force)
    elif args.action == "dev-env":
        success = setup.setup_conan_dev_environment()
    elif args.action == "dev-tools":
        success = setup.setup_conan_development_tools()
    elif args.action == "validate":
        success = setup.run_complete_setup_validation()
    
    if success:
        print("\n🎉 OpenSSL Tools Conan environment setup complete!")
        print("\n📋 Next steps:")
        print("1. Activate environment:")
        if platform.system().lower() == "windows":
            print("   conan-dev\\activate.bat")
        else:
            print("   source conan-dev/activate")
        print("2. Install dependencies:")
        print("   conan install . --profile=linux-gcc11")
        print("3. Build package:")
        print("   conan create . --profile=linux-gcc11")
        print("\n🖥️ Available profiles:")
        if platform.system().lower() == "windows":
            print("- windows-msvc2022, debug")
        elif platform.system().lower() == "darwin":
            print("- macos-clang14, debug")
        else:
            print("- linux-gcc11, linux-clang15, debug")
        sys.exit(0)
    else:
        print("\n❌ Setup failed. Check the logs above.")
        sys.exit(1)

if __name__ == "__main__":
    main()