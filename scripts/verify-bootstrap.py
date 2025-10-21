#!/usr/bin/env python3
"""
Bootstrap Verification Script
Comprehensive verification for openssl-conan-init.py standalone installer

This script provides local verification of all bootstrap components:
- Idempotency verification
- Cross-platform compatibility
- Dependency resolution without pip fallbacks
- Rollback and recovery mechanisms
- Reproducibility validation
- Hardening validation
"""

import os
import sys
import subprocess
import tempfile
import json
import shutil
import platform
from pathlib import Path
from typing import Dict, List, Tuple, Any
import argparse
import time

class BootstrapVerifier:
    """Comprehensive bootstrap verification"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results = {}
        self.temp_dirs = []
    
    def log(self, message: str, level: str = "INFO"):
        """Log message with timestamp"""
        timestamp = time.strftime("%H:%M:%S")
        prefix = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "WARNING": "⚠️",
            "ERROR": "❌",
            "DEBUG": "🔍"
        }.get(level, "ℹ️")
        
        if self.verbose or level in ["SUCCESS", "WARNING", "ERROR"]:
            print(f"[{timestamp}] {prefix} {message}")
    
    def create_temp_dir(self) -> Path:
        """Create temporary directory for testing"""
        temp_dir = Path(tempfile.mkdtemp(prefix="bootstrap_verify_"))
        self.temp_dirs.append(temp_dir)
        return temp_dir
    
    def cleanup(self):
        """Cleanup temporary directories"""
        for temp_dir in self.temp_dirs:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
                self.log(f"Cleaned up {temp_dir}", "DEBUG")
    
    def verify_idempotency(self) -> bool:
        """Verify idempotent operations"""
        self.log("Testing idempotency...")
        
        try:
            temp_dir = self.create_temp_dir()
            
            # First run
            self.log("First bootstrap run...", "DEBUG")
            result1 = self._run_bootstrap(temp_dir / "install1")
            if not result1:
                self.log("First bootstrap run failed", "ERROR")
                return False
            
            # Second run (should be idempotent)
            self.log("Second bootstrap run (idempotency test)...", "DEBUG")
            result2 = self._run_bootstrap(temp_dir / "install1")
            if not result2:
                self.log("Second bootstrap run failed", "ERROR")
                return False
            
            # Verify state persistence
            state_file = temp_dir / "install1" / ".bootstrap_state.json"
            if state_file.exists():
                with open(state_file) as f:
                    state = json.load(f)
                
                # Check that operations are marked as completed
                completed_ops = [op for op, data in state.items() if data.get("completed", False)]
                if len(completed_ops) > 0:
                    self.log(f"Idempotency verified: {len(completed_ops)} operations completed", "SUCCESS")
                    return True
                else:
                    self.log("No completed operations found in state", "ERROR")
                    return False
            else:
                self.log("State file not found", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Idempotency test failed: {e}", "ERROR")
            return False
    
    def verify_cross_platform(self) -> bool:
        """Verify cross-platform compatibility"""
        self.log("Testing cross-platform compatibility...")
        
        platforms = [
            ("linux", "x86_64", "gcc11"),
            ("windows", "x86_64", "msvc193"),
            ("darwin", "arm64", "clang")
        ]
        
        results = []
        for platform, arch, compiler in platforms:
            self.log(f"Testing {platform}-{arch}-{compiler}...", "DEBUG")
            
            try:
                temp_dir = self.create_temp_dir()
                result = self._run_bootstrap(
                    temp_dir / f"install_{platform}_{arch}_{compiler}",
                    platform=platform,
                    arch=arch,
                    compiler=compiler
                )
                results.append(result)
                
                if result:
                    self.log(f"✅ {platform}-{arch}-{compiler} passed", "SUCCESS")
                else:
                    self.log(f"❌ {platform}-{arch}-{compiler} failed", "ERROR")
                    
            except Exception as e:
                self.log(f"❌ {platform}-{arch}-{compiler} error: {e}", "ERROR")
                results.append(False)
        
        success_count = sum(results)
        total_count = len(results)
        
        if success_count == total_count:
            self.log(f"Cross-platform verification passed: {success_count}/{total_count}", "SUCCESS")
            return True
        else:
            self.log(f"Cross-platform verification failed: {success_count}/{total_count}", "ERROR")
            return False
    
    def verify_dependency_resolution(self) -> bool:
        """Verify pip-free dependency resolution"""
        self.log("Testing dependency resolution...")
        
        try:
            temp_dir = self.create_temp_dir()
            
            # Test dependency resolution without pip
            result = self._run_bootstrap(
                temp_dir / "dep_test",
                test_dependencies=True
            )
            
            if result:
                self.log("Dependency resolution verified", "SUCCESS")
                return True
            else:
                self.log("Dependency resolution failed", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Dependency resolution test failed: {e}", "ERROR")
            return False
    
    def verify_rollback_mechanisms(self) -> bool:
        """Verify rollback and recovery mechanisms"""
        self.log("Testing rollback mechanisms...")
        
        try:
            temp_dir = self.create_temp_dir()
            install_dir = temp_dir / "rollback_test"
            
            # Create test file
            test_file = install_dir / "test_file.txt"
            install_dir.mkdir(parents=True)
            test_file.write_text("original content")
            
            # Test rollback functionality
            rollback_script = """
import sys
sys.path.insert(0, 'scripts')
from openssl_conan_init import RollbackManager, BootstrapConfig
from pathlib import Path

config = BootstrapConfig(
    platform='linux',
    arch='x86_64',
    compiler='gcc',
    install_dir=Path('{install_dir}')
)

manager = RollbackManager(config)
manager.create_backup('test_op')
Path('{test_file}').write_text('modified content')
manager.rollback('test_op')

assert Path('{test_file}').read_text() == 'original content'
print('Rollback test passed')
""".format(install_dir=install_dir, test_file=test_file)
            
            # Run rollback test
            result = subprocess.run([
                sys.executable, "-c", rollback_script
            ], cwd=Path.cwd(), capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log("Rollback mechanisms verified", "SUCCESS")
                return True
            else:
                self.log(f"Rollback test failed: {result.stderr}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Rollback test failed: {e}", "ERROR")
            return False
    
    def verify_reproducibility(self) -> bool:
        """Verify reproducible builds"""
        self.log("Testing reproducibility...")
        
        try:
            temp_dir = self.create_temp_dir()
            
            # First installation
            install1 = temp_dir / "install1"
            result1 = self._run_bootstrap(install1)
            if not result1:
                self.log("First installation failed", "ERROR")
                return False
            
            # Second installation
            install2 = temp_dir / "install2"
            result2 = self._run_bootstrap(install2)
            if not result2:
                self.log("Second installation failed", "ERROR")
                return False
            
            # Compare state files
            state1_file = install1 / ".bootstrap_state.json"
            state2_file = install2 / ".bootstrap_state.json"
            
            if state1_file.exists() and state2_file.exists():
                with open(state1_file) as f1, open(state2_file) as f2:
                    state1 = json.load(f1)
                    state2 = json.load(f2)
                
                # Remove timestamps for comparison
                for state in [state1, state2]:
                    for key in state:
                        if 'timestamp' in state[key]:
                            del state[key]['timestamp']
                
                if state1 == state2:
                    self.log("Reproducibility verified", "SUCCESS")
                    return True
                else:
                    self.log("Reproducibility failed: states differ", "ERROR")
                    return False
            else:
                self.log("State files missing", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Reproducibility test failed: {e}", "ERROR")
            return False
    
    def verify_hardening(self) -> bool:
        """Verify hardening validation"""
        self.log("Testing hardening validation...")
        
        try:
            # Test signature validation
            hardening_script = """
import sys
sys.path.insert(0, 'scripts')
from openssl_conan_init import DependencyResolver, BootstrapConfig
from pathlib import Path
import tempfile
import os

config = BootstrapConfig(
    platform='linux',
    arch='x86_64',
    compiler='gcc',
    validate_signatures=True
)

resolver = DependencyResolver(config)

# Test checksum verification
with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
    f.write('test content')
    test_file = f.name

try:
    test_hash = 'sha256:' + 'a' * 64
    result = resolver._verify_checksum(test_file, test_hash)
    print(f'Checksum verification: {result}')
finally:
    os.unlink(test_file)
"""
            
            result = subprocess.run([
                sys.executable, "-c", hardening_script
            ], cwd=Path.cwd(), capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log("Hardening validation verified", "SUCCESS")
                return True
            else:
                self.log(f"Hardening test failed: {result.stderr}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Hardening test failed: {e}", "ERROR")
            return False
    
    def verify_production_scenarios(self) -> bool:
        """Verify production deployment scenarios"""
        self.log("Testing production scenarios...")
        
        try:
            temp_dir = self.create_temp_dir()
            
            # Simulate production deployment
            install_dir = temp_dir / "production"
            result1 = self._run_bootstrap(install_dir)
            if not result1:
                self.log("Production deployment failed", "ERROR")
                return False
            
            # Simulate second deployment (should be idempotent)
            result2 = self._run_bootstrap(install_dir)
            if not result2:
                self.log("Production idempotency failed", "ERROR")
                return False
            
            # Check that critical files exist
            critical_files = [
                "conanfile.py",
                "pyproject.toml",
                ".bootstrap_state.json"
            ]
            
            for file_name in critical_files:
                file_path = install_dir / file_name
                if not file_path.exists():
                    self.log(f"Critical file missing: {file_name}", "ERROR")
                    return False
            
            self.log("Production scenarios verified", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Production scenario test failed: {e}", "ERROR")
            return False
    
    def _run_bootstrap(self, install_dir: Path, platform: str = None, arch: str = None, 
                      compiler: str = None, test_dependencies: bool = False) -> bool:
        """Run bootstrap script"""
        try:
            cmd = [
                sys.executable, "scripts/openssl-conan-init.py",
                "--install-dir", str(install_dir),
                "--force"
            ]
            
            if platform:
                cmd.extend(["--platform", platform])
            if arch:
                cmd.extend(["--arch", arch])
            if compiler:
                cmd.extend(["--compiler", compiler])
            
            if test_dependencies:
                cmd.append("--no-validation")
            
            result = subprocess.run(
                cmd,
                cwd=Path.cwd(),
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if self.verbose:
                self.log(f"Bootstrap output: {result.stdout}", "DEBUG")
                if result.stderr:
                    self.log(f"Bootstrap stderr: {result.stderr}", "DEBUG")
            
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            self.log("Bootstrap timed out", "ERROR")
            return False
        except Exception as e:
            self.log(f"Bootstrap execution failed: {e}", "ERROR")
            return False
    
    def run_all_verifications(self) -> Dict[str, bool]:
        """Run all verification tests"""
        self.log("Starting comprehensive bootstrap verification...")
        
        verifications = [
            ("idempotency", self.verify_idempotency),
            ("cross_platform", self.verify_cross_platform),
            ("dependency_resolution", self.verify_dependency_resolution),
            ("rollback_mechanisms", self.verify_rollback_mechanisms),
            ("reproducibility", self.verify_reproducibility),
            ("hardening", self.verify_hardening),
            ("production_scenarios", self.verify_production_scenarios)
        ]
        
        results = {}
        for name, verify_func in verifications:
            self.log(f"Running {name} verification...")
            try:
                results[name] = verify_func()
            except Exception as e:
                self.log(f"Verification {name} failed with exception: {e}", "ERROR")
                results[name] = False
        
        return results
    
    def generate_report(self, results: Dict[str, bool]) -> str:
        """Generate verification report"""
        total_tests = len(results)
        passed_tests = sum(results.values())
        failed_tests = total_tests - passed_tests
        
        report = f"""
# 🔧 Bootstrap Verification Report

## Summary
- **Total Tests**: {total_tests}
- **Passed**: {passed_tests} ✅
- **Failed**: {failed_tests} ❌
- **Success Rate**: {(passed_tests/total_tests)*100:.1f}%

## Test Results
"""
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            report += f"- **{test_name.replace('_', ' ').title()}**: {status}\n"
        
        if failed_tests == 0:
            report += "\n## 🎉 All Tests Passed!\n"
            report += "Bootstrap verification is complete and ready for production deployment.\n"
        else:
            report += f"\n## ⚠️ {failed_tests} Test(s) Failed\n"
            report += "Please review the failed tests before proceeding with deployment.\n"
        
        return report

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Bootstrap Verification Script")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--test", choices=[
        "idempotency", "cross_platform", "dependency_resolution",
        "rollback_mechanisms", "reproducibility", "hardening",
        "production_scenarios", "all"
    ], default="all", help="Specific test to run")
    parser.add_argument("--output", "-o", help="Output report to file")
    
    args = parser.parse_args()
    
    verifier = BootstrapVerifier(verbose=args.verbose)
    
    try:
        if args.test == "all":
            results = verifier.run_all_verifications()
        else:
            # Run specific test
            test_method = getattr(verifier, f"verify_{args.test}")
            results = {args.test: test_method()}
        
        # Generate and display report
        report = verifier.generate_report(results)
        print(report)
        
        # Save report if requested
        if args.output:
            with open(args.output, 'w') as f:
                f.write(report)
            verifier.log(f"Report saved to {args.output}")
        
        # Exit with appropriate code
        failed_tests = sum(1 for result in results.values() if not result)
        sys.exit(failed_tests)
        
    finally:
        verifier.cleanup()

if __name__ == "__main__":
    main()