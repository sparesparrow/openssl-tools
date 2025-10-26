# OpenSSL Database Schema Validation

This system provides comprehensive database schema validation for OpenSSL configuration and package tracking across all build stages.

## Features

- **Configuration Validation**: Validates OpenSSL build configurations against schema
- **Package Tracking**: Tracks packages in Conan cache with database validation
- **Build Stage Monitoring**: Monitors build stages (foundation, tooling, domain, orchestration)
- **Cache Management**: Validates and manages Conan package cache
- **Reporting**: Generates comprehensive reports on cache status and validation results

## Usage

### Setup
```bash
# Run the setup script
./scripts/setup_openssl_database_validation.sh
```

### Validate Configurations
```bash
# Validate a specific configuration
python3 -m openssl_tools.database.openssl_schema_validator \
    --action validate-config \
    --config-file openssl-config/general-build.json
```

### Track Packages
```bash
# Track a package in cache
python3 -m openssl_tools.database.openssl_schema_validator \
    --action track-package \
    --package-info '{"name":"openssl","version":"3.4.1","user":"sparesparrow","channel":"stable","package_id":"abc123"}' \
    --build-stage domain
```

### Cache Management
```bash
# Validate existing cache
python3 scripts/conan/integrate_cache_validation.py --action validate

# Generate cache report
python3 scripts/conan/integrate_cache_validation.py --action report

# Monitor cache changes
python3 scripts/conan/integrate_cache_validation.py --action monitor
```

### Generate Reports
```bash
# Generate cache report
python3 -m openssl_tools.database.openssl_schema_validator \
    --action generate-report
```

## Database Schema

The system uses SQLite databases to track:

- **Build Configurations**: OpenSSL build configurations and their validation status
- **Package Cache**: Packages stored in Conan cache with validation results
- **Build Stages**: Build stage tracking and dependencies
- **Validation Results**: Detailed validation results for each package

## Configuration Files

- `openssl-config/*.json`: OpenSSL build configurations
- `conan-dev/cache-monitoring.yml`: Cache monitoring configuration
- `conan-dev/hooks/*.py`: Conan hooks for package tracking

## Reports

Reports are generated in:
- `conan-dev/schema-reports/`: Schema validation reports
- `conan-dev/cache-validation-report.md`: Comprehensive cache report
- `conan-dev/cache-validation-results.json`: Detailed validation results

## Integration with Conan

The system integrates with Conan through:
- **Hooks**: Automatic package tracking on creation/removal
- **Extensions**: Custom Conan commands for validation
- **Cache Monitoring**: Real-time cache validation

## Troubleshooting

### Common Issues

1. **Database not found**: Run the setup script to create databases
2. **Validation failures**: Check configuration files for syntax errors
3. **Cache issues**: Validate existing cache and clean if necessary

### Debug Commands

```bash
# Check database status
sqlite3 conan-dev/package-cache.db "SELECT COUNT(*) FROM package_cache;"

# View validation results
sqlite3 conan-dev/validation-results.db "SELECT * FROM validation_results LIMIT 10;"

# Check build configurations
sqlite3 conan-dev/build-configurations.db "SELECT * FROM build_configurations;"
```
