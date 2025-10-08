#!/usr/bin/env python3
"""
Update Workflows for Package Upload
Updates existing workflows to include package artifact uploads to multiple registries.
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional


class WorkflowPackageUploadUpdater:
    """Updates workflow files to include package artifact uploads."""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.workflows_dir = repo_root / '.github' / 'workflows'
        
        # Package upload steps template
        self.upload_steps_template = """
      - name: Upload packages to Artifactory
        if: env.ARTIFACTORY_URL != ''
        run: |
          conan remote add artifactory ${{ env.ARTIFACTORY_URL }}/conan-local
          conan user -p ${{ secrets.ARTIFACTORY_PASSWORD }} -r artifactory ${{ secrets.ARTIFACTORY_USERNAME }}
          conan upload "openssl/*" -r=artifactory --all --confirm || true
      
      - name: Upload packages to GitHub Packages
        if: github.event_name == 'push' && github.ref == 'refs/heads/main'
        run: |
          conan remote add github-packages https://maven.pkg.github.com/${{ github.repository }}
          conan user -p ${{ secrets.GITHUB_TOKEN }} -r github-packages ${{ github.actor }}
          conan upload "openssl/*" -r=github-packages --all --confirm || true
      
      - name: Upload build artifacts
        uses: actions/upload-artifact@v4
        with:
          name: openssl-packages-${{ matrix.profile || 'default' }}
          path: |
            ~/.conan2/p/*/p/
          retention-days: 30
"""
    
    def find_workflow_files(self) -> List[Path]:
        """Find workflow files that build packages."""
        if not self.workflows_dir.exists():
            return []
        
        workflow_files = []
        for workflow_file in self.workflows_dir.glob('*.yml'):
            if self._is_package_building_workflow(workflow_file):
                workflow_files.append(workflow_file)
        
        return workflow_files
    
    def _is_package_building_workflow(self, workflow_file: Path) -> bool:
        """Check if a workflow file builds packages."""
        try:
            content = workflow_file.read_text(encoding='utf-8')
            
            # Look for package building indicators
            package_indicators = [
                'conan create',
                'conan build',
                'conan install',
                'conanfile.py',
                'package/',
                '~/.conan2/p/'
            ]
            
            return any(indicator in content for indicator in package_indicators)
            
        except Exception:
            return False
    
    def update_workflow_file(self, workflow_path: Path) -> bool:
        """Update a workflow file to include package uploads."""
        print(f"[UPDATE] Processing: {workflow_path.name}")
        
        try:
            content = workflow_path.read_text(encoding='utf-8')
            original_content = content
            
            # Check if upload steps already exist
            if 'Upload packages to Artifactory' in content:
                print(f"[SKIP] {workflow_path.name} already has package upload steps")
                return False
            
            # Find the right place to insert upload steps
            # Look for existing upload artifact steps or build steps
            upload_insertion_point = self._find_upload_insertion_point(content)
            
            if upload_insertion_point == -1:
                print(f"[WARN] Could not find insertion point in {workflow_path.name}")
                return False
            
            # Insert the upload steps
            lines = content.split('\n')
            lines.insert(upload_insertion_point, self.upload_steps_template)
            
            new_content = '\n'.join(lines)
            
            if new_content != original_content:
                workflow_path.write_text(new_content, encoding='utf-8')
                print(f"[OK] Updated {workflow_path.name} with package upload steps")
                return True
            else:
                print(f"[SKIP] No changes needed for {workflow_path.name}")
                return False
                
        except Exception as e:
            print(f"[ERROR] Failed to update {workflow_path.name}: {e}")
            return False
    
    def _find_upload_insertion_point(self, content: str) -> int:
        """Find the best place to insert upload steps."""
        lines = content.split('\n')
        
        # Look for existing upload artifact steps
        for i, line in enumerate(lines):
            if 'actions/upload-artifact@' in line:
                # Insert after the upload artifact step
                return i + 1
        
        # Look for build steps
        for i, line in enumerate(lines):
            if 'conan create' in line or 'conan build' in line:
                # Insert after the build step
                return i + 1
        
        # Look for job steps section
        for i, line in enumerate(lines):
            if line.strip() == 'steps:' and i < len(lines) - 1:
                # Insert after the steps: line
                return i + 1
        
        return -1
    
    def add_environment_variables(self, workflow_path: Path) -> bool:
        """Add environment variables for package uploads."""
        try:
            content = workflow_path.read_text(encoding='utf-8')
            
            # Check if environment section exists
            if 'env:' in content:
                # Add to existing env section
                env_vars = """
  ARTIFACTORY_URL: ${{ secrets.ARTIFACTORY_URL }}
  ARTIFACTORY_USERNAME: ${{ secrets.ARTIFACTORY_USERNAME }}
  ARTIFACTORY_PASSWORD: ${{ secrets.ARTIFACTORY_PASSWORD }}
"""
                
                # Find the env: line and add variables
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if line.strip() == 'env:':
                        lines.insert(i + 1, env_vars)
                        break
                
                new_content = '\n'.join(lines)
                if new_content != content:
                    workflow_path.write_text(new_content, encoding='utf-8')
                    print(f"[OK] Added environment variables to {workflow_path.name}")
                    return True
            
            return False
            
        except Exception as e:
            print(f"[ERROR] Failed to add environment variables to {workflow_path.name}: {e}")
            return False
    
    def update_all_workflows(self) -> Dict[str, int]:
        """Update all workflow files."""
        workflow_files = self.find_workflow_files()
        
        if not workflow_files:
            print("[WARN] No package building workflow files found")
            return {"updated": 0, "skipped": 0, "errors": 0}
        
        print(f"[INFO] Found {len(workflow_files)} package building workflow files")
        
        results = {"updated": 0, "skipped": 0, "errors": 0}
        
        for workflow_path in workflow_files:
            try:
                # Update workflow with upload steps
                if self.update_workflow_file(workflow_path):
                    results["updated"] += 1
                else:
                    results["skipped"] += 1
                
                # Add environment variables
                self.add_environment_variables(workflow_path)
                
            except Exception as e:
                print(f"[ERROR] Failed to process {workflow_path.name}: {e}")
                results["errors"] += 1
        
        return results
    
    def create_secrets_documentation(self) -> None:
        """Create documentation for required secrets."""
        secrets_doc = """# Required Secrets for Package Upload

This document lists the secrets that need to be configured in GitHub for package upload functionality.

## Artifactory Secrets

- `ARTIFACTORY_URL`: The base URL of your Artifactory instance
  - Example: `https://your-company.jfrog.io`
- `ARTIFACTORY_USERNAME`: Username for Artifactory authentication
- `ARTIFACTORY_PASSWORD`: Password or API key for Artifactory authentication

## GitHub Packages Secrets

- `GITHUB_TOKEN`: Automatically provided by GitHub Actions
- `GITHUB_ACTOR`: Automatically provided by GitHub Actions
- `GITHUB_REPOSITORY`: Automatically provided by GitHub Actions

## Conan Center Secrets (Optional)

- `CONAN_CENTER_USERNAME`: Username for Conan Center
- `CONAN_CENTER_PASSWORD`: Password for Conan Center

## How to Configure Secrets

1. Go to your GitHub repository
2. Click on "Settings" tab
3. Click on "Secrets and variables" → "Actions"
4. Click "New repository secret"
5. Add each secret with the appropriate value

## Environment Variables

The following environment variables are used in workflows:

- `ARTIFACTORY_URL`: Base URL for Artifactory
- `ARTIFACTORY_USERNAME`: Artifactory username
- `ARTIFACTORY_PASSWORD`: Artifactory password
- `ARTIFACTORY_REPO`: Artifactory repository name (default: conan-local)

## Package Upload Behavior

- Packages are uploaded to Artifactory if `ARTIFACTORY_URL` is set
- Packages are uploaded to GitHub Packages on pushes to main branch
- Packages are uploaded to Conan Center only when explicitly enabled
- All uploads are non-blocking (failures don't stop the workflow)
"""
        
        doc_path = self.repo_root / "docs" / "package-upload-secrets.md"
        doc_path.parent.mkdir(parents=True, exist_ok=True)
        doc_path.write_text(secrets_doc)
        print(f"[INFO] Created secrets documentation: {doc_path}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Update workflows for package upload")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed without making changes")
    parser.add_argument("--create-docs", action="store_true", help="Create documentation for required secrets")
    
    args = parser.parse_args()
    
    # Get repository root
    repo_root = Path(__file__).parent.parent.parent
    
    # Initialize updater
    updater = WorkflowPackageUploadUpdater(repo_root)
    
    if args.create_docs:
        updater.create_secrets_documentation()
        return 0
    
    if args.dry_run:
        print("[DRY-RUN] Would update the following workflow files:")
        workflow_files = updater.find_workflow_files()
        for workflow_path in workflow_files:
            print(f"  - {workflow_path.name}")
        return 0
    
    # Update all workflows
    results = updater.update_all_workflows()
    
    print(f"\n[SUMMARY] Update results:")
    print(f"  Updated: {results['updated']}")
    print(f"  Skipped: {results['skipped']}")
    print(f"  Errors: {results['errors']}")
    
    # Create documentation
    updater.create_secrets_documentation()
    
    return 0 if results['errors'] == 0 else 1


if __name__ == '__main__':
    sys.exit(main())