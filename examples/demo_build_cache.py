#!/usr/bin/env python3
"""
Demo script for OpenSSL Tools Build Cache
Demonstrates build artifact caching and reuse
"""

import os
import sys
import time
import subprocess
import tempfile
import shutil
from pathlib import Path

# Add the package to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from openssl_tools.utils.build_cache import BuildCacheManager, CompilerCacheManager
from openssl_tools.utils.build_optimizer import BuildOptimizer


def create_demo_project():
    """Create a demo C project for testing build caching"""
    demo_dir = tempfile.mkdtemp(prefix='openssl-tools-demo-')
    
    # Create a simple C program
    main_c = os.path.join(demo_dir, 'main.c')
    with open(main_c, 'w') as f:
        f.write('''
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

int main() {
    printf("Hello from OpenSSL Tools Build Cache Demo!\\n");
    printf("Build time: %ld\\n", time(NULL));
    return 0;
}
''')
    
    # Create a Makefile
    makefile = os.path.join(demo_dir, 'Makefile')
    with open(makefile, 'w') as f:
        f.write('''
CC=gcc
CFLAGS=-O2 -g -Wall
TARGET=hello
SOURCE=main.c

$(TARGET): $(SOURCE)
\t$(CC) $(CFLAGS) -o $(TARGET) $(SOURCE)

clean:
\trm -f $(TARGET)

.PHONY: clean
''')
    
    return demo_dir


def demo_build_caching():
    """Demonstrate build caching functionality"""
    print("OpenSSL Tools Build Cache Demo")
    print("=" * 40)
    
    # Create demo project
    print("Creating demo project...")
    demo_dir = create_demo_project()
    print(f"Demo project created at: {demo_dir}")
    
    try:
        # Initialize build cache manager
        print("\nInitializing build cache manager...")
        cache_manager = BuildCacheManager(
            cache_dir=os.path.join(demo_dir, 'cache'),
            max_size_gb=1,
            max_age_days=7
        )
        
        # Initialize compiler cache manager
        print("Initializing compiler cache manager...")
        compiler_cache = CompilerCacheManager(
            cache_dir=os.path.join(demo_dir, 'ccache')
        )
        
        # Initialize build optimizer
        print("Initializing build optimizer...")
        config = {
            'source_dir': demo_dir,
            'build_dir': os.path.join(demo_dir, 'build'),
            'max_jobs': 2,
            'enable_ccache': True,
            'enable_sccache': False,
            'optimize_build': True
        }
        optimizer = BuildOptimizer(config)
        
        # Generate build ID
        build_config = {
            'build_system': 'make',
            'target': 'hello',
            'max_jobs': 2
        }
        build_id = optimizer.generate_build_id(demo_dir, build_config)
        print(f"Generated build ID: {build_id}")
        
        # First build (should compile everything)
        print("\nFirst build (clean)...")
        start_time = time.time()
        
        # Set up build environment
        env = optimizer.setup_build_environment()
        env.update(os.environ)
        
        # Build
        result = subprocess.run(
            ['make', 'hello'],
            cwd=demo_dir,
            env=env,
            capture_output=True,
            text=True
        )
        
        first_build_time = time.time() - start_time
        print(f"First build completed in {first_build_time:.2f} seconds")
        
        if result.returncode != 0:
            print(f"Build failed: {result.stderr}")
            return
        
        # Cache the built artifact
        hello_binary = os.path.join(demo_dir, 'hello')
        if os.path.exists(hello_binary):
            print("Caching build artifact...")
            cache_manager.store_artifact(
                hello_binary,
                build_id,
                dependencies=[os.path.join(demo_dir, 'main.c')]
            )
        
        # Clean build
        print("\nCleaning build...")
        subprocess.run(['make', 'clean'], cwd=demo_dir)
        
        # Second build (should use cache)
        print("Second build (with cache)...")
        start_time = time.time()
        
        # Check if we can retrieve from cache
        if cache_manager.retrieve_artifact(build_id, hello_binary):
            print("✅ Retrieved binary from cache!")
            cached_build_time = time.time() - start_time
        else:
            print("Cache miss, rebuilding...")
            result = subprocess.run(
                ['make', 'hello'],
                cwd=demo_dir,
                env=env,
                capture_output=True,
                text=True
            )
            cached_build_time = time.time() - start_time
        
        print(f"Second build completed in {cached_build_time:.2f} seconds")
        
        # Calculate improvement
        if first_build_time > 0:
            improvement = ((first_build_time - cached_build_time) / first_build_time) * 100
            print(f"\nBuild time improvement: {improvement:.1f}%")
        
        # Show cache statistics
        print("\nCache Statistics:")
        stats = cache_manager.get_cache_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # Show compiler cache statistics
        print("\nCompiler Cache Statistics:")
        compiler_stats = compiler_cache.get_cache_stats()
        for key, value in compiler_stats.items():
            if key.endswith('_stats'):
                print(f"  {key}:")
                for line in str(value).split('\n'):
                    if line.strip():
                        print(f"    {line}")
            else:
                print(f"  {key}: {value}")
        
        # Test the built binary
        print("\nTesting built binary...")
        result = subprocess.run([hello_binary], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Binary works correctly!")
            print(f"Output: {result.stdout.strip()}")
        else:
            print(f"❌ Binary failed: {result.stderr}")
        
        # List cached artifacts
        print("\nCached Artifacts:")
        artifacts = cache_manager.list_artifacts()
        for artifact in artifacts:
            print(f"  {artifact['key']}: {artifact['size']} bytes, {artifact['last_accessed']}")
        
    finally:
        # Cleanup
        print(f"\nCleaning up demo project: {demo_dir}")
        shutil.rmtree(demo_dir, ignore_errors=True)


def demo_conan_integration():
    """Demonstrate Conan integration with build caching"""
    print("\nConan Integration Demo")
    print("=" * 30)
    
    # Check if we're in a Conan environment
    if not os.path.exists('conanfile.py'):
        print("No conanfile.py found, skipping Conan demo")
        return
    
    print("Testing Conan package creation with caching...")
    
    # First build
    print("First Conan build...")
    start_time = time.time()
    result = subprocess.run(['conan', 'create', '.', '--build=missing'], 
                          capture_output=True, text=True)
    first_time = time.time() - start_time
    print(f"First build completed in {first_time:.2f} seconds")
    
    if result.returncode != 0:
        print(f"Conan build failed: {result.stderr}")
        return
    
    # Second build (should use cache)
    print("Second Conan build (with cache)...")
    start_time = time.time()
    result = subprocess.run(['conan', 'create', '.', '--build=missing'], 
                          capture_output=True, text=True)
    second_time = time.time() - start_time
    print(f"Second build completed in {second_time:.2f} seconds")
    
    # Calculate improvement
    if first_time > 0:
        improvement = ((first_time - second_time) / first_time) * 100
        print(f"Conan build time improvement: {improvement:.1f}%")
    
    # Show Conan cache stats
    print("\nConan Cache Statistics:")
    result = subprocess.run(['conan', 'cache', 'stats'], 
                          capture_output=True, text=True)
    if result.returncode == 0:
        print(result.stdout)
    else:
        print("Could not get Conan cache statistics")


def main():
    """Main demo function"""
    print("OpenSSL Tools Build Cache Demonstration")
    print("=" * 50)
    
    try:
        # Demo build caching
        demo_build_caching()
        
        # Demo Conan integration
        demo_conan_integration()
        
        print("\n✅ Demo completed successfully!")
        
    except KeyboardInterrupt:
        print("\n❌ Demo interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()