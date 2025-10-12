#!/bin/bash
# scripts/build-openssl-local.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
ARTIFACTS_DIR="${PROJECT_ROOT}/artifacts"

# Default configuration
VERSION="${VERSION:-$(date +%Y%m%d)-$(git rev-parse --short HEAD)}"
PROFILE="${PROFILE:-conan-profiles/ci-linux-gcc.profile}"
BUILD_TYPE="${BUILD_TYPE:-Release}"
ENABLE_FIPS="${ENABLE_FIPS:-false}"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --profile)
            PROFILE="$2"
            shift 2
            ;;
        --version)
            VERSION="$2"
            shift 2
            ;;
        --build-type)
            BUILD_TYPE="$2"
            shift 2
            ;;
        --fips)
            ENABLE_FIPS="$1"
            shift
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  --profile PROFILE    Conan profile to use (default: conan-profiles/ci-linux-gcc.profile)"
            echo "  --version VERSION    Version tag for artifacts"
            echo "  --build-type TYPE    Build type: Release or Debug (default: Release)"
            echo "  --fips              Enable FIPS mode"
            echo "  --help              Show this help"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "🔨 Local OpenSSL Build"
echo "======================"
echo "📦 Version: ${VERSION}"
echo "📋 Profile: ${PROFILE}"
echo "🏗️  Build Type: ${BUILD_TYPE}"
echo "🔐 FIPS: ${ENABLE_FIPS}"
echo ""

# Clean and prepare directories
echo "🧹 Preparing directories..."
rm -rf "${ARTIFACTS_DIR}"
mkdir -p "${ARTIFACTS_DIR}"

# Check if Conan is available
if ! command -v conan &> /dev/null; then
    echo "❌ Conan not found. Please install Conan 2.x"
    exit 1
fi

# Check if profile exists
if [[ ! -f "${PROJECT_ROOT}/${PROFILE}" ]]; then
    echo "❌ Profile not found: ${PROFILE}"
    exit 1
fi

# Set Conan options based on flags
CONAN_OPTIONS=""
if [[ "${ENABLE_FIPS}" == "true" ]]; then
    CONAN_OPTIONS="${CONAN_OPTIONS} -o fips=True"
fi

if [[ "${BUILD_TYPE}" == "Debug" ]]; then
    CONAN_OPTIONS="${CONAN_OPTIONS} -s build_type=Debug"
fi

echo "⚙️  Installing dependencies with Conan..."
cd "${PROJECT_ROOT}"

# Install dependencies
conan install . \
    --profile "${PROFILE}" \
    --build=missing \
    ${CONAN_OPTIONS}

echo "🔨 Building OpenSSL..."
# Build the package
conan build . \
    --profile "${PROFILE}" \
    ${CONAN_OPTIONS}

echo "📦 Creating package..."
# Create package
conan export-pkg . \
    --profile "${PROFILE}" \
    ${CONAN_OPTIONS}

echo "📤 Exporting artifacts..."
# Export package to artifacts directory
conan cache path "openssl/*" > /tmp/package_path.txt
PACKAGE_PATH=$(cat /tmp/package_path.txt)

if [[ -d "${PACKAGE_PATH}" ]]; then
    cp -r "${PACKAGE_PATH}"/* "${ARTIFACTS_DIR}/"
    echo "✅ Artifacts copied to ${ARTIFACTS_DIR}"
else
    echo "❌ Package path not found"
    exit 1
fi

# Create build info
echo "📝 Creating build info..."
PLATFORM="$(uname -s)-$(uname -m)"
cat > "${ARTIFACTS_DIR}/BUILD_INFO.json" << EOF
{
    "version": "${VERSION}",
    "platform": "${PLATFORM}",
    "profile": "${PROFILE}",
    "build_type": "${BUILD_TYPE}",
    "fips_enabled": ${ENABLE_FIPS},
    "build_date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "commit_sha": "$(git rev-parse HEAD)",
    "conan_version": "$(conan --version)",
    "build_successful": true
}
EOF

# Create checksums
echo "🔐 Creating checksums..."
cd "${ARTIFACTS_DIR}"
find . -type f -exec sha256sum {} \; > SHA256SUMS

# Create archive
echo "📦 Creating archive..."
cd "${PROJECT_ROOT}"
ARCHIVE_NAME="openssl-${VERSION}-${PLATFORM}.tar.gz"
tar czf "${ARCHIVE_NAME}" -C "${ARTIFACTS_DIR}" .

echo ""
echo "🎉 Build completed successfully!"
echo "📦 Archive: ${ARCHIVE_NAME}"
echo "📁 Size: $(du -h "${ARCHIVE_NAME}" | cut -f1)"
echo "📁 Location: ${PWD}/${ARCHIVE_NAME}"
echo ""

# Show basic info about the build
if [[ -f "${ARTIFACTS_DIR}/bin/openssl" ]]; then
    echo "🔍 OpenSSL version:"
    "${ARTIFACTS_DIR}/bin/openssl" version
elif [[ -f "${ARTIFACTS_DIR}/openssl.exe" ]]; then
    echo "🔍 OpenSSL version:"
    "${ARTIFACTS_DIR}/openssl.exe" version
else
    echo "ℹ️  OpenSSL binary location: Check ${ARTIFACTS_DIR}/"
fi