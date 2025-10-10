#!/bin/bash
# scripts/build-all-platforms-now.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "⚡ BUILD ALL PLATFORMS NOW - MAXIMUM SPEED"
echo "=========================================="
echo ""

# Configuration
ARTIFACTORY_URL="${ARTIFACTORY_URL:-}"
ARTIFACTORY_TOKEN="${ARTIFACTORY_TOKEN:-}"
ARTIFACTORY_REPO="${ARTIFACTORY_REPO:-openssl-releases}"
VERSION="${VERSION:-$(date +%Y%m%d)-$(git rev-parse --short HEAD)}"

# Build settings
MAX_PARALLEL="${MAX_PARALLEL:-$(nproc)}"
BUILD_TIMEOUT="${BUILD_TIMEOUT:-600}"  # 10 minutes per platform
DOCKER_BUILDKIT=1
DOCKER_CLI_EXPERIMENTAL=enabled

# Export for Docker
export DOCKER_BUILDKIT DOCKER_CLI_EXPERIMENTAL

echo "📦 Version: ${VERSION}"
echo "⚡ Parallel builds: ${MAX_PARALLEL}"
echo "⏱️  Timeout: ${BUILD_TIMEOUT}s per platform"
echo ""

# Function to check credentials
check_credentials() {
    if [[ -z "${ARTIFACTORY_URL}" || -z "${ARTIFACTORY_TOKEN}" ]]; then
        echo "❌ Missing credentials!"
        echo ""
        echo "Quick fix:"
        echo "export ARTIFACTORY_URL=your-url"
        echo "export ARTIFACTORY_TOKEN=your-token"
        echo ""
        echo "Or run: ./scripts/quick-start.sh setup"
        exit 1
    fi
    echo "✅ Credentials OK"
}

# Function to build single platform with maximum speed
build_platform_fast() {
    local platform="$1"
    local service="$2"
    
    echo "🚀 Building ${platform}..."
    
    # Build with all optimizations
    timeout "${BUILD_TIMEOUT}" \
        docker build \
        --build-arg UBUNTU_VERSION="22.04" \
        --build-arg COMPILER="gcc-11" \
        --build-arg BUILD_TYPE="Release" \
        --build-arg ENABLE_FIPS="ON" \
        --target artifacts \
        --tag "openssl-${platform}:latest" \
        -f "${PROJECT_ROOT}/docker/Dockerfile.ubuntu-builder-fast" \
        "${PROJECT_ROOT}" \
        > "${PROJECT_ROOT}/logs/build-${platform}.log" 2>&1 &
    
    local build_pid=$!
    echo "${build_pid}" > "${PROJECT_ROOT}/logs/build-${platform}.pid"
    
    if wait "${build_pid}"; then
        echo "✅ ${platform} built"
        return 0
    else
        echo "❌ ${platform} failed"
        return 1
    fi
}

# Function to build all platforms in parallel
build_all_platforms() {
    echo "🏗️  Building all platforms in parallel..."
    
    # Clean and prepare
    rm -rf "${PROJECT_ROOT}/artifacts"
    mkdir -p "${PROJECT_ROOT}/artifacts" "${PROJECT_ROOT}/logs"
    
    # Platform definitions
    declare -A PLATFORMS=(
        ["ubuntu-20.04-gcc"]="ubuntu-20.04-gcc"
        ["ubuntu-22.04-clang"]="ubuntu-22.04-clang"
        ["windows-2022"]="windows-2022"
        ["macos-x86_64"]="macos-x86_64"
        ["macos-arm64"]="macos-arm64"
    )
    
    # Start all builds
    local build_pids=()
    local build_platforms=()
    
    for platform in "${!PLATFORMS[@]}"; do
        build_platform_fast "${platform}" "${PLATFORMS[${platform}]}" &
        build_pids+=($!)
        build_platforms+=("${platform}")
    done
    
    # Wait for all builds
    local successful=0
    local failed=0
    
    for i in "${!build_pids[@]}"; do
        if wait "${build_pids[$i]}"; then
            successful=$((successful + 1))
        else
            failed=$((failed + 1))
        fi
    done
    
    echo "📊 Results: ${successful} successful, ${failed} failed"
    
    if [[ $successful -gt 0 ]]; then
        return 0
    else
        return 1
    fi
}

# Function to extract and package artifacts
package_artifacts() {
    echo "📦 Packaging artifacts..."
    
    # Extract from successful builds
    for platform in ubuntu-20.04-gcc ubuntu-22.04-clang windows-2022 macos-x86_64 macos-arm64; do
        if [[ -f "${PROJECT_ROOT}/logs/build-${platform}.pid" ]]; then
            local pid=$(cat "${PROJECT_ROOT}/logs/build-${platform}.pid")
            if kill -0 "${pid}" 2>/dev/null || [[ -f "${PROJECT_ROOT}/logs/build-${platform}.log" ]]; then
                echo "📤 Extracting ${platform}..."
                
                # Create platform directory
                mkdir -p "${PROJECT_ROOT}/artifacts/${platform}"
                
                # Extract artifacts
                docker run --rm \
                    -v "${PROJECT_ROOT}/artifacts/${platform}:/host-artifacts" \
                    "openssl-${platform}:latest" \
                    sh -c "cp -r /artifacts/* /host-artifacts/ 2>/dev/null || true" || true
                
                # Create metadata
                cat > "${PROJECT_ROOT}/artifacts/${platform}/BUILD_INFO.json" << EOF
{
    "version": "${VERSION}",
    "platform": "${platform}",
    "build_date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "commit_sha": "$(git rev-parse HEAD)",
    "build_successful": true
}
EOF
                
                # Create archive
                cd "${PROJECT_ROOT}/artifacts"
                if [[ -d "${platform}" ]]; then
                    tar czf "openssl-${VERSION}-${platform}.tar.gz" "${platform}/"
                    echo "✅ Created: openssl-${VERSION}-${platform}.tar.gz"
                fi
            fi
        fi
    done
}

# Function to upload artifacts
upload_artifacts() {
    echo "📤 Uploading artifacts..."
    
    local upload_count=0
    
    # Upload all archives
    for archive in "${PROJECT_ROOT}/artifacts"/*.tar.gz; do
        if [[ -f "$archive" ]]; then
            local filename=$(basename "$archive")
            echo "📤 Uploading ${filename}..."
            
            if curl -s -f \
                -H "Authorization: Bearer ${ARTIFACTORY_TOKEN}" \
                -T "${archive}" \
                "${ARTIFACTORY_URL}/artifactory/${ARTIFACTORY_REPO}/${VERSION}/${filename}"; then
                echo "✅ ${filename} uploaded"
                upload_count=$((upload_count + 1))
            else
                echo "❌ ${filename} upload failed"
            fi
        fi
    done
    
    echo "📊 Uploaded ${upload_count} artifacts"
}

# Function to show final summary
show_summary() {
    echo ""
    echo "🎉 BUILD COMPLETE!"
    echo "=================="
    echo "📦 Version: ${VERSION}"
    echo "🌐 Artifactory: ${ARTIFACTORY_URL}/artifactory/${ARTIFACTORY_REPO}/${VERSION}/"
    echo ""
    
    # Count artifacts
    local artifact_count=$(find "${PROJECT_ROOT}/artifacts" -name "*.tar.gz" | wc -l)
    echo "📦 Artifacts: ${artifact_count}"
    
    # List artifacts
    for archive in "${PROJECT_ROOT}/artifacts"/*.tar.gz; do
        if [[ -f "$archive" ]]; then
            local filename=$(basename "$archive")
            local size=$(du -h "$archive" | cut -f1)
            echo "   - ${filename} (${size})"
        fi
    done
    
    echo ""
    echo "🚀 All platforms built and uploaded!"
}

# Main execution
main() {
    local start_time=$(date +%s)
    
    echo "🚀 Starting maximum speed build at $(date)"
    echo ""
    
    # Quick checks
    check_credentials
    
    # Build all platforms
    if build_all_platforms; then
        echo "✅ All builds completed"
    else
        echo "❌ Some builds failed"
        exit 1
    fi
    
    # Package artifacts
    package_artifacts
    
    # Upload artifacts
    upload_artifacts
    
    # Show summary
    show_summary
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    echo "⏱️  Total time: ${duration}s ($(($duration / 60))m)"
    echo "🎉 DONE!"
}

# Error handling
trap 'echo "❌ Build failed at line $LINENO"' ERR

# Execute
main "$@"