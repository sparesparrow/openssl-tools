# .cursor/ Directory Structure

This document explains the proper organization of the `.cursor/` directory according to the official Cursor CLI configuration structure.

## Official Structure

The `.cursor/` directory should contain:

```
.cursor/
├── cli-config.json    # Global CLI configuration (in ~/.cursor/)
├── cli.json          # Project-level CLI permissions
└── rules/            # Project rules directory
    ├── rule1.mdc     # Individual rule files
    ├── rule2.mdc
    └── backend/      # Nested rules for specific areas
        └── api.mdc
```

## Current Structure

Our current structure includes both official and custom extensions:

```
.cursor/
├── cli-config.json              # ✅ Official: CLI configuration
├── cli.json                     # ✅ Official: Project permissions
├── rules/                       # ✅ Official: Project rules
│   ├── build-optimization.mdc
│   ├── cicd-modernization.mdc
│   ├── clang-tidy-policy.mdc
│   ├── conan-devops.mdc
│   ├── logging-quality.mdc
│   ├── monitoring-observability.mdc
│   ├── openssl-docs-policy.mdc
│   ├── python-automation.mdc
│   ├── repository-config.mdc
│   ├── security-compliance.mdc
│   ├── sqlite-schema-validation.mdc
│   ├── testing-quality.mdc
│   ├── the-way-of-python.mdc
│   └── windows-build.mdc
├── agents/                      # ⚠️ Custom: Agent configurations
│   ├── ci-cd-agent.yml
│   ├── ci-repair-agent.yml
│   ├── database-agent.yml
│   └── ...
├── commands/                    # ⚠️ Custom: Command definitions
│   ├── build-commands.json
│   ├── database-commands.json
│   └── ...
├── composer/                    # ⚠️ Custom: Composer rules
│   └── openssl-composer-rules.json
├── docs/                        # ⚠️ Custom: Documentation templates
│   └── templates/
├── workflows/                   # ⚠️ Custom: Workflow definitions
│   └── development-workflow.json
└── openssl-tools-settings.json # ⚠️ Custom: Project settings
```

## File Descriptions

### Official Files

#### `.cursor/cli-config.json`
Global CLI configuration following the [official schema](https://cursor.com/docs/cli/reference/configuration):
- `model`: AI model selection
- `temperature`: Model temperature
- `maxTokens`: Maximum response tokens
- `timeout`: Operation timeout
- `outputFormat`: Output format specification
- `force`: Force execution flag
- `printResult`: Print results flag
- `stream`: Streaming mode flag
- `mcp`: MCP configuration
- `context`: Context configuration

#### `.cursor/cli.json`
Project-level CLI permissions:
- `permissions.allow`: Allowed operations
- `permissions.deny`: Denied operations

#### `.cursor/rules/`
Project rules in MDC format:
- Each `.mdc` file contains project-specific rules
- Rules can have metadata (description, globs, alwaysApply)
- Nested directories automatically attach when files are referenced

### Custom Extensions

#### `.cursor/agents/`
Custom agent configurations for specialized tasks:
- `ci-repair-agent.yml`: CI repair automation
- `database-agent.yml`: Database operations
- `security-compliance-agent.yml`: Security scanning

#### `.cursor/commands/`
Custom command definitions:
- `build-commands.json`: Build system commands
- `database-commands.json`: Database operations
- `openssl-commands.json`: OpenSSL-specific commands

#### `.cursor/composer/`
Custom composer rules for code generation:
- `openssl-composer-rules.json`: OpenSSL code generation rules

#### `.cursor/docs/`
Documentation templates and guides:
- `templates/`: Reusable documentation templates

#### `.cursor/workflows/`
Custom workflow definitions:
- `development-workflow.json`: Development process workflows

#### `.cursor/openssl-tools-settings.json`
Project-specific settings:
- Development environment configuration
- Pipeline settings
- Editor preferences
- Git integration settings

## MCP Configuration

The MCP (Model Context Protocol) configuration is located at the project root:

```
mcp.json                         # ✅ Official: MCP server configuration
```

This file contains MCP server definitions:
- `openssl-database`: Database operations
- `openssl-build`: Build system integration
- `openssl-security`: Security scanning
- `github`: GitHub integration
- `openssl-ci`: CI/CD context

## Usage in agent-loop.sh

The `agent-loop.sh` script uses these configurations:

```bash
# Configuration paths
CURSOR_CONFIG_FILE="${CURSOR_CONFIG_FILE:-.cursor/cli-config.json}"
CURSOR_MCP_CONFIG="${CURSOR_MCP_CONFIG:-mcp.json}"
CURSOR_AGENT_CONFIG="${CURSOR_AGENT_CONFIG:-.cursor/agents/ci-repair-agent.yml}"
```

## Best Practices

1. **Official Structure**: Follow the official Cursor CLI structure for core files
2. **Custom Extensions**: Use custom directories for project-specific functionality
3. **Documentation**: Document custom extensions and their purposes
4. **Version Control**: Include official files in git, consider ignoring custom extensions
5. **Naming**: Use descriptive names for custom files to avoid conflicts

## Migration Notes

- Moved `mcp.json` from `.cursor/` to project root (official location)
- Renamed `settings.json` to `openssl-tools-settings.json` (custom extension)
- Created `cli.json` for project-level permissions (official structure)
- Maintained custom extensions for project-specific functionality

## References

- [Cursor CLI Configuration](https://cursor.com/docs/cli/reference/configuration)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Cursor CLI Documentation](https://cursor.com/docs/cli)
