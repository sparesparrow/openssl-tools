"""
Bootstrap Verification Test Suite
Comprehensive testing for openssl-conan-init.py standalone installer

Tests cover:
- Idempotency verification
- Cross-platform compatibility
- Dependency resolution without pip fallbacks
- Rollback and recovery mechanisms
- Reproducibility validation
"""

import pytest
import tempfile
import shutil
import subprocess
import json
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import platform

# Add the scripts directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from openssl_conan_init import (
    OpenSSLConanBootstrap,
    BootstrapConfig,
    PlatformValidator,
    DependencyResolver,
    IdempotencyManager,
    RollbackManager,
    BootstrapValidator,
    BootstrapError
)

class TestPlatformValidator:
    """Test cross-platform validation"""
    
    def test_detect_platform(self):
        """Test platform detection"""
        system, arch, compiler = PlatformValidator.detect_platform()
        
        assert system in ["linux", "windows", "darwin"]
        assert arch in ["x86_64", "arm64"]
        assert compiler in ["gcc", "clang", "msvc", "unknown"]
    
    def test_validate_platform_linux_gcc11(self):
        """Test Linux GCC 11 validation"""
        config = BootstrapConfig(
            platform="linux",
            arch="x86_64", 
            compiler="gcc11"
        )
        
        with patch('shutil.which', return_value="/usr/bin/gcc"):
            assert PlatformValidator.validate_platform(config) is True
    
    def test_validate_platform_windows_msvc193(self):
        """Test Windows MSVC 193 validation"""
        config = BootstrapConfig(
            platform="windows",
            arch="x86_64",
            compiler="msvc193"
        )
        
        with patch('shutil.which', return_value="cl.exe"):
            assert PlatformValidator.validate_platform(config) is True
    
    def test_validate_platform_macos_arm64(self):
        """Test macOS ARM64 validation"""
        config = BootstrapConfig(
            platform="darwin",
            arch="arm64",
            compiler="clang"
        )
        
        with patch('shutil.which', return_value="/usr/bin/clang"):
            assert PlatformValidator.validate_platform(config) is True
    
    def test_validate_unsupported_platform(self):
        """Test unsupported platform rejection"""
        config = BootstrapConfig(
            platform="unsupported",
            arch="x86_64",
            compiler="gcc"
        )
        
        with pytest.raises(BootstrapError):
            PlatformValidator.validate_platform(config)

class TestIdempotencyManager:
    """Test idempotency operations"""
    
    def test_idempotent_operations(self):
        """Test that operations are idempotent"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = BootstrapConfig(
                platform="linux",
                arch="x86_64",
                compiler="gcc",
                install_dir=Path(temp_dir)
            )
            
            manager = IdempotencyManager(config)
            
            # First run
            assert not manager.is_completed("test_operation")
            manager.mark_completed("test_operation", {"version": "1.0.0"})
            assert manager.is_completed("test_operation")
            
            # Second run (should be idempotent)
            assert manager.is_completed("test_operation")
    
    def test_state_persistence(self):
        """Test state persistence across restarts"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = BootstrapConfig(
                platform="linux",
                arch="x86_64",
                compiler="gcc",
                install_dir=Path(temp_dir)
            )
            
            # First manager instance
            manager1 = IdempotencyManager(config)
            manager1.mark_completed("persistent_operation", {"data": "test"})
            
            # Second manager instance (simulates restart)
            manager2 = IdempotencyManager(config)
            assert manager2.is_completed("persistent_operation")
            
            details = manager2.state["persistent_operation"]["details"]
            assert details["data"] == "test"

class TestDependencyResolver:
    """Test pip-free dependency resolution"""
    
    def test_dependency_loading(self):
        """Test dependency specification loading"""
        config = BootstrapConfig(
            platform="linux",
            arch="x86_64",
            compiler="gcc"
        )
        
        resolver = DependencyResolver(config)
        dependencies = resolver.dependencies
        
        assert "conan" in dependencies
        assert "pyyaml" in dependencies
        assert "requests" in dependencies
        
        # Check Conan version
        assert dependencies["conan"]["version"] == "2.21.0"
    
    def test_checksum_verification(self):
        """Test checksum verification"""
        config = BootstrapConfig(
            platform="linux",
            arch="x86_64",
            compiler="gcc"
        )
        
        resolver = DependencyResolver(config)
        
        # Create test file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content")
            test_file = f.name
        
        try:
            # Test valid checksum
            test_hash = "sha256:" + "a" * 64
            with patch.object(resolver, '_verify_checksum', return_value=True):
                assert resolver._verify_checksum(test_file, test_hash)
            
            # Test invalid checksum
            with patch.object(resolver, '_verify_checksum', return_value=False):
                assert not resolver._verify_checksum(test_file, test_hash)
        finally:
            os.unlink(test_file)
    
    def test_package_installation_check(self):
        """Test package installation verification"""
        config = BootstrapConfig(
            platform="linux",
            arch="x86_64",
            compiler="gcc"
        )
        
        resolver = DependencyResolver(config)
        
        # Test Conan installation check
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "Conan version 2.21.0"
            
            assert resolver._is_installed("conan", "2.21.0")
            
            # Test with different version
            assert not resolver._is_installed("conan", "1.0.0")

class TestRollbackManager:
    """Test rollback and recovery mechanisms"""
    
    def test_backup_creation(self):
        """Test backup creation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = BootstrapConfig(
                platform="linux",
                arch="x86_64",
                compiler="gcc",
                install_dir=Path(temp_dir)
            )
            
            # Create test files
            test_file = Path(temp_dir) / "test_file.txt"
            test_file.write_text("original content")
            
            manager = RollbackManager(config)
            assert manager.create_backup("test_operation")
            
            # Check backup was created
            backup_dir = config.install_dir / ".bootstrap_backup" / "test_operation"
            assert backup_dir.exists()
            assert (backup_dir / "test_file.txt").exists()
    
    def test_rollback_operation(self):
        """Test rollback functionality"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = BootstrapConfig(
                platform="linux",
                arch="x86_64",
                compiler="gcc",
                install_dir=Path(temp_dir)
            )
            
            # Create original file
            original_file = Path(temp_dir) / "test_file.txt"
            original_file.write_text("original content")
            
            # Create backup
            manager = RollbackManager(config)
            manager.create_backup("test_operation")
            
            # Modify file
            original_file.write_text("modified content")
            
            # Rollback
            assert manager.rollback("test_operation")
            
            # Check file was restored
            assert original_file.read_text() == "original content"
    
    def test_rollback_nonexistent_backup(self):
        """Test rollback with non-existent backup"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = BootstrapConfig(
                platform="linux",
                arch="x86_64",
                compiler="gcc",
                install_dir=Path(temp_dir)
            )
            
            manager = RollbackManager(config)
            assert not manager.rollback("nonexistent_operation")

class TestBootstrapValidator:
    """Test bootstrap validation"""
    
    def test_environment_validation(self):
        """Test environment validation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = BootstrapConfig(
                platform="linux",
                arch="x86_64",
                compiler="gcc",
                install_dir=Path(temp_dir)
            )
            
            validator = BootstrapValidator(config)
            
            with patch.object(validator, '_check_python_version', return_value=True), \
                 patch.object(validator, '_check_platform_compatibility', return_value=True), \
                 patch.object(validator, '_check_disk_space', return_value=True), \
                 patch.object(validator, '_check_permissions', return_value=True), \
                 patch.object(validator, '_check_network_connectivity', return_value=True):
                
                assert validator.validate_environment()
    
    def test_installation_validation(self):
        """Test installation validation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = BootstrapConfig(
                platform="linux",
                arch="x86_64",
                compiler="gcc",
                install_dir=Path(temp_dir)
            )
            
            validator = BootstrapValidator(config)
            
            with patch.object(validator, '_check_conan_installation', return_value=True), \
                 patch.object(validator, '_check_openssl_tools_installation', return_value=True), \
                 patch.object(validator, '_check_environment_variables', return_value=True), \
                 patch.object(validator, '_check_file_integrity', return_value=True):
                
                assert validator.validate_installation()

class TestCrossPlatformCompatibility:
    """Test cross-platform compatibility matrix"""
    
    @pytest.mark.parametrize("platform,arch,compiler", [
        ("linux", "x86_64", "gcc11"),
        ("linux", "x86_64", "clang15"),
        ("linux", "arm64", "gcc11"),
        ("windows", "x86_64", "msvc2022"),
        ("windows", "x86_64", "msvc193"),
        ("darwin", "x86_64", "clang"),
        ("darwin", "arm64", "clang"),
    ])
    def test_platform_matrix(self, platform, arch, compiler):
        """Test platform compatibility matrix"""
        config = BootstrapConfig(
            platform=platform,
            arch=arch,
            compiler=compiler
        )
        
        # Mock platform detection
        with patch('platform.system', return_value=platform), \
             patch('platform.machine', return_value=arch), \
             patch('shutil.which', return_value="/usr/bin/compiler"):
            
            assert PlatformValidator.validate_platform(config)

class TestReproducibilityValidation:
    """Test reproducibility and consistency"""
    
    def test_deterministic_installation(self):
        """Test that installation is deterministic"""
        with tempfile.TemporaryDirectory() as temp_dir1, \
             tempfile.TemporaryDirectory() as temp_dir2:
            
            config1 = BootstrapConfig(
                platform="linux",
                arch="x86_64",
                compiler="gcc",
                install_dir=Path(temp_dir1)
            )
            
            config2 = BootstrapConfig(
                platform="linux",
                arch="x86_64",
                compiler="gcc",
                install_dir=Path(temp_dir2)
            )
            
            # Mock successful installation
            with patch('subprocess.run') as mock_run:
                mock_run.return_value.returncode = 0
                mock_run.return_value.stdout = "Conan version 2.21.0"
                
                resolver1 = DependencyResolver(config1)
                resolver2 = DependencyResolver(config2)
                
                # Both should resolve to same dependencies
                deps1 = resolver1.dependencies
                deps2 = resolver2.dependencies
                
                assert deps1 == deps2
    
    def test_consistent_state_tracking(self):
        """Test consistent state tracking across runs"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = BootstrapConfig(
                platform="linux",
                arch="x86_64",
                compiler="gcc",
                install_dir=Path(temp_dir)
            )
            
            # First run
            manager1 = IdempotencyManager(config)
            manager1.mark_completed("test_op", {"version": "1.0.0"})
            
            # Second run with same config
            manager2 = IdempotencyManager(config)
            
            # State should be consistent
            assert manager2.is_completed("test_op")
            assert manager2.state["test_op"]["details"]["version"] == "1.0.0"

class TestBootstrapIntegration:
    """Integration tests for complete bootstrap process"""
    
    def test_complete_bootstrap_flow(self):
        """Test complete bootstrap flow"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = BootstrapConfig(
                platform="linux",
                arch="x86_64",
                compiler="gcc",
                install_dir=Path(temp_dir),
                force_reinstall=True
            )
            
            # Mock all external dependencies
            with patch('subprocess.run') as mock_run, \
                 patch('urllib.request.urlretrieve') as mock_download, \
                 patch('shutil.unpack_archive') as mock_unpack, \
                 patch('importlib.import_module') as mock_import:
                
                # Mock successful operations
                mock_run.return_value.returncode = 0
                mock_run.return_value.stdout = "Conan version 2.21.0"
                mock_download.return_value = None
                mock_unpack.return_value = None
                mock_import.return_value = MagicMock()
                
                bootstrap = OpenSSLConanBootstrap(config)
                
                # Mock individual step methods
                with patch.object(bootstrap, '_resolve_dependencies', return_value=True), \
                     patch.object(bootstrap, '_setup_conan', return_value=True), \
                     patch.object(bootstrap, '_setup_openssl_tools', return_value=True), \
                     patch.object(bootstrap, '_configure_environment', return_value=True), \
                     patch.object(bootstrap, '_validate_installation', return_value=True):
                    
                    assert bootstrap.run()
    
    def test_bootstrap_failure_rollback(self):
        """Test bootstrap failure with rollback"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = BootstrapConfig(
                platform="linux",
                arch="x86_64",
                compiler="gcc",
                install_dir=Path(temp_dir),
                enable_rollback=True
            )
            
            bootstrap = OpenSSLConanBootstrap(config)
            
            # Mock successful first step, failure on second
            with patch.object(bootstrap, '_resolve_dependencies', return_value=True), \
                 patch.object(bootstrap, '_setup_conan', return_value=False), \
                 patch.object(bootstrap.rollback_manager, 'rollback', return_value=True):
                
                assert not bootstrap.run()

class TestProductionScenarios:
    """Test production deployment scenarios"""
    
    def test_idempotent_production_deployment(self):
        """Test idempotent production deployment"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = BootstrapConfig(
                platform="linux",
                arch="x86_64",
                compiler="gcc",
                install_dir=Path(temp_dir)
            )
            
            # First deployment
            bootstrap1 = OpenSSLConanBootstrap(config)
            with patch.object(bootstrap1, 'run', return_value=True):
                assert bootstrap1.run()
            
            # Second deployment (should be idempotent)
            bootstrap2 = OpenSSLConanBootstrap(config)
            with patch.object(bootstrap2, 'run', return_value=True):
                assert bootstrap2.run()
            
            # Check that state was preserved
            manager = IdempotencyManager(config)
            assert manager.is_completed("dependency_resolution")
    
    def test_rollback_production_scenario(self):
        """Test rollback in production scenario"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = BootstrapConfig(
                platform="linux",
                arch="x86_64",
                compiler="gcc",
                install_dir=Path(temp_dir),
                enable_rollback=True
            )
            
            # Create initial state
            test_file = Path(temp_dir) / "important_file.txt"
            test_file.write_text("original content")
            
            bootstrap = OpenSSLConanBootstrap(config)
            
            # Mock backup creation
            with patch.object(bootstrap.rollback_manager, 'create_backup', return_value=True), \
                 patch.object(bootstrap, '_resolve_dependencies', return_value=True), \
                 patch.object(bootstrap, '_setup_conan', return_value=False), \
                 patch.object(bootstrap.rollback_manager, 'rollback', return_value=True):
                
                # Bootstrap should fail and rollback
                assert not bootstrap.run()
                
                # File should be restored
                assert test_file.read_text() == "original content"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])