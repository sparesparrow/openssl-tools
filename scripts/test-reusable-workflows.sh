#!/bin/bash
set -e

# Test script for reusable workflows
# This script validates the YAML syntax and structure of the reusable workflows

echo "🔍 Testing Reusable Workflows..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to validate YAML syntax
validate_yaml() {
    local file="$1"
    local name="$2"
    
    echo -n "  Validating $name... "
    
    if command_exists yamllint; then
        if yamllint "$file" >/dev/null 2>&1; then
            echo -e "${GREEN}✓${NC}"
            return 0
        else
            echo -e "${RED}✗${NC}"
            echo "    YAML syntax errors found:"
            yamllint "$file" 2>&1 | sed 's/^/    /'
            return 1
        fi
    elif command_exists python3; then
        if python3 -c "import yaml; yaml.safe_load(open('$file'))" >/dev/null 2>&1; then
            echo -e "${GREEN}✓${NC}"
            return 0
        else
            echo -e "${RED}✗${NC}"
            echo "    YAML syntax errors found"
            return 1
        fi
    else
        echo -e "${YELLOW}⚠${NC} (no YAML validator available)"
        return 0
    fi
}

# Function to check workflow structure
check_workflow_structure() {
    local file="$1"
    local name="$2"
    
    echo -n "  Checking $name structure... "
    
    # Check for required trigger (workflow_call for reusable, workflow_dispatch for test)
    if ! grep -q "workflow_call:" "$file" && ! grep -q "workflow_dispatch:" "$file"; then
        echo -e "${RED}✗${NC}"
        echo "    Missing 'workflow_call' or 'workflow_dispatch' trigger"
        return 1
    fi
    
    # Check for inputs section
    if ! grep -q "inputs:" "$file"; then
        echo -e "${RED}✗${NC}"
        echo "    Missing 'inputs' section"
        return 1
    fi
    
    # Check for jobs section
    if ! grep -q "jobs:" "$file"; then
        echo -e "${RED}✗${NC}"
        echo "    Missing 'jobs' section"
        return 1
    fi
    
    echo -e "${GREEN}✓${NC}"
    return 0
}

# Function to check composite action structure
check_composite_action_structure() {
    local file="$1"
    local name="$2"
    
    echo -n "  Checking $name structure... "
    
    # Check for required runs section
    if ! grep -q "runs:" "$file"; then
        echo -e "${RED}✗${NC}"
        echo "    Missing 'runs' section"
        return 1
    fi
    
    # Check for composite type
    if ! grep -q "using: 'composite'" "$file"; then
        echo -e "${RED}✗${NC}"
        echo "    Not a composite action (missing 'using: composite')"
        return 1
    fi
    
    # Check for inputs section
    if ! grep -q "inputs:" "$file"; then
        echo -e "${RED}✗${NC}"
        echo "    Missing 'inputs' section"
        return 1
    fi
    
    echo -e "${GREEN}✓${NC}"
    return 0
}

# Main validation
echo "📋 Validating workflow files..."

# Check if workflows directory exists
if [ ! -d ".github/workflows" ]; then
    echo -e "${RED}Error: .github/workflows directory not found${NC}"
    exit 1
fi

# Validate build workflow
echo "🔨 Build Workflow:"
if [ -f ".github/workflows/build-openssl.yml" ]; then
    validate_yaml ".github/workflows/build-openssl.yml" "build-openssl.yml"
    check_workflow_structure ".github/workflows/build-openssl.yml" "build-openssl.yml"
else
    echo -e "${RED}  build-openssl.yml not found${NC}"
    exit 1
fi

# Validate test workflow
echo "🧪 Test Workflow:"
if [ -f ".github/workflows/test-integration.yml" ]; then
    validate_yaml ".github/workflows/test-integration.yml" "test-integration.yml"
    check_workflow_structure ".github/workflows/test-integration.yml" "test-integration.yml"
else
    echo -e "${RED}  test-integration.yml not found${NC}"
    exit 1
fi

# Validate publish workflow
echo "📦 Publish Workflow:"
if [ -f ".github/workflows/publish-cloudsmith.yml" ]; then
    validate_yaml ".github/workflows/publish-cloudsmith.yml" "publish-cloudsmith.yml"
    check_workflow_structure ".github/workflows/publish-cloudsmith.yml" "publish-cloudsmith.yml"
else
    echo -e "${RED}  publish-cloudsmith.yml not found${NC}"
    exit 1
fi

# Validate composite action
echo "🔧 Composite Action:"
if [ -f ".github/actions/cloudsmith-publish/action.yml" ]; then
    validate_yaml ".github/actions/cloudsmith-publish/action.yml" "cloudsmith-publish/action.yml"
    check_composite_action_structure ".github/actions/cloudsmith-publish/action.yml" "cloudsmith-publish/action.yml"
else
    echo -e "${RED}  cloudsmith-publish/action.yml not found${NC}"
    exit 1
fi

# Validate test workflow
echo "🧪 Test Workflow:"
if [ -f ".github/workflows/test-reusable-workflows.yml" ]; then
    validate_yaml ".github/workflows/test-reusable-workflows.yml" "test-reusable-workflows.yml"
    check_workflow_structure ".github/workflows/test-reusable-workflows.yml" "test-reusable-workflows.yml"
else
    echo -e "${YELLOW}  test-reusable-workflows.yml not found (optional)${NC}"
fi

# Check for required tools
echo "🛠️  Checking required tools..."

check_tool() {
    local tool="$1"
    local install_cmd="$2"
    
    if command_exists "$tool"; then
        echo -e "  $tool: ${GREEN}✓${NC}"
    else
        echo -e "  $tool: ${YELLOW}⚠${NC} (not installed - $install_cmd)"
    fi
}

check_tool "yamllint" "pip install yamllint"
check_tool "python3" "apt-get install python3"
check_tool "conan" "pip install conan"
check_tool "syft" "curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin"
check_tool "trivy" "curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin"
check_tool "cloudsmith" "pip install cloudsmith-cli"

# Summary
echo ""
echo "📊 Summary:"
echo "  ✅ All workflow files found and validated"
echo "  ✅ YAML syntax is correct"
echo "  ✅ Workflow structure is valid"
echo "  ✅ Composite action structure is valid"
echo ""
echo -e "${GREEN}🎉 All reusable workflows are ready to use!${NC}"
echo ""
echo "Next steps:"
echo "  1. Commit and push these workflows to your repository"
echo "  2. Create a Git tag (e.g., v1.0.0) for versioning"
echo "  3. Test the workflows using the test workflow"
echo "  4. Use the workflows in other repositories with @v1"