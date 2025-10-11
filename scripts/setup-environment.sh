#!/bin/bash
# scripts/setup-environment.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "🌍 Setting up OpenSSL Tools environment"

# Function to detect shell
detect_shell() {
    local shell_name=$(basename "$SHELL")
    case "$shell_name" in
        "bash")
            echo "bash"
            ;;
        "zsh")
            echo "zsh"
            ;;
        "fish")
            echo "fish"
            ;;
        *)
            echo "bash"  # Default to bash
            ;;
    esac
}

# Function to get shell config file
get_shell_config() {
    local shell_type="$1"
    case "$shell_type" in
        "bash")
            echo "${HOME}/.bashrc"
            ;;
        "zsh")
            echo "${HOME}/.zshrc"
            ;;
        "fish")
            echo "${HOME}/.config/fish/config.fish"
            ;;
        *)
            echo "${HOME}/.bashrc"
            ;;
    esac
}

# Function to create environment loader
create_environment_loader() {
    echo "📝 Creating environment loader..."
    
    cat > "${PROJECT_ROOT}/scripts/load-environment.sh" << 'EOF'
#!/bin/bash
# scripts/load-environment.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Function to load environment
load_environment() {
    # Load .env file if it exists
    if [[ -f "${PROJECT_ROOT}/.env" ]]; then
        set -a
        source "${PROJECT_ROOT}/.env"
        set +a
        echo "✅ Loaded environment from .env"
    else
        echo "⚠️  No .env file found at ${PROJECT_ROOT}/.env"
    fi
    
    # Set OpenSSL Tools specific variables
    export OPENSSL_TOOLS_ROOT="${PROJECT_ROOT}"
    export OPENSSL_TOOLS_SCRIPTS="${PROJECT_ROOT}/scripts"
    export OPENSSL_TOOLS_PROFILES="${PROJECT_ROOT}/profiles"
    export OPENSSL_TOOLS_DOCKER="${PROJECT_ROOT}/docker"
    export OPENSSL_TOOLS_ARTIFACTS="${PROJECT_ROOT}/artifacts"
    export OPENSSL_TOOLS_LOGS="${PROJECT_ROOT}/logs"
    
    # Add scripts to PATH
    export PATH="${OPENSSL_TOOLS_SCRIPTS}:${PATH}"
    
    # Set Docker environment
    export DOCKER_BUILDKIT=1
    export DOCKER_CLI_EXPERIMENTAL=enabled
    
    # Set Conan environment
    export CONAN_USER_HOME="${HOME}/.conan2"
    export CONAN_DEFAULT_PROFILE_PATH="${OPENSSL_TOOLS_PROFILES}/conan/ubuntu-22.04.profile"
    
    # Set build environment
    export DEFAULT_BUILD_PLATFORMS="${DEFAULT_BUILD_PLATFORMS:-ubuntu-22.04-clang,windows-2022}"
    export ENABLE_CONAN_UPLOAD="${ENABLE_CONAN_UPLOAD:-true}"
    export DEVELOPMENT_MODE="${DEVELOPMENT_MODE:-true}"
    export VERBOSE_LOGGING="${VERBOSE_LOGGING:-false}"
    
    # Set Cursor Agents environment
    export CURSOR_AGENTS_ENABLED="${CURSOR_AGENTS_ENABLED:-true}"
    export CORE_AGENT_REPO="${CORE_AGENT_REPO:-../openssl}"
    export TOOLS_AGENT_REPO="${TOOLS_AGENT_REPO:-.}"
    
    echo "✅ OpenSSL Tools environment loaded"
}

# Function to show environment status
show_environment_status() {
    echo "📊 OpenSSL Tools Environment Status"
    echo "==================================="
    echo "Root Directory: ${OPENSSL_TOOLS_ROOT:-[NOT SET]}"
    echo "Scripts Directory: ${OPENSSL_TOOLS_SCRIPTS:-[NOT SET]}"
    echo "Profiles Directory: ${OPENSSL_TOOLS_PROFILES:-[NOT SET]}"
    echo "Docker Directory: ${OPENSSL_TOOLS_DOCKER:-[NOT SET]}"
    echo "Artifacts Directory: ${OPENSSL_TOOLS_ARTIFACTS:-[NOT SET]}"
    echo "Logs Directory: ${OPENSSL_TOOLS_LOGS:-[NOT SET]}"
    echo ""
    echo "Artifactory URL: ${ARTIFACTORY_URL:-[NOT SET]}"
    echo "Artifactory Repo: ${ARTIFACTORY_REPO:-[NOT SET]}"
    echo "Artifactory Token: ${ARTIFACTORY_TOKEN:+[SET]}${ARTIFACTORY_TOKEN:-[NOT SET]}"
    echo ""
    echo "Conan Remote: ${CONAN_REMOTE_NAME:-[NOT SET]}"
    echo "Conan Remote URL: ${CONAN_REMOTE_URL:-[NOT SET]}"
    echo ""
    echo "Build Platforms: ${DEFAULT_BUILD_PLATFORMS:-[NOT SET]}"
    echo "Conan Upload: ${ENABLE_CONAN_UPLOAD:-[NOT SET]}"
    echo "Development Mode: ${DEVELOPMENT_MODE:-[NOT SET]}"
}

# Function to validate environment
validate_environment() {
    local errors=0
    
    # Check required directories
    local required_dirs=(
        "${OPENSSL_TOOLS_ROOT}"
        "${OPENSSL_TOOLS_SCRIPTS}"
        "${OPENSSL_TOOLS_PROFILES}"
        "${OPENSSL_TOOLS_DOCKER}"
    )
    
    for dir in "${required_dirs[@]}"; do
        if [[ -d "$dir" ]]; then
            echo "✅ Directory exists: $dir"
        else
            echo "❌ Directory missing: $dir"
            errors=$((errors + 1))
        fi
    done
    
    # Check required environment variables
    local required_vars=(
        "ARTIFACTORY_URL"
        "ARTIFACTORY_TOKEN"
        "ARTIFACTORY_REPO"
    )
    
    for var in "${required_vars[@]}"; do
        if [[ -n "${!var:-}" ]]; then
            echo "✅ Variable set: $var"
        else
            echo "❌ Variable missing: $var"
            errors=$((errors + 1))
        fi
    done
    
    # Check script permissions
    local scripts=(
        "docker-build-and-upload.sh"
        "cursor-agents-coordinator.sh"
        "validate-artifactory-packages.sh"
        "generate_sbom.py"
        "dev-setup.sh"
    )
    
    for script in "${scripts[@]}"; do
        if [[ -x "${OPENSSL_TOOLS_SCRIPTS}/${script}" ]]; then
            echo "✅ Script executable: $script"
        else
            echo "❌ Script not executable: $script"
            errors=$((errors + 1))
        fi
    done
    
    if [[ $errors -eq 0 ]]; then
        echo "🎉 Environment validation passed!"
        return 0
    else
        echo "💥 Environment validation failed with $errors errors"
        return 1
    fi
}

# Main execution
case "${1:-load}" in
    "load")
        load_environment
        ;;
    "status")
        load_environment
        show_environment_status
        ;;
    "validate")
        load_environment
        validate_environment
        ;;
    "help")
        echo "OpenSSL Tools Environment Loader"
        echo ""
        echo "Usage: $0 {load|status|validate|help}"
        echo ""
        echo "Commands:"
        echo "  load     - Load environment variables (default)"
        echo "  status   - Show environment status"
        echo "  validate - Validate environment setup"
        echo "  help     - Show this help"
        ;;
    *)
        echo "Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac
EOF
    
    chmod +x "${PROJECT_ROOT}/scripts/load-environment.sh"
    echo "✅ Environment loader created"
}

# Function to update shell configuration
update_shell_config() {
    local shell_type="$1"
    local config_file="$2"
    
    echo "📝 Updating $shell_type configuration..."
    
    # Create backup
    if [[ -f "$config_file" ]]; then
        cp "$config_file" "${config_file}.backup.$(date +%Y%m%d_%H%M%S)"
        echo "✅ Created backup: ${config_file}.backup.$(date +%Y%m%d_%H%M%S)"
    fi
    
    # Create OpenSSL Tools section
    local openssl_section=""
    case "$shell_type" in
        "bash")
            openssl_section="
# OpenSSL Tools Environment Setup
# Auto-generated by openssl-tools setup-environment.sh
if [[ -f \"${PROJECT_ROOT}/scripts/load-environment.sh\" ]]; then
    source \"${PROJECT_ROOT}/scripts/load-environment.sh\" load
fi
"
            ;;
        "zsh")
            openssl_section="
# OpenSSL Tools Environment Setup
# Auto-generated by openssl-tools setup-environment.sh
if [[ -f \"${PROJECT_ROOT}/scripts/load-environment.sh\" ]]; then
    source \"${PROJECT_ROOT}/scripts/load-environment.sh\" load
fi
"
            ;;
        "fish")
            openssl_section="
# OpenSSL Tools Environment Setup
# Auto-generated by openssl-tools setup-environment.sh
if test -f \"${PROJECT_ROOT}/scripts/load-environment.sh\"
    source \"${PROJECT_ROOT}/scripts/load-environment.sh\" load
end
"
            ;;
    esac
    
    # Check if section already exists
    if grep -q "OpenSSL Tools Environment Setup" "$config_file" 2>/dev/null; then
        echo "⚠️  OpenSSL Tools section already exists in $config_file"
        echo "   Skipping $config_file update"
    else
        echo "$openssl_section" >> "$config_file"
        echo "✅ $config_file updated with OpenSSL Tools environment"
    fi
}

# Function to create systemd user environment
create_systemd_environment() {
    echo "🔧 Creating systemd user environment..."
    
    local systemd_dir="${HOME}/.config/systemd/user"
    mkdir -p "$systemd_dir"
    
    cat > "${systemd_dir}/openssl-tools-environment.service" << EOF
[Unit]
Description=OpenSSL Tools Environment
After=graphical-session.target

[Service]
Type=oneshot
EnvironmentFile=${PROJECT_ROOT}/.env
ExecStart=${PROJECT_ROOT}/scripts/load-environment.sh load
RemainAfterExit=yes

[Install]
WantedBy=default.target
EOF
    
    echo "✅ Systemd user environment created"
}

# Function to create environment test
create_environment_test() {
    echo "🧪 Creating environment test..."
    
    cat > "${PROJECT_ROOT}/scripts/test-environment.sh" << 'EOF'
#!/bin/bash
# scripts/test-environment.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "🧪 Testing OpenSSL Tools environment setup"

# Test 1: Load environment
echo "1️⃣ Testing environment loading..."
if source "${PROJECT_ROOT}/scripts/load-environment.sh" load; then
    echo "✅ Environment loaded successfully"
else
    echo "❌ Environment loading failed"
    exit 1
fi

# Test 2: Validate environment
echo ""
echo "2️⃣ Testing environment validation..."
if source "${PROJECT_ROOT}/scripts/load-environment.sh" validate; then
    echo "✅ Environment validation passed"
else
    echo "❌ Environment validation failed"
    exit 1
fi

# Test 3: Check shell integration
echo ""
echo "3️⃣ Testing shell integration..."
if [[ -n "${OPENSSL_TOOLS_ROOT:-}" ]]; then
    echo "✅ Shell integration working"
else
    echo "❌ Shell integration not working"
    exit 1
fi

# Test 4: Check PATH
echo ""
echo "4️⃣ Testing PATH setup..."
if command -v docker-build-and-upload.sh >/dev/null 2>&1; then
    echo "✅ Scripts in PATH"
else
    echo "❌ Scripts not in PATH"
    exit 1
fi

# Test 5: Check Docker
echo ""
echo "5️⃣ Testing Docker environment..."
if docker info >/dev/null 2>&1; then
    echo "✅ Docker accessible"
else
    echo "❌ Docker not accessible"
    exit 1
fi

# Test 6: Check Conan
echo ""
echo "6️⃣ Testing Conan environment..."
if command -v conan >/dev/null 2>&1; then
    echo "✅ Conan available"
    if conan profile list >/dev/null 2>&1; then
        echo "✅ Conan profiles configured"
    else
        echo "⚠️  Conan profiles not configured"
    fi
else
    echo "⚠️  Conan not available"
fi

echo ""
echo "🎉 All environment tests passed!"
EOF
    
    chmod +x "${PROJECT_ROOT}/scripts/test-environment.sh"
    echo "✅ Environment test created"
}

# Function to create environment manager
create_environment_manager() {
    echo "🔧 Creating environment manager..."
    
    cat > "${PROJECT_ROOT}/scripts/manage-environment.sh" << 'EOF'
#!/bin/bash
# scripts/manage-environment.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

show_help() {
    echo "OpenSSL Tools Environment Manager"
    echo ""
    echo "Usage: $0 {load|status|validate|test|reload|reset|help}"
    echo ""
    echo "Commands:"
    echo "  load     - Load environment variables"
    echo "  status   - Show environment status"
    echo "  validate - Validate environment setup"
    echo "  test     - Run environment tests"
    echo "  reload   - Reload shell configuration"
    echo "  reset    - Reset environment configuration"
    echo "  help     - Show this help"
    echo ""
}

load_environment() {
    source "${PROJECT_ROOT}/scripts/load-environment.sh" load
}

show_status() {
    source "${PROJECT_ROOT}/scripts/load-environment.sh" status
}

validate_environment() {
    source "${PROJECT_ROOT}/scripts/load-environment.sh" validate
}

test_environment() {
    "${PROJECT_ROOT}/scripts/test-environment.sh"
}

reload_shell() {
    echo "🔄 Reloading shell configuration..."
    
    local shell_name=$(basename "$SHELL")
    case "$shell_name" in
        "bash")
            source ~/.bashrc
            ;;
        "zsh")
            source ~/.zshrc
            ;;
        "fish")
            source ~/.config/fish/config.fish
            ;;
        *)
            echo "⚠️  Unknown shell: $shell_name"
            ;;
    esac
    
    echo "✅ Shell configuration reloaded"
}

reset_environment() {
    echo "⚠️  This will reset all environment configuration"
    read -p "Are you sure? (y/N): " confirm
    if [[ "$confirm" =~ ^[Yy]$ ]]; then
        # Remove from shell configs
        for config in ~/.bashrc ~/.zshrc ~/.config/fish/config.fish; do
            if [[ -f "$config" ]]; then
                sed -i '/OpenSSL Tools Environment Setup/,/^$/d' "$config" 2>/dev/null || true
            fi
        done
        
        # Remove systemd service
        rm -f ~/.config/systemd/user/openssl-tools-environment.service
        
        echo "✅ Environment configuration reset"
    else
        echo "❌ Reset cancelled"
    fi
}

# Main execution
case "${1:-help}" in
    "load")
        load_environment
        ;;
    "status")
        show_status
        ;;
    "validate")
        validate_environment
        ;;
    "test")
        test_environment
        ;;
    "reload")
        reload_shell
        ;;
    "reset")
        reset_environment
        ;;
    "help"|*)
        show_help
        ;;
esac
EOF
    
    chmod +x "${PROJECT_ROOT}/scripts/manage-environment.sh"
    echo "✅ Environment manager created"
}

# Main execution
main() {
    echo "🌍 OpenSSL Tools Environment Setup"
    echo "=================================="
    echo ""
    
    # Detect shell
    local shell_type=$(detect_shell)
    local config_file=$(get_shell_config "$shell_type")
    
    echo "🔍 Detected shell: $shell_type"
    echo "📁 Config file: $config_file"
    echo ""
    
    # Create environment loader
    create_environment_loader
    
    # Update shell configuration
    update_shell_config "$shell_type" "$config_file"
    
    # Create systemd user environment (if systemd is available)
    if systemctl --user >/dev/null 2>&1; then
        create_systemd_environment
    else
        echo "⚠️  Systemd not available, skipping user service creation"
    fi
    
    # Create environment test
    create_environment_test
    
    # Create environment manager
    create_environment_manager
    
    echo ""
    echo "🎉 Environment setup complete!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Reload your shell: source $config_file"
    echo "2. Test environment: ./scripts/test-environment.sh"
    echo "3. Manage environment: ./scripts/manage-environment.sh help"
    echo ""
    echo "🔧 Environment management:"
    echo "  ./scripts/manage-environment.sh load     - Load environment"
    echo "  ./scripts/manage-environment.sh status   - Show status"
    echo "  ./scripts/manage-environment.sh validate - Validate setup"
    echo "  ./scripts/manage-environment.sh test     - Run tests"
    echo "  ./scripts/manage-environment.sh reload   - Reload shell"
}

# Execute main function
main "$@"