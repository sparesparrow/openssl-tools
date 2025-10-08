# OpenSSL Tools Build Cache System

This document describes the build caching and optimization system implemented in OpenSSL Tools, designed to significantly improve build performance by reusing previously compiled objects and linked binaries.

## Overview

The build cache system provides:

- **Intelligent Artifact Caching**: Automatically caches compiled objects and binaries
- **Compiler Caching**: Integration with ccache and sccache for C/C++ compilation
- **Conan Integration**: Seamless integration with Conan package manager
- **CI/CD Optimization**: GitHub Actions workflows with multi-level caching
- **Build Statistics**: Comprehensive metrics and performance monitoring

## Features

### 1. Build Artifact Caching

The system automatically caches build artifacts based on:
- Source file content (SHA-256 hashes)
- Build configuration
- Platform and architecture
- Dependencies

```python
from openssl_tools.utils.build_cache import BuildCacheManager

# Initialize cache manager
cache_manager = BuildCacheManager(
    cache_dir="~/.openssl-tools-cache",
    max_size_gb=10,
    max_age_days=30
)

# Store an artifact
cache_manager.store_artifact(
    "path/to/binary",
    build_id="abc123",
    dependencies=["src/main.c", "src/utils.c"]
)

# Retrieve an artifact
if cache_manager.retrieve_artifact(build_id="abc123", target_path="path/to/binary"):
    print("Using cached artifact!")
```

### 2. Compiler Caching

Integration with ccache and sccache for C/C++ compilation:

```python
from openssl_tools.utils.build_cache import CompilerCacheManager

# Initialize compiler cache
compiler_cache = CompilerCacheManager()

# Set up ccache
ccache_env = compiler_cache.setup_ccache(max_size="5G")
# Use ccache_env in your build environment

# Set up sccache
sccache_env = compiler_cache.setup_sccache()
# Use sccache_env in your build environment
```

### 3. Build Optimization

Intelligent build optimization with parallel jobs and caching:

```python
from openssl_tools.utils.build_optimizer import BuildOptimizer

# Initialize build optimizer
config = {
    'source_dir': '.',
    'build_dir': 'build',
    'max_jobs': 8,
    'enable_ccache': True,
    'enable_sccache': False,
    'optimize_build': True
}
optimizer = BuildOptimizer(config)

# Optimize Make build
optimizer.optimize_make_build(target='all')

# Optimize CMake build
optimizer.optimize_cmake_build(target='all')

# Optimize Autotools build
optimizer.optimize_autotools_build(['--prefix=/usr/local'])
```

## Usage

### Command Line Interface

#### Build Cache Manager

```bash
# Show cache statistics
python -m openssl_tools.utils.build_cache --stats

# List cached artifacts
python -m openssl_tools.utils.build_cache --list

# Clean up old artifacts
python -m openssl_tools.utils.build_cache --cleanup

# List artifacts for specific build
python -m openssl_tools.utils.build_cache --list --build-id abc123
```

#### Build Optimizer

```bash
# Optimize build with auto-detection
python -m openssl_tools.utils.build_optimizer --source-dir . --build-dir build

# Use specific build system
python -m openssl_tools.utils.build_optimizer --build-system cmake --target all

# Enable ccache
python -m openssl_tools.utils.build_optimizer --enable-ccache

# Show build statistics
python -m openssl_tools.utils.build_optimizer --stats
```

### Conan Integration

The build cache system is fully integrated with Conan:

```bash
# Create package with optimization
conan create . --profile=conan-profiles/optimized-cache.profile

# Install with caching
conan install . --build=missing --profile=conan-profiles/optimized-cache.profile
```

### GitHub Actions Integration

The system includes comprehensive GitHub Actions workflows:

```yaml
# Use the build-cache workflow
- uses: actions/checkout@v4
- name: Set up ccache
  uses: actions/cache@v4
  with:
    path: ~/.ccache
    key: ccache-${{ runner.os }}-${{ matrix.python-version }}-${{ hashFiles('**/conanfile.py') }}
```

## Configuration

### Build Cache Configuration

```python
config = {
    'cache_dir': '~/.openssl-tools-cache',  # Cache directory
    'max_size_gb': 10,                      # Maximum cache size
    'max_age_days': 30,                     # Maximum age of artifacts
    'enable_ccache': True,                  # Enable ccache
    'enable_sccache': False,                # Enable sccache
    'ccache_max_size': '5G',                # ccache maximum size
    'max_jobs': 8,                          # Maximum parallel jobs
    'optimize_build': True,                 # Enable build optimization
    'reproducible_builds': True             # Enable reproducible builds
}
```

### Conan Profile Configuration

```ini
[settings]
os=Linux
arch=x86_64
compiler=gcc
compiler.version=11
build_type=Release

[conf]
# Build optimization
tools.cmake.cmaketoolchain:jobs=8
tools.env:MAKEFLAGS=-j8
tools.env:CONAN_CPU_COUNT=8

# Compiler caching
tools.env:CCACHE_DIR=/tmp/ccache
tools.env:CCACHE_MAXSIZE=5G
tools.env:CC=ccache gcc
tools.env:CXX=ccache g++
```

## Performance Benefits

### Typical Performance Improvements

- **First Build**: Normal compilation time
- **Cached Build**: 50-90% faster (depending on cache hit rate)
- **Incremental Builds**: 80-95% faster
- **CI/CD Builds**: 60-85% faster

### Cache Hit Rates

- **Source Code Changes**: 0-20% (expected)
- **Configuration Changes**: 20-50% (partial reuse)
- **No Changes**: 90-100% (full reuse)
- **Dependency Updates**: 30-70% (selective reuse)

## Monitoring and Statistics

### Build Statistics

```python
# Get build statistics
stats = optimizer.get_build_statistics()
print(f"Build jobs: {stats['build_optimizer']['max_jobs']}")
print(f"Cache enabled: {stats['build_optimizer']['cache_enabled']}")
print(f"CCache enabled: {stats['build_optimizer']['ccache_enabled']}")
```

### Cache Statistics

```python
# Get cache statistics
cache_stats = cache_manager.get_cache_stats()
print(f"Total cache size: {cache_stats['total_size_mb']:.2f} MB")
print(f"Total files: {cache_stats['total_files']}")
print(f"Unique builds: {cache_stats['unique_builds']}")
```

### Compiler Cache Statistics

```python
# Get compiler cache statistics
compiler_stats = compiler_cache.get_cache_stats()
print(f"CCache available: {compiler_stats['ccache_available']}")
print(f"SCCache available: {compiler_stats['sccache_available']}")
```

## Best Practices

### 1. Cache Management

- **Regular Cleanup**: Run cache cleanup regularly to prevent disk space issues
- **Size Limits**: Set appropriate cache size limits based on available disk space
- **Age Limits**: Set appropriate age limits to ensure fresh builds

### 2. Build Optimization

- **Parallel Jobs**: Use appropriate number of parallel jobs (typically 75% of CPU cores)
- **Compiler Caching**: Enable ccache for C/C++ projects, sccache for Rust projects
- **Reproducible Builds**: Enable reproducible builds for consistent caching

### 3. CI/CD Integration

- **Multi-level Caching**: Use both Conan cache and build artifact cache
- **Cache Keys**: Use appropriate cache keys based on source files and configuration
- **Cache Restoration**: Restore caches before builds, save after successful builds

### 4. Development Workflow

- **Incremental Builds**: Use incremental builds during development
- **Clean Builds**: Use clean builds for release builds
- **Cache Validation**: Validate cache integrity for critical builds

## Troubleshooting

### Common Issues

1. **Cache Misses**: Check if source files or configuration changed
2. **Disk Space**: Monitor cache size and clean up old artifacts
3. **Permission Issues**: Ensure proper permissions for cache directories
4. **Compiler Issues**: Verify ccache/sccache installation and configuration

### Debug Information

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Get detailed cache information
artifacts = cache_manager.list_artifacts()
for artifact in artifacts:
    print(f"Artifact: {artifact['key']}")
    print(f"  Size: {artifact['size']} bytes")
    print(f"  Created: {artifact['created']}")
    print(f"  Dependencies: {artifact['dependencies']}")
```

## Demo

Run the build cache demonstration:

```bash
python scripts/demo-build-cache.py
```

This will:
1. Create a demo C project
2. Build it with caching enabled
3. Demonstrate cache reuse
4. Show performance improvements
5. Display cache statistics

## Integration with OpenSSL

The build cache system is designed to work seamlessly with OpenSSL builds:

1. **Conan Integration**: Full integration with OpenSSL Conan recipes
2. **CI/CD Optimization**: GitHub Actions workflows for OpenSSL builds
3. **Cross-platform Support**: Works on Linux, macOS, and Windows
4. **Multi-architecture**: Supports x86_64, ARM64, and other architectures

## Future Enhancements

- **Distributed Caching**: Support for distributed cache across multiple machines
- **Cloud Integration**: Integration with cloud storage for cache persistence
- **Machine Learning**: ML-based cache prediction and optimization
- **Advanced Metrics**: More detailed performance metrics and analysis