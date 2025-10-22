#!/usr/bin/env python3
"""
Fix Cache Entries Script
Cleans up duplicate and malformed cache entries in workflow files.
"""

import re
from pathlib import Path


def fix_cache_entries(content: str) -> str:
    """Fix cache entries in workflow content."""
    # Remove duplicate cache entries
    content = re.sub(
        r'cache:\s*[\'"]pip[\'"]\s*\n\s*cache:\s*[\'"]pip[\'"]',
        "cache: 'pip'",
        content,
        flags=re.MULTILINE
    )
    
    # Fix malformed cache entries
    content = re.sub(
        r'cache:\s*[\'"]pip[\'"]+',
        "cache: 'pip'",
        content
    )
    
    # Remove multiple consecutive cache entries
    content = re.sub(
        r'(cache:\s*[\'"]pip[\'"]\s*\n\s*)+',
        "cache: 'pip'\n",
        content,
        flags=re.MULTILINE
    )
    
    return content


def main():
    """Main entry point."""
    workflows_dir = Path('.github/workflows')
    
    for workflow_file in workflows_dir.glob('*.yml'):
        try:
            content = workflow_file.read_text(encoding='utf-8')
            original_content = content
            
            content = fix_cache_entries(content)
            
            if content != original_content:
                workflow_file.write_text(content, encoding='utf-8')
                print(f"✅ Fixed {workflow_file}")
            else:
                print(f"⏭️  No changes needed for {workflow_file}")
                
        except Exception as e:
            print(f"❌ Error fixing {workflow_file}: {e}")


if __name__ == '__main__':
    main()