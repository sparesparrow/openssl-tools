#!/usr/bin/env python3
"""
OpenSSL Performance Testing Script
Based on ngapy-dev patterns for comprehensive performance validation
"""

import argparse
import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml


class PerformanceTestHarness:
    """Performance testing harness for OpenSSL"""
    
    def __init__(self, results_dir: Optional[Path] = None):
        self.results_dir = results_dir or Path("performance_results")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        self.results = {}
        self.baseline_results = {}
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def run_openssl_speed_test(self, algorithm: str, iterations: int = 1000) -> Dict:
        """Run OpenSSL speed test for a specific algorithm"""
        self.logger.info(f"Running speed test for {algorithm}")
        
        try:
            # Run OpenSSL speed command
            cmd = ["openssl", "speed", "-seconds", "10", algorithm]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode != 0:
                self.logger.error(f"Speed test failed for {algorithm}: {result.stderr}")
                return {"error": result.stderr}
                
            # Parse results
            results = self._parse_speed_output(result.stdout, algorithm)
            self.logger.info(f"Speed test completed for {algorithm}")
            return results
            
        except subprocess.TimeoutExpired:
            self.logger.error(f"Speed test timed out for {algorithm}")
            return {"error": "timeout"}
        except Exception as e:
            self.logger.error(f"Speed test failed for {algorithm}: {e}")
            return {"error": str(e)}
            
    def _parse_speed_output(self, output: str, algorithm: str) -> Dict:
        """Parse OpenSSL speed test output"""
        lines = output.split('\n')
        results = {"algorithm": algorithm, "timestamp": datetime.now().isoformat()}
        
        for line in lines:
            if algorithm in line and "sign" in line:
                # Parse signing performance
                parts = line.split()
                if len(parts) >= 4:
                    results["sign_operations"] = int(parts[1])
                    results["sign_time"] = float(parts[2])
                    results["sign_per_second"] = float(parts[3])
                    
            elif algorithm in line and "verify" in line:
                # Parse verification performance
                parts = line.split()
                if len(parts) >= 4:
                    results["verify_operations"] = int(parts[1])
                    results["verify_time"] = float(parts[2])
                    results["verify_per_second"] = float(parts[3])
                    
            elif algorithm in line and "kbytes" in line:
                # Parse throughput
                parts = line.split()
                if len(parts) >= 4:
                    results["kbytes"] = int(parts[1])
                    results["time"] = float(parts[2])
                    results["kbytes_per_second"] = float(parts[3])
                    
        return results
        
    def run_crypto_benchmark(self, test_config: Dict) -> Dict:
        """Run comprehensive crypto benchmark"""
        self.logger.info("Running comprehensive crypto benchmark")
        
        algorithms = test_config.get("algorithms", [
            "rsa", "dsa", "ecdsa", "aes-128-cbc", "aes-256-cbc",
            "sha256", "sha512", "md5"
        ])
        
        benchmark_results = {
            "timestamp": datetime.now().isoformat(),
            "algorithms": {}
        }
        
        for algorithm in algorithms:
            self.logger.info(f"Benchmarking {algorithm}")
            results = self.run_openssl_speed_test(algorithm)
            benchmark_results["algorithms"][algorithm] = results
            
        return benchmark_results
        
    def run_memory_usage_test(self) -> Dict:
        """Test memory usage during crypto operations"""
        self.logger.info("Running memory usage test")
        
        try:
            # Use OpenSSL speed with memory monitoring
            cmd = ["openssl", "speed", "-seconds", "5", "rsa", "aes-128-cbc"]
            
            # Start process and monitor memory
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Monitor memory usage
            memory_samples = []
            start_time = time.time()
            
            while process.poll() is None and (time.time() - start_time) < 30:
                try:
                    # Get memory usage (simplified)
                    memory_info = self._get_memory_usage()
                    memory_samples.append({
                        "timestamp": time.time() - start_time,
                        "memory_mb": memory_info
                    })
                    time.sleep(0.1)
                except Exception as e:
                    self.logger.warning(f"Memory monitoring error: {e}")
                    
            # Wait for process to complete
            stdout, stderr = process.communicate(timeout=10)
            
            return {
                "timestamp": datetime.now().isoformat(),
                "memory_samples": memory_samples,
                "max_memory_mb": max(sample["memory_mb"] for sample in memory_samples) if memory_samples else 0,
                "avg_memory_mb": sum(sample["memory_mb"] for sample in memory_samples) / len(memory_samples) if memory_samples else 0
            }
            
        except Exception as e:
            self.logger.error(f"Memory usage test failed: {e}")
            return {"error": str(e)}
            
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            # Fallback method
            return 0.0
            
    def run_concurrent_test(self, num_threads: int = 4) -> Dict:
        """Test performance under concurrent load"""
        self.logger.info(f"Running concurrent test with {num_threads} threads")
        
        try:
            import threading
            import queue
            
            results_queue = queue.Queue()
            threads = []
            
            def worker_thread(thread_id: int):
                """Worker thread for concurrent testing"""
                try:
                    start_time = time.time()
                    result = subprocess.run(
                        ["openssl", "speed", "-seconds", "5", "rsa"],
                        capture_output=True,
                        text=True,
                        timeout=60
                    )
                    end_time = time.time()
                    
                    results_queue.put({
                        "thread_id": thread_id,
                        "success": result.returncode == 0,
                        "duration": end_time - start_time,
                        "output": result.stdout
                    })
                except Exception as e:
                    results_queue.put({
                        "thread_id": thread_id,
                        "success": False,
                        "error": str(e)
                    })
                    
            # Start threads
            start_time = time.time()
            for i in range(num_threads):
                thread = threading.Thread(target=worker_thread, args=(i,))
                threads.append(thread)
                thread.start()
                
            # Wait for all threads to complete
            for thread in threads:
                thread.join(timeout=120)
                
            end_time = time.time()
            
            # Collect results
            thread_results = []
            while not results_queue.empty():
                thread_results.append(results_queue.get())
                
            successful_threads = sum(1 for r in thread_results if r.get("success", False))
            
            return {
                "timestamp": datetime.now().isoformat(),
                "num_threads": num_threads,
                "total_duration": end_time - start_time,
                "successful_threads": successful_threads,
                "thread_results": thread_results
            }
            
        except Exception as e:
            self.logger.error(f"Concurrent test failed: {e}")
            return {"error": str(e)}
            
    def compare_with_baseline(self, current_results: Dict, baseline_file: Path) -> Dict:
        """Compare current results with baseline"""
        if not baseline_file.exists():
            self.logger.warning(f"Baseline file not found: {baseline_file}")
            return {"error": "baseline_not_found"}
            
        try:
            with open(baseline_file, 'r') as f:
                baseline = json.load(f)
                
            comparison = {
                "timestamp": datetime.now().isoformat(),
                "baseline_file": str(baseline_file),
                "comparisons": {}
            }
            
            # Compare algorithm performance
            if "algorithms" in current_results and "algorithms" in baseline:
                for algorithm in current_results["algorithms"]:
                    if algorithm in baseline["algorithms"]:
                        current = current_results["algorithms"][algorithm]
                        baseline_alg = baseline["algorithms"][algorithm]
                        
                        comparison["comparisons"][algorithm] = {}
                        
                        # Compare key metrics
                        for metric in ["sign_per_second", "verify_per_second", "kbytes_per_second"]:
                            if metric in current and metric in baseline_alg:
                                current_val = current[metric]
                                baseline_val = baseline_alg[metric]
                                
                                if baseline_val > 0:
                                    improvement = ((current_val - baseline_val) / baseline_val) * 100
                                    comparison["comparisons"][algorithm][metric] = {
                                        "current": current_val,
                                        "baseline": baseline_val,
                                        "improvement_percent": improvement
                                    }
                                    
            return comparison
            
        except Exception as e:
            self.logger.error(f"Baseline comparison failed: {e}")
            return {"error": str(e)}
            
    def save_results(self, results: Dict, filename: str):
        """Save test results to file"""
        results_path = self.results_dir / filename
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2)
        self.logger.info(f"Results saved to {results_path}")
        
    def generate_report(self, results: Dict) -> Path:
        """Generate performance test report"""
        report_path = self.results_dir / f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = {
            "test_suite": "OpenSSL Performance Tests",
            "timestamp": datetime.now().isoformat(),
            "results": results,
            "summary": self._generate_summary(results)
        }
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        self.logger.info(f"Performance report generated: {report_path}")
        return report_path
        
    def _generate_summary(self, results: Dict) -> Dict:
        """Generate test summary"""
        summary = {
            "total_tests": 0,
            "successful_tests": 0,
            "failed_tests": 0,
            "performance_metrics": {}
        }
        
        if "algorithms" in results:
            summary["total_tests"] = len(results["algorithms"])
            summary["successful_tests"] = sum(
                1 for alg in results["algorithms"].values() 
                if "error" not in alg
            )
            summary["failed_tests"] = summary["total_tests"] - summary["successful_tests"]
            
            # Calculate average performance
            total_sign_per_sec = 0
            total_verify_per_sec = 0
            count = 0
            
            for alg in results["algorithms"].values():
                if "error" not in alg:
                    if "sign_per_second" in alg:
                        total_sign_per_sec += alg["sign_per_second"]
                    if "verify_per_second" in alg:
                        total_verify_per_sec += alg["verify_per_second"]
                    count += 1
                    
            if count > 0:
                summary["performance_metrics"] = {
                    "avg_sign_per_second": total_sign_per_sec / count,
                    "avg_verify_per_second": total_verify_per_sec / count
                }
                
        return summary


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='OpenSSL Performance Tests')
    parser.add_argument('--config', type=Path, help='Test configuration file')
    parser.add_argument('--results-dir', type=Path, help='Results directory')
    parser.add_argument('--baseline', type=Path, help='Baseline results file')
    parser.add_argument('--algorithms', nargs='+', 
                       default=['rsa', 'aes-128-cbc', 'sha256'],
                       help='Algorithms to test')
    parser.add_argument('--threads', type=int, default=4,
                       help='Number of threads for concurrent test')
    
    args = parser.parse_args()
    
    # Initialize test harness
    harness = PerformanceTestHarness(args.results_dir)
    
    # Load configuration
    config = {}
    if args.config and args.config.exists():
        with open(args.config, 'r') as f:
            config = yaml.safe_load(f)
    else:
        config = {
            "algorithms": args.algorithms,
            "concurrent_threads": args.threads
        }
        
    # Run tests
    all_results = {}
    
    # Crypto benchmark
    harness.logger.info("Running crypto benchmark")
    crypto_results = harness.run_crypto_benchmark(config)
    all_results["crypto_benchmark"] = crypto_results
    
    # Memory usage test
    harness.logger.info("Running memory usage test")
    memory_results = harness.run_memory_usage_test()
    all_results["memory_usage"] = memory_results
    
    # Concurrent test
    harness.logger.info("Running concurrent test")
    concurrent_results = harness.run_concurrent_test(config.get("concurrent_threads", 4))
    all_results["concurrent_test"] = concurrent_results
    
    # Compare with baseline if provided
    if args.baseline:
        harness.logger.info("Comparing with baseline")
        comparison = harness.compare_with_baseline(all_results, args.baseline)
        all_results["baseline_comparison"] = comparison
        
    # Save results
    harness.save_results(all_results, "performance_results.json")
    
    # Generate report
    report_path = harness.generate_report(all_results)
    
    # Print summary
    summary = harness._generate_summary(all_results)
    print(f"\nPerformance Test Summary:")
    print(f"Total tests: {summary['total_tests']}")
    print(f"Successful: {summary['successful_tests']}")
    print(f"Failed: {summary['failed_tests']}")
    
    if summary["performance_metrics"]:
        print(f"Average sign operations/sec: {summary['performance_metrics']['avg_sign_per_second']:.2f}")
        print(f"Average verify operations/sec: {summary['performance_metrics']['avg_verify_per_second']:.2f}")
        
    print(f"Report saved to: {report_path}")
    
    return 0 if summary["failed_tests"] == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
