#!/bin/bash
# scripts/docker-build-and-upload.sh

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
ARTIFACTS_DIR="${PROJECT_ROOT}/artifacts"
DOCKER_DIR="${PROJECT_ROOT}/docker"

# Artifactory configuration
ARTIFACTORY_URL="${ARTIFACTORY_URL:-https://your-artifactory.com}"
ARTIFACTORY_REPO="${ARTIFACTORY_REPO:-openssl-releases}"
ARTIFACTORY_TOKEN="${ARTIFACTORY_TOKEN:-}"

# Version detection
if [[ "${GITHUB_REF_Type:-}" == "tag" ]]; then
    VERSION="${GITHUB_REF_NAME}"
    PACKAGE_TYPE="release"
else
    VERSION="$(date +%Y%m%d)-$(git rev-parse --short HEAD)"
    PACKAGE_TYPE="snapshot"
fi

echo "🚀 Starting Docker-based OpenSSL build pipeline"
echo "📦 Version: ${VERSION}"
echo "🏷️  Type: ${PACKAGE_TYPE}"

# Function to activate cursor agent
activate_cursor_agent() {
    local agent_name="$1"
    local repo_path="$2"
    
    echo "🤖 Activating Cursor Agent: ${agent_name}"
    
    if command -v cursor-agent >/dev/null 2>&1; then
        cursor-agent activate \
            --name="${agent_name}" \
            --repository="${repo_path}" \
            --mode="background" \
            --task="build-coordination" \
            --context="docker-pipeline" \
            --timeout="3600"
    else
        echo "⚠️  cursor-agent command not found, skipping agent activation"
    fi
}

# Function to build platform artifacts
build_platform() {
    local platform="$1"
    local service="$2"
    
    echo "🔨 Building ${platform} artifacts using Docker"
    
    # Activate appropriate cursor agent
    case "${platform}" in
        ubuntu*|macos*)
            activate_cursor_agent "openssl-core-agent" "${PROJECT_ROOT}"
            ;;
        windows*)
            activate_cursor_agent "openssl-core-agent" "${PROJECT_ROOT}"
            ;;
    esac
    
    # Create platform artifacts directory
    mkdir -p "${ARTIFACTS_DIR}/${platform}"
    
    # Build with docker-compose
    cd "${DOCKER_DIR}"
    docker-compose build "${service}"
    
    # Extract artifacts
    docker-compose run --rm "${service}" sh -c "
        cp -r /artifacts/* /host-artifacts/ 2>/dev/null || true
        cp -r /conan-packages/* /host-artifacts/conan/ 2>/dev/null || true
    " || true
    
    # Generate build metadata
    cat > "${ARTIFACTS_DIR}/${platform}/BUILD_INFO.json" << EOF
{
    "version": "${VERSION}",
    "platform": "${platform}", 
    "build_date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "commit_sha": "$(git rev-parse HEAD)",
    "docker_image": "${service}",
    "package_type": "${PACKAGE_TYPE}"
}
EOF
    
    # Generate SBOM
    if [[ -f "${PROJECT_ROOT}/scripts/generate_sbom.py" ]]; then
        python3 "${PROJECT_ROOT}/scripts/generate_sbom.py" \
            --build-info "${ARTIFACTS_DIR}/${platform}/BUILD_INFO.json" \
            --output "${ARTIFACTS_DIR}/${platform}/SBOM.json"
    fi
    
    # Create checksums
    cd "${ARTIFACTS_DIR}/${platform}"
    find . -type f -exec sha256sum {} \; > SHA256SUMS
    
    # Create platform archive
    cd "${ARTIFACTS_DIR}"
    tar czf "openssl-${VERSION}-${platform}.tar.gz" "${platform}/"
    
    echo "✅ ${platform} build completed"
}

# Function to upload to Artifactory using Docker
upload_to_artifactory() {
    local artifact_path="$1"
    local platform="$2"
    
    echo "📤 Uploading ${platform} to Artifactory"
    
    # Activate tools agent for upload coordination
    activate_cursor_agent "openssl-tools-agent" "${PROJECT_ROOT}/../openssl-tools"
    
    # Use curl in Docker container for consistent uploads
    docker run --rm \
        -v "${ARTIFACTS_DIR}:/artifacts:ro" \
        -e ARTIFACTORY_URL="${ARTIFACTORY_URL}" \
        -e ARTIFACTORY_TOKEN="${ARTIFACTORY_TOKEN}" \
        -e VERSION="${VERSION}" \
        -e PACKAGE_TYPE="${PACKAGE_TYPE}" \
        --name openssl-uploader \
        curlimages/curl:latest \
        sh -c "
            # Upload main artifact
            curl -f \
                -H 'Authorization: Bearer \${ARTIFACTORY_TOKEN}' \
                -T '/artifacts/${artifact_path}' \
                '\${ARTIFACTORY_URL}/artifactory/\${ARTIFACTORY_REPO}/\${VERSION}/${artifact_path}'
            
            # Upload checksums
            curl -f \
                -H 'Authorization: Bearer \${ARTIFACTORY_TOKEN}' \
                -T '/artifacts/${platform}/SHA256SUMS' \
                '\${ARTIFACTORY_URL}/artifactory/\${ARTIFACTORY_REPO}/\${VERSION}/${platform}-SHA256SUMS'
            
            # Upload SBOM
            if [[ -f '/artifacts/${platform}/SBOM.json' ]]; then
                curl -f \
                    -H 'Authorization: Bearer \${ARTIFACTORY_TOKEN}' \
                    -T '/artifacts/${platform}/SBOM.json' \
                    '\${ARTIFACTORY_URL}/artifactory/\${ARTIFACTORY_REPO}/\${VERSION}/${platform}-SBOM.json'
            fi
        "
    
    echo "✅ ${platform} uploaded to Artifactory"
}

# Function to upload Conan packages
upload_conan_packages() {
    echo "📦 Uploading Conan packages to Artifactory"
    
    # Setup Conan remote
    docker run --rm \
        -v "${HOME}/.conan2:/root/.conan2" \
        -v "${ARTIFACTS_DIR}:/artifacts:ro" \
        -e ARTIFACTORY_URL="${ARTIFACTORY_URL}" \
        -e ARTIFACTORY_TOKEN="${ARTIFACTORY_TOKEN}" \
        --name conan-uploader \
        conanio/conan:2.0 \
        sh -c "
            # Configure Artifactory remote
            conan remote add artifactory \${ARTIFACTORY_URL}/artifactory/api/conan/conan
            conan remote login artifactory admin -p \${ARTIFACTORY_TOKEN}
            
            # Copy packages from all platforms
            find /artifacts -name 'conan-packages' -type d | while read conan_dir; do
                if [[ -d \"\${conan_dir}\" ]]; then
                    cp -r \"\${conan_dir}\"/* /root/.conan2/p/ 2>/dev/null || true
                fi
            done
            
            # Upload all OpenSSL packages
            conan upload 'openssl/*' -r=artifactory --confirm
        "
    
    echo "✅ Conan packages uploaded"
}

# Function to validate uploaded packages
validate_packages() {
    echo "🔍 Validating uploaded packages"
    
    # Test Conan package installation
    docker run --rm \
        -v "${PROJECT_ROOT}:/src:ro" \
        -e ARTIFACTORY_URL="${ARTIFACTORY_URL}" \
        -e ARTIFACTORY_TOKEN="${ARTIFACTORY_TOKEN}" \
        -e VERSION="${VERSION}" \
        --name package-validator \
        conanio/conan:2.0 \
        sh -c "
            # Configure remote
            conan remote add artifactory \${ARTIFACTORY_URL}/artifactory/api/conan/conan
            conan remote login artifactory admin -p \${ARTIFACTORY_TOKEN}
            
            # Try to install the package we just uploaded
            mkdir -p /tmp/test && cd /tmp/test
            echo '[requires]' > conanfile.txt
            echo 'openssl/[\${VERSION}]' >> conanfile.txt
            echo '[generators]' >> conanfile.txt
            echo 'CMakeDeps' >> conanfile.txt
            echo 'CMakeToolchain' >> conanfile.txt
            
            conan install . -r=artifactory --build=missing
            
            if [[ -f 'conan_toolchain.cmake' ]]; then
                echo '✅ Conan package validation successful'
            else
                echo '❌ Conan package validation failed'
                exit 1
            fi
        "
    
    # Test artifact download
    docker run --rm \
        -e ARTIFACTORY_URL="${ARTIFACTORY_URL}" \
        -e ARTIFACTORY_TOKEN="${ARTIFACTORY_TOKEN}" \
        -e VERSION="${VERSION}" \
        --name artifact-validator \
        curlimages/curl:latest \
        sh -c "
            # Test download of Ubuntu artifact
            curl -f \
                -H 'Authorization: Bearer \${ARTIFACTORY_TOKEN}' \
                -o /tmp/test-artifact.tar.gz \
                '\${ARTIFACTORY_URL}/artifactory/\${ARTIFACTORY_REPO}/\${VERSION}/openssl-\${VERSION}-ubuntu-22.04-clang.tar.gz'
            
            if [[ -f '/tmp/test-artifact.tar.gz' ]]; then
                echo '✅ Artifact download validation successful'
            else
                echo '❌ Artifact download validation failed'
                exit 1
            fi
        "
    
    echo "✅ Package validation completed"
}

# Main execution
main() {
    echo "🚀 Starting main build pipeline"
    
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
    
    # Build all platforms
    for platform in "${!BUILD_MATRIX[@]}"; do
        build_platform "${platform}" "${BUILD_MATRIX[${platform}]}"
    done
    
    # Upload artifacts
    for platform in "${!BUILD_MATRIX[@]}"; do
        artifact_name="openssl-${VERSION}-${platform}.tar.gz"
        if [[ -f "${ARTIFACTS_DIR}/${artifact_name}" ]]; then
            upload_to_artifactory "${artifact_name}" "${platform}"
        fi
    done
    
    # Upload Conan packages
    upload_conan_packages
    
    # Validate uploads
    validate_packages
    
    echo "🎉 Build and upload pipeline completed successfully!"
    echo "📊 Summary:"
    echo "   Version: ${VERSION}"
    echo "   Package Type: ${PACKAGE_TYPE}"
    echo "   Platforms: $(printf '%s ' "${!BUILD_MATRIX[@]}")"
    echo "   Artifactory: ${ARTIFACTORY_URL}/artifactory/${ARTIFACTORY_REPO}/${VERSION}/"
}

# Error handling
trap 'echo "❌ Build pipeline failed at line $LINENO"' ERR

# Execute main function
main "$@"