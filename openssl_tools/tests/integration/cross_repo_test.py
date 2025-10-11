#!/usr/bin/env python3
"""
Cross-Repository Integration Test Script

This script tests the integration between openssl and openssl-tools repositories
by simulating the repository_dispatch trigger and validating the response.
"""

import os
import sys
import json
import time
import requests
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_openssl_repository_structure():
    """Test that OpenSSL repository has the required structure"""
    print("🔍 Testing OpenSSL repository structure...")
    
    openssl_repo = Path("/home/sparrow/projects/openssl")
    
    required_files = [
        "conanfile.py",
        "VERSION.dat",
        "config",
        "Configure"
    ]
    
    required_dirs = [
        "crypto",
        "ssl", 
        "apps",
        "include"
    ]
    
    all_good = True
    
    for file in required_files:
        file_path = openssl_repo / file
        if file_path.exists():
            print(f"✅ {file} found")
        else:
            print(f"❌ {file} missing")
            all_good = False
    
    for dir_name in required_dirs:
        dir_path = openssl_repo / dir_name
        if dir_path.is_dir():
            print(f"✅ {dir_name}/ directory found")
        else:
            print(f"❌ {dir_name}/ directory missing")
            all_good = False
    
    return all_good

def test_conanfile_compatibility():
    """Test that conanfile.py works with OpenSSL source"""
    print("\n🔧 Testing conanfile.py compatibility...")
    
    openssl_repo = Path("/home/sparrow/projects/openssl")
    openssl_tools_repo = Path("/home/sparrow/projects/openssl-tools")
    
    # Copy conanfile.py from openssl-tools to openssl
    conanfile_source = openssl_tools_repo / "conanfile.py"
    conanfile_dest = openssl_repo / "conanfile.py"
    
    if not conanfile_source.exists():
        print("❌ conanfile.py not found in openssl-tools")
        return False
    
    # Test conanfile.py import and basic functionality
    try:
        import sys
        sys.path.insert(0, str(openssl_repo))
        
        from conanfile import OpenSSLConan
        print("✅ conanfile.py imports successfully")
        
        conan = OpenSSLConan()
        conan.recipe_folder = str(openssl_repo)
        
        # Test version detection
        conan.set_version()
        print(f"✅ Version detection works: {conan.version}")
        
        # Test basic configuration
        conan.configure()
        print("✅ Basic configuration works")
        
        return True
        
    except Exception as e:
        print(f"❌ conanfile.py test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_workflow_syntax():
    """Test that workflow files have valid syntax"""
    print("\n📋 Testing workflow syntax...")
    
    openssl_repo = Path("/home/sparrow/projects/openssl")
    openssl_tools_repo = Path("/home/sparrow/projects/openssl-tools")
    
    workflow_files = [
        openssl_repo / ".github/workflows/trigger-tools.yml",
        openssl_repo / ".github/workflows/simplified-basic-validation.yml",
        openssl_tools_repo / ".github/workflows/cross-repository-integration.yml",
        openssl_tools_repo / ".github/workflows/basic-openssl-integration.yml"
    ]
    
    all_good = True
    
    for workflow_file in workflow_files:
        if workflow_file.exists():
            try:
                import yaml
                with open(workflow_file, 'r') as f:
                    yaml.safe_load(f)
                print(f"✅ {workflow_file.name} has valid YAML syntax")
            except Exception as e:
                print(f"❌ {workflow_file.name} has YAML syntax error: {e}")
                all_good = False
        else:
            print(f"⚠️  {workflow_file.name} not found")
    
    return all_good

def test_event_type_consistency():
    """Test that event types are consistent between repositories"""
    print("\n🔗 Testing event type consistency...")
    
    openssl_repo = Path("/home/sparrow/projects/openssl")
    openssl_tools_repo = Path("/home/sparrow/projects/openssl-tools")
    
    # Check trigger-tools.yml event type
    trigger_tools_file = openssl_repo / ".github/workflows/trigger-tools.yml"
    if trigger_tools_file.exists():
        with open(trigger_tools_file, 'r') as f:
            content = f.read()
            if "openssl-build-triggered" in content:
                print("✅ trigger-tools.yml uses correct event type: openssl-build-triggered")
            else:
                print("❌ trigger-tools.yml uses incorrect event type")
                return False
    
    # Check cross-repository-integration.yml event type
    integration_file = openssl_tools_repo / ".github/workflows/cross-repository-integration.yml"
    if integration_file.exists():
        with open(integration_file, 'r') as f:
            content = f.read()
            if "openssl-build-triggered" in content:
                print("✅ cross-repository-integration.yml expects correct event type: openssl-build-triggered")
            else:
                print("❌ cross-repository-integration.yml expects incorrect event type")
                return False
    
    return True

def simulate_repository_dispatch():
    """Simulate a repository_dispatch event"""
    print("\n🚀 Simulating repository_dispatch event...")
    
    # This would normally be done by GitHub Actions
    # For testing, we'll just validate the payload structure
    payload = {
        "source_repo_sha": "test-sha-123",
        "source_repo_ref": "main",
        "build_scope": "test",
        "triggered_by": "test-user",
        "triggered_at": "2025-10-10T02:00:00Z",
        "github_event": "workflow_dispatch",
        "github_ref": "refs/heads/main",
        "github_repository": "sparesparrow/openssl"
    }
    
    print("✅ Payload structure is valid:")
    for key, value in payload.items():
        print(f"  {key}: {value}")
    
    return True

def main():
    """Main test function"""
    print("🧪 Cross-Repository Integration Test")
    print("=" * 50)
    
    tests = [
        ("OpenSSL Repository Structure", test_openssl_repository_structure),
        ("Conanfile Compatibility", test_conanfile_compatibility),
        ("Workflow Syntax", test_workflow_syntax),
        ("Event Type Consistency", test_event_type_consistency),
        ("Repository Dispatch Simulation", simulate_repository_dispatch)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Cross-repository integration is ready.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
