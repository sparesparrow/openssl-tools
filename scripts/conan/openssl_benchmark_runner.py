#!/usr/bin/env python3
"""
OpenSSL Benchmark Runner Module
Execute and report OpenSSL performance benchmarks
"""

import os
import sys
import subprocess
import time
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List, NamedTuple
from dataclasses import dataclass
import csv
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class BenchmarkResult:
    """Individual benchmark result"""
    name: str
    score: float
    unit: str
    iterations: int
    duration: float


@dataclass
class ComparisonResult:
    """Benchmark comparison result"""
    summary: str
    improvements: List[str]
    regressions: List[str]


@dataclass
class BenchmarkRunResult:
    """Result of benchmark execution"""
    success: bool
    output_dir: Optional[str] = None
    benchmark_results: List[BenchmarkResult] = None
    total_time: float = 0.0
    comparison_results: Optional[ComparisonResult] = None
    error: Optional[str] = None


class OpenSSLBenchmarkRunner:
    """OpenSSL benchmark runner and reporter"""
    
    def __init__(self, conan_api, profile=None, build_dir=None, openssl_dir=None,
                 output_dir=None, benchmarks=None, iterations=1000, format="json",
                 compare=None, baseline=None, verbose=False):
        self.conan_api = conan_api
        self.profile = profile
        self.build_dir = Path(build_dir or "build-linux-gcc")
        self.openssl_dir = Path(openssl_dir or "openssl-source")
        self.output_dir = Path(output_dir or "benchmarks")
        self.benchmarks = benchmarks or ["all"]
        self.iterations = iterations
        self.format = format
        self.compare = compare
        self.baseline = baseline
        self.verbose = verbose
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _run_speed_benchmark(self) -> List[BenchmarkResult]:
        """Run OpenSSL speed benchmark"""
        results = []
        
        try:
            # Run openssl speed command
            cmd = ["openssl", "speed", "-seconds", "10"]
            
            if self.verbose:
                logger.info(f"Running speed benchmark: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                cwd=self.openssl_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                # Parse speed benchmark output
                results.extend(self._parse_speed_output(result.stdout))
            else:
                logger.error(f"Speed benchmark failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            logger.error("Speed benchmark timed out")
        except Exception as e:
            logger.error(f"Speed benchmark error: {e}")
        
        return results
    
    def _parse_speed_output(self, output: str) -> List[BenchmarkResult]:
        """Parse OpenSSL speed command output"""
        results = []
        lines = output.strip().split('\n')
        
        for line in lines:
            if 'k' in line and 'sign' in line.lower():
                # Parse signature benchmarks
                parts = line.split()
                if len(parts) >= 3:
                    try:
                        name = f"sign_{parts[0]}"
                        score = float(parts[1])
                        unit = "ops/sec"
                        results.append(BenchmarkResult(
                            name=name,
                            score=score,
                            unit=unit,
                            iterations=self.iterations,
                            duration=10.0
                        ))
                    except (ValueError, IndexError):
                        continue
            elif 'k' in line and 'verify' in line.lower():
                # Parse verification benchmarks
                parts = line.split()
                if len(parts) >= 3:
                    try:
                        name = f"verify_{parts[0]}"
                        score = float(parts[1])
                        unit = "ops/sec"
                        results.append(BenchmarkResult(
                            name=name,
                            score=score,
                            unit=unit,
                            iterations=self.iterations,
                            duration=10.0
                        ))
                    except (ValueError, IndexError):
                        continue
        
        return results
    
    def _run_memory_benchmark(self) -> List[BenchmarkResult]:
        """Run memory usage benchmark"""
        results = []
        
        try:
            # Use valgrind if available for memory profiling
            cmd = ["valgrind", "--tool=massif", "--time-unit=ms", 
                   "openssl", "speed", "-seconds", "5"]
            
            result = subprocess.run(
                ["which", "valgrind"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                logger.warning("valgrind not available, skipping memory benchmark")
                return results
            
            if self.verbose:
                logger.info("Running memory benchmark with valgrind")
            
            result = subprocess.run(
                cmd,
                cwd=self.openssl_dir,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            if result.returncode == 0:
                # Parse valgrind output for memory usage
                memory_usage = self._parse_memory_output(result.stderr)
                if memory_usage:
                    results.append(BenchmarkResult(
                        name="memory_usage",
                        score=memory_usage,
                        unit="bytes",
                        iterations=1,
                        duration=5.0
                    ))
            else:
                logger.error(f"Memory benchmark failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            logger.error("Memory benchmark timed out")
        except Exception as e:
            logger.error(f"Memory benchmark error: {e}")
        
        return results
    
    def _parse_memory_output(self, output: str) -> Optional[float]:
        """Parse valgrind memory output"""
        # Simple parsing - look for peak memory usage
        for line in output.split('\n'):
            if 'peak' in line.lower() and 'bytes' in line.lower():
                # Extract number from line
                import re
                numbers = re.findall(r'\d+', line)
                if numbers:
                    return float(numbers[-1])  # Take the last number
        return None
    
    def _run_crypto_benchmark(self) -> List[BenchmarkResult]:
        """Run cryptographic algorithm benchmarks"""
        results = []
        
        # Test different algorithms
        algorithms = ["aes-128-cbc", "aes-256-cbc", "sha256", "sha512", "rsa2048", "ecdsa"]
        
        for algo in algorithms:
            try:
                cmd = ["openssl", "speed", "-seconds", "5", algo]
                
                if self.verbose:
                    logger.info(f"Running crypto benchmark for {algo}")
                
                result = subprocess.run(
                    cmd,
                    cwd=self.openssl_dir,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode == 0:
                    # Parse algorithm-specific results
                    algo_results = self._parse_algorithm_output(result.stdout, algo)
                    results.extend(algo_results)
                else:
                    logger.warning(f"Crypto benchmark failed for {algo}: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                logger.warning(f"Crypto benchmark timed out for {algo}")
            except Exception as e:
                logger.error(f"Crypto benchmark error for {algo}: {e}")
        
        return results
    
    def _parse_algorithm_output(self, output: str, algorithm: str) -> List[BenchmarkResult]:
        """Parse algorithm-specific benchmark output"""
        results = []
        lines = output.strip().split('\n')
        
        for line in lines:
            if algorithm in line.lower():
                parts = line.split()
                if len(parts) >= 2:
                    try:
                        score = float(parts[1])
                        unit = "ops/sec" if "sign" in line.lower() or "verify" in line.lower() else "bytes/sec"
                        results.append(BenchmarkResult(
                            name=f"{algorithm}_{parts[0]}",
                            score=score,
                            unit=unit,
                            iterations=self.iterations,
                            duration=5.0
                        ))
                    except (ValueError, IndexError):
                        continue
        
        return results
    
    def _compare_with_baseline(self, results: List[BenchmarkResult]) -> Optional[ComparisonResult]:
        """Compare results with baseline"""
        if not self.baseline:
            return None
        
        try:
            baseline_file = Path(self.baseline)
            if not baseline_file.exists():
                logger.warning(f"Baseline file not found: {baseline_file}")
                return None
            
            with open(baseline_file, 'r') as f:
                baseline_data = json.load(f)
            
            baseline_results = {}
            for result in baseline_data.get('benchmark_results', []):
                baseline_results[result['name']] = result['score']
            
            improvements = []
            regressions = []
            
            for result in results:
                if result.name in baseline_results:
                    baseline_score = baseline_results[result.name]
                    improvement = (result.score - baseline_score) / baseline_score * 100
                    
                    if improvement > 5:  # 5% improvement threshold
                        improvements.append(f"{result.name}: +{improvement:.1f}%")
                    elif improvement < -5:  # 5% regression threshold
                        regressions.append(f"{result.name}: {improvement:.1f}%")
            
            summary = f"Found {len(improvements)} improvements and {len(regressions)} regressions"
            
            return ComparisonResult(
                summary=summary,
                improvements=improvements,
                regressions=regressions
            )
            
        except Exception as e:
            logger.error(f"Comparison failed: {e}")
            return None
    
    def _save_results(self, results: List[BenchmarkResult], comparison: Optional[ComparisonResult]) -> str:
        """Save benchmark results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if self.format == "json":
            output_file = self.output_dir / f"benchmark_results_{timestamp}.json"
            
            data = {
                "timestamp": datetime.now().isoformat(),
                "benchmark_results": [
                    {
                        "name": r.name,
                        "score": r.score,
                        "unit": r.unit,
                        "iterations": r.iterations,
                        "duration": r.duration
                    }
                    for r in results
                ]
            }
            
            if comparison:
                data["comparison"] = {
                    "summary": comparison.summary,
                    "improvements": comparison.improvements,
                    "regressions": comparison.regressions
                }
            
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)
        
        elif self.format == "csv":
            output_file = self.output_dir / f"benchmark_results_{timestamp}.csv"
            
            with open(output_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["name", "score", "unit", "iterations", "duration"])
                
                for result in results:
                    writer.writerow([result.name, result.score, result.unit, 
                                   result.iterations, result.duration])
        
        return str(output_file)
    
    def run(self) -> BenchmarkRunResult:
        """Execute OpenSSL benchmarks"""
        start_time = time.time()
        all_results = []
        
        try:
            # Check if OpenSSL is available
            result = subprocess.run(
                ["openssl", "version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return BenchmarkRunResult(
                    success=False,
                    error="OpenSSL not found or not working"
                )
            
            # Run requested benchmarks
            if "speed" in self.benchmarks or "all" in self.benchmarks:
                speed_results = self._run_speed_benchmark()
                all_results.extend(speed_results)
            
            if "memory" in self.benchmarks or "all" in self.benchmarks:
                memory_results = self._run_memory_benchmark()
                all_results.extend(memory_results)
            
            if "crypto" in self.benchmarks or "all" in self.benchmarks:
                crypto_results = self._run_crypto_benchmark()
                all_results.extend(crypto_results)
            
            total_time = time.time() - start_time
            
            # Compare with baseline if provided
            comparison = self._compare_with_baseline(all_results)
            
            # Save results
            output_file = self._save_results(all_results, comparison)
            
            return BenchmarkRunResult(
                success=True,
                output_dir=str(self.output_dir),
                benchmark_results=all_results,
                total_time=total_time,
                comparison_results=comparison
            )
            
        except Exception as e:
            return BenchmarkRunResult(
                success=False,
                error=f"Benchmark execution failed: {str(e)}"
            )


def main():
    """Main function for standalone execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="OpenSSL Benchmark Runner")
    parser.add_argument("--profile", "-p", help="Conan profile to use")
    parser.add_argument("--build-dir", help="Build directory")
    parser.add_argument("--openssl-dir", help="OpenSSL source directory")
    parser.add_argument("--output-dir", help="Benchmark output directory")
    parser.add_argument("--benchmarks", nargs="+", 
                       choices=["speed", "memory", "crypto", "ssl", "all"], 
                       default=["all"], help="Benchmark types to run")
    parser.add_argument("--iterations", type=int, default=1000, help="Number of iterations")
    parser.add_argument("--format", choices=["json", "csv", "html", "markdown"], 
                       default="json", help="Output format")
    parser.add_argument("--compare", help="Compare with previous results")
    parser.add_argument("--baseline", help="Baseline benchmark file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Create runner
    runner = OpenSSLBenchmarkRunner(
        conan_api=None,  # Not needed for standalone
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
        print("✅ OpenSSL benchmarks completed successfully")
        print(f"Output directory: {result.output_dir}")
        print(f"Benchmarks run: {len(result.benchmark_results)}")
        print(f"Total execution time: {result.total_time:.2f} seconds")
        if result.comparison_results:
            print(f"Performance comparison: {result.comparison_results.summary}")
        if args.verbose:
            for benchmark in result.benchmark_results:
                print(f"  - {benchmark.name}: {benchmark.score}")
    else:
        print(f"❌ OpenSSL benchmarks failed: {result.error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
