#!/bin/bash
# OpenSSL Tools Repository Cleanup Script
# Removes temporary reports, logs, and IDE-specific files

set -e

echo "🧹 Starting OpenSSL Tools Repository Cleanup..."

# Create backup directory for important files we're moving
mkdir -p docs/backup

# Move important documentation before deletion
echo "📁 Moving important documentation to docs/..."
if [ -f ".cursor/README-cursor-agent-setup.md" ]; then
    mv .cursor/README-cursor-agent-setup.md docs/cursor-agent-setup.md
    echo "  ✅ Moved Cursor setup guide to docs/"
fi

if [ -f ".github/ci.md" ]; then
    mv .github/ci.md docs/ci-cd-guide.md
    echo "  ✅ Moved CI documentation to docs/"
fi

# Delete temporary status reports
echo "🗑️  Deleting temporary status reports..."
rm -f ACTUAL_WORKFLOW_STATUS.md
rm -f ARTIFACTS_REVIEW_SUMMARY.md
rm -f EXPERT_ANALYSIS_IMPLEMENTATION_SUMMARY.md
rm -f EXPERT_IMPLEMENTATION_FINAL_STATUS.md
rm -f EXTENDED_REALITY_CHECK_REPORT.md
rm -f FINAL_COMPLETION_REPORT.md
rm -f FINAL_QUEUE_STATUS_UPDATE.md
rm -f FINAL_STATUS_UPDATE.md
rm -f IMPLEMENTATION_COMPLETE_SUMMARY.md
rm -f IMPLEMENTATION_SUMMARY.md
rm -f IMPLEMENTATION_TESTING_RESULTS.md
rm -f IMPLEMENTED_FEATURES.md
rm -f QUEUE_MONITORING_UPDATE.md
rm -f WORKFLOW_EXECUTION_STATUS.md
rm -f WORKFLOW_FIXES_COMPLETE.md
rm -f WORKFLOW_FIXES_SUMMARY.md
rm -f YAML_FIX_SUMMARY.md
echo "  ✅ Deleted 18 temporary status reports"

# Delete phase completion reports
echo "🗑️  Deleting phase completion reports..."
rm -f PHASE1_COMPLETE.md
rm -f PHASE1_STATUS.md
rm -f PHASE2_COMPLETE.md
rm -f PHASE3_COMPLETE.md
rm -f PHASE3_PLAN.md
rm -f SETUP_COMPLETE.md
echo "  ✅ Deleted 6 phase completion reports"

# Delete GitHub workflow reports
echo "🗑️  Deleting GitHub workflow reports..."
rm -f .github/WORKFLOW_BATCH_STATUS.md
rm -f .github/WORKFLOW_FIXES_REPORT.md
rm -f .github/WORKFLOW_STATUS.md
echo "  ✅ Deleted 3 GitHub workflow reports"

# Delete documentation consolidation reports
echo "🗑️  Deleting documentation consolidation reports..."
rm -f DOCUMENTATION_CONSOLIDATION_SUMMARY.md
echo "  ✅ Deleted documentation consolidation report"

# Delete redundant README files
echo "🗑️  Deleting redundant README files..."
rm -f README-agent-loop-improved.md
rm -f README
echo "  ✅ Deleted 2 redundant README files"

# Delete test and development artifacts
echo "🗑️  Deleting test and development artifacts..."
rm -rf test_consumer/
rm -rf artifacts/
rm -rf logs/
rm -f cleanup-report.txt
echo "  ✅ Deleted test artifacts and logs"

# Remove .cursor/ from version control but keep locally
echo "🔧 Managing .cursor/ directory..."
if [ -d ".cursor" ]; then
    # Remove from git but keep locally
    git rm -r --cached .cursor/ 2>/dev/null || echo "  ℹ️  .cursor/ not in git index"
    echo "  ✅ Removed .cursor/ from version control"
fi

# Update .gitignore
echo "📝 Updating .gitignore..."
cat >> .gitignore << 'EOF'

# Cursor IDE configuration (local)
.cursor/

# Temporary reports and logs
*-report.md
*-status.md
*-summary.md
*_COMPLETE.md
*_STATUS.md
ACTUAL_*.md
EXPERT_*.md
FINAL_*.md
IMPLEMENTATION_*.md
QUEUE_*.md
WORKFLOW_*.md
YAML_*.md

# Test and development artifacts
test_consumer/
artifacts/
logs/
cleanup-report.txt

# Redundant README files
README-agent-loop-improved.md
README
EOF
echo "  ✅ Updated .gitignore"

# Clean up any remaining temporary files
echo "🧽 Final cleanup..."
find . -name "*.log" -type f -delete 2>/dev/null || true
find . -name "workspace-analysis.log" -type f -delete 2>/dev/null || true
echo "  ✅ Cleaned up log files"

echo ""
echo "🎉 Repository cleanup completed successfully!"
echo ""
echo "📊 Summary:"
echo "  • Deleted 30+ temporary markdown files"
echo "  • Removed .cursor/ from version control"
echo "  • Moved important docs to docs/ directory"
echo "  • Updated .gitignore to prevent future clutter"
echo "  • Cleaned up test artifacts and logs"
echo ""
echo "✨ Repository is now clean and professional!"