# OpenSSL Tools Conan 2.x + GitHub Packages Setup

This document describes how to set up a proper Python dev/testing environment with Conan 2.x and GitHub Packages for the openssl-tools project, following patterns from openssl-tools.

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Set up the complete Conan environment
python scripts/setup-openssl-tools-conan.py

# Set up GitHub Packages integration
python scripts/setup-github-packages-conan.py --github-owner=sparesparrow --github-repo=openssl-tools
```

### 2. Activate Environment

```bash
# Linux/macOS
source conan-dev/activate

# Windows
conan-dev\activate.bat
```

### 3. Build and Test

```bash
# Build package
conan create . --profile=linux-gcc11

# Run tests
python scripts/test-openssl-tools-conan.py --profile=linux-gcc11

# Upload to GitHub Packages
python scripts/conan/upload-to-github-packages.py --profile=linux-gcc11
```

## 📋 Prerequisites

- Python 3.8+
- Git
- GitHub Personal Access Token (for GitHub Packages)

## 🔧 Environment Setup

### Conan 2.x Configuration

The setup creates a complete Conan 2.x environment with:

- **Virtual Environment**: Isolated Python environment
- **Conan Profiles**: Platform-specific build configurations
- **GitHub Packages Remote**: Artifact storage
- **Development Scripts**: Easy-to-use automation

### Directory Structure

```
openssl-tools/
├── conan-dev/                    # Conan development environment
│   ├── venv/                     # Python virtual environment
│   ├── profiles/                 # Conan profiles
│   ├── cache/                    # Conan cache
│   ├── artifacts/                # Build artifacts
│   └── global.conf              # Conan configuration
├── scripts/
│   ├── conan/                    # Conan automation scripts
│   │   ├── upload-to-github-packages.py
│   │   └── install-from-github-packages.py
│   ├── setup-openssl-tools-conan.py
│   ├── setup-github-packages-conan.py
│   └── test-openssl-tools-conan.py
└── .github/workflows/
    └── conan-github-packages.yml # GitHub Actions workflow
```

## 🐍 Python Environment

### Virtual Environment

The setup creates a Python virtual environment with:

- **Conan 2.x**: Latest Conan package manager
- **Dependencies**: All required Python packages
- **Isolation**: Clean environment for development

### Dependencies

Core dependencies installed:
- `conan>=2.0.0` - Conan 2.x package manager
- `requests>=2.31.0` - HTTP library
- `click>=8.1.0` - Command-line interface
- `pyyaml>=6.0.0` - YAML processing
- `jinja2>=3.1.0` - Template engine

Optional dependencies based on options:
- `numpy>=1.20.0` - Numerical computing (statistics)
- `scipy>=1.7.0` - Scientific computing (statistics)
- `pygithub>=1.59.0` - GitHub API (GitHub integration)
- `python-gitlab>=4.0.0` - GitLab API (GitLab integration)
- `httpx>=0.25.0` - HTTP client (API integration)

## 🔧 Conan Profiles

### Linux Profiles

- **linux-gcc11**: GCC 11 with libstdc++11
- **linux-clang15**: Clang 15 with libstdc++11
- **debug**: Debug build configuration

### Windows Profiles

- **windows-msvc2022**: Visual Studio 2022
- **debug**: Debug build configuration

### macOS Profiles

- **macos-clang14**: Apple Clang 14 with libc++
- **debug**: Debug build configuration

## 📦 GitHub Packages Integration

### Remote Configuration

GitHub Packages is configured as a Conan remote:

```bash
# Remote URL
https://maven.pkg.github.com/sparesparrow/openssl-tools

# Authentication
conan remote login github-packages --username sparesparrow --password <token>
```

### Package Upload

```bash
# Upload to GitHub Packages
python scripts/conan/upload-to-github-packages.py --profile=linux-gcc11

# Dry run
python scripts/conan/upload-to-github-packages.py --profile=linux-gcc11 --dry-run
```

### Package Installation

```bash
# Install from GitHub Packages
python scripts/conan/install-from-github-packages.py --profile=linux-gcc11

# Install specific version
python scripts/conan/install-from-github-packages.py --profile=linux-gcc11 --version=1.0.0
```

## 🔄 GitHub Actions Workflow

### Automated CI/CD

The setup creates a GitHub Actions workflow that:

1. **Multi-platform builds**: Linux, Windows, macOS
2. **Conan 2.x integration**: Latest Conan features
3. **GitHub Packages upload**: Automatic artifact storage
4. **Testing**: Comprehensive test suite
5. **SBOM generation**: Software Bill of Materials

### Workflow Triggers

- **Push to main/develop**: Build and test
- **Tags**: Build, test, and upload
- **Pull requests**: Build and test
- **Manual dispatch**: On-demand builds

## 🧪 Testing

### Test Types

1. **Conan Tests**: Package creation and validation
2. **Unit Tests**: Python unit tests
3. **Integration Tests**: End-to-end functionality

### Running Tests

```bash
# All tests
python scripts/test-openssl-tools-conan.py --test-type=all --profile=linux-gcc11

# Specific test types
python scripts/test-openssl-tools-conan.py --test-type=conan --profile=linux-gcc11
python scripts/test-openssl-tools-conan.py --test-type=unit
python scripts/test-openssl-tools-conan.py --test-type=integration
```

## 🛠️ Development Workflow

### 1. Setup (One-time)

```bash
# Clone repository
git clone https://github.com/sparesparrow/openssl-tools.git
cd openssl-tools

# Setup Conan environment
python scripts/setup-openssl-tools-conan.py

# Setup GitHub Packages
python scripts/setup-github-packages-conan.py --github-owner=sparesparrow --github-repo=openssl-tools

# Set GitHub token
export GITHUB_TOKEN=your_token_here
```

### 2. Daily Development

```bash
# Activate environment
source conan-dev/activate  # Linux/macOS
# or
conan-dev\activate.bat     # Windows

# Build package
conan create . --profile=linux-gcc11

# Run tests
python scripts/test-openssl-tools-conan.py --profile=linux-gcc11

# Upload to GitHub Packages
python scripts/conan/upload-to-github-packages.py --profile=linux-gcc11
```

### 3. CI/CD Integration

The GitHub Actions workflow automatically:
- Builds on multiple platforms
- Runs comprehensive tests
- Uploads to GitHub Packages
- Generates SBOM

## 🔍 Troubleshooting

### Common Issues

#### 1. GitHub Token Issues

```bash
# Check token
echo $GITHUB_TOKEN

# Re-authenticate
conan remote login github-packages --username sparesparrow --password $GITHUB_TOKEN
```

#### 2. Profile Not Found

```bash
# List available profiles
conan profile list

# Create profile
conan profile detect --force
```

#### 3. Build Failures

```bash
# Clean build
conan remove "*" --confirm

# Verbose output
conan create . --profile=linux-gcc11 --verbose
```

#### 4. Python Environment Issues

```bash
# Recreate virtual environment
rm -rf conan-dev/venv
python scripts/setup-openssl-tools-conan.py --force
```

### Debug Commands

```bash
# Conan info
conan info .

# Profile details
conan profile show linux-gcc11

# Remote list
conan remote list

# Cache info
conan cache path
```

## 📊 Benefits

### Following ngapy Patterns

- **Python Environment Management**: Isolated virtual environment
- **Conan Integration**: Proper package management
- **SCM Integration**: Git-based versioning
- **Environment Variables**: PYTHONPATH and package configuration
- **Dependency Management**: Clear separation of concerns

### Conan 2.x Advantages

- **Modern API**: Latest Conan features
- **Better Performance**: Improved build times
- **GitHub Packages**: Native GitHub integration
- **Enhanced Security**: Better authentication
- **Improved Caching**: More efficient builds

### GitHub Packages Benefits

- **Integrated Storage**: Native GitHub integration
- **Access Control**: GitHub permissions
- **Version Management**: Git-based versioning
- **CI/CD Integration**: Seamless automation
- **Cost Effective**: No additional storage costs

## 🤝 Contributing

### Adding New Features

1. **Update conanfile.py**: Add new options or dependencies
2. **Update profiles**: Modify build configurations
3. **Update scripts**: Enhance automation
4. **Update tests**: Add test coverage
5. **Update documentation**: Keep docs current

### Testing Changes

```bash
# Test locally
python scripts/test-openssl-tools-conan.py --test-type=all --profile=linux-gcc11

# Test on multiple platforms
python scripts/test-openssl-tools-conan.py --test-type=conan --profile=windows-msvc2022
python scripts/test-openssl-tools-conan.py --test-type=conan --profile=macos-clang14
```

## 📚 References

- [Conan 2.x Documentation](https://docs.conan.io/2/)
- [GitHub Packages Documentation](https://docs.github.com/en/packages)
- [openssl-tools Patterns](https://bitbucket.honeywell.com/projects/NGAIMS/repos/openssl-tools)
- [OpenSSL Tools Repository](https://github.com/sparesparrow/openssl-tools)

## 🆘 Support

For issues and questions:

1. **Check logs**: Enable verbose output with `--verbose`
2. **Check documentation**: Review this README
3. **Check GitHub Issues**: Search existing issues
4. **Create new issue**: Provide detailed information

---

This setup provides a robust, scalable, and maintainable Python development environment with Conan 2.x and GitHub Packages, following proven patterns from openssl-tools while leveraging modern tooling and GitHub's ecosystem.