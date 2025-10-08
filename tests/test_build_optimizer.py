#!/usr/bin/env python3
"""
Tests for build cache management and optimization.
"""

import pytest
import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from build_optimizer import BuildCacheManager, BuildOptimizer, BuildInfo


class TestBuildCacheManager:
    """Test cases for BuildCacheManager."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.cache_dir = Path(self.temp_dir) / "test-cache"
        self.cache_manager = BuildCacheManager(
            cache_dir=self.cache_dir,
            max_cache_size_gb=1
        )
        
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
        
    def test_init(self):
        """Test BuildCacheManager initialization."""
        assert self.cache_manager.cache_dir == self.cache_dir
        assert self.cache_manager.max_cache_size_gb == 1
        assert self.cache_manager.index_file == self.cache_dir / "build_index.json"
        assert self.cache_manager.stats_file == self.cache_dir / "cache_stats.json"
        assert self.cache_dir.exists()
        
    def test_calculate_build_hash(self):
        """Test build hash calculation."""
        # Create test files
        test_file1 = self.temp_dir / "test1.c"
        test_file2 = self.temp_dir / "test2.c"
        
        test_file1.write_text("int main() { return 0; }")
        test_file2.write_text("int helper() { return 1; }")
        
        build_options = {"debug": True, "optimize": False}
        dependencies = ["openssl", "crypto"]
        compiler_info = {"gcc": "11.0"}
        
        hash1 = self.cache_manager.calculate_build_hash(
            [test_file1, test_file2],
            build_options,
            dependencies,
            compiler_info
        )
        
        # Same inputs should produce same hash
        hash2 = self.cache_manager.calculate_build_hash(
            [test_file1, test_file2],
            build_options,
            dependencies,
            compiler_info
        )
        
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA256 hex length
        
        # Different inputs should produce different hashes
        different_options = {"debug": False, "optimize": True}
        hash3 = self.cache_manager.calculate_build_hash(
            [test_file1, test_file2],
            different_options,
            dependencies,
            compiler_info
        )
        
        assert hash1 != hash3
        
    def test_get_cached_artifacts_cache_hit(self):
        """Test cache hit scenario."""
        # Create mock cache entry
        build_hash = "test_hash_123"
        cache_path = self.cache_dir / build_hash
        cache_path.mkdir(parents=True)
        
        # Create mock artifact
        artifact_file = cache_path / "test_artifact.o"
        artifact_file.write_text("mock object file")
        
        # Add to index
        self.cache_manager.build_index[build_hash] = {
            "created_at": datetime.now().isoformat(),
            "last_accessed": datetime.now().isoformat(),
            "size_bytes": 100
        }
        
        # Test cache hit
        result = self.cache_manager.get_cached_artifacts(build_hash)
        assert result == cache_path
        
        # Verify access time was updated
        assert "last_accessed" in self.cache_manager.build_index[build_hash]
        
    def test_get_cached_artifacts_cache_miss(self):
        """Test cache miss scenario."""
        build_hash = "nonexistent_hash"
        
        result = self.cache_manager.get_cached_artifacts(build_hash)
        assert result is None
        
    def test_store_artifacts(self):
        """Test storing artifacts in cache."""
        # Create source artifacts
        artifacts_path = Path(self.temp_dir) / "artifacts"
        artifacts_path.mkdir()
        
        artifact_file = artifacts_path / "test.o"
        artifact_file.write_text("object file content")
        
        # Create build info
        build_info = BuildInfo(
            source_files=["test.c"],
            build_options={"debug": True},
            dependencies=["openssl"],
            compiler="gcc",
            compiler_version="11.0",
            target_arch="x86_64",
            build_type="Debug",
            timestamp=datetime.now(),
            build_hash="test_hash",
            artifacts_path="",
            build_time=10.5,
            success=True
        )
        
        build_hash = "test_hash"
        
        # Store artifacts
        result = self.cache_manager.store_artifacts(build_hash, artifacts_path, build_info)
        assert result is True
        
        # Verify artifacts were stored
        cache_path = self.cache_dir / build_hash
        assert cache_path.exists()
        assert (cache_path / "test.o").exists()
        
        # Verify index was updated
        assert build_hash in self.cache_manager.build_index
        
    def test_get_directory_size(self):
        """Test directory size calculation."""
        # Create test directory with files
        test_dir = Path(self.temp_dir) / "size_test"
        test_dir.mkdir()
        
        # Create files with known sizes
        file1 = test_dir / "file1.txt"
        file1.write_text("12345")  # 5 bytes
        
        file2 = test_dir / "file2.txt"
        file2.write_text("1234567890")  # 10 bytes
        
        subdir = test_dir / "subdir"
        subdir.mkdir()
        file3 = subdir / "file3.txt"
        file3.write_text("123")  # 3 bytes
        
        total_size = self.cache_manager._get_directory_size(test_dir)
        assert total_size == 18  # 5 + 10 + 3
        
    def test_list_cached_builds(self):
        """Test listing cached builds."""
        # Add mock builds to index
        self.cache_manager.build_index = {
            "hash1": {
                "build_info": {
                    "build_time": 10.5,
                    "success": True
                },
                "created_at": "2024-01-01T00:00:00",
                "last_accessed": "2024-01-01T12:00:00",
                "size_bytes": 1000
            },
            "hash2": {
                "build_info": {
                    "build_time": 5.2,
                    "success": False
                },
                "created_at": "2024-01-02T00:00:00",
                "last_accessed": "2024-01-02T12:00:00",
                "size_bytes": 500
            }
        }
        
        builds = self.cache_manager.list_cached_builds()
        
        assert len(builds) == 2
        assert builds[0]["hash"] == "hash2"  # More recent
        assert builds[1]["hash"] == "hash1"
        assert builds[0]["size_bytes"] == 500
        assert builds[0]["success"] is False
        
    def test_get_cache_stats(self):
        """Test cache statistics."""
        # Set up mock stats
        self.cache_manager.cache_stats = {
            "cache_hits": 10,
            "cache_misses": 5,
            "total_builds": 15
        }
        
        # Create mock cache directory
        cache_path = self.cache_dir / "test_build"
        cache_path.mkdir()
        test_file = cache_path / "test.o"
        test_file.write_text("test content")
        
        stats = self.cache_manager.get_cache_stats()
        
        assert stats["cache_hits"] == 10
        assert stats["cache_misses"] == 5
        assert stats["hit_rate"] == 10 / 15  # 10 / (10 + 5)
        assert stats["total_builds"] == 15
        assert stats["cached_builds"] == 0  # No builds in index
        
    def test_clear_cache(self):
        """Test cache clearing."""
        # Create mock cache entries
        build_hash1 = "hash1"
        build_hash2 = "hash2"
        
        cache_path1 = self.cache_dir / build_hash1
        cache_path2 = self.cache_dir / build_hash2
        
        cache_path1.mkdir()
        cache_path2.mkdir()
        
        (cache_path1 / "file1.o").write_text("content1")
        (cache_path2 / "file2.o").write_text("content2")
        
        # Add to index
        self.cache_manager.build_index = {
            build_hash1: {
                "created_at": (datetime.now() - timedelta(days=10)).isoformat(),
                "size_bytes": 100
            },
            build_hash2: {
                "created_at": (datetime.now() - timedelta(days=5)).isoformat(),
                "size_bytes": 200
            }
        }
        
        # Clear entries older than 7 days
        cleared = self.cache_manager.clear_cache(older_than_days=7)
        assert cleared == 1  # Only hash1 should be cleared
        
        # Verify hash1 was removed
        assert build_hash1 not in self.cache_manager.build_index
        assert not cache_path1.exists()
        
        # Verify hash2 still exists
        assert build_hash2 in self.cache_manager.build_index
        assert cache_path2.exists()
        
    def test_clear_all_cache(self):
        """Test clearing all cache entries."""
        # Create mock cache entries
        build_hash = "test_hash"
        cache_path = self.cache_dir / build_hash
        cache_path.mkdir()
        (cache_path / "file.o").write_text("content")
        
        self.cache_manager.build_index = {
            build_hash: {
                "created_at": datetime.now().isoformat(),
                "size_bytes": 100
            }
        }
        
        # Clear all
        cleared = self.cache_manager.clear_cache()
        assert cleared == 1
        
        # Verify everything was cleared
        assert build_hash not in self.cache_manager.build_index
        assert not cache_path.exists()


class TestBuildOptimizer:
    """Test cases for BuildOptimizer."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.cache_dir = Path(self.temp_dir) / "test-cache"
        self.cache_manager = BuildCacheManager(cache_dir=self.cache_dir)
        self.optimizer = BuildOptimizer(self.cache_manager)
        
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
        
    def test_init(self):
        """Test BuildOptimizer initialization."""
        assert self.optimizer.cache_manager == self.cache_manager
        
    def test_optimize_build_command(self):
        """Test build command optimization."""
        base_command = ["make", "all"]
        source_files = [Path("test.c")]
        build_options = {"build_type": "Release"}
        
        optimized = self.optimizer.optimize_build_command(
            base_command, source_files, build_options
        )
        
        # Should add parallel make option
        assert "-j" in optimized
        assert any(str(cpu_count) in optimized for cpu_count in [1, 2, 4, 8, 16])
        
        # Should add optimization flags for Release
        assert "-O3" in optimized
        assert "-DNDEBUG" in optimized
        
    def test_should_use_cache(self):
        """Test cache usage decision."""
        build_hash = "test_hash"
        
        # Force rebuild should not use cache
        assert not self.optimizer.should_use_cache(build_hash, force_rebuild=True)
        
        # Without force rebuild, depends on cache availability
        with patch.object(self.cache_manager, 'get_cached_artifacts') as mock_get:
            mock_get.return_value = None
            assert not self.optimizer.should_use_cache(build_hash, force_rebuild=False)
            
            mock_get.return_value = Path("/some/cache/path")
            assert self.optimizer.should_use_cache(build_hash, force_rebuild=False)
            
    def test_get_build_dependencies(self):
        """Test build dependency extraction."""
        # Create test C file with includes
        test_file = Path(self.temp_dir) / "test.c"
        test_file.write_text("""
        #include <stdio.h>
        #include <openssl/ssl.h>
        #include "local_header.h"
        #include <crypto/evp.h>
        
        int main() {
            return 0;
        }
        """)
        
        dependencies = self.optimizer.get_build_dependencies([test_file])
        
        # Should extract system and library dependencies
        assert "openssl" in dependencies
        assert "crypto" in dependencies
        assert "stdio" in dependencies
        assert "local_header" in dependencies


@pytest.mark.integration
class TestBuildOptimizerIntegration:
    """Integration tests for build optimization."""
    
    def setup_method(self):
        """Set up integration test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """Clean up integration test fixtures."""
        shutil.rmtree(self.temp_dir)
        
    @pytest.mark.slow
    def test_full_cache_workflow(self):
        """Test complete cache workflow."""
        cache_dir = Path(self.temp_dir) / "integration-cache"
        cache_manager = BuildCacheManager(cache_dir=cache_dir)
        
        # Create test source files
        source_dir = Path(self.temp_dir) / "source"
        source_dir.mkdir()
        
        source_file = source_dir / "test.c"
        source_file.write_text("int main() { return 0; }")
        
        # Create test artifacts
        artifacts_dir = Path(self.temp_dir) / "artifacts"
        artifacts_dir.mkdir()
        
        artifact_file = artifacts_dir / "test.o"
        artifact_file.write_text("object file content")
        
        # Calculate build hash
        build_hash = cache_manager.calculate_build_hash(
            [source_file],
            {"debug": True},
            ["openssl"]
        )
        
        # Create build info
        build_info = BuildInfo(
            source_files=[str(source_file)],
            build_options={"debug": True},
            dependencies=["openssl"],
            compiler="gcc",
            compiler_version="11.0",
            target_arch="x86_64",
            build_type="Debug",
            timestamp=datetime.now(),
            build_hash=build_hash,
            artifacts_path="",
            build_time=5.0,
            success=True
        )
        
        # Store artifacts
        result = cache_manager.store_artifacts(build_hash, artifacts_dir, build_info)
        assert result is True
        
        # Retrieve artifacts
        cached_path = cache_manager.get_cached_artifacts(build_hash)
        assert cached_path is not None
        assert (cached_path / "test.o").exists()
        
        # Verify cache stats
        stats = cache_manager.get_cache_stats()
        assert stats["cache_hits"] == 1
        assert stats["total_builds"] == 1