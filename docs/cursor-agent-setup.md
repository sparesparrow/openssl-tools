# Cursor Agent Setup Guide

This guide explains how to set up the Cursor Agent for AI-powered CI repair automation in the `agent-loop.sh` script.

## Overview

The `agent-loop.sh` script can run in two modes:

1. **Simple Mode** (default): Automatically reruns failed workflows and approves action-required jobs
2. **AI-Powered Mode**: Uses Cursor Agent to analyze failures and propose intelligent fixes

## Prerequisites

### 1. Install Cursor CLI

The Cursor CLI must be installed and available in your PATH:

```bash
# Install Cursor CLI (if not already installed)
# Follow instructions at: https://cursor.com/docs/cli
```

### 2. Get Cursor API Key

1. Go to [Cursor Settings](https://cursor.com/settings/api)
2. Sign in to your Cursor account
3. Generate a new API key
4. Copy the API key

### 3. Set Environment Variable

Set the `CURSOR_API_KEY` environment variable:

```bash
# Option 1: Export for current session
export CURSOR_API_KEY="your-api-key-here"

# Option 2: Add to shell profile (permanent)
echo 'export CURSOR_API_KEY="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc

# Option 3: Use .env file (recommended for development)
echo 'CURSOR_API_KEY="your-api-key-here"' >> .env
```

## Usage

### Simple Mode (No API Key)

```bash
# Run without API key - uses simple rerun/approve logic
BRANCH=simplify-openssl-build ./agent-loop.sh
```

**Output:**
```
{"level":"warn","msg":"cursor-agent found but CURSOR_API_KEY not set, running in simple mode"}
{"level":"info","msg":"To enable AI-powered planning, set CURSOR_API_KEY environment variable"}
{"level":"info","msg":"Get your API key from: https://cursor.com/settings/api"}
```

### AI-Powered Mode (With API Key)

```bash
# Set API key and run with AI planning
export CURSOR_API_KEY="your-api-key-here"
BRANCH=simplify-openssl-build ./agent-loop.sh
```

**Output:**
```
{"level":"info","msg":"cursor-agent available with API key - AI-powered planning enabled"}
{"level":"info","msg":"Running cursor-agent in headless mode (mode=planning, model=auto, timeout=60s, mcp=false)"}
```

## Configuration

### Cursor CLI Configuration

The script uses configuration from `.cursor/cli-config.json`:

```json
{
  "model": "auto",
  "temperature": 0.2,
  "maxTokens": 8192,
  "timeout": 60000,
  "outputFormat": "json",
  "force": true,
  "mcp": {
    "enabled": false,
    "servers": ["github", "openssl-ci"]
  }
}
```

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `CURSOR_API_KEY` | Cursor API key for authentication | - | Yes (for AI mode) |
| `REPO` | GitHub repository (owner/repo) | `sparesparrow/openssl-tools` | No |
| `PR_NUMBER` | Pull request number | `6` | No |
| `PR_BRANCH` | Branch name | `simplify-openssl-build` | No |
| `MAX_ITERATIONS` | Maximum loop iterations | `12` | No |
| `INTERVAL` | Wait time between iterations (seconds) | `60` | No |
| `LOG_LEVEL` | Logging level (debug/info/warn/error) | `info` | No |

## Features

### Simple Mode Features

- ✅ **Automatic Rerun**: Reruns failed and cancelled workflow runs
- ✅ **Auto Approve**: Approves action-required workflow runs
- ✅ **Status Monitoring**: Monitors workflow status and reports progress
- ✅ **Branch Management**: Automatically checks out correct branch
- ✅ **Error Handling**: Graceful handling of GitHub API errors

### AI-Powered Mode Features

All Simple Mode features plus:

- 🤖 **Intelligent Analysis**: AI analyzes failure patterns and root causes
- 🔧 **Smart Fixes**: Proposes targeted fixes for workflow issues
- 📝 **Patch Generation**: Creates unified diff patches for fixes
- 🎯 **Batch Operations**: Groups related actions for efficient execution
- 📊 **Context Awareness**: Uses PR status, commit history, and workflow runs
- 🔄 **Iterative Improvement**: Learns from previous iterations

## Troubleshooting

### Common Issues

#### 1. "cursor-agent found but CURSOR_API_KEY not set"

**Solution:**
```bash
export CURSOR_API_KEY="your-api-key-here"
```

#### 2. "cursor-agent not found"

**Solution:**
```bash
# Install Cursor CLI
# Follow instructions at: https://cursor.com/docs/cli
```

#### 3. "Agent exited with code 1"

**Possible Causes:**
- Invalid API key
- Network connectivity issues
- Cursor service unavailable

**Solution:**
- Verify API key is correct
- Check internet connection
- Try again later

#### 4. "Invalid JSON response from agent"

**Solution:**
- The script automatically falls back to simple mode
- Check Cursor service status
- Verify API key permissions

### Debug Mode

Enable debug logging for detailed information:

```bash
LOG_LEVEL=debug BRANCH=simplify-openssl-build ./agent-loop.sh
```

### Testing API Key

Test your API key directly:

```bash
# Test cursor-agent with simple prompt
timeout 10s cursor-agent -p --force --output-format json "Return only valid JSON: {\"test\": \"success\"}"
```

## Security Considerations

### API Key Security

- **Never commit API keys** to version control
- **Use environment variables** or secure key management
- **Rotate keys regularly** for security
- **Use least privilege** - only necessary permissions

### Best Practices

1. **Use .env files** for local development
2. **Use CI/CD secrets** for automated environments
3. **Monitor API usage** for unexpected activity
4. **Set up alerts** for failed authentication attempts

## Examples

### Basic Usage

```bash
# Simple mode (no API key needed)
./agent-loop.sh

# AI-powered mode (requires API key)
export CURSOR_API_KEY="your-key"
./agent-loop.sh "Fix all failing workflows" execution
```

### Advanced Usage

```bash
# Custom configuration
REPO="myorg/myrepo" \
PR_NUMBER="123" \
PR_BRANCH="feature-branch" \
MAX_ITERATIONS="5" \
INTERVAL="30" \
LOG_LEVEL="debug" \
CURSOR_API_KEY="your-key" \
./agent-loop.sh "Analyze and fix CI issues" planning
```

### CI/CD Integration

```yaml
# GitHub Actions example
- name: Run Agent Loop
  env:
    CURSOR_API_KEY: ${{ secrets.CURSOR_API_KEY }}
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    BRANCH=${{ github.head_ref }} ./agent-loop.sh
```

## Support

For issues with:

- **Cursor CLI**: [Cursor Documentation](https://cursor.com/docs/cli)
- **API Keys**: [Cursor Settings](https://cursor.com/settings/api)
- **Script Issues**: Check this repository's issues

## Changelog

- **v1.0**: Initial implementation with simple mode
- **v1.1**: Added AI-powered mode with Cursor Agent integration
- **v1.2**: Improved error handling and fallback logic
- **v1.3**: Added comprehensive configuration and documentation
