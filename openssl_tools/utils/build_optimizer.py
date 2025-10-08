#!/usr/bin/env python3
"""
OpenSSL Tools Build Optimizer
Based on ngapy-dev patterns for build optimization and caching strategies
"""

import logging
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import json
import hashlib
import psutil


class BuildOptimizer:
    """Build optimizer following ngapy-dev patterns"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger('openssl_tools.build_optimizer')
        
        # Initialize optimization settings
        self.source_dir = Path(config.get('source_dir', '.'))
        self.build_dir = Path(config.get('build_dir', 'build'))
        self.max_jobs = config.get('max_jobs', psutil.cpu_count() or 4)
        self.enable_ccache = config.get('enable_ccache', True)
        self.enable_sccache = config.get('enable_sccache', False)
        self.optimize_build = config.get('optimize_build', True)
        self.reproducible_builds = config.get('reproducible_builds', True)
        
        # Cache directories
        self.cache_dir = Path(config.get('cache_dir', '.cache'))
        self.ccache_dir = self.cache_dir / 'ccache'
        self.sccache_dir = self.cache_dir / 'sccache'
        self.build_cache_dir = self.cache_dir / 'build'
        
        # Initialize caches
        self._setup_caches()
    
    def _setup_caches(self) -> None:
        """Setup cache directories and tools"""
        # Create cache directories
        for cache_dir in [self.cache_dir, self.ccache_dir, self.sccache_dir, self.build_cache_dir]:
            cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup ccache if enabled
        if self.enable_ccache:
            self._setup_ccache()
        
        # Setup sccache if enabled
        if self.enable_sccache:
            self._setup_sccache()
    
    def _setup_ccache(self) -> None:
        """Setup ccache for compilation caching"""
        try:
            # Check if ccache is available
            result = subprocess.run(['ccache', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                # Configure ccache
                os.environ['CCACHE_DIR'] = str(self.ccache_dir)
                os.environ['CCACHE_MAXSIZE'] = '2G'
                os.environ['CCACHE_COMPRESS'] = '1'
                os.environ['CCACHE_HARDLINK'] = '1'
                
                # Set compiler wrappers
                os.environ['CC'] = 'ccache gcc'
                os.environ['CXX'] = 'ccache g++'
                
                self.logger.info("ccache configured successfully")
            else:
                self.logger.warning("ccache not available, disabling")
                self.enable_ccache = False
        except FileNotFoundError:
            self.logger.warning("ccache not found, disabling")
            self.enable_ccache = False
    
    def _setup_sccache(self) -> None:
        """Setup sccache for compilation caching"""
        try:
            # Check if sccache is available
            result = subprocess.run(['sccache', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                # Configure sccache
                os.environ['SCCACHE_DIR'] = str(self.sccache_dir)
                os.environ['RUSTC_WRAPPER'] = 'sccache'
                
                self.logger.info("sccache configured successfully")
            else:
                self.logger.warning("sccache not available, disabling")
                self.enable_sccache = False
        except FileNotFoundError:
            self.logger.warning("sccache not found, disabling")
            self.enable_sccache = False
    
    def optimize_build_environment(self) -> Dict[str, str]:
        """Optimize build environment variables"""
        env = os.environ.copy()
        
        # Set build optimization flags
        if self.optimize_build:
            env['CFLAGS'] = '-O2 -DNDEBUG'
            env['CXXFLAGS'] = '-O2 -DNDEBUG'
            env['LDFLAGS'] = '-s'
        
        # Set reproducible build flags
        if self.reproducible_builds:
            env['SOURCE_DATE_EPOCH'] = str(int(time.time()))
            env['TZ'] = 'UTC'
        
        # Set parallel build flags
        env['MAKEFLAGS'] = f'-j{self.max_jobs}'
        env['CMAKE_BUILD_PARALLEL_LEVEL'] = str(self.max_jobs)
        
        # Set cache directories
        env['CCACHE_DIR'] = str(self.ccache_dir)
        if self.enable_sccache:
            env['SCCACHE_DIR'] = str(self.sccache_dir)
        
        self.logger.info("Build environment optimized")
        return env
    
    def get_build_cache_key(self, build_config: Dict[str, Any]) -> str:
        """Generate cache key for build configuration"""
        # Create hash of build configuration
        config_str = json.dumps(build_config, sort_keys=True)
        config_hash = hashlib.sha256(config_str.encode()).hexdigest()[:16]
        
        # Include source directory hash
        source_hash = self._get_directory_hash(self.source_dir)
        
        return f"{config_hash}_{source_hash}"
    
    def _get_directory_hash(self, directory: Path) -> str:
        """Get hash of directory contents"""
        hasher = hashlib.sha256()
        
        for file_path in sorted(directory.rglob('*')):
            if file_path.is_file():
                # Add file path and size to hash
                hasher.update(str(file_path.relative_to(directory)).encode())
                hasher.update(str(file_path.stat().st_size).encode())
                
                # Add file modification time
                hasher.update(str(file_path.stat().st_mtime).encode())
        
        return hasher.hexdigest()[:16]
    
    def get_cached_build(self, cache_key: str) -> Optional[Path]:
        """Get cached build if available"""
        cache_path = self.build_cache_dir / cache_key
        
        if cache_path.exists():
            # Check if cache is still valid
            if self._is_cache_valid(cache_path, cache_key):
                self.logger.info(f"Using cached build: {cache_path}")
                return cache_path
            else:
                # Remove invalid cache
                shutil.rmtree(cache_path)
                self.logger.info(f"Removed invalid cache: {cache_path}")
        
        return None
    
    def _is_cache_valid(self, cache_path: Path, cache_key: str) -> bool:
        """Check if cache is still valid"""
        try:
            # Check cache metadata
            metadata_file = cache_path / '.cache_metadata'
            if not metadata_file.exists():
                return False
            
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            # Check if source directory has changed
            current_source_hash = self._get_directory_hash(self.source_dir)
            if metadata.get('source_hash') != current_source_hash:
                return False
            
            # Check cache age (24 hours)
            cache_age = time.time() - metadata.get('created_at', 0)
            if cache_age > 24 * 3600:
                return False
            
            return True
        except Exception as e:
            self.logger.warning(f"Failed to validate cache: {e}")
            return False
    
    def cache_build(self, cache_key: str, build_artifacts: List[Path]) -> bool:
        """Cache build artifacts"""
        try:
            cache_path = self.build_cache_dir / cache_key
            cache_path.mkdir(parents=True, exist_ok=True)
            
            # Copy build artifacts
            for artifact in build_artifacts:
                if artifact.exists():
                    dest_path = cache_path / artifact.name
                    if artifact.is_dir():
                        shutil.copytree(artifact, dest_path, dirs_exist_ok=True)
                    else:
                        shutil.copy2(artifact, dest_path)
            
            # Save cache metadata
            metadata = {
                'cache_key': cache_key,
                'source_hash': self._get_directory_hash(self.source_dir),
                'created_at': time.time(),
                'artifacts': [str(a) for a in build_artifacts]
            }
            
            metadata_file = cache_path / '.cache_metadata'
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            self.logger.info(f"Cached build artifacts: {cache_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to cache build: {e}")
            return False
    
    def clean_build_cache(self, max_age_hours: int = 24) -> int:
        """Clean old build cache entries"""
        cleaned_count = 0
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        for cache_dir in self.build_cache_dir.iterdir():
            if cache_dir.is_dir():
                try:
                    metadata_file = cache_dir / '.cache_metadata'
                    if metadata_file.exists():
                        with open(metadata_file, 'r') as f:
                            metadata = json.load(f)
                        
                        cache_age = current_time - metadata.get('created_at', 0)
                        if cache_age > max_age_seconds:
                            shutil.rmtree(cache_dir)
                            cleaned_count += 1
                            self.logger.info(f"Cleaned old cache: {cache_dir}")
                except Exception as e:
                    self.logger.warning(f"Failed to clean cache {cache_dir}: {e}")
        
        self.logger.info(f"Cleaned {cleaned_count} cache entries")
        return cleaned_count
    
    def get_build_statistics(self) -> Dict[str, Any]:
        """Get build statistics"""
        stats = {
            'cache_size': self._get_directory_size(self.cache_dir),
            'ccache_size': self._get_directory_size(self.ccache_dir) if self.enable_ccache else 0,
            'sccache_size': self._get_directory_size(self.sccache_dir) if self.enable_sccache else 0,
            'build_cache_size': self._get_directory_size(self.build_cache_dir),
            'cache_entries': len(list(self.build_cache_dir.iterdir())),
            'max_jobs': self.max_jobs,
            'enable_ccache': self.enable_ccache,
            'enable_sccache': self.enable_sccache,
            'optimize_build': self.optimize_build,
            'reproducible_builds': self.reproducible_builds
        }
        
        return stats
    
    def _get_directory_size(self, directory: Path) -> int:
        """Get directory size in bytes"""
        total_size = 0
        try:
            for file_path in directory.rglob('*'):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
        except Exception as e:
            self.logger.warning(f"Failed to calculate directory size for {directory}: {e}")
        return total_size
    
    def optimize_makefile(self, makefile_path: Path) -> bool:
        """Optimize Makefile for parallel builds"""
        try:
            if not makefile_path.exists():
                return False
            
            # Read Makefile
            with open(makefile_path, 'r') as f:
                content = f.read()
            
            # Add parallel build optimization
            optimizations = [
                f"MAKEFLAGS += -j{self.max_jobs}",
                "MAKEFLAGS += --no-print-directory",
                "MAKEFLAGS += --silent",
            ]
            
            # Add ccache support if enabled
            if self.enable_ccache:
                optimizations.extend([
                    "CC = ccache gcc",
                    "CXX = ccache g++",
                ])
            
            # Add optimization flags
            if self.optimize_build:
                optimizations.extend([
                    "CFLAGS += -O2 -DNDEBUG",
                    "CXXFLAGS += -O2 -DNDEBUG",
                    "LDFLAGS += -s",
                ])
            
            # Add reproducible build flags
            if self.reproducible_builds:
                optimizations.extend([
                    f"CFLAGS += -DSOURCE_DATE_EPOCH={int(time.time())}",
                    "TZ = UTC",
                ])
            
            # Write optimized Makefile
            optimized_content = '\n'.join(optimizations) + '\n\n' + content
            with open(makefile_path, 'w') as f:
                f.write(optimized_content)
            
            self.logger.info(f"Optimized Makefile: {makefile_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to optimize Makefile {makefile_path}: {e}")
            return False
    
    def optimize_cmake(self, cmake_path: Path) -> bool:
        """Optimize CMake configuration"""
        try:
            if not cmake_path.exists():
                return False
            
            # Read CMakeLists.txt
            with open(cmake_path, 'r') as f:
                content = f.read()
            
            # Add optimization settings
            optimizations = [
                f"set(CMAKE_BUILD_PARALLEL_LEVEL {self.max_jobs})",
                "set(CMAKE_EXPORT_COMPILE_COMMANDS ON)",
            ]
            
            # Add ccache support if enabled
            if self.enable_ccache:
                optimizations.extend([
                    "find_program(CCACHE_FOUND ccache)",
                    "if(CCACHE_FOUND)",
                    "    set_property(GLOBAL PROPERTY RULE_LAUNCH_COMPILE ccache)",
                    "    set_property(GLOBAL PROPERTY RULE_LAUNCH_LINK ccache)",
                    "endif()",
                ])
            
            # Add optimization flags
            if self.optimize_build:
                optimizations.extend([
                    "set(CMAKE_C_FLAGS_RELEASE \"-O2 -DNDEBUG\")",
                    "set(CMAKE_CXX_FLAGS_RELEASE \"-O2 -DNDEBUG\")",
                ])
            
            # Add reproducible build flags
            if self.reproducible_builds:
                optimizations.extend([
                    f"set(CMAKE_C_FLAGS \"${{CMAKE_C_FLAGS}} -DSOURCE_DATE_EPOCH={int(time.time())}\")",
                    "set(CMAKE_CXX_FLAGS \"${CMAKE_CXX_FLAGS} -DSOURCE_DATE_EPOCH={int(time.time())}\")",
                ])
            
            # Write optimized CMakeLists.txt
            optimized_content = '\n'.join(optimizations) + '\n\n' + content
            with open(cmake_path, 'w') as f:
                f.write(optimized_content)
            
            self.logger.info(f"Optimized CMakeLists.txt: {cmake_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to optimize CMakeLists.txt {cmake_path}: {e}")
            return False
    
    def get_ccache_statistics(self) -> Dict[str, Any]:
        """Get ccache statistics"""
        if not self.enable_ccache:
            return {}
        
        try:
            result = subprocess.run(['ccache', '-s'], capture_output=True, text=True)
            if result.returncode == 0:
                stats = {}
                for line in result.stdout.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip().replace(' ', '_').lower()
                        value = value.strip()
                        try:
                            # Try to convert to number
                            if value.isdigit():
                                stats[key] = int(value)
                            else:
                                stats[key] = value
                        except ValueError:
                            stats[key] = value
                return stats
        except Exception as e:
            self.logger.warning(f"Failed to get ccache statistics: {e}")
        
        return {}
    
    def get_sccache_statistics(self) -> Dict[str, Any]:
        """Get sccache statistics"""
        if not self.enable_sccache:
            return {}
        
        try:
            result = subprocess.run(['sccache', '--show-stats'], capture_output=True, text=True)
            if result.returncode == 0:
                stats = {}
                for line in result.stdout.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip().replace(' ', '_').lower()
                        value = value.strip()
                        try:
                            # Try to convert to number
                            if value.isdigit():
                                stats[key] = int(value)
                            else:
                                stats[key] = value
                        except ValueError:
                            stats[key] = value
                return stats
        except Exception as e:
            self.logger.warning(f"Failed to get sccache statistics: {e}")
        
        return {}
    
    def clear_all_caches(self) -> None:
        """Clear all caches"""
        try:
            # Clear ccache
            if self.enable_ccache:
                subprocess.run(['ccache', '-C'], check=True)
                self.logger.info("Cleared ccache")
            
            # Clear sccache
            if self.enable_sccache:
                subprocess.run(['sccache', '--stop-server'], check=True)
                subprocess.run(['sccache', '--start-server'], check=True)
                self.logger.info("Cleared sccache")
            
            # Clear build cache
            if self.build_cache_dir.exists():
                shutil.rmtree(self.build_cache_dir)
                self.build_cache_dir.mkdir(parents=True, exist_ok=True)
                self.logger.info("Cleared build cache")
            
        except Exception as e:
            self.logger.error(f"Failed to clear caches: {e}")
    
    def optimize_for_ci(self) -> None:
        """Optimize build for CI environment"""
        # Disable interactive features
        os.environ['DEBIAN_FRONTEND'] = 'noninteractive'
        os.environ['CI'] = 'true'
        
        # Set conservative parallel jobs for CI
        self.max_jobs = min(self.max_jobs, 2)
        
        # Enable verbose output for CI
        os.environ['VERBOSE'] = '1'
        
        self.logger.info("Optimized build for CI environment")
    
    def optimize_for_development(self) -> None:
        """Optimize build for development environment"""
        # Enable debug symbols
        os.environ['CFLAGS'] = '-g -O0'
        os.environ['CXXFLAGS'] = '-g -O0'
        
        # Enable verbose output
        os.environ['VERBOSE'] = '1'
        
        # Disable optimization for faster builds
        self.optimize_build = False
        
        self.logger.info("Optimized build for development environment")