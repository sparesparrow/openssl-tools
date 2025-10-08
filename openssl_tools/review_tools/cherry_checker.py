#!/usr/bin/env python3
"""
OpenSSL Cherry Checker Tool - Python Implementation
Check cherry-picked commits
"""

import os
import sys
import subprocess
import argparse
import logging
from typing import List, Optional, Dict, Any, Set
from pathlib import Path
import json
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CherryCheckerTool:
    """Check cherry-picked commits"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the Cherry Checker tool"""
        self.config = self._load_config(config_path)
        
    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration from file or environment"""
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        
        # Default configuration
        return {
            'tools': {
                'cherry_checker': {
                    'check_duplicates': True,
                    'check_author': True,
                    'check_message': True
                }
            }
        }
    
    def parse_arguments(self, args: List[str]) -> argparse.Namespace:
        """Parse command line arguments"""
        parser = argparse.ArgumentParser(
            description='Check cherry-picked commits',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  cherry-checker HEAD~10..HEAD
  cherry-checker --branch=master HEAD~5..HEAD
  cherry-checker --check-duplicates HEAD~20..HEAD
            """
        )
        
        parser.add_argument('range', help='Commit range to check')
        parser.add_argument('--branch', help='Base branch to compare against')
        parser.add_argument('--check-duplicates', action='store_true', 
                          help='Check for duplicate commits')
        parser.add_argument('--check-author', action='store_true', 
                          help='Check author consistency')
        parser.add_argument('--check-message', action='store_true', 
                          help='Check commit message consistency')
        parser.add_argument('--verbose', action='store_true', help='Verbose output')
        
        return parser.parse_args(args)
    
    def get_commits_in_range(self, commit_range: str) -> List[Dict[str, Any]]:
        """Get commits in the specified range"""
        try:
            result = subprocess.run(
                ['git', 'log', '--pretty=format:%H|%an|%ae|%s|%b', commit_range],
                capture_output=True,
                text=True,
                check=True
            )
            
            commits = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                
                parts = line.split('|', 4)
                if len(parts) >= 4:
                    commits.append({
                        'hash': parts[0],
                        'author_name': parts[1],
                        'author_email': parts[2],
                        'subject': parts[3],
                        'body': parts[4] if len(parts) > 4 else ''
                    })
            
            return commits
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get commits: {e}")
            return []
    
    def get_commit_message(self, commit_hash: str) -> str:
        """Get full commit message for a commit"""
        try:
            result = subprocess.run(
                ['git', 'show', '--pretty=format:%B', '--no-patch', commit_hash],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            logger.warning(f"Could not get message for {commit_hash}: {e}")
            return ""
    
    def check_duplicates(self, commits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Check for duplicate commits"""
        duplicates = []
        seen_subjects = {}
        
        for commit in commits:
            subject = commit['subject']
            if subject in seen_subjects:
                duplicates.append({
                    'type': 'duplicate_subject',
                    'commit1': seen_subjects[subject],
                    'commit2': commit,
                    'message': f"Duplicate subject: {subject}"
                })
            else:
                seen_subjects[subject] = commit
        
        return duplicates
    
    def check_author_consistency(self, commits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Check author consistency"""
        issues = []
        authors = set()
        
        for commit in commits:
            author = f"{commit['author_name']} <{commit['author_email']}>"
            authors.add(author)
        
        if len(authors) > 1:
            issues.append({
                'type': 'multiple_authors',
                'authors': list(authors),
                'message': f"Multiple authors found: {', '.join(authors)}"
            })
        
        return issues
    
    def check_message_consistency(self, commits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Check commit message consistency"""
        issues = []
        
        for commit in commits:
            message = commit['subject']
            
            # Check for common issues
            if not message:
                issues.append({
                    'type': 'empty_subject',
                    'commit': commit,
                    'message': "Empty commit subject"
                })
            
            if message.startswith('WIP'):
                issues.append({
                    'type': 'wip_commit',
                    'commit': commit,
                    'message': "WIP commit found"
                })
            
            if len(message) > 72:
                issues.append({
                    'type': 'long_subject',
                    'commit': commit,
                    'message': f"Subject too long ({len(message)} characters)"
                })
            
            # Check for cherry-pick markers
            if 'cherry picked from commit' in message.lower():
                issues.append({
                    'type': 'cherry_pick_marker',
                    'commit': commit,
                    'message': "Cherry-pick marker found in message"
                })
        
        return issues
    
    def check_against_branch(self, commits: List[Dict[str, Any]], branch: str) -> List[Dict[str, Any]]:
        """Check commits against a base branch"""
        issues = []
        
        try:
            # Get commits in the base branch
            base_commits = self.get_commits_in_range(branch)
            base_subjects = {commit['subject'] for commit in base_commits}
            
            # Check if any commits already exist in the base branch
            for commit in commits:
                if commit['subject'] in base_subjects:
                    issues.append({
                        'type': 'already_in_branch',
                        'commit': commit,
                        'message': f"Commit already exists in {branch}"
                    })
        
        except Exception as e:
            logger.warning(f"Could not check against branch {branch}: {e}")
        
        return issues
    
    def format_issue(self, issue: Dict[str, Any]) -> str:
        """Format an issue for display"""
        if issue['type'] == 'duplicate_subject':
            return (f"DUPLICATE: {issue['message']}\n"
                   f"  {issue['commit1']['hash'][:8]}: {issue['commit1']['subject']}\n"
                   f"  {issue['commit2']['hash'][:8]}: {issue['commit2']['subject']}")
        
        elif issue['type'] == 'multiple_authors':
            return f"MULTIPLE AUTHORS: {issue['message']}"
        
        elif issue['type'] in ['empty_subject', 'wip_commit', 'long_subject', 'cherry_pick_marker']:
            return (f"{issue['type'].upper()}: {issue['message']}\n"
                   f"  {issue['commit']['hash'][:8]}: {issue['commit']['subject']}")
        
        elif issue['type'] == 'already_in_branch':
            return (f"ALREADY IN BRANCH: {issue['message']}\n"
                   f"  {issue['commit']['hash'][:8]}: {issue['commit']['subject']}")
        
        else:
            return f"UNKNOWN: {issue['message']}"
    
    def run(self, args: List[str]) -> int:
        """Main entry point"""
        try:
            parsed_args = self.parse_arguments(args)
            
            # Get commits in range
            commits = self.get_commits_in_range(parsed_args.range)
            if not commits:
                logger.info("No commits found in range")
                return 0
            
            logger.info(f"Checking {len(commits)} commits in range {parsed_args.range}")
            
            issues = []
            
            # Check duplicates
            if parsed_args.check_duplicates:
                duplicates = self.check_duplicates(commits)
                issues.extend(duplicates)
            
            # Check author consistency
            if parsed_args.check_author:
                author_issues = self.check_author_consistency(commits)
                issues.extend(author_issues)
            
            # Check message consistency
            if parsed_args.check_message:
                message_issues = self.check_message_consistency(commits)
                issues.extend(message_issues)
            
            # Check against base branch
            if parsed_args.branch:
                branch_issues = self.check_against_branch(commits, parsed_args.branch)
                issues.extend(branch_issues)
            
            # Report issues
            if issues:
                logger.warning(f"Found {len(issues)} issues:")
                for issue in issues:
                    print(self.format_issue(issue))
                    print()
                return 1
            else:
                logger.info("No issues found")
                return 0
            
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
            return 1
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return 1


def main():
    """Main entry point for command line usage"""
    tool = CherryCheckerTool()
    sys.exit(tool.run(sys.argv[1:]))


if __name__ == '__main__':
    main()