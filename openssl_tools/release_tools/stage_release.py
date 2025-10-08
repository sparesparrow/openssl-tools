#!/usr/bin/env python3
"""
OpenSSL Stage Release Tool - Python Implementation
Stage OpenSSL releases
"""

import os
import sys
import subprocess
import argparse
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path
import json
import re
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StageReleaseTool:
    """Stage OpenSSL releases"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the Stage Release tool"""
        self.config = self._load_config(config_path)
        
    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration from file or environment"""
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        
        # Default configuration
        return {
            'tools': {
                'release_tools': {
                    'templates_dir': 'templates',
                    'output_dir': 'releases',
                    'backup_dir': 'backups'
                }
            }
        }
    
    def parse_arguments(self, args: List[str]) -> argparse.Namespace:
        """Parse command line arguments"""
        parser = argparse.ArgumentParser(
            description='Stage OpenSSL releases',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  stage-release 3.5.0
  stage-release --pre-release 3.5.0-beta1
  stage-release --security 3.4.1
            """
        )
        
        parser.add_argument('version', help='Version to stage')
        parser.add_argument('--pre-release', action='store_true', help='Pre-release version')
        parser.add_argument('--security', action='store_true', help='Security release')
        parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
        parser.add_argument('--verbose', action='store_true', help='Verbose output')
        parser.add_argument('--backup', action='store_true', help='Create backup before staging')
        
        return parser.parse_args(args)
    
    def validate_version(self, version: str) -> bool:
        """Validate version format"""
        # Check if version matches semantic versioning
        pattern = r'^\d+\.\d+\.\d+(-[a-zA-Z0-9.-]+)?$'
        return bool(re.match(pattern, version))
    
    def get_version_info(self, version: str) -> Dict[str, Any]:
        """Extract version information"""
        parts = version.split('-')
        base_version = parts[0]
        pre_release = parts[1] if len(parts) > 1 else None
        
        major, minor, patch = map(int, base_version.split('.'))
        
        return {
            'full_version': version,
            'base_version': base_version,
            'major': major,
            'minor': minor,
            'patch': patch,
            'pre_release': pre_release,
            'is_pre_release': pre_release is not None
        }
    
    def create_backup(self, version: str) -> bool:
        """Create backup of current state"""
        try:
            backup_dir = os.path.join(self.config['tools']['release_tools']['backup_dir'], version)
            os.makedirs(backup_dir, exist_ok=True)
            
            # Create git archive
            archive_path = os.path.join(backup_dir, f"openssl-{version}-backup.tar.gz")
            subprocess.run(['git', 'archive', '--format=tar.gz', '--output', archive_path, 'HEAD'], check=True)
            
            logger.info(f"Backup created: {archive_path}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create backup: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error creating backup: {e}")
            return False
    
    def update_version_files(self, version_info: Dict[str, Any]) -> bool:
        """Update version-related files"""
        try:
            # Update VERSION.dat
            self._update_version_dat(version_info)
            
            # Update other version files
            self._update_other_version_files(version_info)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update version files: {e}")
            return False
    
    def _update_version_dat(self, version_info: Dict[str, Any]) -> None:
        """Update VERSION.dat file"""
        version_dat_path = 'VERSION.dat'
        
        if not os.path.exists(version_dat_path):
            logger.warning("VERSION.dat not found, creating it")
            with open(version_dat_path, 'w') as f:
                f.write(f"MAJOR={version_info['major']}\n")
                f.write(f"MINOR={version_info['minor']}\n")
                f.write(f"PATCH={version_info['patch']}\n")
        else:
            # Update existing file
            with open(version_dat_path, 'r') as f:
                content = f.read()
            
            content = re.sub(r'MAJOR=\d+', f"MAJOR={version_info['major']}", content)
            content = re.sub(r'MINOR=\d+', f"MINOR={version_info['minor']}", content)
            content = re.sub(r'PATCH=\d+', f"PATCH={version_info['patch']}", content)
            
            with open(version_dat_path, 'w') as f:
                f.write(content)
    
    def _update_other_version_files(self, version_info: Dict[str, Any]) -> None:
        """Update other version-related files"""
        # Update CHANGES.md
        self._update_changes_md(version_info)
        
        # Update NEWS.md
        self._update_news_md(version_info)
        
        # Update README.md
        self._update_readme_md(version_info)
    
    def _update_changes_md(self, version_info: Dict[str, Any]) -> None:
        """Update CHANGES.md file"""
        changes_path = 'CHANGES.md'
        
        if not os.path.exists(changes_path):
            logger.warning("CHANGES.md not found")
            return
        
        # Add version header if not present
        with open(changes_path, 'r') as f:
            content = f.read()
        
        version_header = f"Changes between {version_info['base_version']} and previous versions"
        
        if version_header not in content:
            # Add version header at the beginning
            content = f"{version_header}\n{'=' * len(version_header)}\n\n{content}"
            
            with open(changes_path, 'w') as f:
                f.write(content)
    
    def _update_news_md(self, version_info: Dict[str, Any]) -> None:
        """Update NEWS.md file"""
        news_path = 'NEWS.md'
        
        if not os.path.exists(news_path):
            logger.warning("NEWS.md not found")
            return
        
        # Add version entry if not present
        with open(news_path, 'r') as f:
            content = f.read()
        
        version_entry = f"OpenSSL {version_info['full_version']}"
        
        if version_entry not in content:
            # Add version entry at the beginning
            content = f"{version_entry}\n{'=' * len(version_entry)}\n\n{content}"
            
            with open(news_path, 'w') as f:
                f.write(content)
    
    def _update_readme_md(self, version_info: Dict[str, Any]) -> None:
        """Update README.md file"""
        readme_path = 'README.md'
        
        if not os.path.exists(readme_path):
            logger.warning("README.md not found")
            return
        
        # Update version references in README
        with open(readme_path, 'r') as f:
            content = f.read()
        
        # Update version references
        content = re.sub(r'OpenSSL \d+\.\d+\.\d+', f"OpenSSL {version_info['base_version']}", content)
        
        with open(readme_path, 'w') as f:
            f.write(content)
    
    def run_tests(self, version_info: Dict[str, Any]) -> bool:
        """Run tests for the release"""
        try:
            logger.info("Running tests...")
            
            # Configure OpenSSL
            subprocess.run(['./config'], check=True)
            
            # Build OpenSSL
            subprocess.run(['make'], check=True)
            
            # Run tests
            subprocess.run(['make', 'test'], check=True)
            
            logger.info("Tests passed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Tests failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error running tests: {e}")
            return False
    
    def create_release_artifacts(self, version_info: Dict[str, Any]) -> bool:
        """Create release artifacts"""
        try:
            output_dir = self.config['tools']['release_tools']['output_dir']
            os.makedirs(output_dir, exist_ok=True)
            
            # Create source tarball
            tarball_name = f"openssl-{version_info['full_version']}.tar.gz"
            tarball_path = os.path.join(output_dir, tarball_name)
            
            subprocess.run(['git', 'archive', '--format=tar.gz', '--output', tarball_path, 'HEAD'], check=True)
            
            logger.info(f"Created tarball: {tarball_path}")
            
            # Create checksums
            self._create_checksums(tarball_path)
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create release artifacts: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error creating artifacts: {e}")
            return False
    
    def _create_checksums(self, file_path: str) -> None:
        """Create checksums for a file"""
        try:
            # SHA256 checksum
            result = subprocess.run(['sha256sum', file_path], capture_output=True, text=True, check=True)
            sha256_checksum = result.stdout.split()[0]
            
            checksum_file = f"{file_path}.sha256"
            with open(checksum_file, 'w') as f:
                f.write(f"{sha256_checksum}  {os.path.basename(file_path)}\n")
            
            logger.info(f"Created checksum: {checksum_file}")
            
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to create checksums: {e}")
    
    def generate_release_notes(self, version_info: Dict[str, Any]) -> bool:
        """Generate release notes"""
        try:
            output_dir = self.config['tools']['release_tools']['output_dir']
            notes_file = os.path.join(output_dir, f"RELEASE_NOTES_{version_info['full_version']}.md")
            
            with open(notes_file, 'w') as f:
                f.write(f"# OpenSSL {version_info['full_version']} Release Notes\n\n")
                f.write(f"Release Date: {datetime.now().strftime('%Y-%m-%d')}\n\n")
                
                if version_info['is_pre_release']:
                    f.write("**This is a pre-release version.**\n\n")
                
                f.write("## Changes\n\n")
                f.write("See CHANGES.md for detailed change log.\n\n")
                f.write("## Download\n\n")
                f.write(f"- Source: openssl-{version_info['full_version']}.tar.gz\n")
                f.write(f"- Checksum: openssl-{version_info['full_version']}.tar.gz.sha256\n\n")
                f.write("## Installation\n\n")
                f.write("See INSTALL.md for installation instructions.\n")
            
            logger.info(f"Generated release notes: {notes_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to generate release notes: {e}")
            return False
    
    def run(self, args: List[str]) -> int:
        """Main entry point"""
        try:
            parsed_args = self.parse_arguments(args)
            
            # Validate version
            if not self.validate_version(parsed_args.version):
                logger.error(f"Invalid version format: {parsed_args.version}")
                return 1
            
            # Get version info
            version_info = self.get_version_info(parsed_args.version)
            
            logger.info(f"Staging release {parsed_args.version}")
            logger.info(f"Version info: {version_info}")
            
            if parsed_args.dry_run:
                logger.info("Dry run mode - no changes will be made")
                return 0
            
            # Create backup if requested
            if parsed_args.backup:
                if not self.create_backup(parsed_args.version):
                    logger.error("Failed to create backup")
                    return 1
            
            # Update version files
            if not self.update_version_files(version_info):
                logger.error("Failed to update version files")
                return 1
            
            # Run tests
            if not self.run_tests(version_info):
                logger.error("Tests failed")
                return 1
            
            # Create release artifacts
            if not self.create_release_artifacts(version_info):
                logger.error("Failed to create release artifacts")
                return 1
            
            # Generate release notes
            if not self.generate_release_notes(version_info):
                logger.error("Failed to generate release notes")
                return 1
            
            logger.info("Release staging completed successfully!")
            return 0
            
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
            return 1
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return 1


def main():
    """Main entry point for command line usage"""
    tool = StageReleaseTool()
    sys.exit(tool.run(sys.argv[1:]))


if __name__ == '__main__':
    main()