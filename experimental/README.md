# GitHub Workflow Fixer MCP Server

A powerful Model Context Protocol server that provides AI assistants with capabilities to analyze, diagnose, and automatically fix failing GitHub workflows in any repository.

## 🚀 Features

- **Intelligent Analysis**: Analyzes workflow failures and identifies common patterns
- **Automated Fixes**: Suggests and applies fixes for common GitHub Actions issues
- **Status Monitoring**: Real-time workflow status tracking and reporting  
- **Batch Operations**: Rerun multiple failed workflows with a single command
- **Security First**: Secure token handling with rate limiting and retry logic
- **Enterprise Ready**: Comprehensive logging, error handling, and monitoring

## 📋 Prerequisites

- Python 3.8 or higher
- GitHub Personal Access Token with `actions:read` and `actions:write` permissions
- Repository access permissions for target repositories

## 🔧 Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
export GITHUB_TOKEN="your_github_personal_access_token_here"
export LOG_LEVEL="INFO"  # Optional: DEBUG, INFO, WARNING, ERROR
```

### 3. Test the Server

```bash
python github_workflow_fixer_mcp.py
```

## 🎯 Usage Examples

### With Claude Desktop

Add to your Claude Desktop MCP configuration:

```json
{
  "mcpServers": {
    "github-workflow-fixer": {
      "command": "python",
      "args": ["path/to/github_workflow_fixer_mcp.py"],
      "env": {
        "GITHUB_TOKEN": "your_token_here"
      }
    }
  }
}
```

### With MCP Clients

The server exposes the following tools:

#### 1. Analyze Repository Workflows
```python
# Analyzes recent workflow runs and suggests fixes
analyze_repository_workflows(
    repository="owner/repo-name",
    limit=20
)
```

#### 2. Get Workflow Status  
```python
# Get current workflow status for a repository
get_workflow_status(
    repository="owner/repo-name", 
    branch="main"  # optional
)
```

#### 3. Fix Workflow Issues
```python
# Apply automated fixes (dry-run by default)
fix_workflow_issues(
    repository="owner/repo-name",
    dry_run=True,  # Set to False to actually apply fixes
    max_fixes=3
)
```

#### 4. Rerun Failed Workflows
```python
# Rerun failed workflows to test if issues are transient
rerun_failed_workflows(
    repository="owner/repo-name",
    max_reruns=5
)
```

### Resources Available

- **workflow://status/{repository}** - Real-time workflow status data

### Prompts Available  

- **workflow_troubleshooting_guide** - Expert guidance for debugging workflows

## 🔐 Security Considerations

- **Token Security**: Store GitHub tokens securely using environment variables
- **Rate Limiting**: Built-in GitHub API rate limiting with exponential backoff
- **Input Validation**: All repository names and parameters are validated
- **Minimal Permissions**: Only requires necessary GitHub API permissions
- **Audit Logging**: All actions are logged for security auditing

## 🚀 Advanced Usage

### Running as HTTP Server

```bash
python github_workflow_fixer_mcp.py --http
```

This starts an HTTP server on port 8000 for web-based MCP clients.

### Custom Configuration

The server supports various environment variables:

- `GITHUB_TOKEN` - GitHub Personal Access Token (required)
- `LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)
- `GITHUB_API_BASE_URL` - Custom GitHub API base URL for GitHub Enterprise

## 🛠️ Architecture

The server is built using:

- **FastMCP**: High-level MCP server framework
- **httpx**: Async HTTP client for GitHub API calls  
- **tenacity**: Retry logic with exponential backoff
- **Jinja2**: Template engine for generating reports
- **Pydantic**: Data validation and settings management

## 📊 Monitoring & Logging

All operations are logged with structured logging:

```
2025-01-11 15:30:45 - github_workflow_fixer - INFO - Retrieved 15 workflow runs
2025-01-11 15:30:46 - github_workflow_fixer - INFO - Found 3 failed runs requiring attention
2025-01-11 15:30:47 - github_workflow_fixer - INFO - Generated 2 suggested fixes
```

Logs are written to both console and `mcp_workflow_fixer.log` file.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality  
4. Ensure all tests pass
5. Submit a pull request

## 📜 License

MIT License - see LICENSE file for details.

## 🔗 Related Projects

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [FastMCP](https://github.com/pydantic/fastmcp) 
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

---

*Built with ❤️ for the MCP community*
