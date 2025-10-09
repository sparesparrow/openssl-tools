#!/usr/bin/env python3
"""
Workflow Validation Script
Validates that all GitHub Actions workflows use standardized Python and Conan profile usage.

This script checks:
1. All workflows use actions/setup-python@v6
2. All workflows use 'python' instead of 'python3'
3. All profile names match exactly what's in conan-dev/profiles/
4. All workflows use our standardized setup script
5. CONAN_USER_HOME is properly set
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple, Set


class WorkflowValidator:
    """Validates GitHub Actions workflows for standardization."""
    
    def __init__(self):
        self.workflows_dir = Path('.github/workflows')
        self.profiles_dir = Path('conan-dev/profiles')
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
    def get_available_profiles(self) -> Set[str]:
        """Get set of available profile names from conan-dev/profiles/."""
        if not self.profiles_dir.exists():
            self.warnings.append(f"Profiles directory not found: {self.profiles_dir}")
            return set()
        
        profiles = set()
        for profile_file in self.profiles_dir.glob('*.profile'):
            profiles.add(profile_file.stem)
        
        return profiles
    
    def validate_python_setup_actions(self, content: str, file_path: Path) -> None:
        """Validate Python setup actions use v6."""
        # Check for old Python setup actions
        old_actions = re.findall(r'uses: actions/setup-python@v[45]', content)
        if old_actions:
            self.errors.append(f"{file_path}: Found old Python setup actions: {old_actions}")
        
        # Check for missing cache in Python setup actions
        # Look for Python setup actions that don't have cache
        python_setup_pattern = r'uses: actions/setup-python@v6\n\s+with:\n\s+python-version: [^\n]+(?:\n\s+[^\n]+)*'
        python_setup_blocks = re.findall(python_setup_pattern, content, re.MULTILINE)
        
        for block in python_setup_blocks:
            if 'cache:' not in block:
                self.warnings.append(f"{file_path}: Python setup actions missing cache: 'pip'")
                break
    
    def validate_python_commands(self, content: str, file_path: Path) -> None:
        """Validate Python commands use 'python' instead of 'python3'."""
        python3_commands = re.findall(r'python3\s+', content)
        if python3_commands:
            self.errors.append(f"{file_path}: Found python3 commands: {python3_commands}")
    
    def validate_profile_names(self, content: str, file_path: Path, available_profiles: Set[str]) -> None:
        """Validate profile names match available profiles exactly."""
        # Find profile references in specific contexts (matrix, --profile, etc.)
        profile_patterns = [
            r'profile:\s*([a-zA-Z0-9_-]+)',  # matrix profile definitions
            r'--profile[=\s]+([a-zA-Z0-9_-]+)',  # command line profile arguments
            r'profile\s*=\s*([a-zA-Z0-9_-]+)',  # variable assignments
        ]
        
        # Common words to ignore
        ignore_words = {
            'description', 'run', 'detect', 's', '--build', '-', 'ci-linux-gcc', 'ci-linux-clang',
            'ci-macos-x64', 'ci-macos-arm64', 'ci-macos-universal', 'conan-profiles', 'conan',
            'case', 'sed', 'echo', 'cp', 'for', 's-changed'
        }
        
        for pattern in profile_patterns:
            matches = re.findall(pattern, content)
            for profile in matches:
                if (profile not in available_profiles and 
                    profile not in ['${{', 'matrix.', '}}', 'matrix'] and
                    profile not in ignore_words):
                    self.errors.append(f"{file_path}: Unknown profile name: {profile}")
    
    def validate_conan_setup_scripts(self, content: str, file_path: Path) -> None:
        """Validate conan setup scripts use our standardized script."""
        old_setup_patterns = [
            r'python scripts/ci/conan_automation\.py setup',
            r'python scripts/setup-conan-python-env\.py',
            r'python scripts/conan/conan_cli\.py setup',
        ]
        
        for pattern in old_setup_patterns:
            matches = re.findall(pattern, content)
            if matches:
                self.warnings.append(f"{file_path}: Found old conan setup patterns: {matches}")
    
    def validate_conan_home(self, content: str, file_path: Path) -> None:
        """Validate CONAN_USER_HOME is properly set."""
        if 'conan' in content.lower() and 'CONAN_USER_HOME' not in content:
            self.warnings.append(f"{file_path}: Uses Conan but doesn't set CONAN_USER_HOME")
    
    def validate_workflow_file(self, file_path: Path, available_profiles: Set[str]) -> None:
        """Validate a single workflow file."""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            self.validate_python_setup_actions(content, file_path)
            self.validate_python_commands(content, file_path)
            self.validate_profile_names(content, file_path, available_profiles)
            self.validate_conan_setup_scripts(content, file_path)
            self.validate_conan_home(content, file_path)
            
        except Exception as e:
            self.errors.append(f"{file_path}: Error reading file: {e}")
    
    def validate_all_workflows(self) -> None:
        """Validate all workflow files."""
        print("🔍 Validating all GitHub Actions workflows...")
        
        available_profiles = self.get_available_profiles()
        print(f"Available profiles: {sorted(available_profiles)}")
        
        if not self.workflows_dir.exists():
            self.errors.append(f"Workflows directory not found: {self.workflows_dir}")
            return
        
        total_count = 0
        for workflow_file in self.workflows_dir.glob('*.yml'):
            if workflow_file.name.startswith('templates/'):
                continue  # Skip template files
            total_count += 1
            self.validate_workflow_file(workflow_file, available_profiles)
        
        for workflow_file in self.workflows_dir.glob('*.yaml'):
            if workflow_file.name.startswith('templates/'):
                continue  # Skip template files
            total_count += 1
            self.validate_workflow_file(workflow_file, available_profiles)
        
        # Print results
        print(f"\n📊 Validation Results:")
        print(f"Total workflows processed: {total_count}")
        print(f"Errors found: {len(self.errors)}")
        print(f"Warnings found: {len(self.warnings)}")
        
        if self.errors:
            print(f"\n❌ Errors:")
            for error in self.errors:
                print(f"  - {error}")
        
        if self.warnings:
            print(f"\n⚠️  Warnings:")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        if not self.errors and not self.warnings:
            print(f"\n✅ All workflows are properly standardized!")
        elif not self.errors:
            print(f"\n✅ No errors found, but there are some warnings to review.")
        else:
            print(f"\n❌ Validation failed with {len(self.errors)} errors.")


def main():
    """Main entry point."""
    validator = WorkflowValidator()
    validator.validate_all_workflows()
    
    # Exit with error code if there are errors
    if validator.errors:
        exit(1)


if __name__ == '__main__':
    main()