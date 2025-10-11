# Agent Loop Improved - Enterprise-Grade CI Orchestration

A robust, secure, and production-ready CI orchestration script with comprehensive error handling, security enhancements, and advanced configuration management.

## 🚀 Key Improvements

### **Security Enhancements**
- **Secure API Key Management**: API keys stored in files with 600 permissions instead of environment variables
- **Input Validation**: Comprehensive validation for all inputs with regex patterns
- **Secure Logging**: Automatic redaction of sensitive data patterns
- **Restrictive File Permissions**: umask 077 for all file operations
- **Command Injection Prevention**: Strict JSON parsing without shell expansion

### **Robustness & Reliability**
- **Signal Handling**: Comprehensive cleanup on SIGTERM/SIGINT with proper process management
- **Circuit Breaker**: Prevents infinite loops with exponential backoff and jitter
- **Resource Management**: Automatic cleanup of temporary files and background processes
- **Error Recovery**: Intelligent retry logic with consecutive failure tracking
- **Git Safety**: Repository validation and working directory checks

### **Configuration Management**
- **JSON Configuration**: Centralized configuration file instead of environment variables
- **Validation**: All configuration values validated with proper error messages
- **Defaults**: Sensible defaults with fallback to environment variables
- **Flexibility**: Easy to customize for different environments

### **Enhanced Features**
- **Dry Run Mode**: Test operations without making actual changes
- **Schema Validation**: JSON schema validation for agent responses
- **Structured Logging**: JSON-formatted logs with syslog integration
- **API Key Testing**: Real API key validation with actual API calls

## 📋 Prerequisites

- **Bash 4.0+** with support for associative arrays
- **jq** for JSON processing
- **gh** (GitHub CLI) for GitHub API access
- **git** for repository operations
- **curl** for HTTP requests
- **timeout** for command timeouts
- **logger** (optional) for syslog integration

## 🛠️ Installation

1. **Download the improved script:**
   ```bash
   curl -O https://raw.githubusercontent.com/sparesparrow/openssl-tools/main/agent-loop-improved.sh
   chmod +x agent-loop-improved.sh
   ```

2. **Set up secure API key:**
   ```bash
   ./setup-secure-api-key.sh
   ```

3. **Configure the script:**
   ```bash
   cp .agent-config.json.example .agent-config.json
   # Edit .agent-config.json with your settings
   ```

## ⚙️ Configuration

### **Configuration File (.agent-config.json)**

```json
{
  "repo": "sparesparrow/openssl-tools",
  "pr_number": "6",
  "pr_branch": "simplify-openssl-build",
  "max_iterations": 12,
  "interval": 60,
  "log_level": "info",
  "agent_timeout_sec": 60,
  "use_streaming": false,
  "dry_run": false,
  "task": "Ensure all PR workflows are green with minimal safe changes",
  "mode": "execution",
  "cursor_config_file": ".cursor/cli-config.json",
  "cursor_mcp_config": "mcp.json",
  "cursor_agent_config": ".cursor/agents/ci-repair-agent.yml",
  "agent_model": "auto",
  "mcp_enabled": true
}
```

### **Configuration Options**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `repo` | string | `sparesparrow/openssl-tools` | GitHub repository (owner/repo) |
| `pr_number` | string | `6` | Pull request number |
| `pr_branch` | string | `simplify-openssl-build` | Branch name |
| `max_iterations` | number | `12` | Maximum iterations to run |
| `interval` | number | `60` | Seconds between iterations |
| `log_level` | string | `info` | Log level (debug\|info\|warn\|error) |
| `agent_timeout_sec` | number | `60` | Timeout for cursor-agent calls |
| `use_streaming` | boolean | `false` | Use streaming mode for cursor-agent |
| `dry_run` | boolean | `false` | Dry run mode (no actual changes) |
| `task` | string | `"Ensure all PR workflows..."` | Task description |
| `mode` | string | `execution` | Execution mode |
| `agent_model` | string | `auto` | Cursor agent model |
| `mcp_enabled` | boolean | `true` | Enable MCP (Model Context Protocol) |

## 🔐 Security Setup

### **API Key Management**

The improved script uses secure file-based API key storage:

```bash
# Set up secure API key
./setup-secure-api-key.sh

# Or manually create the file
mkdir -p ~/.cursor
echo "key_your_api_key_here" > ~/.cursor/api-key
chmod 600 ~/.cursor/api-key
```

### **File Permissions**

The script automatically sets restrictive permissions:
- API key file: `600` (owner read/write only)
- Temporary files: `600` (owner read/write only)
- Configuration directory: `700` (owner access only)

### **Input Validation**

All inputs are validated with strict patterns:
- Repository format: `^[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+$`
- PR number: `^[0-9]+$`
- Branch name: `^[a-zA-Z0-9/_-]+$`
- Numeric parameters: Positive integers only

## 🚀 Usage

### **Basic Usage**

```bash
# Run with default configuration
./agent-loop-improved.sh

# Run in dry-run mode (safe testing)
DRY_RUN=true ./agent-loop-improved.sh

# Run with debug logging
LOG_LEVEL=debug ./agent-loop-improved.sh
```

### **Advanced Usage**

```bash
# Custom configuration file
CONFIG_FILE=/path/to/custom-config.json ./agent-loop-improved.sh

# Override specific settings
REPO=myorg/myrepo PR_NUMBER=123 ./agent-loop-improved.sh

# Run with environment variables (fallback)
CURSOR_API_KEY=key_... ./agent-loop-improved.sh
```

### **Environment Variables (Fallback)**

If no configuration file is found, the script falls back to environment variables:

```bash
export REPO="sparesparrow/openssl-tools"
export PR_NUMBER="6"
export PR_BRANCH="simplify-openssl-build"
export MAX_ITERATIONS="12"
export INTERVAL="60"
export LOG_LEVEL="info"
export DRY_RUN="false"
export CURSOR_API_KEY="key_your_api_key_here"
```

## 📊 Logging

### **Structured Logging**

The script uses structured JSON logging:

```json
{"ts":"2025-01-11T04:21:43+0200","level":"info","msg":"Repository: sparesparrow/openssl-tools"}
{"ts":"2025-01-11T04:21:43+0200","level":"debug","msg":"Loaded config: model=auto, timeout=60s"}
```

### **Log Levels**

- **debug**: Detailed debugging information
- **info**: General information messages
- **warn**: Warning messages
- **error**: Error messages

### **Syslog Integration**

If available, logs are also sent to syslog:

```bash
# View logs in syslog
journalctl -t agent-loop-improved

# Or in traditional syslog
tail -f /var/log/syslog | grep agent-loop-improved
```

## 🔧 Troubleshooting

### **Common Issues**

1. **API Key Not Found**
   ```bash
   # Set up API key
   ./setup-secure-api-key.sh
   ```

2. **Permission Denied**
   ```bash
   # Fix file permissions
   chmod 600 ~/.cursor/api-key
   chmod 700 ~/.cursor
   ```

3. **Invalid Configuration**
   ```bash
   # Validate JSON configuration
   jq empty .agent-config.json
   ```

4. **Cursor Agent Not Found**
   ```bash
   # Install cursor-agent
   curl https://cursor.com/install -fsS | bash
   ```

### **Debug Mode**

Run with debug logging to see detailed information:

```bash
LOG_LEVEL=debug ./agent-loop-improved.sh
```

### **Dry Run Mode**

Test operations without making changes:

```bash
DRY_RUN=true ./agent-loop-improved.sh
```

## 🔄 Migration from Original Script

### **Key Differences**

1. **Configuration**: JSON file instead of environment variables
2. **API Key**: File-based storage instead of environment variable
3. **Logging**: Structured JSON logging with syslog integration
4. **Security**: Enhanced input validation and secure file handling
5. **Error Handling**: Comprehensive error recovery and circuit breaker

### **Migration Steps**

1. **Backup existing configuration:**
   ```bash
   cp agent-loop.sh agent-loop.sh.backup
   ```

2. **Set up new configuration:**
   ```bash
   ./setup-secure-api-key.sh
   cp .agent-config.json.example .agent-config.json
   # Edit .agent-config.json with your settings
   ```

3. **Test with dry run:**
   ```bash
   DRY_RUN=true ./agent-loop-improved.sh
   ```

4. **Run in production:**
   ```bash
   ./agent-loop-improved.sh
   ```

## 📈 Performance

### **Optimizations**

- **Exponential Backoff**: Intelligent retry logic with jitter
- **Circuit Breaker**: Prevents resource exhaustion
- **Resource Management**: Automatic cleanup of temporary files
- **Parallel Processing**: Efficient handling of multiple operations
- **Caching**: Intelligent caching of API responses

### **Resource Usage**

- **Memory**: Minimal memory footprint with automatic cleanup
- **CPU**: Efficient JSON processing with single jq calls
- **Disk**: Temporary files automatically cleaned up
- **Network**: Intelligent retry logic with backoff

## 🛡️ Security Considerations

### **Data Protection**

- **API Keys**: Stored in secure files with 600 permissions
- **Logs**: Sensitive data automatically redacted
- **Temporary Files**: Created with restrictive permissions
- **Input Validation**: All inputs validated with strict patterns

### **Access Control**

- **File Permissions**: Restrictive umask (077) for all operations
- **Process Isolation**: Proper signal handling and cleanup
- **Error Handling**: Secure error messages without sensitive data

### **Audit Trail**

- **Structured Logging**: All operations logged with timestamps
- **Syslog Integration**: Centralized logging for audit purposes
- **Configuration Tracking**: All configuration changes logged

## 🤝 Contributing

### **Development Setup**

1. **Clone the repository:**
   ```bash
   git clone https://github.com/sparesparrow/openssl-tools.git
   cd openssl-tools
   ```

2. **Set up development environment:**
   ```bash
   ./setup-secure-api-key.sh
   cp .agent-config.json.example .agent-config.json
   ```

3. **Test changes:**
   ```bash
   DRY_RUN=true LOG_LEVEL=debug ./agent-loop-improved.sh
   ```

### **Code Style**

- **Bash**: Follow bash best practices with `set -euo pipefail`
- **Security**: Always validate inputs and use secure file operations
- **Logging**: Use structured logging with appropriate levels
- **Error Handling**: Comprehensive error handling with cleanup

## 📄 License

This project is licensed under the same terms as the original openssl-tools project.

## 🆘 Support

For issues and questions:

1. **Check the troubleshooting section** above
2. **Run with debug logging** to see detailed information
3. **Use dry run mode** to test without making changes
4. **Check the logs** for specific error messages

## 🔮 Future Enhancements

- **Metrics Collection**: Prometheus metrics export
- **Web Dashboard**: Real-time monitoring interface
- **Plugin System**: Extensible plugin architecture
- **Multi-Repository**: Support for multiple repositories
- **Advanced Scheduling**: Cron-like scheduling capabilities
