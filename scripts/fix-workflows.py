#!/usr/bin/env python3
"""Fix common GitHub workflow issues"""

import os
import re
import yaml
import glob
from pathlib import Path

def fix_workflow_file(filepath):
    """Fix a single workflow file"""
    print(f"Processing: {filepath}")
    
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            original_content = content
        
        # Fix 1: Update action versions
        fixes = [
            ('actions/checkout@v3', 'actions/checkout@v4'),
            ('actions/setup-python@v4', 'actions/setup-python@v5'),
            ('actions/upload-artifact@v3', 'actions/upload-artifact@v4'),
        ]
        
        for old, new in fixes:
            if old in content:
                content = content.replace(old, new)
                print(f"  Updated: {old} -> {new}")
        
        # Fix 2: Add permissions if missing
        if 'permissions:' not in content and 'jobs:' in content:
            content = content.replace('jobs:', 'permissions:\n  contents: read\n\njobs:')
            print("  Added: permissions")
        
        # Fix 3: Add timeout if missing
        if 'timeout-minutes:' not in content and 'runs-on:' in content:
            content = re.sub(r'(runs-on: [^\n]+)', r'\1\n    timeout-minutes: 30', content)
            print("  Added: timeout")
        
        # Write back if changed
        if content != original_content:
            with open(filepath, 'w') as f:
                f.write(content)
            return True
        return False
        
    except Exception as e:
        print(f"  Error: {e}")
        return False

def main():
    """Main function"""
    # Change to repo root if in scripts dir
    if os.path.basename(os.getcwd()) == 'scripts':
        os.chdir('..')
    
    workflow_files = glob.glob('.github/workflows/*.yml') + glob.glob('.github/workflows/*.yaml')
    
    print(f"Found {len(workflow_files)} workflow files")
    
    fixed_count = 0
    for filepath in workflow_files:
        if fix_workflow_file(filepath):
            fixed_count += 1
    
    print(f"\nFixed {fixed_count} workflow files")
    return 0

if __name__ == '__main__':
    exit(main())
