#!/bin/bash
# scripts/dev-setup.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "🚀 Setting up OpenSSL Tools development environment"

# Function to check prerequisites
check_prerequisites() {
    echo "🔍 Checking prerequisites..."
    
    local missing_deps=()
    
    # Check for required commands
    for cmd in docker git python3 pip3 curl; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
            missing_deps+=("$cmd")
        fi
    done
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        echo "❌ Missing required dependencies: ${missing_deps[*]}"
        echo "Please install the missing dependencies and try again"
        exit 1
    fi
    
    echo "✅ All prerequisites found"
}

# Function to setup Docker
setup_docker() {
    echo "🐳 Setting up Docker..."
    
    # Check if Docker is running
    if ! docker info >/dev/null 2>&1; then
        echo "❌ Docker is not running. Please start Docker and try again"
        exit 1
    fi
    
    # Test Docker build
    echo "Testing Docker build capability..."
    docker run --rm hello-world >/dev/null 2>&1 || {
        echo "❌ Docker test failed"
        exit 1
    }
    
    echo "✅ Docker setup complete"
}

# Function to setup Conan
setup_conan() {
    echo "📦 Setting up Conan..."
    
    # Install Conan if not present
    if ! command -v conan >/dev/null 2>&1; then
        echo "Installing Conan..."
        pip3 install conan==2.0.*
    fi
    
    # Detect and create profiles
    conan profile detect --force
    
    # Copy custom profiles
    if [[ -d "${PROJECT_ROOT}/profiles/conan" ]]; then
        echo "Installing custom Conan profiles..."
        for profile in "${PROJECT_ROOT}/profiles/conan"/*.profile; do
            if [[ -f "$profile" ]]; then
                profile_name=$(basename "$profile" .profile)
                cp "$profile" ~/.conan2/profiles/
                echo "✅ Installed profile: $profile_name"
            fi
        done
    fi
    
    echo "✅ Conan setup complete"
}

# Function to setup environment variables
setup_environment() {
    echo "🔧 Setting up environment variables..."
    
    # Create .env file if it doesn't exist
    if [[ ! -f "${PROJECT_ROOT}/.env" ]]; then
        if [[ -f "${PROJECT_ROOT}/.env.template" ]]; then
            cp "${PROJECT_ROOT}/.env.template" "${PROJECT_ROOT}/.env"
            echo "✅ Created .env file from template"
            echo "⚠️  Please edit .env file with your actual values"
        else
            cat > "${PROJECT_ROOT}/.env" << 'EOF'
# Artifactory Configuration
ARTIFACTORY_URL=https://your-artifactory.com
ARTIFACTORY_TOKEN=your-token-here
ARTIFACTORY_REPO=openssl-releases

# Build Configuration
DEFAULT_BUILD_PLATFORMS=ubuntu-22.04-clang,windows-2022
ENABLE_CONAN_UPLOAD=true
ENABLE_GITHUB_PACKAGES=false

# Development Configuration
DEVELOPMENT_MODE=true
VERBOSE_LOGGING=false
EOF
            echo "✅ Created .env file with defaults"
        fi
    fi
    
    # Source environment variables
    set -a
    source "${PROJECT_ROOT}/.env"
    set +a
    
    echo "✅ Environment setup complete"
}

# Function to validate setup
validate_setup() {
    echo "🔍 Validating setup..."
    
    # Test Docker Compose
    cd "${PROJECT_ROOT}/docker"
    if docker-compose config >/dev/null 2>&1; then
        echo "✅ Docker Compose configuration valid"
    else
        echo "❌ Docker Compose configuration invalid"
        return 1
    fi
    
    # Test Conan
    if conan profile list >/dev/null 2>&1; then
        echo "✅ Conan profiles configured"
    else
        echo "❌ Conan profiles not configured"
        return 1
    fi
    
    # Test Python scripts
    if python3 -c "import json, hashlib, os, sys" >/dev/null 2>&1; then
        echo "✅ Python dependencies available"
    else
        echo "❌ Python dependencies missing"
        return 1
    fi
    
    # Test script permissions
    local scripts=("docker-build-and-upload.sh" "cursor-agents-coordinator.sh" "validate-artifactory-packages.sh")
    for script in "${scripts[@]}"; do
        if [[ -x "${PROJECT_ROOT}/scripts/${script}" ]]; then
            echo "✅ Script executable: $script"
        else
            echo "❌ Script not executable: $script"
            chmod +x "${PROJECT_ROOT}/scripts/${script}"
            echo "✅ Fixed permissions for: $script"
        fi
    done
    
    echo "✅ Setup validation complete"
}

# Function to run quick test
run_quick_test() {
    echo "🧪 Running quick test..."
    
    # Test Docker build (dry run)
    cd "${PROJECT_ROOT}/docker"
    echo "Testing Docker build configuration..."
    if docker-compose config >/dev/null 2>&1; then
        echo "✅ Docker Compose configuration test passed"
    else
        echo "❌ Docker Compose configuration test failed"
        return 1
    fi
    
    # Test Conan profile
    echo "Testing Conan profile..."
    if conan profile show default >/dev/null 2>&1; then
        echo "✅ Conan profile test passed"
    else
        echo "❌ Conan profile test failed"
        return 1
    fi
    
    echo "✅ Quick test completed successfully"
}

# Function to display next steps
display_next_steps() {
    echo ""
    echo "🎉 OpenSSL Tools development environment setup complete!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Edit .env file with your Artifactory credentials"
    echo "2. Test the setup: ./scripts/dev-setup.sh test"
    echo "3. Start Cursor Agents: ./scripts/cursor-agents-coordinator.sh start"
    echo "4. Run a build: ./scripts/docker-build-and-upload.sh"
    echo ""
    echo "📚 Available commands:"
    echo "  ./scripts/docker-build-and-upload.sh     - Build and upload artifacts"
    echo "  ./scripts/cursor-agents-coordinator.sh   - Manage Cursor Agents"
    echo "  ./scripts/validate-artifactory-packages.sh - Validate uploaded packages"
    echo ""
    echo "🐳 Docker commands:"
    echo "  cd docker && docker-compose build        - Build all platforms"
    echo "  cd docker && docker-compose up ubuntu-22-04-clang - Build specific platform"
    echo ""
    echo "📦 Conan commands:"
    echo "  conan profile list                       - List available profiles"
    echo "  conan profile show default               - Show default profile"
    echo ""
}

# Main execution
main() {
    case "${1:-setup}" in
        "setup")
            check_prerequisites
            setup_docker
            setup_conan
            setup_environment
            validate_setup
            run_quick_test
            display_next_steps
            ;;
        "test")
            validate_setup
            run_quick_test
            echo "✅ All tests passed!"
            ;;
        "reset")
            echo "🔄 Resetting development environment..."
            rm -rf "${PROJECT_ROOT}/artifacts"
            rm -rf "${PROJECT_ROOT}/logs"
            docker system prune -f
            echo "✅ Environment reset complete"
            ;;
        *)
            echo "Usage: $0 {setup|test|reset}"
            echo "  setup - Complete development environment setup"
            echo "  test  - Validate current setup"
            echo "  reset - Reset environment (clean artifacts and logs)"
            exit 1
            ;;
    esac
}

# Execute main function
main "$@"