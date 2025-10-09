# JFrog Artifactory Setup Guide

This guide provides comprehensive instructions for setting up JFrog Artifactory integration with the OpenSSL Tools repository.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Artifactory Instance Setup](#artifactory-instance-setup)
- [Repository Configuration](#repository-configuration)
- [Secrets Configuration](#secrets-configuration)
- [Conan Integration](#conan-integration)
- [Workflow Configuration](#workflow-configuration)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

## Overview

JFrog Artifactory serves as the central package repository for OpenSSL builds, providing:

- **Package Storage**: Centralized storage for Conan packages
- **Version Management**: Semantic versioning and release management
- **Access Control**: Fine-grained permissions and security
- **Caching**: Intelligent caching for faster builds
- **Integration**: Seamless integration with CI/CD workflows

## Prerequisites

Before setting up Artifactory integration, ensure you have:

- JFrog Artifactory instance (Cloud or self-hosted)
- Administrative access to the Artifactory instance
- GitHub repository with appropriate permissions
- Conan 2.x installed locally (for testing)

## Artifactory Instance Setup

### 1. Create Artifactory Instance

#### Option A: JFrog Cloud (Recommended for most users)

1. Go to [JFrog Cloud](https://jfrog.com/cloud/)
2. Sign up for a free account or choose a paid plan
3. Create a new Artifactory instance
4. Note your instance URL (e.g., `https://your-instance.jfrog.io`)

#### Option B: Self-Hosted

1. Download Artifactory from [JFrog Downloads](https://jfrog.com/download/)
2. Follow the installation guide for your platform
3. Configure your instance URL

### 2. Create Conan Repository

1. Log into your Artifactory instance
2. Navigate to **Administration** → **Repositories**
3. Click **Add Repository** → **Conan**
4. Configure the repository:
   - **Repository Key**: `conan-local`
   - **Description**: `OpenSSL Conan Packages`
   - **Package Type**: `Conan`
   - **Repository Layout**: `conan-default`
   - **Handle Releases**: `Yes`
   - **Handle Snapshots**: `Yes`

### 3. Configure Security

1. Navigate to **Administration** → **Security** → **Users**
2. Create a dedicated user for CI/CD:
   - **Username**: `openssl-ci`
   - **Email**: `openssl-ci@yourdomain.com`
   - **Password**: Generate a strong password
3. Assign appropriate permissions:
   - **Read**: `conan-local`
   - **Write**: `conan-local`
   - **Delete**: `conan-local` (optional)

## Repository Configuration

### 1. Add Artifactory Remote

Add your Artifactory instance as a Conan remote:

```bash
# Add the remote
conan remote add artifactory https://your-instance.jfrog.io/artifactory/api/conan/conan-local

# Authenticate
conan user -r artifactory openssl-ci
# Enter the password when prompted
```

### 2. Verify Connection

Test the connection to Artifactory:

```bash
# List packages in the remote
conan search "*" -r artifactory

# Upload a test package
conan create . openssl/3.5.0@test/test
conan upload openssl/3.5.0@test/test -r artifactory
```

## Secrets Configuration

### Required GitHub Secrets

Add the following secrets to your GitHub repository:

#### Core Secrets
```yaml
# Artifactory connection
ARTIFACTORY_URL: "https://your-instance.jfrog.io"
ARTIFACTORY_USERNAME: "openssl-ci"
ARTIFACTORY_PASSWORD: "your-strong-password"
ARTIFACTORY_API_KEY: "your-api-key"

# Conan authentication
CONAN_LOGIN_USERNAME: "openssl-ci"
CONAN_PASSWORD: "your-strong-password"

# GitHub integration
OPENSSL_TOOLS_TOKEN: "your-github-token"
```

#### Optional Secrets
```yaml
# Package signing
ARTIFACTORY_SIGNING_KEY: "your-private-key"
ARTIFACTORY_SIGNING_PASSPHRASE: "your-passphrase"

# Additional integrations
GITHUB_TOKEN: "your-github-token"
```

### Setting Up Secrets

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret with the exact name and value
5. Click **Add secret** to save

### Generating API Key

To generate an Artifactory API key:

1. Log into Artifactory
2. Click on your username in the top-right corner
3. Select **User Profile**
4. Go to **Authentication Settings**
5. Click **Generate API Key**
6. Copy the generated key

## Conan Integration

### 1. Configure Conan Client

Create a Conan configuration file:

```ini
# ~/.conan2/conan.conf
[storage]
path = ~/.conan2/storage

[remotes]
artifactory = https://your-instance.jfrog.io/artifactory/api/conan/conan-local

[log]
level = info

[general]
default_profile = default
```

### 2. Create Profiles

Create build profiles for different platforms:

```ini
# ~/.conan2/profiles/default
[settings]
os=Linux
arch=x86_64
compiler=gcc
compiler.version=11
compiler.libcxx=libstdc++11
build_type=Release

[options]
openssl:shared=True
openssl:fips=False

[conf]
tools.system.package_manager:mode=install
tools.system.package_manager:sudo=True
```

### 3. Package Configuration

Configure the OpenSSL package recipe:

```python
# conanfile.py
from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout

class OpenSSLConan(ConanFile):
    name = "openssl"
    version = "3.5.0"
    
    # Package metadata
    description = "OpenSSL library"
    license = "Apache-2.0"
    url = "https://github.com/openssl/openssl"
    homepage = "https://www.openssl.org"
    
    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fips": [True, False],
    }
    default_options = {
        "shared": True,
        "fips": False,
    }
    
    def configure(self):
        if self.options.fips:
            self.options.shared = False
    
    def layout(self):
        cmake_layout(self)
    
    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
    
    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
    
    def package(self):
        cmake = CMake(self)
        cmake.install()
    
    def package_info(self):
        self.cpp_info.libs = ["ssl", "crypto"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["dl", "pthread"]
```

## Workflow Configuration

### 1. Package Upload Workflow

Create a workflow for uploading packages to Artifactory:

```yaml
# .github/workflows/package-upload.yml
name: Package Upload

on:
  push:
    branches: [main, develop]
  workflow_dispatch:

jobs:
  upload-package:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install Conan
        run: |
          pip install conan
          conan config install conan/
      
      - name: Configure Artifactory
        run: |
          conan remote add artifactory ${{ secrets.ARTIFACTORY_URL }}/artifactory/api/conan/conan-local
          conan user -r artifactory ${{ secrets.ARTIFACTORY_USERNAME }} -p ${{ secrets.ARTIFACTORY_PASSWORD }}
      
      - name: Build Package
        run: |
          conan create . openssl/3.5.0@test/test
      
      - name: Upload Package
        run: |
          conan upload openssl/3.5.0@test/test -r artifactory --confirm
```

### 2. Cache Warm-up Workflow

Create a workflow for warming up the Artifactory cache:

```yaml
# .github/workflows/cache-warmup.yml
name: Cache Warm-up

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
  workflow_dispatch:

jobs:
  warmup-cache:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        platform: [linux, macos, windows]
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install Conan
        run: pip install conan
      
      - name: Configure Artifactory
        run: |
          conan remote add artifactory ${{ secrets.ARTIFACTORY_URL }}/artifactory/api/conan/conan-local
          conan user -r artifactory ${{ secrets.ARTIFACTORY_USERNAME }} -p ${{ secrets.ARTIFACTORY_PASSWORD }}
      
      - name: Warm up Cache
        run: |
          conan install openssl/3.5.0@test/test -r artifactory
```

## Testing

### 1. Local Testing

Test the Artifactory integration locally:

```bash
# Configure Conan
conan config install conan/

# Add Artifactory remote
conan remote add artifactory https://your-instance.jfrog.io/artifactory/api/conan/conan-local

# Authenticate
conan user -r artifactory openssl-ci

# Test package creation
conan create . openssl/3.5.0@test/test

# Test package upload
conan upload openssl/3.5.0@test/test -r artifactory --confirm

# Test package download
conan install openssl/3.5.0@test/test -r artifactory
```

### 2. Workflow Testing

Test the GitHub workflows:

1. Create a test branch
2. Make a small change to trigger the workflow
3. Push the changes
4. Monitor the workflow execution
5. Verify packages are uploaded to Artifactory

### 3. Integration Testing

Test the complete integration:

1. Build packages using the build matrix
2. Upload packages to Artifactory
3. Download packages from Artifactory
4. Verify package integrity and functionality

## Troubleshooting

### Common Issues

#### Authentication Failures

**Problem**: Cannot authenticate with Artifactory

**Solutions**:
- Verify username and password are correct
- Check if the user has appropriate permissions
- Ensure the Artifactory URL is correct
- Verify the API key is valid

#### Package Upload Failures

**Problem**: Packages fail to upload

**Solutions**:
- Check network connectivity
- Verify repository permissions
- Ensure package format is correct
- Check for duplicate packages

#### Workflow Failures

**Problem**: GitHub workflows fail

**Solutions**:
- Verify all secrets are set correctly
- Check workflow syntax
- Review workflow logs for specific errors
- Ensure proper permissions are granted

### Debugging Steps

1. **Check Logs**: Review workflow logs for detailed error messages
2. **Verify Secrets**: Ensure all required secrets are set
3. **Test Locally**: Test commands locally before running in workflows
4. **Check Permissions**: Verify user permissions in Artifactory
5. **Network Issues**: Check for network connectivity problems

### Getting Help

- Check the [GitHub Issues](https://github.com/sparesparrow/openssl-tools/issues)
- Review Artifactory documentation
- Consult Conan documentation
- Check workflow logs for specific error messages

## Security Best Practices

### 1. Secret Management

- Use strong, unique passwords
- Rotate secrets regularly
- Use API keys instead of passwords when possible
- Limit secret access to necessary workflows only

### 2. Access Control

- Create dedicated users for CI/CD
- Use minimal required permissions
- Regularly review and audit access
- Implement proper authentication

### 3. Package Security

- Sign packages when possible
- Verify package integrity
- Use secure channels for package transfer
- Implement proper versioning

## Maintenance

### Regular Tasks

1. **Secret Rotation**: Rotate secrets every 90 days
2. **Permission Review**: Review user permissions quarterly
3. **Package Cleanup**: Clean up old packages regularly
4. **Security Updates**: Keep Artifactory updated
5. **Monitoring**: Monitor usage and performance

### Monitoring

- Set up alerts for failed uploads
- Monitor storage usage
- Track package download statistics
- Review access logs regularly

## Conclusion

This guide provides comprehensive instructions for setting up JFrog Artifactory integration with the OpenSSL Tools repository. Follow the steps carefully and test thoroughly to ensure proper integration.

For additional support or questions, please refer to the troubleshooting section or open an issue on GitHub.