#!/bin/bash
# scripts/setup-credentials.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "🔐 Setting up OpenSSL Tools credentials"

# Function to check if running interactively
is_interactive() {
    [[ -t 0 && -t 1 ]]
}

# Function to prompt for credentials
prompt_credentials() {
    echo "📝 Please provide your Artifactory credentials:"
    echo ""
    
    # Artifactory URL
    read -p "Artifactory URL (e.g., https://your-company.jfrog.io): " ARTIFACTORY_URL
    while [[ -z "$ARTIFACTORY_URL" ]]; do
        echo "❌ Artifactory URL is required"
        read -p "Artifactory URL: " ARTIFACTORY_URL
    done
    
    # Artifactory Token
    read -s -p "Artifactory Token/Password: " ARTIFACTORY_TOKEN
    echo ""
    while [[ -z "$ARTIFACTORY_TOKEN" ]]; do
        echo "❌ Artifactory Token is required"
        read -s -p "Artifactory Token: " ARTIFACTORY_TOKEN
        echo ""
    done
    
    # Artifactory Repository
    read -p "Artifactory Repository (default: openssl-releases): " ARTIFACTORY_REPO
    ARTIFACTORY_REPO="${ARTIFACTORY_REPO:-openssl-releases}"
    
    # GitHub Token (optional)
    read -p "GitHub Token (optional, for GitHub Packages): " GITHUB_TOKEN
    
    # Docker Hub credentials (optional)
    read -p "Docker Hub Username (optional): " DOCKER_HUB_USERNAME
    if [[ -n "$DOCKER_HUB_USERNAME" ]]; then
        read -s -p "Docker Hub Password: " DOCKER_HUB_PASSWORD
        echo ""
    fi
    
    # Conan credentials (optional)
    read -p "Conan Remote Name (default: artifactory): " CONAN_REMOTE_NAME
    CONAN_REMOTE_NAME="${CONAN_REMOTE_NAME:-artifactory}"
    
    read -p "Conan Remote URL (default: auto-detected): " CONAN_REMOTE_URL
    if [[ -z "$CONAN_REMOTE_URL" ]]; then
        CONAN_REMOTE_URL="${ARTIFACTORY_URL}/artifactory/api/conan/conan"
    fi
}

# Function to load existing credentials from environment
load_existing_credentials() {
    echo "📋 Loading existing credentials from environment..."
    
    ARTIFACTORY_URL="${ARTIFACTORY_URL:-}"
    ARTIFACTORY_TOKEN="${ARTIFACTORY_TOKEN:-}"
    ARTIFACTORY_REPO="${ARTIFACTORY_REPO:-openssl-releases}"
    GITHUB_TOKEN="${GITHUB_TOKEN:-}"
    DOCKER_HUB_USERNAME="${DOCKER_HUB_USERNAME:-}"
    DOCKER_HUB_PASSWORD="${DOCKER_HUB_PASSWORD:-}"
    CONAN_REMOTE_NAME="${CONAN_REMOTE_NAME:-artifactory}"
    CONAN_REMOTE_URL="${CONAN_REMOTE_URL:-}"
}

# Function to validate credentials
validate_credentials() {
    echo "🔍 Validating credentials..."
    
    local errors=0
    
    # Validate Artifactory URL
    if [[ -z "$ARTIFACTORY_URL" ]]; then
        echo "❌ ARTIFACTORY_URL is not set"
        errors=$((errors + 1))
    elif [[ ! "$ARTIFACTORY_URL" =~ ^https?:// ]]; then
        echo "❌ ARTIFACTORY_URL must start with http:// or https://"
        errors=$((errors + 1))
    else
        echo "✅ ARTIFACTORY_URL: $ARTIFACTORY_URL"
    fi
    
    # Validate Artifactory Token
    if [[ -z "$ARTIFACTORY_TOKEN" ]]; then
        echo "❌ ARTIFACTORY_TOKEN is not set"
        errors=$((errors + 1))
    else
        echo "✅ ARTIFACTORY_TOKEN: [HIDDEN]"
    fi
    
    # Validate Artifactory Repository
    if [[ -z "$ARTIFACTORY_REPO" ]]; then
        echo "❌ ARTIFACTORY_REPO is not set"
        errors=$((errors + 1))
    else
        echo "✅ ARTIFACTORY_REPO: $ARTIFACTORY_REPO"
    fi
    
    # Optional validations
    if [[ -n "$GITHUB_TOKEN" ]]; then
        echo "✅ GITHUB_TOKEN: [HIDDEN]"
    fi
    
    if [[ -n "$DOCKER_HUB_USERNAME" ]]; then
        echo "✅ DOCKER_HUB_USERNAME: $DOCKER_HUB_USERNAME"
        if [[ -z "$DOCKER_HUB_PASSWORD" ]]; then
            echo "⚠️  DOCKER_HUB_PASSWORD is not set (Docker Hub uploads will fail)"
        else
            echo "✅ DOCKER_HUB_PASSWORD: [HIDDEN]"
        fi
    fi
    
    if [[ $errors -gt 0 ]]; then
        echo "❌ $errors validation errors found"
        return 1
    fi
    
    echo "✅ All required credentials are valid"
    return 0
}

# Function to test Artifactory connection
test_artifactory_connection() {
    echo "🌐 Testing Artifactory connection..."
    
    local test_url="${ARTIFACTORY_URL}/artifactory/api/system/ping"
    
    if curl -s -f -H "Authorization: Bearer ${ARTIFACTORY_TOKEN}" "$test_url" >/dev/null 2>&1; then
        echo "✅ Artifactory connection successful"
        return 0
    else
        echo "❌ Artifactory connection failed"
        echo "   URL: $test_url"
        echo "   Please check your credentials and network connection"
        return 1
    fi
}

# Function to create .env file
create_env_file() {
    echo "📝 Creating .env file..."
    
    cat > "${PROJECT_ROOT}/.env" << EOF
# OpenSSL Tools Environment Configuration
# Generated on $(date)

# Artifactory Configuration
ARTIFACTORY_URL=${ARTIFACTORY_URL}
ARTIFACTORY_TOKEN=${ARTIFACTORY_TOKEN}
ARTIFACTORY_REPO=${ARTIFACTORY_REPO}

# GitHub Configuration (optional)
GITHUB_TOKEN=${GITHUB_TOKEN:-}

# Docker Hub Configuration (optional)
DOCKER_HUB_USERNAME=${DOCKER_HUB_USERNAME:-}
DOCKER_HUB_PASSWORD=${DOCKER_HUB_PASSWORD:-}

# Conan Configuration
CONAN_REMOTE_NAME=${CONAN_REMOTE_NAME}
CONAN_REMOTE_URL=${CONAN_REMOTE_URL}

# Build Configuration
DEFAULT_BUILD_PLATFORMS=ubuntu-22.04-clang,windows-2022
ENABLE_CONAN_UPLOAD=true
ENABLE_GITHUB_PACKAGES=false

# Development Configuration
DEVELOPMENT_MODE=true
VERBOSE_LOGGING=false

# Cursor Agents Configuration
CURSOR_AGENTS_ENABLED=true
CORE_AGENT_REPO=../openssl
TOOLS_AGENT_REPO=.

# Docker Configuration
DOCKER_BUILDKIT=1
DOCKER_CLI_EXPERIMENTAL=enabled

# Conan Configuration
CONAN_USER_HOME=~/.conan2
CONAN_DEFAULT_PROFILE_PATH=profiles/conan/ubuntu-22.04.profile
EOF
    
    # Set secure permissions
    chmod 600 "${PROJECT_ROOT}/.env"
    echo "✅ .env file created with secure permissions"
}

# Function to update ~/.bashrc
update_bashrc() {
    echo "📝 Updating ~/.bashrc..."
    
    local bashrc_file="${HOME}/.bashrc"
    local openssl_tools_section="
# OpenSSL Tools Environment Variables
# Auto-generated by openssl-tools setup-credentials.sh
export OPENSSL_TOOLS_ROOT=\"${PROJECT_ROOT}\"
export ARTIFACTORY_URL=\"${ARTIFACTORY_URL}\"
export ARTIFACTORY_REPO=\"${ARTIFACTORY_REPO}\"
export CONAN_REMOTE_NAME=\"${CONAN_REMOTE_NAME}\"
export CONAN_REMOTE_URL=\"${CONAN_REMOTE_URL}\"
export DEFAULT_BUILD_PLATFORMS=\"ubuntu-22.04-clang,windows-2022\"
export ENABLE_CONAN_UPLOAD=\"true\"
export DEVELOPMENT_MODE=\"true\"
export DOCKER_BUILDKIT=\"1\"
export DOCKER_CLI_EXPERIMENTAL=\"enabled\"

# OpenSSL Tools PATH additions
export PATH=\"\${OPENSSL_TOOLS_ROOT}/scripts:\$PATH\"

# Source .env file if it exists
if [[ -f \"\${OPENSSL_TOOLS_ROOT}/.env\" ]]; then
    set -a
    source \"\${OPENSSL_TOOLS_ROOT}/.env\"
    set +a
fi
"
    
    # Check if section already exists
    if grep -q "OpenSSL Tools Environment Variables" "$bashrc_file" 2>/dev/null; then
        echo "⚠️  OpenSSL Tools section already exists in ~/.bashrc"
        echo "   Skipping ~/.bashrc update"
    else
        echo "$openssl_tools_section" >> "$bashrc_file"
        echo "✅ ~/.bashrc updated with OpenSSL Tools environment variables"
    fi
}

# Function to create credential validation script
create_credential_validator() {
    echo "🔧 Creating credential validation script..."
    
    cat > "${PROJECT_ROOT}/scripts/validate-credentials.sh" << 'EOF'
#!/bin/bash
# scripts/validate-credentials.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "🔍 Validating OpenSSL Tools credentials"

# Load environment
if [[ -f "${PROJECT_ROOT}/.env" ]]; then
    set -a
    source "${PROJECT_ROOT}/.env"
    set +a
fi

# Check required variables
local errors=0

if [[ -z "${ARTIFACTORY_URL:-}" ]]; then
    echo "❌ ARTIFACTORY_URL not set"
    errors=$((errors + 1))
else
    echo "✅ ARTIFACTORY_URL: ${ARTIFACTORY_URL}"
fi

if [[ -z "${ARTIFACTORY_TOKEN:-}" ]]; then
    echo "❌ ARTIFACTORY_TOKEN not set"
    errors=$((errors + 1))
else
    echo "✅ ARTIFACTORY_TOKEN: [HIDDEN]"
fi

if [[ -z "${ARTIFACTORY_REPO:-}" ]]; then
    echo "❌ ARTIFACTORY_REPO not set"
    errors=$((errors + 1))
else
    echo "✅ ARTIFACTORY_REPO: ${ARTIFACTORY_REPO}"
fi

# Test Artifactory connection
if [[ $errors -eq 0 ]]; then
    echo "🌐 Testing Artifactory connection..."
    if curl -s -f -H "Authorization: Bearer ${ARTIFACTORY_TOKEN}" "${ARTIFACTORY_URL}/artifactory/api/system/ping" >/dev/null 2>&1; then
        echo "✅ Artifactory connection successful"
    else
        echo "❌ Artifactory connection failed"
        errors=$((errors + 1))
    fi
fi

if [[ $errors -eq 0 ]]; then
    echo "🎉 All credentials are valid and working!"
    exit 0
else
    echo "💥 $errors credential issues found"
    exit 1
fi
EOF
    
    chmod +x "${PROJECT_ROOT}/scripts/validate-credentials.sh"
    echo "✅ Credential validation script created"
}

# Function to create credential management script
create_credential_manager() {
    echo "🔧 Creating credential management script..."
    
    cat > "${PROJECT_ROOT}/scripts/manage-credentials.sh" << 'EOF'
#!/bin/bash
# scripts/manage-credentials.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

show_help() {
    echo "OpenSSL Tools Credential Manager"
    echo ""
    echo "Usage: $0 {show|test|update|reset|backup|restore}"
    echo ""
    echo "Commands:"
    echo "  show     - Display current credentials (masked)"
    echo "  test     - Test credential validity"
    echo "  update   - Update credentials interactively"
    echo "  reset    - Reset all credentials"
    echo "  backup   - Backup current credentials"
    echo "  restore  - Restore credentials from backup"
    echo ""
}

show_credentials() {
    echo "📋 Current OpenSSL Tools Credentials"
    echo "===================================="
    
    if [[ -f "${PROJECT_ROOT}/.env" ]]; then
        set -a
        source "${PROJECT_ROOT}/.env"
        set +a
        
        echo "Artifactory URL: ${ARTIFACTORY_URL:-[NOT SET]}"
        echo "Artifactory Repo: ${ARTIFACTORY_REPO:-[NOT SET]}"
        echo "Artifactory Token: ${ARTIFACTORY_TOKEN:+[SET]}${ARTIFACTORY_TOKEN:-[NOT SET]}"
        echo "GitHub Token: ${GITHUB_TOKEN:+[SET]}${GITHUB_TOKEN:-[NOT SET]}"
        echo "Docker Hub User: ${DOCKER_HUB_USERNAME:-[NOT SET]}"
        echo "Conan Remote: ${CONAN_REMOTE_NAME:-[NOT SET]}"
    else
        echo "❌ No .env file found"
    fi
}

test_credentials() {
    "${PROJECT_ROOT}/scripts/validate-credentials.sh"
}

update_credentials() {
    "${PROJECT_ROOT}/scripts/setup-credentials.sh"
}

reset_credentials() {
    echo "⚠️  This will remove all stored credentials"
    read -p "Are you sure? (y/N): " confirm
    if [[ "$confirm" =~ ^[Yy]$ ]]; then
        rm -f "${PROJECT_ROOT}/.env"
        echo "✅ Credentials reset"
    else
        echo "❌ Reset cancelled"
    fi
}

backup_credentials() {
    local backup_file="${PROJECT_ROOT}/.env.backup.$(date +%Y%m%d_%H%M%S)"
    if [[ -f "${PROJECT_ROOT}/.env" ]]; then
        cp "${PROJECT_ROOT}/.env" "$backup_file"
        echo "✅ Credentials backed up to: $backup_file"
    else
        echo "❌ No .env file to backup"
    fi
}

restore_credentials() {
    local backup_files=($(ls "${PROJECT_ROOT}/.env.backup."* 2>/dev/null || true))
    if [[ ${#backup_files[@]} -eq 0 ]]; then
        echo "❌ No backup files found"
        return 1
    fi
    
    echo "Available backups:"
    for i in "${!backup_files[@]}"; do
        echo "  $((i+1)). ${backup_files[$i]}"
    done
    
    read -p "Select backup to restore (1-${#backup_files[@]}): " selection
    if [[ "$selection" =~ ^[0-9]+$ ]] && [[ $selection -ge 1 ]] && [[ $selection -le ${#backup_files[@]} ]]; then
        cp "${backup_files[$((selection-1))]}" "${PROJECT_ROOT}/.env"
        echo "✅ Credentials restored from: ${backup_files[$((selection-1))]}"
    else
        echo "❌ Invalid selection"
    fi
}

# Main execution
case "${1:-help}" in
    "show")
        show_credentials
        ;;
    "test")
        test_credentials
        ;;
    "update")
        update_credentials
        ;;
    "reset")
        reset_credentials
        ;;
    "backup")
        backup_credentials
        ;;
    "restore")
        restore_credentials
        ;;
    "help"|*)
        show_help
        ;;
esac
EOF
    
    chmod +x "${PROJECT_ROOT}/scripts/manage-credentials.sh"
    echo "✅ Credential management script created"
}

# Function to setup Conan remote
setup_conan_remote() {
    echo "📦 Setting up Conan remote..."
    
    if command -v conan >/dev/null 2>&1; then
        # Remove existing remote if it exists
        conan remote remove "${CONAN_REMOTE_NAME}" 2>/dev/null || true
        
        # Add new remote
        conan remote add "${CONAN_REMOTE_NAME}" "${CONAN_REMOTE_URL}"
        
        # Login to remote
        echo "${ARTIFACTORY_TOKEN}" | conan remote login "${CONAN_REMOTE_NAME}" admin -p -
        
        echo "✅ Conan remote '${CONAN_REMOTE_NAME}' configured"
    else
        echo "⚠️  Conan not found, skipping remote setup"
    fi
}

# Function to create credential test
create_credential_test() {
    echo "🧪 Creating credential test..."
    
    cat > "${PROJECT_ROOT}/scripts/test-credentials.sh" << 'EOF'
#!/bin/bash
# scripts/test-credentials.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "🧪 Testing OpenSSL Tools credentials and connectivity"

# Load environment
if [[ -f "${PROJECT_ROOT}/.env" ]]; then
    set -a
    source "${PROJECT_ROOT}/.env"
    set +a
fi

# Test 1: Environment variables
echo "1️⃣ Testing environment variables..."
"${PROJECT_ROOT}/scripts/validate-credentials.sh"

# Test 2: Artifactory connectivity
echo ""
echo "2️⃣ Testing Artifactory connectivity..."
if curl -s -f -H "Authorization: Bearer ${ARTIFACTORY_TOKEN}" "${ARTIFACTORY_URL}/artifactory/api/system/ping" >/dev/null 2>&1; then
    echo "✅ Artifactory ping successful"
else
    echo "❌ Artifactory ping failed"
    exit 1
fi

# Test 3: Conan remote
echo ""
echo "3️⃣ Testing Conan remote..."
if command -v conan >/dev/null 2>&1; then
    if conan remote list | grep -q "${CONAN_REMOTE_NAME}"; then
        echo "✅ Conan remote '${CONAN_REMOTE_NAME}' found"
    else
        echo "❌ Conan remote '${CONAN_REMOTE_NAME}' not found"
        exit 1
    fi
else
    echo "⚠️  Conan not available, skipping remote test"
fi

# Test 4: Docker connectivity
echo ""
echo "4️⃣ Testing Docker connectivity..."
if docker info >/dev/null 2>&1; then
    echo "✅ Docker is running"
else
    echo "❌ Docker is not running"
    exit 1
fi

# Test 5: Script permissions
echo ""
echo "5️⃣ Testing script permissions..."
local scripts=(
    "docker-build-and-upload.sh"
    "cursor-agents-coordinator.sh"
    "validate-artifactory-packages.sh"
    "generate_sbom.py"
    "dev-setup.sh"
)

for script in "${scripts[@]}"; do
    if [[ -x "${PROJECT_ROOT}/scripts/${script}" ]]; then
        echo "✅ $script is executable"
    else
        echo "❌ $script is not executable"
        exit 1
    fi
done

echo ""
echo "🎉 All credential tests passed!"
EOF
    
    chmod +x "${PROJECT_ROOT}/scripts/test-credentials.sh"
    echo "✅ Credential test script created"
}

# Main execution
main() {
    echo "🔐 OpenSSL Tools Credential Setup"
    echo "================================="
    echo ""
    
    # Check if running interactively
    if is_interactive; then
        # Load existing credentials or prompt for new ones
        if [[ -f "${PROJECT_ROOT}/.env" ]]; then
            echo "📋 Found existing .env file"
            read -p "Do you want to update credentials? (y/N): " update_confirm
            if [[ "$update_confirm" =~ ^[Yy]$ ]]; then
                prompt_credentials
            else
                load_existing_credentials
            fi
        else
            prompt_credentials
        fi
    else
        # Non-interactive mode - load from environment
        load_existing_credentials
    fi
    
    # Validate credentials
    if ! validate_credentials; then
        echo "❌ Credential validation failed"
        exit 1
    fi
    
    # Test Artifactory connection
    if ! test_artifactory_connection; then
        echo "❌ Artifactory connection test failed"
        exit 1
    fi
    
    # Create configuration files
    create_env_file
    update_bashrc
    create_credential_validator
    create_credential_manager
    create_credential_test
    setup_conan_remote
    
    echo ""
    echo "🎉 Credential setup complete!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Reload your shell: source ~/.bashrc"
    echo "2. Test credentials: ./scripts/test-credentials.sh"
    echo "3. Start building: ./scripts/docker-build-and-upload.sh"
    echo ""
    echo "🔧 Credential management:"
    echo "  ./scripts/manage-credentials.sh show    - Show current credentials"
    echo "  ./scripts/manage-credentials.sh test    - Test credentials"
    echo "  ./scripts/manage-credentials.sh update  - Update credentials"
    echo "  ./scripts/manage-credentials.sh backup  - Backup credentials"
}

# Execute main function
main "$@"