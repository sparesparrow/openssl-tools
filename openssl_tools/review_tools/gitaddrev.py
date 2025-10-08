#!/usr/bin/env python3
"""
OpenSSL GitAddRev Tool - Python Implementation
Add reviewers to commit messages with CLA validation
"""

import os
import sys
import re
import argparse
import json
import logging
from typing import List, Optional, Dict, Any, Set
from dataclasses import dataclass
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Reviewer:
    """Represents a reviewer"""
    name: str
    email: str
    github_id: Optional[str] = None
    has_cla: bool = False
    is_otc: bool = False
    is_omc: bool = False
    is_author: bool = False


class OpenSSLQueryAPI:
    """Interface to OpenSSL Query API"""
    
    def __init__(self, api_endpoint: str = "https://api.openssl.org"):
        self.api_endpoint = api_endpoint
        self.session = requests.Session()
    
    def find_person_tag(self, identifier: str, tag_type: str = 'rev') -> Optional[str]:
        """Find person tag from identifier"""
        try:
            # This would make API calls to OpenSSL Query API
            # For now, return a placeholder
            logger.debug(f"Looking up person tag for {identifier}")
            return f"placeholder_{identifier}"
        except Exception as e:
            logger.warning(f"Failed to find person tag for {identifier}: {e}")
            return None
    
    def has_cla(self, person_tag: str) -> bool:
        """Check if person has CLA"""
        try:
            # This would check CLA status via API
            # For now, return True as placeholder
            logger.debug(f"Checking CLA for {person_tag}")
            return True
        except Exception as e:
            logger.warning(f"Failed to check CLA for {person_tag}: {e}")
            return False
    
    def is_member_of(self, identifier: str, group: str) -> bool:
        """Check if person is member of group (otc, omc, etc.)"""
        try:
            # This would check group membership via API
            # For now, return False as placeholder
            logger.debug(f"Checking {group} membership for {identifier}")
            return False
        except Exception as e:
            logger.warning(f"Failed to check {group} membership for {identifier}: {e}")
            return False
    
    def list_people(self) -> List[Dict[str, Any]]:
        """List all people in the database"""
        try:
            # This would fetch from API
            # For now, return empty list
            logger.debug("Listing people from API")
            return []
        except Exception as e:
            logger.warning(f"Failed to list people: {e}")
            return []


class GitAddRevTool:
    """Add reviewers to commit messages with validation"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the GitAddRev tool"""
        self.config = self._load_config(config_path)
        self.query_api = OpenSSLQueryAPI(
            self.config.get('tools', {}).get('review_tools', {}).get('api_endpoint', 'https://api.openssl.org')
        )
        
        # Configuration
        review_config = self.config.get('tools', {}).get('review_tools', {})
        self.min_reviewers = review_config.get('min_reviewers', 2)
        self.min_otc = review_config.get('min_otc', 0)
        self.min_omc = review_config.get('min_omc', 0)
        
        # State
        self.reviewers: List[Reviewer] = []
        self.nocla_reviewers: List[str] = []
        self.unknown_reviewers: List[str] = []
        self.author_email = os.environ.get('GIT_AUTHOR_EMAIL', '')
        self.author_reviewer: Optional[Reviewer] = None
        
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
        parser = argparse.ArgumentParser(description='Add reviewers to commit messages')
        
        parser.add_argument('--list', action='store_true', help='List known reviewers')
        parser.add_argument('--reviewer', action='append', help='Add reviewer')
        parser.add_argument('--prnum', type=int, help='Pull request number')
        parser.add_argument('--commit', help='Specific commit to process')
        parser.add_argument('--rmreviewers', action='store_true', help='Remove existing reviewers')
        parser.add_argument('--myemail', help='My email address')
        parser.add_argument('--verbose', action='store_true', help='Verbose output')
        parser.add_argument('--tools', action='store_true', help='Tools repository')
        parser.add_argument('--fuzz-corpora', action='store_true', help='Fuzz-corpora repository')
        parser.add_argument('--perftools', action='store_true', help='Perftools repository')
        parser.add_argument('--installer', action='store_true', help='Installer repository')
        parser.add_argument('--web', action='store_true', help='Web repository')
        parser.add_argument('--release', action='store_true', help='Release commit')
        
        return parser.parse_args(args)
    
    def is_author(self, reviewer: Reviewer) -> bool:
        """Check if reviewer is the author"""
        return (self.author_reviewer and 
                reviewer.email == self.author_reviewer.email)
    
    def try_add_reviewer(self, identifier: str) -> Optional[Reviewer]:
        """Try to add a reviewer with validation"""
        # Parse identifier
        if identifier.startswith('@'):
            github_id = identifier[1:]
            person_tag = self.query_api.find_person_tag({'github': github_id}, 'rev')
        else:
            person_tag = self.query_api.find_person_tag(identifier, 'rev')
            github_id = None
        
        if not person_tag:
            self.unknown_reviewers.append(identifier)
            return None
        
        # Check CLA
        if not self.query_api.has_cla(person_tag.lower()):
            self.nocla_reviewers.append(identifier)
            return None
        
        # Create reviewer object
        reviewer = Reviewer(
            name=person_tag,
            email=identifier if '@' in identifier else f"{person_tag}@openssl.org",
            github_id=github_id,
            has_cla=True,
            is_otc=self.query_api.is_member_of(identifier, 'otc'),
            is_omc=self.query_api.is_member_of(identifier, 'omc'),
            is_author=self.is_author(Reviewer(name=person_tag, email=identifier))
        )
        
        # Check if already added
        if any(r.email == reviewer.email for r in self.reviewers):
            return reviewer
        
        # Add to reviewers list
        self.reviewers.append(reviewer)
        return reviewer
    
    def list_reviewers(self) -> None:
        """List known reviewers"""
        try:
            people = self.query_api.list_people()
            if not people:
                logger.info("No reviewers found in database")
                return
            
            # Format and display
            logger.info("Known reviewers:")
            for person in people:
                # This would format the output properly
                logger.info(f"  {person}")
                
        except Exception as e:
            logger.error(f"Failed to list reviewers: {e}")
    
    def validate_reviewers(self, trivial: bool = False) -> bool:
        """Validate reviewer requirements"""
        # Check author CLA for non-trivial commits
        if not trivial and self.author_reviewer and not self.author_reviewer.has_cla:
            logger.error(f"Commit author {self.author_email} has no CLA, and this is a non-trivial commit")
            return False
        
        # Check unknown reviewers
        if self.unknown_reviewers:
            logger.error(f"Unknown reviewers: {', '.join(self.unknown_reviewers)}")
            return False
        
        # Check reviewers without CLA
        if self.nocla_reviewers:
            logger.error(f"Reviewers without CLA: {', '.join(self.nocla_reviewers)}")
            return False
        
        # Count reviewers
        author_count = sum(1 for r in self.reviewers if r.is_author)
        otc_count = sum(1 for r in self.reviewers if r.is_otc)
        omc_count = sum(1 for r in self.reviewers if r.is_omc)
        
        # Check minimum reviewers
        if len(self.reviewers) < self.min_reviewers - author_count:
            logger.error(f"Too few reviewers (total must be at least {self.min_reviewers - author_count})")
            return False
        
        # Check OTC requirement
        if otc_count < self.min_otc:
            logger.error("At least one of the reviewers must be an OTC member")
            return False
        
        # Check OMC requirement
        if omc_count < self.min_omc:
            logger.error("At least one of the reviewers must be an OMC member")
            return False
        
        return True
    
    def process_commit_message(self, message_lines: List[str], args: argparse.Namespace) -> List[str]:
        """Process commit message and add reviewers"""
        # Check if this is a trivial commit
        trivial = any('CLA: Trivial' in line for line in message_lines)
        
        # Add author as reviewer if not already present
        if self.author_email and not any(r.email == self.author_email for r in self.reviewers):
            self.author_reviewer = self.try_add_reviewer(self.author_email)
        
        # Validate reviewers
        if not self.validate_reviewers(trivial):
            sys.exit(1)
        
        # Process commit message
        output_lines = []
        last_is_rev = False
        
        for line in message_lines:
            line = line.rstrip()
            last_is_rev = False
            
            # Skip existing merge line if removing reviewers
            if (re.match(r'^\(Merged from https://github\.com/openssl/', line) and 
                not args.rmreviewers):
                last_is_rev = True
                continue
            
            # Skip existing Reviewed-by lines if removing reviewers
            if re.match(r'^Reviewed-by:\s*', line):
                if not args.rmreviewers:
                    last_is_rev = True
                    # Remove from reviewers list if already present
                    match = re.match(r'^Reviewed-by:\s*(\S.*\S)\s*$', line)
                    if match:
                        reviewer_name = match.group(1)
                        self.reviewers = [r for r in self.reviewers if r.name != reviewer_name]
                continue
            
            # Skip existing Release line if adding release
            if re.match(r'^Release:\s*yes\s*$', line, re.IGNORECASE):
                if args.release:
                    continue
            
            output_lines.append(line)
        
        # Add reviewers
        if not args.rmreviewers and self.reviewers:
            # Add blank line unless last line was a review line
            if not last_is_rev:
                output_lines.append("")
            
            for reviewer in self.reviewers:
                if not reviewer.is_author:  # Authors don't get Reviewed-by trailers
                    output_lines.append(f"Reviewed-by: {reviewer.name}")
        
        # Add release line
        if args.release:
            output_lines.append("Release: yes")
        
        # Add merge line
        if args.prnum:
            repo_type = self._determine_repo_type(args)
            output_lines.append(f"(Merged from https://github.com/openssl/{repo_type}/pull/{args.prnum})")
        
        return output_lines
    
    def _determine_repo_type(self, args: argparse.Namespace) -> str:
        """Determine repository type from arguments"""
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
    
    def run(self, args: List[str]) -> int:
        """Main entry point"""
        try:
            parsed_args = self.parse_arguments(args)
            
            if parsed_args.list:
                self.list_reviewers()
                return 0
            
            # Add reviewers from command line
            if parsed_args.reviewer:
                for reviewer in parsed_args.reviewer:
                    self.try_add_reviewer(reviewer)
            
            # Add my email if provided
            if parsed_args.myemail:
                self.try_add_reviewer(parsed_args.myemail)
            
            # Read commit message from stdin
            message_lines = sys.stdin.readlines()
            message_lines = [line.rstrip() for line in message_lines]
            
            # Process commit message
            output_lines = self.process_commit_message(message_lines, parsed_args)
            
            # Output processed message
            for line in output_lines:
                print(line)
            
            return 0
            
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
            return 1
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return 1


def main():
    """Main entry point for command line usage"""
    tool = GitAddRevTool()
    sys.exit(tool.run(sys.argv[1:]))


if __name__ == '__main__':
    main()