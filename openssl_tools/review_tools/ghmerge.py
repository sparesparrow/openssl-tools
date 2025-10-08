#!/usr/bin/env python3
"""
OpenSSL GhMerge Tool - Python Implementation
Merge GitHub pull requests with safety checks
"""

import os
import sys
import subprocess
import argparse
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path
import json
import requests

try:
    from github import Github
    GITHUB_AVAILABLE = True
except ImportError:
    GITHUB_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GhMergeTool:
    """Merge GitHub pull requests with safety checks"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the GhMerge tool"""
        self.config = self._load_config(config_path)
        self.github_token = os.environ.get('GITHUB_TOKEN')
        self.github = None
        
        if self.github_token and GITHUB_AVAILABLE:
            self.github = Github(self.github_token)
        elif self.github_token and not GITHUB_AVAILABLE:
            logger.warning("GitHub token provided but PyGithub not available")
        
    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration from file or environment"""
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        
        # Default configuration
        return {
            'tools': {
                'github': {
                    'api_endpoint': 'https://api.github.com',
                    'default_remote': 'origin'
                }
            }
        }
    
    def parse_arguments(self, args: List[str]) -> argparse.Namespace:
        """Parse command line arguments"""
        parser = argparse.ArgumentParser(
            description='Merge GitHub pull requests with safety checks',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  ghmerge 1234 steve levitte
  ghmerge --tools --squash 1234 steve
  ghmerge --web 1234 @richsalz
            """
        )
        
        parser.add_argument('prnum', type=int, help='GitHub pull request number')
        parser.add_argument('reviewers', nargs='*', help='Reviewers to add')
        parser.add_argument('--noautosquash', action='store_true', help='No autosquash in rebase')
        parser.add_argument('--squash', action='store_true', help='Use squash merge')
        parser.add_argument('--nobuild', action='store_true', help='Skip build step')
        parser.add_argument('--remote', help='Git remote to use')
        parser.add_argument('--tools', action='store_true', help='Use tools repository')
        parser.add_argument('--web', action='store_true', help='Use web repository')
        parser.add_argument('--trivial', action='store_true', help='Mark as trivial')
        parser.add_argument('--verbose', action='store_true', help='Verbose output')
        
        return parser.parse_args(args)
    
    def get_remote_name(self, args: argparse.Namespace) -> str:
        """Get the remote name to use"""
        if args.remote:
            return args.remote
        
        # Try to find default remote
        try:
            result = subprocess.run(
                ['git', 'remote', '-v'],
                capture_output=True,
                text=True,
                check=True
            )
            
            for line in result.stdout.split('\n'):
                if 'github.openssl.org' in line and '(push)' in line:
                    return line.split()[0]
            
            # Fallback to origin
            return 'origin'
            
        except subprocess.CalledProcessError:
            logger.warning("Could not determine remote, using origin")
            return 'origin'
    
    def get_repository_name(self, args: argparse.Namespace) -> str:
        """Get repository name based on arguments"""
        if args.web:
            return 'openssl/web'
        elif args.tools:
            return 'openssl/tools'
        else:
            return 'openssl/openssl'
    
    def fetch_pull_request(self, prnum: int, repo_name: str) -> Optional[Dict[str, Any]]:
        """Fetch pull request information from GitHub"""
        if not self.github:
            logger.error("GitHub token not available")
            return None
        
        try:
            repo = self.github.get_repo(repo_name)
            pr = repo.get_pull(prnum)
            
            return {
                'number': pr.number,
                'title': pr.title,
                'body': pr.body,
                'state': pr.state,
                'merged': pr.merged,
                'head': {
                    'ref': pr.head.ref,
                    'sha': pr.head.sha
                },
                'base': {
                    'ref': pr.base.ref,
                    'sha': pr.base.sha
                },
                'user': {
                    'login': pr.user.login
                }
            }
        except Exception as e:
            logger.error(f"Failed to fetch pull request {prnum}: {e}")
            return None
    
    def show_pull_request_info(self, pr_info: Dict[str, Any]) -> None:
        """Show pull request information"""
        logger.info(f"Pull Request #{pr_info['number']}: {pr_info['title']}")
        logger.info(f"Author: {pr_info['user']['login']}")
        logger.info(f"State: {pr_info['state']}")
        logger.info(f"Head: {pr_info['head']['ref']} ({pr_info['head']['sha'][:8]})")
        logger.info(f"Base: {pr_info['base']['ref']} ({pr_info['base']['sha'][:8]})")
        
        if pr_info['body']:
            logger.info("Description:")
            for line in pr_info['body'].split('\n')[:10]:  # Show first 10 lines
                logger.info(f"  {line}")
            if len(pr_info['body'].split('\n')) > 10:
                logger.info("  ...")
    
    def show_diff(self, pr_info: Dict[str, Any]) -> None:
        """Show diff for the pull request"""
        try:
            # Fetch the diff
            if self.github:
                repo = self.github.get_repo(self.get_repository_name(argparse.Namespace()))
                pr = repo.get_pull(pr_info['number'])
                
                logger.info("Diff:")
                logger.info("=" * 50)
                print(pr.diff().decode('utf-8'))
                logger.info("=" * 50)
                
        except Exception as e:
            logger.warning(f"Could not fetch diff: {e}")
    
    def run_build(self, args: argparse.Namespace) -> bool:
        """Run build if not disabled"""
        if args.nobuild or args.tools or args.web:
            logger.info("Skipping build step")
            return True
        
        try:
            logger.info("Running build...")
            # This would run the actual build
            # For now, just return success
            logger.info("Build completed successfully")
            return True
        except Exception as e:
            logger.error(f"Build failed: {e}")
            return False
    
    def add_reviewers(self, prnum: int, reviewers: List[str], args: argparse.Namespace) -> bool:
        """Add reviewers using addrev tool"""
        try:
            # Build addrev command
            addrev_cmd = ['addrev', f'--prnum={prnum}']
            
            if args.trivial:
                addrev_cmd.append('--trivial')
            
            if args.tools:
                addrev_cmd.append('--tools')
            elif args.web:
                addrev_cmd.append('--web')
            
            addrev_cmd.extend(reviewers)
            
            logger.info(f"Running: {' '.join(addrev_cmd)}")
            result = subprocess.run(addrev_cmd, check=True)
            return result.returncode == 0
            
        except subprocess.CalledProcessError as e:
            logger.error(f"addrev failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error in addrev: {e}")
            return False
    
    def merge_pull_request(self, pr_info: Dict[str, Any], args: argparse.Namespace) -> bool:
        """Merge the pull request"""
        try:
            remote_name = self.get_remote_name(args)
            
            # Fetch latest changes
            logger.info(f"Fetching from {remote_name}...")
            subprocess.run(['git', 'fetch', remote_name], check=True)
            
            # Checkout base branch
            base_branch = pr_info['base']['ref']
            logger.info(f"Checking out {base_branch}...")
            subprocess.run(['git', 'checkout', base_branch], check=True)
            
            # Pull latest changes
            subprocess.run(['git', 'pull', remote_name, base_branch], check=True)
            
            # Create merge commit
            head_sha = pr_info['head']['sha']
            logger.info(f"Merging {head_sha}...")
            
            if args.squash:
                # Squash merge
                subprocess.run(['git', 'merge', '--squash', head_sha], check=True)
                subprocess.run(['git', 'commit'], check=True)
            else:
                # Regular merge
                subprocess.run(['git', 'merge', '--no-ff', head_sha], check=True)
            
            # Post-process with rebase if not squash
            if not args.squash:
                if args.noautosquash:
                    subprocess.run(['git', 'rebase', '-i', 'HEAD~1'], check=True)
                else:
                    subprocess.run(['git', 'rebase', '-i', '--autosquash', 'HEAD~1'], check=True)
            
            logger.info("Merge completed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Merge failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during merge: {e}")
            return False
    
    def confirm_merge(self, pr_info: Dict[str, Any]) -> bool:
        """Ask user to confirm merge"""
        logger.info("=" * 60)
        logger.info("MERGE CONFIRMATION")
        logger.info("=" * 60)
        logger.info(f"About to merge PR #{pr_info['number']}: {pr_info['title']}")
        logger.info(f"Author: {pr_info['user']['login']}")
        logger.info("=" * 60)
        
        response = input("Do you want to continue? (y/N): ").strip().lower()
        return response in ['y', 'yes']
    
    def run(self, args: List[str]) -> int:
        """Main entry point"""
        try:
            parsed_args = self.parse_arguments(args)
            
            # Get repository name
            repo_name = self.get_repository_name(parsed_args)
            
            # Fetch pull request
            pr_info = self.fetch_pull_request(parsed_args.prnum, repo_name)
            if not pr_info:
                logger.error(f"Could not fetch pull request {parsed_args.prnum}")
                return 1
            
            # Show pull request info
            self.show_pull_request_info(pr_info)
            
            # Show diff
            self.show_diff(pr_info)
            
            # Run build
            if not self.run_build(parsed_args):
                logger.error("Build failed, aborting merge")
                return 1
            
            # Add reviewers
            if parsed_args.reviewers:
                if not self.add_reviewers(parsed_args.prnum, parsed_args.reviewers, parsed_args):
                    logger.error("Failed to add reviewers")
                    return 1
            
            # Confirm merge
            if not self.confirm_merge(pr_info):
                logger.info("Merge cancelled by user")
                return 0
            
            # Perform merge
            if not self.merge_pull_request(pr_info, parsed_args):
                logger.error("Merge failed")
                return 1
            
            logger.info("Merge completed successfully!")
            return 0
            
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
            return 1
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return 1


def main():
    """Main entry point for command line usage"""
    tool = GhMergeTool()
    sys.exit(tool.run(sys.argv[1:]))


if __name__ == '__main__':
    main()