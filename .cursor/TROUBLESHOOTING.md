# Cursor CLI Integration Troubleshooting Guide

This guide helps resolve common issues with the Cursor CLI integration in `agent-loop.sh`.

## Common Issues and Solutions

### 1. CURSOR_API_KEY Not Set

**Error:**
```
{"level":"error","msg":"CURSOR_API_KEY not set - cursor-agent requires a valid API key"}
```

**Solution:**
1. Get your API key from [Cursor Settings](https://cursor.com/settings/api)
2. Set the environment variable:
   ```bash
   export CURSOR_API_KEY=your_api_key_here
   ```
3. Or add it to your shell profile (`~/.bashrc`, `~/.zshrc`):
   ```bash
   echo 'export CURSOR_API_KEY=your_api_key_here' >> ~/.bashrc
   source ~/.bashrc
   ```

### 2. Python3 ENOENT Error

**Error:**
```
Error (unhandledRejection): spawn python3 ENOENT
```

**Causes:**
- MCP server trying to run `python3` but it's not found
- MCP package not installed
- Invalid MCP server configuration

**Solutions:**

#### Option A: Disable MCP (Quick Fix)
Edit `.cursor/cli-config.json`:
```json
{
  "mcp": {
    "enabled": false,
    ...
  }
}
```

#### Option B: Install MCP Package
```bash
# Using pipx (recommended)
pipx install mcp

# Or using pip in virtual environment
python3 -m venv venv
source venv/bin/activate
pip install mcp
```

#### Option C: Use Simple CI Server
The simple server doesn't require MCP package:
```bash
# Test the simple server
python3 scripts/mcp/ci-server-simple.py get_recent_commits 5
```

### 3. Invalid JSON Response from Agent

**Error:**
```
{"level":"error","msg":"Invalid JSON response from agent"}
```

**Causes:**
- Cursor-agent output format issues
- Stderr mixing with stdout
- Agent timeout or failure

**Solutions:**

#### Check Agent Output Manually
```bash
# Test cursor-agent directly
CURSOR_API_KEY=your_key cursor-agent -p --force --output-format json "Test prompt"
```

#### Enable Debug Logging
```bash
LOG_LEVEL=debug ./agent-loop.sh
```

#### Check Agent Version
```bash
cursor-agent --version
```

### 4. MCP Server Connection Issues

**Error:**
```
Error: mcp package not found. Install with: pip install mcp
```

**Solutions:**

#### Install MCP Package
```bash
pipx install mcp
```

#### Use Simple Server Instead
Update `.cursor/mcp-servers.json`:
```json
{
  "mcpServers": {
    "openssl-ci-simple": {
      "command": "python3",
      "args": ["${workspaceFolder}/scripts/mcp/ci-server-simple.py"],
      "cwd": "${workspaceFolder}"
    }
  }
}
```

### 5. Configuration File Issues

**Error:**
```
{"level":"warn","msg":"jq not found, using default configuration"}
```

**Solution:**
Install jq for JSON parsing:
```bash
# Ubuntu/Debian
sudo apt install jq

# macOS
brew install jq

# Or disable config loading by setting:
export CURSOR_CONFIG_FILE=""
```

### 6. GitHub CLI Issues

**Error:**
```
gh: command not found
```

**Solution:**
Install GitHub CLI:
```bash
# Ubuntu/Debian
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh

# macOS
brew install gh

# Authenticate
gh auth login
```

## Testing the Integration

### 1. Test Configuration Loading
```bash
LOG_LEVEL=debug ./agent-loop.sh "Test" execution 2>&1 | head -20
```

Look for:
```
{"level":"info","msg":"Loading Cursor CLI configuration from .cursor/cli-config.json"}
{"level":"debug","msg":"Loaded config: model=auto, timeout=60s, mcp=false"}
```

### 2. Test Cursor-Agent
```bash
CURSOR_API_KEY=your_key cursor-agent -p --force --output-format json "Test prompt"
```

### 3. Test MCP Server
```bash
# Test simple server
python3 scripts/mcp/ci-server-simple.py get_recent_commits 5

# Test MCP server (if MCP package installed)
python3 scripts/mcp/ci-server.py
```

### 4. Test Full Integration
```bash
CURSOR_API_KEY=your_key ./agent-loop.sh "Test run" execution
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CURSOR_API_KEY` | Cursor API key (required) | - |
| `CURSOR_CONFIG_FILE` | Path to CLI config | `.cursor/cli-config.json` |
| `CURSOR_MCP_CONFIG` | Path to MCP config | `.cursor/mcp-servers.json` |
| `CURSOR_AGENT_CONFIG` | Path to agent config | `.cursor/agents/ci-repair-agent.yml` |
| `LOG_LEVEL` | Logging level | `info` |
| `AGENT_TIMEOUT_SEC` | Agent timeout | `60` |

## Configuration Files

### Required Files
- `.cursor/cli-config.json` - Main configuration
- `.cursor/mcp-servers.json` - MCP server config (if MCP enabled)

### Optional Files
- `.cursor/agents/ci-repair-agent.yml` - Agent behavior
- `.cursor/rules/` - Rule files for guidance

## Fallback Behavior

The script gracefully falls back when components are missing:

1. **No CURSOR_API_KEY** → Simple mode (rerun/approve only)
2. **No MCP package** → Disable MCP, use basic prompts
3. **No jq** → Use default configuration
4. **No cursor-agent** → Simple mode only

## Getting Help

### Check Logs
```bash
LOG_LEVEL=debug ./agent-loop.sh 2>&1 | tee debug.log
```

### Test Individual Components
```bash
# Test GitHub CLI
gh run list --limit 5

# Test cursor-agent
CURSOR_API_KEY=your_key cursor-agent --help

# Test MCP server
python3 scripts/mcp/ci-server-simple.py --help
```

### Common Commands
```bash
# Run with debug logging
LOG_LEVEL=debug ./agent-loop.sh

# Run with custom config
CURSOR_CONFIG_FILE=.cursor/custom-config.json ./agent-loop.sh

# Run in planning mode
./agent-loop.sh "Analyze workflows" planning

# Run with MCP disabled
# Edit .cursor/cli-config.json: "enabled": false
```

## Performance Tips

1. **Use Simple Mode** for basic rerun/approve operations
2. **Disable MCP** if you don't need enhanced context
3. **Reduce timeout** for faster iterations: `AGENT_TIMEOUT_SEC=30`
4. **Use streaming** for long operations: `USE_STREAMING=true`

## Security Notes

- Never commit CURSOR_API_KEY to git
- Use environment variables or secure secret management
- Regularly rotate API keys
- Review MCP server permissions

## Version Compatibility

- **cursor-agent**: Latest version recommended
- **GitHub CLI**: v2.0+ required
- **Python**: 3.8+ for MCP servers
- **jq**: Any recent version

## Still Having Issues?

1. Check the [Cursor CLI Documentation](https://cursor.com/docs/cli)
2. Review the [MCP Documentation](https://modelcontextprotocol.io/)
3. Test with minimal configuration
4. Enable debug logging and review output
5. Check GitHub CLI authentication: `gh auth status`
