#!/bin/bash
# scripts/validate-artifactory-packages.sh

set -euo pipefail

# Configuration  
ARTIFACTORY_URL="${ARTIFACTORY_URL:-https://your-artifactory.com}"
ARTIFACTORY_TOKEN="${ARTIFACTORY_TOKEN:-}"
VALIDATION_DIR="/tmp/openssl-validation-$$"

echo "🔍 Starting Artifactory Package Validation"

# Function to validate Conan packages
validate_conan_packages() {
    local version="$1"
    echo "📦 Validating Conan packages for version: ${version}"
    
    mkdir -p "${VALIDATION_DIR}/conan-test"
    cd "${VALIDATION_DIR}/conan-test"
    
    # Create test conanfile
    cat > conanfile.txt << EOF
[requires]
openssl/${version}

[generators]
CMakeDeps
CMakeToolchain

[options]
openssl:shared=True
EOF
    
    # Test with Docker to ensure clean environment
    docker run --rm \
        -v "${VALIDATION_DIR}/conan-test:/workspace" \
        -w /workspace \
        -e ARTIFACTORY_URL="${ARTIFACTORY_URL}" \
        -e ARTIFACTORY_TOKEN="${ARTIFACTORY_TOKEN}" \
        conanio/conan:2.0 \
        sh -c "
            # Configure remote
            conan remote add artifactory \${ARTIFACTORY_URL}/artifactory/api/conan/conan
            conan remote login artifactory admin -p \${ARTIFACTORY_TOKEN}
            
            # Install package
            conan install . -r=artifactory --build=missing -s build_type=Release
            
            # Verify files exist
            if [[ -f 'conan_toolchain.cmake' && -f 'OpenSSLConfig.cmake' ]]; then
                echo '✅ Conan package validation successful'
                exit 0
            else
                echo '❌ Conan package validation failed - missing files'
                ls -la
                exit 1
            fi
        "
}

# Function to validate binary artifacts
validate_binary_artifacts() {
    local version="$1"
    echo "🔧 Validating binary artifacts for version: ${version}"
    
    mkdir -p "${VALIDATION_DIR}/binary-test"
    cd "${VALIDATION_DIR}/binary-test"
    
    # Test platforms
    platforms=("ubuntu-20.04-gcc" "ubuntu-22.04-clang" "windows-2022" "macos-x86_64")
    
    for platform in "${platforms[@]}"; do
        echo "  Testing ${platform}..."
        
        # Download artifact
        curl -f \
            -H "Authorization: Bearer ${ARTIFACTORY_TOKEN}" \
            -o "${platform}.tar.gz" \
            "${ARTIFACTORY_URL}/artifactory/openssl-releases/${version}/openssl-${version}-${platform}.tar.gz"
        
        # Extract and verify
        tar -xzf "${platform}.tar.gz"
        
        # Check essential files exist
        if [[ -d "${platform}/opt/openssl/bin" || -d "${platform}/C/openssl/bin" ]]; then
            echo "  ✅ ${platform} - Binary structure valid"
        else
            echo "  ❌ ${platform} - Binary structure invalid"
            return 1
        fi
        
        # Verify checksums
        if [[ -f "${platform}/SHA256SUMS" ]]; then
            cd "${platform}"
            if sha256sum -c SHA256SUMS --quiet; then
                echo "  ✅ ${platform} - Checksums valid"
            else
                echo "  ❌ ${platform} - Checksums invalid"
                return 1
            fi
            cd ..
        fi
        
        # Verify SBOM if exists
        if [[ -f "${platform}/SBOM.json" ]]; then
            if python3 -m json.tool "${platform}/SBOM.json" >/dev/null 2>&1; then
                echo "  ✅ ${platform} - SBOM valid"
            else
                echo "  ❌ ${platform} - SBOM invalid"
                return 1
            fi
        fi
        
        # Clean up
        rm -rf "${platform}" "${platform}.tar.gz"
    done
}

# Function to test end-to-end usage
test_end_to_end_usage() {
    local version="$1"
    echo "🧪 Testing end-to-end usage for version: ${version}"
    
    mkdir -p "${VALIDATION_DIR}/e2e-test"
    cd "${VALIDATION_DIR}/e2e-test"
    
    # Create test CMake project
    cat > CMakeLists.txt << 'EOF'
cmake_minimum_required(VERSION 3.15)
project(OpenSSLTest)

find_package(OpenSSL REQUIRED)

add_executable(ssl_test main.cpp)
target_link_libraries(ssl_test OpenSSL::SSL OpenSSL::Crypto)
EOF
    
    cat > main.cpp << 'EOF'
#include <openssl/ssl.h>
#include <openssl/err.h>
#include <iostream>

int main() {
    SSL_library_init();
    SSL_load_error_strings();
    
    std::cout << "OpenSSL Version: " << OPENSSL_VERSION_TEXT << std::endl;
    std::cout << "✅ OpenSSL integration test successful!" << std::endl;
    
    return 0;
}
EOF
    
    # Test with Docker
    docker run --rm \
        -v "${VALIDATION_DIR}/e2e-test:/workspace" \
        -w /workspace \
        -e ARTIFACTORY_URL="${ARTIFACTORY_URL}" \
        -e ARTIFACTORY_TOKEN="${ARTIFACTORY_TOKEN}" \
        -e VERSION="${version}" \
        conanio/conan:2.0 \
        sh -c "
            # Install dependencies
            apt-get update && apt-get install -y build-essential cmake
            
            # Configure Conan
            conan remote add artifactory \${ARTIFACTORY_URL}/artifactory/api/conan/conan
            conan remote login artifactory admin -p \${ARTIFACTORY_TOKEN}
            
            # Create conanfile for dependencies
            echo '[requires]' > conanfile.txt
            echo 'openssl/\${VERSION}' >> conanfile.txt
            echo '[generators]' >> conanfile.txt
            echo 'CMakeDeps' >> conanfile.txt
            echo 'CMakeToolchain' >> conanfile.txt
            
            # Install dependencies
            conan install . -r=artifactory --build=missing -s build_type=Release
            
            # Build test
            cmake . -DCMAKE_TOOLCHAIN_FILE=conan_toolchain.cmake
            make
            
            # Run test
            ./ssl_test
        "
}

# Function to generate validation report
generate_report() {
    local version="$1"
    local status="$2"
    
    cat > "${VALIDATION_DIR}/validation-report.json" << EOF
{
    "validation_date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "version": "${version}",
    "status": "${status}",
    "artifactory_url": "${ARTIFACTORY_URL}",
    "tests": {
        "conan_packages": "$(test "${CONAN_TEST_STATUS:-unknown}" = "success" && echo "PASS" || echo "FAIL")",
        "binary_artifacts": "$(test "${BINARY_TEST_STATUS:-unknown}" = "success" && echo "PASS" || echo "FAIL")",
        "end_to_end": "$(test "${E2E_TEST_STATUS:-unknown}" = "success" && echo "PASS" || echo "FAIL")"
    },
    "artifacts_validated": [
        "ubuntu-20.04-gcc",
        "ubuntu-22.04-clang", 
        "windows-2022",
        "macos-x86_64"
    ]
}
EOF
    
    echo "📋 Validation report generated: ${VALIDATION_DIR}/validation-report.json"
    cat "${VALIDATION_DIR}/validation-report.json"
}

# Main execution
main() {
    local version="${1:-$(date +%Y%m%d)-$(git rev-parse --short HEAD)}"
    
    echo "🎯 Validating OpenSSL packages version: ${version}"
    
    # Clean validation directory
    rm -rf "${VALIDATION_DIR}"
    mkdir -p "${VALIDATION_DIR}"
    
    # Validate Conan packages
    if validate_conan_packages "${version}"; then
        CONAN_TEST_STATUS="success"
        echo "✅ Conan package validation passed"
    else
        CONAN_TEST_STATUS="failed"
        echo "❌ Conan package validation failed"
    fi
    
    # Validate binary artifacts
    if validate_binary_artifacts "${version}"; then
        BINARY_TEST_STATUS="success" 
        echo "✅ Binary artifact validation passed"
    else
        BINARY_TEST_STATUS="failed"
        echo "❌ Binary artifact validation failed"
    fi
    
    # Test end-to-end usage
    if test_end_to_end_usage "${version}"; then
        E2E_TEST_STATUS="success"
        echo "✅ End-to-end validation passed"
    else
        E2E_TEST_STATUS="failed"
        echo "❌ End-to-end validation failed"
    fi
    
    # Determine overall status
    if [[ "${CONAN_TEST_STATUS}" = "success" && "${BINARY_TEST_STATUS}" = "success" && "${E2E_TEST_STATUS}" = "success" ]]; then
        OVERALL_STATUS="success"
        echo "🎉 All validations passed!"
    else
        OVERALL_STATUS="failed"
        echo "💥 Some validations failed!"
    fi
    
    # Generate report
    generate_report "${version}" "${OVERALL_STATUS}"
    
    # Cleanup
    rm -rf "${VALIDATION_DIR}"
    
    # Exit with appropriate code
    if [[ "${OVERALL_STATUS}" = "success" ]]; then
        exit 0
    else
        exit 1
    fi
}

# Trap cleanup
trap 'rm -rf "${VALIDATION_DIR}"' EXIT

# Execute main function
main "$@"