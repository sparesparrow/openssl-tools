#!/bin/bash

# Verify Reusable Workflows
# This script validates the YAML syntax and structure of all reusable workflows

set -e

echo "🔍 Verifying Reusable Workflows..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check YAML syntax
check_yaml() {
    local file=$1
    local name=$2
    
    echo -n "  Checking $name... "
    
    if command -v yamllint >/dev/null 2>&1; then
        if yamllint "$file" >/dev/null 2>&1; then
            echo -e "${GREEN}✅ Valid YAML${NC}"
        else
            echo -e "${RED}❌ Invalid YAML${NC}"
            yamllint "$file"
            return 1
        fi
    else
        # Basic YAML validation using Python
        if python3 -c "import yaml; yaml.safe_load(open('$file'))" >/dev/null 2>&1; then
            echo -e "${GREEN}✅ Valid YAML${NC}"
        else
            echo -e "${RED}❌ Invalid YAML${NC}"
            return 1
        fi
    fi
}

# Function to check workflow structure
check_workflow_structure() {
    local file=$1
    local name=$2
    
    echo -n "  Checking $name structure... "
    
    # Check for required workflow_call trigger
    if grep -q "workflow_call:" "$file"; then
        echo -e "${GREEN}✅ Has workflow_call trigger${NC}"
    else
        echo -e "${RED}❌ Missing workflow_call trigger${NC}"
        return 1
    fi
    
    # Check for inputs section
    if grep -q "inputs:" "$file"; then
        echo -n "    Inputs: "
        local input_count=$(grep -c "description:" "$file" || echo "0")
        echo -e "${GREEN}✅ $input_count inputs defined${NC}"
    else
        echo -e "${YELLOW}⚠️  No inputs section${NC}"
    fi
    
    # Check for outputs section
    if grep -q "outputs:" "$file"; then
        echo -n "    Outputs: "
        local output_count=$(grep -c "value:" "$file" || echo "0")
        echo -e "${GREEN}✅ $output_count outputs defined${NC}"
    else
        echo -e "${YELLOW}⚠️  No outputs section${NC}"
    fi
    
    # Check for secrets section
    if grep -q "secrets:" "$file"; then
        echo -n "    Secrets: "
        local secret_count=$(grep -c "description:" "$file" | tail -1 || echo "0")
        echo -e "${GREEN}✅ $secret_count secrets defined${NC}"
    else
        echo -e "${YELLOW}⚠️  No secrets section${NC}"
    fi
}

# Function to check composite action structure
check_composite_action() {
    local file=$1
    local name=$2
    
    echo -n "  Checking $name structure... "
    
    # Check for composite action structure
    if grep -q "using: 'composite'" "$file"; then
        echo -e "${GREEN}✅ Composite action structure${NC}"
    else
        echo -e "${RED}❌ Not a composite action${NC}"
        return 1
    fi
    
    # Check for inputs section
    if grep -q "inputs:" "$file"; then
        echo -n "    Inputs: "
        local input_count=$(grep -c "description:" "$file" || echo "0")
        echo -e "${GREEN}✅ $input_count inputs defined${NC}"
    else
        echo -e "${YELLOW}⚠️  No inputs section${NC}"
    fi
    
    # Check for outputs section
    if grep -q "outputs:" "$file"; then
        echo -n "    Outputs: "
        local output_count=$(grep -c "value:" "$file" || echo "0")
        echo -e "${GREEN}✅ $output_count outputs defined${NC}"
    else
        echo -e "${YELLOW}⚠️  No outputs section${NC}"
    fi
}

# Main verification
echo "📋 Checking Reusable Workflows..."

# Check build-openssl.yml
echo "1. Build OpenSSL Workflow"
check_yaml ".github/workflows/build-openssl.yml" "build-openssl.yml"
check_workflow_structure ".github/workflows/build-openssl.yml" "build-openssl.yml"

# Check test-integration.yml
echo "2. Test Integration Workflow"
check_yaml ".github/workflows/test-integration.yml" "test-integration.yml"
check_workflow_structure ".github/workflows/test-integration.yml" "test-integration.yml"

# Check publish-cloudsmith.yml
echo "3. Publish Cloudsmith Workflow"
check_yaml ".github/workflows/publish-cloudsmith.yml" "publish-cloudsmith.yml"
check_workflow_structure ".github/workflows/publish-cloudsmith.yml" "publish-cloudsmith.yml"

# Check composite action
echo "4. Cloudsmith Publish Composite Action"
check_yaml ".github/actions/cloudsmith-publish/action.yml" "cloudsmith-publish/action.yml"
check_composite_action ".github/actions/cloudsmith-publish/action.yml" "cloudsmith-publish/action.yml"

# Check demo workflow
echo "5. Demo Workflow"
check_yaml ".github/workflows/demo-reusable-workflows.yml" "demo-reusable-workflows.yml"

echo ""
echo "🎉 Workflow verification completed!"
echo ""
echo "📚 Next steps:"
echo "  1. Run 'act' to test workflows locally"
echo "  2. Use workflow_dispatch to test in GitHub"
echo "  3. Check Cloudsmith for published packages"
echo "  4. Review security scan results"
echo ""
echo "🔗 Useful commands:"
echo "  act -W .github/workflows/demo-reusable-workflows.yml"
echo "  act -W .github/workflows/build-openssl.yml -e .github/workflows/build-openssl.yml"
echo "  act -W .github/workflows/test-integration.yml -e .github/workflows/test-integration.yml"
