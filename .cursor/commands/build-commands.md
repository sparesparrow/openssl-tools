---
description: Build system commands for OpenSSL components (crypto, SSL, tools)
globs: ["**/conanfile.py", "**/CMakeLists.txt", "**/Makefile", "scripts/build/**", "openssl-*/**"]
alwaysApply: true
category: "Build Commands"
version: "1.0.0"
---

# Build Commands

OpenSSL component building and compilation commands for the Cursor IDE.

## Available Commands

### 🔐 Build OpenSSL Crypto Component
- **ID**: `build.crypto`
- **Description**: Build OpenSSL crypto component only
- **Command**: `cd openssl-crypto && conan create . --profile:build=default --profile:host=default -s build_type=Release -o '*:shared=True' --build=missing`
- **Category**: Build
- **Group**: build

### 🔒 Build OpenSSL SSL Component
- **ID**: `build.ssl`
- **Description**: Build OpenSSL SSL component (requires crypto)
- **Command**: `cd openssl-ssl && conan create . --profile:build=default --profile:host=default -s build_type=Release -o '*:shared=True' --build=missing`
- **Category**: Build
- **Group**: build

### 🔧 Build OpenSSL Tools Component
- **ID**: `build.tools`
- **Description**: Build OpenSSL tools component (requires ssl)
- **Command**: `cd openssl-tools && conan create . --profile:build=default --profile:host=default -s build_type=Release -o '*:shared=True' --build=missing`
- **Category**: Build
- **Group**: build

### 🏗️ Build All Components
- **ID**: `build.all`
- **Description**: Build all OpenSSL components with database tracking
- **Command**: `./scripts/build/build-all-components.sh`
- **Category**: Build
- **Group**: build

### 🧹 Clean Build Cache
- **ID**: `build.clean`
- **Description**: Clean all Conan packages and rebuild from scratch
- **Command**: `conan remove 'openssl-*' -f && ./scripts/build/build-all-components.sh`
- **Category**: Build
- **Group**: build

## Usage

### In Cursor IDE
1. Open Command Palette (`Ctrl+Shift+P`)
2. Type command ID (e.g., `build.crypto`)
3. Execute with Enter

### Command Dependencies
- **crypto** → **ssl** → **tools**
- Use `build.all` for complete build with proper dependency order
- Use `build.clean` to start fresh build

### Environment Requirements
- Conan 2.x installed and configured
- Default profiles set up
- Database running (for `build.all`)

## Build Profiles

Commands use the following Conan profiles:
- **Build Profile**: `default`
- **Host Profile**: `default`
- **Build Type**: `Release`
- **Shared Libraries**: `True`
- **Build Policy**: `missing` (build missing dependencies)

## Troubleshooting

### Build Failures
- Check Conan profiles are configured
- Verify dependencies are available
- Use `build.clean` for fresh start

### Missing Dependencies
- Ensure database is running for `build.all`
- Check Conan remote configuration
- Verify profile settings
