#!/usr/bin/env python3
"""
OpenSSL Tools - Fuzz Corpora Integration
Integrates fuzz-corpora dependency for fuzzing tests.
"""

import subprocess
import os
import logging
import json
import shutil
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import tempfile
import time
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FuzzCorporaManager:
    """Manages fuzz-corpora dependency and fuzzing operations."""
    
    def __init__(self, corpora_repo: str = None, local_path: Optional[Path] = None):
        self.corpora_repo = corpora_repo or "https://github.com/sparesparrow/fuzz-corpora"
        self.local_path = local_path or Path.cwd() / "fuzz-corpora"
        self.corpus_dir = self.local_path / "corpus"
        self.results_dir = Path.cwd() / "fuzz-results"
        self.results_dir.mkdir(exist_ok=True)
        
    def setup_fuzz_dependency(self, force_clone: bool = False) -> bool:
        """
        Set up fuzz-corpora as a build dependency.
        
        Args:
            force_clone: If True, force re-clone the repository
            
        Returns:
            bool: True if setup was successful
        """
        try:
            # Clone or update the repository
            if not self.local_path.exists() or force_clone:
                if self.local_path.exists():
                    logger.info("Removing existing fuzz-corpora directory")
                    shutil.rmtree(self.local_path)
                    
                logger.info(f"Cloning fuzz-corpora from {self.corpora_repo}")
                subprocess.run([
                    "git", "clone", self.corpora_repo, str(self.local_path)
                ], check=True)
            else:
                # Update existing repository
                logger.info("Updating fuzz-corpora repository")
                subprocess.run([
                    "git", "pull", "origin", "main"
                ], cwd=self.local_path, check=True)
                
            # Verify corpus directory exists
            if not self.corpus_dir.exists():
                logger.error("Corpus directory not found in fuzz-corpora")
                return False
                
            # Install required fuzzing tools
            self._install_fuzzing_tools()
            
            # Export as Conan package
            self._export_conan_package()
            
            logger.info("Fuzz-corpora dependency set up successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to set up fuzz-corpora dependency: {e}")
            return False
            
    def _install_fuzzing_tools(self):
        """Install required fuzzing tools."""
        tools_to_install = [
            ("python3-pip", "pip"),
            ("python3-dev", "python3-dev"),
            ("clang", "clang"),
            ("llvm", "llvm")
        ]
        
        for package, tool in tools_to_install:
            if not shutil.which(tool):
                logger.info(f"Installing {package}")
                try:
                    subprocess.run([
                        "sudo", "apt-get", "install", "-y", package
                    ], check=True)
                except subprocess.CalledProcessError:
                    logger.warning(f"Failed to install {package}")
                    
        # Install Python fuzzing libraries
        python_packages = [
            "atheris",
            "hypothesis",
            "fuzzingbook"
        ]
        
        for package in python_packages:
            try:
                subprocess.run([
                    "pip3", "install", package
                ], check=True)
                logger.info(f"Installed {package}")
            except subprocess.CalledProcessError:
                logger.warning(f"Failed to install {package}")
                
    def _export_conan_package(self):
        """Export fuzz-corpora as a Conan package."""
        try:
            # Create Conan recipe if it doesn't exist
            conanfile_path = self.local_path / "conanfile.py"
            if not conanfile_path.exists():
                self._create_conan_recipe()
                
            # Export the package
            logger.info("Exporting fuzz-corpora as Conan package")
            subprocess.run([
                "conan", "export", str(self.local_path), "fuzz-corpora/1.0@sparesparrow/stable"
            ], check=True)
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to export Conan package: {e}")
            
    def _create_conan_recipe(self):
        """Create a Conan recipe for fuzz-corpora."""
        conanfile_content = '''
from conans import ConanFile, tools

class FuzzCorporaConan(ConanFile):
    name = "fuzz-corpora"
    version = "1.0"
    description = "Fuzzing corpora for OpenSSL testing"
    url = "https://github.com/sparesparrow/fuzz-corpora"
    license = "MIT"
    exports_sources = "corpus/*"
    
    def package(self):
        self.copy("corpus/*", dst="corpus")
        
    def package_info(self):
        self.cpp_info.libs = []
        self.env_info.FUZZ_CORPUS_DIR = os.path.join(self.package_folder, "corpus")
'''
        
        conanfile_path = self.local_path / "conanfile.py"
        with open(conanfile_path, 'w') as f:
            f.write(conanfile_content)
            
    def run_fuzz_tests(self, target_binary: Path, 
                      timeout: int = 3600,
                      max_crashes: int = 10,
                      corpus_subset: Optional[str] = None) -> Dict:
        """
        Run fuzzing tests on a target binary.
        
        Args:
            target_binary: Path to the target binary to fuzz
            timeout: Maximum fuzzing time in seconds
            max_crashes: Maximum number of crashes to collect
            corpus_subset: Specific corpus subset to use (optional)
            
        Returns:
            Dict with fuzzing results
        """
        if not target_binary.exists():
            logger.error(f"Target binary not found: {target_binary}")
            return {}
            
        if not self.corpus_dir.exists():
            logger.error("Corpus directory not found. Set up fuzz-corpora first.")
            return {}
            
        try:
            # Prepare fuzzing environment
            fuzz_dir = self.results_dir / f"fuzz_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            fuzz_dir.mkdir(exist_ok=True)
            
            # Select corpus directory
            corpus_path = self.corpus_dir
            if corpus_subset:
                corpus_path = self.corpus_dir / corpus_subset
                if not corpus_path.exists():
                    logger.warning(f"Corpus subset not found: {corpus_subset}, using full corpus")
                    corpus_path = self.corpus_dir
                    
            # Run fuzzing with Atheris (Python fuzzing)
            if target_binary.suffix == '.py':
                return self._run_python_fuzzing(target_binary, corpus_path, fuzz_dir, timeout, max_crashes)
            else:
                return self._run_binary_fuzzing(target_binary, corpus_path, fuzz_dir, timeout, max_crashes)
                
        except Exception as e:
            logger.error(f"Failed to run fuzz tests: {e}")
            return {}
            
    def _run_python_fuzzing(self, target_script: Path, corpus_path: Path,
                           fuzz_dir: Path, timeout: int, max_crashes: int) -> Dict:
        """Run Python fuzzing with Atheris."""
        logger.info(f"Running Python fuzzing on {target_script}")
        
        # Create fuzzing wrapper
        fuzz_wrapper = fuzz_dir / "fuzz_wrapper.py"
        wrapper_content = f'''
import atheris
import sys
import os
import json
from pathlib import Path

# Add corpus directory to path
corpus_dir = Path("{corpus_path}")
sys.path.insert(0, str(corpus_dir))

# Import the target module
import {target_script.stem}

def fuzz_function(data):
    """Fuzz function that processes input data."""
    try:
        # Call the target function with the fuzzed data
        {target_script.stem}.process_data(data)
    except Exception as e:
        # Log crashes but don't stop fuzzing
        crash_file = Path("{fuzz_dir}") / f"crash_{{len(list(Path('{fuzz_dir}').glob('crash_*')))}}.txt"
        with open(crash_file, 'w') as f:
            f.write(f"Crash: {{e}}\\nData: {{data[:100]}}")
        print(f"Crash found: {{e}}")

def main():
    atheris.Setup(sys.argv, fuzz_function)
    atheris.Fuzz()

if __name__ == "__main__":
    main()
'''
        
        with open(fuzz_wrapper, 'w') as f:
            f.write(wrapper_content)
            
        # Run fuzzing
        start_time = time.time()
        try:
            result = subprocess.run([
                "python3", str(fuzz_wrapper),
                "-max_total_time", str(timeout),
                "-max_crashes", str(max_crashes),
                str(corpus_path)
            ], cwd=fuzz_dir, capture_output=True, text=True, timeout=timeout + 60)
            
            end_time = time.time()
            
            # Collect results
            crashes = list(fuzz_dir.glob("crash_*.txt"))
            
            return {
                "target": str(target_script),
                "type": "python",
                "duration": end_time - start_time,
                "crashes_found": len(crashes),
                "crash_files": [str(c) for c in crashes],
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
                "corpus_size": len(list(corpus_path.rglob("*")))
            }
            
        except subprocess.TimeoutExpired:
            logger.warning("Fuzzing timed out")
            return {
                "target": str(target_script),
                "type": "python",
                "duration": timeout,
                "crashes_found": len(list(fuzz_dir.glob("crash_*.txt"))),
                "timeout": True
            }
            
    def _run_binary_fuzzing(self, target_binary: Path, corpus_path: Path,
                           fuzz_dir: Path, timeout: int, max_crashes: int) -> Dict:
        """Run binary fuzzing with AFL++ or similar."""
        logger.info(f"Running binary fuzzing on {target_binary}")
        
        # Check if AFL++ is available
        if shutil.which("afl-fuzz"):
            return self._run_afl_fuzzing(target_binary, corpus_path, fuzz_dir, timeout, max_crashes)
        else:
            logger.warning("AFL++ not found, using basic fuzzing approach")
            return self._run_basic_fuzzing(target_binary, corpus_path, fuzz_dir, timeout, max_crashes)
            
    def _run_afl_fuzzing(self, target_binary: Path, corpus_path: Path,
                        fuzz_dir: Path, timeout: int, max_crashes: int) -> Dict:
        """Run AFL++ fuzzing."""
        # Set up AFL environment
        os.environ["AFL_SKIP_CPUFREQ"] = "1"
        
        # Create output directory
        afl_output = fuzz_dir / "afl_output"
        afl_output.mkdir(exist_ok=True)
        
        start_time = time.time()
        
        try:
            # Run AFL++ fuzzing
            result = subprocess.run([
                "afl-fuzz",
                "-i", str(corpus_path),
                "-o", str(afl_output),
                "-t", "1000+",  # Timeout per execution
                "-m", "none",   # No memory limit
                "--", str(target_binary), "@@"
            ], cwd=fuzz_dir, timeout=timeout)
            
            end_time = time.time()
            
            # Collect results
            crashes = list(afl_output.rglob("crashes/*"))
            hangs = list(afl_output.rglob("hangs/*"))
            
            return {
                "target": str(target_binary),
                "type": "afl",
                "duration": end_time - start_time,
                "crashes_found": len(crashes),
                "hangs_found": len(hangs),
                "crash_files": [str(c) for c in crashes],
                "hang_files": [str(h) for h in hangs],
                "return_code": result.returncode,
                "corpus_size": len(list(corpus_path.rglob("*")))
            }
            
        except subprocess.TimeoutExpired:
            logger.warning("AFL fuzzing timed out")
            crashes = list(afl_output.rglob("crashes/*"))
            hangs = list(afl_output.rglob("hangs/*"))
            
            return {
                "target": str(target_binary),
                "type": "afl",
                "duration": timeout,
                "crashes_found": len(crashes),
                "hangs_found": len(hangs),
                "timeout": True
            }
            
    def _run_basic_fuzzing(self, target_binary: Path, corpus_path: Path,
                          fuzz_dir: Path, timeout: int, max_crashes: int) -> Dict:
        """Run basic fuzzing without specialized tools."""
        logger.info("Running basic fuzzing")
        
        crashes = []
        start_time = time.time()
        test_count = 0
        
        # Get all test files from corpus
        test_files = list(corpus_path.rglob("*"))
        
        try:
            for test_file in test_files:
                if time.time() - start_time > timeout:
                    break
                    
                if len(crashes) >= max_crashes:
                    break
                    
                if test_file.is_file():
                    test_count += 1
                    
                    # Run the binary with the test file
                    try:
                        result = subprocess.run([
                            str(target_binary), str(test_file)
                        ], capture_output=True, text=True, timeout=10)
                        
                        # Check for crashes (non-zero exit code)
                        if result.returncode != 0:
                            crash_file = fuzz_dir / f"crash_{len(crashes)}.txt"
                            with open(crash_file, 'w') as f:
                                f.write(f"Test file: {test_file}\n")
                                f.write(f"Return code: {result.returncode}\n")
                                f.write(f"Stdout: {result.stdout}\n")
                                f.write(f"Stderr: {result.stderr}\n")
                            crashes.append(crash_file)
                            
                    except subprocess.TimeoutExpired:
                        # Treat timeouts as hangs
                        hang_file = fuzz_dir / f"hang_{len(crashes)}.txt"
                        with open(hang_file, 'w') as f:
                            f.write(f"Test file: {test_file}\n")
                            f.write("Timeout after 10 seconds\n")
                        crashes.append(hang_file)
                        
            end_time = time.time()
            
            return {
                "target": str(target_binary),
                "type": "basic",
                "duration": end_time - start_time,
                "crashes_found": len(crashes),
                "crash_files": [str(c) for c in crashes],
                "tests_run": test_count,
                "corpus_size": len(test_files)
            }
            
        except Exception as e:
            logger.error(f"Basic fuzzing failed: {e}")
            return {}
            
    def analyze_fuzz_results(self, results: Dict) -> Dict:
        """
        Analyze fuzzing results and generate report.
        
        Args:
            results: Fuzzing results dictionary
            
        Returns:
            Dict with analysis results
        """
        analysis = {
            "summary": {
                "target": results.get("target", "unknown"),
                "type": results.get("type", "unknown"),
                "duration": results.get("duration", 0),
                "crashes_found": results.get("crashes_found", 0),
                "hangs_found": results.get("hangs_found", 0),
                "tests_run": results.get("tests_run", 0),
                "corpus_size": results.get("corpus_size", 0)
            },
            "severity": "low",
            "recommendations": []
        }
        
        # Determine severity
        crash_count = results.get("crashes_found", 0)
        hang_count = results.get("hangs_found", 0)
        
        if crash_count > 10 or hang_count > 5:
            analysis["severity"] = "high"
        elif crash_count > 5 or hang_count > 2:
            analysis["severity"] = "medium"
            
        # Generate recommendations
        if crash_count > 0:
            analysis["recommendations"].append("Review and fix crash-causing inputs")
        if hang_count > 0:
            analysis["recommendations"].append("Investigate timeout/hang conditions")
        if results.get("tests_run", 0) < 100:
            analysis["recommendations"].append("Increase corpus size for better coverage")
            
        return analysis
        
    def generate_fuzz_report(self, results: Dict, output_path: Optional[Path] = None) -> Path:
        """
        Generate a detailed fuzzing report.
        
        Args:
            results: Fuzzing results
            output_path: Path to save the report (optional)
            
        Returns:
            Path to the generated report
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.results_dir / f"fuzz_report_{timestamp}.json"
            
        analysis = self.analyze_fuzz_results(results)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "results": results,
            "analysis": analysis,
            "environment": {
                "corpus_repo": self.corpora_repo,
                "corpus_path": str(self.corpus_dir),
                "python_version": subprocess.check_output(["python3", "--version"]).decode().strip()
            }
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        logger.info(f"Generated fuzz report: {output_path}")
        return output_path


def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="OpenSSL Fuzz Corpora Integration")
    parser.add_argument("--corpora-repo", help="Fuzz-corpora repository URL")
    parser.add_argument("--local-path", type=Path, help="Local path for fuzz-corpora")
    parser.add_argument("--setup", action="store_true", help="Set up fuzz-corpora dependency")
    parser.add_argument("--fuzz", type=Path, help="Run fuzzing on target binary")
    parser.add_argument("--timeout", type=int, default=3600, help="Fuzzing timeout in seconds")
    parser.add_argument("--max-crashes", type=int, default=10, help="Maximum crashes to collect")
    parser.add_argument("--corpus-subset", help="Use specific corpus subset")
    parser.add_argument("--report", type=Path, help="Generate fuzzing report")
    
    args = parser.parse_args()
    
    manager = FuzzCorporaManager(
        corpora_repo=args.corpora_repo,
        local_path=args.local_path
    )
    
    if args.setup:
        success = manager.setup_fuzz_dependency()
        if not success:
            sys.exit(1)
            
    if args.fuzz:
        results = manager.run_fuzz_tests(
            args.fuzz,
            timeout=args.timeout,
            max_crashes=args.max_crashes,
            corpus_subset=args.corpus_subset
        )
        
        if results:
            print(f"Fuzzing completed:")
            print(f"  Target: {results.get('target')}")
            print(f"  Duration: {results.get('duration', 0):.1f} seconds")
            print(f"  Crashes found: {results.get('crashes_found', 0)}")
            print(f"  Hangs found: {results.get('hangs_found', 0)}")
            
            # Generate report if requested
            if args.report:
                manager.generate_fuzz_report(results, args.report)
        else:
            print("Fuzzing failed")
            sys.exit(1)


if __name__ == "__main__":
    import sys
    main()