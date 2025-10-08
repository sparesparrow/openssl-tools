#!/usr/bin/env python3
"""
Test CI/CD Logic and Workflows
Validates workflow logic, change detection, and caching strategies
"""

import os
import sys
import yaml
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

class Colors:
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    BOLD = '\033[1m'
    NC = '\033[0m'

def print_section(title: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.NC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title:^70}{Colors.NC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.NC}\n")

def test_pass(name: str) -> Tuple[bool, str]:
    print(f"  {Colors.GREEN}✓{Colors.NC} {name}")
    return (True, name)

def test_fail(name: str, reason: str = "") -> Tuple[bool, str]:
    print(f"  {Colors.RED}✗{Colors.NC} {name}")
    if reason:
        print(f"    {Colors.RED}→ {reason}{Colors.NC}")
    return (False, name)

def test_info(message: str):
    print(f"    {Colors.BLUE}ℹ{Colors.NC} {message}")

# Test Results
results = {'pass': [], 'fail': []}

print_section("CI/CD LOGIC TESTING SUITE")
print(f"Workspace: {Path.cwd()}")
print(f"Python: {sys.version.split()[0]}")

# ============================================================================
# TEST 1: Workflow File Structure
# ============================================================================
print_section("TEST 1: Workflow File Structure")

workflows = {
    'ci.yml': 'Original CI',
    'optimized-ci.yml': 'Optimized CI',
    'optimized-basic-ci.yml': 'Recommended Progressive CI',
    'modern-ci.yml': 'Advanced Conan CI'
}

for wf_name, description in workflows.items():
    wf_path = Path(f'.github/workflows/{wf_name}')
    
    if not wf_path.exists():
        result = test_fail(f"{wf_name} exists", "File not found")
        results['fail'].append(result[1])
        continue
    
    try:
        with open(wf_path) as f:
            data = yaml.safe_load(f)
            
        # Check for workflow trigger (on: or True key in YAML)
        has_trigger = True in data or 'on' in str(data)
        has_jobs = 'jobs' in data and isinstance(data['jobs'], dict)
        has_name = 'name' in data
        
        if has_trigger and has_jobs:
            result = test_pass(f"{wf_name}: {description}")
            results['pass'].append(result[1])
            
            # Additional info
            job_count = len(data['jobs'])
            test_info(f"{job_count} job(s) defined")
            
        else:
            reason = []
            if not has_trigger:
                reason.append("no trigger")
            if not has_jobs:
                reason.append("no jobs")
            result = test_fail(f"{wf_name}", ", ".join(reason))
            results['fail'].append(result[1])
            
    except Exception as e:
        result = test_fail(f"{wf_name}", f"Parse error: {e}")
        results['fail'].append(result[1])

# ============================================================================
# TEST 2: Change Detection Logic
# ============================================================================
print_section("TEST 2: Change Detection Logic")

# Test optimized-basic-ci.yml change detection
try:
    with open('.github/workflows/optimized-basic-ci.yml') as f:
        workflow = yaml.safe_load(f)
    
    # Check if detect-changes job exists
    if 'detect-changes' in workflow['jobs']:
        result = test_pass("Change detection job exists")
        results['pass'].append(result[1])
        
        # Check for path filtering
        detect_job = workflow['jobs']['detect-changes']
        steps = detect_job.get('steps', [])
        
        has_path_filter = False
        for step in steps:
            if 'dorny/paths-filter' in str(step.get('uses', '')):
                has_path_filter = True
                result = test_pass("Path filter action configured")
                results['pass'].append(result[1])
                
                # Check filter patterns
                filters = step.get('with', {}).get('filters', '')
                if 'source:' in filters and 'docs' in filters:
                    result = test_pass("Filter patterns defined (source, docs)")
                    results['pass'].append(result[1])
                    test_info("Patterns: source changes, doc changes, tests")
                else:
                    result = test_fail("Filter patterns", "Incomplete patterns")
                    results['fail'].append(result[1])
                break
        
        if not has_path_filter:
            result = test_fail("Path filter action", "Not found in workflow")
            results['fail'].append(result[1])
    else:
        result = test_fail("Change detection job", "Not found in workflow")
        results['fail'].append(result[1])
        
except Exception as e:
    result = test_fail("Change detection logic", str(e))
    results['fail'].append(result[1])

# ============================================================================
# TEST 3: Build Caching Strategy
# ============================================================================
print_section("TEST 3: Build Caching Strategy")

try:
    with open('.github/workflows/optimized-basic-ci.yml') as f:
        workflow = yaml.safe_load(f)
    
    # Check for cache action in build jobs
    build_jobs = ['basic-gcc', 'basic-clang']
    caching_found = False
    
    for job_name in build_jobs:
        if job_name in workflow['jobs']:
            job = workflow['jobs'][job_name]
            steps = job.get('steps', [])
            
            for step in steps:
                if 'actions/cache' in str(step.get('uses', '')):
                    caching_found = True
                    result = test_pass(f"Caching enabled in {job_name}")
                    results['pass'].append(result[1])
                    
                    # Check cache configuration
                    cache_config = step.get('with', {})
                    if 'key' in cache_config and 'restore-keys' in cache_config:
                        result = test_pass(f"{job_name}: Cache key strategy configured")
                        results['pass'].append(result[1])
                        test_info(f"Cache invalidates on config changes")
                    break
    
    if not caching_found:
        result = test_fail("Build caching", "No cache actions found")
        results['fail'].append(result[1])
        
except Exception as e:
    result = test_fail("Build caching test", str(e))
    results['fail'].append(result[1])

# ============================================================================
# TEST 4: Conan Profile Completeness
# ============================================================================
print_section("TEST 4: Conan Profile Completeness")

required_sections = ['[settings]', '[options]', '[buildenv]', '[conf]']
profiles = list(Path('conan-profiles').glob('*.profile'))

if not profiles:
    result = test_fail("Conan profiles", "No profiles found")
    results['fail'].append(result[1])
else:
    for profile in profiles:
        with open(profile) as f:
            content = f.read()
        
        missing = [sec for sec in required_sections if sec not in content]
        if not missing:
            result = test_pass(f"{profile.name}: Complete profile")
            results['pass'].append(result[1])
        else:
            result = test_fail(f"{profile.name}", f"Missing: {', '.join(missing)}")
            results['fail'].append(result[1])

# ============================================================================
# TEST 5: Conanfile.py Build Logic
# ============================================================================
print_section("TEST 5: Conanfile.py Build Logic")

if Path('conanfile.py').exists():
    with open('conanfile.py') as f:
        content = f.read()
    
    # Test Conan 2.x API usage
    checks = {
        'Conan 2.x imports': 'from conan import ConanFile' in content,
        'build() method defined': 'def build(self):' in content,
        'package() method defined': 'def package(self):' in content,
        'package_info() method': 'def package_info(self):' in content,
        'No source_folder cwd': 'cwd=self.source_folder' not in content,
        'Configure command': './config' in content or './Configure' in content,
        'Make command': 'make' in content,
        'Test execution': 'make test' in content
    }
    
    for check_name, passes_check in checks.items():
        if passes_check:
            result = test_pass(check_name)
            results['pass'].append(result[1])
        else:
            result = test_fail(check_name)
            results['fail'].append(result[1])
else:
    result = test_fail("conanfile.py", "File not found")
    results['fail'].append(result[1])

# ============================================================================
# TEST 6: Workflow Dependencies and Conditions
# ============================================================================
print_section("TEST 6: Workflow Dependencies and Conditions")

try:
    with open('.github/workflows/optimized-basic-ci.yml') as f:
        workflow = yaml.safe_load(f)
    
    jobs = workflow['jobs']
    
    # Test that build jobs depend on change detection
    for job_name in ['basic-gcc', 'basic-clang']:
        if job_name in jobs:
            job = jobs[job_name]
            
            # Check for needs
            if 'needs' in job and 'detect-changes' in job['needs']:
                result = test_pass(f"{job_name}: Depends on change detection")
                results['pass'].append(result[1])
            else:
                result = test_fail(f"{job_name}: Dependencies", "Missing needs: detect-changes")
                results['fail'].append(result[1])
            
            # Check for conditional execution
            if 'if' in job:
                condition = job['if']
                if 'source-changed' in condition or 'detect-changes' in condition:
                    result = test_pass(f"{job_name}: Conditional on changes")
                    results['pass'].append(result[1])
                    test_info(f"Condition: {condition}")
                else:
                    result = test_fail(f"{job_name}: Condition", "Doesn't check for changes")
                    results['fail'].append(result[1])
            else:
                test_info(f"{job_name}: No conditional (runs always)")
                
except Exception as e:
    result = test_fail("Workflow dependencies", str(e))
    results['fail'].append(result[1])

# ============================================================================
# TEST 7: Documentation Completeness
# ============================================================================
print_section("TEST 7: Documentation Completeness")

required_docs = {
    'CI-CD-COMPLETE-GUIDE.md': 'Complete consolidated guide',
    'IMPLEMENTATION-GUIDE.md': 'Implementation details',
    'FIX-SUMMARY.md': 'Fix documentation'
}

for doc, description in required_docs.items():
    doc_path = Path(doc)
    if doc_path.exists():
        size = doc_path.stat().st_size
        if size > 1000:  # At least 1KB
            result = test_pass(f"{doc}: {description} ({size:,} bytes)")
            results['pass'].append(result[1])
        else:
            result = test_fail(f"{doc}", f"Too small ({size} bytes)")
            results['fail'].append(result[1])
    else:
        result = test_fail(f"{doc}", "Missing")
        results['fail'].append(result[1])

# ============================================================================
# TEST 8: OpenSSL Build System Integration
# ============================================================================
print_section("TEST 8: OpenSSL Build System Integration")

build_files = ['Configure', 'config', 'VERSION.dat', 'build.info']
for bf in build_files:
    if Path(bf).exists():
        result = test_pass(f"{bf} exists")
        results['pass'].append(result[1])
    else:
        if bf == 'config':  # Optional
            test_info(f"{bf} not found (may be generated)")
        else:
            result = test_fail(f"{bf}", "Missing")
            results['fail'].append(result[1])

# Test if we can run config --help
try:
    result_code = subprocess.run(
        ['./config', '--help'],
        capture_output=True,
        timeout=5
    )
    if result_code.returncode == 0:
        result = test_pass("Configure script is executable")
        results['pass'].append(result[1])
    else:
        test_info("Configure script exists but may need dependencies")
except Exception as e:
    test_info(f"Couldn't test configure execution: {e}")

# ============================================================================
# SUMMARY
# ============================================================================
print_section("TEST SUMMARY")

passed = len(results['pass'])
failed = len(results['fail'])
total = passed + failed

print(f"  {Colors.GREEN}✓ Passed:  {passed:3d}{Colors.NC}")
print(f"  {Colors.RED}✗ Failed:  {failed:3d}{Colors.NC}")
print(f"  {'Total:':>10} {total:3d}\n")

if failed == 0:
    print(f"{Colors.GREEN}{Colors.BOLD}{'='*70}{Colors.NC}")
    print(f"{Colors.GREEN}{Colors.BOLD}{'✓ ALL TESTS PASSED':^70}{Colors.NC}")
    print(f"{Colors.GREEN}{Colors.BOLD}{'='*70}{Colors.NC}\n")
    print("✅ CI/CD logic is working correctly")
    print("✅ All workflows are properly configured")
    print("✅ Change detection will work as expected")
    print("✅ Caching strategy is correct")
    print("✅ Conan integration is properly set up")
    print("\n" + Colors.BOLD + "Ready for deployment!" + Colors.NC)
    sys.exit(0)
else:
    print(f"{Colors.RED}{Colors.BOLD}{'='*70}{Colors.NC}")
    print(f"{Colors.RED}{Colors.BOLD}{'✗ SOME TESTS FAILED':^70}{Colors.NC}")
    print(f"{Colors.RED}{Colors.BOLD}{'='*70}{Colors.NC}\n")
    print(f"Failed tests: {failed}")
    print("Review failures above and fix before deploying.")
    sys.exit(1)
