#!/bin/bash
# OpenSSL-Tools Workspace State Analyzer
# Analyzes current state, identifies commits needed, detects issues

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

echo "🔍 OpenSSL-Tools Workspace Analysis Report"
echo "===========================================" 
echo "📅 Generated: $TIMESTAMP"
echo "📂 Root: $PROJECT_ROOT"
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_section() {
    echo -e "${BLUE}## $1${NC}"
    echo "$(printf '=%.0s' {1..50})"
}

print_status() {
    local status="$1"
    local message="$2"
    case "$status" in
        "OK") echo -e "✅ ${GREEN}$message${NC}" ;;
        "WARN") echo -e "⚠️  ${YELLOW}$message${NC}" ;;
        "ERROR") echo -e "❌ ${RED}$message${NC}" ;;
        "INFO") echo -e "ℹ️  ${CYAN}$message${NC}" ;;
        "TODO") echo -e "📝 ${PURPLE}$message${NC}" ;;
    esac
}

# 1. Repository Structure Analysis
analyze_repository_structure() {
    print_section "Repository Structure Analysis"
    
    # Check component directories
    local components=("openssl-crypto" "openssl-ssl" "openssl-tools")
    for comp in "${components[@]}"; do
        if [ -d "$comp" ]; then
            if [ -f "$comp/conanfile.py" ]; then
                print_status "OK" "$comp: Component exists with conanfile.py"
            else
                print_status "ERROR" "$comp: Missing conanfile.py"
            fi
            
            if [ -f "$comp/component-info.json" ]; then
                print_status "OK" "$comp: Has component metadata"
            else
                print_status "WARN" "$comp: Missing component-info.json"
            fi
        else
            print_status "ERROR" "$comp: Component directory missing"
        fi
    done
    
    # Check critical directories
    local critical_dirs=("scripts" "database" ".cursor")
    for dir in "${critical_dirs[@]}"; do
        if [ -d "$dir" ]; then
            local file_count=$(find "$dir" -type f | wc -l)
            print_status "OK" "$dir: Exists with $file_count files"
        else
            print_status "ERROR" "$dir: Critical directory missing"
        fi
    done
    
    # Check OpenSSL source
    if [ -L "openssl-source" ]; then
        local target=$(readlink openssl-source)
        print_status "OK" "openssl-source: Symlink to $target"
    elif [ -d "openssl-source" ]; then
        print_status "OK" "openssl-source: Directory exists"
    else
        print_status "ERROR" "openssl-source: Missing source code"
    fi
    
    echo ""
}

# 2. Build System Analysis
analyze_build_system() {
    print_section "Build System Analysis"
    
    # Check Conan installation
    if command -v conan >/dev/null 2>&1; then
        local conan_version=$(conan --version | head -1)
        print_status "OK" "Conan: $conan_version"
        
        # Check remotes
        local remote_count=$(conan remote list | wc -l)
        print_status "INFO" "Conan remotes configured: $remote_count"
        
        # Check cache
        if [ -d ~/.conan2 ]; then
            local package_count=$(find ~/.conan2/p -maxdepth 1 -type d -name "opens*" 2>/dev/null | wc -l)
            print_status "INFO" "OpenSSL packages in cache: $package_count"
        fi
    else
        print_status "ERROR" "Conan: Not installed"
    fi
    
    # Check Docker
    if command -v docker >/dev/null 2>&1; then
        print_status "OK" "Docker: Available"
        
        # Check PostgreSQL container
        if docker ps | grep -q "openssl-build-db"; then
            print_status "OK" "PostgreSQL: Container running"
        else
            print_status "WARN" "PostgreSQL: Container not running"
        fi
    else
        print_status "ERROR" "Docker: Not installed"
    fi
    
    # Check build scripts
    local build_scripts=("scripts/build/build-all-components.sh" "scripts/upload/upload-to-registries.sh")
    for script in "${build_scripts[@]}"; do
        if [ -f "$script" ]; then
            if [ -x "$script" ]; then
                print_status "OK" "Build script: $script (executable)"
            else
                print_status "WARN" "Build script: $script (not executable)"
            fi
        else
            print_status "ERROR" "Build script: $script (missing)"
        fi
    done
    
    echo ""
}

# 3. Database Analysis
analyze_database() {
    print_section "Database Analysis"
    
    if [ -f "docker-compose.postgres.yml" ]; then
        print_status "OK" "Docker compose: PostgreSQL configuration exists"
    else
        print_status "ERROR" "Docker compose: Missing PostgreSQL configuration"
    fi
    
    if [ -f "database/init/01-create-schema.sql" ]; then
        print_status "OK" "Database schema: Initialization script exists"
    else
        print_status "ERROR" "Database schema: Missing initialization script"
    fi
    
    # Test database connection if container is running
    if docker ps | grep -q "openssl-build-db"; then
        if docker exec openssl-build-db psql -U openssl_admin -d openssl_builds -c "SELECT 1;" >/dev/null 2>&1; then
            local record_count=$(docker exec openssl-build-db psql -U openssl_admin -d openssl_builds -t -c "SELECT COUNT(*) FROM builds;" 2>/dev/null | tr -d ' ' || echo "0")
            print_status "OK" "Database connection: Working ($record_count build records)"
        else
            print_status "ERROR" "Database connection: Failed"
        fi
    else
        print_status "WARN" "Database: Container not running"
    fi
    
    echo ""
}

# 4. Git Status Analysis
analyze_git_status() {
    print_section "Git Status Analysis"
    
    if [ -d .git ]; then
        print_status "OK" "Git repository: Initialized"
        
        # Check current branch
        local current_branch=$(git branch --show-current 2>/dev/null || echo "unknown")
        print_status "INFO" "Current branch: $current_branch"
        
        # Check uncommitted changes
        local staged_files=$(git diff --cached --name-only | wc -l)
        local unstaged_files=$(git diff --name-only | wc -l)
        local untracked_files=$(git ls-files --others --exclude-standard | wc -l)
        
        if [ "$staged_files" -gt 0 ]; then
            print_status "INFO" "Staged files: $staged_files"
        fi
        
        if [ "$unstaged_files" -gt 0 ]; then
            print_status "WARN" "Unstaged changes: $unstaged_files files"
        fi
        
        if [ "$untracked_files" -gt 0 ]; then
            print_status "INFO" "Untracked files: $untracked_files"
            
            # Show some untracked files
            echo "   Recent untracked files:"
            git ls-files --others --exclude-standard | head -5 | sed 's/^/   • /'
            if [ "$untracked_files" -gt 5 ]; then
                echo "   ... and $((untracked_files - 5)) more"
            fi
        fi
        
        # Check if there are commits
        if git rev-parse HEAD >/dev/null 2>&1; then
            local commit_count=$(git rev-list --count HEAD 2>/dev/null || echo "0")
            print_status "INFO" "Total commits: $commit_count"
        else
            print_status "WARN" "No commits yet"
        fi
        
    else
        print_status "ERROR" "Git repository: Not initialized"
    fi
    
    echo ""
}

# 5. Environment Configuration Analysis
analyze_environment() {
    print_section "Environment Configuration"
    
    if [ -f ".env" ]; then
        local env_vars=$(grep -c '^[A-Z]' .env 2>/dev/null || echo "0")
        print_status "OK" "Environment file: .env exists ($env_vars variables)"
        
        # Check critical environment variables
        if grep -q "POSTGRES_PASSWORD" .env; then
            print_status "OK" "Database password: Configured"
        else
            print_status "WARN" "Database password: Not configured"
        fi
        
        if grep -q "ARTIFACTORY_TOKEN" .env; then
            print_status "OK" "Artifactory token: Configured"
        else
            print_status "WARN" "Artifactory token: Not configured"
        fi
        
        if grep -q "GITHUB_TOKEN" .env; then
            print_status "OK" "GitHub token: Configured"
        else
            print_status "WARN" "GitHub token: Not configured"
        fi
    else
        print_status "ERROR" "Environment file: .env missing"
    fi
    
    # Check .gitignore
    if [ -f ".gitignore" ]; then
        local ignore_lines=$(wc -l < .gitignore)
        print_status "OK" ".gitignore: Exists ($ignore_lines lines)"
    else
        print_status "ERROR" ".gitignore: Missing"
    fi
    
    echo ""
}

# 6. Cursor IDE Configuration Analysis
analyze_cursor_config() {
    print_section "Cursor IDE Configuration"
    
    if [ -d ".cursor" ]; then
        local config_files=$(find .cursor -name "*.yml" -o -name "*.json" -o -name "*.md" | wc -l)
        print_status "OK" "Cursor config: Directory exists ($config_files files)"
        
        # Check specific configurations
        local cursor_configs=("agents" "commands" "rules" "monitoring" "tooling")
        for config in "${cursor_configs[@]}"; do
            if [ -d ".cursor/$config" ]; then
                local file_count=$(find ".cursor/$config" -type f | wc -l)
                print_status "OK" "Cursor $config: $file_count files"
            else
                print_status "WARN" "Cursor $config: Directory missing"
            fi
        done
        
        # Check critical files
        if [ -f ".cursor/environment.json" ]; then
            print_status "OK" "Environment config: Present"
        else
            print_status "WARN" "Environment config: Missing"
        fi
        
        if [ -f ".cursor/mcp.json" ]; then
            print_status "OK" "MCP config: Present"
        else
            print_status "WARN" "MCP config: Missing"
        fi
        
    else
        print_status "ERROR" "Cursor config: .cursor directory missing"
    fi
    
    echo ""
}

# 7. File System Health Check
analyze_filesystem_health() {
    print_section "File System Health Check"
    
    # Check disk space
    local disk_usage=$(df -h . | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ "$disk_usage" -lt 80 ]; then
        print_status "OK" "Disk space: ${disk_usage}% used"
    elif [ "$disk_usage" -lt 90 ]; then
        print_status "WARN" "Disk space: ${disk_usage}% used (getting full)"
    else
        print_status "ERROR" "Disk space: ${disk_usage}% used (critically full)"
    fi
    
    # Check for large files
    local large_files=$(find . -type f -size +100M 2>/dev/null | wc -l)
    if [ "$large_files" -gt 0 ]; then
        print_status "WARN" "Large files: $large_files files >100MB found"
        find . -type f -size +100M 2>/dev/null | head -3 | sed 's/^/   • /'
    else
        print_status "OK" "Large files: None >100MB"
    fi
    
    # Check for broken symlinks
    local broken_links=$(find . -type l ! -exec test -e {} \; -print 2>/dev/null | wc -l)
    if [ "$broken_links" -gt 0 ]; then
        print_status "ERROR" "Broken symlinks: $broken_links found"
    else
        print_status "OK" "Symlinks: All valid"
    fi
    
    echo ""
}

# 8. Recommendations
generate_recommendations() {
    print_section "Recommendations & Next Steps"
    
    echo "📋 Files that should be committed:"
    echo "   Essential Configuration:"
    [ -f "conanfile.py" ] && echo "   ✓ conanfile.py"
    [ -f "docker-compose.postgres.yml" ] && echo "   ✓ docker-compose.postgres.yml"
    [ -f ".gitignore" ] && echo "   ✓ .gitignore"
    [ -f "README.md" ] && echo "   ✓ README.md" || echo "   ❌ README.md (missing)"
    
    echo ""
    echo "   Component Files:"
    for comp in openssl-crypto openssl-ssl openssl-tools; do
        [ -f "$comp/conanfile.py" ] && echo "   ✓ $comp/conanfile.py"
        [ -f "$comp/component-info.json" ] && echo "   ✓ $comp/component-info.json"
    done
    
    echo ""
    echo "   Scripts & Automation:"
    [ -f "scripts/build/build-all-components.sh" ] && echo "   ✓ scripts/build/build-all-components.sh"
    [ -f "scripts/upload/upload-to-registries.sh" ] && echo "   ✓ scripts/upload/upload-to-registries.sh"
    [ -d "scripts/database" ] && echo "   ✓ scripts/database/ ($(find scripts/database -name "*.py" | wc -l) files)"
    
    echo ""
    echo "   Database Schema:"
    [ -f "database/init/01-create-schema.sql" ] && echo "   ✓ database/init/01-create-schema.sql"
    
    echo ""
    echo "   Cursor IDE Configuration:"
    [ -d ".cursor" ] && echo "   ✓ .cursor/ directory ($(find .cursor -type f | wc -l) files)"
    
    echo ""
    echo "🔧 Issues to address:"
    
    # Database not running
    if ! docker ps | grep -q "openssl-build-db"; then
        print_status "TODO" "Start PostgreSQL database: docker-compose -f docker-compose.postgres.yml up -d"
    fi
    
    # Missing executables
    if [ -f "scripts/build/build-all-components.sh" ] && [ ! -x "scripts/build/build-all-components.sh" ]; then
        print_status "TODO" "Make build scripts executable: chmod +x scripts/build/*.sh scripts/upload/*.sh"
    fi
    
    # No commits yet
    if ! git rev-parse HEAD >/dev/null 2>&1; then
        print_status "TODO" "Initial commit needed: git add . && git commit -m 'feat: multi-component OpenSSL pipeline initial implementation'"
    fi
    
    # Missing README
    if [ ! -f "README.md" ]; then
        print_status "TODO" "Create README.md with project documentation"
    fi
    
    echo ""
    echo "🚀 Suggested commit sequence:"
    echo "   1. git add .gitignore .env.example *.yml *.md"
    echo "   2. git add openssl-*/conanfile.py openssl-*/component-info.json"
    echo "   3. git add scripts/ database/ .cursor/"
    echo "   4. git add profiles/ docker/"
    echo "   5. git commit -m 'feat: complete multi-component OpenSSL build pipeline'"
    echo ""
}

# Main execution
main() {
    cd "$PROJECT_ROOT"
    
    analyze_repository_structure
    analyze_build_system
    analyze_database
    analyze_git_status
    analyze_environment
    analyze_cursor_config
    analyze_filesystem_health
    generate_recommendations
    
    echo "🎯 Analysis complete! Summary saved to workspace-analysis.log"
}

# Save output to log file
main 2>&1 | tee workspace-analysis.log
