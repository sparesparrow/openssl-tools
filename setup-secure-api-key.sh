#!/usr/bin/env bash
# setup-secure-api-key.sh - Secure API key setup for agent-loop-improved.sh

set -euo pipefail

# Configuration
readonly API_KEY_FILE="$HOME/.cursor/api-key"
readonly API_KEY_DIR="$(dirname "$API_KEY_FILE")"

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $*"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $*"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*"
}

# Check if API key file already exists
check_existing_key() {
    if [[ -f "$API_KEY_FILE" ]]; then
        local perms
        perms=$(stat -c %a "$API_KEY_FILE" 2>/dev/null || echo "unknown")
        
        if [[ "$perms" == "600" ]]; then
            log_success "API key file already exists with correct permissions: $API_KEY_FILE"
            return 0
        else
            log_warn "API key file exists but has insecure permissions: $perms (expected 600)"
            return 1
        fi
    fi
    return 1
}

# Create secure API key file
create_api_key_file() {
    local api_key="$1"
    
    # Create directory if it doesn't exist
    if [[ ! -d "$API_KEY_DIR" ]]; then
        log_info "Creating directory: $API_KEY_DIR"
        mkdir -p "$API_KEY_DIR"
        chmod 700 "$API_KEY_DIR"
    fi
    
    # Create API key file with secure permissions
    log_info "Creating secure API key file: $API_KEY_FILE"
    echo "$api_key" > "$API_KEY_FILE"
    chmod 600 "$API_KEY_FILE"
    
    log_success "API key file created successfully"
}

# Validate API key format
validate_api_key() {
    local api_key="$1"
    
    if [[ -z "$api_key" ]]; then
        log_error "API key cannot be empty"
        return 1
    fi
    
    if [[ ! "$api_key" =~ ^key_[a-zA-Z0-9]{20,}$ ]]; then
        log_error "Invalid API key format. Expected format: key_<alphanumeric_string>"
        log_info "Get your API key from: https://cursor.com/settings/api"
        return 1
    fi
    
    return 0
}

# Test API key validity
test_api_key() {
    local api_key="$1"
    
    log_info "Testing API key validity..."
    
    # Set environment variable for testing
    export CURSOR_API_KEY="$api_key"
    
    # Test with a simple cursor-agent call
    if command -v cursor-agent >/dev/null 2>&1; then
        local test_output
        test_output="$(timeout 10s cursor-agent -p --output-format json "Return only valid JSON: {\"test\": \"success\"}" 2>/dev/null || echo "")"
        
        if [[ -n "$test_output" ]] && echo "$test_output" | jq -e '.test' >/dev/null 2>&1; then
            log_success "API key is valid and working"
            return 0
        else
            log_error "API key test failed - key may be invalid or expired"
            return 1
        fi
    else
        log_warn "cursor-agent not found - cannot test API key validity"
        log_info "Install cursor-agent: curl https://cursor.com/install -fsS | bash"
        return 0  # Don't fail if cursor-agent is not installed
    fi
}

# Main setup function
main() {
    log_info "Setting up secure API key for agent-loop-improved.sh"
    log_info "API key file location: $API_KEY_FILE"
    
    # Check if API key file already exists
    if check_existing_key; then
        log_info "API key file is already properly configured"
        exit 0
    fi
    
    # Get API key from user
    local api_key
    if [[ -n "${CURSOR_API_KEY:-}" ]]; then
        log_info "Using API key from CURSOR_API_KEY environment variable"
        api_key="$CURSOR_API_KEY"
    else
        echo -n "Enter your Cursor API key: "
        read -r api_key
    fi
    
    # Validate API key format
    if ! validate_api_key "$api_key"; then
        exit 1
    fi
    
    # Test API key validity
    if ! test_api_key "$api_key"; then
        log_error "API key validation failed"
        exit 1
    fi
    
    # Create secure API key file
    create_api_key_file "$api_key"
    
    log_success "Setup complete!"
    log_info "You can now run agent-loop-improved.sh with secure API key access"
    log_info "The API key is stored in: $API_KEY_FILE"
    log_info "File permissions: $(stat -c %a "$API_KEY_FILE")"
    
    # Show usage example
    echo
    log_info "Usage example:"
    echo "  ./agent-loop-improved.sh"
    echo "  DRY_RUN=true ./agent-loop-improved.sh  # For testing"
    echo "  LOG_LEVEL=debug ./agent-loop-improved.sh  # For debugging"
}

# Show help
show_help() {
    cat << EOF
Setup secure API key for agent-loop-improved.sh

USAGE:
    $0 [OPTIONS]

OPTIONS:
    -h, --help      Show this help message
    -f, --force     Force recreation of API key file even if it exists

ENVIRONMENT VARIABLES:
    CURSOR_API_KEY  If set, will use this API key instead of prompting

EXAMPLES:
    $0                          # Interactive setup
    CURSOR_API_KEY=key_... $0   # Use environment variable
    $0 --force                  # Force recreation

The API key will be stored in: $API_KEY_FILE
with secure permissions (600).

Get your API key from: https://cursor.com/settings/api
EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -f|--force)
            if [[ -f "$API_KEY_FILE" ]]; then
                log_info "Force mode: removing existing API key file"
                rm -f "$API_KEY_FILE"
            fi
            shift
            ;;
        *)
            log_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Run main function
main "$@"
