# Cursor Commands Configuration

This directory contains command configurations for the Cursor IDE, organized by functionality and following the official Cursor CLI command format.

## File Structure

```
.cursor/commands/
├── README.md                    # This documentation
├── build-commands.json          # Build system commands
├── conan-commands.json          # Conan package manager commands
├── database-commands.json       # Database management commands
├── development-commands.json    # Development environment commands
├── openssl-commands.json        # OpenSSL-specific commands
└── registry-commands.json       # Package registry commands
```

## Command Format

All command files follow the official Cursor CLI command configuration format:

```json
{
  "version": "1.0.0",
  "commands": [
    {
      "id": "unique.command.id",
      "title": "Display Title",
      "description": "Command description",
      "command": "shell command to execute",
      "args": [],
      "options": {
        "cwd": "${workspaceFolder}",
        "group": "command-group",
        "icon": "🔧",
        "category": "Category",
        "shortcut": "Ctrl+Shift+X",
        "prompt": "Optional prompt text",
        "confirmation": "Optional confirmation message"
      }
    }
  ]
}
```

## Required Fields

- **`id`**: Unique identifier for the command (use dot notation: `group.action`)
- **`title`**: Human-readable title displayed in UI
- **`description`**: Brief description of what the command does
- **`command`**: Shell command to execute
- **`args`**: Array of command arguments (usually empty for simple commands)
- **`options`**: Configuration object with optional settings

## Optional Fields in `options`

- **`cwd`**: Working directory (defaults to `${workspaceFolder}`)
- **`group`**: Command grouping for organization
- **`icon`**: Emoji or icon identifier
- **`category`**: Category for command organization
- **`shortcut`**: Keyboard shortcut (e.g., `Ctrl+Shift+B`)
- **`prompt`**: Text to show when prompting for input
- **`confirmation`**: Confirmation message for destructive actions

## Command Categories

### Build Commands (`build-commands.json`)
- **Purpose**: OpenSSL component building and compilation
- **Commands**: 5 commands for building crypto, SSL, tools, and cleanup
- **Examples**: `build.crypto`, `build.ssl`, `build.all`, `build.clean`

### Conan Commands (`conan-commands.json`)
- **Purpose**: Conan package manager operations
- **Commands**: 10 commands for package creation, testing, profiles, and management
- **Examples**: `conan.create-basic`, `conan.test-basic`, `conan.build-release`

### Database Commands (`database-commands.json`)
- **Purpose**: PostgreSQL database management
- **Commands**: 5 commands for database lifecycle management
- **Examples**: `db.start`, `db.stop`, `db.connect`, `db.status`

### Development Commands (`development-commands.json`)
- **Purpose**: Development environment setup and testing
- **Commands**: 4 commands for environment setup and validation
- **Examples**: `dev.setup`, `dev.test-consumer`, `dev.check-env`

### OpenSSL Commands (`openssl-commands.json`)
- **Purpose**: OpenSSL-specific operations and workflows
- **Commands**: 10 main commands + 3 quick actions + context menus
- **Examples**: `openssl.build-all`, `openssl.security-scan`, `openssl.deploy-production`

### Registry Commands (`registry-commands.json`)
- **Purpose**: Package registry and distribution management
- **Commands**: 5 commands for registry operations
- **Examples**: `registry.upload`, `registry.validate`, `registry.clean-cache`

## Advanced Features

### Quick Actions
Some command files include `quickActions` for frequently used operations:

```json
"quickActions": [
  {
    "id": "openssl.quick-build",
    "title": "Quick Build",
    "description": "Fast build with cached dependencies",
    "command": "./scripts/build/build-components-no-db.sh",
    "args": [],
    "options": {
      "shortcut": "Ctrl+Q+B"
    }
  }
]
```

### Context Menus
Context-sensitive commands for specific file types:

```json
"contextMenus": [
  {
    "fileTypes": ["conanfile.py"],
    "actions": [
      {
        "id": "conanfile.create-package",
        "title": "Create Package",
        "command": "conan create . --profile:build=default",
        "args": []
      }
    ]
  }
]
```

## Usage

### In Cursor IDE
1. Open Command Palette (`Ctrl+Shift+P`)
2. Type command ID or title
3. Execute with Enter

### Keyboard Shortcuts
Commands with `shortcut` defined can be executed directly:
- `Ctrl+Shift+B`: Build All Components
- `Ctrl+Shift+U`: Upload to Registries
- `Ctrl+Shift+D`: Database Status

### Context Menus
Right-click on files to access context-specific commands:
- **conanfile.py**: Create Package, Test Package
- ***.sh**: Make Executable, Run Script

## Environment Variables

Commands can use environment variables:
- `${workspaceFolder}`: Current workspace directory
- `${file}`: Currently selected file (in context menus)
- Custom variables: `$ARTIFACTORY_USER`, `$GITHUB_TOKEN`

## Best Practices

1. **Unique IDs**: Use dot notation for hierarchical organization
2. **Descriptive Titles**: Clear, actionable titles
3. **Consistent Icons**: Use emojis for visual identification
4. **Logical Grouping**: Group related commands together
5. **Error Handling**: Commands should handle errors gracefully
6. **Documentation**: Keep descriptions clear and concise

## Migration from Custom Format

The command files were migrated from a custom format to the official Cursor CLI format:

### Before (Custom Format)
```json
{
  "commands": [
    {
      "name": "build:crypto",
      "description": "Build OpenSSL crypto component",
      "command": "cd openssl-crypto && conan create .",
      "cwd": "${workspaceFolder}",
      "group": "build",
      "icon": "🔐"
    }
  ]
}
```

### After (Official Format)
```json
{
  "version": "1.0.0",
  "commands": [
    {
      "id": "build.crypto",
      "title": "Build OpenSSL Crypto Component",
      "description": "Build OpenSSL crypto component only",
      "command": "cd openssl-crypto && conan create .",
      "args": [],
      "options": {
        "cwd": "${workspaceFolder}",
        "group": "build",
        "icon": "🔐",
        "category": "Build"
      }
    }
  ]
}
```

## Validation

All command files are validated for:
- ✅ **JSON Syntax**: Valid JSON structure
- ✅ **Required Fields**: All required fields present
- ✅ **Unique IDs**: No duplicate command IDs
- ✅ **Proper Format**: Follows official Cursor CLI schema

## Troubleshooting

### Command Not Found
- Check command ID spelling
- Verify file is in `.cursor/commands/` directory
- Restart Cursor IDE after adding new commands

### Command Fails
- Check command syntax and paths
- Verify required tools are installed
- Check environment variables are set

### Shortcuts Not Working
- Ensure shortcut format is correct (`Ctrl+Shift+X`)
- Check for conflicts with existing shortcuts
- Restart Cursor IDE after adding shortcuts

## References

- [Cursor CLI Documentation](https://cursor.com/docs/cli)
- [Cursor Commands Reference](https://cursor.com/docs/commands)
- [VS Code Tasks Documentation](https://code.visualstudio.com/docs/editor/tasks) (similar format)
