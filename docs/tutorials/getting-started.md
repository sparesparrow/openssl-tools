# Getting Started with OpenSSL Tools

This tutorial will help you set up OpenSSL Tools for the first time. OpenSSL Tools provides build infrastructure for the OpenSSL project, including CI/CD workflows, package management, and development tooling.

## Prerequisites

Before you begin, ensure you have:

- **Python 3.8+** (we support 3.8, 3.9, 3.10, 3.11, 3.12)
- **Git** for version control
- **GitHub account** for repository access
- **Basic command-line knowledge**

## Quick Start (5 minutes)

### 1. Clone the Repository

```bash
git clone https://github.com/sparesparrow/openssl-tools.git
cd openssl-tools
```

### 2. Set Up Python Environment

Use our automated setup script:

```bash
python setup_python_env.py --versions 3.11
```

This will:
- Create isolated Python environments
- Install required dependencies
- Configure Conan package manager
- Set up build tools

### 3. Verify Installation

```bash
# Check Python environment
python --version

# Check Conan installation
conan --version

# Run basic tests
python -m pytest tests/ -v
```

### 4. Configure GitHub Integration (Optional)

If you want to use GitHub Packages:

```bash
# Set your GitHub token
export GITHUB_TOKEN="your_github_token"

# Configure Conan with GitHub Packages
python conan_remote_manager.py --setup
```

## Detailed Setup

### Python Environment Management

OpenSSL Tools supports multiple Python versions. The setup script creates isolated environments for each version:

```bash
# Set up specific Python versions
python setup_python_env.py --versions 3.9,3.11,3.12

# Set up all supported versions
python setup_python_env.py --all

# Check installed versions
python setup_python_env.py --list
```

**Manual Setup** (if you prefer):
```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Conan Configuration

Conan is used for package management. Configure it for your environment:

```bash
# Basic Conan setup
conan config install conan/

# Add GitHub Packages remote
conan remote add github-packages https://maven.pkg.github.com/sparesparrow/index.json

# Authenticate with GitHub
conan user -r github-packages your-username
```

### Build Profiles

OpenSSL Tools includes pre-configured build profiles:

```bash
# List available profiles
ls conan-profiles/

# Use a specific profile
conan create . --profile=conan-profiles/linux-gcc-release.profile
```

## First Build

### Trigger OpenSSL Build

To trigger a build of OpenSSL using the tools:

```bash
# Create a test build
python scripts/conan/conan_orchestrator.py --action create --profile linux-gcc-release

# Or use Conan directly
conan create . --profile=conan-profiles/linux-gcc-release.profile
```

### Monitor Build Progress

```bash
# Check build status
python scripts/conan/conan_orchestrator.py --action status

# View build logs
tail -f build.log
```

## Understanding the Structure

### Repository Layout

```
openssl-tools/
├── .github/workflows/          # CI/CD workflows
├── scripts/                    # Python automation scripts
│   ├── conan/                 # Conan package management
│   ├── ci/                    # CI/CD automation
│   └── validation/            # Build validation tools
├── conan/                     # Conan configuration
├── conan-dev/                 # Development Conan profiles
├── conan-profiles/            # Production Conan profiles
├── docs/                      # Documentation
└── test_package/              # Conan test package
```

### Key Components

**CI/CD Workflows** (`.github/workflows/`):
- `openssl-ci-dispatcher.yml` - Main CI dispatcher
- `tools-ci.yml` - Tools-specific CI
- `jfrog-artifactory.yml` - Artifactory integration

**Scripts** (`scripts/`):
- `conan_orchestrator.py` - Main Conan orchestration
- `build_optimizer.py` - Build cache optimization
- `package_signer.py` - Package signing

**Configuration** (`conan/`, `conan-dev/`):
- Conan profiles for different platforms
- Build configurations
- Environment settings

## Common Tasks

### Building OpenSSL

```bash
# Build with default profile
conan create . --profile=conan-profiles/linux-gcc-release.profile

# Build with specific options
conan create . --profile=conan-profiles/linux-gcc-release.profile -o openssl:shared=True

# Build for FIPS
conan create . --profile=conan-profiles/linux-fips.profile
```

### Managing Cache

```bash
# Check cache status
python build_optimizer.py --stats

# Clean cache
python build_optimizer.py --clean

# Optimize cache
python build_optimizer.py --optimize
```

### Package Management

```bash
# Upload packages
python conan_remote_manager.py --action upload --remote github-packages

# Search packages
conan search openssl --remote=github-packages

# Install packages
conan install openssl/3.5.0@openssl/stable
```

## Integration with OpenSSL Repository

OpenSSL Tools is designed to work with the [OpenSSL repository](https://github.com/sparesparrow/openssl):

### Cross-Repository Workflow

1. **Make changes** in OpenSSL repository
2. **Create PR** in OpenSSL repository
3. **Basic validation** runs in OpenSSL repository
4. **Comprehensive build** triggers in OpenSSL Tools
5. **Build results** reported back to OpenSSL PR

### Understanding the Separation

- **OpenSSL Repository**: Source code and core functionality
- **OpenSSL Tools Repository**: Build infrastructure and tooling

See [Repository Separation Explained](../explanation/repo-separation.md) for details.

## Troubleshooting

### Common Issues

**Python Environment Issues**:
```bash
# Recreate environment
python setup_python_env.py --clean --versions 3.11

# Check Python path
which python
python -c "import sys; print(sys.path)"
```

**Conan Issues**:
```bash
# Reset Conan configuration
conan config install conan/ --force

# Check Conan version
conan --version

# Verify profiles
conan profile list
```

**Build Issues**:
```bash
# Check build logs
cat build.log

# Clean build directory
rm -rf build/

# Rebuild from scratch
conan create . --profile=conan-profiles/linux-gcc-release.profile --build=missing
```

### Getting Help

1. **Check Documentation**: Browse the [documentation hub](../README.md)
2. **Search Issues**: Look for similar issues in [GitHub Issues](https://github.com/sparesparrow/openssl-tools/issues)
3. **Ask Questions**: Create a [GitHub Discussion](https://github.com/sparesparrow/openssl-tools/discussions)
4. **Report Bugs**: Create a [GitHub Issue](https://github.com/sparesparrow/openssl-tools/issues/new)

## Next Steps

Now that you have OpenSSL Tools set up:

1. **Learn More**: Read [Local Development](local-development.md) for development workflow
2. **Configure CI/CD**: See [Setup Artifactory](../how-to/setup-artifactory.md) for package repository setup
3. **Understand Architecture**: Explore [Architecture](../explanation/architecture.md) for system overview
4. **Contribute**: Check [Contributing Guide](../../CONTRIBUTING.md) for contribution guidelines

## Additional Resources

- [Conan Documentation](https://docs.conan.io/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [OpenSSL Documentation](https://www.openssl.org/docs/)
- [Project Status](../../STATUS.md)

---

**Need Help?** Check the [Troubleshooting Guide](../how-to/troubleshooting.md) or [ask the community](https://github.com/sparesparrow/openssl-tools/discussions).
