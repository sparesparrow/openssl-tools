#!/usr/bin/env python3
"""
Update Workflows for Fuzz Corpora
Replaces git submodule approach with Conan package in all workflow files.
"""

import os
import re
from pathlib import Path
from typing import Dict, List


class WorkflowUpdater:
    """Updates workflow files to use Conan instead of git submodule."""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.workflows_dir = repo_root / '.github' / 'workflows'
        
        # Profile mapping for different platforms
        self.profile_mapping = {
            'ubuntu': 'linux-gcc11',
            'windows': 'windows-msvc2022',
            'macos': 'macos-clang14',
            'default': 'linux-gcc11'
        }
    
    def find_workflow_files(self) -> List[Path]:
        """Find all workflow files."""
        if not self.workflows_dir.exists():
            print(f"[WARN] Workflows directory not found: {self.workflows_dir}")
            return []
        
        yml_files = list(self.workflows_dir.glob('*.yml'))
        yaml_files = list(self.workflows_dir.glob('*.yaml'))
        all_files = yml_files + yaml_files
        
        print(f"[INFO] Found {len(yml_files)} .yml files and {len(yaml_files)} .yaml files")
        return all_files
    
    def detect_platform_from_workflow(self, workflow_content: str) -> str:
        """Detect platform from workflow content."""
        if 'windows' in workflow_content.lower():
            return 'windows'
        elif 'macos' in workflow_content.lower():
            return 'macos'
        elif 'ubuntu' in workflow_content.lower():
            return 'ubuntu'
        else:
            return 'default'
    
    def update_workflow_file(self, workflow_path: Path) -> bool:
        """Update a single workflow file."""
        print(f"[UPDATE] Processing: {workflow_path.name}")
        
        try:
            # Read the workflow file
            content = workflow_path.read_text(encoding='utf-8')
            original_content = content
            
            # Detect platform
            platform = self.detect_platform_from_workflow(content)
            profile = self.profile_mapping.get(platform, 'linux-gcc11')
            
            # Replace git submodule commands
            patterns = [
                (r'git submodule update --init --depth 1 fuzz/corpora', 
                 f'python scripts/setup-fuzz-corpora.py --profile {profile}'),
                (r'checkout fuzz/corpora submodule', 
                 'setup fuzz/corpora via Conan'),
                (r'checkout fuzz/corpora', 
                 'setup fuzz/corpora via Conan')
            ]
            
            for pattern, replacement in patterns:
                content = re.sub(pattern, replacement, content)
            
            # Check if any changes were made
            if content != original_content:
                # Write the updated content
                workflow_path.write_text(content, encoding='utf-8')
                print(f"[OK] Updated {workflow_path.name} with profile: {profile}")
                return True
            else:
                print(f"[SKIP] No fuzz/corpora references found in {workflow_path.name}")
                return False
                
        except Exception as e:
            print(f"[ERROR] Failed to update {workflow_path.name}: {e}")
            return False
    
    def update_all_workflows(self) -> Dict[str, int]:
        """Update all workflow files."""
        workflow_files = self.find_workflow_files()
        
        if not workflow_files:
            print("[WARN] No workflow files found")
            return {"updated": 0, "skipped": 0, "errors": 0}
        
        print(f"[INFO] Found {len(workflow_files)} workflow files")
        
        results = {"updated": 0, "skipped": 0, "errors": 0}
        
        for workflow_path in workflow_files:
            try:
                if self.update_workflow_file(workflow_path):
                    results["updated"] += 1
                else:
                    results["skipped"] += 1
            except Exception as e:
                print(f"[ERROR] Failed to process {workflow_path.name}: {e}")
                results["errors"] += 1
        
        return results
    
    def verify_updates(self) -> bool:
        """Verify that updates were applied correctly."""
        print("\n[VERIFY] Verifying updates...")
        
        workflow_files = self.find_workflow_files()
        remaining_submodule_refs = 0
        
        for workflow_path in workflow_files:
            try:
                content = workflow_path.read_text(encoding='utf-8')
                
                # Check for remaining git submodule references
                if 'git submodule update --init --depth 1 fuzz/corpora' in content:
                    print(f"[WARN] Found remaining submodule reference in {workflow_path.name}")
                    remaining_submodule_refs += 1
                
                # Check for Conan setup references
                if 'setup-fuzz-corpora.py' in content:
                    print(f"[OK] Found Conan setup in {workflow_path.name}")
                
            except Exception as e:
                print(f"[ERROR] Failed to verify {workflow_path.name}: {e}")
        
        if remaining_submodule_refs == 0:
            print("[SUCCESS] All workflow files updated successfully")
            return True
        else:
            print(f"[WARN] {remaining_submodule_refs} workflow files still have submodule references")
            return False


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Update workflows to use Conan for fuzz corpora")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed without making changes")
    parser.add_argument("--verify-only", action="store_true", help="Only verify current state")
    
    args = parser.parse_args()
    
    # Get repository root
    repo_root = Path(__file__).parent.parent.parent
    
    # Initialize updater
    updater = WorkflowUpdater(repo_root)
    
    if args.verify_only:
        success = updater.verify_updates()
        return 0 if success else 1
    
    if args.dry_run:
        print("[DRY-RUN] Would update the following workflow files:")
        workflow_files = updater.find_workflow_files()
        for workflow_path in workflow_files:
            content = workflow_path.read_text(encoding='utf-8')
            if 'git submodule update --init --depth 1 fuzz/corpora' in content:
                platform = updater.detect_platform_from_workflow(content)
                profile = updater.profile_mapping.get(platform, 'linux-gcc11')
                print(f"  - {workflow_path.name} (profile: {profile})")
        return 0
    
    # Update all workflows
    results = updater.update_all_workflows()
    
    print(f"\n[SUMMARY] Update results:")
    print(f"  Updated: {results['updated']}")
    print(f"  Skipped: {results['skipped']}")
    print(f"  Errors: {results['errors']}")
    
    # Verify updates
    success = updater.verify_updates()
    
    return 0 if success else 1


if __name__ == '__main__':
    import sys
    sys.exit(main())