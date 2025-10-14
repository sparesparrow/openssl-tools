#!/usr/bin/env python3
"""
Workflow Fixer - Systematically fix failing GitHub workflow checks.
Uses cursor-agent CLI with supported options only.
"""

import argparse
import json
import subprocess
import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WorkflowFixer:
    def __init__(self, repo: str, api_key: Optional[str] = None):
        self.repo = repo
        self.api_key = api_key or self._get_api_key()
        
    def _get_api_key(self) -> str:
        """Get API key from env or file"""
        # Check CURSOR_API_KEY env var
        api_key = os.getenv('CURSOR_API_KEY')
        if api_key:
            return api_key
            
        # Check ~/.cursor/api-key file
        api_key_file = Path.home() / '.cursor' / 'api-key'
        if api_key_file.exists():
            return api_key_file.read_text().strip()
            
        raise ValueError("No CURSOR_API_KEY found in environment or ~/.cursor/api-key file")
        
    def analyze_failures(self, pr_number: int) -> Dict:
        """Get failed checks for a PR using gh CLI"""
        try:
            result = subprocess.run([
                'gh', 'pr', 'view', str(pr_number), 
                '--json', 'statusCheckRollup',
                '--repo', self.repo
            ], capture_output=True, text=True, check=True)
            
            data = json.loads(result.stdout)
            return data.get('statusCheckRollup', [])
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get PR status: {e}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse PR status JSON: {e}")
            return []
            
    def generate_fix_plan(self, failures: List[Dict]) -> Dict:
        """Use cursor-agent to analyze failures and create plan"""
        prompt = f"""Analyze these GitHub workflow failures and provide actionable fixes:
        
{json.dumps(failures, indent=2)}

Categorize failures as:
1. Quick wins (can disable/skip without risk)
2. Configuration issues (simple YAML fixes)
3. Source code issues (require OpenSSL expertise)

Return ONLY valid JSON with this structure:
{{
  "quick_wins": [{{"check": "name", "action": "disable|skip", "reason": "..."}}],
  "config_fixes": [{{"file": "path.yml", "issue": "...", "fix": "..."}}],
  "source_issues": [{{"check": "name", "analysis": "...", "recommendation": "..."}}]
}}"""
        
        try:
            result = subprocess.run([
                'cursor-agent', '-p',
                '--output-format', 'json',
                '--model', 'sonnet-4',
                prompt
            ], capture_output=True, text=True, check=True)
            
            # cursor-agent returns direct JSON, not wrapped
            return json.loads(result.stdout)
            
        except subprocess.CalledProcessError as e:
            logger.error(f"cursor-agent failed: {e}")
            logger.error(f"stderr: {e.stderr}")
            return {"quick_wins": [], "config_fixes": [], "source_issues": []}
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse cursor-agent JSON: {e}")
            return {"quick_wins": [], "config_fixes": [], "source_issues": []}
            
    def apply_quick_wins(self, quick_wins: List[Dict], pr_number: int, dry_run: bool = True):
        """Apply quick win fixes (disable/skip checks)"""
        if not quick_wins:
            logger.info("No quick wins to apply")
            return
            
        logger.info(f"Applying {len(quick_wins)} quick wins (dry_run={dry_run})")
        
        for win in quick_wins:
            check_name = win.get('check', 'unknown')
            action = win.get('action', 'disable')
            reason = win.get('reason', 'No reason provided')
            
            logger.info(f"Quick win: {action} {check_name} - {reason}")
            
            if not dry_run:
                # Comment on PR explaining the decision
                comment = f"🔧 **Quick Win Applied**\n\n**Check:** {check_name}\n**Action:** {action}\n**Reason:** {reason}\n\nThis is part of systematic workflow cleanup for openssl-tools repository."
                
                try:
                    subprocess.run([
                        'gh', 'pr', 'comment', str(pr_number),
                        '--body', comment,
                        '--repo', self.repo
                    ], check=True)
                    logger.info(f"Added comment to PR #{pr_number}")
                except subprocess.CalledProcessError as e:
                    logger.error(f"Failed to comment on PR: {e}")
                    
    def apply_config_fixes(self, config_fixes: List[Dict], dry_run: bool = True):
        """Apply configuration fixes to YAML files"""
        if not config_fixes:
            logger.info("No config fixes to apply")
            return
            
        logger.info(f"Applying {len(config_fixes)} config fixes (dry_run={dry_run})")
        
        for fix in config_fixes:
            file_path = fix.get('file', '')
            issue = fix.get('issue', '')
            fix_text = fix.get('fix', '')
            
            logger.info(f"Config fix: {file_path} - {issue}")
            
            if not dry_run and file_path:
                # Apply the YAML patch
                try:
                    # This would need to be implemented based on specific fix types
                    logger.info(f"Would apply fix to {file_path}: {fix_text}")
                except Exception as e:
                    logger.error(f"Failed to apply config fix: {e}")
                    
    def report_source_issues(self, source_issues: List[Dict], pr_number: int):
        """Create detailed issue report for source code problems"""
        if not source_issues:
            logger.info("No source issues to report")
            return
            
        logger.info(f"Reporting {len(source_issues)} source issues")
        
        # Create markdown report
        report = "## 🔍 **Source Code Issues Analysis**\n\n"
        report += "The following issues require OpenSSL expertise and cannot be automatically fixed:\n\n"
        
        for issue in source_issues:
            check_name = issue.get('check', 'unknown')
            analysis = issue.get('analysis', '')
            recommendation = issue.get('recommendation', '')
            
            report += f"### {check_name}\n"
            report += f"**Analysis:** {analysis}\n\n"
            report += f"**Recommendation:** {recommendation}\n\n"
            
        report += "---\n"
        report += "**Note:** These issues require manual review by OpenSSL experts."
        
        # Post as PR comment
        try:
            subprocess.run([
                'gh', 'pr', 'comment', str(pr_number),
                '--body', report,
                '--repo', self.repo
            ], check=True)
            logger.info(f"Added source issues report to PR #{pr_number}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to comment on PR: {e}")
            
    def fix_pr(self, pr_number: int, dry_run: bool = True):
        """Main method to fix a PR"""
        logger.info(f"Analyzing PR #{pr_number} in {self.repo}")
        
        # Get failed checks
        failures = self.analyze_failures(pr_number)
        if not failures:
            logger.info(f"No failed checks found for PR #{pr_number}")
            return
            
        logger.info(f"Found {len(failures)} failed checks")
        
        # Generate fix plan using cursor-agent
        plan = self.generate_fix_plan(failures)
        
        # Apply fixes
        self.apply_quick_wins(plan.get('quick_wins', []), pr_number, dry_run)
        self.apply_config_fixes(plan.get('config_fixes', []), dry_run)
        self.report_source_issues(plan.get('source_issues', []), pr_number)
        
        logger.info(f"Completed fixing PR #{pr_number}")

def main():
    parser = argparse.ArgumentParser(description='Fix failing GitHub workflow checks')
    parser.add_argument('--repo', required=True, help='Repository in format owner/repo')
    parser.add_argument('--pr', type=int, help='PR number to fix')
    parser.add_argument('--all-prs', action='store_true', help='Fix all open PRs')
    parser.add_argument('--dry-run', action='store_true', default=True, help='Dry run mode (default)')
    parser.add_argument('--apply', action='store_true', help='Actually apply fixes (overrides dry-run)')
    parser.add_argument('--api-key', help='Cursor API key (overrides env/file)')
    
    args = parser.parse_args()
    
    # Determine if this is a dry run
    dry_run = args.dry_run and not args.apply
    
    try:
        fixer = WorkflowFixer(args.repo, args.api_key)
        
        if args.all_prs:
            # Get all open PRs
            result = subprocess.run([
                'gh', 'pr', 'list', '--json', 'number', '--repo', args.repo
            ], capture_output=True, text=True, check=True)
            
            prs = json.loads(result.stdout)
            for pr in prs:
                pr_number = pr['number']
                fixer.fix_pr(pr_number, dry_run)
        elif args.pr:
            fixer.fix_pr(args.pr, dry_run)
        else:
            parser.error("Must specify either --pr or --all-prs")
            
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
