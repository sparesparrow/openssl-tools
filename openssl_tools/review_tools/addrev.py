#!/usr/bin/env python3
"""
OpenSSL AddRev Tool - Python Implementation
Add or edit reviewers to commits
"""

import os
import sys
import subprocess
import argparse
import re
from typing import List, Optional, Dict, Any
from pathlib import Path
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AddRevTool:
    """Add or edit reviewers to commits"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the AddRev tool"""
        self.config = self._load_config(config_path)
        self.gitaddrev = os.environ.get('GITADDREV', 'gitaddrev')
        
    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration from file or environment"""
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        
        # Default configuration
        return {
            'tools': {
                'review_tools': {
                    'min_reviewers': 2,
                    'min_otc': 0,
                    'min_omc': 0,
                    'api_endpoint': 'https://api.openssl.org'
                }
            }
        }
    
    def parse_arguments(self, args: List[str]) -> argparse.Namespace:
        """Parse command line arguments"""
        parser = argparse.ArgumentParser(
            description='Add or edit reviewers to commits',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  addrev --prnum=1234 steve
  addrev 1234 -2 steve
  addrev 1234 -2 steve @richsalz
  addrev 1234 -2 --reviewer=steve --reviewer=rsalz@openssl.org
            """
        )
        
        parser.add_argument('--help', '-h', action='help', help='Show this help message')
        parser.add_argument('--list', action='store_true', help='List known reviewers and exit')
        parser.add_argument('--verbose', action='store_true', help='Be more verbose')
        parser.add_argument('--trivial', action='store_true', help='Do not require a CLA')
        parser.add_argument('--reviewer', action='append', help='A reviewer to be added')
        parser.add_argument('--rmreviewers', action='store_true', help='Remove existing Reviewed-by lines')
        parser.add_argument('--commit', help='Only apply to specific commit')
        parser.add_argument('--myemail', help='Set email address')
        parser.add_argument('--nopr', action='store_true', help='Do not require a PR number')
        parser.add_argument('--prnum', type=int, help='GitHub pull request number')
        parser.add_argument('--web', action='store_true', help='Use web repository')
        parser.add_argument('--tools', action='store_true', help='Use tools repository')
        parser.add_argument('--fuzz-corpora', action='store_true', help='Use fuzz-corpora repository')
        parser.add_argument('--perftools', action='store_true', help='Use perftools repository')
        parser.add_argument('--installer', action='store_true', help='Use installer repository')
        parser.add_argument('--noself', action='store_true', help='Do not add self as reviewer')
        parser.add_argument('--security', action='store_true', help='Security-related commit')
        parser.add_argument('--release', action='store_true', help='Release-related commit')
        
        # Positional arguments
        parser.add_argument('positional', nargs='*', help='Reviewers or commit range')
        
        return parser.parse_args(args)
    
    def list_reviewers(self) -> None:
        """List known reviewers"""
        try:
            # This would integrate with the OpenSSL Query API
            # For now, we'll use a placeholder
            logger.info("Listing known reviewers...")
            logger.info("This feature requires integration with OpenSSL Query API")
            logger.info("Known reviewers would be listed here")
        except Exception as e:
            logger.error(f"Failed to list reviewers: {e}")
            sys.exit(1)
    
    def get_my_email(self) -> str:
        """Get current user's email from git config"""
        try:
            result = subprocess.run(
                ['git', 'config', '--get', 'user.email'],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            logger.warning("Could not get git user.email")
            return ""
    
    def determine_repository_type(self, args: argparse.Namespace) -> str:
        """Determine repository type based on arguments"""
        if args.web:
            return 'web'
        elif args.tools:
            return 'tools'
        elif args.fuzz_corpora:
            return 'fuzz-corpora'
        elif args.perftools:
            return 'perftools'
        elif args.installer:
            return 'installer'
        else:
            return 'openssl'
    
    def build_gitaddrev_args(self, args: argparse.Namespace) -> List[str]:
        """Build arguments for gitaddrev"""
        gitaddrev_args = []
        
        # Add reviewers
        reviewers = args.reviewer or []
        for reviewer in reviewers:
            gitaddrev_args.extend(['--reviewer', reviewer])
        
        # Add positional reviewers
        for arg in args.positional:
            if re.match(r'^@\w+$', arg):
                gitaddrev_args.extend(['--reviewer', arg])
            elif re.match(r'^\w[-\w]*$', arg) and not re.match(r'^[0-9a-f]{7,}$', arg):
                gitaddrev_args.extend(['--reviewer', arg])
        
        # Add other options
        if args.prnum:
            gitaddrev_args.extend(['--prnum', str(args.prnum)])
        elif args.nopr or args.security:
            gitaddrev_args.append('--nopr')
        
        if args.trivial:
            gitaddrev_args.append('--trivial')
        
        if args.rmreviewers:
            gitaddrev_args.append('--rmreviewers')
        
        if args.commit:
            gitaddrev_args.extend(['--commit', args.commit])
        
        if args.myemail:
            gitaddrev_args.extend(['--myemail', args.myemail])
        elif not args.noself:
            my_email = self.get_my_email()
            if my_email:
                gitaddrev_args.extend(['--myemail', my_email])
        
        if args.verbose:
            gitaddrev_args.append('--verbose')
        
        if args.release:
            gitaddrev_args.append('--release')
        
        # Add repository type
        repo_type = self.determine_repository_type(args)
        if repo_type != 'openssl':
            gitaddrev_args.append(f'--{repo_type}')
        
        return gitaddrev_args
    
    def determine_commit_range(self, args: argparse.Namespace) -> str:
        """Determine commit range from arguments"""
        # Look for commit range in positional arguments
        for arg in args.positional:
            if re.match(r'^[0-9a-f]{7,}$', arg):
                return arg
            elif re.match(r'^HEAD~?\d+\.\.', arg):
                return arg
            elif re.match(r'^HEAD\^+$', arg):
                return arg
        
        # Default to last commit
        return "HEAD^.."
    
    def run_git_filter_branch(self, gitaddrev_args: List[str], commit_range: str) -> int:
        """Run git filter-branch with gitaddrev"""
        try:
            # Set environment variable to suppress warnings
            env = os.environ.copy()
            env['FILTER_BRANCH_SQUELCH_WARNING'] = '1'
            
            # Build the command
            cmd = [
                'git', 'filter-branch', '-f',
                '--tag-name-filter', 'cat',
                '--msg-filter', f"{self.gitaddrev} {' '.join(gitaddrev_args)}",
                commit_range
            ]
            
            logger.info(f"Running: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, env=env, check=True)
            return result.returncode
            
        except subprocess.CalledProcessError as e:
            logger.error(f"git filter-branch failed: {e}")
            return e.returncode
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return 1
    
    def run(self, args: List[str]) -> int:
        """Main entry point"""
        try:
            parsed_args = self.parse_arguments(args)
            
            if parsed_args.list:
                self.list_reviewers()
                return 0
            
            # Validate arguments
            if not parsed_args.prnum and not parsed_args.nopr and not parsed_args.security:
                logger.error("Need either --prnum=NNN or --nopr flag")
                return 1
            
            # Build gitaddrev arguments
            gitaddrev_args = self.build_gitaddrev_args(parsed_args)
            
            # Determine commit range
            commit_range = self.determine_commit_range(parsed_args)
            
            # Run git filter-branch
            return self.run_git_filter_branch(gitaddrev_args, commit_range)
            
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
            return 1
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return 1


def main():
    """Main entry point for command line usage"""
    tool = AddRevTool()
    sys.exit(tool.run(sys.argv[1:]))


if __name__ == '__main__':
    main()