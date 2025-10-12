#!/bin/bash
# scripts/setup-openssl-source.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "📥 Setting up OpenSSL source code for building"

# Check if OpenSSL source already exists
if [[ -d "${PROJECT_ROOT}/openssl-source" ]]; then
    echo "✅ OpenSSL source already exists"
    exit 0
fi

# Create openssl-source directory
mkdir -p "${PROJECT_ROOT}/openssl-source"
cd "${PROJECT_ROOT}/openssl-source"

echo "📥 Cloning OpenSSL source code..."

# Clone OpenSSL (use a specific stable version)
git clone --depth 1 --branch OpenSSL_1_1_1-stable https://github.com/openssl/openssl.git .

echo "✅ OpenSSL source code cloned"

# Create symlink for Docker builds
cd "${PROJECT_ROOT}"
if [[ ! -L "openssl" ]]; then
    ln -s openssl-source openssl
    echo "✅ Created symlink: openssl -> openssl-source"
fi

echo "🎉 OpenSSL source setup complete!"
echo "📁 Source location: ${PROJECT_ROOT}/openssl-source"
echo "🔗 Symlink: ${PROJECT_ROOT}/openssl"