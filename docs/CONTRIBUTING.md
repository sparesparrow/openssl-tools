# Contributing to OpenSSL Tools

Thank you for your interest in contributing to OpenSSL Tools! This document provides guidelines for contributing to the build infrastructure and tooling for the OpenSSL project.

## What is OpenSSL Tools?

OpenSSL Tools is a **companion repository** that provides build infrastructure for the [OpenSSL project](https://github.com/sparesparrow/openssl). It contains:

- CI/CD workflows for multi-platform builds
- Conan package management integration
- Build optimization and caching tools
- Performance benchmarking and testing
- Security scanning and compliance tools

**Important**: This repository does NOT contain OpenSSL source code. For OpenSSL source contributions, see the [OpenSSL repository](https://github.com/sparesparrow/openssl).

## Repository Separation

### OpenSSL Repository
- **Purpose**: OpenSSL source code and core functionality
- **Contributions**: Cryptographic algorithms, SSL/TLS implementation, core features
- **Location**: [sparesparrow/openssl](https://github.com/sparesparrow/openssl)

### OpenSSL Tools Repository (This Repository)
- **Purpose**: Build infrastructure, CI/CD, and development tooling
- **Contributions**: Build scripts, CI workflows, package management, testing tools
- **Location**: [sparesparrow/openssl-tools](https://github.com/sparesparrow/openssl-tools)

## Getting Started

### Prerequisites

- Python 3.8+ (we support 3.8, 3.9, 3.10, 3.11, 3.12)
- Git
- Basic understanding of CI/CD concepts
- Familiarity with Conan package manager (helpful but not required)

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/openssl-tools.git
   cd openssl-tools
   ```

2. **Set Up Python Environment**
   ```bash
   # Use our automated setup
   python setup_python_env.py --versions 3.11
   
   # Or manually
   python3.11 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. **Configure Conan (Optional)**
   ```bash
   # Set up Conan with GitHub Packages
   export GITHUB_TOKEN="your_token"
   python conan_remote_manager.py --setup
   ```

4. **Verify Setup**
   ```bash
   # Run tests
   python -m pytest tests/
   
   # Check scripts
   python scripts/conan/conan_orchestrator.py --help
   ```

## Contribution Workflow

### 1. Choose What to Contribute

**Infrastructure Improvements**:
- CI/CD workflow enhancements
- Build optimization scripts
- Package management improvements
- Performance benchmarking tools

**Documentation**:
- Setup guides and tutorials
- API documentation
- Troubleshooting guides
- Architecture explanations

**Testing and Quality**:
- Test coverage improvements
- Security scanning enhancements
- Performance regression detection
- Integration testing

### 2. Create a Branch

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Or bugfix branch
git checkout -b fix/issue-description
```

### 3. Make Your Changes

**Code Style**:
- Follow PEP 8 for Python code
- Use type hints for function parameters and return values
- Add docstrings for all public functions and classes
- Use meaningful variable and function names

**Testing**:
- Add tests for new functionality
- Ensure existing tests still pass
- Update integration tests if needed

**Documentation**:
- Update relevant documentation
- Add examples for new features
- Update README if needed

### 4. Test Your Changes

```bash
# Run all tests
python -m pytest tests/

# Run specific test categories
python -m pytest tests/test_scripts.py
python -m pytest tests/test_integration.py

# Check code quality
flake8 scripts/
black --check scripts/
mypy scripts/

# Test CI workflows (if applicable)
# Create a test PR to verify workflow changes
```

### 5. Submit a Pull Request

1. **Push your branch**:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create Pull Request**:
   - Use clear, descriptive title
   - Provide detailed description of changes
   - Link to any related issues
   - Include screenshots for UI changes

3. **PR Description Template**:
   ```markdown
   ## Description
   Brief description of changes

   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Documentation update
   - [ ] CI/CD improvement
   - [ ] Performance optimization

   ## Testing
   - [ ] Tests added/updated
   - [ ] All tests pass
   - [ ] Manual testing completed

   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Documentation updated
   - [ ] No breaking changes (or documented)
   ```

## Code Review Process

### Review Criteria

**Functionality**:
- Does the code work as intended?
- Are edge cases handled properly?
- Is error handling comprehensive?

**Code Quality**:
- Is the code readable and maintainable?
- Are there any security vulnerabilities?
- Is performance acceptable?

**Testing**:
- Are tests comprehensive?
- Do tests cover edge cases?
- Are integration tests updated?

**Documentation**:
- Is documentation clear and complete?
- Are examples provided?
- Is the change properly documented?

### Review Process

1. **Automated Checks**: CI/CD runs automatically
2. **Code Review**: At least one maintainer reviews
3. **Testing**: Manual testing for complex changes
4. **Approval**: Maintainer approval required
5. **Merge**: Squash and merge preferred

## Development Guidelines

### Python Development

**Code Style**:
```python
# Use type hints
def process_build(config: BuildConfig) -> BuildResult:
    """Process build configuration and return results."""
    pass

# Use meaningful names
build_cache_hit_rate = calculate_cache_metrics()

# Handle errors properly
try:
    result = risky_operation()
except SpecificException as e:
    logger.error(f"Operation failed: {e}")
    raise
```

**Testing**:
```python
# Use pytest fixtures
@pytest.fixture
def sample_config():
    return BuildConfig(platform="linux", compiler="gcc")

def test_build_process(sample_config):
    result = process_build(sample_config)
    assert result.success
    assert result.build_time > 0
```

### CI/CD Development

**Workflow Guidelines**:
- Use descriptive job names
- Add proper error handling
- Include timeout settings
- Use appropriate permissions
- Add manual triggers for testing

**Example**:
```yaml
name: Test Workflow
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: python -m pytest tests/
```

### Documentation Guidelines

**Structure**:
- Use clear headings and subheadings
- Provide code examples
- Include troubleshooting sections
- Link to related documentation

**Style**:
- Use active voice
- Be concise but complete
- Include screenshots for UI changes
- Update table of contents

## Testing Requirements

### Test Categories

**Unit Tests**:
- Test individual functions and classes
- Mock external dependencies
- Cover edge cases and error conditions

**Integration Tests**:
- Test component interactions
- Use real external services when possible
- Test end-to-end workflows

**Performance Tests**:
- Benchmark critical operations
- Test with large datasets
- Monitor for regressions

### Test Coverage

- **Minimum**: 80% line coverage
- **Target**: 90% line coverage
- **Critical paths**: 100% coverage

### Running Tests

```bash
# All tests
python -m pytest

# With coverage
python -m pytest --cov=scripts --cov-report=html

# Specific test file
python -m pytest tests/test_scripts.py

# Specific test function
python -m pytest tests/test_scripts.py::test_specific_function
```

## Security Guidelines

### Security Considerations

**Secrets Management**:
- Never commit secrets to repository
- Use GitHub Secrets for CI/CD
- Rotate secrets regularly
- Use least-privilege access

**Code Security**:
- Validate all inputs
- Use secure coding practices
- Regular security scanning
- Keep dependencies updated

**Package Security**:
- Sign all packages
- Verify package integrity
- Scan for vulnerabilities
- Maintain audit trails

### Security Testing

```bash
# Security scanning
bandit -r scripts/
safety check
semgrep --config=auto scripts/

# Dependency scanning
pip-audit
```

## Performance Guidelines

### Performance Considerations

**Build Performance**:
- Optimize cache usage
- Use parallel execution
- Minimize I/O operations
- Profile critical paths

**CI/CD Performance**:
- Use appropriate runners
- Cache dependencies
- Optimize job dependencies
- Monitor resource usage

### Performance Testing

```bash
# Benchmark critical operations
python -m pytest tests/test_performance.py

# Profile memory usage
python -m memory_profiler script.py

# Monitor build times
python build_optimizer.py --stats
```

## Release Process

### Versioning

We use [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

- [ ] All tests pass
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version bumped
- [ ] Security scan clean
- [ ] Performance benchmarks updated

## Getting Help

### Support Channels

**GitHub Issues**:
- Bug reports
- Feature requests
- Questions about usage

**Discussions**:
- General questions
- Architecture discussions
- Community support

**Documentation**:
- [Getting Started Guide](docs/tutorials/getting-started.md)
- [API Reference](docs/reference/)
- [Troubleshooting](docs/how-to/troubleshooting.md)

### Community Guidelines

**Be Respectful**:
- Use inclusive language
- Be patient with newcomers
- Provide constructive feedback

**Be Helpful**:
- Answer questions when you can
- Share knowledge and experience
- Contribute to documentation

**Be Professional**:
- Follow the code of conduct
- Keep discussions on-topic
- Respect maintainer decisions

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE-OF-CONDUCT.md). By participating, you agree to uphold this code.

## License

By contributing to OpenSSL Tools, you agree that your contributions will be licensed under the same license as the project (MIT License).

---

Thank you for contributing to OpenSSL Tools! Your contributions help make OpenSSL development more efficient and reliable for everyone.