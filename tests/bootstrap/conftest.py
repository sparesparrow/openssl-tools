"""
Bootstrap Test Configuration
Shared fixtures and utilities for bootstrap verification tests
"""

import pytest
import tempfile
import shutil
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

@pytest.fixture
def temp_workspace():
    """Create temporary workspace for tests"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)

@pytest.fixture
def mock_platform_linux():
    """Mock Linux platform detection"""
    with patch('platform.system', return_value='linux'), \
         patch('platform.machine', return_value='x86_64'), \
         patch('shutil.which', return_value='/usr/bin/gcc'):
        yield

@pytest.fixture
def mock_platform_windows():
    """Mock Windows platform detection"""
    with patch('platform.system', return_value='windows'), \
         patch('platform.machine', return_value='x86_64'), \
         patch('shutil.which', return_value='cl.exe'):
        yield

@pytest.fixture
def mock_platform_macos():
    """Mock macOS platform detection"""
    with patch('platform.system', return_value='darwin'), \
         patch('platform.machine', return_value='arm64'), \
         patch('shutil.which', return_value='/usr/bin/clang'):
        yield

@pytest.fixture
def mock_subprocess_success():
    """Mock successful subprocess calls"""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "Conan version 2.21.0"
        mock_run.return_value.stderr = ""
        yield mock_run

@pytest.fixture
def mock_subprocess_failure():
    """Mock failed subprocess calls"""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value.returncode = 1
        mock_run.return_value.stdout = ""
        mock_run.return_value.stderr = "Command failed"
        yield mock_run

@pytest.fixture
def mock_urllib_download():
    """Mock urllib download operations"""
    with patch('urllib.request.urlretrieve') as mock_download:
        mock_download.return_value = None
        yield mock_download

@pytest.fixture
def mock_file_operations():
    """Mock file operations"""
    with patch('shutil.unpack_archive') as mock_unpack, \
         patch('shutil.copy2') as mock_copy, \
         patch('shutil.copytree') as mock_copytree:
        mock_unpack.return_value = None
        mock_copy.return_value = None
        mock_copytree.return_value = None
        yield {
            'unpack': mock_unpack,
            'copy': mock_copy,
            'copytree': mock_copytree
        }

@pytest.fixture
def mock_import_success():
    """Mock successful module imports"""
    with patch('importlib.import_module') as mock_import:
        mock_module = MagicMock()
        mock_module.__version__ = "1.0.0"
        mock_import.return_value = mock_module
        yield mock_import

@pytest.fixture
def bootstrap_config_linux(temp_workspace):
    """Linux bootstrap configuration for testing"""
    from openssl_conan_init import BootstrapConfig
    return BootstrapConfig(
        platform="linux",
        arch="x86_64",
        compiler="gcc",
        install_dir=temp_workspace,
        force_reinstall=True
    )

@pytest.fixture
def bootstrap_config_windows(temp_workspace):
    """Windows bootstrap configuration for testing"""
    from openssl_conan_init import BootstrapConfig
    return BootstrapConfig(
        platform="windows",
        arch="x86_64",
        compiler="msvc193",
        install_dir=temp_workspace,
        force_reinstall=True
    )

@pytest.fixture
def bootstrap_config_macos(temp_workspace):
    """macOS bootstrap configuration for testing"""
    from openssl_conan_init import BootstrapConfig
    return BootstrapConfig(
        platform="darwin",
        arch="arm64",
        compiler="clang",
        install_dir=temp_workspace,
        force_reinstall=True
    )

@pytest.fixture
def test_files(temp_workspace):
    """Create test files for testing"""
    files = {
        'conanfile.py': temp_workspace / 'conanfile.py',
        'pyproject.toml': temp_workspace / 'pyproject.toml',
        'test_file.txt': temp_workspace / 'test_file.txt'
    }
    
    # Create test files
    files['conanfile.py'].write_text('from conan import ConanFile\nclass Test(ConanFile): pass')
    files['pyproject.toml'].write_text('[project]\nname = "test"')
    files['test_file.txt'].write_text('test content')
    
    return files

@pytest.fixture
def mock_environment():
    """Mock environment variables"""
    with patch.dict(os.environ, {
        'CONAN_USER_HOME': '/tmp/.conan2',
        'OPENSSL_TOOLS_ROOT': '/tmp/openssl-tools',
        'PATH': '/usr/bin:/bin'
    }):
        yield

@pytest.fixture(autouse=True)
def cleanup_temp_files():
    """Cleanup temporary files after each test"""
    yield
    # Cleanup logic if needed
    pass

# Test markers
pytestmark = [
    pytest.mark.bootstrap,
    pytest.mark.verification
]

# Platform-specific test markers
linux_only = pytest.mark.skipif(
    platform.system() != 'Linux',
    reason="Linux-specific test"
)

windows_only = pytest.mark.skipif(
    platform.system() != 'Windows',
    reason="Windows-specific test"
)

macos_only = pytest.mark.skipif(
    platform.system() != 'Darwin',
    reason="macOS-specific test"
)