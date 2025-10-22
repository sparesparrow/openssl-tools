#!/usr/bin/env python3
"""
Workflow Update Script
Updates all GitHub Actions workflows to use standardized Python and Conan profile usage.

This script:
1. Updates all actions/setup-python@v4/v5 to v6
2. Replaces python3 commands with python
3. Updates profile names to match conan-dev/profiles/ exactly
4. Adds cache: 'pip' to Python setup actions
5. Replaces conan setup scripts with our standardized script
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple


class WorkflowUpdater:
    """Updates GitHub Actions workflows for standardization."""
    
    def __init__(self):
        self.workflows_dir = Path('.github/workflows')
        self.profiles_dir = Path('conan-dev/profiles')
        
    def get_available_profiles(self) -> List[str]:
        """Get list of available profile names from conan-dev/profiles/."""
        if not self.profiles_dir.exists():
            return []
        
        profiles = []
        for profile_file in self.profiles_dir.glob('*.profile'):
            profiles.append(profile_file.stem)
        
        return sorted(profiles)
    
    def update_python_setup_actions(self, content: str) -> str:
        """Update Python setup actions to use v6 and add cache."""
        # Update actions/setup-python@v4 or v5 to v6
        content = re.sub(
            r'uses: actions/setup-python@v[45]',
            'uses: actions/setup-python@v6',
            content
        )
        
        # Add cache: 'pip' to Python setup actions that don't already have it
        # First, clean up any duplicate cache entries
        content = re.sub(
            r'cache:\s*[\'"]pip[\'"]\s*\n\s*cache:\s*[\'"]pip[\'"]',
            "cache: 'pip'",
            content
        )
        
        # Then add cache to actions that don't have it
        content = re.sub(
            r'(uses: actions/setup-python@v6\n\s+with:\n\s+python-version: [^\n]+)(?!\n\s+cache:)',
            r'\1\n          cache: \'pip\'',
            content
        )
        
        return content
    
    def update_python_commands(self, content: str) -> str:
        """Replace python3 commands with python."""
        # Replace python3 with python in run commands
        content = re.sub(r'\bpython3\b', 'python', content)
        
        return content
    
    def update_conan_setup_scripts(self, content: str) -> str:
        """Replace conan setup scripts with our standardized script."""
        # Replace various conan setup patterns
        patterns = [
            r'python scripts/ci/conan_automation\.py setup',
            r'python scripts/setup-conan-python-env\.py',
            r'python scripts/conan/conan_cli\.py setup',
        ]
        
        for pattern in patterns:
            content = re.sub(pattern, 'python scripts/setup-ci-environment.py', content)
        
        return content
    
    def update_python_executable_path(self, content: str) -> str:
        """Update Python executable path to use conan-dev Python."""
        # Replace python commands with conan-dev Python path
        content = re.sub(
            r'\bpython\s+',
            'conan-dev/venv/bin/python ',
            content
        )
        
        return content
    
    def update_profile_names(self, content: str, available_profiles: List[str]) -> str:
        """Update profile names to match available profiles exactly."""
        # Common profile name mappings
        profile_mappings = {
            'hermetic-linux-gcc11': 'linux-gcc11',
            'hermetic-linux-clang15': 'linux-clang15',
            'windows-vs2022': 'windows-msvc2022',
            'macos-clang14': 'macos-clang14',  # This one should already be correct
        }
        
        for old_name, new_name in profile_mappings.items():
            if new_name in available_profiles:
                content = re.sub(rf'\b{re.escape(old_name)}\b', new_name, content)
        
        return content
    
    def add_conan_home_env(self, content: str) -> str:
        """Add CONAN_USER_HOME environment variable to workflows that use Conan."""
        # Check if workflow uses Conan
        if 'conan' in content.lower() and 'CONAN_USER_HOME' not in content:
            # Add env section after the workflow name
            env_section = """env:
  CONAN_USER_HOME: ${{ github.workspace }}/.conan2
  CONAN_COLOR_DISPLAY: 1
  CLICOLOR_FORCE: 1
  CLICOLOR: 1

"""
            # Find the first job and add env before it
            content = re.sub(
                r'(jobs:\s*\n)',
                r'\1' + env_section,
                content
            )
        
        return content
    
    def update_workflow_file(self, file_path: Path, available_profiles: List[str]) -> bool:
        """Update a single workflow file."""
        print(f"Updating {file_path}...")
        
        try:
            content = file_path.read_text(encoding='utf-8')
            original_content = content
            
            # Apply all updates
            content = self.update_python_setup_actions(content)
            content = self.update_python_commands(content)
            content = self.update_conan_setup_scripts(content)
            content = self.update_python_executable_path(content)
            content = self.update_profile_names(content, available_profiles)
            content = self.add_conan_home_env(content)
            
            # Only write if content changed
            if content != original_content:
                file_path.write_text(content, encoding='utf-8')
                print(f"✅ Updated {file_path}")
                return True
            else:
                print(f"⏭️  No changes needed for {file_path}")
                return False
                
        except Exception as e:
            print(f"❌ Error updating {file_path}: {e}")
            return False
    
    def update_all_workflows(self) -> None:
        """Update all workflow files."""
        print("🔄 Updating all GitHub Actions workflows...")
        
        available_profiles = self.get_available_profiles()
        print(f"Available profiles: {available_profiles}")
        
        if not self.workflows_dir.exists():
            print(f"❌ Workflows directory not found: {self.workflows_dir}")
            return
        
        updated_count = 0
        total_count = 0
        
        for workflow_file in self.workflows_dir.glob('*.yml'):
            if workflow_file.name.startswith('templates/'):
                continue  # Skip template files
                
            total_count += 1
            if self.update_workflow_file(workflow_file, available_profiles):
                updated_count += 1
        
        for workflow_file in self.workflows_dir.glob('*.yaml'):
            if workflow_file.name.startswith('templates/'):
                continue  # Skip template files
                
            total_count += 1
            if self.update_workflow_file(workflow_file, available_profiles):
                updated_count += 1
        
        print(f"\n📊 Summary:")
        print(f"Total workflows processed: {total_count}")
        print(f"Workflows updated: {updated_count}")
        print(f"Workflows unchanged: {total_count - updated_count}")


def main():
    """Main entry point."""
    updater = WorkflowUpdater()
    updater.update_all_workflows()


if __name__ == '__main__':
    main()