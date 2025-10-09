#!/usr/bin/env bash
# Disable Redundant Workflows to Reduce CI Checks from 202 to ~20-30
# This script helps identify and disable workflows that are redundant with core-ci.yml

set -euo pipefail

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

cd "$(dirname "$0")/.."

echo -e "${BOLD}${BLUE}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${BOLD}${BLUE}  CI Workflow Reduction Tool${NC}"
echo -e "${BOLD}${BLUE}═══════════════════════════════════════════════════════════════════${NC}\n"

echo "Current situation: 32 workflows = ~202 checks"
echo "Target: 5 workflows = ~20-30 checks"
echo "Reduction: 90%"
echo ""

# Workflows to KEEP
KEEP_WORKFLOWS=(
    "core-ci.yml"
    "style-checks.yml"
    "fips-checksums.yml"
    "optimized-basic-ci.yml"
)

# Workflows to DISABLE (redundant with core-ci.yml)
DISABLE_WORKFLOWS=(
    "ci.yml"
    "run-checker-ci.yml"
    "run-checker-daily.yml"
    "run-checker-merge.yml"
    "compiler-zoo.yml"
    "cross-compiles.yml"
    "riscv-more-cross-compiles.yml"
    "windows.yml"
    "windows_comp.yml"
    "os-zoo.yml"
    "perl-minimal-checker.yml"
    "binary-first-ci.yml"
    "incremental-ci-patch.yml"
    "main.yml"
    "coveralls.yml"
    "fuzz-checker.yml"
)

# Workflows to CONVERT to scheduled (not per-PR)
SCHEDULE_WORKFLOWS=(
    "external-tests-misc.yml"
    "external-tests-pyca.yml"
    "external-tests-oqs-provider.yml"
    "external-tests-pkcs11-provider.yml"
    "provider-compatibility.yml"
    "interop-tests.yml"
)

echo -e "${GREEN}KEEP (4 workflows):${NC}"
for wf in "${KEEP_WORKFLOWS[@]}"; do
    if [[ -f ".github/workflows/$wf" ]]; then
        echo -e "  ${GREEN}✓${NC} $wf"
    else
        echo -e "  ${YELLOW}⚠${NC} $wf (not found - needs creation)"
    fi
done

echo -e "\n${RED}DISABLE (${#DISABLE_WORKFLOWS[@]} workflows):${NC}"
for wf in "${DISABLE_WORKFLOWS[@]}"; do
    if [[ -f ".github/workflows/$wf" ]]; then
        echo -e "  ${RED}✗${NC} $wf"
    else
        echo -e "  ${BLUE}ℹ${NC} $wf (already missing)"
    fi
done

echo -e "\n${YELLOW}CONVERT TO SCHEDULE (${#SCHEDULE_WORKFLOWS[@]} workflows):${NC}"
for wf in "${SCHEDULE_WORKFLOWS[@]}"; do
    if [[ -f ".github/workflows/$wf" ]]; then
        echo -e "  ${YELLOW}⏰${NC} $wf"
    else
        echo -e "  ${BLUE}ℹ${NC} $wf (not found)"
    fi
done

echo ""
echo -e "${BOLD}Options:${NC}"
echo "  1. Rename redundant workflows (disable them)"
echo "  2. Show GitHub CLI commands to disable"
echo "  3. Show manual instructions"
echo "  4. Exit"
echo ""

read -p "Choose option [1-4]: " option

case $option in
    1)
        echo ""
        echo -e "${YELLOW}Renaming redundant workflows to .disabled...${NC}"
        for wf in "${DISABLE_WORKFLOWS[@]}"; do
            if [[ -f ".github/workflows/$wf" ]]; then
                mv ".github/workflows/$wf" ".github/workflows/$wf.disabled"
                echo -e "  ${GREEN}✓${NC} Disabled $wf"
            fi
        done
        
        echo ""
        echo -e "${GREEN}Done!${NC} Redundant workflows disabled."
        echo "Commit these changes to apply the reduction."
        echo ""
        echo "To re-enable a workflow:"
        echo "  mv .github/workflows/WORKFLOW.yml.disabled .github/workflows/WORKFLOW.yml"
        ;;
        
    2)
        echo ""
        echo -e "${BLUE}GitHub CLI commands to disable workflows:${NC}"
        echo ""
        for wf in "${DISABLE_WORKFLOWS[@]}"; do
            if [[ -f ".github/workflows/$wf" ]]; then
                echo "gh workflow disable \"$wf\""
            fi
        done
        echo ""
        echo "Copy and paste these commands to disable via GitHub API."
        ;;
        
    3)
        echo ""
        echo -e "${BLUE}Manual instructions:${NC}"
        echo ""
        echo "1. Go to: https://github.com/openssl/openssl/actions/workflows"
        echo "2. For each redundant workflow:"
        echo "   - Click on the workflow name"
        echo "   - Click '...' menu (top right)"
        echo "   - Click 'Disable workflow'"
        echo ""
        echo "Workflows to disable:"
        for wf in "${DISABLE_WORKFLOWS[@]}"; do
            echo "   • $wf"
        done
        ;;
        
    4)
        echo "Exiting."
        exit 0
        ;;
        
    *)
        echo -e "${RED}Invalid option${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${BOLD}${GREEN}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${BOLD}${GREEN}  Expected Result: 202 checks → ~20-30 checks (90% reduction!)${NC}"
echo -e "${BOLD}${GREEN}═══════════════════════════════════════════════════════════════════${NC}"
