#!/bin/bash
# scripts/simple-build.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
ARTIFACTS_DIR="${PROJECT_ROOT}/artifacts"

echo "🔨 Simple OpenSSL Build"
echo "======================="

# Configuration
VERSION="${VERSION:-$(date +%Y%m%d)-$(git rev-parse --short HEAD)}"
BUILD_DIR="${PROJECT_ROOT}/build"
OPENSSL_SOURCE="${PROJECT_ROOT}/openssl"

# Clean and prepare
rm -rf "${ARTIFACTS_DIR}" "${BUILD_DIR}"
mkdir -p "${ARTIFACTS_DIR}" "${BUILD_DIR}"

echo "📦 Version: ${VERSION}"
echo "📁 Source: ${OPENSSL_SOURCE}"
echo "📁 Build: ${BUILD_DIR}"
echo "📁 Artifacts: ${ARTIFACTS_DIR}"
echo ""

# Check if OpenSSL source exists
if [[ ! -d "${OPENSSL_SOURCE}" ]]; then
    echo "❌ OpenSSL source not found at ${OPENSSL_SOURCE}"
    echo "Run: ./scripts/setup-openssl-source.sh"
    exit 1
fi

# Build OpenSSL for current platform
echo "🔨 Building OpenSSL for current platform..."

cd "${BUILD_DIR}"

# Configure OpenSSL
echo "⚙️  Configuring OpenSSL..."
"${OPENSSL_SOURCE}/config" \
    --prefix="${ARTIFACTS_DIR}/openssl" \
    --openssldir="${ARTIFACTS_DIR}/openssl/ssl" \
    shared zlib

# Build OpenSSL
echo "🔨 Building OpenSSL..."
make -j$(nproc)

# Test OpenSSL
echo "🧪 Testing OpenSSL..."
make test

# Install OpenSSL
echo "📦 Installing OpenSSL..."
make install

# Create build info
echo "📝 Creating build info..."
cat > "${ARTIFACTS_DIR}/BUILD_INFO.json" << EOF
{
    "version": "${VERSION}",
    "platform": "$(uname -s)-$(uname -m)",
    "build_date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "commit_sha": "$(git rev-parse HEAD)",
    "build_successful": true,
    "openssl_version": "$(./openssl version)"
}
EOF

# Create checksums
echo "🔐 Creating checksums..."
cd "${ARTIFACTS_DIR}"
find . -type f -exec sha256sum {} \; > SHA256SUMS

# Create archive
echo "📦 Creating archive..."
cd "${PROJECT_ROOT}"
tar czf "openssl-${VERSION}-$(uname -s)-$(uname -m).tar.gz" -C "${ARTIFACTS_DIR}" .

echo ""
echo "🎉 Build completed successfully!"
echo "📦 Artifact: openssl-${VERSION}-$(uname -s)-$(uname -m).tar.gz"
echo "📁 Size: $(du -h "openssl-${VERSION}-$(uname -s)-$(uname -m).tar.gz" | cut -f1)"
echo ""

# Show OpenSSL version
echo "🔍 OpenSSL version:"
"${ARTIFACTS_DIR}/openssl/bin/openssl" version