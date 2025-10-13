#!/bin/bash
set -e

echo "=== MCP Environment Validation ==="

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_PATH="${PROJECT_ROOT}/venv"

# Check virtual environment
if [ ! -f "${VENV_PATH}/bin/python" ]; then
    echo "❌ ERROR: Virtual environment not found at ${VENV_PATH}"
    exit 1
fi
echo "✅ Virtual environment found"

# Check MCP dependencies
echo "🔍 Checking MCP dependencies..."
if ! "${VENV_PATH}/bin/python" -c "import mcp, fastmcp, httpx, pydantic, tenacity" 2>/dev/null; then
    echo "❌ ERROR: Missing MCP dependencies"
    echo "Run: pip install mcp fastmcp httpx pydantic tenacity"
    exit 1
fi
echo "✅ All MCP dependencies installed"

# Verify MCP configuration
MCP_CONFIG="${PROJECT_ROOT}/.cursor/mcp.json"
if [ ! -f "${MCP_CONFIG}" ]; then
    echo "❌ ERROR: MCP configuration not found at ${MCP_CONFIG}"
    exit 1
fi
echo "✅ MCP configuration found"

# Validate JSON syntax
if ! jq empty "${MCP_CONFIG}" 2>/dev/null; then
    echo "❌ ERROR: Invalid JSON in MCP configuration"
    exit 1
fi
echo "✅ MCP configuration is valid JSON"

# Test cursor-agent integration
echo "🔍 Testing cursor-agent MCP integration..."
if ! command -v cursor-agent >/dev/null 2>&1; then
    echo "❌ ERROR: cursor-agent command not found"
    echo "Install Cursor with agent support"
    exit 1
fi

if ! cursor-agent mcp list >/dev/null 2>&1; then
    echo "❌ ERROR: cursor-agent MCP integration failed"
    exit 1
fi
echo "✅ cursor-agent MCP integration working"

# Check if MCP servers are configured
MCP_SERVERS=$(cursor-agent mcp list 2>/dev/null | grep -c "ready\|error\|connecting" || echo "0")
if [ "${MCP_SERVERS}" -eq 0 ]; then
    echo "⚠️  WARNING: No MCP servers detected as ready"
    echo "This might be normal if servers haven't been started yet"
else
    echo "✅ Found ${MCP_SERVERS} MCP server(s)"
fi

# Test individual MCP server tools (if servers are available)
echo "🔍 Testing individual MCP server tools..."
SERVERS=("openssl-database" "openssl-build" "openssl-security" "github-workflow-fixer" "openssl-ci")
for server in "${SERVERS[@]}"; do
    if cursor-agent mcp list-tools "${server}" >/dev/null 2>&1; then
        echo "✅ ${server} server tools available"
    else
        echo "⚠️  ${server} server not responding (might be normal)"
    fi
done

# Check environment variables
echo "🔍 Checking environment variables..."
REQUIRED_VARS=("GITHUB_TOKEN")
for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo "⚠️  WARNING: ${var} environment variable not set"
    else
        echo "✅ ${var} environment variable set"
    fi
done

# Test Python module imports
echo "🔍 Testing Python module imports..."
MODULES=("openssl_tools.automation.ai_agents.database_server" \
         "openssl_tools.automation.ai_agents.build_server" \
         "openssl_tools.automation.ai_agents.security_server" \
         "openssl_tools.automation.ai_agents.ci_server" \
         "openssl_tools.automation.ai_agents.workflow_fixer")

for module in "${MODULES[@]}"; do
    if PYTHONPATH="${PROJECT_ROOT}" "${VENV_PATH}/bin/python" -c "import ${module}" 2>/dev/null; then
        echo "✅ ${module} import successful"
    else
        echo "❌ ERROR: Failed to import ${module}"
        exit 1
    fi
done

echo ""
echo "🎉 All MCP environment checks passed!"
echo ""
echo "Next steps:"
echo "1. Set required environment variables (GITHUB_TOKEN, etc.)"
echo "2. Start MCP servers: cursor-agent mcp login <server-name>"
echo "3. Test in Cursor IDE or use cursor-agent CLI"
echo ""
echo "For debugging:"
echo "- Check logs: tail -f mcp_*.log"
echo "- Test individual servers: python -m openssl_tools.automation.ai_agents.<server_name>"
echo "- Validate configuration: jq . .cursor/mcp.json"