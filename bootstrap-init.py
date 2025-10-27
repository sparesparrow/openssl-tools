#!/usr/bin/env python3
"""
OpenSSL Tools Bootstrap Initialization Script

This script validates and sets up the OpenSSL Tools environment with bundled Python 3.12.3
from Conan cache, providing cross-platform compatibility for development workflows.
"""

import os
import sys
import subprocess
import argparse
import shutil
from pathlib import Path

class OpenSSLToolsBootstrap:
    def __init__(self, args):
        self.args = args
        self.tools_root = Path(args.tools_path or Path.cwd()).resolve()
        self.conan_cache_dir = Path.home() / ".conan2"

    def run_command(self, cmd, cwd=None, check=True, capture_output=False):
        """Run a command and return the result."""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=cwd or self.tools_root,
                check=check,
                capture_output=capture_output,
                text=True
            )
            return result
        except subprocess.CalledProcessError as e:
            print(f"Command failed: {cmd}")
            print(f"Error: {e}")
            if e.stdout:
                print(f"stdout: {e.stdout}")
            if e.stderr:
                print(f"stderr: {e.stderr}")
            if check:
                sys.exit(1)
            return e

    def validate_conan_installation(self):
        """Validate Conan installation and version."""
        print("🔧 Validating Conan installation...")

        try:
            result = self.run_command("conan --version", capture_output=True)
            version_line = result.stdout.strip().split('\n')[0]
            print(f"✅ Conan found: {version_line}")

            # Check if version is 2.x
            if "2." not in version_line:
                print("⚠️  Warning: Conan 2.x recommended for best compatibility")
            return True
        except:
            print("❌ Conan not found in PATH")
            print("Please install Conan 2.x from https://conan.io/")
            return False

    def check_bundled_python(self):
        """Check if bundled Python is available in Conan cache."""
        print("🐍 Checking bundled Python 3.12.3...")

        try:
            # Check if python/3.12.3 is in cache
            result = self.run_command("conan cache path python/3.12.3", capture_output=True)
            python_path = Path(result.stdout.strip())
            python_exe = python_path / "bin" / "python"

            if not python_exe.exists():
                # Try alternative executable names
                python_exe = python_path / "bin" / "python3"
                if not python_exe.exists():
                    python_exe = python_path / "python.exe"
                    if not python_exe.exists():
                        python_exe = python_path / "python3.exe"

            if python_exe.exists():
                print(f"✅ Bundled Python found: {python_exe}")
                return python_exe
            else:
                print(f"❌ Python executable not found in {python_path}")
                return None
        except:
            print("❌ Bundled Python 3.12.3 not found in Conan cache")
            print("Run 'conan install python/3.12.3 --build=missing' to install it")
            return None

    def validate_openssl_tools_package(self):
        """Validate OpenSSL Tools package installation."""
        print("🔍 Validating OpenSSL Tools package...")

        try:
            # Check if openssl-tools/2.2.3 is available
            result = self.run_command("conan cache path openssl-tools/2.2.3", capture_output=True)
            tools_path = Path(result.stdout.strip())

            if tools_path.exists():
                print(f"✅ OpenSSL Tools package found: {tools_path}")

                # Check for wrapper scripts
                bin_dir = tools_path / "bin"
                unix_wrapper = bin_dir / "openssl-tools"
                windows_wrapper = bin_dir / "openssl-tools.bat"

                if unix_wrapper.exists() or windows_wrapper.exists():
                    print("✅ Wrapper scripts found")
                else:
                    print("⚠️  Warning: Wrapper scripts not found")

                return tools_path
            else:
                print("❌ OpenSSL Tools package not found in cache")
                return None
        except:
            print("❌ OpenSSL Tools package not found")
            print("Run 'conan create . --version=2.2.3 --build=missing' to build it")
            return None

    def test_python_environment(self, python_exe):
        """Test the bundled Python environment."""
        print("🧪 Testing Python environment...")

        try:
            # Test basic Python execution
            result = self.run_command(f'"{python_exe}" --version', capture_output=True)
            print(f"✅ Python version: {result.stdout.strip()}")

            # Test pip availability
            result = self.run_command(f'"{python_exe}" -m pip --version', capture_output=True, check=False)
            if result.returncode == 0:
                print(f"✅ Pip available: {result.stdout.strip().split()[0]}")
            else:
                print("⚠️  Warning: pip not available")

            # Test basic import
            test_script = f'''
import sys
import os
print(f"Python executable: {{sys.executable}}")
print(f"Python path: {{sys.path[:3]}}...")
'''
            result = self.run_command(f'"{python_exe}" -c "{test_script}"', capture_output=True)
            print("✅ Basic Python functionality verified")

            return True
        except Exception as e:
            print(f"❌ Python environment test failed: {e}")
            return False

    def create_environment_script(self, python_exe, tools_path):
        """Create an environment activation script."""
        print("📝 Creating environment activation script...")

        env_script = f'''#!/usr/bin/env python3
"""
OpenSSL Tools Environment Activation Script
Generated by bootstrap-init.py

This script sets up the environment for OpenSSL Tools with bundled Python 3.12.3.
"""

import os
import sys
from pathlib import Path

def setup_environment():
    """Set up OpenSSL Tools environment with bundled Python."""

    python_exe = Path("{python_exe}")
    tools_path = Path("{tools_path}")

    if not python_exe.exists():
        print(f"Error: Python executable not found at {{python_exe}}")
        return False

    if not tools_path.exists():
        print(f"Error: Tools path not found at {{tools_path}}")
        return False

    # Add Python to PATH
    python_bin_dir = str(python_exe.parent)
    current_path = os.environ.get('PATH', '')
    if python_bin_dir not in current_path:
        os.environ['PATH'] = python_bin_dir + os.pathsep + current_path

    # Add tools bin directory to PATH
    tools_bin_dir = str(tools_path / "bin")
    if tools_bin_dir not in current_path:
        os.environ['PATH'] = tools_bin_dir + os.pathsep + os.environ.get('PATH', '')

    # Set environment variables
    os.environ['PYTHON_APPLICATION'] = str(python_exe)
    os.environ['OPENSSL_TOOLS_ROOT'] = str(tools_path)
    os.environ['OPENSSL_TOOLS_BIN'] = tools_bin_dir
    os.environ['CONAN_USER_HOME'] = str(Path.home() / ".conan2")

    print("✅ OpenSSL Tools environment activated")
    print(f"Python: {{python_exe}}")
    print(f"Tools: {{tools_path}}")
    print(f"Python version: {{sys.version.split()[0]}}")

    return True

if __name__ == "__main__":
    if setup_environment():
        print("\\nOpenSSL Tools environment is ready!")
        print("You can now use 'openssl-tools' command or run Python scripts directly.")
    else:
        print("Failed to set up OpenSSL Tools environment")
        sys.exit(1)
'''

        script_path = self.tools_root / "activate_openssl_tools.py"
        with open(script_path, 'w') as f:
            f.write(env_script)

        # Make executable on Unix
        if os.name != 'nt':
            os.chmod(script_path, 0o755)

        print(f"✅ Environment script created: {script_path}")
        return script_path

    def run(self):
        """Main execution method."""
        print("🚀 OpenSSL Tools Bootstrap Initialization")
        print(f"Tools root: {self.tools_root}")
        print()

        # Validate Conan
        if not self.validate_conan_installation():
            sys.exit(1)

        # Check bundled Python
        python_exe = self.check_bundled_python()
        if not python_exe:
            print("\\n🔧 Installing bundled Python...")
            try:
                self.run_command("conan install python/3.12.3 --build=missing")
                python_exe = self.check_bundled_python()
                if not python_exe:
                    sys.exit(1)
            except:
                print("❌ Failed to install bundled Python")
                sys.exit(1)

        # Validate OpenSSL Tools package
        tools_path = self.validate_openssl_tools_package()
        if not tools_path:
            print("\\n🔧 Building OpenSSL Tools package...")
            try:
                self.run_command("conan create . --version=2.2.3 --build=missing")
                tools_path = self.validate_openssl_tools_package()
                if not tools_path:
                    sys.exit(1)
            except Exception as e:
                print(f"❌ Failed to build OpenSSL Tools package: {e}")
                sys.exit(1)

        # Test Python environment
        if not self.test_python_environment(python_exe):
            print("⚠️  Warning: Python environment tests failed")

        # Create environment script
        env_script = self.create_environment_script(python_exe, tools_path)

        print("\\n🎉 OpenSSL Tools bootstrap complete!")
        print(f"Python executable: {python_exe}")
        print(f"Tools package: {tools_path}")
        print("\\nTo activate the environment in new shells, run:")
        print(f"python {env_script}")
        print("\\nOr use the wrapper scripts directly:")
        print(f"{tools_path}/bin/openssl-tools (Unix)")
        print(f"{tools_path}/bin/openssl-tools.bat (Windows)")


def main():
    parser = argparse.ArgumentParser(
        description="Bootstrap OpenSSL Tools environment with bundled Python 3.12.3"
    )
    parser.add_argument(
        "--tools-path",
        help="Path to OpenSSL Tools directory"
    )

    args = parser.parse_args()

    bootstrap = OpenSSLToolsBootstrap(args)
    bootstrap.run()


if __name__ == "__main__":
    main()