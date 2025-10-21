#!/bin/bash
set -euo pipefail

# Install OpenSSL Conan extensions to local Conan config
# Usage: ./install-extensions.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONAN_HOME="${CONAN_HOME:-$HOME/.conan2}"

echo "Installing OpenSSL Conan extensions..."

# Ensure Conan config directory exists
mkdir -p "$CONAN_HOME/extensions/commands"
mkdir -p "$CONAN_HOME/extensions/deployers"
mkdir -p "$CONAN_HOME/extensions/graph"

# Copy commands
echo "  → Installing custom commands..."
cp -r "$SCRIPT_DIR/extensions/commands/openssl" "$CONAN_HOME/extensions/commands/"
cp "$SCRIPT_DIR/extensions/commands/__init__.py" "$CONAN_HOME/extensions/commands/" 2>/dev/null || true

# Copy deployers
echo "  → Installing deployers..."
cp "$SCRIPT_DIR/extensions/deployers/full_deploy_enhanced.py" "$CONAN_HOME/extensions/deployers/"

# Copy graph utilities (used by commands)
echo "  → Installing graph utilities..."
cp "$SCRIPT_DIR/extensions/graph/analyzer.py" "$CONAN_HOME/extensions/graph/"

# Export python_requires
echo "  → Exporting python_requires..."
conan export . --name=openssl-tools --version=1.2.0

echo "✓ Extensions installed successfully!"
echo ""
echo "Available commands:"
echo "  - conan openssl:build [--fips] [--profile=PROFILE]"
echo "  - conan openssl:graph [--json]"
echo ""
echo "Available deployers:"
echo "  - full_deploy_enhanced"
echo ""
echo "Test with: conan openssl:build --help"
