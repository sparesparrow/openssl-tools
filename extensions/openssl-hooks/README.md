# OpenSSL Hooks - Conan Extension Package

A comprehensive Conan extension package that provides automated hooks for OpenSSL projects, ensuring quality, security, and compliance throughout the build and packaging process.

## 🚀 Features

### 🔨 Pre-Build Hook (`pre_build.py`)
- **Source Structure Validation**: Ensures OpenSSL source has required files and directories
- **Build Dependencies Check**: Validates all required build tools are available
- **Environment Setup**: Configures build environment with OpenSSL-specific variables
- **Profile Validation**: Validates Conan profile settings for OpenSSL builds
- **Build Configuration**: Prepares build configuration based on platform and settings

### 📦 Post-Package Hook (`post_package.py`)
- **Package Structure Validation**: Ensures packaged OpenSSL components are complete
- **Library Integrity Check**: Validates library files and calculates checksums
- **Headers and Symbols Validation**: Checks OpenSSL headers and exported symbols
- **Package Metadata Generation**: Creates comprehensive package metadata
- **Security Checks**: Performs basic security validation on packaged files
- **SBOM Generation**: Creates Software Bill of Materials in CycloneDX format

### 📤 Pre-Export Hook (`pre_export.py`)
- **Recipe Validation**: Validates Conan recipe structure and content
- **Dependencies Check**: Ensures all dependencies are properly specified
- **Metadata Validation**: Validates package metadata completeness
- **License Compliance**: Checks license compliance for export
- **Security Analysis**: Scans recipe for potential security issues
- **Export Preparation**: Prepares metadata for remote export

### 📋 Post-Export Hook (`post_export.py`)
- **Export Validation**: Validates exported recipe on remote
- **Remote Availability**: Checks package availability on configured remotes
- **Integrity Verification**: Verifies export integrity and completeness
- **Registry Update**: Updates package registry with export information
- **Quality Checks**: Performs final quality and performance checks
- **Export Reporting**: Generates comprehensive export reports

## 📦 Installation

### As a Conan Package

```bash
# Install the package
conan install openssl-hooks/1.0.0@sparesparrow/stable

# Or add to your conanfile.txt
openssl-hooks/1.0.0@sparesparrow/stable
```

### As a Development Dependency

```python
# In your conanfile.py
def requirements(self):
    self.requires("openssl-hooks/1.0.0@sparesparrow/stable")
```

## 🔧 Usage

### Automatic Hook Registration

When you install this package, the hooks are automatically registered with Conan and will be executed during the appropriate phases of your OpenSSL package lifecycle.

### Manual Hook Registration

If you need to register hooks manually:

```bash
# Set environment variable to include hooks directory
export CONAN_HOOKS="/path/to/openssl-hooks/hooks"

# Or add to your conan.conf
[hooks]
CONAN_HOOKS=/path/to/openssl-hooks/hooks
```

### Hook Execution Order

The hooks are executed in the following order during the Conan package lifecycle:

1. **Pre-Export** → Recipe validation and preparation
2. **Pre-Build** → Build environment setup and validation
3. **Post-Package** → Package validation and SBOM generation
4. **Post-Export** → Export validation and quality reporting

## 🛠️ Configuration

### Environment Variables

The hooks use the following environment variables for configuration:

- `OPENSSL_HOOKS_VERSION`: Version of the hooks package
- `OPENSSL_HOOKS_DIR`: Directory containing the hook files
- `CONAN_HOOKS`: List of hook directories (automatically managed)

### Hook Customization

You can customize hook behavior by setting environment variables:

```bash
# Enable verbose output
export OPENSSL_HOOKS_VERBOSE=1

# Disable specific checks
export OPENSSL_HOOKS_SKIP_SECURITY=1
export OPENSSL_HOOKS_SKIP_SBOM=1
```

## 📊 Output and Reporting

### Console Output

The hooks provide detailed console output with emoji indicators:

- ✅ Success operations
- ⚠️ Warnings and recommendations
- ❌ Errors and failures
- 📁 File operations
- 🔍 Validation checks
- 🔒 Security operations
- 📦 Package operations
- 📋 Documentation and metadata

### Generated Files

The hooks generate several files during execution:

- `package_metadata.json`: Comprehensive package metadata
- `sbom.cyclonedx.json`: Software Bill of Materials
- `export_metadata.json`: Export preparation metadata
- `export_report.json`: Export validation report
- `package_registry.json`: Package registry entries

## 🔒 Security Features

### Security Scanning

The hooks perform comprehensive security checks:

- **SAST Analysis**: Static code analysis for potential vulnerabilities
- **Dependency Scanning**: Checks for known vulnerable dependencies
- **License Compliance**: Validates license compatibility
- **File Permissions**: Checks for overly permissive file permissions
- **Hardcoded Secrets**: Scans for potential hardcoded credentials

### SBOM Generation

Software Bill of Materials (SBOM) is generated in CycloneDX format including:

- All package components and their versions
- Dependency relationships
- License information
- Vulnerability data
- Build metadata

## 🧪 Testing

### Running Tests

```bash
# Test the package
conan test test_package openssl-hooks/1.0.0@sparesparrow/stable

# Test with specific profile
conan test test_package openssl-hooks/1.0.0@sparesparrow/stable --profile=default
```

### Test Coverage

The package includes comprehensive tests for:

- Hook registration and execution
- File validation and integrity
- Environment variable setup
- Error handling and edge cases
- Security checks and validation

## 📚 Examples

### Basic OpenSSL Package

```python
from conan import ConanFile

class OpenSSLPackage(ConanFile):
    name = "openssl"
    version = "3.0.0"
    
    def requirements(self):
        # Include the hooks package
        self.requires("openssl-hooks/1.0.0@sparesparrow/stable")
    
    def build(self):
        # Your build logic here
        # Hooks will automatically validate and prepare the environment
        pass
    
    def package(self):
        # Your packaging logic here
        # Hooks will automatically validate the package
        pass
```

### Advanced Configuration

```python
from conan import ConanFile

class AdvancedOpenSSLPackage(ConanFile):
    name = "openssl-advanced"
    version = "3.0.0"
    
    def requirements(self):
        self.requires("openssl-hooks/1.0.0@sparesparrow/stable")
    
    def configure(self):
        # Configure hooks behavior
        self.env_info.OPENSSL_HOOKS_VERBOSE = "1"
        self.env_info.OPENSSL_HOOKS_STRICT = "1"
    
    def build(self):
        # Build with enhanced validation
        pass
```

## 🐛 Troubleshooting

### Common Issues

1. **Hooks Not Executing**
   - Ensure the package is properly installed
   - Check that CONAN_HOOKS environment variable is set
   - Verify hook files are in the correct location

2. **Validation Failures**
   - Check that your OpenSSL source structure is correct
   - Ensure all required build dependencies are available
   - Verify Conan profile settings

3. **Security Check Failures**
   - Review security warnings and fix issues
   - Update dependencies to secure versions
   - Check for hardcoded secrets in your recipe

### Debug Mode

Enable debug mode for detailed output:

```bash
export OPENSSL_HOOKS_DEBUG=1
export CONAN_LOGGING_LEVEL=10
```

## 🤝 Contributing

### Development Setup

```bash
# Clone the repository
git clone https://github.com/sparesparrow/openssl-tools.git
cd openssl-tools/extensions/openssl-hooks

# Install development dependencies
conan install . --build=missing

# Run tests
conan test test_package .
```

### Adding New Hooks

1. Create a new hook file in the `hooks/` directory
2. Implement the `run(conanfile, **kwargs)` function
3. Add comprehensive documentation and error handling
4. Update the `conanfile.py` to include the new hook
5. Add tests for the new hook functionality

## 📄 License

This package is licensed under the Apache License 2.0. See the LICENSE file for details.

## 🔗 Links

- **Repository**: [sparesparrow/openssl-tools](https://github.com/sparesparrow/openssl-tools)
- **Documentation**: [OpenSSL Tools Documentation](https://github.com/sparesparrow/openssl-tools/docs)
- **Issues**: [GitHub Issues](https://github.com/sparesparrow/openssl-tools/issues)
- **Conan Center**: [Conan Center Package](https://conan.io/center/openssl-hooks)

## 📞 Support

For support and questions:

- **GitHub Issues**: Open an issue for bugs and feature requests
- **Discussions**: Use GitHub Discussions for questions and community support
- **Email**: openssl-tools@example.com

---

**Made with ❤️ by the OpenSSL Tools Team**
