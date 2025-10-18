"""
Conftest for Conan Extensions Testing
Provides common fixtures and setup for testing Conan extensions in OpenSSL workspace.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
import subprocess
import os


@pytest.fixture(scope="session")
def temp_workspace():
    """Create a temporary workspace for testing extensions."""
    temp_dir = tempfile.mkdtemp(prefix="openssl_extensions_test_")
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="session")
def mock_conan_client():
    """Mock Conan client for testing."""
    with patch('conans.client.conan_api.ConanAPIV2') as mock_client:
        yield mock_client


@pytest.fixture
def mock_subprocess():
    """Mock subprocess calls for testing external commands."""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
        yield mock_run


@pytest.fixture
def sample_conanfile():
    """Sample conanfile.py content for testing."""
    return """
from conan import ConanFile

class OpenSSLBaseConan(ConanFile):
    name = "openssl-base"
    version = "3.0.0"
    settings = "os", "compiler", "build_type", "arch"

    def configure(self):
        pass

    def requirements(self):
        pass

    def package_info(self):
        pass
"""


@pytest.fixture
def mock_fips_config():
    """Mock FIPS configuration for testing."""
    return {
        "module_path": "/path/to/fips.so",
        "config_path": "/path/to/fipsmodule.cnf",
        "install_path": "/path/to/install"
    }


@pytest.fixture(autouse=True)
def mock_environment():
    """Mock environment variables for consistent testing."""
    env_vars = {
        "CONAN_USER_HOME": "/tmp/conan_home",
        "OPENSSL_MODULES": "/tmp/openssl_modules",
        "OPENSSL_CONF": "/tmp/openssl.conf",
        "PYTHONPATH": "/tmp/pythonpath"
    }

    with patch.dict(os.environ, env_vars, clear=False):
        yield


@pytest.fixture
def performance_timer():
    """Performance timing fixture for benchmarking."""
    import time
    start_time = time.time()
    yield lambda: time.time() - start_time


class ExtensionTestHelper:
    """Helper class for extension testing utilities."""

    @staticmethod
    def run_conan_command(command, cwd=None, env=None):
        """Run a Conan command and return the result."""
        cmd = ["conan"] + command.split()
        result = subprocess.run(
            cmd,
            cwd=cwd,
            env=env,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result

    @staticmethod
    def create_test_conanfile(path, name="test-package", version="1.0"):
        """Create a test conanfile.py at the given path."""
        conanfile_content = f"""
from conan import ConanFile

class TestPackageConan(ConanFile):
    name = "{name}"
    version = "{version}"
    settings = "os", "compiler", "build_type", "arch"

    def configure(self):
        pass

    def requirements(self):
        pass

    def package_info(self):
        pass
"""
        Path(path).write_text(conanfile_content)

    @staticmethod
    def assert_command_success(result, expected_output=None):
        """Assert that a command executed successfully."""
        assert result.returncode == 0, f"Command failed: {result.stderr}"
        if expected_output:
            assert expected_output in result.stdout, f"Expected '{expected_output}' in output"

    @staticmethod
    def assert_command_failure(result, expected_error=None):
        """Assert that a command failed as expected."""
        assert result.returncode != 0, "Command should have failed"
        if expected_error:
            assert expected_error in result.stderr, f"Expected '{expected_error}' in error"


@pytest.fixture
def test_helper():
    """Extension test helper fixture."""
    return ExtensionTestHelper()

