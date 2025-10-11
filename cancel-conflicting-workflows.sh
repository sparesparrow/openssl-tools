#!/bin/bash

# Script to cancel conflicting workflows and keep only essential ones
# This will help reduce the queue backlog

echo "🔧 Cancelling conflicting workflows..."

# Get all queued runs for simplify-openssl-build branch
QUEUED_RUNS=$(gh run list --status queued --branch simplify-openssl-build --json databaseId,workflowName --jq '.[] | select(.workflowName | test("CI Success|Always Pass|Immediate Success|Simple Success Override|Simple Check")) | .databaseId')

if [ -n "$QUEUED_RUNS" ]; then
    echo "Found queued runs to cancel:"
    echo "$QUEUED_RUNS"
    
    for run_id in $QUEUED_RUNS; do
        echo "Cancelling run $run_id..."
        gh run cancel "$run_id" || echo "Failed to cancel run $run_id"
    done
else
    echo "No conflicting queued runs found"
fi

echo "✅ Workflow cancellation complete"