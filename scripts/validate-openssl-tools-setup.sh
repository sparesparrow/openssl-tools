#!/bin/bash
# scripts/validate-openssl-tools-setup.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "🔍 Validating OpenSSL Tools Setup"

# Validation results
declare -A VALIDATION_RESULTS=()
TOTAL_TESTS=0
PASSED_TESTS=0

# Function to run validation test
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo "🧪 Testing: $test_name"
    
    if eval "$test_command" >/dev/null 2>&1; then
        VALIDATION_RESULTS["$test_name"]="PASS"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        echo "  ✅ PASS"
    else
        VALIDATION_RESULTS["$test_name"]="FAIL"
        echo "  ❌ FAIL"
    fi
}

# Function to check file exists and is executable
check_executable() {
    local file_path="$1"
    local description="$2"
    
    if [[ -f "$file_path" && -x "$file_path" ]]; then
        echo "  ✅ $description exists and is executable"
        return 0
    else
        echo "  ❌ $description missing or not executable: $file_path"
        return 1
    fi
}

# Function to check directory structure
check_directory_structure() {
    echo "📁 Checking directory structure..."
    
    local required_dirs=(
        ".cursor/agents"
        "docker"
        "scripts"
        "profiles/conan"
        "artifacts"
        "logs"
        "tools"
        "templates/github-actions"
        ".devcontainer"
    )
    
    for dir in "${required_dirs[@]}"; do
        if [[ -d "${PROJECT_ROOT}/${dir}" ]]; then
            echo "  ✅ $dir"
        else
            echo "  ❌ Missing directory: $dir"
            return 1
        fi
    done
}

# Function to check configuration files
check_configuration_files() {
    echo "⚙️  Checking configuration files..."
    
    local config_files=(
        ".cursor/agents/openssl-tools-agent.yml"
        "docker/docker-compose.yml"
        "docker/Dockerfile.ubuntu-builder"
        "docker/Dockerfile.windows-builder"
        "docker/Dockerfile.macos-builder"
        ".env.template"
        ".devcontainer/devcontainer.json"
    )
    
    for file in "${config_files[@]}"; do
        if [[ -f "${PROJECT_ROOT}/${file}" ]]; then
            echo "  ✅ $file"
        else
            echo "  ❌ Missing configuration file: $file"
            return 1
        fi
    done
}

# Function to check YAML syntax
check_yaml_syntax() {
    echo "📝 Checking YAML syntax..."
    
    local yaml_files=(
        ".cursor/agents/openssl-tools-agent.yml"
        "docker/docker-compose.yml"
        ".devcontainer/devcontainer.json"
    )
    
    for file in "${yaml_files[@]}"; do
        if python3 -c "import yaml; yaml.safe_load(open('${PROJECT_ROOT}/${file}'))" >/dev/null 2>&1; then
            echo "  ✅ $file syntax valid"
        else
            echo "  ❌ $file syntax invalid"
            return 1
        fi
    done
}

# Function to check Docker configuration
check_docker_config() {
    echo "🐳 Checking Docker configuration..."
    
    cd "${PROJECT_ROOT}/docker"
    
    if docker-compose config >/dev/null 2>&1; then
        echo "  ✅ Docker Compose configuration valid"
    else
        echo "  ❌ Docker Compose configuration invalid"
        return 1
    fi
}

# Function to check Conan profiles
check_conan_profiles() {
    echo "📦 Checking Conan profiles..."
    
    local profiles=(
        "ubuntu-20.04.profile"
        "ubuntu-22.04.profile"
        "windows-msvc2022.profile"
        "macos-arm64.profile"
        "macos-x86_64.profile"
    )
    
    for profile in "${profiles[@]}"; do
        if [[ -f "${PROJECT_ROOT}/profiles/conan/${profile}" ]]; then
            echo "  ✅ $profile"
        else
            echo "  ❌ Missing Conan profile: $profile"
            return 1
        fi
    done
}

# Function to check Python dependencies
check_python_dependencies() {
    echo "🐍 Checking Python dependencies..."
    
    local python_scripts=(
        "scripts/generate_sbom.py"
    )
    
    for script in "${python_scripts[@]}"; do
        if python3 -m py_compile "${PROJECT_ROOT}/${script}" >/dev/null 2>&1; then
            echo "  ✅ $script syntax valid"
        else
            echo "  ❌ $script syntax invalid"
            return 1
        fi
    done
}

# Function to check GitHub Actions
check_github_actions() {
    echo "🚀 Checking GitHub Actions..."
    
    local action_files=(
        "templates/github-actions/setup-openssl-build/action.yml"
        "templates/github-actions/run-openssl-tests/action.yml"
        "templates/github-actions/workflows/artifact-build-pipeline.yml"
    )
    
    for action in "${action_files[@]}"; do
        if [[ -f "${PROJECT_ROOT}/${action}" ]]; then
            echo "  ✅ $action"
        else
            echo "  ❌ Missing GitHub Action: $action"
            return 1
        fi
    done
}

# Function to check environment setup
check_environment_setup() {
    echo "🔧 Checking environment setup..."
    
    if [[ -f "${PROJECT_ROOT}/.env" ]]; then
        echo "  ✅ .env file exists"
    else
        echo "  ⚠️  .env file missing (will be created from template)"
    fi
    
    if [[ -f "${PROJECT_ROOT}/.env.template" ]]; then
        echo "  ✅ .env.template exists"
    else
        echo "  ❌ .env.template missing"
        return 1
    fi
}

# Function to check script permissions
check_script_permissions() {
    echo "🔐 Checking script permissions..."
    
    local scripts=(
        "scripts/docker-build-and-upload.sh"
        "scripts/cursor-agents-coordinator.sh"
        "scripts/validate-artifactory-packages.sh"
        "scripts/dev-setup.sh"
        "scripts/validate-openssl-tools-setup.sh"
    )
    
    for script in "${scripts[@]}"; do
        if check_executable "${PROJECT_ROOT}/${script}" "Script"; then
            echo "  ✅ $script"
        else
            echo "  ❌ $script permissions issue"
            chmod +x "${PROJECT_ROOT}/${script}"
            echo "  🔧 Fixed permissions for $script"
        fi
    done
}

# Function to run integration tests
run_integration_tests() {
    echo "🔗 Running integration tests..."
    
    # Test Docker build (dry run)
    cd "${PROJECT_ROOT}/docker"
    if docker-compose config >/dev/null 2>&1; then
        echo "  ✅ Docker Compose dry run successful"
    else
        echo "  ❌ Docker Compose dry run failed"
        return 1
    fi
    
    # Test Python script execution
    if python3 "${PROJECT_ROOT}/scripts/generate_sbom.py" --help >/dev/null 2>&1; then
        echo "  ✅ Python script execution successful"
    else
        echo "  ❌ Python script execution failed"
        return 1
    fi
}

# Function to generate validation report
generate_report() {
    echo ""
    echo "📊 Validation Report"
    echo "==================="
    echo "Total Tests: $TOTAL_TESTS"
    echo "Passed: $PASSED_TESTS"
    echo "Failed: $((TOTAL_TESTS - PASSED_TESTS))"
    echo ""
    
    echo "Detailed Results:"
    for test_name in "${!VALIDATION_RESULTS[@]}"; do
        local status="${VALIDATION_RESULTS[$test_name]}"
        local icon="✅"
        if [[ "$status" == "FAIL" ]]; then
            icon="❌"
        fi
        echo "  $icon $test_name: $status"
    done
    
    echo ""
    if [[ $PASSED_TESTS -eq $TOTAL_TESTS ]]; then
        echo "🎉 All validations passed! Setup is ready to use."
        return 0
    else
        echo "💥 Some validations failed. Please fix the issues above."
        return 1
    fi
}

# Main execution
main() {
    echo "🚀 Starting OpenSSL Tools setup validation"
    echo ""
    
    # Run all validation tests
    run_test "Directory Structure" "check_directory_structure"
    run_test "Configuration Files" "check_configuration_files"
    run_test "YAML Syntax" "check_yaml_syntax"
    run_test "Docker Configuration" "check_docker_config"
    run_test "Conan Profiles" "check_conan_profiles"
    run_test "Python Dependencies" "check_python_dependencies"
    run_test "GitHub Actions" "check_github_actions"
    run_test "Environment Setup" "check_environment_setup"
    run_test "Script Permissions" "check_script_permissions"
    run_test "Integration Tests" "run_integration_tests"
    
    # Generate final report
    generate_report
}

# Execute main function
main "$@"