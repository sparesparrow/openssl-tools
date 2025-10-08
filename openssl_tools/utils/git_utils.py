#!/usr/bin/env python3
"""
Git utilities for OpenSSL tools
"""

import os
import subprocess
import logging
from typing import List, Optional, Dict, Any

logger = logging.getLogger(__name__)


class GitUtils:
    """Git utility functions"""
    
    @staticmethod
    def get_current_branch() -> Optional[str]:
        """Get current git branch"""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None
    
    @staticmethod
    def get_remote_url(remote: str = 'origin') -> Optional[str]:
        """Get remote URL"""
        try:
            result = subprocess.run(
                ['git', 'remote', 'get-url', remote],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None
    
    @staticmethod
    def get_commits_in_range(commit_range: str) -> List[Dict[str, Any]]:
        """Get commits in range"""
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
    
    @staticmethod
    def get_commit_message(commit_hash: str) -> str:
        """Get commit message"""
        try:
            result = subprocess.run(
                ['git', 'show', '--pretty=format:%B', '--no-patch', commit_hash],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return ""
    
    @staticmethod
    def is_git_repository() -> bool:
        """Check if current directory is a git repository"""
        try:
            subprocess.run(['git', 'rev-parse', '--git-dir'], 
                         capture_output=True, check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    @staticmethod
    def get_git_config(key: str) -> Optional[str]:
        """Get git configuration value"""
        try:
            result = subprocess.run(
                ['git', 'config', '--get', key],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None