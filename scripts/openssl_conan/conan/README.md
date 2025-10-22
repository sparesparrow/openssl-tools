# OpenSSL Conan Integration

This directory contains advanced Conan scripts for the OpenSSL project, providing comprehensive package management and build automation capabilities.

## Quick Start

1. **Run the integration script:**
   ```bash
   python scripts/openssl_conan/conan/integrate_with_openssl.py
   ```

2. **Use the example script:**
   ```bash
   python scripts/openssl_conan/conan/openssl_conan_example.py
   ```

3. **Use the helper script:**
   ```bash
   python openssl_conan_helper.py
   ```

## Files

- **`conan_functions.py`** - Core Conan functionality
- **`artifactory_functions.py`** - Artifactory integration
- **`client_config.py`** - Configuration management
- **`conan_artifactory_search.py`** - Package search and discovery
- **`pyupdater_downloader.py`** - File download utilities
- **`test_*.py`** - Unit tests
- **`openssl_conan_example.py`** - Usage examples
- **`integrate_with_openssl.py`** - Integration script

## Features

- ✅ Advanced package management
- ✅ Artifactory integration
- ✅ Configuration tracking
- ✅ Build automation
- ✅ Security scanning
- ✅ CI/CD integration
- ✅ Comprehensive testing
- ✅ Detailed documentation

## Documentation

See `docs/OPENSSL_CONAN_INTEGRATION.md` for detailed documentation.

## Testing

Run the tests:
```bash
python -m pytest scripts/openssl_conan/conan/test_*.py -v
```

## License

Part of the OpenSSL project.