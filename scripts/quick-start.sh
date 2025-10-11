#!/bin/bash
# scripts/quick-start.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "🚀 OpenSSL Tools Quick Start"
echo "============================"
echo ""

# Function to check if credentials are set
check_credentials() {
    if [[ -n "${ARTIFACTORY_URL:-}" && -n "${ARTIFACTORY_TOKEN:-}" ]]; then
        echo "✅ Credentials found in environment"
        return 0
    elif [[ -f "${PROJECT_ROOT}/.env" ]]; then
        echo "✅ Credentials found in .env file"
        source "${PROJECT_ROOT}/.env"
        return 0
    else
        echo "❌ No credentials found"
        return 1
    fi
}

# Function to setup credentials quickly
setup_credentials_quick() {
    echo "🔐 Quick credential setup..."
    echo ""
    
    read -p "Artifactory URL: " ARTIFACTORY_URL
    read -s -p "Artifactory Token: " ARTIFACTORY_TOKEN
    echo ""
    read -p "Artifactory Repo (default: openssl-releases): " ARTIFACTORY_REPO
    ARTIFACTORY_REPO="${ARTIFACTORY_REPO:-openssl-releases}"
    
    # Create .env file
    cat > "${PROJECT_ROOT}/.env" << EOF
ARTIFACTORY_URL=${ARTIFACTORY_URL}
ARTIFACTORY_TOKEN=${ARTIFACTORY_TOKEN}
ARTIFACTORY_REPO=${ARTIFACTORY_REPO}
DEFAULT_BUILD_PLATFORMS=ubuntu-22.04-clang,windows-2022
ENABLE_CONAN_UPLOAD=true
DEVELOPMENT_MODE=true
DOCKER_BUILDKIT=1
DOCKER_CLI_EXPERIMENTAL=enabled
EOF
    
    chmod 600 "${PROJECT_ROOT}/.env"
    echo "✅ Credentials saved to .env"
}

# Function to run super fast build
run_super_fast_build() {
    echo "⚡ Running super fast build..."
    echo ""
    
    # Load environment
    if [[ -f "${PROJECT_ROOT}/.env" ]]; then
        source "${PROJECT_ROOT}/.env"
    fi
    
    # Run super fast build
    "${PROJECT_ROOT}/scripts/super-fast-build.sh"
}

# Function to show help
show_help() {
    echo "OpenSSL Tools Quick Start"
    echo ""
    echo "Usage: $0 {build|setup|help}"
    echo ""
    echo "Commands:"
    echo "  build  - Run super fast build (requires credentials)"
    echo "  setup  - Quick credential setup"
    echo "  help   - Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 setup  # Setup credentials first"
    echo "  $0 build  # Build and upload all platforms"
    echo ""
    echo "Environment variables:"
    echo "  ARTIFACTORY_URL     - Your Artifactory URL"
    echo "  ARTIFACTORY_TOKEN   - Your Artifactory token"
    echo "  ARTIFACTORY_REPO    - Repository name (default: openssl-releases)"
}

# Main execution
case "${1:-build}" in
    "build")
        if check_credentials; then
            run_super_fast_build
        else
            echo "❌ No credentials found"
            echo ""
            echo "Quick setup:"
            echo "1. Run: $0 setup"
            echo "2. Or set environment variables:"
            echo "   export ARTIFACTORY_URL=your-url"
            echo "   export ARTIFACTORY_TOKEN=your-token"
            echo "3. Then run: $0 build"
            exit 1
        fi
        ;;
    "setup")
        setup_credentials_quick
        echo ""
        echo "✅ Setup complete! Now run: $0 build"
        ;;
    "help"|*)
        show_help
        ;;
esac