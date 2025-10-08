#!/usr/bin/env python3
"""
OpenSSL Copyright Year Tool - Python Implementation
Update copyright years in files
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
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CopyrightYearTool:
    """Update copyright years in files"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the Copyright Year tool"""
        self.config = self._load_config(config_path)
        
    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration from file or environment"""
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        
        # Default configuration
        return {
            'tools': {
                'copyright_year': {
                    'current_year': datetime.now().year,
                    'file_patterns': [
                        '*.c', '*.h', '*.py', '*.pl', '*.sh', '*.md',
                        '*.txt', '*.in', '*.conf', '*.tmpl'
                    ],
                    'exclude_patterns': [
                        '*/test/*', '*/tests/*', '*/doc/*', '*/docs/*',
                        '*/external/*', '*/third_party/*'
                    ]
                }
            }
        }
    
    def parse_arguments(self, args: List[str]) -> argparse.Namespace:
        """Parse command line arguments"""
        parser = argparse.ArgumentParser(
            description='Update copyright years in files',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  copyright-year --year=2024
  copyright-year --dry-run --verbose
  copyright-year --file=src/openssl.c --year=2024
            """
        )
        
        parser.add_argument('--year', type=int, help='Year to set (default: current year)')
        parser.add_argument('--file', help='Specific file to update')
        parser.add_argument('--dry-run', action='store_true', help='Show what would be changed')
        parser.add_argument('--verbose', action='store_true', help='Verbose output')
        parser.add_argument('--exclude', action='append', help='Exclude pattern')
        
        return parser.parse_args(args)
    
    def get_current_year(self) -> int:
        """Get current year"""
        return datetime.now().year
    
    def find_files(self, file_patterns: List[str], exclude_patterns: List[str]) -> List[str]:
        """Find files matching patterns"""
        files = []
        
        try:
            # Use git to find files
            cmd = ['git', 'ls-files']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            all_files = result.stdout.strip().split('\n')
            
            for file_path in all_files:
                if not file_path:
                    continue
                
                # Check if file matches any pattern
                matches_pattern = False
                for pattern in file_patterns:
                    if file_path.endswith(pattern.replace('*', '')) or pattern == '*':
                        matches_pattern = True
                        break
                
                if not matches_pattern:
                    continue
                
                # Check if file should be excluded
                excluded = False
                for exclude_pattern in exclude_patterns:
                    if self._matches_pattern(file_path, exclude_pattern):
                        excluded = True
                        break
                
                if not excluded:
                    files.append(file_path)
            
        except subprocess.CalledProcessError as e:
            logger.warning(f"Could not use git to find files: {e}")
            # Fallback to directory traversal
            files = self._find_files_fallback(file_patterns, exclude_patterns)
        
        return files
    
    def _matches_pattern(self, file_path: str, pattern: str) -> bool:
        """Check if file path matches pattern"""
        # Convert glob pattern to regex
        regex_pattern = pattern.replace('*', '.*').replace('/', '/')
        return bool(re.match(regex_pattern, file_path))
    
    def _find_files_fallback(self, file_patterns: List[str], exclude_patterns: List[str]) -> List[str]:
        """Fallback method to find files"""
        files = []
        
        for root, dirs, filenames in os.walk('.'):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for filename in filenames:
                file_path = os.path.join(root, filename)
                file_path = file_path[2:]  # Remove './' prefix
                
                # Check if file matches any pattern
                matches_pattern = False
                for pattern in file_patterns:
                    if filename.endswith(pattern.replace('*', '')) or pattern == '*':
                        matches_pattern = True
                        break
                
                if not matches_pattern:
                    continue
                
                # Check if file should be excluded
                excluded = False
                for exclude_pattern in exclude_patterns:
                    if self._matches_pattern(file_path, exclude_pattern):
                        excluded = True
                        break
                
                if not excluded:
                    files.append(file_path)
        
        return files
    
    def update_copyright_year(self, file_path: str, target_year: int, dry_run: bool = False) -> bool:
        """Update copyright year in a file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            original_content = content
            
            # Common copyright patterns
            patterns = [
                # Copyright 2023 The OpenSSL Project Authors
                (r'Copyright (\d{4}) The OpenSSL Project Authors', 
                 f'Copyright {target_year} The OpenSSL Project Authors'),
                
                # Copyright 2023-2024 The OpenSSL Project Authors
                (r'Copyright (\d{4})-(\d{4}) The OpenSSL Project Authors',
                 f'Copyright \\1-{target_year} The OpenSSL Project Authors'),
                
                # Copyright (c) 2023 The OpenSSL Project Authors
                (r'Copyright \(c\) (\d{4}) The OpenSSL Project Authors',
                 f'Copyright (c) {target_year} The OpenSSL Project Authors'),
                
                # Copyright (c) 2023-2024 The OpenSSL Project Authors
                (r'Copyright \(c\) (\d{4})-(\d{4}) The OpenSSL Project Authors',
                 f'Copyright (c) \\1-{target_year} The OpenSSL Project Authors'),
                
                # Copyright 2023 OpenSSL Project
                (r'Copyright (\d{4}) OpenSSL Project',
                 f'Copyright {target_year} OpenSSL Project'),
                
                # Copyright 2023-2024 OpenSSL Project
                (r'Copyright (\d{4})-(\d{4}) OpenSSL Project',
                 f'Copyright \\1-{target_year} OpenSSL Project'),
            ]
            
            changes_made = False
            for pattern, replacement in patterns:
                new_content = re.sub(pattern, replacement, content)
                if new_content != content:
                    content = new_content
                    changes_made = True
            
            if changes_made:
                if dry_run:
                    logger.info(f"Would update {file_path}")
                    # Show diff
                    self._show_diff(original_content, content, file_path)
                else:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    logger.info(f"Updated {file_path}")
                
                return True
            else:
                if dry_run:
                    logger.debug(f"No changes needed for {file_path}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to update {file_path}: {e}")
            return False
    
    def _show_diff(self, original: str, updated: str, file_path: str) -> None:
        """Show diff between original and updated content"""
        original_lines = original.split('\n')
        updated_lines = updated.split('\n')
        
        for i, (orig_line, upd_line) in enumerate(zip(original_lines, updated_lines)):
            if orig_line != upd_line:
                logger.info(f"  Line {i+1}:")
                logger.info(f"    - {orig_line}")
                logger.info(f"    + {upd_line}")
    
    def run(self, args: List[str]) -> int:
        """Main entry point"""
        try:
            parsed_args = self.parse_arguments(args)
            
            # Determine target year
            target_year = parsed_args.year or self.get_current_year()
            
            logger.info(f"Updating copyright years to {target_year}")
            
            # Get files to process
            if parsed_args.file:
                files = [parsed_args.file]
            else:
                file_patterns = self.config['tools']['copyright_year']['file_patterns']
                exclude_patterns = self.config['tools']['copyright_year']['exclude_patterns']
                
                if parsed_args.exclude:
                    exclude_patterns.extend(parsed_args.exclude)
                
                files = self.find_files(file_patterns, exclude_patterns)
            
            if not files:
                logger.info("No files found to process")
                return 0
            
            logger.info(f"Found {len(files)} files to process")
            
            # Process files
            updated_count = 0
            for file_path in files:
                if self.update_copyright_year(file_path, target_year, parsed_args.dry_run):
                    updated_count += 1
            
            if parsed_args.dry_run:
                logger.info(f"Dry run complete: {updated_count} files would be updated")
            else:
                logger.info(f"Updated {updated_count} files")
            
            return 0
            
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
            return 1
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return 1


def main():
    """Main entry point for command line usage"""
    tool = CopyrightYearTool()
    sys.exit(tool.run(sys.argv[1:]))


if __name__ == '__main__':
    main()