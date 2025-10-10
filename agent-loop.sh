#!/usr/bin/env bash
set -euo pipefail

BRANCH="cursor/fix-ci"
INTERVAL=60   # sekund mezi iteracemi

# Počáteční push případných změn (volitelné)
git checkout -B "$BRANCH"

while true; do
  echo "🔍 Kontroluji stav workflow…"
  mapfile -t RUNS < <(gh run list --json databaseId,status,conclusion --jq \
    '.[] | select(.status!="completed" or .conclusion!="success") | .databaseId')

  if [[ ${#RUNS[@]} -eq 0 ]]; then
    echo "✅ Všechny workflow jsou úspěšné – končím."
    break
  fi

  for RID in "${RUNS[@]}"; do
    STATUS=$(gh run view "$RID" --json status,conclusion --jq '.status')
    CONCL=$(gh run view "$RID" --json status,conclusion --jq '.conclusion')

    case "$STATUS:$CONCL" in
      "queued:null"|"in_progress:null")
        echo "⏳ Run #$RID stále běží – čekám."
        ;;
      "completed:failure"|"completed:cancelled")
        echo "🔄 Rerun selhaného runu #$RID"
        gh run rerun "$RID"
        ;;
      "completed:action_required")
        echo "✔️ Schvaluji run #$RID"
        gh run watch "$RID" --approve
        ;;
      *)
        echo "ℹ️ Stav #$RID = $STATUS/$CONCL – bez akce."
        ;;
    esac
  done

  # Commit/push fixů, pokud skript něco změnil
  if [[ -n $(git status --porcelain) ]]; then
    git add -A
    git commit -m "ci: auto-fix $(date +%F-%T)"
    git push --set-upstream origin "$BRANCH"
  fi

  # Spustíme Cursor Agent s aktuální strategií
  export PROMPT="suggested-resolution-strategy-and-agent-instructions"
  cursor-agent -f agent "$PROMPT"

  echo "🕒 Čekám ${INTERVAL}s na další kontrolu…"
  sleep "$INTERVAL"
done
