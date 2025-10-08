#!/usr/bin/env python3
"""
Build Cache Management for OpenSSL Tools
Implements intelligent caching and artifact reuse for build optimization
"""

import os
import sys
import hashlib
import json
import shutil
import logging
from typing import Dict, Any, List, Optional, Set
from pathlib import Path
import time
import subprocess
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class BuildArtifact:
    """Represents a build artifact with metadata"""
    path: str
    hash: str
    size: int
    created: datetime
    last_accessed: datetime
    build_id: str
    dependencies: List[str]
    platform: str
    arch: str


@dataclass
class BuildCache:
    """Build cache metadata"""
    cache_dir: str
    max_size: int
    max_age_days: int
    artifacts: Dict[str, BuildArtifact]
    last_cleanup: datetime


class BuildCacheManager:
    """Manages build artifacts and caching for optimal performance"""
    
    def __init__(self, cache_dir: str = None, max_size_gb: int = 10, max_age_days: int = 30):
        """Initialize build cache manager"""
        self.cache_dir = cache_dir or os.path.join(os.path.expanduser("~"), ".openssl-tools-cache")
        self.max_size = max_size_gb * 1024 * 1024 * 1024  # Convert to bytes
        self.max_age_days = max_age_days
        self.cache_metadata_file = os.path.join(self.cache_dir, "cache_metadata.json")
        
        # Ensure cache directory exists
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Load existing cache metadata
        self.cache = self._load_cache_metadata()
    
    def _load_cache_metadata(self) -> BuildCache:
        """Load cache metadata from file"""
        if os.path.exists(self.cache_metadata_file):
            try:
                with open(self.cache_metadata_file, 'r') as f:
                    data = json.load(f)
                
                # Convert artifacts back to BuildArtifact objects
                artifacts = {}
                for key, artifact_data in data.get('artifacts', {}).items():
                    artifact_data['created'] = datetime.fromisoformat(artifact_data['created'])
                    artifact_data['last_accessed'] = datetime.fromisoformat(artifact_data['last_accessed'])
                    artifacts[key] = BuildArtifact(**artifact_data)
                
                return BuildCache(
                    cache_dir=data.get('cache_dir', self.cache_dir),
                    max_size=data.get('max_size', self.max_size),
                    max_age_days=data.get('max_age_days', self.max_age_days),
                    artifacts=artifacts,
                    last_cleanup=datetime.fromisoformat(data.get('last_cleanup', datetime.now().isoformat()))
                )
            except Exception as e:
                logger.warning(f"Failed to load cache metadata: {e}")
        
        return BuildCache(
            cache_dir=self.cache_dir,
            max_size=self.max_size,
            max_age_days=self.max_age_days,
            artifacts={},
            last_cleanup=datetime.now()
        )
    
    def _save_cache_metadata(self):
        """Save cache metadata to file"""
        try:
            data = {
                'cache_dir': self.cache.cache_dir,
                'max_size': self.cache.max_size,
                'max_age_days': self.cache.max_age_days,
                'artifacts': {k: asdict(v) for k, v in self.cache.artifacts.items()},
                'last_cleanup': self.cache.last_cleanup.isoformat()
            }
            
            with open(self.cache_metadata_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save cache metadata: {e}")
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of a file"""
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            logger.error(f"Failed to calculate hash for {file_path}: {e}")
            return ""
    
    def _get_platform_info(self) -> tuple:
        """Get platform and architecture information"""
        import platform
        return platform.system().lower(), platform.machine().lower()
    
    def _generate_build_id(self, source_files: List[str], build_config: Dict[str, Any]) -> str:
        """Generate unique build ID based on source files and configuration"""
        # Create hash from source file hashes and build configuration
        combined_hash = hashlib.sha256()
        
        # Add source file hashes
        for file_path in source_files:
            if os.path.exists(file_path):
                file_hash = self._calculate_file_hash(file_path)
                combined_hash.update(file_hash.encode())
        
        # Add build configuration
        config_str = json.dumps(build_config, sort_keys=True)
        combined_hash.update(config_str.encode())
        
        return combined_hash.hexdigest()[:16]
    
    def store_artifact(self, source_path: str, build_id: str, dependencies: List[str] = None) -> bool:
        """Store a build artifact in the cache"""
        try:
            if not os.path.exists(source_path):
                logger.warning(f"Source path {source_path} does not exist")
                return False
            
            # Calculate file hash
            file_hash = self._calculate_file_hash(source_path)
            if not file_hash:
                return False
            
            # Get file info
            file_size = os.path.getsize(source_path)
            platform, arch = self._get_platform_info()
            
            # Create artifact metadata
            artifact = BuildArtifact(
                path=source_path,
                hash=file_hash,
                size=file_size,
                created=datetime.now(),
                last_accessed=datetime.now(),
                build_id=build_id,
                dependencies=dependencies or [],
                platform=platform,
                arch=arch
            )
            
            # Create cache key
            cache_key = f"{build_id}_{file_hash[:8]}"
            
            # Copy file to cache
            cache_path = os.path.join(self.cache_dir, f"{cache_key}_{os.path.basename(source_path)}")
            shutil.copy2(source_path, cache_path)
            
            # Update artifact path to cache location
            artifact.path = cache_path
            
            # Store in cache
            self.cache.artifacts[cache_key] = artifact
            
            logger.info(f"Stored artifact {cache_key} ({file_size} bytes)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store artifact {source_path}: {e}")
            return False
    
    def retrieve_artifact(self, build_id: str, target_path: str, file_hash: str = None) -> bool:
        """Retrieve a build artifact from the cache"""
        try:
            # Find matching artifact
            matching_artifacts = []
            for key, artifact in self.cache.artifacts.items():
                if artifact.build_id == build_id:
                    if file_hash is None or artifact.hash.startswith(file_hash):
                        matching_artifacts.append((key, artifact))
            
            if not matching_artifacts:
                logger.debug(f"No cached artifacts found for build_id {build_id}")
                return False
            
            # Use the most recent artifact
            key, artifact = max(matching_artifacts, key=lambda x: x[1].created)
            
            # Check if artifact still exists
            if not os.path.exists(artifact.path):
                logger.warning(f"Cached artifact {artifact.path} no longer exists")
                del self.cache.artifacts[key]
                return False
            
            # Copy artifact to target location
            shutil.copy2(artifact.path, target_path)
            
            # Update last accessed time
            artifact.last_accessed = datetime.now()
            
            logger.info(f"Retrieved artifact {key} to {target_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to retrieve artifact for build_id {build_id}: {e}")
            return False
    
    def cleanup_cache(self):
        """Clean up old and oversized cache entries"""
        try:
            current_time = datetime.now()
            cutoff_time = current_time - timedelta(days=self.max_age_days)
            
            # Calculate current cache size
            total_size = sum(artifact.size for artifact in self.cache.artifacts.values())
            
            # Remove old artifacts
            artifacts_to_remove = []
            for key, artifact in self.cache.artifacts.items():
                if artifact.last_accessed < cutoff_time:
                    artifacts_to_remove.append(key)
            
            for key in artifacts_to_remove:
                artifact = self.cache.artifacts[key]
                try:
                    if os.path.exists(artifact.path):
                        os.remove(artifact.path)
                    del self.cache.artifacts[key]
                    logger.info(f"Removed old artifact {key}")
                except Exception as e:
                    logger.warning(f"Failed to remove artifact {key}: {e}")
            
            # Remove oversized artifacts if cache is still too large
            if total_size > self.max_size:
                # Sort by last accessed time (oldest first)
                sorted_artifacts = sorted(
                    self.cache.artifacts.items(),
                    key=lambda x: x[1].last_accessed
                )
                
                current_size = sum(artifact.size for artifact in self.cache.artifacts.values())
                for key, artifact in sorted_artifacts:
                    if current_size <= self.max_size:
                        break
                    
                    try:
                        if os.path.exists(artifact.path):
                            os.remove(artifact.path)
                        del self.cache.artifacts[key]
                        current_size -= artifact.size
                        logger.info(f"Removed oversized artifact {key}")
                    except Exception as e:
                        logger.warning(f"Failed to remove artifact {key}: {e}")
            
            # Update cleanup time
            self.cache.last_cleanup = current_time
            
            # Save updated metadata
            self._save_cache_metadata()
            
            logger.info(f"Cache cleanup completed. {len(self.cache.artifacts)} artifacts remaining")
            
        except Exception as e:
            logger.error(f"Cache cleanup failed: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_size = sum(artifact.size for artifact in self.cache.artifacts.values())
        total_files = len(self.cache.artifacts)
        
        # Group by build_id
        build_ids = set(artifact.build_id for artifact in self.cache.artifacts.values())
        
        return {
            'total_size_bytes': total_size,
            'total_size_mb': total_size / (1024 * 1024),
            'total_files': total_files,
            'unique_builds': len(build_ids),
            'cache_dir': self.cache_dir,
            'max_size_mb': self.max_size / (1024 * 1024),
            'max_age_days': self.max_age_days,
            'last_cleanup': self.cache.last_cleanup.isoformat()
        }
    
    def list_artifacts(self, build_id: str = None) -> List[Dict[str, Any]]:
        """List cached artifacts, optionally filtered by build_id"""
        artifacts = []
        for key, artifact in self.cache.artifacts.items():
            if build_id is None or artifact.build_id == build_id:
                artifacts.append({
                    'key': key,
                    'path': artifact.path,
                    'hash': artifact.hash,
                    'size': artifact.size,
                    'created': artifact.created.isoformat(),
                    'last_accessed': artifact.last_accessed.isoformat(),
                    'build_id': artifact.build_id,
                    'platform': artifact.platform,
                    'arch': artifact.arch,
                    'dependencies': artifact.dependencies
                })
        
        return sorted(artifacts, key=lambda x: x['last_accessed'], reverse=True)


class CompilerCacheManager:
    """Manages compiler caching (ccache/sccache) for C/C++ builds"""
    
    def __init__(self, cache_dir: str = None):
        """Initialize compiler cache manager"""
        self.cache_dir = cache_dir or os.path.join(os.path.expanduser("~"), ".ccache")
        self.ccache_available = self._check_ccache_availability()
        self.sccache_available = self._check_sccache_availability()
    
    def _check_ccache_availability(self) -> bool:
        """Check if ccache is available"""
        try:
            result = subprocess.run(['ccache', '--version'], 
                                  capture_output=True, text=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _check_sccache_availability(self) -> bool:
        """Check if sccache is available"""
        try:
            result = subprocess.run(['sccache', '--version'], 
                                  capture_output=True, text=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def setup_ccache(self, max_size: str = "5G") -> Dict[str, str]:
        """Set up ccache environment variables"""
        env_vars = {}
        
        if self.ccache_available:
            env_vars.update({
                'CCACHE_DIR': self.cache_dir,
                'CCACHE_MAXSIZE': max_size,
                'CCACHE_COMPRESS': '1',
                'CCACHE_COMPRESSLEVEL': '6',
                'CCACHE_HARDLINK': '1',
                'CCACHE_SLOPPINESS': 'pch_defines,time_macros',
                'CCACHE_UMASK': '002'
            })
            
            # Set up compiler wrappers
            ccache_path = shutil.which('ccache')
            if ccache_path:
                env_vars.update({
                    'CC': f"{ccache_path} gcc",
                    'CXX': f"{ccache_path} g++",
                    'CCACHE_PREFIX': 'ccache'
                })
        
        return env_vars
    
    def setup_sccache(self) -> Dict[str, str]:
        """Set up sccache environment variables"""
        env_vars = {}
        
        if self.sccache_available:
            env_vars.update({
                'SCCACHE_DIR': self.cache_dir,
                'SCCACHE_CACHE_SIZE': '5G',
                'SCCACHE_GHA_ENABLED': '1'
            })
            
            # Set up compiler wrappers
            sccache_path = shutil.which('sccache')
            if sccache_path:
                env_vars.update({
                    'CC': f"{sccache_path} gcc",
                    'CXX': f"{sccache_path} g++",
                    'RUSTC_WRAPPER': sccache_path
                })
        
        return env_vars
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get compiler cache statistics"""
        stats = {
            'ccache_available': self.ccache_available,
            'sccache_available': self.sccache_available,
            'cache_dir': self.cache_dir
        }
        
        if self.ccache_available:
            try:
                result = subprocess.run(['ccache', '-s'], 
                                      capture_output=True, text=True, check=True)
                stats['ccache_stats'] = result.stdout
            except subprocess.CalledProcessError:
                stats['ccache_stats'] = "Unable to get ccache stats"
        
        if self.sccache_available:
            try:
                result = subprocess.run(['sccache', '--show-stats'], 
                                      capture_output=True, text=True, check=True)
                stats['sccache_stats'] = result.stdout
            except subprocess.CalledProcessError:
                stats['sccache_stats'] = "Unable to get sccache stats"
        
        return stats


def main():
    """Command line interface for cache management"""
    import argparse
    
    parser = argparse.ArgumentParser(description='OpenSSL Tools Build Cache Manager')
    parser.add_argument('--cache-dir', help='Cache directory')
    parser.add_argument('--max-size', type=int, default=10, help='Max cache size in GB')
    parser.add_argument('--max-age', type=int, default=30, help='Max age in days')
    parser.add_argument('--cleanup', action='store_true', help='Clean up cache')
    parser.add_argument('--stats', action='store_true', help='Show cache statistics')
    parser.add_argument('--list', action='store_true', help='List cached artifacts')
    parser.add_argument('--build-id', help='Filter by build ID')
    
    args = parser.parse_args()
    
    # Initialize cache manager
    cache_manager = BuildCacheManager(
        cache_dir=args.cache_dir,
        max_size_gb=args.max_size,
        max_age_days=args.max_age
    )
    
    if args.cleanup:
        cache_manager.cleanup_cache()
    
    if args.stats:
        stats = cache_manager.get_cache_stats()
        print("Cache Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
    
    if args.list:
        artifacts = cache_manager.list_artifacts(build_id=args.build_id)
        print(f"Cached Artifacts ({len(artifacts)}):")
        for artifact in artifacts:
            print(f"  {artifact['key']}: {artifact['size']} bytes, {artifact['last_accessed']}")


if __name__ == '__main__':
    main()