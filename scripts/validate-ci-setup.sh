#!/usr/bin/env bash
# CI/CD Setup Validation Script
# Validates all workflows, profiles, and configuration

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
PASS=0
FAIL=0
WARN=0

# Helper functions
print_header() {
    echo -e "\n${BLUE}═══════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}\n"
}

print_check() {
    echo -n "  Checking $1... "
}

print_pass() {
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASS++))
}

print_fail() {
    echo -e "${RED}✗ FAIL${NC}"
    echo -e "    ${RED}$1${NC}"
    ((FAIL++))
}

print_warn() {
    echo -e "${YELLOW}⚠ WARN${NC}"
    echo -e "    ${YELLOW}$1${NC}"
    ((WARN++))
}

print_info() {
    echo -e "    ${BLUE}ℹ $1${NC}"
}

# Navigate to repo root
cd "$(dirname "$0")/.."

print_header "CI/CD VALIDATION SCRIPT"
echo "Workspace: $(pwd)"
echo "Date: $(date)"
echo ""

# 1. Validate Workflow Files
print_header "1. Workflow Files Validation"

WORKFLOWS=(
    ".github/workflows/ci.yml"
    ".github/workflows/optimized-ci.yml"
    ".github/workflows/optimized-basic-ci.yml"
    ".github/workflows/modern-ci.yml"
)

for workflow in "${WORKFLOWS[@]}"; do
    print_check "$(basename "$workflow")"
    
    if [[ ! -f "$workflow" ]]; then
        print_fail "File not found"
        continue
    fi
    
    # Check YAML syntax with Python
    if python3 -c "import yaml, sys; yaml.safe_load(open('$workflow'))" 2>/dev/null; then
        # Additional checks
        if grep -q "on:" "$workflow" && \
           grep -q "jobs:" "$workflow" && \
           grep -q "runs-on:" "$workflow"; then
            print_pass
        else
            print_fail "Missing required sections (on, jobs, runs-on)"
        fi
    else
        print_fail "Invalid YAML syntax"
    fi
done

# 2. Validate Conan Profiles
print_header "2. Conan Profiles Validation"

PROFILES=(
    "conan-profiles/ci-linux-gcc.profile"
    "conan-profiles/ci-linux-clang.profile"
    "conan-profiles/ci-sanitizers.profile"
    "conan-profiles/ci-macos-x64.profile"
    "conan-profiles/ci-macos-arm64.profile"
)

for profile in "${PROFILES[@]}"; do
    print_check "$(basename "$profile")"
    
    if [[ ! -f "$profile" ]]; then
        print_fail "File not found"
        continue
    fi
    
    # Check required sections
    if grep -q "\[settings\]" "$profile" && \
       grep -q "\[buildenv\]" "$profile"; then
        print_pass
    else
        print_fail "Missing required sections ([settings], [buildenv])"
    fi
done

# 3. Validate Conanfile.py
print_header "3. Conanfile.py Validation"

print_check "conanfile.py exists"
if [[ -f "conanfile.py" ]]; then
    print_pass
else
    print_fail "File not found"
fi

if [[ -f "conanfile.py" ]]; then
    print_check "Python syntax"
    if python3 -m py_compile conanfile.py 2>/dev/null; then
        print_pass
    else
        print_fail "Syntax error in conanfile.py"
    fi
    
    print_check "Conan 2.x imports"
    if grep -q "from conan import ConanFile" conanfile.py; then
        print_pass
    else
        print_fail "Missing 'from conan import ConanFile'"
    fi
    
    print_check "Required methods"
    METHODS=("def build" "def package" "def package_info")
    for method in "${METHODS[@]}"; do
        if ! grep -q "$method" conanfile.py; then
            print_fail "Missing method: $method"
        fi
    done
    if grep -q "def build" conanfile.py && \
       grep -q "def package" conanfile.py && \
       grep -q "def package_info" conanfile.py; then
        print_pass
    fi
    
    print_check "No incorrect cwd references"
    if grep -q "cwd=self.source_folder" conanfile.py; then
        print_fail "Found incorrect cwd=self.source_folder"
    else
        print_pass
    fi
fi

# 4. Validate OpenSSL Build System
print_header "4. OpenSSL Build System"

print_check "Configure script"
if [[ -f "Configure" ]] && [[ -x "Configure" ]]; then
    print_pass
else
    if [[ -f "Configure" ]]; then
        print_warn "Configure exists but may not be executable"
    else
        print_fail "Configure script not found"
    fi
fi

print_check "config script"
if [[ -f "config" ]]; then
    print_pass
else
    print_warn "config script not found (optional)"
fi

print_check "VERSION.dat"
if [[ -f "VERSION.dat" ]]; then
    print_pass
else
    print_fail "VERSION.dat not found"
fi

# 5. Validate Documentation
print_header "5. Documentation"

DOCS=(
    "CI-CD-COMPLETE-GUIDE.md"
    "IMPLEMENTATION-GUIDE.md"
    "FIX-SUMMARY.md"
)

for doc in "${DOCS[@]}"; do
    print_check "$doc"
    if [[ -f "$doc" ]]; then
        size=$(wc -c < "$doc")
        if [[ $size -gt 1000 ]]; then
            print_pass
            print_info "Size: $size bytes"
        else
            print_warn "File is very small ($size bytes)"
        fi
    else
        print_warn "File not found (optional)"
    fi
done

# 6. Check for Common Issues
print_header "6. Common Issues Check"

print_check "Undefined secrets in workflows"
SECRET_REFS=$(grep -r "secrets\." .github/workflows/ | grep -v "secrets.GITHUB_TOKEN" | grep -v "if:" | wc -l || true)
if [[ $SECRET_REFS -eq 0 ]]; then
    print_pass
else
    print_warn "Found $SECRET_REFS secret references - ensure they're conditional"
fi

print_check "Missing file references in workflows"
if grep -r "conandata.yml" .github/workflows/ >/dev/null 2>&1; then
    print_fail "Found reference to non-existent conandata.yml"
else
    print_pass
fi

print_check "Workflow file extensions"
WRONG_EXT=$(find .github/workflows/ -type f ! -name "*.yml" ! -name "*.yaml" 2>/dev/null | wc -l)
if [[ $WRONG_EXT -eq 0 ]]; then
    print_pass
else
    print_warn "Found $WRONG_EXT files with wrong extensions"
fi

# 7. Test Build System (Optional - Quick Check)
print_header "7. Quick Build System Test (Optional)"

print_check "Can run config help"
if ./config --help >/dev/null 2>&1; then
    print_pass
else
    print_warn "config --help failed (may require dependencies)"
fi

# 8. Check Git Status
print_header "8. Git Status"

print_check "Git repository"
if git rev-parse --git-dir >/dev/null 2>&1; then
    print_pass
else
    print_fail "Not a git repository"
fi

if git rev-parse --git-dir >/dev/null 2>&1; then
    print_check "Uncommitted changes"
    if [[ -z $(git status --porcelain) ]]; then
        print_info "Working directory clean"
    else
        print_info "Working directory has changes (normal for development)"
    fi
fi

# 9. System Dependencies Check
print_header "9. System Dependencies (Optional)"

DEPS=(
    "python3:Required for validation scripts"
    "perl:Required for OpenSSL build"
    "make:Required for OpenSSL build"
    "gcc:Required for compilation"
)

for dep in "${DEPS[@]}"; do
    cmd="${dep%%:*}"
    desc="${dep#*:}"
    print_check "$cmd"
    if command -v "$cmd" >/dev/null 2>&1; then
        version=$(
            case "$cmd" in
                python3) python3 --version 2>&1 | cut -d' ' -f2 ;;
                perl) perl --version 2>&1 | grep -oP 'v\K[0-9.]+' | head -1 ;;
                make) make --version 2>&1 | head -1 | grep -oP '[0-9.]+' | head -1 ;;
                gcc) gcc --version 2>&1 | head -1 | grep -oP '[0-9.]+' | head -1 ;;
            esac
        )
        print_pass
        print_info "Version: $version"
    else
        print_warn "$desc - Not found"
    fi
done

# 10. Conan Check (Optional)
print_header "10. Conan Installation (Optional)"

print_check "Conan installed"
if command -v conan >/dev/null 2>&1; then
    version=$(conan --version 2>&1 | grep -oP '[0-9.]+' | head -1)
    if [[ "$version" == 2.* ]]; then
        print_pass
        print_info "Version: $version (Conan 2.x ✓)"
    else
        print_warn "Conan $version found (need 2.x for modern-ci.yml)"
    fi
else
    print_info "Not installed (only needed for Option 3: Modern CI)"
fi

# Summary
print_header "VALIDATION SUMMARY"

TOTAL=$((PASS + FAIL + WARN))

echo -e "${GREEN}Passed:  $PASS${NC}"
echo -e "${RED}Failed:  $FAIL${NC}"
echo -e "${YELLOW}Warnings: $WARN${NC}"
echo -e "Total:   $TOTAL"
echo ""

if [[ $FAIL -eq 0 ]]; then
    echo -e "${GREEN}✓ All critical checks passed!${NC}"
    echo ""
    echo "Ready to proceed with:"
    echo "  • Option 1: Conservative (just merge)"
    echo "  • Option 2: Progressive (enable optimized-basic-ci.yml) ← Recommended"
    echo "  • Option 3: Advanced (enable modern-ci.yml with Conan)"
    echo ""
    exit 0
else
    echo -e "${RED}✗ Some checks failed!${NC}"
    echo ""
    echo "Please fix the failed checks before proceeding."
    echo "See CI-CD-COMPLETE-GUIDE.md for troubleshooting."
    echo ""
    exit 1
fi
