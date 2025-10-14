# MCP GitHub Workflow Fixer Server

A Model Context Protocol (MCP) server that analyzes and fixes failing GitHub workflows using AI-powered analysis.

## Features

- **Workflow Failure Analysis**: Automatically identifies common issues in GitHub Actions workflows
- **Intelligent Fix Suggestions**: Provides targeted fixes for dependency, timeout, and environment issues
- **Workflow Monitoring**: Real-time status tracking and reporting
- **Automated Remediation**: Apply fixes directly through MCP tools
- **Comprehensive Reporting**: Generate detailed analysis reports with actionable insights

## Installation

### Prerequisites

- Python 3.8+
- GitHub Personal Access Token with `repo` and `workflow` permissions

### Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up GitHub token:
```bash
export GITHUB_TOKEN="your_github_token_here"
```

## Usage

### Running the MCP Server

```bash
python github_workflow_fixer.py
```

### MCP Tools Available

#### `analyze_repository_workflows`
Analyze GitHub workflow failures and suggest fixes.

**Parameters:**
- `repository`: GitHub repository in format 'owner/repo'
- `github_token`: (Optional) GitHub token, defaults to GITHUB_TOKEN env var
- `limit`: Maximum workflow runs to analyze (default: 20)

#### `get_workflow_status`
Get current workflow status for a repository.

**Parameters:**
- `repository`: GitHub repository in format 'owner/repo'
- `github_token`: (Optional) GitHub token
- `branch`: (Optional) Specific branch to check

#### `fix_workflow_issues`
Apply automated fixes to common workflow issues.

**Parameters:**
- `repository`: GitHub repository in format 'owner/repo'
- `github_token`: (Optional) GitHub token
- `dry_run`: If true, show changes without applying (default: true)
- `max_fixes`: Maximum number of fixes to apply (default: 3)

#### `rerun_failed_workflows`
Trigger reruns of failed workflows to check for transient issues.

**Parameters:**
- `repository`: GitHub repository in format 'owner/repo'
- `github_token`: (Optional) GitHub token
- `max_reruns`: Maximum workflows to rerun (default: 5)

## Configuration

### Environment Variables

- `GITHUB_TOKEN`: GitHub Personal Access Token (required)
- `LOG_LEVEL`: Logging level (default: INFO)

### Supported Issue Types

The server automatically detects and fixes:

1. **Dependency Issues**: npm/pip installation failures
2. **Timeout Issues**: Workflow timeouts and deadline exceeded errors
3. **Permission Issues**: Access denied or insufficient permissions
4. **Environment Issues**: Missing commands or PATH problems

## Integration with Cursor

To integrate with Cursor IDE:

1. Add to your `.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "github-workflow-fixer": {
      "command": "python",
      "args": ["/path/to/github_workflow_fixer.py"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

2. Restart Cursor to load the MCP server

## Error Handling

The server includes comprehensive error handling:

- **Rate Limiting**: Automatic retry with exponential backoff
- **Authentication**: Clear error messages for invalid tokens
- **Network Issues**: Timeout handling and connection recovery
- **Invalid Input**: Parameter validation with helpful error messages

## Security Considerations

- GitHub tokens are handled securely and never logged
- All API calls use HTTPS with certificate validation
- No sensitive data is stored locally
- Dry-run mode available for all fix operations

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is licensed under the Apache 2.0 License - see the LICENSE file for details.

## Support

For issues and questions:

- Open an issue on GitHub
- Check the logs in `mcp_workflow_fixer.log`
- Ensure your GitHub token has the required permissions

