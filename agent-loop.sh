#!/usr/bin/env bash
# agent-loop.sh – Robustní CI orchestrace s plánováním a validací (Cursor-Agent)
# Použití:
#   ./agent-loop.sh "Popis úkolu" execution
#   ./agent-loop.sh "Diagnostika a plán" planning
#   ./agent-loop.sh --once "Fix failed workflows" execution  # Run once and exit
# Konfigurace přes env:
#   PR_NUMBER (default 6), PR_BRANCH (default simplify-openssl-build)
#   REPO (default sparesparrow/openssl-tools)
#   MAX_ITERATIONS (default 12), INTERVAL (default 60)
#   AGENT_TIMEOUT_SEC (default 600)
#   LOG_LEVEL (debug|info|warn|error, default info)
#   USE_STREAMING (true/false, default false)
#   RUN_ONCE (true/false, default false) - Run single iteration then exit

set -euo pipefail

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

# Global cleanup tracking
declare -a temp_files=()
declare -a background_pids=()

# Cleanup function for signal handling
cleanup() {
    local exit_code=$?
    
    # Kill any background processes
    for pid in "${background_pids[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null || true
            wait "$pid" 2>/dev/null || true
        fi
    done
    
    # Cleanup temp files
    for temp_file in "${temp_files[@]}"; do
        [[ -f "$temp_file" ]] && rm -f "$temp_file" 2>/dev/null || true
    done
    
    # Kill any remaining child processes
    jobs -p | xargs -r kill 2>/dev/null || true
    
    exit $exit_code
}

# Set up signal handlers
trap cleanup EXIT SIGTERM SIGINT

# Secure temporary file creation
create_temp_file() {
    local temp_file
    temp_file="$(mktemp)"
    chmod 600 "$temp_file"
    temp_files+=("$temp_file")
    echo "$temp_file"
}

# Input validation functions
validate_repo_format() {
    local repo="$1"
    if [[ ! "$repo" =~ ^[a-zA-Z0-9_-]+/[a-zA-Z0-9_.-]+$ ]]; then
        log error "Invalid repository format: $repo (expected: owner/repo)"
        return 1
    fi
    return 0
}

validate_pr_number() {
    local pr_num="$1"
    if [[ ! "$pr_num" =~ ^[0-9]+$ ]] || [[ "$pr_num" -lt 1 ]]; then
        log error "Invalid PR number: $pr_num (expected: positive integer)"
        return 1
    fi
    return 0
}

validate_branch_name() {
    local branch="$1"
    if [[ ! "$branch" =~ ^[a-zA-Z0-9._/-]+$ ]] || [[ ${#branch} -gt 255 ]]; then
        log error "Invalid branch name: $branch (expected: alphanumeric with dots, underscores, slashes, hyphens, max 255 chars)"
        return 1
    fi
    return 0
}

validate_all_inputs() {
    validate_repo_format "$REPO" || return 1
    validate_pr_number "$PR_NUMBER" || return 1
    validate_branch_name "$PR_BRANCH" || return 1
    return 0
}

# Parse command line arguments
RUN_ONCE="${RUN_ONCE:-false}"
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
Usage: $0 [OPTIONS] [TASK] [MODE]

Options:
  --once           Run single iteration then exit (default: false)
  --dry-run        Simulate actions without making changes (default: false)
  --help, -h       Show this help message

Arguments:
  TASK             Task description (default: "Ensure all PR workflows are green")
  MODE             Operation mode: planning or execution (default: execution)

Environment Variables:
  REPO             Repository (default: sparesparrow/openssl-tools)
  PR_NUMBER        PR number (default: 6)
  PR_BRANCH        Branch name (default: simplify-openssl-build)
  MAX_ITERATIONS   Maximum loop iterations (default: 12)
  INTERVAL         Seconds between iterations (default: 60)
  AGENT_TIMEOUT_SEC Agent timeout in seconds (default: 60)
  LOG_LEVEL        Logging level: debug|info|warn|error (default: info)
  CURSOR_API_KEY   Cursor API key for AI-powered mode

Examples:
  $0 --once "Fix failed workflows" execution
  $0 --dry-run "Analyze CI issues" planning
  CURSOR_API_KEY=key_xxx $0 "Repair all workflows" execution
EOF
      exit 0
      ;;
    *)
      break
      ;;
  esac
done

# Defaults
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
  log info "Running in single-iteration mode (--once)"
fi

# Cursor CLI configuration paths
CURSOR_CONFIG_FILE="${CURSOR_CONFIG_FILE:-.cursor/cli-config.json}"
CURSOR_MCP_CONFIG="${CURSOR_MCP_CONFIG:-mcp.json}"
CURSOR_AGENT_CONFIG="${CURSOR_AGENT_CONFIG:-.cursor/agents/ci-repair-agent.yml}"

# Configuration values (will be loaded from config file if available)
AGENT_MODEL="${AGENT_MODEL:-auto}"
MCP_ENABLED="${MCP_ENABLED:-true}"
#MCP_SERVERS=""

# Utilities
timestamp() { date '+%Y-%m-%dT%H:%M:%S%z'; }

log() {
  local level="$1"; shift
  local msg="$*"
  # filter by level
  case "$LOG_LEVEL:$level" in
    debug:debug|debug:info|debug:warn|debug:error|info:info|info:warn|info:error|warn:warn|warn:error|error:error)
      echo "{\"ts\":\"$(timestamp)\",\"level\":\"$level\",\"msg\":$(printf '%s' "$msg" | jq -Rs .)}" >&2
      ;;
  esac
}

require_cmd() {
  for c in "$@"; do
    command -v "$c" >/dev/null 2>&1 || { echo "Missing command: $c" >&2; exit 127; }
  done
}

# Exponential backoff with jitter
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
            log error "Circuit breaker triggered: too many consecutive failures ($consecutive_failures)"
            return 1
        fi
        
        if [[ $i -eq $max_retries ]]; then return 1; fi

        # Add jitter to prevent thundering herd
        local jitter=$((RANDOM % 1000))
        local sleep_time=$(( (base_delay * (2 ** (i-1))) + jitter ))
        log warn "Command failed (attempt $i/$max_retries): ${cmd[*]}, retrying in ${sleep_time}ms"
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
    log info "Loading Cursor CLI configuration from $CURSOR_CONFIG_FILE"
    
    # Extract configuration values using jq
    if command -v jq >/dev/null 2>&1; then
      AGENT_MODEL="$(jq -r '.model // "auto"' "$CURSOR_CONFIG_FILE" 2>/dev/null || echo "auto")"
      local timeout_ms
      timeout_ms="$(jq -r '.timeout // 60000' "$CURSOR_CONFIG_FILE" 2>/dev/null || echo "60000")"
      AGENT_TIMEOUT_SEC=$(( timeout_ms / 1000 ))
      MCP_ENABLED="$(jq -r '.mcp.enabled // false' "$CURSOR_CONFIG_FILE" 2>/dev/null || echo "false")"
      MCP_SERVERS="$(jq -r '.mcp.servers[]? // empty' "$CURSOR_CONFIG_FILE" 2>/dev/null | paste -sd ',' - || echo "")"
      
      log debug "Loaded config: model=$AGENT_MODEL, timeout=${AGENT_TIMEOUT_SEC}s, mcp=$MCP_ENABLED, servers=$MCP_SERVERS"
    else
      log warn "jq not found, using default configuration"
    fi
  else
    log debug "Cursor CLI config not found at $CURSOR_CONFIG_FILE, using defaults"
  fi
}

# Note: test_cursor_agent function removed due to hanging issue
# Configuration testing is now done inline in main() function

# Extract and validate JSON from agent output with proper error handling
extract_json() {
  local input="$1"
  
  # Check if jq is available
  if ! command -v jq >/dev/null 2>&1; then
    log error "jq command not found - cannot parse JSON"
    return 1
  fi
  
  # Validate input is not empty
  if [[ -z "$input" ]]; then
    log error "Empty input provided to extract_json"
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
      log debug "Failed to extract result field from input"
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
  
  log error "Could not extract valid JSON from input"
  log debug "Input was: $(echo "$input" | head -c 200)"
  return 1
}

# JSON schema validation for agent responses
validate_agent_response_schema() {
  local json_input="$1"
  local mode="$2"
  
  # Check if input is valid JSON
  if ! echo "$json_input" | jq -e . >/dev/null 2>&1; then
    log error "Invalid JSON provided for schema validation"
    return 1
  fi
  
  case "$mode" in
    planning)
      # Validate planning response schema
      if ! echo "$json_input" | jq -e '.batches' >/dev/null 2>&1; then
        log error "Planning response missing required 'batches' field"
        return 1
      fi
      if ! echo "$json_input" | jq -e '.batches | type == "array"' >/dev/null 2>&1; then
        log error "Planning response 'batches' field must be an array"
        return 1
      fi
      ;;
    execution)
      # Validate execution response schema
      if ! echo "$json_input" | jq -e '.valid' >/dev/null 2>&1; then
        log error "Execution response missing required 'valid' field"
        return 1
      fi
      ;;
  esac
  
  return 0
}

# Test Cursor API key validity
test_cursor_api_key() {
  if [[ -z "${CURSOR_API_KEY:-}" ]]; then
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

  if [[ -z "${CURSOR_API_KEY:-}" ]]; then
    log error "CURSOR_API_KEY not set - cursor-agent requires a valid API key"
    log info "To use cursor-agent, set CURSOR_API_KEY environment variable"
    log info "Get your API key from: https://cursor.com/settings/api"
    return 1
  fi

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

  log info "Running cursor-agent in headless mode (mode=$mode, model=$AGENT_MODEL, timeout=${AGENT_TIMEOUT_SEC}s, mcp=$MCP_ENABLED)"
  
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
    log debug "Using basic cursor-agent command (advanced options not supported)"
    
    # Execute with enhanced context
    if timeout "${AGENT_TIMEOUT_SEC}s" cursor-agent "${cmd_args[@]}" \
      "$full_prompt" >"$tmp_output" 2>"$tmp_stderr"; then
      log info "Agent completed successfully"
    else
      exit_code=$?
      log warn "Agent exited with code $exit_code"
      
      # Provide specific error messages based on exit code
      case $exit_code in
        1)
          log error "Cursor-agent failed - likely authentication or configuration issue"
          log info "Check your CURSOR_API_KEY: https://cursor.com/settings/api"
          ;;
        124)
          log error "Cursor-agent timed out after ${AGENT_TIMEOUT_SEC}s"
          log info "Try increasing AGENT_TIMEOUT_SEC or check network connectivity"
          ;;
        127)
          log error "Cursor-agent command not found"
          log info "Install cursor-agent: curl https://cursor.com/install -fsS | bash"
          ;;
        *)
          log error "Cursor-agent failed with unexpected exit code $exit_code"
          ;;
      esac
      
      # Log stderr for debugging (usually contains the python3 ENOENT error)
      if [[ -f "$tmp_stderr" ]] && [[ -s "$tmp_stderr" ]]; then
        log debug "Agent stderr: $(head -c 200 "$tmp_stderr" 2>/dev/null || echo 'empty')"
      fi
      # Log stdout for debugging
      if [[ -f "$tmp_output" ]] && [[ -s "$tmp_output" ]]; then
        log debug "Agent stdout: $(head -c 500 "$tmp_output" 2>/dev/null || echo 'empty')"
      fi
    fi
  else
    log error "cursor-agent command not found"
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
          log info "Successfully extracted and validated JSON from agent response"
        else
          log warn "Agent response failed schema validation, saving anyway"
          mv "$tmp_clean" "$outfile"
        fi
      else
        # Save raw result and warn
        echo "$agent_result" > "$outfile"
        log warn "Agent output is not valid JSON, saved raw result"
        log debug "Raw result: $(echo "$agent_result" | head -c 200)"
      fi
    else
      log error "No result field in agent output"
      cp "$tmp_output" "$outfile" 2>/dev/null || echo '{}' > "$outfile"
    fi
  else
    log error "Invalid JSON response from agent"
    if [[ -f "$tmp_output" ]]; then
      log debug "Raw agent output: $(head -c 500 "$tmp_output" 2>/dev/null || echo 'empty')"
      # Try to find any JSON-like content
      local potential_json
      potential_json="$(grep -oE '\{[^}]*\}' "$tmp_output" 2>/dev/null | head -1 || echo "")"
      if [[ -n "$potential_json" ]]; then
        log debug "Found potential JSON: $(echo "$potential_json" | head -c 200)"
      fi
    fi
    cp "$tmp_output" "$outfile" 2>/dev/null || echo '{}' > "$outfile"
  fi
  
  # Temp files are cleaned up automatically by trap
  
  # Log excerpt for debugging
  if [[ -f "$outfile" ]]; then
    local excerpt
    excerpt="$(head -c 300 "$outfile" 2>/dev/null || echo "")"
    log debug "Agent output excerpt: $(echo "$excerpt" | jq -Rs . 2>/dev/null || echo '""')"
  fi
  
  return $exit_code
}

# Streaming variant with progress tracking
run_cursor_agent_stream() {
  local mode="$1"; shift
  local prompt="$1"; shift
  local outfile="$1"; shift

  if [[ -z "${CURSOR_API_KEY:-}" ]]; then
    log error "CURSOR_API_KEY not set - cursor-agent requires a valid API key"
    log info "To use cursor-agent, set CURSOR_API_KEY environment variable"
    log info "Get your API key from: https://cursor.com/settings/api"
    return 1
  fi

  local full_prompt
  case "$mode" in
    planning)
      full_prompt="🎯 PLANNING PHASE - CI Repair Planner

$prompt

OUTPUT REQUIREMENTS:
- Your response must be ONLY valid JSON (no markdown, no code fences)
- Start with { and end with }
- Use this exact structure:

{
  \"batches\": [{\"name\": \"batch-1\", \"actions\": [\"rerun:ID\"]}],
  \"patches\": [{\"filename\": \"path.yml\", \"diff\": \"unified diff\"}],
  \"stop_condition\": \"all_green\",
  \"notes\": \"rationale\"
}"
      ;;
    execution)
      full_prompt="⚙️ EXECUTION PHASE - Plan Validation

$prompt

OUTPUT REQUIREMENTS:
- Your response must be ONLY valid JSON (no markdown, no code fences)
- Start with { and end with }
- Use this exact structure:

{\"valid\": true, \"issues\": [], \"corrected_patches\": []}"
      ;;
  esac

  log info "Starting cursor-agent with streaming (mode=$mode, timeout=${AGENT_TIMEOUT_SEC}s)"
  
  local accumulated_result=""
  local tmp_stream tmp_final
  tmp_stream="$(mktemp)"
  tmp_final="$(mktemp)"
  
  # Use stream-json for progress tracking
  local exit_code=0
  timeout "${AGENT_TIMEOUT_SEC}s" cursor-agent -p --force \
    --output-format stream-json \
    "$full_prompt" 2>&1 | tee "$tmp_stream" | while IFS= read -r line; do
      
      # Parse streaming JSON for progress
      local type subtype
      type=$(echo "$line" | jq -r '.type // empty' 2>/dev/null || echo "")
      
      case "$type" in
        system)
          subtype=$(echo "$line" | jq -r '.subtype // empty' 2>/dev/null || echo "")
          if [[ "$subtype" == "init" ]]; then
            local model
            model=$(echo "$line" | jq -r '.model // "unknown"' 2>/dev/null || echo "unknown")
            log info "🤖 Using model: $model"
          fi
          ;;
        assistant)
          # Accumulate assistant responses
          local content
          content=$(echo "$line" | jq -r '.message.content[0].text // empty' 2>/dev/null || echo "")
          if [[ -n "$content" ]]; then
            accumulated_result="${accumulated_result}${content}"
            # Show abbreviated progress
            local preview="${content:0:80}"
            [[ ${#content} -gt 80 ]] && preview="${preview}..."
            log debug "Agent: $preview"
          fi
          ;;
        tool_call)
          subtype=$(echo "$line" | jq -r '.subtype // empty' 2>/dev/null || echo "")
          if [[ "$subtype" == "started" ]]; then
            # Determine tool type
            if echo "$line" | jq -e '.tool_call.readToolCall' >/dev/null 2>&1; then
              local path
              path=$(echo "$line" | jq -r '.tool_call.readToolCall.args.path // "unknown"' 2>/dev/null || echo "unknown")
              log info "📖 Reading: $path"
            elif echo "$line" | jq -e '.tool_call.writeToolCall' >/dev/null 2>&1; then
              local path
              path=$(echo "$line" | jq -r '.tool_call.writeToolCall.args.path // "unknown"' 2>/dev/null || echo "unknown")
              log info "✏️  Writing: $path"
            fi
          elif [[ "$subtype" == "completed" ]]; then
            if echo "$line" | jq -e '.tool_call.writeToolCall.result.success' >/dev/null 2>&1; then
              local lines
              lines=$(echo "$line" | jq -r '.tool_call.writeToolCall.result.success.linesCreated // 0' 2>/dev/null || echo "0")
              log info "   ✅ Wrote $lines lines"
            elif echo "$line" | jq -e '.tool_call.readToolCall.result.success' >/dev/null 2>&1; then
              local lines
              lines=$(echo "$line" | jq -r '.tool_call.readToolCall.result.success.totalLines // 0' 2>/dev/null || echo "0")
              log info "   ✅ Read $lines lines"
            fi
          fi
          ;;
        result)
          # Final result - extract the complete text
          local final_result duration
          final_result=$(echo "$line" | jq -r '.result // empty' 2>/dev/null || echo "")
          duration=$(echo "$line" | jq -r '.duration_ms // 0' 2>/dev/null || echo "0")
          if [[ -n "$final_result" ]]; then
            accumulated_result="$final_result"
          fi
          log info "✅ Agent completed in ${duration}ms"
          ;;
      esac
  done || exit_code=$?

  # Extract JSON from the accumulated result
  if [[ -n "$accumulated_result" ]]; then
    if extract_json "$accumulated_result" > "$tmp_final" 2>/dev/null; then
      mv "$tmp_final" "$outfile"
      log info "Successfully extracted JSON from streamed response"
    else
      echo "$accumulated_result" > "$outfile"
      log warn "Could not extract valid JSON from streamed response"
    fi
  else
    # Fallback: extract from stream file's result event
    if [[ -f "$tmp_stream" ]]; then
      local fallback_result
      fallback_result=$(jq -r 'select(.type=="result") | .result' "$tmp_stream" 2>/dev/null | tail -1 || echo "")
      if [[ -n "$fallback_result" ]]; then
        if extract_json "$fallback_result" > "$tmp_final" 2>/dev/null; then
          mv "$tmp_final" "$outfile"
        else
          echo "$fallback_result" > "$outfile"
        fi
      else
        echo '{}' > "$outfile"
        log error "No result found in stream"
      fi
    fi
  fi
  
  rm -f "$tmp_stream" "$tmp_final"
  return $exit_code
}

# Zjištění stavu PR a runů
get_runs_json() {
  gh run list --limit 30 --json databaseId,displayTitle,workflowName,status,conclusion,headBranch,createdAt,updatedAt 2>/dev/null || echo "[]"
}

get_pr_status_json() {
  gh pr view "$PR_NUMBER" --json statusCheckRollup,headRefName,baseRefName,author,mergeable,mergeStateStatus 2>/dev/null || echo "{}"
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
    log info "Run $rid status=$status conclusion=$concl"
    case "$status:$concl" in
      completed:failure|completed:cancelled)
        log warn "Rerunning failed/cancelled run $rid"
        gh run rerun "$rid" || true
        ;;
      completed:action_required)
        log info "Approving action required for $rid"
        gh run watch "$rid" --approve || true
        ;;
      queued:|in_progress:)
        log info "Run $rid still queued/in_progress"
        ;;
      *)
        :
        ;;
    esac
  done
}

# Generování promptu pro plánování
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

# Prompt pro validaci (syntaxe, rizika)
make_execution_prompt() {
  local plan_json="$1"
  
  cat <<EOF
You are validating a CI repair plan before execution.

PLAN TO VALIDATE:
${plan_json}

VALIDATION TASKS:
1. Verify YAML diff syntax is valid (proper unified diff format)
2. Check patches are minimal and low-risk
3. Flag any risk of re-enabling legacy incompatible workflows
4. Ensure workflow triggers include '${PR_BRANCH}' branch
5. Verify concurrency groups won't cause mutual cancellation
6. Check for queue explosion risks (too broad triggers)

CORRECTION RULES:
- Fix syntax errors in patches
- Add missing branch: ${PR_BRANCH} to triggers if needed
- Add concurrency groups if missing
- Remove risky changes

IMPORTANT: Your response must be ONLY valid JSON. No markdown. No code blocks.

Start your response with { and end with }

Required structure:
{
  "valid": true,
  "issues": ["List any issues found, empty array if none"],
  "corrected_patches": [
    {
      "filename": ".github/workflows/example.yml",
      "diff": "corrected unified diff if needed"
    }
  ],
  "recommendations": ["Any additional recommendations"]
}

If the plan is valid and needs no corrections, return:
{
  "valid": true,
  "issues": [],
  "corrected_patches": [],
  "recommendations": []
}
EOF
}

apply_patch() {
  local fname="$1"
  local diff_content="$2"
  
  log info "Applying patch to $fname"
  
  # Check if file exists
  if [[ ! -f "$fname" ]]; then
    log warn "File $fname does not exist, skipping patch"
    return 1
  fi
  
  # Check git repository status
  if ! git rev-parse --git-dir >/dev/null 2>&1; then
    log error "Not in a git repository, cannot apply patch"
    return 1
  fi
  
  # Check if working directory is clean (allow staged changes)
  if ! git diff --quiet; then
    log warn "Working directory has unstaged changes, patch may conflict"
  fi
  
  # Write diff to secure temp file
  local tmp
  tmp="$(create_temp_file)"
  printf '%s\n' "$diff_content" >"$tmp"
  
  # Try to apply patch
  if git apply --check "$tmp" 2>/dev/null; then
    if git apply --index "$tmp"; then
      log info "Successfully applied patch to $fname"
      return 0
    else
      log error "Failed to apply patch to $fname (check failed but apply failed)"
      return 1
    fi
  else
    log error "git apply --check failed for $fname"
    log debug "Patch content: $(cat "$tmp" | head -20)"
    return 1
  fi
}

commit_and_push() {
  local msg="$1"
  
  # Check if there are changes
  if git diff --cached --quiet && git diff --quiet; then
    log info "No changes to commit"
    return 0
  fi
  
  # Stage any unstaged changes
  git add -u 2>/dev/null || true
  
  # Show what will be committed
  log debug "Changes to commit: $(git diff --cached --stat)"
  
  if [[ "$DRY_RUN" == "true" ]]; then
    log info "DRY RUN: Would commit with message: $msg"
    log info "DRY RUN: Would push to $PR_BRANCH"
    return 0
  fi
  
  # Commit
  if ! git diff --cached --quiet; then
    if git commit -m "$msg"; then
      log info "Committed: $msg"
    else
      log warn "Commit failed"
      return 1
    fi
  fi
  
  # Push
  if git push origin "$PR_BRANCH" 2>&1; then
    log info "Pushed to $PR_BRANCH"
    return 0
  else
    log error "Push failed"
    return 1
  fi
}

# Apply patches from plan
apply_patches_from_plan() {
  local plan_file="$1"
  
  if [[ ! -f "$plan_file" ]]; then
    log warn "Plan file not found: $plan_file"
    return 1
  fi
  
  local patches_len
  patches_len="$(jq -r '.patches | length' "$plan_file" 2>/dev/null || echo 0)"
  
  if [[ "$patches_len" -eq 0 ]]; then
    log info "No patches to apply"
    return 0
  fi
  
  log info "Applying $patches_len patches from plan"
  local applied=0
  
  for i in $(seq 0 $((patches_len-1))); do
    local fname diffc
    fname="$(jq -r ".patches[$i].filename" "$plan_file" 2>/dev/null || echo "")"
    diffc="$(jq -r ".patches[$i].diff" "$plan_file" 2>/dev/null || echo "")"
    
    if [[ -z "$fname" ]] || [[ -z "$diffc" ]] || [[ "$diffc" == "null" ]]; then
      log warn "Skipping invalid patch at index $i"
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
    tmp="$(mktemp)"
    jq '.patches = []' "$plan_file" > "$tmp" && mv "$tmp" "$plan_file"
  fi
  
  return 0
}

# Execute batch actions from plan
execute_batch_actions() {
  local plan_file="$1"
  
  if [[ ! -f "$plan_file" ]]; then
    log warn "Plan file not found: $plan_file"
    return 1
  fi
  
  local batches_len
  batches_len="$(jq -r '.batches | length' "$plan_file" 2>/dev/null || echo 0)"
  
  if [[ "$batches_len" -eq 0 ]]; then
    log info "No batch actions to execute"
    return 0
  fi
  
  # Get first batch
  local batch_name actions_len
  batch_name="$(jq -r '.batches[0].name' "$plan_file" 2>/dev/null || echo "unnamed")"
  actions_len="$(jq -r '.batches[0].actions | length' "$plan_file" 2>/dev/null || echo 0)"
  
  if [[ "$actions_len" -eq 0 ]]; then
    log info "Batch '$batch_name' has no actions, removing"
    local tmp
    tmp="$(mktemp)"
    jq '.batches |= .[1:]' "$plan_file" > "$tmp" && mv "$tmp" "$plan_file"
    return 0
  fi
  
  log info "Executing batch '$batch_name' with $actions_len actions"
  
  for idx in $(seq 0 $((actions_len-1))); do
    local action
    action="$(jq -r ".batches[0].actions[$idx]" "$plan_file" 2>/dev/null || echo "")"
    
    [[ -z "$action" ]] && continue
    
    case "$action" in
      rerun:*)
        local rid="${action#rerun:}"
        if [[ "$DRY_RUN" == "true" ]]; then
          log info "DRY RUN: Would rerun workflow run: $rid"
        else
          log info "Rerunning workflow run: $rid"
          gh run rerun "$rid" 2>&1 || log warn "Failed to rerun $rid"
        fi
        ;;
      approve:*)
        local rid="${action#approve:}"
        if [[ "$DRY_RUN" == "true" ]]; then
          log info "DRY RUN: Would approve workflow run: $rid"
        else
          log info "Approving workflow run: $rid"
          gh run watch "$rid" --approve 2>&1 || log warn "Failed to approve $rid"
        fi
        ;;
      apply-patch:*)
        local patchname="${action#apply-patch:}"
        log info "Looking for patch: $patchname in plan"
        # Find this patch in the patches array and apply it
        local patch_idx
        patch_idx=$(jq -r ".patches | map(.filename | contains(\"$patchname\")) | index(true)" "$plan_file" 2>/dev/null || echo "null")
        if [[ "$patch_idx" != "null" ]]; then
          local fname diffc
          fname="$(jq -r ".patches[$patch_idx].filename" "$plan_file")"
          diffc="$(jq -r ".patches[$patch_idx].diff" "$plan_file")"
          if [[ "$DRY_RUN" == "true" ]]; then
            log info "DRY RUN: Would apply patch to $fname"
          else
            apply_patch "$fname" "$diffc" || true
          fi
        else
          log warn "Patch $patchname not found in patches array"
        fi
        ;;
      enable-workflow:*)
        local wpath="${action#enable-workflow:}"
        local wname="$(basename "$wpath")"
        if [[ "$DRY_RUN" == "true" ]]; then
          log info "DRY RUN: Would enable workflow: $wname"
        else
          log info "Enabling workflow: $wname"
          if [[ -f ".github/workflows-disabled/$wname" ]]; then
            git mv ".github/workflows-disabled/$wname" ".github/workflows/$wname" 2>/dev/null || true
            git add ".github/workflows/$wname" 2>/dev/null || true
          else
            log warn "Workflow $wname not found in workflows-disabled/"
          fi
        fi
        ;;
      disable-workflow:*)
        local wpath="${action#disable-workflow:}"
        local wname="$(basename "$wpath")"
        if [[ "$DRY_RUN" == "true" ]]; then
          log info "DRY RUN: Would disable workflow: $wname"
        else
          log info "Disabling workflow: $wname"
          if [[ -f ".github/workflows/$wname" ]]; then
            git mv ".github/workflows/$wname" ".github/workflows-disabled/$wname" 2>/dev/null || true
            git add ".github/workflows-disabled/$wname" 2>/dev/null || true
          else
            log warn "Workflow $wname not found in workflows/"
          fi
        fi
        ;;
      rerun-failed-workflows)
        if [[ "$DRY_RUN" == "true" ]]; then
          log info "DRY RUN: Would rerun all failed workflows"
        else
          log info "Rerunning all failed workflows"
          # Get current failed runs and rerun them
          local current_runs
          current_runs="$(get_runs_json)"
          approve_or_rerun "$current_runs"
        fi
        ;;
      *)
        log warn "Unknown action: $action"
        ;;
      esac
    done
  
  # Commit any changes from batch actions
  if ! git diff --cached --quiet || ! git diff --quiet; then
    commit_and_push "ci: execute batch '$batch_name' actions"
  fi
  
  # Remove executed batch
  local tmp
  tmp="$(mktemp)"
  jq '.batches |= .[1:]' "$plan_file" > "$tmp" && mv "$tmp" "$plan_file"
  
  return 0
}

# Generate fallback plan
generate_fallback_plan() {
  local outfile="${1:-}"
  log warn "Generating minimal fallback plan"
  
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
  local plan_file="$(mktemp)"
  
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
  local plan_file="$(mktemp)"
  echo "$plan" > "$plan_file"
  
  # Execute batch actions from plan
  execute_batch_actions "$plan_file"
  
  # Clean up
  rm -f "$plan_file"
}

# Main orchestration
main() {
  require_cmd gh jq git curl timeout
  
  # Load Cursor CLI configuration early
  load_cursor_config
  
  log info "=== Agent Loop Start ==="
  log info "Repository: $REPO"
  log info "PR: #${PR_NUMBER} ($PR_BRANCH)"
  log info "Mode: $MODE"
  log info "Max iterations: $MAX_ITERATIONS"
  log info "Run once: $RUN_ONCE"
  log info "Streaming: $USE_STREAMING"
  log info "Dry run: $DRY_RUN"
  log info "Interval: ${INTERVAL}s"
  log info "Cursor Config: $CURSOR_CONFIG_FILE (MCP: $MCP_ENABLED)"
  
  if [[ "$DRY_RUN" == "true" ]]; then
    log info "DRY RUN MODE: No actual changes will be made"
  fi
  
  # Test cursor-agent configuration
  log info "Testing cursor-agent configuration..."
  
  # Validate all inputs first
  if ! validate_all_inputs; then
    log error "Input validation failed"
    exit 1
  fi
  
  # Test cursor-agent configuration with actual API validation
  local test_result=2  # Default to API key not set
  if ! command -v cursor-agent >/dev/null 2>&1; then
    test_result=1  # Command not found
  elif [[ -n "${CURSOR_API_KEY:-}" ]]; then
    if [[ "$CURSOR_API_KEY" =~ ^key_ ]]; then
      # Test actual API key validity
      if test_cursor_api_key; then
        test_result=0  # API key is valid and working
      else
        test_result=3  # API key format looks correct but doesn't work
      fi
    else
      test_result=4  # API key format invalid
    fi
  fi
  
  log debug "test_cursor_agent returned: $test_result"
  
  case $test_result in
    0)
      log info "cursor-agent configured correctly - AI-powered planning enabled"
      ;;
    1)
      log warn "cursor-agent not found, running in simple mode (rerun/approve only)"
      log info "Install cursor-agent: curl https://cursor.com/install -fsS | bash"
      ;;
    2)
      log warn "cursor-agent found but CURSOR_API_KEY not set, running in simple mode"
      log info "To enable AI-powered planning, set CURSOR_API_KEY environment variable"
      log info "Get your API key from: https://cursor.com/settings/api"
      ;;
    3)
      log warn "cursor-agent authentication failed, running in simple mode"
      log error "API key format looks correct but authentication failed"
      log info "Check if your API key is valid and not expired"
      log info "Get a new API key from: https://cursor.com/settings/api"
      ;;
    4)
      log warn "cursor-agent API key format invalid, running in simple mode"
      log error "API key should start with 'key_' prefix"
      log info "Get a valid API key from: https://cursor.com/settings/api"
      ;;
    *)
      log warn "cursor-agent test failed with unknown issue, running in simple mode"
      log info "Check cursor-agent installation and configuration"
      ;;
  esac
  
  log debug "Case statement completed, continuing with branch check"
  
  # Ensure we're on the correct branch
  local current_branch
  current_branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")"
  if [[ "$current_branch" != "$PR_BRANCH" ]]; then
    log warn "Not on target branch ($PR_BRANCH), currently on ($current_branch)"
    log info "Attempting to checkout $PR_BRANCH..."
    
    # Try to fetch and checkout
    if git fetch origin "pull/${PR_NUMBER}/head:${PR_BRANCH}" 2>&1; then
      git checkout "$PR_BRANCH" 2>&1 || log error "Checkout failed"
    else
      log warn "Could not fetch PR, trying direct checkout"
      git checkout "$PR_BRANCH" 2>&1 || log error "Checkout failed"
    fi
    
    # Pull latest
    git pull origin "$PR_BRANCH" 2>&1 || log warn "Pull failed"
  fi
  
  # Verify we're on correct branch now
  current_branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")"
  if [[ "$current_branch" != "$PR_BRANCH" ]]; then
    log error "Still not on $PR_BRANCH after checkout attempt, aborting"
    exit 1
  fi
  
  log info "Working on branch: $current_branch"
  
  # File paths for agent outputs
  local plan_file=".agent_plan.json"
  local execution_file=".agent_execution.json"
  
  # Initial status check
  local runs_json pr_json not_green not_green_len
  
  # Main loop
  local iteration=0
  while [[ $iteration -lt $MAX_ITERATIONS ]]; do
    iteration=$((iteration + 1))
    log info "=== Iteration $iteration/$MAX_ITERATIONS ==="
    
    # Collect current state
    runs_json="$(collect_workflow_runs)"
    pr_json="$(collect_pr_info)"
    
    # Check if all workflows are green
    not_green="$(check_workflow_status "$runs_json")"
    not_green_len="$(echo "$not_green" | jq length)"
    
    if [[ "$not_green_len" == "0" ]]; then
      log success "All workflows are green! 🎉"
    break
  fi

    log info "Found $not_green_len workflows needing attention"
    
    # Generate plan
    local plan
    if [[ $test_result -eq 0 ]]; then
      plan="$(generate_plan "$runs_json" "$pr_json" "$not_green")"
      
      if [[ -z "$plan" ]]; then
        log warn "No actionable plan generated, trying simple rerun..."
        # Simple fallback: rerun failed workflows
        approve_or_rerun "$not_green"
      else
        # Execute plan
        execute_plan "$plan"
      fi
    else
      log info "Running in simple mode - rerunning failed workflows"
      # Simple mode: just rerun failed workflows
      approve_or_rerun "$not_green"
    fi
    
    # Wait before next iteration
    log info "Waiting ${INTERVAL}s before next iteration..."
    sleep "$INTERVAL"
  done
  
  if [[ $iteration -eq $MAX_ITERATIONS ]]; then
    log warn "Reached maximum iterations ($MAX_ITERATIONS)"
  fi
  
  log info "=== Agent Loop Complete ==="
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  main "$@"
fi
