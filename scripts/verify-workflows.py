#!/usr/bin/env python3
"""
Workflow Verification Script
Validates that all reusable workflows are properly configured and can be called.
"""

import yaml
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any

def validate_workflow_file(workflow_path: Path) -> Dict[str, Any]:
    """Validate a single workflow file."""
    try:
        with open(workflow_path, 'r') as f:
            workflow = yaml.safe_load(f)
        
        validation_result = {
            'file': str(workflow_path),
            'valid': True,
            'errors': [],
            'warnings': [],
            'inputs': {},
            'outputs': {},
            'secrets': {}
        }
        
        # Check if it's a reusable workflow
        # Note: 'on' becomes True in YAML parsing, so we need to check for it differently
        workflow_trigger = workflow.get('on') or workflow.get(True)
        if not workflow_trigger:
            validation_result['errors'].append("Missing 'on' trigger")
            validation_result['valid'] = False
        elif 'workflow_call' not in workflow_trigger:
            validation_result['warnings'].append("Not a reusable workflow (missing workflow_call)")
        
        # Validate workflow_call structure
        workflow_trigger = workflow.get('on') or workflow.get(True)
        if workflow_trigger and 'workflow_call' in workflow_trigger:
            workflow_call = workflow_trigger['workflow_call']
            
            # Check inputs
            if 'inputs' in workflow_call:
                validation_result['inputs'] = workflow_call['inputs']
                for input_name, input_config in workflow_call['inputs'].items():
                    if 'type' not in input_config:
                        validation_result['errors'].append(f"Input '{input_name}' missing type")
                        validation_result['valid'] = False
                    if 'description' not in input_config:
                        validation_result['warnings'].append(f"Input '{input_name}' missing description")
            
            # Check outputs
            if 'outputs' in workflow_call:
                validation_result['outputs'] = workflow_call['outputs']
                for output_name, output_config in workflow_call['outputs'].items():
                    if 'value' not in output_config:
                        validation_result['errors'].append(f"Output '{output_name}' missing value")
                        validation_result['valid'] = False
                    if 'description' not in output_config:
                        validation_result['warnings'].append(f"Output '{output_name}' missing description")
            
            # Check secrets
            if 'secrets' in workflow_call:
                validation_result['secrets'] = workflow_call['secrets']
                for secret_name, secret_config in workflow_call['secrets'].items():
                    if 'description' not in secret_config:
                        validation_result['warnings'].append(f"Secret '{secret_name}' missing description")
        
        # Check for required jobs
        if 'jobs' not in workflow:
            validation_result['errors'].append("Missing 'jobs' section")
            validation_result['valid'] = False
        else:
            # Check for at least one job
            if not workflow['jobs']:
                validation_result['errors'].append("No jobs defined")
                validation_result['valid'] = False
        
        return validation_result
        
    except yaml.YAMLError as e:
        return {
            'file': str(workflow_path),
            'valid': False,
            'errors': [f"YAML parsing error: {e}"],
            'warnings': [],
            'inputs': {},
            'outputs': {},
            'secrets': {}
        }
    except Exception as e:
        return {
            'file': str(workflow_path),
            'valid': False,
            'errors': [f"Unexpected error: {e}"],
            'warnings': [],
            'inputs': {},
            'outputs': {},
            'secrets': {}
        }

def validate_composite_action(action_path: Path) -> Dict[str, Any]:
    """Validate a composite action file."""
    try:
        with open(action_path, 'r') as f:
            action = yaml.safe_load(f)
        
        validation_result = {
            'file': str(action_path),
            'valid': True,
            'errors': [],
            'warnings': [],
            'inputs': {},
            'outputs': {}
        }
        
        # Check required fields
        if 'name' not in action:
            validation_result['errors'].append("Missing 'name' field")
            validation_result['valid'] = False
        
        if 'description' not in action:
            validation_result['warnings'].append("Missing 'description' field")
        
        if 'runs' not in action:
            validation_result['errors'].append("Missing 'runs' section")
            validation_result['valid'] = False
        elif action.get('runs', {}).get('using') != 'composite':
            validation_result['errors'].append("Not a composite action (missing 'using: composite')")
            validation_result['valid'] = False
        
        # Check inputs
        if 'inputs' in action:
            validation_result['inputs'] = action['inputs']
            for input_name, input_config in action['inputs'].items():
                if 'description' not in input_config:
                    validation_result['warnings'].append(f"Input '{input_name}' missing description")
                if 'required' not in input_config:
                    validation_result['warnings'].append(f"Input '{input_name}' missing required field")
        
        # Check outputs
        if 'outputs' in action:
            validation_result['outputs'] = action['outputs']
            for output_name, output_config in action['outputs'].items():
                if 'description' not in output_config:
                    validation_result['warnings'].append(f"Output '{output_name}' missing description")
                if 'value' not in output_config:
                    validation_result['errors'].append(f"Output '{output_name}' missing value")
                    validation_result['valid'] = False
        
        return validation_result
        
    except yaml.YAMLError as e:
        return {
            'file': str(action_path),
            'valid': False,
            'errors': [f"YAML parsing error: {e}"],
            'warnings': [],
            'inputs': {},
            'outputs': {}
        }
    except Exception as e:
        return {
            'file': str(action_path),
            'valid': False,
            'errors': [f"Unexpected error: {e}"],
            'warnings': [],
            'inputs': {},
            'outputs': {}
        }

def main():
    """Main verification function."""
    print("🔍 Verifying Reusable Workflows and Composite Actions")
    print("=" * 60)
    
    # Define paths
    workflows_dir = Path(".github/workflows")
    actions_dir = Path(".github/actions")
    
    # Reusable workflows to check
    reusable_workflows = [
        "build-openssl.yml",
        "test-integration.yml", 
        "publish-cloudsmith.yml"
    ]
    
    # Composite actions to check
    composite_actions = [
        "cloudsmith-publish/action.yml"
    ]
    
    all_valid = True
    results = []
    
    # Validate reusable workflows
    print("\n📋 Validating Reusable Workflows:")
    print("-" * 40)
    
    for workflow_file in reusable_workflows:
        workflow_path = workflows_dir / workflow_file
        if workflow_path.exists():
            result = validate_workflow_file(workflow_path)
            results.append(result)
            
            status = "✅" if result['valid'] else "❌"
            print(f"{status} {workflow_file}")
            
            if result['errors']:
                for error in result['errors']:
                    print(f"   ❌ Error: {error}")
                    all_valid = False
            
            if result['warnings']:
                for warning in result['warnings']:
                    print(f"   ⚠️  Warning: {warning}")
            
            # Show inputs/outputs summary
            if result['inputs']:
                print(f"   📥 Inputs: {len(result['inputs'])}")
            if result['outputs']:
                print(f"   📤 Outputs: {len(result['outputs'])}")
            if result['secrets']:
                print(f"   🔐 Secrets: {len(result['secrets'])}")
        else:
            print(f"❌ {workflow_file} - File not found")
            all_valid = False
    
    # Validate composite actions
    print("\n🔧 Validating Composite Actions:")
    print("-" * 40)
    
    for action_file in composite_actions:
        action_path = actions_dir / action_file
        if action_path.exists():
            result = validate_composite_action(action_path)
            results.append(result)
            
            status = "✅" if result['valid'] else "❌"
            print(f"{status} {action_file}")
            
            if result['errors']:
                for error in result['errors']:
                    print(f"   ❌ Error: {error}")
                    all_valid = False
            
            if result['warnings']:
                for warning in result['warnings']:
                    print(f"   ⚠️  Warning: {warning}")
            
            # Show inputs/outputs summary
            if result['inputs']:
                print(f"   📥 Inputs: {len(result['inputs'])}")
            if result['outputs']:
                print(f"   📤 Outputs: {len(result['outputs'])}")
        else:
            print(f"❌ {action_file} - File not found")
            all_valid = False
    
    # Generate summary report
    print("\n📊 Summary Report:")
    print("-" * 40)
    
    total_files = len(reusable_workflows) + len(composite_actions)
    valid_files = sum(1 for r in results if r['valid'])
    
    print(f"Total files checked: {total_files}")
    print(f"Valid files: {valid_files}")
    print(f"Invalid files: {total_files - valid_files}")
    
    if all_valid:
        print("\n🎉 All workflows and actions are valid!")
        print("\n📝 Next steps:")
        print("1. Test workflows with workflow_dispatch")
        print("2. Verify Cloudsmith integration")
        print("3. Check artifact uploads")
        return 0
    else:
        print("\n❌ Some workflows or actions have errors that need to be fixed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())