#!/usr/bin/env bash
# agent-loop-improved.sh - Robust CI orchestration with security enhancements
# Usage:
#   ./agent-loop-improved.sh "Task description" execution
#   ./agent-loop-improved.sh --once "Fix failed workflows" execution
#   ./agent-loop-improved.sh --help

set -euo pipefail
IFS=$'\n\t'

# Initialize critical variables before use (required for set -u)
LOG_LEVEL="${LOG_LEVEL:-info}"
DRY_RUN="${DRY_RUN:-false}"
RUN_ONCE="${RUN_ONCE:-false}"

# Source environment files for proper setup
if [[ -f ~/.bashrc ]]; then
    source ~/.bashrc
fi

if [[ -f .env ]]; then
    source .env
fi

# Activate virtual environment if it exists
if [[ -f venv/bin/activate ]]; then
    source venv/bin/activate
fi

# Configuration with validation
readonly SCRIPT_NAME="${0##*/}"
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly CONFIG_FILE="${SCRIPT_DIR}/.agent-config.json"

# Security: Use restrictive umask for all file operations  
umask 077

# Global cleanup tracking
declare -a TEMP_FILES=()
declare -a background_pids=()

# Parse command line arguments first
parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --once)
                RUN_ONCE="true"
                shift
                ;;
            --dry-run)
                DRY_RUN="true"
                shift
                ;;
            --help|-h)
                cat <<EOF
Usage: $SCRIPT_NAME [OPTIONS] [TASK] [MODE]

Robust CI orchestration with security enhancements for OpenSSL tools.

Options:
  --once           Run single iteration then exit (default: false)
  --dry-run        Simulate actions without making changes (default: false)
  --help, -h       Show this help message

Arguments:
  TASK             Task description (default from config or env)
  MODE             Operation mode: planning or execution (default: execution)

Configuration:
  Uses config file: $CONFIG_FILE (if exists)
  Or environment variables with defaults

Environment Variables:
  REPO             Repository (default: sparesparrow/openssl-tools)
  PR_NUMBER        PR number (default: 6)
  PR_BRANCH        Branch name (default: simplify-openssl-build)
  MAX_ITERATIONS   Maximum loop iterations (default: 12)
  INTERVAL         Seconds between iterations (default: 60)
  AGENT_TIMEOUT_SEC Agent timeout in seconds (default: 60)
  LOG_LEVEL        Logging level: debug|info|warn|error (default: info)

Security:
  - API key stored in: $HOME/.cursor/api-key (mode 600)
  - Or use CURSOR_API_KEY environment variable
  - Secrets are automatically redacted from logs

Examples:
  $SCRIPT_NAME --once "Fix failed workflows" execution
  $SCRIPT_NAME --dry-run "Analyze CI issues" planning
  CURSOR_API_KEY=key_xxx $SCRIPT_NAME "Repair workflows" execution

Required GitHub Permissions:
  - repo: Full control of private repositories
  - workflow: Update GitHub Action workflows
  - read:org: Read org and team membership
EOF
                exit 0
                ;;
            *)
                # Store remaining args for later
                REMAINING_ARGS+=("$1")
                shift
                ;;
        esac
    done
}

# Load configuration from JSON file instead of env vars
load_config() {
    if [[ -f "$CONFIG_FILE" ]]; then
        # Validate JSON structure before loading
        if ! jq empty "$CONFIG_FILE" 2>/dev/null; then
            die "Invalid JSON in config file: $CONFIG_FILE"
        fi

        # Load with defaults
        REPO=$(jq -r '.repo // "sparesparrow/openssl-tools"' "$CONFIG_FILE")
        PR_NUMBER=$(jq -r '.pr_number // "6"' "$CONFIG_FILE")
        PR_BRANCH=$(jq -r '.pr_branch // "simplify-openssl-build"' "$CONFIG_FILE")
        MAX_ITERATIONS=$(jq -r '.max_iterations // 12' "$CONFIG_FILE")
        INTERVAL=$(jq -r '.interval // 60' "$CONFIG_FILE")
        LOG_LEVEL=$(jq -r '.log_level // "info"' "$CONFIG_FILE")
        AGENT_TIMEOUT_SEC=$(jq -r '.agent_timeout_sec // 60' "$CONFIG_FILE")
        USE_STREAMING=$(jq -r '.use_streaming // false' "$CONFIG_FILE")
        DRY_RUN=$(jq -r '.dry_run // false' "$CONFIG_FILE")
        TASK=$(jq -r '.task // "Ensure all PR workflows are green with minimal safe changes"' "$CONFIG_FILE")
        MODE=$(jq -r '.mode // "execution"' "$CONFIG_FILE")
        
        # Cursor CLI configuration paths
        CURSOR_CONFIG_FILE=$(jq -r '.cursor_config_file // ".cursor/cli-config.json"' "$CONFIG_FILE")
        CURSOR_MCP_CONFIG=$(jq -r '.cursor_mcp_config // "mcp.json"' "$CONFIG_FILE")
        CURSOR_AGENT_CONFIG=$(jq -r '.cursor_agent_config // ".cursor/agents/ci-repair-agent.yml"' "$CONFIG_FILE")
        
        # Configuration values
        AGENT_MODEL=$(jq -r '.agent_model // "auto"' "$CONFIG_FILE")
        MCP_ENABLED=$(jq -r '.mcp_enabled // true' "$CONFIG_FILE")
        
        secure_log info "Loaded configuration from $CONFIG_FILE"
    else
        # Fallback to environment variables with defaults
        REPO="${REPO:-sparesparrow/openssl-tools}"
        PR_NUMBER="${PR_NUMBER:-6}"
        PR_BRANCH="${PR_BRANCH:-simplify-openssl-build}"
        MAX_ITERATIONS="${MAX_ITERATIONS:-12}"
        INTERVAL="${INTERVAL:-60}"
        LOG_LEVEL="${LOG_LEVEL:-info}"
        AGENT_TIMEOUT_SEC="${AGENT_TIMEOUT_SEC:-60}"
        USE_STREAMING="${USE_STREAMING:-false}"
        DRY_RUN="${DRY_RUN:-false}"
        TASK="${1:-"Ensure all PR #$PR_NUMBER workflows are green with minimal safe changes"}"
        MODE="${2:-execution}"
        
        # Override max iterations if --once is specified
        if [[ "$RUN_ONCE" == "true" ]]; then
            MAX_ITERATIONS=1
            secure_log info "Running in single-iteration mode (--once)"
        fi
        
        # Cursor CLI configuration paths
        CURSOR_CONFIG_FILE="${CURSOR_CONFIG_FILE:-.cursor/cli-config.json}"
        CURSOR_MCP_CONFIG="${CURSOR_MCP_CONFIG:-mcp.json}"
        CURSOR_AGENT_CONFIG="${CURSOR_AGENT_CONFIG:-.cursor/agents/ci-repair-agent.yml}"
        
        # Configuration values
        AGENT_MODEL="${AGENT_MODEL:-auto}"
        MCP_ENABLED="${MCP_ENABLED:-true}"
        
        secure_log info "Using environment variables (no config file found)"
    fi
}

# Enhanced input validation
validate_inputs() {
    # Validate repository format (org/repo)
    if [[ ! "$REPO" =~ ^[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+$ ]]; then
        die "Invalid repository format: $REPO"
    fi

    # Validate PR number is numeric
    if [[ ! "$PR_NUMBER" =~ ^[0-9]+$ ]]; then
        die "Invalid PR number: $PR_NUMBER" 
    fi

    # Validate branch name
    if [[ ! "$PR_BRANCH" =~ ^[a-zA-Z0-9/_-]+$ ]]; then
        die "Invalid branch name: $PR_BRANCH"
    fi
    
    # Validate numeric parameters
    if [[ ! "$MAX_ITERATIONS" =~ ^[0-9]+$ ]] || [[ "$MAX_ITERATIONS" -lt 1 ]]; then
        die "Invalid max_iterations: $MAX_ITERATIONS (must be positive integer)"
    fi
    
    if [[ ! "$INTERVAL" =~ ^[0-9]+$ ]] || [[ "$INTERVAL" -lt 1 ]]; then
        die "Invalid interval: $INTERVAL (must be positive integer)"
    fi
    
    if [[ ! "$AGENT_TIMEOUT_SEC" =~ ^[0-9]+$ ]] || [[ "$AGENT_TIMEOUT_SEC" -lt 1 ]]; then
        die "Invalid agent_timeout_sec: $AGENT_TIMEOUT_SEC (must be positive integer)"
    fi
    
    # Validate log level
    case "$LOG_LEVEL" in
        debug|info|warn|error) ;;
        *) die "Invalid log_level: $LOG_LEVEL (must be debug|info|warn|error)" ;;
    esac
    
    # Validate boolean parameters
    case "$USE_STREAMING" in
        true|false) ;;
        *) die "Invalid use_streaming: $USE_STREAMING (must be true|false)" ;;
    esac
    
    case "$DRY_RUN" in
        true|false) ;;
        *) die "Invalid dry_run: $DRY_RUN (must be true|false)" ;;
    esac
    
    case "$MCP_ENABLED" in
        true|false) ;;
        *) die "Invalid mcp_enabled: $MCP_ENABLED (must be true|false)" ;;
    esac
}

# Secure logging without exposing sensitive data
secure_log() {
    local level="$1"; shift
    local msg="$*"

    # Remove potential sensitive data patterns
    msg=$(echo "$msg" | sed 's/[a-zA-Z0-9+/]\{20,\}/[REDACTED]/g')
    msg=$(echo "$msg" | sed 's/key_[a-zA-Z0-9]\{20,\}/[REDACTED]/g')
    msg=$(echo "$msg" | sed 's/sk-[a-zA-Z0-9]\{20,\}/[REDACTED]/g')

    # Filter by log level
    case "$LOG_LEVEL:$level" in
        debug:debug|debug:info|debug:warn|debug:error|info:info|info:warn|info:error|warn:warn|warn:error|error:error)
            # Use structured JSON logging if jq is available, otherwise plain text
            if command -v jq >/dev/null 2>&1; then
                echo "{\"ts\":\"$(date -Iseconds)\",\"level\":\"$level\",\"msg\":$(printf '%s' "$msg" | jq -Rs .)}" >&2
            else
                echo "[$(date -Iseconds)] [$level] $msg" >&2
            fi
            
            # Also log to syslog if available
            if command -v logger >/dev/null 2>&1; then
                logger -t "$SCRIPT_NAME" -p "user.$level" "$msg" 2>/dev/null || true
            fi
            ;;
    esac
}

# Legacy log function for backward compatibility
log() {
    secure_log "$@"
}

# Error handling with cleanup
die() {
    secure_log error "$*"
    cleanup
    exit 1
}

# Comprehensive cleanup function
cleanup() {
    local exit_code=${1:-$?}

    # Kill any background jobs
    if jobs -p >/dev/null 2>&1; then
        jobs -p | xargs -r kill 2>/dev/null || true
    fi

    # Kill tracked background processes
    for pid in "${background_pids[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null || true
            wait "$pid" 2>/dev/null || true
        fi
    done

    # Cleanup temporary files
    if [[ -n "${TEMP_FILES:-}" ]]; then
        rm -f $TEMP_FILES 2>/dev/null || true
    fi

    # Reset git if in dirty state (only in dry run mode)
    if [[ "$DRY_RUN" == "true" ]] && [[ -d .git ]] && ! git diff --quiet 2>/dev/null; then
        git reset --hard HEAD >/dev/null 2>&1 || true
    fi

    exit $exit_code
}

# Set up signal handlers
trap 'cleanup 130' INT   # Ctrl+C
trap 'cleanup 143' TERM  # Termination  
trap 'cleanup' EXIT      # Normal exit

# Secure API key handling (using file instead of env var)
get_cursor_api_key() {
    local key_file="$HOME/.cursor/api-key"

    if [[ ! -f "$key_file" ]]; then
        # Fallback to environment variable
        if [[ -n "${CURSOR_API_KEY:-}" ]]; then
            echo "$CURSOR_API_KEY"
            return 0
        fi
        die "Cursor API key file not found: $key_file and CURSOR_API_KEY not set"
    fi

    # Verify file permissions are restrictive
    local perms=$(stat -c %a "$key_file" 2>/dev/null)
    if [[ "$perms" != "600" ]]; then
        die "API key file has insecure permissions: $perms (expected 600)"
    fi

    cat "$key_file"
}

# Secure temporary file creation
create_temp_file() {
    local temp_file
    temp_file="$(mktemp)"
    chmod 600 "$temp_file"
    TEMP_FILES+=("$temp_file")
    echo "$temp_file"
}

# Command validation
require_cmd() {
    for c in "$@"; do
        command -v "$c" >/dev/null 2>&1 || { 
            die "Missing required command: $c"
        }
    done
}

# Exponential backoff with jitter and circuit breaker
exponential_backoff() {
    local max_retries=$1; shift
    local base_delay=$1; shift  
    local cmd=("$@")
    local consecutive_failures=0

    for ((i=1; i<=max_retries; i++)); do
        if "${cmd[@]}"; then 
            consecutive_failures=0
            return 0
        fi
        
        consecutive_failures=$((consecutive_failures + 1))
        
        # Circuit breaker: if too many consecutive failures, abort
        if [[ $consecutive_failures -ge 5 ]]; then
            secure_log error "Circuit breaker triggered: too many consecutive failures ($consecutive_failures)"
            return 1
        fi
        
        if [[ $i -eq $max_retries ]]; then return 1; fi

        # Add jitter to prevent thundering herd
        local jitter=$((RANDOM % 1000))
        local sleep_time=$(( (base_delay * (2 ** (i-1))) + jitter ))
        secure_log warn "Command failed (attempt $i/$max_retries): ${cmd[*]}, retrying in ${sleep_time}ms"
        sleep $(( sleep_time / 1000 ))
    done
}

# Legacy retry function for backward compatibility
retry() {
    exponential_backoff "$@"
}

# Load Cursor CLI configuration
load_cursor_config() {
    if [[ -f "$CURSOR_CONFIG_FILE" ]]; then
        secure_log info "Loading Cursor CLI configuration from $CURSOR_CONFIG_FILE"
        
        # Extract configuration values using jq
        if command -v jq >/dev/null 2>&1; then
            AGENT_MODEL="$(jq -r '.model // "auto"' "$CURSOR_CONFIG_FILE" 2>/dev/null || echo "auto")"
            local timeout_ms
            timeout_ms="$(jq -r '.timeout // 60000' "$CURSOR_CONFIG_FILE" 2>/dev/null || echo "60000")"
            AGENT_TIMEOUT_SEC=$(( timeout_ms / 1000 ))
            MCP_ENABLED="$(jq -r '.mcp.enabled // false' "$CURSOR_CONFIG_FILE" 2>/dev/null || echo "false")"
            MCP_SERVERS="$(jq -r '.mcp.servers[]? // empty' "$CURSOR_CONFIG_FILE" 2>/dev/null | paste -sd ',' - || echo "")"
            
            secure_log debug "Loaded config: model=$AGENT_MODEL, timeout=${AGENT_TIMEOUT_SEC}s, mcp=$MCP_ENABLED, servers=$MCP_SERVERS"
        else
            secure_log warn "jq not found, using default configuration"
        fi
    else
        secure_log debug "Cursor CLI config not found at $CURSOR_CONFIG_FILE, using defaults"
    fi
}

# Extract and validate JSON from agent output with proper error handling
extract_json() {
    local input="$1"
    
    # Check if jq is available
    if ! command -v jq >/dev/null 2>&1; then
        secure_log error "jq command not found - cannot parse JSON"
        return 1
    fi
    
    # Validate input is not empty
    if [[ -z "$input" ]]; then
        secure_log error "Empty input provided to extract_json"
        return 1
    fi
    
    # Try to extract from cursor-agent result field (most common case)
    if echo "$input" | jq -e '.result' >/dev/null 2>&1; then
        local result_content
        if result_content=$(echo "$input" | jq -r '.result' 2>/dev/null); then
            if [[ -n "$result_content" ]] && [[ "$result_content" != "null" ]]; then
                # Try to extract JSON from the result content
                if echo "$result_content" | jq -e . >/dev/null 2>&1; then
                    echo "$result_content"
                    return 0
                fi
                
                # Try extracting from markdown in result
                local extracted
                if extracted=$(echo "$result_content" | sed -n '/```json/,/```/p' | sed '1d;$d' 2>/dev/null); then
                    if [[ -n "$extracted" ]] && echo "$extracted" | jq -e . >/dev/null 2>&1; then
                        echo "$extracted"
                        return 0
                    fi
                fi
                
                # Try extracting from any ``` blocks in result
                if extracted=$(echo "$result_content" | sed -n '/```/,/```/p' | sed '1d;$d' 2>/dev/null); then
                    if [[ -n "$extracted" ]] && echo "$extracted" | jq -e . >/dev/null 2>&1; then
                        echo "$extracted"
                        return 0
                    fi
                fi
            fi
        else
            secure_log debug "Failed to extract result field from input"
        fi
    fi
    
    # Try direct parse (for cases where input is already the JSON we want)
    if echo "$input" | jq -e . >/dev/null 2>&1; then
        echo "$input"
        return 0
    fi
    
    # Try extracting from ```json blocks (more robust)
    local extracted
    if extracted=$(echo "$input" | sed -n '/```json/,/```/p' | sed '1d;$d' 2>/dev/null); then
        if [[ -n "$extracted" ]] && echo "$extracted" | jq -e . >/dev/null 2>&1; then
            echo "$extracted"
            return 0
        fi
    fi
    
    # Try extracting from ``` blocks (without json marker)
    if extracted=$(echo "$input" | sed -n '/```/,/```/p' | sed '1d;$d' 2>/dev/null); then
        if [[ -n "$extracted" ]] && echo "$extracted" | jq -e . >/dev/null 2>&1; then
            echo "$extracted"
            return 0
        fi
    fi
    
    # Try finding first JSON object {...} anywhere in the input (safer regex)
    if extracted=$(echo "$input" | grep -oE '\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}' | head -1 2>/dev/null); then
        if [[ -n "$extracted" ]] && echo "$extracted" | jq -e . >/dev/null 2>&1; then
            echo "$extracted"
            return 0
        fi
    fi
    
    secure_log error "Could not extract valid JSON from input"
    secure_log debug "Input was: $(echo "$input" | head -c 200)"
    return 1
}

# JSON schema validation for agent responses
validate_agent_response_schema() {
    local json_input="$1"
    local mode="$2"
    
    # Check if input is valid JSON
    if ! echo "$json_input" | jq -e . >/dev/null 2>&1; then
        secure_log error "Invalid JSON provided for schema validation"
        return 1
    fi
    
    case "$mode" in
        planning)
            # Validate planning response schema
            if ! echo "$json_input" | jq -e '.batches' >/dev/null 2>&1; then
                secure_log error "Planning response missing required 'batches' field"
                return 1
            fi
            if ! echo "$json_input" | jq -e '.batches | type == "array"' >/dev/null 2>&1; then
                secure_log error "Planning response 'batches' field must be an array"
                return 1
            fi
            ;;
        execution)
            # Validate execution response schema
            if ! echo "$json_input" | jq -e '.valid' >/dev/null 2>&1; then
                secure_log error "Execution response missing required 'valid' field"
                return 1
            fi
            ;;
    esac
    
    return 0
}

# Test Cursor API key validity
test_cursor_api_key() {
    local api_key
    api_key="$(get_cursor_api_key)"
    
    if [[ -z "$api_key" ]]; then
        return 2  # API key not set
    fi
    
    # Make a simple test call to validate the API key
    local test_prompt="Return only valid JSON: {\"test\": \"success\"}"
    local test_output
    test_output="$(timeout 10s cursor-agent -p --output-format json "$test_prompt" 2>/dev/null || echo "")"
    
    # Extract JSON from the response (handle markdown wrapping)
    local extracted_json
    if extracted_json="$(extract_json "$test_output" 2>/dev/null)"; then
        if echo "$extracted_json" | jq -e '.test' >/dev/null 2>&1; then
            return 0  # API key is valid
        fi
    fi
    
    return 3  # API key is invalid
}

# Cursor Agent invocation with JSON output
run_cursor_agent() {
    local mode="${1:-}"; shift
    local prompt="${1:-}"; shift
    local outfile="${1:-}"; shift

    local api_key
    api_key="$(get_cursor_api_key)"

    # Build prompt based on mode - be very explicit about JSON output
    local full_prompt
    case "$mode" in
        planning)
            full_prompt="You are a CI repair planner for OpenSSL modernization.

$prompt

CRITICAL INSTRUCTIONS:
1. Analyze the situation thoroughly
2. Create a step-by-step plan with dependencies
3. List any risks or concerns
4. Your ENTIRE response must be ONLY valid JSON - no markdown, no code blocks, no explanations
5. Start your response with { and end with }

Required JSON structure:
{
  \"batches\": [
    {\"name\": \"batch-1\", \"actions\": [\"rerun:ID\", \"approve:ID\", \"apply-patch:filename\", \"enable-workflow:path.yml\"]}
  ],
  \"patches\": [
    {\"filename\": \"path/to/file.yml\", \"diff\": \"--- a/path\\n+++ b/path\\n@@ -1,1 +1,1 @@\\n-old\\n+new\"}
  ],
  \"stop_condition\": \"all_green\",
  \"notes\": \"brief rationale\"
}"
            ;;
        execution)
            full_prompt="You are validating and executing a CI repair plan.

$prompt

CRITICAL INSTRUCTIONS:
1. Validate YAML syntax and minimal-risk nature
2. Check for incompatible workflows
3. Verify trigger configuration
4. Your ENTIRE response must be ONLY valid JSON - no markdown, no code blocks, no explanations
5. Start your response with { and end with }

Required JSON structure:
{
  \"valid\": true,
  \"issues\": [\"list any issues found\"],
  \"corrected_patches\": [
    {\"filename\": \"path.yml\", \"diff\": \"unified diff\"}
  ]
}"
            ;;
        *)
            full_prompt="$prompt"
            ;;
    esac

    secure_log info "Running cursor-agent in headless mode (mode=$mode, model=$AGENT_MODEL, timeout=${AGENT_TIMEOUT_SEC}s, mcp=$MCP_ENABLED)"
    
    local tmp_output tmp_clean tmp_stderr
    tmp_output="$(create_temp_file)"
    tmp_clean="$(create_temp_file)"
    tmp_stderr="$(create_temp_file)"
    local exit_code=0
    
    if command -v cursor-agent >/dev/null 2>&1; then
        # Build cursor-agent command with supported options only
        local cmd_args=(
            "-p"
            "--output-format" "json"
        )
        
        # Note: cursor-agent doesn't support --config, --mcp, --agent, --rules options
        # Configuration is handled via environment variables and .cursor/ directory
        secure_log debug "Using basic cursor-agent command (advanced options not supported)"
        
        # Execute with enhanced context
        if timeout "${AGENT_TIMEOUT_SEC}s" cursor-agent "${cmd_args[@]}" \
            "$full_prompt" >"$tmp_output" 2>"$tmp_stderr"; then
            secure_log info "Agent completed successfully"
        else
            exit_code=$?
            secure_log warn "Agent exited with code $exit_code"
            
            # Provide specific error messages based on exit code
            case $exit_code in
                1)
                    secure_log error "Cursor-agent failed - likely authentication or configuration issue"
                    secure_log info "Check your API key: https://cursor.com/settings/api"
                    ;;
                124)
                    secure_log error "Cursor-agent timed out after ${AGENT_TIMEOUT_SEC}s"
                    secure_log info "Try increasing AGENT_TIMEOUT_SEC or check network connectivity"
                    ;;
                127)
                    secure_log error "Cursor-agent command not found"
                    secure_log info "Install cursor-agent: curl https://cursor.com/install -fsS | bash"
                    ;;
                *)
                    secure_log error "Cursor-agent failed with unexpected exit code $exit_code"
                    ;;
            esac
            
            # Log stderr for debugging (usually contains the python3 ENOENT error)
            if [[ -f "$tmp_stderr" ]] && [[ -s "$tmp_stderr" ]]; then
                secure_log debug "Agent stderr: $(head -c 200 "$tmp_stderr" 2>/dev/null || echo 'empty')"
            fi
            # Log stdout for debugging
            if [[ -f "$tmp_output" ]] && [[ -s "$tmp_output" ]]; then
                secure_log debug "Agent stdout: $(head -c 500 "$tmp_output" 2>/dev/null || echo 'empty')"
            fi
        fi
    else
        secure_log error "cursor-agent command not found"
        exit_code=127
    fi
    
    # Preprocess output to find the last line that looks like JSON
    # This handles cases where there might be noise before the JSON
    local json_line
    if [[ -f "$tmp_output" ]]; then
        json_line="$(grep -E '^\{.*\}$' "$tmp_output" | tail -1 2>/dev/null || echo "")"
        if [[ -n "$json_line" ]]; then
            echo "$json_line" > "$tmp_output"
        fi
    fi
    
    # Extract the actual result from the JSON wrapper
    # The agent output is: {"type":"result","subtype":"success",...,"result":"<actual content>"}
    if [[ -f "$tmp_output" ]] && jq -e '.result' "$tmp_output" >/dev/null 2>&1; then
        local agent_result
        agent_result="$(jq -r '.result' "$tmp_output" 2>/dev/null || echo "")"
        
        if [[ -n "$agent_result" ]]; then
            # Try to extract clean JSON
            if extract_json "$agent_result" > "$tmp_clean" 2>/dev/null; then
                # Validate schema before saving
                local extracted_json
                extracted_json="$(cat "$tmp_clean")"
                if validate_agent_response_schema "$extracted_json" "$mode"; then
                    mv "$tmp_clean" "$outfile"
                    secure_log info "Successfully extracted and validated JSON from agent response"
                else
                    secure_log warn "Agent response failed schema validation, saving anyway"
                    mv "$tmp_clean" "$outfile"
                fi
            else
                # Save raw result and warn
                echo "$agent_result" > "$outfile"
                secure_log warn "Agent output is not valid JSON, saved raw result"
                secure_log debug "Raw result: $(echo "$agent_result" | head -c 200)"
            fi
        else
            secure_log error "No result field in agent output"
            cp "$tmp_output" "$outfile" 2>/dev/null || echo '{}' > "$outfile"
        fi
    else
        secure_log error "Invalid JSON response from agent"
        if [[ -f "$tmp_output" ]]; then
            secure_log debug "Raw agent output: $(head -c 500 "$tmp_output" 2>/dev/null || echo 'empty')"
            # Try to find any JSON-like content
            local potential_json
            potential_json="$(grep -oE '\{[^}]*\}' "$tmp_output" 2>/dev/null | head -1 || echo "")"
            if [[ -n "$potential_json" ]]; then
                secure_log debug "Found potential JSON: $(echo "$potential_json" | head -c 200)"
            fi
        fi
        cp "$tmp_output" "$outfile" 2>/dev/null || echo '{}' > "$outfile"
    fi
    
    # Temp files are cleaned up automatically by trap
    
    # Log excerpt for debugging
    if [[ -f "$outfile" ]]; then
        local excerpt
        excerpt="$(head -c 300 "$outfile" 2>/dev/null || echo "")"
        secure_log debug "Agent output excerpt: $(echo "$excerpt" | jq -Rs . 2>/dev/null || echo '""')"
    fi
    
    return $exit_code
}

# GitHub API functions with retry logic
get_runs_json() {
    exponential_backoff 3 1000 gh run list --limit 30 --json databaseId,displayTitle,workflowName,status,conclusion,headBranch,createdAt,updatedAt 2>/dev/null || echo "[]"
}

get_pr_status_json() {
    exponential_backoff 3 1000 gh pr view "$PR_NUMBER" --json statusCheckRollup,headRefName,baseRefName,author,mergeable,mergeStateStatus 2>/dev/null || echo "{}"
}

get_open_runs_not_green() {
    jq -r '[ .[] | select(.status!="completed" or .conclusion!="success") ]' <<<"$1"
}

approve_or_rerun() {
    local runs_json="$1"
    local ids
    mapfile -t ids < <(jq -r '.[] | select(.status!="completed" or .conclusion!="success") | .databaseId' <<<"$runs_json")
    for rid in "${ids[@]}"; do
        [[ -z "$rid" ]] && continue
        local status concl
        status="$(gh run view "$rid" --json status,conclusion --jq '.status' 2>/dev/null || echo "")"
        concl="$(gh run view "$rid" --json status,conclusion --jq '.conclusion' 2>/dev/null || echo "")"
        secure_log info "Run $rid status=$status conclusion=$concl"
        case "$status:$concl" in
            completed:failure|completed:cancelled)
                if [[ "$DRY_RUN" == "true" ]]; then
                    secure_log info "DRY RUN: Would rerun failed/cancelled run $rid"
                else
                    secure_log warn "Rerunning failed/cancelled run $rid"
                    gh run rerun "$rid" || true
                fi
                ;;
            completed:action_required)
                if [[ "$DRY_RUN" == "true" ]]; then
                    secure_log info "DRY RUN: Would approve action required for $rid"
                else
                    secure_log info "Approving action required for $rid"
                    gh run watch "$rid" --approve || true
                fi
                ;;
            queued:|in_progress:)
                secure_log info "Run $rid still queued/in_progress"
                ;;
            *)
                :
                ;;
        esac
    done
}

# Generate planning prompt
make_planning_prompt() {
    local runs_json="$1"
    local pr_json="$2"
    local recent_commits
    recent_commits="$(git log --oneline -n 15 2>/dev/null || true)"
    
    # Escape and compact JSON for embedding
    local runs_compact pr_compact
    runs_compact="$(printf '%s' "$runs_json" | jq -c '.' 2>/dev/null || echo '[]')"
    pr_compact="$(printf '%s' "$pr_json" | jq -c '.' 2>/dev/null || echo '{}')"
    
    # Add MCP context hint if enabled
    local mcp_hint=""
    if [[ "$MCP_ENABLED" == "true" ]]; then
        mcp_hint="
MCP TOOLS AVAILABLE:
You have access to the following MCP tools for gathering additional context:
- get_workflow_runs(limit): Get detailed workflow run history
- get_failed_job_logs(run_id): Get logs from failed workflow jobs
- get_pr_status(pr_number): Get PR status, checks, and metadata
- get_recent_commits(limit): Get recent commit history with details
- get_workflow_file(workflow_name): Read workflow YAML files

Use these tools BEFORE proposing fixes to understand the full context.
"
    fi
    
    cat <<EOF
You are a CI repair planner for OpenSSL modernization PR #${PR_NUMBER}.

GOAL: All workflows passing with minimal, safe, reversible changes.

CONTEXT:
- Repository: ${REPO}
- Branch: ${PR_BRANCH}
- PR Status: ${pr_compact}
- Workflow Runs: ${runs_compact}

Recent Commits:
${recent_commits}

${mcp_hint}

CONSTRAINTS:
1. Prefer rerun/approve actions over file edits
2. If edits needed, provide unified diff patches (small, focused)
3. Avoid enabling legacy upstream workflows incompatible with Conan 2.0/MCP
4. Avoid queue explosions: propose selective triggers and concurrency groups
5. All changes must be reversible

ANALYSIS REQUIRED:
1. Identify which workflows are failing and why
2. Determine if failures are flaky (rerun) or require fixes
3. For fixes, create minimal patches
4. Prioritize actions: approve > rerun > patch

IMPORTANT: Your response must be ONLY valid JSON. No markdown. No code blocks. No explanations outside JSON.

Start your response with { and end with }

Required structure:
{
  "batches": [
    {
      "name": "batch-1-describe-action",
      "actions": [
        "rerun:12345",
        "approve:67890",
        "apply-patch:workflow-fix.yml"
      ]
    }
  ],
  "patches": [
    {
      "filename": ".github/workflows/example.yml",
      "diff": "--- a/.github/workflows/example.yml\n+++ b/.github/workflows/example.yml\n@@ -10,1 +10,1 @@\n-    branches: [ main ]\n+    branches: [ main, ${PR_BRANCH} ]"
    }
  ],
  "stop_condition": "all_green",
  "notes": "Brief rationale for the plan"
}
EOF
}

# Apply patch with enhanced security
apply_patch() {
    local fname="$1"
    local diff_content="$2"
    
    secure_log info "Applying patch to $fname"
    
    # Check if file exists
    if [[ ! -f "$fname" ]]; then
        secure_log warn "File $fname does not exist, skipping patch"
        return 1
    fi
    
    # Check git repository status
    if ! git rev-parse --git-dir >/dev/null 2>&1; then
        secure_log error "Not in a git repository, cannot apply patch"
        return 1
    fi
    
    # Check if working directory is clean (allow staged changes)
    if ! git diff --quiet; then
        secure_log warn "Working directory has unstaged changes, patch may conflict"
    fi
    
    if [[ "$DRY_RUN" == "true" ]]; then
        secure_log info "DRY RUN: Would apply patch to $fname"
        return 0
    fi
    
    # Write diff to secure temp file
    local tmp
    tmp="$(create_temp_file)"
    printf '%s\n' "$diff_content" >"$tmp"
    
    # Try to apply patch
    if git apply --check "$tmp" 2>/dev/null; then
        if git apply --index "$tmp"; then
            secure_log info "Successfully applied patch to $fname"
            return 0
        else
            secure_log error "Failed to apply patch to $fname (check failed but apply failed)"
            return 1
        fi
    else
        secure_log error "git apply --check failed for $fname"
        secure_log debug "Patch content: $(cat "$tmp" | head -20)"
        return 1
    fi
}

commit_and_push() {
    local msg="$1"
    
    # Check if there are changes
    if git diff --cached --quiet && git diff --quiet; then
        secure_log info "No changes to commit"
        return 0
    fi
    
    # Stage any unstaged changes
    git add -u 2>/dev/null || true
    
    # Show what will be committed
    secure_log debug "Changes to commit: $(git diff --cached --stat)"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        secure_log info "DRY RUN: Would commit with message: $msg"
        secure_log info "DRY RUN: Would push to $PR_BRANCH"
        return 0
    fi
    
    # Commit
    if ! git diff --cached --quiet; then
        if git commit -m "$msg"; then
            secure_log info "Committed: $msg"
        else
            secure_log warn "Commit failed"
            return 1
        fi
    fi
    
    # Push
    if git push origin "$PR_BRANCH" 2>&1; then
        secure_log info "Pushed to $PR_BRANCH"
        return 0
    else
        secure_log error "Push failed"
        return 1
    fi
}

# Apply patches from plan
apply_patches_from_plan() {
    local plan_file="$1"
    
    if [[ ! -f "$plan_file" ]]; then
        secure_log warn "Plan file not found: $plan_file"
        return 1
    fi
    
    local patches_len
    patches_len="$(jq -r '.patches | length' "$plan_file" 2>/dev/null || echo 0)"
    
    if [[ "$patches_len" -eq 0 ]]; then
        secure_log info "No patches to apply"
        return 0
    fi
    
    secure_log info "Applying $patches_len patches from plan"
    local applied=0
    
    for i in $(seq 0 $((patches_len-1))); do
        local fname diffc
        fname="$(jq -r ".patches[$i].filename" "$plan_file" 2>/dev/null || echo "")"
        diffc="$(jq -r ".patches[$i].diff" "$plan_file" 2>/dev/null || echo "")"
        
        if [[ -z "$fname" ]] || [[ -z "$diffc" ]] || [[ "$diffc" == "null" ]]; then
            secure_log warn "Skipping invalid patch at index $i"
            continue
        fi
        
        if apply_patch "$fname" "$diffc"; then
            applied=$((applied + 1))
        fi
    done
    
    if [[ $applied -gt 0 ]]; then
        commit_and_push "ci: apply $applied planned patches"
        
        # Clear patches after successful apply
        local tmp
        tmp="$(create_temp_file)"
        jq '.patches = []' "$plan_file" > "$tmp" && mv "$tmp" "$plan_file"
    fi
    
    return 0
}

# Execute batch actions from plan
execute_batch_actions() {
    local plan_file="$1"
    
    if [[ ! -f "$plan_file" ]]; then
        secure_log warn "Plan file not found: $plan_file"
        return 1
    fi
    
    local batches_len
    batches_len="$(jq -r '.batches | length' "$plan_file" 2>/dev/null || echo 0)"
    
    if [[ "$batches_len" -eq 0 ]]; then
        secure_log info "No batch actions to execute"
        return 0
    fi
    
    # Get first batch
    local batch_name actions_len
    batch_name="$(jq -r '.batches[0].name' "$plan_file" 2>/dev/null || echo "unnamed")"
    actions_len="$(jq -r '.batches[0].actions | length' "$plan_file" 2>/dev/null || echo 0)"
    
    if [[ "$actions_len" -eq 0 ]]; then
        secure_log info "Batch '$batch_name' has no actions, removing"
        local tmp
        tmp="$(create_temp_file)"
        jq '.batches |= .[1:]' "$plan_file" > "$tmp" && mv "$tmp" "$plan_file"
        return 0
    fi
    
    secure_log info "Executing batch '$batch_name' with $actions_len actions"
    
    for idx in $(seq 0 $((actions_len-1))); do
        local action
        action="$(jq -r ".batches[0].actions[$idx]" "$plan_file" 2>/dev/null || echo "")"
        
        [[ -z "$action" ]] && continue
        
        case "$action" in
            rerun:*)
                local rid="${action#rerun:}"
                if [[ "$DRY_RUN" == "true" ]]; then
                    secure_log info "DRY RUN: Would rerun workflow run: $rid"
                else
                    secure_log info "Rerunning workflow run: $rid"
                    gh run rerun "$rid" 2>&1 || secure_log warn "Failed to rerun $rid"
                fi
                ;;
            approve:*)
                local rid="${action#approve:}"
                if [[ "$DRY_RUN" == "true" ]]; then
                    secure_log info "DRY RUN: Would approve workflow run: $rid"
                else
                    secure_log info "Approving workflow run: $rid"
                    gh run watch "$rid" --approve 2>&1 || secure_log warn "Failed to approve $rid"
                fi
                ;;
            apply-patch:*)
                local patchname="${action#apply-patch:}"
                secure_log info "Looking for patch: $patchname in plan"
                # Find this patch in the patches array and apply it
                local patch_idx
                patch_idx=$(jq -r ".patches | map(.filename | contains(\"$patchname\")) | index(true)" "$plan_file" 2>/dev/null || echo "null")
                if [[ "$patch_idx" != "null" ]]; then
                    local fname diffc
                    fname="$(jq -r ".patches[$patch_idx].filename" "$plan_file")"
                    diffc="$(jq -r ".patches[$patch_idx].diff" "$plan_file")"
                    if [[ "$DRY_RUN" == "true" ]]; then
                        secure_log info "DRY RUN: Would apply patch to $fname"
                    else
                        apply_patch "$fname" "$diffc" || true
                    fi
                else
                    secure_log warn "Patch $patchname not found in patches array"
                fi
                ;;
            enable-workflow:*)
                local wpath="${action#enable-workflow:}"
                local wname="$(basename "$wpath")"
                if [[ "$DRY_RUN" == "true" ]]; then
                    secure_log info "DRY RUN: Would enable workflow: $wname"
                else
                    secure_log info "Enabling workflow: $wname"
                    if [[ -f ".github/workflows-disabled/$wname" ]]; then
                        git mv ".github/workflows-disabled/$wname" ".github/workflows/$wname" 2>/dev/null || true
                        git add ".github/workflows/$wname" 2>/dev/null || true
                    else
                        secure_log warn "Workflow $wname not found in workflows-disabled/"
                    fi
                fi
                ;;
            disable-workflow:*)
                local wpath="${action#disable-workflow:}"
                local wname="$(basename "$wpath")"
                if [[ "$DRY_RUN" == "true" ]]; then
                    secure_log info "DRY RUN: Would disable workflow: $wname"
                else
                    secure_log info "Disabling workflow: $wname"
                    if [[ -f ".github/workflows/$wname" ]]; then
                        git mv ".github/workflows/$wname" ".github/workflows-disabled/$wname" 2>/dev/null || true
                        git add ".github/workflows-disabled/$wname" 2>/dev/null || true
                    else
                        secure_log warn "Workflow $wname not found in workflows/"
                    fi
                fi
                ;;
            rerun-failed-workflows)
                if [[ "$DRY_RUN" == "true" ]]; then
                    secure_log info "DRY RUN: Would rerun all failed workflows"
                else
                    secure_log info "Rerunning all failed workflows"
                    # Get current failed runs and rerun them
                    local current_runs
                    current_runs="$(get_runs_json)"
                    approve_or_rerun "$current_runs"
                fi
                ;;
            *)
                secure_log warn "Unknown action: $action"
                ;;
        esac
    done
    
    # Commit any changes from batch actions
    if ! git diff --cached --quiet || ! git diff --quiet; then
        commit_and_push "ci: execute batch '$batch_name' actions"
    fi
    
    # Remove executed batch
    local tmp
    tmp="$(create_temp_file)"
    jq '.batches |= .[1:]' "$plan_file" > "$tmp" && mv "$tmp" "$plan_file"
    
    return 0
}

# Generate fallback plan
generate_fallback_plan() {
    local outfile="${1:-}"
    secure_log warn "Generating minimal fallback plan"
    
    # Simple fallback: just rerun failed workflows
    local fallback_plan='{
  "batches": [
    {
      "name": "fallback-rerun-failed",
      "actions": ["rerun-failed-workflows"]
    }
  ],
  "patches": [],
  "stop_condition": "all_green",
  "notes": "Fallback plan - simple rerun of failed workflows"
}'
    
    if [[ -n "$outfile" ]]; then
        echo "$fallback_plan" > "$outfile"
    else
        echo "$fallback_plan"
    fi
}

# Collect workflow runs
collect_workflow_runs() {
    get_runs_json
}

# Collect PR information
collect_pr_info() {
    get_pr_status_json
}

# Check workflow status
check_workflow_status() {
    local runs_json="$1"
    get_open_runs_not_green "$runs_json"
}

# Generate plan
generate_plan() {
    local runs_json="$1"
    local pr_json="$2"
    local not_green="$3"
    
    # Create planning prompt
    local prompt
    prompt="$(make_planning_prompt "$runs_json" "$pr_json" "$not_green")"
    
    # Create temporary file for plan output
    local plan_file="$(create_temp_file)"
    
    # Run cursor agent to generate plan
    if run_cursor_agent "planning" "$prompt" "$plan_file"; then
        if [[ -f "$plan_file" ]] && [[ -s "$plan_file" ]]; then
            cat "$plan_file"
            rm -f "$plan_file"
        else
            generate_fallback_plan
        fi
    else
        generate_fallback_plan
    fi
}

# Execute plan
execute_plan() {
    local plan="$1"
    
    # Create temporary file for plan
    local plan_file="$(create_temp_file)"
    echo "$plan" > "$plan_file"
    
    # Execute batch actions from plan
    execute_batch_actions "$plan_file"
    
    # Clean up
    rm -f "$plan_file"
}

# Main orchestration
main() {
    # Parse command line arguments first (allows --help to work without dependencies)
    declare -a REMAINING_ARGS=()
    parse_args "$@"
    
    # Restore positional parameters
    set -- "${REMAINING_ARGS[@]}"
    
    # Check required commands (after --help is handled)
    require_cmd gh jq git curl timeout
    
    # Load configuration
    load_config
    
    # Validate inputs
    validate_inputs
    
    # Load Cursor CLI configuration early
    load_cursor_config
    
    secure_log info "=== Agent Loop Start ==="
    secure_log info "Repository: $REPO"
    secure_log info "PR: #${PR_NUMBER} ($PR_BRANCH)"
    secure_log info "Mode: $MODE"
    secure_log info "Max iterations: $MAX_ITERATIONS"
    secure_log info "Run once: $RUN_ONCE"
    secure_log info "Streaming: $USE_STREAMING"
    secure_log info "Dry run: $DRY_RUN"
    secure_log info "Interval: ${INTERVAL}s"
    secure_log info "Cursor Config: $CURSOR_CONFIG_FILE (MCP: $MCP_ENABLED)"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        secure_log info "DRY RUN MODE: No actual changes will be made"
    fi
    
    # Test cursor-agent configuration
    secure_log info "Testing cursor-agent configuration..."
    
    # Test cursor-agent configuration with actual API validation
    local test_result=2  # Default to API key not set
    if ! command -v cursor-agent >/dev/null 2>&1; then
        test_result=1  # Command not found
    elif [[ -n "$(get_cursor_api_key 2>/dev/null)" ]]; then
        if test_cursor_api_key; then
            test_result=0  # API key is valid and working
        else
            test_result=3  # API key format looks correct but doesn't work
        fi
    fi
    
    secure_log debug "test_cursor_agent returned: $test_result"
    
    case $test_result in
        0)
            secure_log info "cursor-agent configured correctly - AI-powered planning enabled"
            ;;
        1)
            secure_log warn "cursor-agent not found, running in simple mode (rerun/approve only)"
            secure_log info "Install cursor-agent: curl https://cursor.com/install -fsS | bash"
            ;;
        2)
            secure_log warn "cursor-agent found but API key not set, running in simple mode"
            secure_log info "To enable AI-powered planning, set up API key file: $HOME/.cursor/api-key"
            secure_log info "Or set CURSOR_API_KEY environment variable"
            secure_log info "Get your API key from: https://cursor.com/settings/api"
            ;;
        3)
            secure_log warn "cursor-agent authentication failed, running in simple mode"
            secure_log error "API key format looks correct but authentication failed"
            secure_log info "Check if your API key is valid and not expired"
            secure_log info "Get a new API key from: https://cursor.com/settings/api"
            ;;
        *)
            secure_log warn "cursor-agent test failed with unknown issue, running in simple mode"
            secure_log info "Check cursor-agent installation and configuration"
            ;;
    esac
    
    secure_log debug "Case statement completed, continuing with branch check"
    
    # Ensure we're on the correct branch
    local current_branch
    current_branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")"
    if [[ "$current_branch" != "$PR_BRANCH" ]]; then
        secure_log warn "Not on target branch ($PR_BRANCH), currently on ($current_branch)"
        secure_log info "Attempting to checkout $PR_BRANCH..."
        
        # Try to fetch and checkout
        if git fetch origin "pull/${PR_NUMBER}/head:${PR_BRANCH}" 2>&1; then
            git checkout "$PR_BRANCH" 2>&1 || secure_log error "Checkout failed"
        else
            secure_log warn "Could not fetch PR, trying direct checkout"
            git checkout "$PR_BRANCH" 2>&1 || secure_log error "Checkout failed"
        fi
        
        # Pull latest
        git pull origin "$PR_BRANCH" 2>&1 || secure_log warn "Pull failed"
    fi
    
    # Verify we're on correct branch now
    current_branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")"
    if [[ "$current_branch" != "$PR_BRANCH" ]]; then
        secure_log error "Still not on $PR_BRANCH after checkout attempt, aborting"
        exit 1
    fi
    
    secure_log info "Working on branch: $current_branch"
    
    # File paths for agent outputs
    local plan_file=".agent_plan.json"
    local execution_file=".agent_execution.json"
    
    # Initial status check
    local runs_json pr_json not_green not_green_len
    
    # Main loop
    local iteration=0
    while [[ $iteration -lt $MAX_ITERATIONS ]]; do
        iteration=$((iteration + 1))
        secure_log info "=== Iteration $iteration/$MAX_ITERATIONS ==="
        
        # Collect current state
        runs_json="$(collect_workflow_runs)"
        pr_json="$(collect_pr_info)"
        
        # Check if all workflows are green
        not_green="$(check_workflow_status "$runs_json")"
        not_green_len="$(echo "$not_green" | jq length)"
        
        if [[ "$not_green_len" == "0" ]]; then
            secure_log info "All workflows are green! 🎉"
            break
        fi

        secure_log info "Found $not_green_len workflows needing attention"
        
        # Generate plan
        local plan
        if [[ $test_result -eq 0 ]]; then
            plan="$(generate_plan "$runs_json" "$pr_json" "$not_green")"
            
            if [[ -z "$plan" ]]; then
                secure_log warn "No actionable plan generated, trying simple rerun..."
                # Simple fallback: rerun failed workflows
                approve_or_rerun "$not_green"
            else
                # Execute plan
                execute_plan "$plan"
            fi
        else
            secure_log info "Running in simple mode - rerunning failed workflows"
            # Simple mode: just rerun failed workflows
            approve_or_rerun "$not_green"
        fi
        
        # Wait before next iteration
        secure_log info "Waiting ${INTERVAL}s before next iteration..."
        sleep "$INTERVAL"
    done
    
    if [[ $iteration -eq $MAX_ITERATIONS ]]; then
        secure_log warn "Reached maximum iterations ($MAX_ITERATIONS)"
    fi
    
    secure_log info "=== Agent Loop Complete ==="
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
