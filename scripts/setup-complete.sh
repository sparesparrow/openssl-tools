#!/bin/bash
# scripts/setup-complete.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "🚀 Complete OpenSSL Tools Setup"
echo "==============================="
echo ""

# Function to show setup options
show_setup_options() {
    echo "📋 Setup Options:"
    echo "1. Complete Setup (Credentials + Environment + Validation)"
    echo "2. Credentials Only"
    echo "3. Environment Only"
    echo "4. Validation Only"
    echo "5. Interactive Setup"
    echo "6. Reset Everything"
    echo ""
}

# Function to run complete setup
run_complete_setup() {
    echo "🎯 Running complete setup..."
    echo ""
    
    # Step 1: Setup credentials
    echo "1️⃣ Setting up credentials..."
    "${PROJECT_ROOT}/scripts/setup-credentials.sh"
    
    # Step 2: Setup environment
    echo ""
    echo "2️⃣ Setting up environment..."
    "${PROJECT_ROOT}/scripts/setup-environment.sh"
    
    # Step 3: Validate everything
    echo ""
    echo "3️⃣ Validating complete setup..."
    "${PROJECT_ROOT}/scripts/validate-openssl-tools-setup.sh"
    
    # Step 4: Test credentials
    echo ""
    echo "4️⃣ Testing credentials..."
    "${PROJECT_ROOT}/scripts/test-credentials.sh"
    
    # Step 5: Test environment
    echo ""
    echo "5️⃣ Testing environment..."
    "${PROJECT_ROOT}/scripts/test-environment.sh"
    
    echo ""
    echo "🎉 Complete setup finished!"
}

# Function to run credentials setup
run_credentials_setup() {
    echo "🔐 Setting up credentials..."
    "${PROJECT_ROOT}/scripts/setup-credentials.sh"
}

# Function to run environment setup
run_environment_setup() {
    echo "🌍 Setting up environment..."
    "${PROJECT_ROOT}/scripts/setup-environment.sh"
}

# Function to run validation
run_validation() {
    echo "🔍 Running validation..."
    "${PROJECT_ROOT}/scripts/validate-openssl-tools-setup.sh"
}

# Function to run interactive setup
run_interactive_setup() {
    echo "🎮 Interactive setup mode"
    echo ""
    
    # Check current status
    echo "📊 Current setup status:"
    if [[ -f "${PROJECT_ROOT}/.env" ]]; then
        echo "✅ .env file exists"
    else
        echo "❌ .env file missing"
    fi
    
    if [[ -f "${PROJECT_ROOT}/scripts/load-environment.sh" ]]; then
        echo "✅ Environment loader exists"
    else
        echo "❌ Environment loader missing"
    fi
    
    if grep -q "OpenSSL Tools Environment Setup" ~/.bashrc 2>/dev/null; then
        echo "✅ Shell configuration updated"
    else
        echo "❌ Shell configuration not updated"
    fi
    
    echo ""
    
    # Ask what to setup
    read -p "Setup credentials? (y/N): " setup_creds
    if [[ "$setup_creds" =~ ^[Yy]$ ]]; then
        run_credentials_setup
    fi
    
    echo ""
    read -p "Setup environment? (y/N): " setup_env
    if [[ "$setup_env" =~ ^[Yy]$ ]]; then
        run_environment_setup
    fi
    
    echo ""
    read -p "Run validation? (y/N): " run_validation
    if [[ "$run_validation" =~ ^[Yy]$ ]]; then
        run_validation
    fi
}

# Function to reset everything
reset_everything() {
    echo "⚠️  This will reset ALL OpenSSL Tools configuration"
    echo "   This includes:"
    echo "   - .env file"
    echo "   - Shell configuration"
    echo "   - Environment loaders"
    echo "   - All generated scripts"
    echo ""
    read -p "Are you absolutely sure? (y/N): " confirm
    if [[ "$confirm" =~ ^[Yy]$ ]]; then
        echo "🔄 Resetting everything..."
        
        # Remove .env file
        rm -f "${PROJECT_ROOT}/.env"
        echo "✅ Removed .env file"
        
        # Remove from shell configs
        for config in ~/.bashrc ~/.zshrc ~/.config/fish/config.fish; do
            if [[ -f "$config" ]]; then
                sed -i '/OpenSSL Tools Environment Setup/,/^$/d' "$config" 2>/dev/null || true
                echo "✅ Cleaned $config"
            fi
        done
        
        # Remove systemd service
        rm -f ~/.config/systemd/user/openssl-tools-environment.service
        echo "✅ Removed systemd service"
        
        # Remove generated scripts
        rm -f "${PROJECT_ROOT}/scripts/load-environment.sh"
        rm -f "${PROJECT_ROOT}/scripts/validate-credentials.sh"
        rm -f "${PROJECT_ROOT}/scripts/manage-credentials.sh"
        rm -f "${PROJECT_ROOT}/scripts/test-credentials.sh"
        rm -f "${PROJECT_ROOT}/scripts/test-environment.sh"
        rm -f "${PROJECT_ROOT}/scripts/manage-environment.sh"
        echo "✅ Removed generated scripts"
        
        # Clean artifacts and logs
        rm -rf "${PROJECT_ROOT}/artifacts"
        rm -rf "${PROJECT_ROOT}/logs"
        echo "✅ Cleaned artifacts and logs"
        
        echo ""
        echo "🎉 Reset complete! Run setup again to reconfigure."
    else
        echo "❌ Reset cancelled"
    fi
}

# Function to show status
show_status() {
    echo "📊 OpenSSL Tools Setup Status"
    echo "============================="
    echo ""
    
    # Check files
    echo "📁 Files:"
    if [[ -f "${PROJECT_ROOT}/.env" ]]; then
        echo "✅ .env file exists"
    else
        echo "❌ .env file missing"
    fi
    
    if [[ -f "${PROJECT_ROOT}/scripts/load-environment.sh" ]]; then
        echo "✅ Environment loader exists"
    else
        echo "❌ Environment loader missing"
    fi
    
    if [[ -f "${PROJECT_ROOT}/scripts/validate-credentials.sh" ]]; then
        echo "✅ Credential validator exists"
    else
        echo "❌ Credential validator missing"
    fi
    
    # Check shell integration
    echo ""
    echo "🐚 Shell Integration:"
    if grep -q "OpenSSL Tools Environment Setup" ~/.bashrc 2>/dev/null; then
        echo "✅ Bash configuration updated"
    else
        echo "❌ Bash configuration not updated"
    fi
    
    if grep -q "OpenSSL Tools Environment Setup" ~/.zshrc 2>/dev/null; then
        echo "✅ Zsh configuration updated"
    else
        echo "❌ Zsh configuration not updated"
    fi
    
    # Check environment
    echo ""
    echo "🌍 Environment:"
    if [[ -n "${OPENSSL_TOOLS_ROOT:-}" ]]; then
        echo "✅ Environment variables loaded"
    else
        echo "❌ Environment variables not loaded"
    fi
    
    # Check credentials
    echo ""
    echo "🔐 Credentials:"
    if [[ -n "${ARTIFACTORY_URL:-}" ]]; then
        echo "✅ Artifactory URL set"
    else
        echo "❌ Artifactory URL not set"
    fi
    
    if [[ -n "${ARTIFACTORY_TOKEN:-}" ]]; then
        echo "✅ Artifactory token set"
    else
        echo "❌ Artifactory token not set"
    fi
    
    # Check tools
    echo ""
    echo "🛠️  Tools:"
    if command -v docker >/dev/null 2>&1; then
        echo "✅ Docker available"
    else
        echo "❌ Docker not available"
    fi
    
    if command -v conan >/dev/null 2>&1; then
        echo "✅ Conan available"
    else
        echo "❌ Conan not available"
    fi
    
    if command -v python3 >/dev/null 2>&1; then
        echo "✅ Python3 available"
    else
        echo "❌ Python3 not available"
    fi
}

# Function to show help
show_help() {
    echo "OpenSSL Tools Complete Setup"
    echo ""
    echo "Usage: $0 {complete|credentials|environment|validation|interactive|reset|status|help}"
    echo ""
    echo "Commands:"
    echo "  complete     - Run complete setup (credentials + environment + validation)"
    echo "  credentials  - Setup credentials only"
    echo "  environment  - Setup environment only"
    echo "  validation   - Run validation only"
    echo "  interactive  - Interactive setup mode"
    echo "  reset        - Reset all configuration"
    echo "  status       - Show current setup status"
    echo "  help         - Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 complete     # Full setup"
    echo "  $0 interactive  # Step-by-step setup"
    echo "  $0 status       # Check current status"
    echo "  $0 reset        # Reset everything"
}

# Main execution
case "${1:-interactive}" in
    "complete")
        run_complete_setup
        ;;
    "credentials")
        run_credentials_setup
        ;;
    "environment")
        run_environment_setup
        ;;
    "validation")
        run_validation
        ;;
    "interactive")
        show_setup_options
        run_interactive_setup
        ;;
    "reset")
        reset_everything
        ;;
    "status")
        show_status
        ;;
    "help"|*)
        show_help
        ;;
esac