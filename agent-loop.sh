#!/usr/bin/env bash
# agent-loop.sh – Robustní CI orchestrace s plánováním a validací (Cursor-Agent)
# Použití:
#   ./agent-loop.sh "Popis úkolu" execution
#   ./agent-loop.sh "Diagnostika a plán" planning
# Konfigurace přes env:
#   PR_NUMBER (default 6), PR_BRANCH (default simplify-openssl-build)
#   REPO (default sparesparrow/openssl-tools)
#   MAX_ITERATIONS (default 12), INTERVAL (default 60)
#   AGENT_TIMEOUT_SEC (default 600), AGENT_DETACH (true/false, default false)
#   LOG_LEVEL (debug|info|warn|error, default info)

set -euo pipefail

# Defaults
REPO="${REPO:-sparesparrow/openssl-tools}"
PR_NUMBER="${PR_NUMBER:-6}"
PR_BRANCH="${PR_BRANCH:-simplify-openssl-build}"
MAX_ITERATIONS="${MAX_ITERATIONS:-12}"
INTERVAL="${INTERVAL:-60}"
LOG_LEVEL="${LOG_LEVEL:-info}"
AGENT_TIMEOUT_SEC="${AGENT_TIMEOUT_SEC:-600}"
AGENT_DETACH="${AGENT_DETACH:-false}"
TASK="${1:-"Ensure all PR #$PR_NUMBER workflows are green with minimal safe changes"}"
MODE="${2:-execution}"

# Utilities
timestamp() { date '+%Y-%m-%dT%H:%M:%S%z'; }

log() {
  local level="$1"; shift
  local msg="$*"
  local levels="debug info warn error"
  # filter by level
  case "$LOG_LEVEL:$level" in
    debug:debug|debug:info|debug:warn|debug:error|info:info|info:warn|info:error|warn:warn|warn:error|error:error)
      echo "{"ts":"$(timestamp)","level":"$level","msg":$(printf '%s' "$msg" | jq -Rs .)}" >&2
      ;;
  esac
}

require_cmd() {
  for c in "$@"; do
    command -v "$c" >/dev/null 2>&1 || { echo "Missing command: $c" >&2; exit 127; }
  done
}

json_escape() { jq -Rs .; } # robustní JSON escape

retry() {
  local tries=$1; shift
  local delay=$1; shift
  local cmd=("$@")
  local attempt=1
  while (( attempt <= tries )); do
    if "${cmd[@]}"; then return 0; fi
    log warn "Command failed (attempt $attempt/$tries): ${cmd[*]}"
    sleep $((delay * attempt))
    attempt=$((attempt + 1))
  done
  return 1
}

# Cursor Agent invokace s timeoutem a volitelným detach
run_cursor_agent() {
  local mode="$1"; shift
  local prompt="$1"; shift
  local outfile="$1"; shift

  [[ -z "${CURSOR_API_KEY:-}" ]] && { log error "CURSOR_API_KEY not set"; return 1; }

  if [[ "$AGENT_DETACH" == "true" ]]; then
    log info "Starting cursor-agent in detach mode (mode=$mode, timeout=${AGENT_TIMEOUT_SEC}s)"
    cursor-agent --detach --pid-file .cursor.pid -f agent --timeout "$AGENT_TIMEOUT_SEC" --mode "$mode" "$prompt" >"$outfile" 2>&1 || true
    sleep 5
    if [[ -f .cursor.pid ]]; then
      log info "Stopping detached agent PID=$(cat .cursor.pid)"
      kill "$(cat .cursor.pid)" || true
      rm -f .cursor.pid
    fi
  else
    log info "Running cursor-agent once (mode=$mode, timeout=${AGENT_TIMEOUT_SEC}s)"
    timeout "${AGENT_TIMEOUT_SEC}s" cursor-agent --once -f agent --mode "$mode" "$prompt" >"$outfile" 2>&1 || true
  fi
  # Log tail for debugging
  log debug "Agent output tail: $(tail -n 30 "$outfile" | jq -Rs .)"
  return 0
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
  cat <<EOF
You are a CI repair planner for OpenSSL modernization PR #${PR_NUMBER}.
Goal: All workflows passing with minimal, safe, reversible changes.

Context:
- Repo: ${REPO}
- Branch: ${PR_BRANCH}
- PR status (JSON): $(printf '%s' "$pr_json" | jq -c .)
- Latest runs (JSON): $(printf '%s' "$runs_json" | jq -c .)
- Recent commits:
$(printf '%s' "$recent_commits")

Constraints:
- Prefer rerun/approve over edits.
- If edits needed, provide unified diff patches (small, focused).
- Avoid enabling legacy upstream workflows incompatible with Conan 2.0/MCP.
- Avoid queue explosions: propose selective triggers and concurrency.

Output format (strict JSON):
{
  "batches": [
    {"name": "batch-1", "actions": ["rerun:ID", "approve:ID", "apply-patch:patch.diff", "enable-workflow:path.yml"] }
  ],
  "patches": [{"filename":"path/to.yml","diff":"--- a/...\
+++ b/...\
..."}],
  "stop_condition": "all_green | or | only_selected_workflows_green",
  "notes": "short rationale"
}
EOF
}

# Prompt pro validaci (syntaxe, rizika)
make_validation_prompt() {
  local plan_json="$1"
  cat <<EOF
Validate the following plan for CI repairs:
Plan (JSON):
$(printf '%s' "$plan_json" | jq -c .)

Tasks:
- Verify YAML diffs syntax and minimal-risk nature.
- Flag any risk of re-enabling legacy incompatible workflows.
- Ensure triggers include '${PR_BRANCH}' and avoid queue explosion.
- Ensure concurrency groups do not cause mutual cancellation.
- Suggest corrections if needed.

Output (JSON):
{"valid": true/false, "issues": ["..."], "corrected_patches": [ { "filename": "...", "diff": "..." } ]}
EOF
}

apply_patch() {
  local fname="$1"; shift
  local diff_content="$1"; shift
  log info "Applying patch to $fname"
  # Write to temp and apply
  local tmp
  tmp="$(mktemp)"
  printf '%s
' "$diff_content" >"$tmp"
  git apply --index "$tmp" || { log error "git apply failed for $fname"; rm -f "$tmp"; return 1; }
  rm -f "$tmp"
  return 0
}

commit_and_push() {
  local msg="$1"
  git status --porcelain
  if ! git diff --cached --quiet; then
    git commit -m "$msg" || true
  fi
  git push origin "$PR_BRANCH" || true
}

# Hlavní
main() {
  require_cmd gh jq git

  log info "Agent Loop Start: repo=$REPO pr=#${PR_NUMBER} branch=$PR_BRANCH mode=$MODE"
  # Ujisti se, že jsme na správné větvi
  current_branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")"
  if [[ "$current_branch" != "$PR_BRANCH" ]]; then
    log warn "Not on target branch ($PR_BRANCH). Attempting checkout..."
    git fetch origin "pull/${PR_NUMBER}/head:${PR_BRANCH}" || true
    git checkout "$PR_BRANCH" || true
    git pull origin "$PR_BRANCH" || true
  fi

  # Fáze plánování + validace (jen jednou na začátku)
  local plan_file=".agent_plan.json"
  local validation_file=".agent_validation.json"

  local runs_json pr_json not_green
  runs_json="$(get_runs_json)"
  pr_json="$(get_pr_status_json)"
  not_green="$(get_open_runs_not_green "$runs_json")"

  if [[ "$MODE" == "planning" || "$MODE" == "execution" ]]; then
    # Planning
    log info "Generating plan (planning mode)"
    local planning_prompt
    planning_prompt="$(make_planning_prompt "$runs_json" "$pr_json")"
    run_cursor_agent "planning" "$planning_prompt" "$plan_file" || true

    # Pokud agent neposlal validní JSON, fallback na no-op plán
    if ! jq -e . "$plan_file" >/dev/null 2>&1; then
      log warn "Agent plan invalid JSON, generating minimal fallback plan"
      cat >"$plan_file" <<'JSON'
{"batches":[{"name":"fallback","actions":[]}],"patches":[],"stop_condition":"all_green","notes":"fallback plan"}
JSON
    fi

    # Validation
    log info "Validating plan"
    local plan_json
    plan_json="$(cat "$plan_file")"
    local validation_prompt
    validation_prompt="$(make_validation_prompt "$plan_json")"
    run_cursor_agent "validation" "$validation_prompt" "$validation_file" || true

    # Aplikace případných corrected patches (pokud validace vrátila)
    if jq -e '.corrected_patches' "$validation_file" >/dev/null 2>&1; then
      local cnt
      cnt="$(jq -r '.corrected_patches | length' "$validation_file" 2>/dev/null || echo 0)"
      if [[ "$cnt" != "0" ]]; then
        log info "Applying corrected patches from validation"
        for i in $(seq 0 $((cnt-1))); do
          fname="$(jq -r ".corrected_patches[$i].filename" "$validation_file")"
          diffc="$(jq -r ".corrected_patches[$i].diff" "$validation_file")"
          apply_patch "$fname" "$diffc" || true
        done
        commit_and_push "ci: apply corrected patches from validation"
      fi
    fi
  fi

  # Execution loop
  local iteration=1
  while (( iteration <= MAX_ITERATIONS )); do
    log info "Iteration $iteration/$MAX_ITERATIONS"

    # Rychlé odblokovací kroky: rerun/approve
    runs_json="$(get_runs_json)"
    pr_json="$(get_pr_status_json)"
    not_green="$(get_open_runs_not_green "$runs_json")"

    local not_green_len
    not_green_len="$(jq -r 'length' <<<"$not_green")"
    log info "Not green count: $not_green_len"

    if [[ "$not_green_len" -eq 0 ]]; then
      log info "✅ All workflows green. Exiting."
      break
    fi

    # Schval a rerun co lze
    approve_or_rerun "$runs_json"

    # Pokud stále nejsme green, zkus aplikovat patche z plánu (batch-by-batch)
    if [[ -s "$plan_file" ]]; then
      local batches_len
      batches_len="$(jq -r '.batches | length' "$plan_file" 2>/dev/null || echo 0)"
      if [[ "$batches_len" -gt 0 ]]; then
        # vem první batch a proveď akce
        local actions_len
        actions_len="$(jq -r '.batches[0].actions | length' "$plan_file" 2>/dev/null || echo 0)"
        if [[ "$actions_len" -gt 0 ]]; then
          log info "Executing batch actions"
          for idx in $(seq 0 $((actions_len-1))); do
            action="$(jq -r ".batches[0].actions[$idx]" "$plan_file")"
            case "$action" in
              rerun:*)
                rid="${action#rerun:}"
                log info "Rerun by plan: $rid"
                gh run rerun "$rid" || true
                ;;
              approve:*)
                rid="${action#approve:}"
                log info "Approve by plan: $rid"
                gh run watch "$rid" --approve || true
                ;;
              apply-patch:*)
                pfile="${action#apply-patch:}"
                log info "Applying patch file from plan array"
                # optional: find this patch in .patches and apply
                ;;
              enable-workflow:*)
                wpath="${action#enable-workflow:}"
                log info "Enabling workflow: $wpath"
                git mv ".github/workflows-disabled/$(basename "$wpath")" ".github/workflows/$(basename "$wpath")" 2>/dev/null || true
                ;;
              *)
                log warn "Unknown action: $action"
                ;;
            esac
          done
          commit_and_push "ci: execute plan batch actions"
          # remove executed batch (shift)
          tmpf="$(mktemp)"
          jq ' .batches |= .[1:] ' "$plan_file" >"$tmpf" && mv "$tmpf" "$plan_file"
        fi
      fi

      # Aplikace patchů přímo (pokud existují v .patches)
      local patches_len
      patches_len="$(jq -r '.patches | length' "$plan_file" 2>/dev/null || echo 0)"
      if [[ "$patches_len" -gt 0 ]]; then
        for i in $(seq 0 $((patches_len-1))); do
          fname="$(jq -r ".patches[$i].filename" "$plan_file")"
          diffc="$(jq -r ".patches[$i].diff" "$plan_file")"
          apply_patch "$fname" "$diffc" || true
        done
        commit_and_push "ci: apply planned patches"
        # clear patches after apply
        tmpf="$(mktemp)"
        jq ' .patches = [] ' "$plan_file" >"$tmpf" && mv "$tmpf" "$plan_file"
      fi
    fi

    log info "⏳ Sleeping ${INTERVAL}s before next check..."
    sleep "$INTERVAL"
    iteration=$((iteration + 1))
  done

  if (( iteration > MAX_ITERATIONS )); then
    log error "Reached MAX_ITERATIONS=$MAX_ITERATIONS without all green."
    exit 1
  fi

  log info "Done."
}

main "$@"