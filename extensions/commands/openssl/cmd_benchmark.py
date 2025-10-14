#!/usr/bin/env python3
"""
OpenSSL Benchmark Command for Conan Extension
Runs performance benchmarks and generates reports
"""

from conan.api.conan_api import ConanAPI
from conan.api.output import ConanOutput
from conan.cli.command import conan_command
import argparse
import os
import sys
from pathlib import Path


@conan_command(group="openssl")
def benchmark(conan_api: ConanAPI, parser, *args):
    """
    Run OpenSSL performance benchmarks.
    
    This command executes OpenSSL performance benchmarks and generates
    detailed reports with metrics and comparisons.
    """
    parser.add_argument("--profile", "-p", help="Conan profile to use for benchmarking")
    parser.add_argument("--build-dir", help="Build directory (from build command)")
    parser.add_argument("--openssl-dir", help="OpenSSL source directory (default: openssl-source)")
    parser.add_argument("--output-dir", help="Benchmark output directory")
    parser.add_argument("--benchmarks", nargs="+", 
                       choices=["speed", "memory", "crypto", "ssl", "all"], 
                       default=["all"], help="Benchmark types to run")
    parser.add_argument("--iterations", type=int, default=1000, 
                       help="Number of iterations per benchmark")
    parser.add_argument("--format", choices=["json", "csv", "html", "markdown"], 
                       default="json", help="Output format")
    parser.add_argument("--compare", help="Compare with previous benchmark results")
    parser.add_argument("--baseline", help="Baseline benchmark for comparison")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args(*args)
    
    try:
        # Import the OpenSSL benchmark runner script
        openssl_tools_root = Path(__file__).parent.parent.parent.parent
        sys.path.insert(0, str(openssl_tools_root / "scripts" / "conan"))
        
        from openssl_benchmark_runner import OpenSSLBenchmarkRunner
        
        # Create runner instance
        runner = OpenSSLBenchmarkRunner(
            conan_api=conan_api,
            profile=args.profile,
            build_dir=args.build_dir,
            openssl_dir=args.openssl_dir,
            output_dir=args.output_dir,
            benchmarks=args.benchmarks,
            iterations=args.iterations,
            format=args.format,
            compare=args.compare,
            baseline=args.baseline,
            verbose=args.verbose
        )
        
        # Execute benchmarks
        result = runner.run()
        
        if result.success:
            ConanOutput().info("✅ OpenSSL benchmarks completed successfully")
            ConanOutput().info(f"Output directory: {result.output_dir}")
            ConanOutput().info(f"Benchmarks run: {len(result.benchmark_results)}")
            ConanOutput().info(f"Total execution time: {result.total_time:.2f} seconds")
            if result.comparison_results:
                ConanOutput().info(f"Performance comparison: {result.comparison_results.summary}")
            if args.verbose:
                for benchmark in result.benchmark_results:
                    ConanOutput().info(f"  - {benchmark.name}: {benchmark.score}")
        else:
            ConanOutput().error(f"❌ OpenSSL benchmarks failed: {result.error}")
            return 1
            
    except ImportError as e:
        ConanOutput().error(f"❌ Failed to import OpenSSL benchmark runner module: {e}")
        ConanOutput().info("Make sure you're running from the openssl-tools repository")
        return 1
    except Exception as e:
        ConanOutput().error(f"❌ Unexpected error during benchmarking: {e}")
        return 1
    
    return 0
