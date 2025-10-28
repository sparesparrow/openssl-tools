#!/usr/bin/env python3
"""
Secrets and Variables Audit Script for OpenSSL Tools
This script helps identify and configure required secrets and variables.
"""

import os
import re
import glob
import yaml
from pathlib import Path


def find_secret_references():
    """Find all secret and variable references in workflows."""
    secrets = set()
    variables = set()
    
    workflow_files = glob.glob('.github/workflows/*.yml') + glob.glob('.github/workflows/*.yaml')
    
    for workflow_file in workflow_files:
        try:
            with open(workflow_file, 'r') as f:
                content = f.read()
                
            # Find secrets.* references
            secret_matches = re.findall(r'secrets\.([A-Z_][A-Z0-9_]*)', content)
            secrets.update(secret_matches)
            
            # Find vars.* references
            var_matches = re.findall(r'vars\.([A-Z_][A-Z0-9_]*)', content)
            variables.update(var_matches)
            
        except Exception as e:
            print(f"Error reading {workflow_file}: {e}")
    
    return sorted(secrets), sorted(variables)


def get_required_secrets():
    """Define required secrets based on OpenSSL tools workflows."""
    return {
        'GITHUB_TOKEN': {
            'description': 'GitHub Actions token (automatically provided)',
            'required': True,
            'scope': 'repo, packages:write',
            'example': 'ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
        },
        'ARTIFACTORY_USERNAME': {
            'description': 'JFrog Artifactory username for package publishing',
            'required': False,
            'scope': 'Artifactory access',
            'example': 'your-email@domain.com'
        },
        'ARTIFACTORY_PASSWORD': {
            'description': 'JFrog Artifactory password/token for package publishing',
            'required': False,
            'scope': 'Artifactory write access',
            'example': 'your-artifactory-token'
        },
        'CLOUDSMITH_API_KEY': {
            'description': 'Cloudsmith API key for Conan package publishing',
            'required': False,
            'scope': 'Cloudsmith write access',
            'example': 'your-cloudsmith-api-key'
        },
        'COVERITY_TOKEN': {
            'description': 'Synopsys Coverity token for static analysis',
            'required': False,
            'scope': 'Coverity analysis',
            'example': 'your-coverity-token'
        }
    }


def get_required_variables():
    """Define required repository variables."""
    return {
        'CONAN_VERSION': {
            'description': 'Conan version to use in workflows',
            'default': '2.0.17',
            'example': '2.0.17'
        },
        'PYTHON_VERSION': {
            'description': 'Python version to use in workflows',
            'default': '3.12',
            'example': '3.12'
        },
        'ARTIFACTORY_URL': {
            'description': 'Base URL for JFrog Artifactory instance',
            'default': '',
            'example': 'https://yourdomain.jfrog.io/artifactory'
        },
        'CONAN_REPOSITORY_NAME': {
            'description': 'Name of the Conan repository',
            'default': 'sparesparrow-conan',
            'example': 'sparesparrow-conan'
        },
        'CONAN_REPOSITORY_URL': {
            'description': 'URL of the Conan repository',
            'default': 'https://conan.cloudsmith.io/sparesparrow-conan/openssl-conan/',
            'example': 'https://conan.cloudsmith.io/your-org/your-repo/'
        },
        'GITHUB_PACKAGES_URL': {
            'description': 'GitHub Packages Maven URL',
            'default': '',
            'example': 'https://maven.pkg.github.com/your-org/your-repo'
        }
    }


def audit_current_configuration():
    """Audit current secrets and variables configuration."""
    print("🔍 OpenSSL Tools Security Configuration Audit")
    print("=" * 50)
    
    found_secrets, found_variables = find_secret_references()
    required_secrets = get_required_secrets()
    required_variables = get_required_variables()
    
    print("\n📊 Secrets Analysis:")
    print("-" * 20)
    
    for secret_name in found_secrets:
        status = "✅ Known" if secret_name in required_secrets else "⚠️  Unknown"
        required = "Required" if required_secrets.get(secret_name, {}).get('required', False) else "Optional"
        print(f"{status} {secret_name} ({required})")
        
        if secret_name in required_secrets:
            desc = required_secrets[secret_name]['description']
            print(f"    Description: {desc}")
    
    print("\n📊 Variables Analysis:")
    print("-" * 20)
    
    for var_name in found_variables:
        status = "✅ Known" if var_name in required_variables else "⚠️  Unknown"
        default_val = required_variables.get(var_name, {}).get('default', 'N/A')
        print(f"{status} {var_name} (default: {default_val})")
        
        if var_name in required_variables:
            desc = required_variables[var_name]['description']
            print(f"    Description: {desc}")
    
    # Missing required secrets
    missing_required = [name for name, config in required_secrets.items() 
                       if config['required'] and name not in found_secrets]
    
    if missing_required:
        print("\n❌ Missing Required Secrets:")
        print("-" * 30)
        for secret_name in missing_required:
            config = required_secrets[secret_name]
            print(f"• {secret_name}: {config['description']}")
    
    return found_secrets, found_variables


def generate_setup_instructions(found_secrets, found_variables):
    """Generate setup instructions for GitHub repository."""
    required_secrets = get_required_secrets()
    required_variables = get_required_variables()
    
    print("\n🛠️  GitHub Repository Setup Instructions")
    print("=" * 45)
    
    print("\n1️⃣ Repository Secrets (Settings → Secrets and variables → Actions → Secrets):")
    for secret_name in found_secrets:
        if secret_name in required_secrets:
            config = required_secrets[secret_name]
            required_text = "[REQUIRED]" if config['required'] else "[OPTIONAL]"
            print(f"\n   {required_text} {secret_name}")
            print(f"   Description: {config['description']}")
            print(f"   Scope: {config.get('scope', 'N/A')}")
            print(f"   Example: {config.get('example', 'N/A')}")
    
    print("\n2️⃣ Repository Variables (Settings → Secrets and variables → Actions → Variables):")
    for var_name in found_variables:
        if var_name in required_variables:
            config = required_variables[var_name]
            print(f"\n   {var_name}")
            print(f"   Description: {config['description']}")
            print(f"   Default: {config.get('default', 'N/A')}")
            print(f"   Example: {config.get('example', 'N/A')}")
    
    print("\n3️⃣ Security Configuration Commands:")
    print("   # Enable GitHub Code Security (if private repo)")
    print("   # Go to Settings → Security and analysis → Enable all security features")
    print("")
    print("   # Configure branch protection")
    print("   # Go to Settings → Branches → Add rule for 'main' branch")
    print("")
    print("   # Enable CodeQL analysis")
    print("   # Go to Security → Code scanning → Set up CodeQL")


def main():
    """Main function."""
    try:
        os.chdir(Path(__file__).parent.parent.parent)  # Go to repo root
        found_secrets, found_variables = audit_current_configuration()
        generate_setup_instructions(found_secrets, found_variables)
        
        print("\n✅ Audit complete! Review the setup instructions above.")
        
    except Exception as e:
        print(f"❌ Error during audit: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
