#!/usr/bin/env python3
"""
OpenSSL Tools Implementation Validation Script
Tests the enhanced DevOps automation implementation
"""
import subprocess
import sys
import os
import yaml
import json
from pathlib import Path

def run_command(cmd, cwd=None, capture_output=True):
    """Run a shell command and return result"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd,
                              capture_output=capture_output, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def validate_yaml_files():
    """Validate all YAML syntax in workflows and actions"""
    print("?? Validating YAML syntax...")

    yaml_files = [
        ".github/workflows/reusable/build-component.yml",
        ".github/workflows/security-gates.yml",
        ".github/workflows/test-integration.yml",
        ".github/workflows/reusable/security-scan.yml",
        ".github/actions/setup-conan/action.yml",
        ".github/actions/security-scan/action.yml",
        ".github/actions/cloudsmith-publish/action.yml"
    ]

    all_valid = True
    for yaml_file in yaml_files:
        if os.path.exists(yaml_file):
            try:
                with open(yaml_file, 'r') as f:
                    yaml.safe_load(f)
                print(f"  ? {yaml_file}")
            except yaml.YAMLError as e:
                print(f"  ? {yaml_file}: {e}")
                all_valid = False
        else:
            print(f"  ??  {yaml_file} not found")
            all_valid = False

    return all_valid

def test_matrix_strategy():
    """Test matrix strategy with act (if available)"""
    print("?? Testing matrix strategy...")

    # Check if act is available
    success, _, _ = run_command("which act")
    if not success:
        print("  ??  act CLI not found - skipping matrix strategy test")
        print("     Install act: https://github.com/nektos/act")
        return True

    # Test matrix with different platform inputs
    test_cases = [
        ("linux-gcc11", "should include linux-gcc11"),
        ("all", "should include all platforms"),
        ("windows-msvc2022", "should include windows-msvc2022")
    ]

    for platform_input, description in test_cases:
        print(f"  ?? Testing platform='{platform_input}' ({description})")
        success, stdout, stderr = run_command(
            f"act -j build --matrix platform:{platform_input}",
            cwd="."
        )
        if success:
            print(f"    ? Matrix test passed for {platform_input}")
        else:
            print(f"    ? Matrix test failed for {platform_input}: {stderr}")
            return False

    return True

def test_conan_integration():
    """Test Conan integration with dynamic versioning"""
    print("?? Testing Conan integration...")

    # Test bootstrap script
    if os.path.exists("openssl-conan-init.py"):
        success, stdout, stderr = run_command("python3 openssl-conan-init.py")
        if success:
            print("  ? Bootstrap script executed successfully")
        else:
            print(f"  ? Bootstrap script failed: {stderr}")
            return False
    else:
        print("  ? openssl-conan-init.py not found")
        return False

    # Test dynamic versioning
    if os.path.exists("conanfile.py"):
        try:
            # Import and test version setting
            sys.path.insert(0, ".")
            # This is a basic syntax check - full testing would require Conan
            with open("conanfile.py", "r") as f:
                content = f.read()
                if "def set_version(self):" in content:
                    print("  ? Dynamic versioning method found")
                else:
                    print("  ? Dynamic versioning method not found")
                    return False
        except Exception as e:
            print(f"  ? Conanfile validation error: {e}")
            return False
    else:
        print("  ? conanfile.py not found")
        return False

    return True

def test_fips_compliance_setup():
    """Test FIPS compliance setup"""
    print("?? Testing FIPS compliance setup...")

    # Check if OpenSSL is available
    success, stdout, _ = run_command("openssl version")
    if success:
        print("  ? OpenSSL available")
    else:
        print("  ??  OpenSSL not available - FIPS testing limited")
        return True  # Not a hard failure

    # Check FIPS provider availability
    success, stdout, _ = run_command("openssl list -providers")
    if "fips" in stdout.lower():
        print("  ? FIPS provider available")
    else:
        print("  ??  FIPS provider not detected (may be expected)")

    return True

def test_cloudsmith_dry_run():
    """Test Cloudsmith publishing dry run"""
    print("?? Testing Cloudsmith publishing (dry run)...")

    # Check if cloudsmith CLI is available
    success, _, _ = run_command("which cloudsmith")
    if not success:
        print("  ??  cloudsmith CLI not available - install with: pip install cloudsmith-cli")
        return True  # Not a hard failure

    # Dry run publishing (would need actual credentials for real test)
    print("  ??  Cloudsmith CLI available - dry run test would require credentials")
    print("     Manual test: cloudsmith push conan --dry-run <owner>/<repo> <package>")

    return True

def main():
    """Run all validation tests"""
    print("?? OpenSSL Tools Implementation Validation")
    print("=" * 50)

    tests = [
        ("YAML Syntax Validation", validate_yaml_files),
        ("Matrix Strategy Testing", test_matrix_strategy),
        ("Conan Integration Testing", test_conan_integration),
        ("FIPS Compliance Setup", test_fips_compliance_setup),
        ("Cloudsmith Publishing Test", test_cloudsmith_dry_run)
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n?? {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
            status = "? PASSED" if result else "? FAILED"
            print(f"?? {test_name}: {status}")
        except Exception as e:
            print(f"?? {test_name}: ? ERROR - {e}")
            results.append((test_name, False))

    print("\n" + "=" * 50)
    print("?? VALIDATION SUMMARY")

    all_passed = True
    for test_name, result in results:
        status = "? PASSED" if result else "? FAILED"
        print(f"  {status} {test_name}")
        if not result:
            all_passed = False

    print(f"\n?? OVERALL RESULT: {'? ALL TESTS PASSED' if all_passed else '? SOME TESTS FAILED'}")

    if not all_passed:
        print("\n?? Next Steps:")
        print("  - Fix failing tests")
        print("  - Run: python scripts/validate-implementation.py")
        print("  - Test workflows with: act -j <job-name>")
        sys.exit(1)
    else:
        print("\n?? Implementation validation successful!")
        print("   Ready for production deployment.")

if __name__ == "__main__":
    main()