#!/bin/bash
# scripts/fast-build-and-upload.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
ARTIFACTS_DIR="${PROJECT_ROOT}/artifacts"
DOCKER_DIR="${PROJECT_ROOT}/docker"

# Configuration
ARTIFACTORY_URL="${ARTIFACTORY_URL:-https://your-artifactory.com}"
ARTIFACTORY_REPO="${ARTIFACTORY_REPO:-openssl-releases}"
ARTIFACTORY_TOKEN="${ARTIFACTORY_TOKEN:-}"

# Version detection
if [[ "${GITHUB_REF_TYPE:-}" == "tag" ]]; then
    VERSION="${GITHUB_REF_NAME}"
    PACKAGE_TYPE="release"
else
    VERSION="$(date +%Y%m%d)-$(git rev-parse --short HEAD)"
    PACKAGE_TYPE="snapshot"
fi

# Parallel build configuration
MAX_PARALLEL_BUILDS="${MAX_PARALLEL_BUILDS:-$(nproc)}"
BUILD_TIMEOUT="${BUILD_TIMEOUT:-1800}"  # 30 minutes per platform

echo "🚀 Fast OpenSSL Build and Upload Pipeline"
echo "=========================================="
echo "📦 Version: ${VERSION}"
echo "🏷️  Type: ${PACKAGE_TYPE}"
echo "⚡ Max Parallel Builds: ${MAX_PARALLEL_BUILDS}"
echo ""

# Function to check prerequisites
check_prerequisites() {
    echo "🔍 Checking prerequisites..."
    
    local errors=0
    
    # Check Docker
    if ! docker info >/dev/null 2>&1; then
        echo "❌ Docker is not running"
        errors=$((errors + 1))
    else
        echo "✅ Docker is running"
    fi
    
    # Check Artifactory credentials
    if [[ -z "${ARTIFACTORY_URL}" || "${ARTIFACTORY_URL}" == "https://your-artifactory.com" ]]; then
        echo "❌ ARTIFACTORY_URL not configured"
        errors=$((errors + 1))
    else
        echo "✅ Artifactory URL configured"
    fi
    
    if [[ -z "${ARTIFACTORY_TOKEN}" ]]; then
        echo "❌ ARTIFACTORY_TOKEN not configured"
        errors=$((errors + 1))
    else
        echo "✅ Artifactory token configured"
    fi
    
    # Check required directories
    if [[ ! -d "${DOCKER_DIR}" ]]; then
        echo "❌ Docker directory not found: ${DOCKER_DIR}"
        errors=$((errors + 1))
    else
        echo "✅ Docker directory found"
    fi
    
    if [[ $errors -gt 0 ]]; then
        echo "💥 $errors prerequisite errors found"
        echo ""
        echo "Quick fix:"
        echo "1. Start Docker: sudo systemctl start docker"
        echo "2. Set credentials: export ARTIFACTORY_URL=your-url && export ARTIFACTORY_TOKEN=your-token"
        echo "3. Or run: ./scripts/setup-credentials.sh"
        exit 1
    fi
    
    echo "✅ All prerequisites met"
}

# Function to build platform with timeout and error handling
build_platform_async() {
    local platform="$1"
    local service="$2"
    local log_file="${PROJECT_ROOT}/logs/build-${platform}.log"
    
    echo "🔨 Building ${platform} (PID: $$)"
    
    # Create log directory
    mkdir -p "${PROJECT_ROOT}/logs"
    
    # Build with timeout
    timeout "${BUILD_TIMEOUT}" \
        docker-compose -f "${DOCKER_DIR}/docker-compose.yml" build "${service}" \
        > "${log_file}" 2>&1 &
    
    local build_pid=$!
    echo "${build_pid}" > "${PROJECT_ROOT}/logs/build-${platform}.pid"
    
    # Wait for build to complete
    if wait "${build_pid}"; then
        echo "✅ ${platform} build completed"
        return 0
    else
        echo "❌ ${platform} build failed (check ${log_file})"
        return 1
    fi
}

# Function to build all platforms in parallel
build_all_platforms() {
    echo "🏗️  Building all platforms in parallel..."
    
    # Clean artifacts directory
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
    
    # Start all builds in parallel
    local build_pids=()
    local build_platforms=()
    
    for platform in "${!BUILD_MATRIX[@]}"; do
        echo "🚀 Starting build for ${platform}..."
        build_platform_async "${platform}" "${BUILD_MATRIX[${platform}]}" &
        build_pids+=($!)
        build_platforms+=("${platform}")
    done
    
    # Wait for all builds to complete
    echo "⏳ Waiting for all builds to complete..."
    local failed_builds=()
    local successful_builds=()
    
    for i in "${!build_pids[@]}"; do
        local pid="${build_pids[$i]}"
        local platform="${build_platforms[$i]}"
        
        if wait "${pid}"; then
            successful_builds+=("${platform}")
            echo "✅ ${platform} build successful"
        else
            failed_builds+=("${platform}")
            echo "❌ ${platform} build failed"
        fi
    done
    
    # Report results
    echo ""
    echo "📊 Build Results:"
    echo "✅ Successful: ${#successful_builds[@]} platforms"
    for platform in "${successful_builds[@]}"; do
        echo "   - ${platform}"
    done
    
    if [[ ${#failed_builds[@]} -gt 0 ]]; then
        echo "❌ Failed: ${#failed_builds[@]} platforms"
        for platform in "${failed_builds[@]}"; do
            echo "   - ${platform} (check logs/build-${platform}.log)"
        done
    fi
    
    # Return success if at least one platform built successfully
    if [[ ${#successful_builds[@]} -gt 0 ]]; then
        return 0
    else
        return 1
    fi
}

# Function to extract artifacts from successful builds
extract_artifacts() {
    echo "📦 Extracting artifacts from successful builds..."
    
    # Find successful builds
    local successful_builds=()
    for pid_file in "${PROJECT_ROOT}/logs/build-"*.pid; do
        if [[ -f "$pid_file" ]]; then
            local platform=$(basename "$pid_file" .pid | sed 's/build-//')
            if [[ -f "${PROJECT_ROOT}/logs/build-${platform}.log" ]]; then
                # Check if build was successful by looking for success indicators
                if grep -q "✅ ${platform} build completed" "${PROJECT_ROOT}/logs/build-${platform}.log" 2>/dev/null; then
                    successful_builds+=("${platform}")
                fi
            fi
        fi
    done
    
    # Extract artifacts for each successful build
    for platform in "${successful_builds[@]}"; do
        echo "📤 Extracting artifacts for ${platform}..."
        
        # Create platform artifacts directory
        mkdir -p "${ARTIFACTS_DIR}/${platform}"
        
        # Extract using docker-compose
        cd "${DOCKER_DIR}"
        docker-compose run --rm "${platform}" sh -c "
            # Copy artifacts if they exist
            if [[ -d /artifacts ]]; then
                cp -r /artifacts/* /host-artifacts/ 2>/dev/null || true
            fi
            if [[ -d /conan-packages ]]; then
                cp -r /conan-packages/* /host-artifacts/conan/ 2>/dev/null || true
            fi
        " || true
        
        # Generate build metadata
        cat > "${ARTIFACTS_DIR}/${platform}/BUILD_INFO.json" << EOF
{
    "version": "${VERSION}",
    "platform": "${platform}",
    "build_date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "commit_sha": "$(git rev-parse HEAD)",
    "package_type": "${PACKAGE_TYPE}",
    "build_successful": true
}
EOF
        
        # Generate checksums
        cd "${ARTIFACTS_DIR}/${platform}"
        find . -type f -name "*.so" -o -name "*.dll" -o -name "*.dylib" -o -name "openssl" -o -name "*.exe" | \
            xargs sha256sum > SHA256SUMS 2>/dev/null || true
        
        # Create platform archive
        cd "${ARTIFACTS_DIR}"
        if [[ -d "${platform}" ]]; then
            tar czf "openssl-${VERSION}-${platform}.tar.gz" "${platform}/"
            echo "✅ Created archive: openssl-${VERSION}-${platform}.tar.gz"
        fi
    done
}

# Function to upload artifacts to Artifactory
upload_artifacts() {
    echo "📤 Uploading artifacts to Artifactory..."
    
    local upload_count=0
    local failed_uploads=()
    
    # Find all artifact archives
    for archive in "${ARTIFACTS_DIR}"/*.tar.gz; do
        if [[ -f "$archive" ]]; then
            local filename=$(basename "$archive")
            local platform=$(echo "$filename" | sed "s/openssl-${VERSION}-//" | sed 's/.tar.gz//')
            
            echo "📤 Uploading ${filename}..."
            
            # Upload using curl
            if curl -s -f \
                -H "Authorization: Bearer ${ARTIFACTORY_TOKEN}" \
                -T "${archive}" \
                "${ARTIFACTORY_URL}/artifactory/${ARTIFACTORY_REPO}/${VERSION}/${filename}"; then
                echo "✅ ${filename} uploaded successfully"
                upload_count=$((upload_count + 1))
            else
                echo "❌ ${filename} upload failed"
                failed_uploads+=("${filename}")
            fi
        fi
    done
    
    # Upload checksums
    for platform_dir in "${ARTIFACTS_DIR}"/*/; do
        if [[ -d "$platform_dir" ]]; then
            local platform=$(basename "$platform_dir")
            local checksum_file="${platform_dir}/SHA256SUMS"
            
            if [[ -f "$checksum_file" ]]; then
                echo "📤 Uploading checksums for ${platform}..."
                curl -s -f \
                    -H "Authorization: Bearer ${ARTIFACTORY_TOKEN}" \
                    -T "${checksum_file}" \
                    "${ARTIFACTORY_URL}/artifactory/${ARTIFACTORY_REPO}/${VERSION}/${platform}-SHA256SUMS" || \
                    echo "⚠️  Checksum upload failed for ${platform}"
            fi
        fi
    done
    
    # Report upload results
    echo ""
    echo "📊 Upload Results:"
    echo "✅ Successful uploads: ${upload_count}"
    if [[ ${#failed_uploads[@]} -gt 0 ]]; then
        echo "❌ Failed uploads: ${#failed_uploads[@]}"
        for upload in "${failed_uploads[@]}"; do
            echo "   - ${upload}"
        done
    fi
}

# Function to upload Conan packages
upload_conan_packages() {
    echo "📦 Uploading Conan packages..."
    
    # Find Conan packages
    local conan_packages_found=false
    for platform_dir in "${ARTIFACTS_DIR}"/*/; do
        if [[ -d "${platform_dir}/conan" ]]; then
            conan_packages_found=true
            break
        fi
    done
    
    if [[ "$conan_packages_found" == "false" ]]; then
        echo "⚠️  No Conan packages found, skipping upload"
        return 0
    fi
    
    # Use Docker to upload Conan packages
    docker run --rm \
        -v "${ARTIFACTS_DIR}:/artifacts:ro" \
        -e ARTIFACTORY_URL="${ARTIFACTORY_URL}" \
        -e ARTIFACTORY_TOKEN="${ARTIFACTORY_TOKEN}" \
        conanio/conan:2.0 \
        sh -c "
            # Configure Artifactory remote
            conan remote add artifactory \${ARTIFACTORY_URL}/artifactory/api/conan/conan || true
            echo \${ARTIFACTORY_TOKEN} | conan remote login artifactory admin -p -
            
            # Copy packages from all platforms
            find /artifacts -name 'conan' -type d | while read conan_dir; do
                if [[ -d \"\${conan_dir}\" ]]; then
                    cp -r \"\${conan_dir}\"/* /root/.conan2/p/ 2>/dev/null || true
                fi
            done
            
            # Upload all OpenSSL packages
            conan upload 'openssl/*' -r=artifactory --confirm || echo 'No OpenSSL packages to upload'
        " && echo "✅ Conan packages uploaded" || echo "❌ Conan package upload failed"
}

# Function to generate build summary
generate_summary() {
    echo ""
    echo "🎉 Build and Upload Summary"
    echo "==========================="
    echo "📦 Version: ${VERSION}"
    echo "🏷️  Type: ${PACKAGE_TYPE}"
    echo "🌐 Artifactory: ${ARTIFACTORY_URL}/artifactory/${ARTIFACTORY_REPO}/${VERSION}/"
    echo ""
    
    # Count successful builds
    local successful_builds=0
    for pid_file in "${PROJECT_ROOT}/logs/build-"*.pid; do
        if [[ -f "$pid_file" ]]; then
            local platform=$(basename "$pid_file" .pid | sed 's/build-//')
            if grep -q "✅ ${platform} build completed" "${PROJECT_ROOT}/logs/build-${platform}.log" 2>/dev/null; then
                successful_builds=$((successful_builds + 1))
            fi
        fi
    done
    
    echo "📊 Build Results:"
    echo "   Successful builds: ${successful_builds}/5 platforms"
    echo "   Total platforms: ubuntu-20.04-gcc, ubuntu-22.04-clang, windows-2022, macos-x86_64, macos-arm64"
    echo ""
    
    # List uploaded artifacts
    echo "📦 Uploaded Artifacts:"
    for archive in "${ARTIFACTS_DIR}"/*.tar.gz; do
        if [[ -f "$archive" ]]; then
            local filename=$(basename "$archive")
            local size=$(du -h "$archive" | cut -f1)
            echo "   - ${filename} (${size})"
        fi
    done
    
    echo ""
    echo "🔗 Artifactory URL: ${ARTIFACTORY_URL}/artifactory/${ARTIFACTORY_REPO}/${VERSION}/"
    echo "📁 Local artifacts: ${ARTIFACTS_DIR}/"
    echo "📋 Build logs: ${PROJECT_ROOT}/logs/"
}

# Function to cleanup
cleanup() {
    echo "🧹 Cleaning up..."
    
    # Remove PID files
    rm -f "${PROJECT_ROOT}/logs/build-"*.pid
    
    # Keep logs for debugging but limit size
    find "${PROJECT_ROOT}/logs" -name "*.log" -size +10M -delete 2>/dev/null || true
    
    echo "✅ Cleanup completed"
}

# Main execution
main() {
    local start_time=$(date +%s)
    
    echo "🚀 Starting fast build and upload pipeline at $(date)"
    echo ""
    
    # Check prerequisites
    check_prerequisites
    
    # Build all platforms
    if build_all_platforms; then
        echo "✅ Build phase completed"
    else
        echo "❌ Build phase failed"
        exit 1
    fi
    
    # Extract artifacts
    extract_artifacts
    
    # Upload artifacts
    upload_artifacts
    
    # Upload Conan packages
    upload_conan_packages
    
    # Generate summary
    generate_summary
    
    # Cleanup
    cleanup
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    echo ""
    echo "⏱️  Total execution time: ${duration} seconds ($(($duration / 60)) minutes)"
    echo "🎉 Fast build and upload pipeline completed!"
}

# Error handling
trap 'echo "❌ Pipeline failed at line $LINENO"; cleanup; exit 1' ERR

# Execute main function
main "$@"