# OpenSSL Tools

Python tools for OpenSSL development, review, and release management with Conan integration.

## Overview

This package provides Python implementations of OpenSSL development tools, converted from the original Perl scripts and enhanced with modern Python features and Conan package management integration.

## Features

### Review Tools
- **addrev**: Add or edit reviewers to commits
- **gitaddrev**: Add reviewers to commit messages with CLA validation
- **ghmerge**: Merge GitHub pull requests with safety checks
- **gitlabutil**: GitLab merge request query tool
- **cherry-checker**: Check cherry-picked commits

### Release Tools
- **stage-release**: Stage OpenSSL releases
- **copyright-year**: Update copyright years in files
- **release-aux**: Release auxiliary tools

### Statistics Tools
- **bn-rand-range**: Generate statistical test data for BN_rand_range
- **statistical-analysis**: Statistical analysis tools

## Installation

### Using Conan (Recommended)

```bash
# Install the package
conan install openssl-tools/1.0.0@

# Or add to your conanfile.py
self.requires("openssl-tools/1.0.0")
```

### Using pip

```bash
# Install from source
pip install -e .

# Install with optional dependencies
pip install -e .[statistics,github,gitlab,dev]
```

## Usage

### Command Line Tools

All tools are available as command-line scripts:

```bash
# Review tools
addrev --prnum=1234 steve
gitaddrev --list
ghmerge 1234 steve levitte
gitlabutil --state=all
cherry-checker HEAD~10..HEAD

# Release tools
stage-release 3.5.0
copyright-year --year=2024
bn-rand-range --output=test/bn_rand_range.h
```

### Python API

```python
from openssl_tools.review_tools import AddRevTool, GitAddRevTool
from openssl_tools.release_tools import StageReleaseTool
from openssl_tools.statistics import BnRandRangeTool

# Use tools programmatically
addrev_tool = AddRevTool()
addrev_tool.run(['--prnum=1234', 'steve'])

stage_tool = StageReleaseTool()
stage_tool.run(['3.5.0'])
```

## Configuration

Tools can be configured using a `tools_config.json` file:

```json
{
  "tools": {
    "review_tools": {
      "enabled": true,
      "min_reviewers": 2,
      "min_otc": 0,
      "min_omc": 0,
      "api_endpoint": "https://api.openssl.org"
    },
    "release_tools": {
      "enabled": true,
      "templates_dir": "templates",
      "output_dir": "releases"
    },
    "statistics": {
      "enabled": true,
      "alpha_chi2": 0.95,
      "alpha_binomial": 0.9999
    }
  }
}
```

## Environment Variables

- `OPENSSL_TOOLS_CONFIG`: Path to configuration file
- `GITHUB_TOKEN`: GitHub API token for GitHub integration
- `GITLAB_TOKEN`: GitLab API token for GitLab integration
- `GITADDREV`: Path to gitaddrev executable

## Dependencies

### Core Dependencies
- Python 3.8+
- requests
- click
- pyyaml
- jinja2

### Optional Dependencies
- numpy, scipy (for statistics tools)
- pygithub (for GitHub integration)
- python-gitlab (for GitLab integration)

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/sparesparrow/openssl-tools.git
cd openssl-tools

# Install in development mode
pip install -e .[dev]

# Run tests
pytest

# Format code
black openssl_tools/

# Lint code
flake8 openssl_tools/
```

### Conan Integration

The package is designed to work with Conan package manager:

```python
# In your conanfile.py
class MyConanFile(ConanFile):
    def requirements(self):
        self.requires("openssl-tools/1.0.0")
    
    def build(self):
        # Use OpenSSL tools in your build
        pass
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

Licensed under the Apache License 2.0. See LICENSE file for details.

## Acknowledgments

- Original OpenSSL tools team for the Perl implementations
- OpenSSL community for feedback and contributions
- Conan team for the package management system