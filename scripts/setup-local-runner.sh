#!/bin/bash
# scripts/setup-local-runner.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Default configuration
RUNNER_VERSION="${RUNNER_VERSION:-2.314.1}"
RUNNER_NAME="${RUNNER_NAME:-}"
RUNNER_LABELS="${RUNNER_LABELS:-}"
GITHUB_TOKEN="${GITHUB_TOKEN:-}"
REPO_URL="${REPO_URL:-}"

# Detect platform
detect_platform() {
    case "$(uname -s)" in
        Linux)
            if [[ "$(uname -m)" == "x86_64" ]]; then
                echo "linux-x64"
            elif [[ "$(uname -m)" == "aarch64" ]]; then
                echo "linux-arm64"
            else
                echo "linux-$(uname -m)"
            fi
            ;;
        Darwin)
            if [[ "$(uname -m)" == "x86_64" ]]; then
                echo "osx-x64"
            elif [[ "$(uname -m)" == "arm64" ]]; then
                echo "osx-arm64"
            else
                echo "osx-$(uname -m)"
            fi
            ;;
        CYGWIN*|MINGW*|MSYS*)
            echo "win-x64"
            ;;
        *)
            echo "unknown"
            ;;
    esac
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --runner-name)
            RUNNER_NAME="$2"
            shift 2
            ;;
        --labels)
            RUNNER_LABELS="$2"
            shift 2
            ;;
        --token)
            GITHUB_TOKEN="$2"
            shift 2
            ;;
        --repo-url)
            REPO_URL="$2"
            shift 2
            ;;
        --version)
            RUNNER_VERSION="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Set up a GitHub Actions self-hosted runner for local builds."
            echo ""
            echo "Options:"
            echo "  --runner-name NAME    Name for the runner (default: auto-generated)"
            echo "  --labels LABELS       Comma-separated labels (default: auto-detected)"
            echo "  --token TOKEN         GitHub Personal Access Token"
            echo "  --repo-url URL        Repository URL (default: auto-detected)"
            echo "  --version VERSION     Runner version (default: 2.314.1)"
            echo "  --help                Show this help"
            echo ""
            echo "Environment Variables:"
            echo "  GITHUB_TOKEN          GitHub Personal Access Token"
            echo "  REPO_URL             Repository URL"
            echo ""
            echo "Examples:"
            echo "  $0 --labels ubuntu-local --token ghp_xxx"
            echo "  $0 --runner-name my-runner --labels windows-local"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "🚀 GitHub Actions Local Runner Setup"
echo "===================================="

# Detect platform and set defaults
PLATFORM=$(detect_platform)
echo "🖥️  Detected platform: ${PLATFORM}"

# Set default runner name
if [[ -z "${RUNNER_NAME}" ]]; then
    RUNNER_NAME="local-runner-$(hostname)-$(date +%s)"
fi

# Set default labels based on platform
if [[ -z "${RUNNER_LABELS}" ]]; then
    case "$(uname -s)" in
        Linux)
            RUNNER_LABELS="ubuntu-local,self-hosted"
            ;;
        Darwin)
            RUNNER_LABELS="macos-local,self-hosted"
            ;;
        CYGWIN*|MINGW*|MSYS*)
            RUNNER_LABELS="windows-local,self-hosted"
            ;;
        *)
            RUNNER_LABELS="local,self-hosted"
            ;;
    esac
fi

# Set repository URL
if [[ -z "${REPO_URL}" ]]; then
    if git remote get-url origin &>/dev/null; then
        REPO_URL=$(git remote get-url origin | sed 's|git@github.com:|https://github.com/|; s|\.git$||')
    else
        echo "❌ Could not detect repository URL. Please specify --repo-url"
        exit 1
    fi
fi

# Check for token
if [[ -z "${GITHUB_TOKEN}" ]]; then
    echo "❌ GitHub token not provided. Use --token or set GITHUB_TOKEN environment variable"
    echo ""
    echo "To create a token:"
    echo "1. Go to https://github.com/settings/tokens"
    echo "2. Generate a new token with 'repo' scope"
    echo "3. Set GITHUB_TOKEN=your_token_here"
    exit 1
fi

echo "📋 Configuration:"
echo "  Runner Name: ${RUNNER_NAME}"
echo "  Labels: ${RUNNER_LABELS}"
echo "  Repository: ${REPO_URL}"
echo "  Platform: ${PLATFORM}"
echo "  Version: ${RUNNER_VERSION}"
echo ""

# Create runner directory
RUNNER_DIR="${PROJECT_ROOT}/runner-${RUNNER_NAME}"
echo "📁 Creating runner directory: ${RUNNER_DIR}"
rm -rf "${RUNNER_DIR}"
mkdir -p "${RUNNER_DIR}"
cd "${RUNNER_DIR}"

# Download runner
echo "📥 Downloading GitHub Actions Runner..."
RUNNER_ARCHIVE="actions-runner-${PLATFORM}-${RUNNER_VERSION}.tar.gz"
RUNNER_URL="https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/${RUNNER_ARCHIVE}"

if command -v curl &> /dev/null; then
    curl -L -o "${RUNNER_ARCHIVE}" "${RUNNER_URL}"
elif command -v wget &> /dev/null; then
    wget -O "${RUNNER_ARCHIVE}" "${RUNNER_URL}"
else
    echo "❌ Neither curl nor wget found. Please install one of them."
    exit 1
fi

# Extract runner
echo "📦 Extracting runner..."
tar xzf "${RUNNER_ARCHIVE}"

# Configure runner
echo "⚙️  Configuring runner..."
./config.sh \
    --url "${REPO_URL}" \
    --token "${GITHUB_TOKEN}" \
    --name "${RUNNER_NAME}" \
    --labels "${RUNNER_LABELS}" \
    --unattended \
    --replace

# Create service script for easy management
create_service_script() {
    local script_name="$1"
    local start_cmd="$2"
    local stop_cmd="$3"

    cat > "${script_name}" << EOF
#!/bin/bash
# ${script_name} - Manage GitHub Actions Runner

SCRIPT_DIR="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"
RUNNER_DIR="\${SCRIPT_DIR}"

case "\${1:-}" in
    start)
        echo "🚀 Starting runner..."
        cd "\${RUNNER_DIR}"
        nohup ${start_cmd} > runner.log 2>&1 &
        echo \$! > runner.pid
        echo "✅ Runner started (PID: \$(cat runner.pid))"
        ;;
    stop)
        if [[ -f "\${RUNNER_DIR}/runner.pid" ]]; then
            echo "🛑 Stopping runner..."
            ${stop_cmd}
            kill \$(cat "\${RUNNER_DIR}/runner.pid") 2>/dev/null || true
            rm -f "\${RUNNER_DIR}/runner.pid"
            echo "✅ Runner stopped"
        else
            echo "ℹ️  Runner not running"
        fi
        ;;
    status)
        if [[ -f "\${RUNNER_DIR}/runner.pid" ]] && kill -0 \$(cat "\${RUNNER_DIR}/runner.pid") 2>/dev/null; then
            echo "✅ Runner is running (PID: \$(cat "\${RUNNER_DIR}/runner.pid"))"
        else
            echo "❌ Runner is not running"
            rm -f "\${RUNNER_DIR}/runner.pid" 2>/dev/null || true
        fi
        ;;
    logs)
        if [[ -f "\${RUNNER_DIR}/runner.log" ]]; then
            tail -f "\${RUNNER_DIR}/runner.log"
        else
            echo "📝 No log file found"
        fi
        ;;
    *)
        echo "Usage: \$0 {start|stop|status|logs}"
        echo ""
        echo "Commands:"
        echo "  start   Start the runner in background"
        echo "  stop    Stop the runner"
        echo "  status  Check runner status"
        echo "  logs    Show runner logs"
        exit 1
        ;;
esac
EOF

    chmod +x "${script_name}"
}

case "$(uname -s)" in
    Linux|Darwin)
        create_service_script "runner-service.sh" "./run.sh" "./config.sh remove --token ${GITHUB_TOKEN}"
        ;;
    CYGWIN*|MINGW*|MSYS*)
        create_service_script "runner-service.bat" "run.cmd" "config.cmd remove --token ${GITHUB_TOKEN}"
        ;;
esac

# Clean up
rm -f "${RUNNER_ARCHIVE}"

echo ""
echo "🎉 Runner setup completed!"
echo "=========================="
echo "📁 Runner Directory: ${RUNNER_DIR}"
echo "🏷️  Labels: ${RUNNER_LABELS}"
echo ""
echo "🚀 To start the runner:"
echo "  cd ${RUNNER_DIR}"
echo "  ./run.sh  # Linux/macOS"
echo "  # or"
echo "  run.cmd   # Windows"
echo ""
echo "🔧 Service management:"
echo "  ${RUNNER_DIR}/runner-service.sh start|stop|status|logs"
echo ""
echo "⚠️  Remember to stop the runner when done:"
echo "  ${RUNNER_DIR}/runner-service.sh stop"
echo ""
echo "🧹 To remove the runner:"
echo "  cd ${RUNNER_DIR}"
echo "  ./config.sh remove --token ${GITHUB_TOKEN}"