#!/usr/bin/env bash
set -euo pipefail

BRANCH="${BRANCH:-cursor/fix-ci}"
INTERVAL="${INTERVAL:-60}"

# Helper: safe JSON escape (pro vložení JSONu z gh do textového promptu)
json_escape() {
  python3 - <<'PY'
import sys, json
print(json.dumps(sys.stdin.read())[1:-1])
PY
}

while true; do
  # 1) Nasbírej aktuální stav
  RUNS_JSON="$(gh run list --limit 10 --json databaseId,displayTitle,workflowName,status,conclusion,headBranch,updatedAt || true)"
  PRS_JSON="$(gh pr list --limit 10 --json number,title,headRefName,baseRefName,author,mergeable,mergeStateStatus || true)"
  LAST_COMMITS="$(git log --oneline -n 10 || true)"

  # 2) Zjisti, zda jsou všechny workflow zelené
  NOT_GREEN_COUNT="$(jq -r '[ .[] | select(.status!="completed" or .conclusion!="success") ] | length' <<< "${RUNS_JSON:-[]}")"
  ALL_GREEN="false"
  [[ "${NOT_GREEN_COUNT}" == "0" ]] && ALL_GREEN="true"

  # 3) Volitelně proveď akce (rerun, approve) – příklad:
  if [[ "${ALL_GREEN}" != "true" ]]; then
    mapfile -t NEEDS_ATTENTION < <(jq -r '.[] | select(.status!="completed" or .conclusion!="success") | .databaseId' <<< "${RUNS_JSON:-[]}")
    for RID in "${NEEDS_ATTENTION[@]}"; do
      STATUS="$(gh run view "$RID" --json status,conclusion --jq '.status')"
      CONCL="$(gh run view "$RID" --json status,conclusion --jq '.conclusion')"
      case "$STATUS:$CONCL" in
        "completed:failure"|"completed:cancelled")
          gh run rerun "$RID" || true
          ;;
        "completed:action_required")
          gh run watch "$RID" --approve || true
          ;;
        *) : ;;
      esac
    done
  fi

  # 4) Vytvoř PROMPT z template + dynamických částí
  # Připrav escapované JSON bloky pro bezpečné vložení
  RUNS_JSON_ESCAPED="$(printf "%s" "${RUNS_JSON:-[]}" | json_escape || true)"
  PRS_JSON_ESCAPED="$(printf "%s" "${PRS_JSON:-[]}" | json_escape || true)"
  LAST_COMMITS_ESCAPED="$(printf "%s" "${LAST_COMMITS:-}" | json_escape || true)"

  read -r -d '' PROMPT <<EOF || true
You are a CI/CD repair and orchestration agent for OpenSSL modernization.
Goal: Ensure all workflows are enabled and passing. Iterate with minimal, safe changes.

Context:
- Repository branch: ${BRANCH}
- All workflows green: ${ALL_GREEN}

Latest workflow runs (JSON):
${RUNS_JSON}

Open PRs (JSON):
${PRS_JSON}

Recent commits:
${LAST_COMMITS}

Tasks:
1) If any workflow requires approval, approve it safely.
2) If any workflow failed due to flakiness/transient error, rerun it.
3) If triggers are misconfigured, propose a minimal diff (YAML) to fix.
4) If repository settings block execution, suggest explicit owner actions.
5) Never introduce risky changes; prefer minimal, reversible edits.
6) When suggesting file edits, output unified diff patches ready to apply.

Output format:
- Action plan (bullet list)
- If edits needed: provide unified diffs
- Next gh commands to run
- Stop condition criteria

EOF

  # 5) Spusť Cursor Agent s dynamicky složeným PROMPTEM
  export PROMPT
  cursor-agent --once -f agent "$PROMPT" || true

  # 6) Ukonči smyčku, pokud je vše zelené, jinak čekej a opakuj
  if [[ "${ALL_GREEN}" == "true" ]]; then
    echo "✅ All workflows are green. Exiting."
    break
  fi

  echo "⏳ Waiting ${INTERVAL}s before next iteration…"
  sleep "${INTERVAL}"
done
