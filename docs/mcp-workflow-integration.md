# MCP Workflow Integration Guide

This guide explains how to use the GitHub Workflow Fixer MCP server integration in the OpenSSL Tools project.

## Overview

The MCP (Model Context Protocol) server integration provides intelligent workflow analysis and automated fixing capabilities for GitHub Actions workflows. It combines AI-powered analysis with existing workflow automation tools.

## Components

### 1. MCP Server (`scripts/mcp/github_workflow_fixer_mcp.py`)

A FastMCP-based server that provides:
- **Intelligent Analysis**: Analyzes workflow failures and identifies patterns
- **Automated Fixes**: Suggests and applies fixes for common issues
- **Status Monitoring**: Real-time workflow status tracking
- **Batch Operations**: Rerun multiple failed workflows

### 2. Unified Workflow Manager (`scripts/unified_workflow_manager.py`)

A wrapper that combines:
- Existing workflow automation tools (WorkflowManager, WorkflowMonitor, etc.)
- MCP server capabilities
- Unified interface for both approaches

### 3. Cursor IDE Integration

The MCP server is configured in `.cursor/mcp.json` for local development use.

## Usage

### Local Development with Cursor

1. **Start Cursor IDE** with the project open
2. **Verify MCP server** appears in available tools
3. **Use MCP tools** directly in Cursor for workflow analysis

Available MCP tools:
- `analyze_repository_workflows` - Analyze workflow failures
- `get_workflow_status` - Get current workflow status
- `fix_workflow_issues` - Apply automated fixes
- `rerun_failed_workflows` - Rerun failed workflows

### Command Line Usage

#### Basic Analysis

```bash
# Analyze recent workflow failures
python scripts/unified_workflow_manager.py --repo sparesparrow/openssl-tools --action analyze

# Monitor current status
python scripts/unified_workflow_manager.py --repo sparesparrow/openssl-tools --action monitor

# Comprehensive analysis and fixing
python scripts/unified_workflow_manager.py --repo sparesparrow/openssl-tools --action analyze-and-fix
```

#### Advanced Options

```bash
# Analyze with custom limit
python scripts/unified_workflow_manager.py --repo sparesparrow/openssl-tools --action analyze --limit 50

# Apply fixes (dry run by default)
python scripts/unified_workflow_manager.py --repo sparesparrow/openssl-tools --action fix --dry-run

# Actually apply fixes
python scripts/unified_workflow_manager.py --repo sparesparrow/openssl-tools --action fix --dry-run=false

# Rerun failed workflows
python scripts/unified_workflow_manager.py --repo sparesparrow/openssl-tools --action recover --max-reruns 10

# Save output to file
python scripts/unified_workflow_manager.py --repo sparesparrow/openssl-tools --action analyze --output analysis-report.md
```

### Programmatic Usage

```python
import asyncio
from scripts.unified_workflow_manager import UnifiedWorkflowManager

async def main():
    # Initialize manager
    manager = UnifiedWorkflowManager('sparesparrow/openssl-tools')
    
    # Analyze workflows
    analysis = await manager.analyze_workflows(limit=20)
    print(analysis)
    
    # Monitor status
    status = manager.monitor_status()
    print(status)
    
    # Apply fixes (dry run)
    fixes = await manager.fix_issues(dry_run=True, max_fixes=3)
    print(fixes)
    
    # Comprehensive analysis
    report = await manager.analyze_and_fix(limit=20, dry_run=True)
    print(report)

asyncio.run(main())
```

## CI/CD Integration

### Automatic Analysis

The `conan-ci.yml` workflow includes a `workflow-analysis` job that:

1. **Triggers on failure** or manual dispatch
2. **Installs MCP dependencies**
3. **Runs intelligent analysis** using the unified manager
4. **Posts results to PR** as a comment

### Workflow Configuration

The analysis job is configured in `.github/workflows/conan-ci.yml`:

```yaml
workflow-analysis:
  needs: compile-changes
  if: failure() || github.event_name == 'workflow_dispatch'
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
        cache: 'pip'
    - name: Install MCP dependencies
      run: |
        pip install -r scripts/mcp/requirements.txt
        pip install -r requirements.txt
    - name: Analyze workflow failures
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      run: |
        python -c "
        import asyncio
        import sys
        sys.path.insert(0, 'scripts')
        from unified_workflow_manager import UnifiedWorkflowManager
        
        async def analyze():
            manager = UnifiedWorkflowManager('${{ github.repository }}')
            report = await manager.analyze_and_fix(limit=10)
            print(report)
            with open('/tmp/workflow-analysis.md', 'w') as f:
                f.write(report)
        
        asyncio.run(analyze())
        "
    - name: Post analysis to PR
      if: github.event_name == 'pull_request'
      uses: actions/github-script@v7
      with:
        script: |
          const fs = require('fs');
          try {
            const report = fs.readFileSync('/tmp/workflow-analysis.md', 'utf8');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `## 🔧 Workflow Analysis Report\n\n${report}`
            });
          } catch (error) {
            console.log('Could not read analysis report:', error.message);
          }
```

## Available MCP Tools

### 1. analyze_repository_workflows

Analyzes GitHub workflow failures and suggests fixes.

**Parameters:**
- `repository`: GitHub repository in format 'owner/repo'
- `github_token`: GitHub personal access token (optional)
- `limit`: Maximum number of workflow runs to analyze (default: 20)

**Returns:** Detailed analysis report with suggested fixes

### 2. get_workflow_status

Gets current status of workflows for a repository.

**Parameters:**
- `repository`: GitHub repository in format 'owner/repo'
- `github_token`: GitHub personal access token (optional)
- `branch`: Specific branch to check (optional)

**Returns:** Current workflow status summary

### 3. fix_workflow_issues

Applies automated fixes to common workflow issues.

**Parameters:**
- `repository`: GitHub repository in format 'owner/repo'
- `github_token`: GitHub personal access token (optional)
- `dry_run`: If True, only show what would be changed (default: True)
- `max_fixes`: Maximum number of fixes to apply (default: 3)

**Returns:** Results of fix application

### 4. rerun_failed_workflows

Reruns failed workflows to test if issues are transient.

**Parameters:**
- `repository`: GitHub repository in format 'owner/repo'
- `github_token`: GitHub personal access token (optional)
- `max_reruns`: Maximum number of workflows to rerun (default: 5)

**Returns:** Results of workflow reruns

## Configuration

### Environment Variables

- `GITHUB_TOKEN`: GitHub Personal Access Token (required)
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

### Cursor Configuration

The MCP server is configured in `.cursor/mcp.json`:

```json
"github-workflow-fixer": {
  "command": "${workspaceFolder}/venv/bin/python",
  "args": ["${workspaceFolder}/scripts/mcp/github_workflow_fixer_mcp.py"],
  "cwd": "${workspaceFolder}",
  "env": {
    "GITHUB_TOKEN": "${GITHUB_TOKEN}",
    "LOG_LEVEL": "INFO"
  }
}
```

And enabled in `.cursor/cli-config.json`:

```json
"mcp": {
  "enabled": true,
  "servers": [
    "github",
    "openssl-ci",
    "openssl-database",
    "openssl-build",
    "openssl-security",
    "github-workflow-fixer"
  ]
}
```

## Troubleshooting

### Common Issues

1. **MCP server not starting**
   - Check that `GITHUB_TOKEN` is set
   - Verify Python dependencies are installed
   - Check logs in `mcp_workflow_fixer.log`

2. **Analysis fails**
   - Verify repository format is 'owner/repo'
   - Check GitHub token permissions
   - Ensure repository is accessible

3. **Cursor integration not working**
   - Restart Cursor IDE
   - Check `.cursor/mcp.json` configuration
   - Verify MCP server is in the servers list

### Validation Script

Use the validation script to check configuration:

```bash
python scripts/validate-mcp-config.py
```

This script validates:
- MCP server dependencies are installed
- GitHub token is configured
- MCP server can be started successfully
- Connection to GitHub API works

### Logs

MCP server logs are written to:
- Console output
- `mcp_workflow_fixer.log` file

Check these logs for detailed error information.

## Examples

### Example 1: Basic Workflow Analysis

```bash
# Analyze recent workflow failures
python scripts/unified_workflow_manager.py \
  --repo sparesparrow/openssl-tools \
  --action analyze \
  --limit 10
```

### Example 2: Fix Common Issues

```bash
# Show what would be fixed (dry run)
python scripts/unified_workflow_manager.py \
  --repo sparesparrow/openssl-tools \
  --action fix \
  --dry-run \
  --max-fixes 5

# Actually apply fixes
python scripts/unified_workflow_manager.py \
  --repo sparesparrow/openssl-tools \
  --action fix \
  --dry-run=false \
  --max-fixes 3
```

### Example 3: Comprehensive Analysis

```bash
# Full analysis with all components
python scripts/unified_workflow_manager.py \
  --repo sparesparrow/openssl-tools \
  --action analyze-and-fix \
  --limit 20 \
  --output comprehensive-report.md
```

### Example 4: Rerun Failed Workflows

```bash
# Rerun up to 10 failed workflows
python scripts/unified_workflow_manager.py \
  --repo sparesparrow/openssl-tools \
  --action recover \
  --max-reruns 10
```

## Security Considerations

- **Token Security**: Store GitHub tokens securely using environment variables
- **Rate Limiting**: Built-in GitHub API rate limiting with exponential backoff
- **Input Validation**: All repository names and parameters are validated
- **Minimal Permissions**: Only requires necessary GitHub API permissions
- **Audit Logging**: All actions are logged for security auditing

## Performance

- **Async Operations**: All GitHub API calls are asynchronous
- **Connection Pooling**: HTTP client uses connection pooling
- **Caching**: Results are cached where appropriate
- **Rate Limiting**: Respects GitHub API rate limits

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Related Documentation

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [FastMCP Documentation](https://github.com/pydantic/fastmcp)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [OpenSSL Tools CI/CD Guide](.github/ci.md)
