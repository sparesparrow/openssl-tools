#!/bin/bash
# Hybrid configure wrapper for OpenSSL
# Attempts Python-based configuration first, falls back to Perl Configure

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OPENSSL_TOOLS_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is available and has the required modules
check_python_configurator() {
    if ! command -v python3 &> /dev/null; then
        log_warn "Python3 not found, falling back to Perl Configure"
        return 1
    fi

    # Check if the Python configurator script exists
    if [[ ! -f "$SCRIPT_DIR/conan/openssl_configure.py" ]]; then
        log_warn "Python configurator not found, falling back to Perl Configure"
        return 1
    fi

    # Try to import required modules
    if ! python3 -c "import sys; sys.path.insert(0, '$SCRIPT_DIR/conan'); from openssl_configure import OpenSSLConfigurator" 2>/dev/null; then
        log_warn "Python configurator dependencies not available, falling back to Perl Configure"
        return 1
    fi

    return 0
}

# Try Python-based configuration
try_python_configure() {
    log_info "Attempting Python-based OpenSSL configuration..."

    # Set PYTHONPATH to include our scripts
    export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

    # Call the Python configurator
    if python3 "$SCRIPT_DIR/conan/cmd_configure.py" "$@"; then
        log_info "Python configuration completed successfully"
        return 0
    else
        log_error "Python configuration failed"
        return 1
    fi
}

# Fallback to Perl Configure
fallback_perl_configure() {
    log_info "Falling back to Perl Configure script..."

    # Find the OpenSSL source directory
    if [[ -f "../Configure" ]]; then
        OPENSSL_SRC="../"
    elif [[ -f "../../openssl-upstream/Configure" ]]; then
        OPENSSL_SRC="../../openssl-upstream/"
    elif [[ -f "../../../overlay/Configure" ]]; then
        OPENSSL_SRC="../../../overlay/"
    else
        log_error "Could not find OpenSSL Configure script"
        exit 1
    fi

    log_info "Using OpenSSL Configure at: $OPENSSL_SRC"

    # Execute the Perl Configure script
    cd "$OPENSSL_SRC"
    if perl Configure "$@"; then
        log_info "Perl Configure completed successfully"
        return 0
    else
        log_error "Perl Configure failed"
        exit 1
    fi
}

# Main execution
main() {
    log_info "OpenSSL Configure Wrapper Starting..."

    # Check if we can use Python configurator
    if check_python_configurator; then
        if try_python_configure "$@"; then
            exit 0
        fi
    fi

    # Fallback to Perl Configure
    fallback_perl_configure "$@"
}

# Run main function with all arguments
main "$@"