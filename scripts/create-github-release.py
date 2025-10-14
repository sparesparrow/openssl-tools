#!/usr/bin/env python3
"""
Create a GitHub release for the OpenSSL Tools Conan package
"""

import argparse
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
import requests
from datetime import datetime

def get_git_info():
    """Get Git information"""
    try:
        # Get current commit hash
        commit_result = subprocess.run([
            "git", "rev-parse", "HEAD"
        ], capture_output=True, text=True, check=True)
        commit_hash = commit_result.stdout.strip()[:8]
        
        # Get current branch
        branch_result = subprocess.run([
            "git", "rev-parse", "--abbrev-ref", "HEAD"
        ], capture_output=True, text=True, check=True)
        branch = branch_result.stdout.strip()
        
        # Get version from git describe
        try:
            version_result = subprocess.run([
                "git", "describe", "--tags", "--always", "--dirty"
            ], capture_output=True, text=True, check=True)
            version = version_result.stdout.strip()
        except subprocess.CalledProcessError:
            version = f"0.1.0-{commit_hash}"
        
        return {
            "commit": commit_hash,
            "branch": branch,
            "version": version
        }
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to get Git info: {e}")
        return None

def create_source_archive(output_dir, version):
    """Create a zip archive of the source code"""
    try:
        # Get project root
        project_root = Path(__file__).parent.parent
        
        # Create zip file
        zip_path = output_dir / f"openssl-tools-{version}.zip"
        
        # Files to include
        include_patterns = [
            "*.py",
            "*.toml",
            "*.txt",
            "*.md",
            "*.yml",
            "*.yaml",
            "*.sh",
            "*.cfg",
            "*.conf",
            "*.profile",
            "openssl_tools/**/*",
            "scripts/**/*",
            "conan-profiles/**/*",
            "tests/**/*",
            "docs/**/*"
        ]
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for pattern in include_patterns:
                for file_path in project_root.glob(pattern):
                    if file_path.is_file() and not file_path.name.startswith('.'):
                        arcname = file_path.relative_to(project_root)
                        zipf.write(file_path, arcname)
        
        print(f"✅ Created source archive: {zip_path}")
        return zip_path
        
    except Exception as e:
        print(f"❌ Failed to create source archive: {e}")
        return None

def create_github_release(owner, repo, version, token, zip_path, git_info):
    """Create a GitHub release with the package as an asset"""
    try:
        # GitHub API URL
        url = f"https://api.github.com/repos/{owner}/{repo}/releases"
        
        # Release data
        release_data = {
            "tag_name": f"v{version}",
            "name": f"OpenSSL Tools {version}",
            "body": f"# OpenSSL Tools {version}\n\n"
                   f"Python tools for OpenSSL development with Conan 2.x integration\n\n"
                   f"## Features\n"
                   f"- 🔧 **Review Tools**: Code review and management utilities\n"
                   f"- 🚀 **Release Tools**: Release preparation and announcement tools\n"
                   f"- 📊 **Statistics**: Code analysis and metrics tools\n"
                   f"- 🔗 **GitHub Integration**: Native GitHub API integration\n"
                   f"- 📦 **Conan 2.x**: Modern package management with Conan 2.x\n"
                   f"- 🐍 **Python Environment**: Isolated development environment\n\n"
                   f"## Installation\n"
                   f"```bash\n"
                   f"# Setup Conan environment\n"
                   f"python scripts/setup-openssl-tools-conan.py\n"
                   f"\n"
                   f"# Activate environment\n"
                   f"source conan-dev/activate\n"
                   f"\n"
                   f"# Install package\n"
                   f"conan install openssl-tools/{version}@\n"
                   f"```\n\n"
                   f"## Conan Package\n"
                   f"This release includes a Conan 2.x package for easy integration into C++ projects.\n\n"
                   f"## Build Information\n"
                   f"- **Commit**: {git_info['commit']}\n"
                   f"- **Branch**: {git_info['branch']}\n"
                   f"- **Generated**: {datetime.now().isoformat()}\n\n"
                   f"## Documentation\n"
                   f"See [CONAN-GITHUB-PACKAGES-SETUP.md](CONAN-GITHUB-PACKAGES-SETUP.md) for detailed setup instructions.",
            "draft": False,
            "prerelease": version.endswith(('dev', 'alpha', 'beta', 'rc', 'dirty'))
        }
        
        # Headers
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Create release
        print(f"🚀 Creating GitHub release: {release_data['tag_name']}")
        response = requests.post(url, json=release_data, headers=headers)
        
        if response.status_code == 201:
            release_info = response.json()
            print(f"✅ Created release: {release_info['html_url']}")
            
            # Upload package as asset
            upload_url = release_info['upload_url'].replace('{?name,label}', '')
            
            with open(zip_path, 'rb') as f:
                asset_data = f.read()
            
            asset_headers = {
                "Authorization": f"token {token}",
                "Content-Type": "application/zip"
            }
            
            asset_response = requests.post(
                f"{upload_url}?name={zip_path.name}",
                data=asset_data,
                headers=asset_headers
            )
            
            if asset_response.status_code == 201:
                print(f"✅ Uploaded source archive: {zip_path.name}")
                return True
            else:
                print(f"❌ Failed to upload asset: {asset_response.status_code} - {asset_response.text}")
                return False
                
        else:
            print(f"❌ Failed to create release: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to create GitHub release: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Create GitHub release for OpenSSL Tools")
    parser.add_argument("--github-owner", required=True, help="GitHub owner/username")
    parser.add_argument("--github-repo", required=True, help="GitHub repository name")
    parser.add_argument("--github-token", help="GitHub Personal Access Token")
    parser.add_argument("--version", help="Release version (auto-detected if not provided)")
    
    args = parser.parse_args()
    
    print("🚀 Creating GitHub release for OpenSSL Tools...")
    
    # Get Git info
    git_info = get_git_info()
    if not git_info:
        return 1
    
    version = args.version or git_info["version"]
    print(f"📦 Version: {version}")
    print(f"🔗 Commit: {git_info['commit']}")
    print(f"🌿 Branch: {git_info['branch']}")
    
    # Get GitHub token
    if not args.github_token:
        import getpass
        args.github_token = getpass.getpass("Enter GitHub Personal Access Token: ")
    
    if not args.github_token:
        print("❌ GitHub token is required")
        return 1
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create source archive
        zip_path = create_source_archive(temp_path, version)
        if not zip_path:
            return 1
        
        # Create GitHub release
        success = create_github_release(
            args.github_owner, 
            args.github_repo, 
            version, 
            args.github_token, 
            zip_path,
            git_info
        )
        
        if success:
            print("🎉 Release created successfully!")
            print(f"📦 Release: https://github.com/{args.github_owner}/{args.github_repo}/releases")
            return 0
        else:
            return 1

if __name__ == "__main__":
    sys.exit(main())