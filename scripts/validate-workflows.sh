#!/bin/bash
# OpenSSL Tools Workflow Validation Script
# Performs comprehensive validation of the enhanced DevOps automation

set -e

echo "?? OpenSSL Tools Workflow Validation"
echo "===================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}? $2${NC}"
    else
        echo -e "${RED}? $2${NC}"
    fi
}

echo "1. Validating YAML syntax..."
yamllint .github/workflows/reusable/*.yml 2>/dev/null && print_status 0 "Reusable workflows YAML valid" || print_status 1 "Reusable workflows YAML invalid"
yamllint .github/workflows/security-gates.yml 2>/dev/null && print_status 0 "Security gates YAML valid" || print_status 1 "Security gates YAML invalid"
yamllint .github/actions/**/*.yml 2>/dev/null && print_status 0 "Composite actions YAML valid" || print_status 1 "Composite actions YAML invalid"

echo
echo "2. Testing matrix strategy..."
if command -v act &> /dev/null; then
    act -j build --matrix platform:linux-gcc11 --dry-run >/dev/null 2>&1 && print_status 0 "Matrix strategy test passed" || print_status 1 "Matrix strategy test failed"
else
    echo -e "${YELLOW}??  act CLI not found - install from https://github.com/nektos/act${NC}"
fi

echo
echo "3. Testing Conan integration..."
python3 openssl-conan-init.py >/dev/null 2>&1 && print_status 0 "Bootstrap script executed" || print_status 1 "Bootstrap script failed"

# Test dynamic versioning
GIT_VERSION=$(git describe --tags --always 2>/dev/null || echo "1.2.7-dev")
echo "   Detected version: $GIT_VERSION"

echo
echo "4. Validating FIPS compliance setup..."
if command -v openssl &> /dev/null; then
    openssl list -providers 2>/dev/null | grep -i fips >/dev/null && print_status 0 "FIPS provider available" || echo -e "${YELLOW}??  FIPS provider not detected${NC}"
else
    echo -e "${YELLOW}??  OpenSSL not available${NC}"
fi

echo
echo "5. Testing Cloudsmith integration (dry run)..."
if command -v cloudsmith &> /dev/null; then
    echo -e "${YELLOW}??  Cloudsmith CLI available - dry run requires credentials${NC}"
else
    echo -e "${YELLOW}??  cloudsmith CLI not available - install with: pip install cloudsmith-cli${NC}"
fi

echo
echo "6. Running comprehensive Python validation..."
python3 scripts/validate-implementation.py && print_status 0 "Python validation passed" || print_status 1 "Python validation failed"

echo
echo "===================================="
echo "?? Validation complete!"
echo
echo "Next steps:"
echo "  - Fix any failed validations"
echo "  - Test workflows: act -j <job-name>"
echo "  - Deploy to production when all checks pass"