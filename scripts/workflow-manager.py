#!/usr/bin/env python3
"""
Unified Workflow Manager - Consolidates workflow-health-check.py, workflow_fixer.py,
workflow-recovery.py, github_workflow_fixer.py, monitor-workflows.py
"""

import os
import sys
import json
import argparse
from pathlib import Path
from github import Github
from typing import Dict, List
from datetime import datetime, timedelta

class UnifiedWorkflowManager:
    def __init__(self, repo_owner: str, repo_name: str, token: str = None):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.token = token or os.getenv('GITHUB_TOKEN')
        self.github = Github(self.token) if self.token else None
    
    def health_check(self) -> Dict:
        """Consolidated health check functionality"""
        # Absorb workflow-health-check.py logic
        if not self.github:
            return {"error": "GitHub token not configured"}

        try:
            repo = self.github.get_repo(f"{self.repo_owner}/{self.repo_name}")
            workflows = repo.get_workflows()

            health_report = {
                "total_workflows": 0,
                "active_workflows": 0,
                "failed_runs": 0,
                "success_rate": 0.0,
                "issues": []
            }

            for workflow in workflows:
                health_report["total_workflows"] += 1
                if workflow.state == "active":
                    health_report["active_workflows"] += 1

                # Check recent runs
                runs = workflow.get_runs()
                recent_runs = list(runs[:10])  # Last 10 runs

                failed_count = sum(1 for run in recent_runs if run.conclusion == "failure")
                health_report["failed_runs"] += failed_count

                if failed_count > 5:
                    health_report["issues"].append(f"Workflow '{workflow.name}' has {failed_count} recent failures")

            total_runs = health_report["total_workflows"] * 10  # Approximate
            if total_runs > 0:
                health_report["success_rate"] = ((total_runs - health_report["failed_runs"]) / total_runs) * 100

            return health_report

        except Exception as e:
            return {"error": str(e)}

    def fix_workflows(self) -> bool:
        """Consolidated workflow fixing functionality"""
        # Absorb workflow_fixer.py + github_workflow_fixer.py logic
        if not self.github:
            print("❌ GitHub token not configured")
            return False

        try:
            repo = self.github.get_repo(f"{self.repo_owner}/{self.repo_name}")
            workflows = repo.get_workflows()

            fixes_applied = 0

            for workflow in workflows:
                runs = workflow.get_runs()
                recent_runs = list(runs[:5])  # Last 5 runs

                # Check for common issues and apply fixes
                if any(run.conclusion == "failure" for run in recent_runs):
                    # Apply common fixes
                    fixes_applied += self._apply_workflow_fixes(workflow, recent_runs)

            print(f"✅ Applied {fixes_applied} workflow fixes")
            return fixes_applied > 0

        except Exception as e:
            print(f"❌ Error fixing workflows: {e}")
            return False

    def _apply_workflow_fixes(self, workflow, recent_runs) -> int:
        """Apply fixes to a specific workflow"""
        fixes = 0

        # Common fix: Re-run failed jobs
        for run in recent_runs:
            if run.conclusion == "failure" and run.status != "in_progress":
                try:
                    run.rerun()
                    fixes += 1
                    print(f"🔄 Re-running failed workflow run {run.id}")
                except:
                    pass  # Some runs can't be re-run

        return fixes

    def recover_workflows(self) -> bool:
        """Consolidated recovery functionality"""
        # Absorb workflow-recovery.py logic
        if not self.github:
            print("❌ GitHub token not configured")
            return False

        try:
            repo = self.github.get_repo(f"{self.repo_owner}/{self.repo_name}")
            workflows = repo.get_workflows()

            recovery_actions = 0

            for workflow in workflows:
                # Check for stuck workflows
                runs = workflow.get_runs()
                for run in runs:
                    if run.status == "in_progress":
                        # Check if run has been running too long (e.g., > 6 hours)
                        created_at = run.created_at
                        if (datetime.now(created_at.tzinfo) - created_at).total_seconds() > 6 * 3600:
                            try:
                                run.cancel()
                                recovery_actions += 1
                                print(f"🛑 Cancelled stuck workflow run {run.id}")
                            except:
                                pass

            print(f"✅ Performed {recovery_actions} recovery actions")
            return recovery_actions > 0

        except Exception as e:
            print(f"❌ Error recovering workflows: {e}")
            return False

    def monitor_workflows(self, hours: int = 24) -> Dict:
        """Consolidated monitoring functionality"""
        # Absorb monitor-workflows.py logic
        if not self.github:
            return {"error": "GitHub token not configured"}

        try:
            repo = self.github.get_repo(f"{self.repo_owner}/{self.repo_name}")
            workflows = repo.get_workflows()

            monitoring_report = {
                "period_hours": hours,
                "workflows_monitored": 0,
                "total_runs": 0,
                "successful_runs": 0,
                "failed_runs": 0,
                "alerts": []
            }

            since = datetime.now() - timedelta(hours=hours)

            for workflow in workflows:
                monitoring_report["workflows_monitored"] += 1
                runs = workflow.get_runs()
                recent_runs = [run for run in runs if run.created_at > since]

                for run in recent_runs:
                    monitoring_report["total_runs"] += 1
                    if run.conclusion == "success":
                        monitoring_report["successful_runs"] += 1
                    elif run.conclusion == "failure":
                        monitoring_report["failed_runs"] += 1
                        monitoring_report["alerts"].append(f"Failed run: {run.id} ({workflow.name})")

            return monitoring_report

        except Exception as e:
            return {"error": str(e)}

def main():
    parser = argparse.ArgumentParser(description='Unified Workflow Manager')
    parser.add_argument('--repo', required=True, help='owner/repo')
    parser.add_argument('--action', choices=['health-check', 'fix', 'recover', 'monitor'], required=True)
    # ... rest of consolidated CLI

    args = parser.parse_args()

    # Parse repo argument
    try:
        owner, repo = args.repo.split('/')
    except ValueError:
        print("❌ Invalid repo format. Use: owner/repo")
        sys.exit(1)

    # Check for GitHub token
    if not os.getenv('GITHUB_TOKEN'):
        print("❌ GITHUB_TOKEN environment variable not set")
        print("Please set your GitHub token: export GITHUB_TOKEN=your_token")
        sys.exit(1)

    # Initialize manager
    manager = UnifiedWorkflowManager(owner, repo)

    # Execute action
    if args.action == 'health-check':
        result = manager.health_check()
        if "error" in result:
            print(f"❌ Health check failed: {result['error']}")
        else:
            print("🏥 Health Check Results:")
            print(f"   Total workflows: {result['total_workflows']}")
            print(f"   Active workflows: {result['active_workflows']}")
            print(f"   Recent failures: {result['failed_runs']}")
            print(".1f")
            if result['issues']:
                print("   Issues found:")
                for issue in result['issues']:
                    print(f"     - {issue}")

    elif args.action == 'fix':
        success = manager.fix_workflows()
        if success:
            print("✅ Workflow fixes applied successfully")
        else:
            print("❌ No fixes needed or fixes failed")

    elif args.action == 'recover':
        success = manager.recover_workflows()
        if success:
            print("✅ Workflow recovery completed")
        else:
            print("❌ No recovery actions needed or recovery failed")

    elif args.action == 'monitor':
        result = manager.monitor_workflows()
        if "error" in result:
            print(f"❌ Monitoring failed: {result['error']}")
        else:
            print("🔍 Monitoring Results:")
            print(f"   Workflows monitored: {result['workflows_monitored']}")
            print(f"   Total runs: {result['total_runs']}")
            print(f"   Successful: {result['successful_runs']}")
            print(f"   Failed: {result['failed_runs']}")
            if result['alerts']:
                print("   Alerts:")
                for alert in result['alerts']:
                    print(f"     🚨 {alert}")

if __name__ == '__main__':
    main()
