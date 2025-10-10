#!/bin/bash
# Repository Cleanup for Production Readiness
set -euo pipefail

echo "🧹 OpenSSL-Tools Repository Cleanup"
echo "===================================="

# Track what we're removing
CLEANUP_LOG="cleanup-report.txt"
echo "Cleanup Report - $(date)" > "$CLEANUP_LOG"
echo "==============================" >> "$CLEANUP_LOG"
echo "" >> "$CLEANUP_LOG"

# 1. Remove large accidental files
echo "1️⃣ Removing large accidental files..."
if [ -f "json" ]; then
    SIZE=$(du -h json | cut -f1)
    echo "  - Removing json ($SIZE)"
    echo "Removed: json ($SIZE)" >> "$CLEANUP_LOG"
    rm -f json
fi

if [ -f "os" ]; then
    SIZE=$(du -h os | cut -f1)
    echo "  - Removing os ($SIZE)"
    echo "Removed: os ($SIZE)" >> "$CLEANUP_LOG"
    rm -f os
fi

# 2. Remove old tarballs and build artifacts
echo "2️⃣ Removing old build artifacts..."
if [ -f "openssl-20251010-ba87b67-Linux-x86_64.tar.gz" ]; then
    echo "  - Removing old tarball"
    echo "Removed: openssl-20251010-ba87b67-Linux-x86_64.tar.gz" >> "$CLEANUP_LOG"
    rm -f openssl-20251010-ba87b67-Linux-x86_64.tar.gz
fi

# 3. Remove virtual environments (should not be in git)
echo "3️⃣ Removing virtual environments..."
if [ -d "conan-dev/venv" ]; then
    SIZE=$(du -sh conan-dev/venv | cut -f1)
    echo "  - Removing conan-dev/venv ($SIZE)"
    echo "Removed: conan-dev/venv/ ($SIZE)" >> "$CLEANUP_LOG"
    rm -rf conan-dev/venv
fi

# 4. Remove development-only files
echo "4️⃣ Removing development files..."
for file in workspace-analysis.log validate-phase1.sh openssl_tools.log; do
    if [ -f "$file" ]; then
        echo "  - Removing $file"
        echo "Removed: $file" >> "$CLEANUP_LOG"
        rm -f "$file"
    fi
done

# 5. Remove test artifacts and temporary directories
echo "5️⃣ Cleaning test artifacts..."
for dir in test-consumer artifacts logs; do
    if [ -d "$dir" ]; then
        SIZE=$(du -sh "$dir" 2>/dev/null | cut -f1 || echo "unknown")
        echo "  - Removing $dir/ ($SIZE)"
        echo "Removed: $dir/ ($SIZE)" >> "$CLEANUP_LOG"
        rm -rf "$dir"
    fi
done

# 6. Remove Python cache files
echo "6️⃣ Removing Python cache..."
find . -type d -name "__pycache__" -not -path "./venv/*" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -not -path "./venv/*" -delete 2>/dev/null || true
echo "Removed: __pycache__ directories and *.pyc files" >> "$CLEANUP_LOG"

# 7. Remove temporary files
echo "7️⃣ Removing temporary files..."
find . -name "*.tmp" -delete 2>/dev/null || true
find . -name "*.swp" -delete 2>/dev/null || true
find . -name "*.swo" -delete 2>/dev/null || true
find . -name ".DS_Store" -delete 2>/dev/null || true
echo "Removed: temporary files (*.tmp, *.swp, .DS_Store)" >> "$CLEANUP_LOG"

# 8. Report final size
echo ""
echo "✅ Repository cleanup complete!"
echo ""
echo "📊 Cleanup Summary:"
cat "$CLEANUP_LOG"
echo ""
echo "📏 New repository size:"
du -sh .
echo ""
echo "💾 Cleanup report saved to: $CLEANUP_LOG"

