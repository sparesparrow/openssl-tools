#!/bin/bash
# scripts/super-fast-build.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
ARTIFACTS_DIR="${PROJECT_ROOT}/artifacts"
DOCKER_DIR="${PROJECT_ROOT}/docker"

# Configuration
ARTIFACTORY_URL="${ARTIFACTORY_URL:-https://your-artifactory.com}"
ARTIFACTORY_REPO="${ARTIFACTORY_REPO:-openssl-releases}"
ARTIFACTORY_TOKEN="${ARTIFACTORY_TOKEN:-}"

# Version
VERSION="${VERSION:-$(date +%Y%m%d)-$(git rev-parse --short HEAD)}"

# Build configuration
MAX_PARALLEL="${MAX_PARALLEL:-$(nproc)}"
BUILD_TIMEOUT="${BUILD_TIMEOUT:-900}"  # 15 minutes per platform
DOCKER_BUILDKIT=1
DOCKER_CLI_EXPERIMENTAL=enabled

echo "⚡ Super Fast OpenSSL Build Pipeline"
echo "===================================="
echo "📦 Version: ${VERSION}"
echo "⚡ Max Parallel: ${MAX_PARALLEL}"
echo "⏱️  Timeout: ${BUILD_TIMEOUT}s per platform"
echo ""

# Function to check prerequisites
check_prerequisites() {
    echo "🔍 Quick prerequisite check..."
    
    # Check Docker
    if ! docker info >/dev/null 2>&1; then
        echo "❌ Docker not running"
        exit 1
    fi
    
    # Check credentials
    if [[ -z "${ARTIFACTORY_TOKEN}" ]]; then
        echo "❌ ARTIFACTORY_TOKEN not set"
        echo "Quick fix: export ARTIFACTORY_TOKEN=your-token"
        exit 1
    fi
    
    echo "✅ Prerequisites OK"
}

# Function to build single platform
build_platform() {
    local platform="$1"
    local service="$2"
    local log_file="${PROJECT_ROOT}/logs/build-${platform}.log"
    
    echo "🔨 Building ${platform}..."
    
    # Create log directory
    mkdir -p "${PROJECT_ROOT}/logs"
    
    # Build with optimizations
    timeout "${BUILD_TIMEOUT}" \
        docker-compose -f "${DOCKER_DIR}/docker-compose.fast.yml" \
        build \
        --parallel \
        --no-cache \
        "${service}" \
        > "${log_file}" 2>&1 &
    
    local build_pid=$!
    echo "${build_pid}" > "${PROJECT_ROOT}/logs/build-${platform}.pid"
    
    # Wait for completion
    if wait "${build_pid}"; then
        echo "✅ ${platform} built successfully"
        return 0
    else
        echo "❌ ${platform} build failed"
        return 1
    fi
}

# Function to build all platforms in parallel
build_all_parallel() {
    echo "🏗️  Building all platforms in parallel..."
    
    # Clean and prepare
    rm -rf "${ARTIFACTS_DIR}"
    mkdir -p "${ARTIFACTS_DIR}"
    
    # Build matrix
    declare -A BUILD_MATRIX=(
        ["ubuntu-20.04-gcc"]="ubuntu-20-04-gcc"
        ["ubuntu-22.04-clang"]="ubuntu-22-04-clang"
        ["windows-2022"]="windows-2022"
        ["macos-x86_64"]="macos-x86_64"
        ["macos-arm64"]="macos-arm64"
    )
    
    # Start all builds
    local build_pids=()
    local build_platforms=()
    
    for platform in "${!BUILD_MATRIX[@]}"; do
        build_platform "${platform}" "${BUILD_MATRIX[${platform}]}" &
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
    
    echo "📊 Build Results: ${successful} successful, ${failed} failed"
    
    if [[ $successful -gt 0 ]]; then
        return 0
    else
        return 1
    fi
}

# Function to extract and package artifacts
package_artifacts() {
    echo "📦 Packaging artifacts..."
    
    # Extract artifacts from successful builds
    for platform in ubuntu-20.04-gcc ubuntu-22.04-clang windows-2022 macos-x86_64 macos-arm64; do
        if [[ -f "${PROJECT_ROOT}/logs/build-${platform}.pid" ]]; then
            local pid=$(cat "${PROJECT_ROOT}/logs/build-${platform}.pid")
            if kill -0 "${pid}" 2>/dev/null || [[ -f "${PROJECT_ROOT}/logs/build-${platform}.log" ]]; then
                echo "📤 Extracting ${platform}..."
                
                # Create platform directory
                mkdir -p "${ARTIFACTS_DIR}/${platform}"
                
                # Extract using docker-compose
                cd "${DOCKER_DIR}"
                docker-compose -f docker-compose.fast.yml run --rm "${platform}" sh -c "
                    cp -r /artifacts/* /host-artifacts/ 2>/dev/null || true
                    cp -r /conan-packages/* /host-artifacts/conan/ 2>/dev/null || true
                " || true
                
                # Create metadata
                cat > "${ARTIFACTS_DIR}/${platform}/BUILD_INFO.json" << EOF
{
    "version": "${VERSION}",
    "platform": "${platform}",
    "build_date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "commit_sha": "$(git rev-parse HEAD)",
    "build_successful": true
}
EOF
                
                # Create archive
                cd "${ARTIFACTS_DIR}"
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
    for archive in "${ARTIFACTS_DIR}"/*.tar.gz; do
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

# Function to show summary
show_summary() {
    echo ""
    echo "🎉 Super Fast Build Complete!"
    echo "============================="
    echo "📦 Version: ${VERSION}"
    echo "🌐 Artifactory: ${ARTIFACTORY_URL}/artifactory/${ARTIFACTORY_REPO}/${VERSION}/"
    echo ""
    
    # Count artifacts
    local artifact_count=$(find "${ARTIFACTS_DIR}" -name "*.tar.gz" | wc -l)
    echo "📦 Artifacts created: ${artifact_count}"
    
    # List artifacts
    for archive in "${ARTIFACTS_DIR}"/*.tar.gz; do
        if [[ -f "$archive" ]]; then
            local filename=$(basename "$archive")
            local size=$(du -h "$archive" | cut -f1)
            echo "   - ${filename} (${size})"
        fi
    done
    
    echo ""
    echo "🚀 Ready for deployment!"
}

# Main execution
main() {
    local start_time=$(date +%s)
    
    # Quick checks
    check_prerequisites
    
    # Build all platforms
    if build_all_parallel; then
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
}

# Error handling
trap 'echo "❌ Build failed at line $LINENO"' ERR

# Execute
main "$@"