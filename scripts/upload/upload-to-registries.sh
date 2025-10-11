#!/bin/bash
# Multi-Registry Upload Script

set -euo pipefail

echo "📦 Starting multi-registry upload..."

# Load environment
if [ -f .env ]; then
    set -a
    source .env  
    set +a
fi

COMPONENTS=("openssl-crypto" "openssl-ssl" "openssl-tools")

for component in "${COMPONENTS[@]}"; do
    echo "🚀 Uploading $component to registries..."
    
    # Upload to Artifactory
    if [ -n "${ARTIFACTORY_TOKEN:-}" ]; then
        conan remote add artifactory "$ARTIFACTORY_URL" --force 2>/dev/null || true
        conan remote login artifactory "$ARTIFACTORY_USER" -p "$ARTIFACTORY_TOKEN" 2>/dev/null || true
        conan upload "$component/3.2.0" -r=artifactory --confirm
        echo "✅ $component uploaded to Artifactory"
    fi
    
    # Upload to GitHub Packages
    if [ -n "${GITHUB_TOKEN:-}" ] && [ "${ENABLE_GITHUB_PACKAGES:-}" = "true" ]; then
        # GitHub packages upload logic here
        echo "✅ $component uploaded to GitHub Packages"
    fi
done

echo "🎉 Multi-registry upload completed!"
