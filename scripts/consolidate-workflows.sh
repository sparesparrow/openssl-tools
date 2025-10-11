#!/bin/bash
set -euo pipefail

# Workflow Consolidation Script
# This script consolidates GitHub Actions workflows for the openssl-tools project

echo "🔧 Starting workflow consolidation..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "conanfile.py" ]; then
    print_error "This script must be run from the openssl-tools repository root"
    exit 1
fi

# Create backup directory structure
print_status "Creating backup directory structure..."
mkdir -p .github/workflows-backup/{legacy-openssl,experimental,upstream-only}
mkdir -p .github/workflows/reusable
mkdir -p .github/workflow-templates

# Move upstream-only workflows
print_status "Moving upstream-only workflows..."
if [ -d ".github/workflows-upstream-only" ]; then
    mv .github/workflows-upstream-only/* .github/workflows-backup/upstream-only/ 2>/dev/null || true
    rmdir .github/workflows-upstream-only 2>/dev/null || true
    print_success "Moved upstream-only workflows to backup"
else
    print_warning "No upstream-only workflows directory found"
fi

# Move disabled workflows to experimental
print_status "Moving disabled workflows to experimental..."
if [ -d ".github/workflows-disabled" ]; then
    # Move OpenSSL-specific workflows to legacy-openssl
    for file in .github/workflows-disabled/*openssl* .github/workflows-disabled/*ci* .github/workflows-disabled/*core* .github/workflows-disabled/*cross* .github/workflows-disabled/*deploy* .github/workflows-disabled/*backport* .github/workflows-disabled/*weekly* .github/workflows-disabled/*windows*; do
        if [ -f "$file" ]; then
            mv "$file" .github/workflows-backup/legacy-openssl/
        fi
    done
    
    # Move experimental workflows
    mv .github/workflows-disabled/* .github/workflows-backup/experimental/ 2>/dev/null || true
    rmdir .github/workflows-disabled 2>/dev/null || true
    print_success "Moved disabled workflows to backup"
else
    print_warning "No disabled workflows directory found"
fi

# Identify production workflows
print_status "Identifying production workflows..."
PRODUCTION_WORKFLOWS=(
    "openssl-build-publish.yml"
    "conan-ci.yml"
    "static-analysis.yml"
    "style-checks.yml"
)

# Move non-production workflows to backup
print_status "Moving non-production workflows to backup..."
for workflow in .github/workflows/*.yml; do
    if [ -f "$workflow" ]; then
        filename=$(basename "$workflow")
        if [[ " ${PRODUCTION_WORKFLOWS[@]} " =~ " ${filename} " ]]; then
            print_status "Keeping production workflow: $filename"
        else
            mv "$workflow" .github/workflows-backup/experimental/
            print_status "Moved to experimental: $filename"
        fi
    fi
done

# Create README files for backup directories
print_status "Creating README files for backup directories..."

# Main backup README
cat > .github/workflows-backup/README.md << 'EOF'
# Archived Workflows

This directory contains workflows that are not actively used but preserved for reference and potential future adaptation.

## Structure

### `legacy-openssl/`
Workflows from upstream openssl/tools that are incompatible with the Conan 2.0 modernization.

### `upstream-only/`
Workflows specifically designed for the OpenSSL source repository.

### `experimental/`
Workflows from PR #6 development iterations and experimental approaches.

## Usage Guidelines

- **Reference only**: These workflows are for reference and historical context
- **Do not activate**: Never enable these workflows directly
- **Adapt carefully**: If adapting, use current production workflows as base
- **Document changes**: Document any adaptations for future reference
EOF

# Legacy OpenSSL README
cat > .github/workflows-backup/legacy-openssl/README.md << 'EOF'
# Legacy OpenSSL Workflows

Workflows from upstream openssl/tools that are incompatible with Conan 2.0 modernization.

## Why Archived
- Incompatible build system (Configure + Make vs Conan)
- Missing OpenSSL source files and directories
- Different purpose (source development vs package management)

## Adaptation Guidelines
1. Replace OpenSSL source references with Conan package references
2. Use conanfile.py instead of Configure/config
3. Use conan-profiles/ instead of OpenSSL-specific configs
4. Focus on package building rather than source compilation
EOF

# Experimental README
cat > .github/workflows-backup/experimental/README.md << 'EOF'
# Experimental Workflows

Workflows from PR #6 development iterations and experimental approaches.

## Categories
- Success approaches (nuclear, minimal, simple)
- Optimization attempts (fast-lane, incremental, optimized)
- Consolidation attempts (consolidated, comprehensive)
- Conan-specific experiments
- Platform-specific experiments
- Integration experiments

## Lessons Learned
- Conan 2.0 approach was the right direction
- Reusable workflows work well
- Gradual migration is better than big bangs
- Clear separation of concerns is important
EOF

# Count workflows
print_status "Counting workflows..."
ACTIVE_COUNT=$(find .github/workflows -name "*.yml" -not -path "*/reusable/*" -not -path "*/templates/*" | wc -l)
LEGACY_COUNT=$(find .github/workflows-backup/legacy-openssl -name "*.yml" 2>/dev/null | wc -l)
EXPERIMENTAL_COUNT=$(find .github/workflows-backup/experimental -name "*.yml" 2>/dev/null | wc -l)
UPSTREAM_COUNT=$(find .github/workflows-backup/upstream-only -name "*.yml" 2>/dev/null | wc -l)
TOTAL_ARCHIVED=$((LEGACY_COUNT + EXPERIMENTAL_COUNT + UPSTREAM_COUNT))

# Summary
echo ""
print_success "Workflow consolidation complete!"
echo ""
echo "📊 Summary:"
echo "  Active workflows: $ACTIVE_COUNT"
echo "  Archived workflows: $TOTAL_ARCHIVED"
echo "    - Legacy OpenSSL: $LEGACY_COUNT"
echo "    - Experimental: $EXPERIMENTAL_COUNT"
echo "    - Upstream-only: $UPSTREAM_COUNT"
echo ""
echo "📁 Directory structure:"
echo "  .github/workflows/           # Active production workflows"
echo "  .github/workflows/reusable/  # Reusable workflow components"
echo "  .github/workflow-templates/  # Workflow templates"
echo "  .github/workflows-backup/    # Archived workflows"
echo ""

# Verify production workflows exist
print_status "Verifying production workflows..."
MISSING_WORKFLOWS=()
for workflow in "${PRODUCTION_WORKFLOWS[@]}"; do
    if [ ! -f ".github/workflows/$workflow" ]; then
        MISSING_WORKFLOWS+=("$workflow")
    fi
done

if [ ${#MISSING_WORKFLOWS[@]} -eq 0 ]; then
    print_success "All production workflows are present"
else
    print_warning "Missing production workflows:"
    for workflow in "${MISSING_WORKFLOWS[@]}"; do
        echo "  - $workflow"
    done
fi

# Check for any remaining .yml files in workflows directory
REMAINING_WORKFLOWS=$(find .github/workflows -name "*.yml" -not -path "*/reusable/*" -not -path "*/templates/*" | wc -l)
if [ "$REMAINING_WORKFLOWS" -gt "$ACTIVE_COUNT" ]; then
    print_warning "Found additional workflow files that may need attention"
    find .github/workflows -name "*.yml" -not -path "*/reusable/*" -not -path "*/templates/*"
fi

echo ""
print_success "Consolidation script completed successfully!"
echo ""
echo "Next steps:"
echo "1. Review the active workflows in .github/workflows/"
echo "2. Test the workflows to ensure they work correctly"
echo "3. Update documentation as needed"
echo "4. Commit the changes to version control"