# OpenSSL Tools - Build Orchestration Package

## 📦 Package Overview
- **Name**: `openssl-tools`
- **Version**: `1.2.4` (current)
- **Channel**: `stable`
- **User**: `sparesparrow`
- **Purpose**: Build tools, automation scripts, and infrastructure components for OpenSSL

## 🔄 Version Management Rules

### Before Making Changes
1. **ALWAYS update version first** in `conanfile.py`
2. **NEVER modify conanfile.py** without version bump
3. **Update dependency versions** if foundation packages changed
4. **Commit version change** before calling `conan create`

### Version Update Workflow
```bash
# 1. Update version in conanfile.py
version = "1.2.5"  # Increment appropriately

# 2. Update dependency versions if needed
requires = ["openssl-base/1.0.2@sparesparrow/stable"]

# 3. Commit the change
git add conanfile.py
git commit -m "bump: openssl-tools to 1.2.5"

# 4. Build and upload
conan create . --build=missing
conan upload openssl-tools/1.2.5@sparesparrow/stable -r=sparesparrow-conan
```

## 📋 Package Contents

### Exported Sources
- `scripts/*` - Build and automation scripts
- `profiles/*` - Conan build profiles
- `docker/*` - Docker configurations
- `templates/*` - Build templates
- `.cursor/*` - Cursor IDE configurations
- `openssl_tools/**` - Python tools and utilities

### Package Artifacts
- **Python Tools**: `openssl_tools/` directory with Python modules
- **Profiles**: `profiles/` directory with build profiles
- **Scripts**: `scripts/` directory with shell scripts
- **Templates**: `templates/` directory with template files

### Environment Variables
- `OPENSSL_TOOLS_VERSION` - Package version
- `OPENSSL_TOOLS_ROOT` - Root path to tools
- `PYTHONPATH` - Prepend package folder for Python imports

## 🏗️ Build Process

### Dependencies
- `openssl-base/1.0.1@sparesparrow/stable` - Foundation utilities

### Build Commands
```bash
# Install dependencies (will use cached foundation packages)
conan install . --build=missing

# Create package
conan create . --build=missing

# Upload to remote
conan upload openssl-tools/1.2.4@sparesparrow/stable -r=sparesparrow-conan
```

## 🧪 Validation

### Package Validation
```bash
# Check package contents
conan cache path openssl-tools/1.2.4@sparesparrow/stable

# Validate with script
python ../scripts/validate-conan-packages.py openssl-tools/1.2.4
```

### Expected Contents
- ✅ `openssl_tools/` directory with Python files
- ✅ `profiles/` directory with profile files
- ✅ `scripts/` directory with shell scripts
- ✅ `templates/` directory with template files
- ✅ Environment variables properly set
- ✅ Dependencies correctly resolved

## 🔗 Dependencies

### Requires
- `openssl-base` - Foundation utilities and profiles

### Consumed By
- `openssl` - Requires this package for build orchestration

### Version Compatibility
- **Major version changes** (1.x → 2.x): Breaking changes, update all consumers
- **Minor version changes** (1.2.x → 1.3.x): New features, backward compatible
- **Patch version changes** (1.2.3 → 1.2.4): Bug fixes, fully backward compatible

## 🚨 Critical Notes

1. **Tooling Layer**: Bridges foundation and domain layers
2. **Build Orchestration**: Provides build tools and automation
3. **Dependency Management**: Must update when foundation packages change
4. **Python Package**: Contains Python tools and utilities
5. **CI/CD Integration**: Provides automation for build processes

## 📝 Change Log

### Version 1.2.4
- Updated dependency to openssl-base/1.0.1
- Fixed package() method to properly copy all artifacts
- Added proper package_info() with environment variables
- Removed dependency on non-existent base_conanfile

### Version 1.2.3
- Initial release with build orchestration tools
- Python tools, profiles, scripts, and templates



