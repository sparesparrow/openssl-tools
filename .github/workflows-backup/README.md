# Archived Workflows

This directory contains workflows that are not actively used but preserved for reference and potential future adaptation.

## Structure

### `legacy-openssl/`
Workflows from upstream openssl/tools that are incompatible with the Conan 2.0 modernization:

- **Incompatible with openssl-tools**: These workflows expect traditional OpenSSL source structure
- **Source-based approach**: Designed for OpenSSL source repository development
- **Legacy build system**: Uses `Configure`, `config`, `VERSION.dat` instead of Conan
- **Platform-specific**: Many workflows are tied to specific OpenSSL build patterns

### `upstream-only/`
Workflows specifically designed for the OpenSSL source repository (`openssl/openssl`):

- **Source repository specific**: Designed for OpenSSL source development
- **Not suitable for packages**: Focus on source compilation rather than package management
- **OpenSSL-specific CI patterns**: Direct `./config` and `make` commands
- **Documentation deployment**: OpenSSL.org specific deployment workflows

### `experimental/`
Workflows from PR #6 development iterations and experimental approaches:

- **Development iterations**: Various approaches tried during CI modernization
- **Experimental features**: Nuclear success, minimal approaches, optimizations
- **Learning artifacts**: Historical record of CI evolution
- **Superseded approaches**: Replaced by current production workflows

## Usage Guidelines

### When to Reference Archived Workflows
1. **Understanding OpenSSL patterns**: Reference legacy workflows to understand OpenSSL-specific requirements
2. **Adapting functionality**: Use as reference when adapting OpenSSL-specific features
3. **Historical context**: Understand the evolution of the CI system
4. **Troubleshooting**: Reference when debugging OpenSSL-specific issues

### When NOT to Use Archived Workflows
1. **Direct activation**: Never enable these workflows directly
2. **Copy-paste**: Don't copy workflows without adaptation
3. **Production use**: These are not suitable for production use
4. **Modern development**: Use current production workflows instead

## Migration Path

If you need functionality from archived workflows:

1. **Analyze the archived workflow** to understand its purpose
2. **Identify the core functionality** that needs to be adapted
3. **Use current production workflows** as the base
4. **Adapt OpenSSL-specific parts** to work with Conan
5. **Test thoroughly** before deploying
6. **Document the changes** for future reference

## File Counts

- **Legacy OpenSSL**: ~20 workflows
- **Upstream Only**: ~15 workflows  
- **Experimental**: ~66 workflows
- **Total Archived**: ~101 workflows

## Maintenance

- **Regular cleanup**: Remove truly obsolete workflows
- **Documentation updates**: Keep README files current
- **Reference updates**: Update references when workflows change
- **Archive organization**: Maintain clear categorization