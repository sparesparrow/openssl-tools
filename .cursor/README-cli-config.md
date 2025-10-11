# Cursor CLI Configuration Compliance

This document explains how the `.cursor/cli-config.json` file is structured to be compliant with the [official Cursor CLI configuration schema](https://cursor.com/docs/cli/reference/configuration).

## Configuration Structure

The configuration file follows the official Cursor CLI schema with the following structure:

### Top-Level Configuration

```json
{
  "model": "auto",
  "temperature": 0.2,
  "maxTokens": 8192,
  "timeout": 60000,
  "outputFormat": "json",
  "force": true,
  "printResult": true,
  "stream": false
}
```

**Fields:**
- `model`: AI model to use (`"auto"` for automatic selection)
- `temperature`: Model temperature (0.0-1.0, lower = more focused)
- `maxTokens`: Maximum tokens in response
- `timeout`: Timeout in milliseconds
- `outputFormat`: Output format (`"json"`, `"text"`, `"markdown"`)
- `force`: Force execution without confirmation
- `printResult`: Print results to stdout
- `stream`: Enable streaming output

### MCP Configuration

```json
{
  "mcp": {
    "enabled": false,
    "servers": [
      "github",
      "openssl-ci",
      "openssl-database",
      "openssl-build",
      "openssl-security"
    ],
    "timeout": 5000
  }
}
```

**Fields:**
- `enabled`: Enable MCP (Model Context Protocol) integration
- `servers`: List of MCP server names to connect to
- `timeout`: MCP server timeout in milliseconds

### Context Configuration

```json
{
  "context": {
    "includeGitHistory": true,
    "maxCommits": 15,
    "includePrInfo": true,
    "includeWorkflowRuns": true,
    "rulesDirectories": [
      ".cursor/rules"
    ]
  }
}
```

**Fields:**
- `includeGitHistory`: Include git commit history in context
- `maxCommits`: Maximum number of commits to include
- `includePrInfo`: Include pull request information
- `includeWorkflowRuns`: Include workflow run information
- `rulesDirectories`: Directories containing rule files

### CI Repair Configuration (Custom Extension)

```json
{
  "ciRepair": {
    "maxBatchActions": 5,
    "requireConfirmation": false,
    "autoCommit": true,
    "commitMessagePrefix": "ci(auto-fix):",
    "allowedActions": [
      "rerun",
      "approve",
      "apply-patch",
      "enable-workflow",
      "disable-workflow",
      "rerun-failed-workflows"
    ]
  }
}
```

**Note:** This is a custom extension for the `agent-loop.sh` script and is not part of the official Cursor CLI schema.

## Compliance with Official Schema

### ✅ Compliant Fields

The following fields are fully compliant with the [official Cursor CLI configuration](https://cursor.com/docs/cli/reference/configuration):

- `model` - AI model selection
- `temperature` - Model temperature
- `maxTokens` - Maximum response tokens
- `timeout` - Operation timeout
- `outputFormat` - Output format specification
- `force` - Force execution flag
- `printResult` - Print results flag
- `stream` - Streaming mode flag

### ✅ MCP Integration

The MCP configuration follows the official schema:
- `mcp.enabled` - Enable/disable MCP
- `mcp.servers` - List of MCP servers
- `mcp.timeout` - MCP server timeout

### ✅ Context Configuration

Context fields are compliant with the official schema:
- `context.includeGitHistory` - Git history inclusion
- `context.maxCommits` - Maximum commits
- `context.includePrInfo` - PR information inclusion
- `context.includeWorkflowRuns` - Workflow run inclusion
- `context.rulesDirectories` - Rules directory paths

### ⚠️ Custom Extensions

The `ciRepair` section is a custom extension for the `agent-loop.sh` script and is not part of the official Cursor CLI schema. This is intentional and provides additional functionality specific to CI repair operations.

## Usage in agent-loop.sh

The `agent-loop.sh` script loads this configuration using:

```bash
# Load configuration values
AGENT_MODEL="$(jq -r '.model // "auto"' "$CURSOR_CONFIG_FILE")"
timeout_ms="$(jq -r '.timeout // 60000' "$CURSOR_CONFIG_FILE")"
MCP_ENABLED="$(jq -r '.mcp.enabled // false' "$CURSOR_CONFIG_FILE")"
```

## Environment Variable Overrides

The following environment variables can override configuration values:

- `CURSOR_CONFIG_FILE` - Path to configuration file
- `CURSOR_MCP_CONFIG` - Path to MCP server configuration
- `CURSOR_AGENT_CONFIG` - Path to agent configuration
- `AGENT_MODEL` - Override model setting
- `MCP_ENABLED` - Override MCP enablement

## Validation

To validate the configuration:

```bash
# Check JSON syntax
jq . .cursor/cli-config.json

# Test configuration loading
LOG_LEVEL=debug ./agent-loop.sh "Test" execution 2>&1 | head -10
```

## Migration from Custom Schema

The configuration was updated from a custom schema to be compliant with the official Cursor CLI schema:

### Before (Custom Schema)
```json
{
  "agent": {
    "model": "auto",
    "timeout_ms": 60000
  },
  "headless": {
    "output_format": "json",
    "force_mode": true
  }
}
```

### After (Official Schema)
```json
{
  "model": "auto",
  "timeout": 60000,
  "outputFormat": "json",
  "force": true
}
```

## References

- [Cursor CLI Configuration Reference](https://cursor.com/docs/cli/reference/configuration)
- [Cursor CLI Documentation](https://cursor.com/docs/cli)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)

## Best Practices

1. **Use Official Schema**: Stick to the official Cursor CLI configuration schema
2. **Custom Extensions**: Only add custom fields when necessary and document them
3. **Environment Overrides**: Use environment variables for runtime overrides
4. **Validation**: Always validate JSON syntax before committing
5. **Documentation**: Document any custom extensions or deviations
