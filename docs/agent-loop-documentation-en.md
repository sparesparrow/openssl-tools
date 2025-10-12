# Agent-Loop.sh - Complete Documentation

## Overview
Robust CI orchestration with planning and validation using Cursor-Agent for OpenSSL modernization. This script combines traditional CI operations with AI-assisted planning for automated GitHub workflow repair.

## Basic Usage

### Two Main Modes:

**Planning Mode** - Analysis and plan creation:
```bash
./agent-loop.sh "Diagnose and plan for PR #6" planning
```

**Execution Mode** - Validation and execution:
```bash
./agent-loop.sh "Fix all failed workflows" execution
```

## Environment Configuration

### Basic Parameters:
- `PR_NUMBER=6` - Pull request number
- `PR_BRANCH=simplify-openssl-build` - PR branch name
- `REPO=sparesparrow/openssl-tools` - Repository
- `MAX_ITERATIONS=12` - Maximum iterations
- `INTERVAL=60` - Interval between iterations (seconds)

### Cursor-Agent Configuration (REQUIRED for AI features):
- `CURSOR_API_KEY` - **REQUIRED** - API key from cursor.com/settings/api
- `AGENT_TIMEOUT_SEC=600` - Agent timeout (seconds)
- `CURSOR_CONFIG_FILE=.cursor/cli-config.json` - Cursor configuration path
- `CURSOR_MCP_CONFIG=mcp.json` - MCP configuration for advanced features
- `CURSOR_AGENT_CONFIG=.cursor/agents/ci-repair-agent.yml` - Specific agent configuration

### Advanced Settings:
- `LOG_LEVEL=info` - Logging level (debug|info|warn|error)
- `USE_STREAMING=false` - Streaming mode for real-time progress tracking
- `AGENT_MODEL=auto` - AI agent model (auto selects best available)
- `MCP_ENABLED=true` - Enable MCP support for access to additional tools

## Cursor API Key Setup

### Getting API Key:
1. Go to [cursor.com/settings/api](https://cursor.com/settings/api)
2. Sign in to your Cursor account
3. Click "Create new API key"
4. Copy the key (displayed only once!)

### Environment Setup:
```bash
export CURSOR_API_KEY="your-api-key-here"
```

### Configuration Verification:
```bash
# Verify cursor-agent installation
cursor-agent --version

# Test connection
echo "Test connection" | cursor-agent -p
```

## Cursor-Agent CLI Installation

### Automatic Installation:
```bash
curl https://cursor.com/install -fsS | bash
```

### Manual PATH Setup:
```bash
# For bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# For zsh
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc  
source ~/.zshrc
```

### Installation Verification:
```bash
cursor-agent --version
```

## Model Context Protocol (MCP) Configuration

### What is MCP:
MCP is an open standard for connecting AI applications to external systems and data. It enables AI agents to access:
- Workflow history and analysis
- Repository structure and metadata  
- Build logs and error analysis
- GitHub API functions

### Basic MCP Configuration (`mcp.json`):
```json
{
  "mcpServers": {
    "github": {
      "command": "mcp-server-github",
      "args": ["--token", "your-github-token"]
    },
    "filesystem": {
      "command": "mcp-server-filesystem", 
      "args": ["--root", "."]
    }
  }
}
```

### Advanced Configuration (`.cursor/cli-config.json`):
```json
{
  "model": "claude-3.5-sonnet",
  "timeout": 600000,
  "mcp": {
    "enabled": true,
    "servers": ["github", "filesystem"]
  }
}
```

## Usage Examples

### 1. Basic CI Repair for PR #6:
```bash
export CURSOR_API_KEY="sk-..."
./agent-loop.sh "Ensure all PR #6 workflows are green with minimal changes" execution
```

### 2. Detailed Analysis with Debug Logging:
```bash
export LOG_LEVEL=debug
export CURSOR_API_KEY="sk-..."
./agent-loop.sh "Analyze failed Conan 2.0 workflows and create repair plan" planning
```

### 3. Streaming Mode for Real-time Monitoring:
```bash
export USE_STREAMING=true
export CURSOR_API_KEY="sk-..."
./agent-loop.sh "Fix OpenSSL modernization compatibility issues" execution
```

### 4. Specific Workflow Repairs:
```bash
export PR_NUMBER=6
export PR_BRANCH=simplify-openssl-build
./agent-loop.sh "Fix binary-first-ci.yml and conan-ci-enhanced.yml failures" execution
```

## Automatic Actions Performed by Script

### GitHub Workflow Operations:
- **rerun:ID** - Rerun failed workflow run
- **approve:ID** - Approve workflow requiring manual approval  
- **apply-patch:filename** - Apply unified diff patch to file
- **enable-workflow:path** - Move workflow from workflows-disabled/ to workflows/
- **disable-workflow:path** - Move workflow from workflows/ to workflows-disabled/
- **rerun-failed-workflows** - Rerun all currently failed workflow runs

### AI Planning and Validation:
- Analysis of workflow failures and their causes
- Creation of minimal, safe YAML patches
- Action prioritization (approve > rerun > patch)
- YAML syntax validation before application
- Risk checking and Conan 2.0 compatibility

### Git Operations:
- Automatic commit of changes with descriptive commit messages
- Push to PR branch with retry logic
- Branch management and checkout

## Output JSON Formats

### Plan from Planning Mode:
```json
{
  "batches": [
    {
      "name": "batch-1-rerun-failed",
      "actions": [
        "rerun:12345", 
        "approve:67890",
        "apply-patch:workflow-fix.yml"
      ]
    }
  ],
  "patches": [
    {
      "filename": ".github/workflows/conan-ci-enhanced.yml",
      "diff": "--- a/.github/workflows/conan-ci-enhanced.yml\n+++ b/.github/workflows/conan-ci-enhanced.yml\n@@ -10,1 +10,1 @@\n-    branches: [main]\n+    branches: [main, simplify-openssl-build]"
    }
  ],
  "stop_condition": "all_green",
  "notes": "Added PR branch to workflow triggers for proper CI execution"
}
```

### Validation from Execution Mode:
```json
{
  "valid": true,
  "issues": [],
  "corrected_patches": [],
  "recommendations": [
    "Add concurrency group to prevent job cancellation",
    "Consider workflow caching for faster builds"
  ]
}
```

## System Requirements

### Required Tools:
- `gh` (GitHub CLI) - for GitHub API operations
- `jq` (JSON processor) - for JSON response processing  
- `git` - for repository operations
- `curl` - for HTTP requests
- `timeout` - for timeout control
- `cursor-agent` (optional) - for AI features

### Access Rights:
- GitHub personal access token with repository access
- Cursor API key for AI functionality  
- Write access to target repository (sparesparrow/openssl-tools)

### GitHub CLI Verification:
```bash
# Login
gh auth login

# Test repository access
gh repo view sparesparrow/openssl-tools

# Test workflow operations
gh run list --repo sparesparrow/openssl-tools --limit 5
```

## Troubleshooting and Problem Solving

### Common Errors and Solutions:

**"CURSOR_API_KEY not set":**
```bash
# Get key from cursor.com/settings/api
export CURSOR_API_KEY="your-key-from-cursor-settings"
```

**"cursor-agent command not found":**
```bash
# Install cursor-agent
curl https://cursor.com/install -fsS | bash
# Then restart terminal or:
source ~/.bashrc  # or ~/.zshrc
```

**"JSON parsing errors from agent":**
```bash
# Debug mode for detailed logs
export LOG_LEVEL=debug
./agent-loop.sh "task" execution 2>&1 | tee debug.log
```

**"Permission denied" during git operations:**
```bash
# Verify GitHub authentication
gh auth status
# Check SSH keys
ssh -T git@github.com
```

**"No workflow runs found":**
```bash
# Check you're on correct branch
git branch
git checkout simplify-openssl-build
# Verify PR existence
gh pr view 6
```

### Debug Mode and Logging:

**Enable Debug Logging:**
```bash
export LOG_LEVEL=debug
./agent-loop.sh "task" execution 2>&1 | tee -a agent-debug.log
```

**Log Analysis:**
```bash
# Filter error messages
grep '"level":"error"' agent-debug.log | jq '.'

# Monitor agent communication
grep '"level":"debug"' agent-debug.log | grep -i agent | jq '.msg'
```

### Performance Optimization:

**Fast Iterations:**
```bash
export MAX_ITERATIONS=5
export INTERVAL=30
```

**Streaming for Real-time Feedback:**
```bash
export USE_STREAMING=true
```

**Timeout Configuration:**
```bash
export AGENT_TIMEOUT_SEC=300  # For faster response
```

## Advanced Usage

### Custom Agent Configuration (`.cursor/agents/ci-repair-agent.yml`):
```yaml
name: ci-repair-agent
description: Specialized agent for CI/CD workflow repairs
model: claude-3.5-sonnet
temperature: 0.1
max_tokens: 4000
system_prompt: |
  You are a CI/CD expert specializing in GitHub Actions and OpenSSL build systems.
  Focus on minimal, safe changes that preserve functionality while fixing failures.
```

### Batch Processing Multiple PRs:
```bash
for pr in 5 6 7; do
  export PR_NUMBER=$pr
  ./agent-loop.sh "Fix PR #$pr workflows" execution
  sleep 60
done
```

### CI/CD Pipeline Integration:
```bash
# In GitHub Actions workflow
- name: Run agent-loop
  run: |
    export CURSOR_API_KEY="${{ secrets.CURSOR_API_KEY }}"
    ./agent-loop.sh "Automated CI repair" execution
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## MCP (Model Context Protocol) Integration

### Overview
MCP is an open standard for connecting AI applications to external systems and data. In the context of `agent-loop.sh`, it enables:

- **Automatic connection** to MCP servers
- **Access to tools** from multiple servers simultaneously
- **Implementation of patterns** from [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)
- **Support for workflow pause/resume** signals

### MCP Server Flow
```
User->>Client: Send query
Client<<->>MCP_Server: Get available tools
Client->>Claude: Send query with tool descriptions
Claude-->>Client: Decide tool execution
Client->>MCP_Server: Request tool execution
MCP_Server->>Tools: Execute chosen tools
Tools-->>MCP_Server: Return results
MCP_Server-->>Client: Send results
Client->>Claude: Send tool results
Claude-->>Client: Provide final response
Client-->>User: Display response
```

### MCP Best Practices

1. **Error Handling**
   - Use type system for explicit error modeling
   - Wrap external calls in `try-catch` blocks
   - Provide clear and meaningful error messages
   - Handle network timeouts and connection issues

2. **Security**
   - Store API keys securely in `local.properties`, environment variables, or secret managers
   - Validate all external responses
   - Be careful with permissions and trust boundaries

### MCP Troubleshooting

**Server Path Issues:**
```bash
# Relative path
java -jar build/libs/client.jar ./server/build/libs/server.jar

# Absolute path
java -jar build/libs/client.jar /Users/username/projects/mcp-server/build/libs/server.jar

# Windows path
java -jar build/libs/client.jar C:/projects/mcp-server/build/libs/server.jar
```

**Response Timing:**
- First response may take up to 30 seconds
- This is normal during server initialization
- Subsequent responses are typically faster
- Don't interrupt the process during initial waiting

**Common Error Messages:**
- `Connection refused`: Ensure server is running and path is correct
- `Tool execution failed`: Verify required environment variables are set
- `ANTHROPIC_API_KEY is not set`: Check environment variables

## Architecture and Design

### Main Components:

1. **Configuration Management** - Loading and validation of configuration
2. **Cursor Agent Integration** - AI-powered planning and validation
3. **GitHub API Operations** - Workflow management and monitoring
4. **JSON Processing** - Robust AI response processing
5. **Error Handling** - Graceful fallback and recovery
6. **Logging System** - Structured logging with various levels

### Design Patterns:

- **Strategy Pattern** - Different modes (planning vs execution)
- **Template Method** - Standardized workflow for all operations
- **Observer Pattern** - Real-time workflow status monitoring
- **Command Pattern** - Batch action execution
- **Factory Pattern** - Dynamic prompt and configuration creation

This script represents an advanced tool for CI/CD operation automation using modern AI technologies for intelligent decision-making and workflow repair.
