#!/bin/bash
# scripts/cursor-agents-coordinator.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Cursor agent paths
OPENSSL_REPO="${PROJECT_ROOT}"
OPENSSL_TOOLS_REPO="${PROJECT_ROOT}/../openssl-tools"

echo "🤖 Starting Cursor Agents Coordination"

# Function to check cursor-agent availability
check_cursor_agent() {
    if ! command -v cursor-agent >/dev/null 2>&1; then
        echo "❌ cursor-agent command not found"
        echo "Please install Cursor with agent support or run without agents"
        return 1
    fi
    echo "✅ cursor-agent found"
    return 0
}

# Function to start openssl core agent
start_core_agent() {
    echo "🚀 Starting OpenSSL Core Agent"
    
    cursor-agent start \
        --config="${OPENSSL_REPO}/.cursor/agents/openssl-core-agent.yml" \
        --repository="${OPENSSL_REPO}" \
        --mode="background" \
        --log-level="info" \
        --output="${PROJECT_ROOT}/logs/core-agent.log" &
    
    CORE_AGENT_PID=$!
    echo "📝 Core Agent PID: ${CORE_AGENT_PID}"
    echo "${CORE_AGENT_PID}" > "${PROJECT_ROOT}/logs/core-agent.pid"
}

# Function to start openssl tools agent  
start_tools_agent() {
    echo "🚀 Starting OpenSSL Tools Agent"
    
    if [[ -d "${OPENSSL_TOOLS_REPO}" ]]; then
        cursor-agent start \
            --config="${OPENSSL_TOOLS_REPO}/.cursor/agents/openssl-tools-agent.yml" \
            --repository="${OPENSSL_TOOLS_REPO}" \
            --mode="background" \
            --log-level="info" \
            --output="${PROJECT_ROOT}/logs/tools-agent.log" &
        
        TOOLS_AGENT_PID=$!
        echo "📝 Tools Agent PID: ${TOOLS_AGENT_PID}"
        echo "${TOOLS_AGENT_PID}" > "${PROJECT_ROOT}/logs/tools-agent.pid"
    else
        echo "⚠️  OpenSSL Tools repository not found at ${OPENSSL_TOOLS_REPO}"
        echo "   Skipping tools agent startup"
    fi  
}

# Function to coordinate build task
coordinate_build() {
    echo "🎯 Coordinating build task between agents"
    
    # Send build task to core agent
    cursor-agent task \
        --agent="openssl-core-agent" \
        --task="docker_build_coordination" \
        --parameters='{
            "build_type": "multi_platform",
            "version": "'${VERSION:-$(date +%Y%m%d)-$(git rev-parse --short HEAD)}'",
            "platforms": ["ubuntu-20.04-gcc", "ubuntu-22.04-clang", "windows-2022", "macos-x86_64", "macos-arm64"],
            "artifacts_dir": "'${PROJECT_ROOT}/artifacts'"
        }' \
        --async
    
    # Send dependency management task to tools agent
    if [[ -f "${PROJECT_ROOT}/logs/tools-agent.pid" ]]; then
        cursor-agent task \
            --agent="openssl-tools-agent" \
            --task="dependency_coordination" \
            --parameters='{
                "action": "prepare_conan_packages",
                "target_registries": ["artifactory"],
                "build_profiles": ["release", "debug"]
            }' \
            --async
    fi
}

# Function to monitor agent status
monitor_agents() {
    echo "📊 Monitoring agent status"
    
    while true; do
        if [[ -f "${PROJECT_ROOT}/logs/core-agent.pid" ]]; then
            CORE_PID=$(cat "${PROJECT_ROOT}/logs/core-agent.pid")
            if kill -0 "${CORE_PID}" 2>/dev/null; then
                echo "✅ Core Agent (PID: ${CORE_PID}) - Running"
            else
                echo "❌ Core Agent - Stopped"
            fi
        fi
        
        if [[ -f "${PROJECT_ROOT}/logs/tools-agent.pid" ]]; then
            TOOLS_PID=$(cat "${PROJECT_ROOT}/logs/tools-agent.pid")
            if kill -0 "${TOOLS_PID}" 2>/dev/null; then
                echo "✅ Tools Agent (PID: ${TOOLS_PID}) - Running"
            else
                echo "❌ Tools Agent - Stopped"
            fi
        fi
        
        sleep 30
    done
}

# Function to stop agents
stop_agents() {
    echo "🛑 Stopping Cursor Agents"
    
    if [[ -f "${PROJECT_ROOT}/logs/core-agent.pid" ]]; then
        CORE_PID=$(cat "${PROJECT_ROOT}/logs/core-agent.pid")
        if kill -0 "${CORE_PID}" 2>/dev/null; then
            kill "${CORE_PID}"
            echo "✅ Core Agent stopped"
        fi
        rm -f "${PROJECT_ROOT}/logs/core-agent.pid"
    fi
    
    if [[ -f "${PROJECT_ROOT}/logs/tools-agent.pid" ]]; then
        TOOLS_PID=$(cat "${PROJECT_ROOT}/logs/tools-agent.pid")
        if kill -0 "${TOOLS_PID}" 2>/dev/null; then
            kill "${TOOLS_PID}"
            echo "✅ Tools Agent stopped"
        fi
        rm -f "${PROJECT_ROOT}/logs/tools-agent.pid"
    fi
}

# Setup logging
mkdir -p "${PROJECT_ROOT}/logs"

# Trap cleanup
trap stop_agents EXIT

# Main execution
case "${1:-start}" in
    "start")
        if check_cursor_agent; then
            start_core_agent
            start_tools_agent
            coordinate_build
            echo "🎉 Agents started and coordinated"
        else
            echo "⚠️  Running without cursor agents"
        fi
        ;;
    "monitor")
        monitor_agents
        ;;
    "stop")
        stop_agents
        ;;
    "coordinate")
        coordinate_build
        ;;
    *)
        echo "Usage: $0 {start|monitor|stop|coordinate}"
        exit 1
        ;;
esac