#!/usr/bin/env python3
"""
OpenSSL GitLabUtil Tool - Python Implementation
GitLab merge request query tool
"""

import os
import sys
import argparse
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path
import json
try:
    import gitlab
    GITLAB_AVAILABLE = True
except ImportError:
    GITLAB_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GitLabUtilTool:
    """GitLab merge request query tool"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the GitLabUtil tool"""
        self.config = self._load_config(config_path)
        self.gitlab_token = self._get_gitlab_token()
        self.gitlab = None
        
        if self.gitlab_token and GITLAB_AVAILABLE:
            self.gitlab = gitlab.Gitlab(
                self.config.get('tools', {}).get('gitlab', {}).get('api_endpoint', 'https://gitlab.com'),
                private_token=self.gitlab_token
            )
        elif self.gitlab_token and not GITLAB_AVAILABLE:
            logger.warning("GitLab token provided but python-gitlab not available")
    
    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration from file or environment"""
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        
        # Default configuration
        return {
            'tools': {
                'gitlab': {
                    'api_endpoint': 'https://gitlab.com/api/v4'
                }
            }
        }
    
    def _get_gitlab_token(self) -> Optional[str]:
        """Get GitLab token from environment or file"""
        # Try environment variable first
        token = os.environ.get('GITLAB_TOKEN')
        if token:
            return token
        
        # Try token file
        token_file = os.path.expanduser('~/.gitlabtoken')
        if os.path.exists(token_file):
            try:
                with open(token_file, 'r') as f:
                    return f.read().strip()
            except Exception as e:
                logger.warning(f"Could not read GitLab token file: {e}")
        
        return None
    
    def parse_arguments(self, args: List[str]) -> argparse.Namespace:
        """Parse command line arguments"""
        parser = argparse.ArgumentParser(
            description='GitLab merge request query tool',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  gitlabutil --state=all 1
  gitlabutil --state=all --user=foo --text
  gitlabutil --checkout 145
            """
        )
        
        parser.add_argument('--state', choices=['all', 'merged', 'opened', 'closed'], 
                          default='opened', help='State of requests to query')
        parser.add_argument('--token', help='GitLab private token')
        parser.add_argument('--desc', help='Description regex filter')
        parser.add_argument('--user', help='Filter by user name')
        parser.add_argument('--text', action='store_true', help='Print full description')
        parser.add_argument('--fetch', action='store_true', help='Fetch branch from request')
        parser.add_argument('--checkout', action='store_true', help='Checkout branch from request')
        parser.add_argument('number', type=int, nargs='?', help='Specific merge request number')
        
        return parser.parse_args(args)
    
    def list_merge_requests(self, args: argparse.Namespace) -> List[Dict[str, Any]]:
        """List merge requests based on criteria"""
        if not self.gitlab:
            logger.error("GitLab not initialized. Check token configuration.")
            return []
        
        try:
            # Get current project (assuming we're in a git repository)
            project = self._get_current_project()
            if not project:
                logger.error("Could not determine current GitLab project")
                return []
            
            # Get merge requests
            mrs = project.mergerequests.list(
                state=args.state,
                order_by='created_at',
                sort='desc'
            )
            
            # Filter by user if specified
            if args.user:
                mrs = [mr for mr in mrs if mr.author['username'] == args.user]
            
            # Filter by description if specified
            if args.desc:
                import re
                pattern = re.compile(args.desc, re.IGNORECASE)
                mrs = [mr for mr in mrs if pattern.search(mr.description or '')]
            
            return mrs
            
        except Exception as e:
            logger.error(f"Failed to list merge requests: {e}")
            return []
    
    def _get_current_project(self) -> Optional[Any]:
        """Get current GitLab project"""
        try:
            # Get remote URL
            result = subprocess.run(
                ['git', 'remote', 'get-url', 'origin'],
                capture_output=True,
                text=True,
                check=True
            )
            
            remote_url = result.stdout.strip()
            
            # Extract project path from URL
            # Assuming format: git@gitlab.com:group/project.git
            # or https://gitlab.com/group/project.git
            if 'gitlab.com' in remote_url:
                if remote_url.startswith('git@'):
                    # SSH format
                    project_path = remote_url.split(':')[1].replace('.git', '')
                else:
                    # HTTPS format
                    project_path = remote_url.split('gitlab.com/')[1].replace('.git', '')
                
                return self.gitlab.projects.get(project_path)
            
        except Exception as e:
            logger.warning(f"Could not determine current project: {e}")
        
        return None
    
    def show_merge_request(self, mr: Dict[str, Any], show_text: bool = False) -> None:
        """Show merge request information"""
        print(f"MR !{mr.iid}: {mr.title}")
        print(f"  Author: {mr.author['name']} (@{mr.author['username']})")
        print(f"  State: {mr.state}")
        print(f"  Created: {mr.created_at}")
        print(f"  Updated: {mr.updated_at}")
        print(f"  Source: {mr.source_branch}")
        print(f"  Target: {mr.target_branch}")
        
        if show_text and mr.description:
            print(f"  Description:")
            for line in mr.description.split('\n'):
                print(f"    {line}")
        
        print()
    
    def fetch_branch(self, mr: Dict[str, Any], checkout: bool = False) -> bool:
        """Fetch branch from merge request"""
        try:
            branch_name = mr.source_branch
            
            # Fetch the branch
            logger.info(f"Fetching branch {branch_name}...")
            subprocess.run(['git', 'fetch', 'origin', f"{branch_name}:{branch_name}"], check=True)
            
            if checkout:
                logger.info(f"Checking out branch {branch_name}...")
                subprocess.run(['git', 'checkout', branch_name], check=True)
            
            logger.info(f"Branch {branch_name} fetched successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to fetch branch: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return False
    
    def run(self, args: List[str]) -> int:
        """Main entry point"""
        try:
            parsed_args = self.parse_arguments(args)
            
            # Override token if provided
            if parsed_args.token:
                self.gitlab_token = parsed_args.token
                self.gitlab = gitlab.Gitlab(
                    self.config.get('tools', {}).get('gitlab', {}).get('api_endpoint', 'https://gitlab.com'),
                    private_token=self.gitlab_token
                )
            
            if not self.gitlab:
                logger.error("GitLab token not available. Set GITLAB_TOKEN or use --token")
                return 1
            
            # Get merge requests
            if parsed_args.number:
                # Show specific merge request
                project = self._get_current_project()
                if not project:
                    logger.error("Could not determine current project")
                    return 1
                
                try:
                    mr = project.mergerequests.get(parsed_args.number)
                    self.show_merge_request(mr, parsed_args.text)
                    
                    if parsed_args.fetch or parsed_args.checkout:
                        self.fetch_branch(mr, parsed_args.checkout)
                    
                except Exception as e:
                    logger.error(f"Could not fetch merge request {parsed_args.number}: {e}")
                    return 1
            else:
                # List merge requests
                mrs = self.list_merge_requests(parsed_args)
                
                if not mrs:
                    logger.info("No merge requests found")
                    return 0
                
                # Show merge requests
                for mr in mrs:
                    self.show_merge_request(mr, parsed_args.text)
                
                # Handle fetch/checkout if only one match
                if (parsed_args.fetch or parsed_args.checkout) and len(mrs) == 1:
                    self.fetch_branch(mrs[0], parsed_args.checkout)
                elif (parsed_args.fetch or parsed_args.checkout) and len(mrs) > 1:
                    logger.error("Multiple merge requests match criteria. Cannot fetch/checkout.")
                    return 1
            
            return 0
            
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
            return 1
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return 1


def main():
    """Main entry point for command line usage"""
    tool = GitLabUtilTool()
    sys.exit(tool.run(sys.argv[1:]))


if __name__ == '__main__':
    main()