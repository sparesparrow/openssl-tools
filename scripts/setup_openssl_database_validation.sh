#!/bin/bash
#
# Setup OpenSSL Database Schema Validation System
# Comprehensive setup script for OpenSSL configuration validation and package tracking
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Ensure we're in the openssl-tools directory
if [[ ! -f "$PROJECT_ROOT/scripts/conan/integrate_cache_validation.py" ]]; then
    echo "Error: Script not found in expected location"
    echo "Expected: $PROJECT_ROOT/scripts/conan/integrate_cache_validation.py"
    echo "Current directory: $(pwd)"
    echo "Script directory: $SCRIPT_DIR"
    echo "Project root: $PROJECT_ROOT"
    exit 1
fi

echo -e "${BLUE}🚀 OpenSSL Database Schema Validation Setup${NC}"
echo "=================================================="
echo "Project Root: $PROJECT_ROOT"
echo ""

# Function to print status
print_status() {
    local status=$1
    local message=$2
    if [ "$status" = "success" ]; then
        echo -e "${GREEN}✅ $message${NC}"
    elif [ "$status" = "warning" ]; then
        echo -e "${YELLOW}⚠️  $message${NC}"
    elif [ "$status" = "error" ]; then
        echo -e "${RED}❌ $message${NC}"
    else
        echo -e "${BLUE}ℹ️  $message${NC}"
    fi
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
print_status "info" "Checking prerequisites..."

if ! command_exists python3; then
    print_status "error" "Python 3 is required but not installed"
    exit 1
fi

if ! command_exists sqlite3; then
    print_status "warning" "SQLite3 is not installed - some features may not work"
fi

print_status "success" "Prerequisites check completed"

# Setup database schema validation
print_status "info" "Setting up database schema validation system..."

cd "$PROJECT_ROOT"

# Run the cache validation setup
if python3 "$PROJECT_ROOT/scripts/conan/integrate_cache_validation.py" --action setup; then
    print_status "success" "Database schema validation system setup completed"
else
    print_status "error" "Failed to setup database schema validation system"
    exit 1
fi

# Validate existing cache
print_status "info" "Validating existing Conan cache..."

if python3 "$PROJECT_ROOT/scripts/conan/integrate_cache_validation.py" --action validate; then
    print_status "success" "Cache validation completed"
else
    print_status "warning" "Cache validation had issues but continued"
fi

# Generate initial report
print_status "info" "Generating initial cache report..."

if python3 "$PROJECT_ROOT/scripts/conan/integrate_cache_validation.py" --action report; then
    print_status "success" "Initial cache report generated"
else
    print_status "warning" "Failed to generate initial cache report"
fi

# Create sample OpenSSL configurations
print_status "info" "Creating sample OpenSSL configurations..."

CONFIG_DIR="$PROJECT_ROOT/openssl-config"
mkdir -p "$CONFIG_DIR"

# Create sample configurations
cat > "$CONFIG_DIR/general-build.json" << 'EOF'
{
  "config_name": "general-build",
  "openssl_version": "3.4.1",
  "fips_enabled": false,
  "enable_quic": true,
  "enable_ktls": true,
  "enable_zlib": true,
  "enable_zstd": true,
  "shared": true,
  "deployment_target": "general",
  "description": "General purpose OpenSSL build with modern features"
}
EOF

cat > "$CONFIG_DIR/fips-government.json" << 'EOF'
{
  "config_name": "fips-government",
  "openssl_version": "3.4.1",
  "fips_enabled": true,
  "enable_quic": false,
  "enable_ktls": false,
  "enable_zlib": false,
  "enable_zstd": false,
  "shared": false,
  "deployment_target": "fips-government",
  "description": "FIPS 140-3 compliant build for government use"
}
EOF

cat > "$CONFIG_DIR/embedded-build.json" << 'EOF'
{
  "config_name": "embedded-build",
  "openssl_version": "3.4.1",
  "fips_enabled": false,
  "enable_quic": false,
  "enable_ktls": false,
  "enable_zlib": false,
  "enable_zstd": false,
  "no_asm": true,
  "no_deprecated": true,
  "no_legacy": true,
  "shared": false,
  "deployment_target": "embedded",
  "description": "Minimal embedded build with reduced features"
}
EOF

print_status "success" "Sample OpenSSL configurations created in $CONFIG_DIR"

# Create usage documentation
print_status "info" "Creating usage documentation..."

DOC_DIR="$PROJECT_ROOT/docs"
mkdir -p "$DOC_DIR"

cat > "$DOC_DIR/openssl-database-validation.md" << 'EOF'
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
EOF

print_status "success" "Usage documentation created in $DOC_DIR/openssl-database-validation.md"

# Create quick test script
print_status "info" "Creating quick test script..."

cat > "$PROJECT_ROOT/scripts/test/test_quick_validation.py" << 'EOF'
#!/usr/bin/env python3
"""
Quick validation test for OpenSSL database schema validation
"""

import sys
from pathlib import Path

# Add the openssl_tools module to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from openssl_tools.database.openssl_schema_validator import OpenSSLSchemaValidator

def quick_test():
    """Run a quick validation test"""
    print("🧪 Quick OpenSSL Database Validation Test")
    print("=" * 50)

    # Initialize validator
    project_root = Path(__file__).parent.parent.parent
    validator = OpenSSLSchemaValidator(project_root)

    # Test configuration validation
    test_config = {
        "config_name": "quick-test",
        "openssl_version": "3.4.1",
        "fips_enabled": False,
        "shared": True,
        "deployment_target": "general"
    }

    print("🔍 Testing configuration validation...")
    result = validator.validate_openssl_configuration(test_config)

    if result["valid"]:
        print(f"✅ Configuration valid (hash: {result['config_hash']})")
    else:
        print(f"❌ Configuration invalid: {result['errors']}")
        return False

    # Test cache summary
    print("📊 Testing cache summary...")
    summary = validator.get_package_cache_summary()
    print(f"Total packages: {summary.get('total_packages', 0)}")

    print("🎉 Quick test completed successfully!")
    return True

if __name__ == "__main__":
    success = quick_test()
    sys.exit(0 if success else 1)
EOF

chmod +x "$PROJECT_ROOT/scripts/test/test_quick_validation.py"
print_status "success" "Quick test script created"

# Run quick test
print_status "info" "Running quick validation test..."

if python3 "$PROJECT_ROOT/scripts/test/test_quick_validation.py"; then
    print_status "success" "Quick validation test passed"
else
    print_status "warning" "Quick validation test had issues"
fi

# Final summary
echo ""
echo -e "${BLUE}📋 Setup Summary${NC}"
echo "=================="
echo -e "${GREEN}✅ Database schema validation system setup completed${NC}"
echo -e "${GREEN}✅ Sample OpenSSL configurations created${NC}"
echo -e "${GREEN}✅ Usage documentation created${NC}"
echo -e "${GREEN}✅ Quick test script created${NC}"
echo ""
echo -e "${BLUE}📁 Key Files Created:${NC}"
echo "  - Database files: conan-dev/*.db"
echo "  - Configurations: openssl-config/*.json"
echo "  - Documentation: docs/openssl-database-validation.md"
echo "  - Test script: scripts/test/test_quick_validation.py"
echo ""
echo -e "${BLUE}🚀 Next Steps:${NC}"
echo "  1. Review the generated documentation"
echo "  2. Test with your OpenSSL configurations"
echo "  3. Integrate with your build process"
echo "  4. Set up regular cache monitoring"
echo ""
echo -e "${GREEN}🎉 OpenSSL Database Schema Validation System is ready!${NC}"
