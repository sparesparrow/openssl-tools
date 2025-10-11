# Cursor CLI Integration for agent-loop.sh

This document describes the integration of Cursor CLI features into the `agent-loop.sh` script for enhanced AI-powered CI repair.

## Overview

The `agent-loop.sh` script now supports advanced Cursor CLI features including:

- **Headless mode configuration** via `.cursor/cli-config.json`
- **MCP (Model Context Protocol) integration** for enhanced context
- **Agent-specific configuration** via `.cursor/agents/ci-repair-agent.yml`
- **Rule-based guidance** from `.cursor/rules/`

## Configuration Files

### 1. `.cursor/cli-config.json`

Main configuration file for Cursor CLI behavior:

```json
{
  "agent": {
    "model": "claude-3.5-sonnet",
    "temperature": 0.2,
    "max_tokens": 8192,
    "timeout_ms": 60000
  },
  "headless": {
    "output_format": "json",
    "force_mode": true,
    "print_result": true,
    "stream": false
  },
  "mcp": {
    "enabled": true,
    "servers": ["github", "openssl-ci", ...],
    "timeout_ms": 5000
  }
}
```

### 2. `.cursor/mcp-servers.json`

MCP server configuration for context providers:

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"]
    },
    "openssl-ci": {
      "command": "python3",
      "args": ["${workspaceFolder}/scripts/mcp/ci-server.py"]
    }
  }
}
```

### 3. `.cursor/agents/ci-repair-agent.yml`

Agent-specific configuration for CI repair behavior:

```yaml
name: ci-repair-agent
capabilities:
  - workflow_analysis
  - log_parsing
  - patch_generation

mcp_servers:
  - github
  - openssl-ci

rules:
  - path: .cursor/rules/cicd-modernization.mdc
    weight: high
```

## MCP Servers

### openssl-ci Server

Located at `scripts/mcp/ci-server.py`, provides CI-specific context:

**Available Tools:**

1. **get_workflow_runs(limit)** - Get recent workflow run history
2. **get_failed_job_logs(run_id)** - Get logs from failed jobs
3. **get_pr_status(pr_number)** - Get PR status and checks
4. **get_recent_commits(limit)** - Get recent commit history
5. **get_workflow_file(workflow_name)** - Read workflow files

### GitHub Server

Provided by `@modelcontextprotocol/server-github`, gives access to:
- Repository information
- Pull requests and reviews
- Issues and comments
- Workflow runs

## Usage

### Basic Usage

```bash
# Use default configuration
./agent-loop.sh

# With custom configuration
CURSOR_CONFIG_FILE=.cursor/custom-config.json ./agent-loop.sh
```

### Environment Variables

- `CURSOR_CONFIG_FILE` - Path to CLI config (default: `.cursor/cli-config.json`)
- `CURSOR_MCP_CONFIG` - Path to MCP config (default: `.cursor/mcp-servers.json`)
- `CURSOR_AGENT_CONFIG` - Path to agent config (default: `.cursor/agents/ci-repair-agent.yml`)
- `CURSOR_API_KEY` - API key for cursor-agent (required)

### Enabling MCP

Set `"enabled": true` in `.cursor/cli-config.json`:

```json
{
  "mcp": {
    "enabled": true,
    "servers": ["github", "openssl-ci"]
  }
}
```

The script will automatically:
1. Load MCP server configurations
2. Pass MCP config to cursor-agent via `--mcp` flag
3. Include MCP tool hints in prompts
4. Enable cursor-agent to call MCP tools for context

## How It Works

### 1. Configuration Loading

At startup, `agent-loop.sh` calls `load_cursor_config()` which:
- Reads `.cursor/cli-config.json`
- Extracts model, timeout, and MCP settings
- Sets environment variables for cursor-agent

### 2. Enhanced Cursor-Agent Invocation

When calling cursor-agent, the script builds a command with:

```bash
cursor-agent -p --force \
  --output-format json \
  --config .cursor/cli-config.json \
  --mcp .cursor/mcp-servers.json \
  --agent .cursor/agents/ci-repair-agent.yml \
  --rules .cursor/rules \
  "<prompt>"
```

### 3. MCP Context in Prompts

When MCP is enabled, prompts include:

```
MCP TOOLS AVAILABLE:
- get_workflow_runs(limit): Get detailed workflow run history
- get_failed_job_logs(run_id): Get logs from failed jobs
- get_pr_status(pr_number): Get PR status and checks
...

Use these tools BEFORE proposing fixes.
```

### 4. Agent Decision-Making

With MCP access, cursor-agent can:
1. Call `get_workflow_runs()` to see failure patterns
2. Call `get_failed_job_logs(run_id)` to analyze specific failures
3. Call `get_workflow_file(name)` to read workflow configurations
4. Propose informed fixes based on full context

## Benefits

### 1. Enhanced Context

MCP provides real-time access to:
- Workflow logs and status
- PR metadata and reviews
- Git history and commits
- Build system state (via other MCP servers)

### 2. Better Decisions

With full context, cursor-agent can:
- Identify root causes more accurately
- Propose more appropriate fixes
- Avoid breaking changes
- Consider historical patterns

### 3. Consistency

Configuration files ensure:
- Reproducible behavior across runs
- Consistent model and temperature settings
- Unified rule application
- Standardized tool access

### 4. Modularity

MCP servers can be:
- Added without modifying agent-loop.sh
- Enabled/disabled via configuration
- Developed independently
- Shared across projects

## Testing

### Test Configuration Loading

```bash
# Enable debug logging
LOG_LEVEL=debug ./agent-loop.sh
```

Look for:
```
{"level":"info","msg":"Loading Cursor CLI configuration from .cursor/cli-config.json"}
{"level":"debug","msg":"Loaded config: model=claude-3.5-sonnet, timeout=60s, mcp=true"}
```

### Test MCP Server

```bash
# Test the CI MCP server directly
python3 scripts/mcp/ci-server.py
```

### Test Cursor-Agent with MCP

```bash
# Set API key
export CURSOR_API_KEY=your_key

# Run with MCP enabled
./agent-loop.sh
```

Check for MCP tool usage in logs:
```
{"level":"debug","msg":"Using MCP config: .cursor/mcp-servers.json (servers: github,openssl-ci)"}
```

## Troubleshooting

### MCP Server Not Starting

**Issue:** MCP server fails to start

**Solutions:**
1. Check Python dependencies: `pip install mcp`
2. Verify server script is executable: `chmod +x scripts/mcp/ci-server.py`
3. Check environment variables in `.cursor/mcp-servers.json`

### Cursor-Agent Not Using MCP

**Issue:** Cursor-agent doesn't call MCP tools

**Solutions:**
1. Verify `"enabled": true` in `.cursor/cli-config.json`
2. Check MCP server configuration in `.cursor/mcp-servers.json`
3. Ensure cursor-agent CLI supports `--mcp` flag (check version)
4. Review prompt to ensure MCP tool hints are included

### Configuration Not Loading

**Issue:** Configuration file not found or not loaded

**Solutions:**
1. Check file path: `ls -la .cursor/cli-config.json`
2. Verify JSON syntax: `jq . .cursor/cli-config.json`
3. Check environment variables: `echo $CURSOR_CONFIG_FILE`

## Best Practices

1. **Start Simple**: Enable MCP gradually, test with one server first
2. **Monitor Logs**: Use `LOG_LEVEL=debug` to see configuration and MCP usage
3. **Test Servers**: Test MCP servers independently before integration
4. **Version Control**: Keep configurations in git for reproducibility
5. **Document Changes**: Update this README when adding new MCP servers

## Future Enhancements

Potential improvements:

1. **Database MCP Integration**: Connect to PostgreSQL for build history
2. **Build System MCP**: Access Conan package information
3. **Security MCP**: Integrate security scanning results
4. **Metrics MCP**: Provide performance metrics and trends
5. **Cache MCP**: Access build cache information

## References

- [Cursor CLI Documentation](https://cursor.com/docs/cli)
- [Cursor CLI Headless Mode](https://cursor.com/docs/cli/headless)
- [Cursor CLI MCP Integration](https://cursor.com/docs/cli/mcp)
- [Cursor CLI Configuration](https://cursor.com/docs/cli/reference/configuration)
- [Cursor CLI CI Fix Cookbook](https://cursor.com/docs/cli/cookbook/fix-ci)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)

