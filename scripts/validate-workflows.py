#!/usr/bin/env python3
"""
Validate GitHub Actions workflow syntax and structure.
"""

import os
import yaml
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

def validate_workflow_syntax(file_path: Path) -> Dict[str, Any]:
    """Validate a single workflow file."""
    result = {
        'file': str(file_path),
        'valid': True,
        'errors': [],
        'warnings': [],
        'info': {}
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Parse YAML
        workflow = yaml.safe_load(content)
        
        # Basic structure validation
        if not isinstance(workflow, dict):
            result['valid'] = False
            result['errors'].append("Workflow must be a YAML dictionary")
            return result
            
        # Check required fields
        required_fields = ['name']
        for field in required_fields:
            if field not in workflow:
                result['valid'] = False
                result['errors'].append(f"Missing required field: {field}")
        
        # Check for trigger (on field)
        if 'on' not in workflow:
            result['valid'] = False
            result['errors'].append("Missing required field: on")
        else:
            on_config = workflow.get('on', {})
            if not isinstance(on_config, dict):
                result['warnings'].append("'on' field should be a dictionary")
            elif not on_config:
                result['warnings'].append("'on' field is empty")
        
        # Validate workflow_call structure for reusable workflows
        if 'workflow_call' in workflow.get('on', {}):
            result['info']['type'] = 'reusable'
            
            # Check inputs structure
            inputs = workflow.get('on', {}).get('workflow_call', {}).get('inputs', {})
            if inputs:
                for input_name, input_config in inputs.items():
                    if not isinstance(input_config, dict):
                        result['warnings'].append(f"Input '{input_name}' should be a dictionary")
                        continue
                        
                    # Check required input fields
                    if 'description' not in input_config:
                        result['warnings'].append(f"Input '{input_name}' missing description")
                    if 'type' not in input_config:
                        result['warnings'].append(f"Input '{input_name}' missing type")
                    if 'required' not in input_config:
                        result['warnings'].append(f"Input '{input_name}' missing required field")
            
            # Check outputs structure
            outputs = workflow.get('on', {}).get('workflow_call', {}).get('outputs', {})
            if outputs:
                for output_name, output_config in outputs.items():
                    if not isinstance(output_config, dict):
                        result['warnings'].append(f"Output '{output_name}' should be a dictionary")
                        continue
                        
                    if 'description' not in output_config:
                        result['warnings'].append(f"Output '{output_name}' missing description")
                    if 'value' not in output_config:
                        result['warnings'].append(f"Output '{output_name}' missing value")
            
            # Check secrets structure
            secrets = workflow.get('on', {}).get('workflow_call', {}).get('secrets', {})
            if secrets:
                for secret_name, secret_config in secrets.items():
                    if not isinstance(secret_config, dict):
                        result['warnings'].append(f"Secret '{secret_name}' should be a dictionary")
                        continue
                        
                    if 'description' not in secret_config:
                        result['warnings'].append(f"Secret '{secret_name}' missing description")
                    if 'required' not in secret_config:
                        result['warnings'].append(f"Secret '{secret_name}' missing required field")
        else:
            result['info']['type'] = 'regular'
        
        # Validate jobs structure
        jobs = workflow.get('jobs', {})
        if not jobs:
            result['warnings'].append("No jobs defined")
        else:
            for job_name, job_config in jobs.items():
                if not isinstance(job_config, dict):
                    result['errors'].append(f"Job '{job_name}' must be a dictionary")
                    continue
                    
                # Check for required job fields
                if 'runs-on' not in job_config and 'uses' not in job_config:
                    result['warnings'].append(f"Job '{job_name}' missing runs-on or uses")
                
                # Check for steps in regular jobs
                if 'uses' not in job_config and 'steps' not in job_config:
                    result['warnings'].append(f"Job '{job_name}' missing steps")
        
        # Count jobs and steps
        result['info']['job_count'] = len(jobs)
        total_steps = 0
        for job_config in jobs.values():
            if isinstance(job_config, dict) and 'steps' in job_config:
                total_steps += len(job_config['steps'])
        result['info']['total_steps'] = total_steps
        
    except yaml.YAMLError as e:
        result['valid'] = False
        result['errors'].append(f"YAML syntax error: {e}")
    except Exception as e:
        result['valid'] = False
        result['errors'].append(f"Unexpected error: {e}")
    
    return result

def validate_composite_action(file_path: Path) -> Dict[str, Any]:
    """Validate a composite action file."""
    result = {
        'file': str(file_path),
        'valid': True,
        'errors': [],
        'warnings': [],
        'info': {}
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        action = yaml.safe_load(content)
        
        # Check required fields
        required_fields = ['name', 'description', 'inputs', 'runs']
        for field in required_fields:
            if field not in action:
                result['valid'] = False
                result['errors'].append(f"Missing required field: {field}")
        
        # Validate runs structure
        runs = action.get('runs', {})
        if not isinstance(runs, dict):
            result['valid'] = False
            result['errors'].append("'runs' must be a dictionary")
        elif runs.get('using') != 'composite':
            result['valid'] = False
            result['errors'].append("'runs.using' must be 'composite'")
        elif 'steps' not in runs:
            result['valid'] = False
            result['errors'].append("'runs.steps' is required")
        
        # Count inputs and steps
        result['info']['input_count'] = len(action.get('inputs', {}))
        result['info']['output_count'] = len(action.get('outputs', {}))
        result['info']['step_count'] = len(runs.get('steps', []))
        
    except yaml.YAMLError as e:
        result['valid'] = False
        result['errors'].append(f"YAML syntax error: {e}")
    except Exception as e:
        result['valid'] = False
        result['errors'].append(f"Unexpected error: {e}")
    
    return result

def main():
    """Main validation function."""
    workflows_dir = Path('.github/workflows')
    actions_dir = Path('.github/actions')
    
    all_results = []
    total_files = 0
    valid_files = 0
    
    print("🔍 Validating GitHub Actions workflows and composite actions...")
    print("=" * 60)
    
    # Validate workflows
    if workflows_dir.exists():
        print(f"\n📁 Validating workflows in {workflows_dir}")
        for workflow_file in workflows_dir.glob('*.yml'):
            if workflow_file.name.startswith('.'):
                continue
                
            print(f"\n🔍 Validating {workflow_file.name}...")
            result = validate_workflow_syntax(workflow_file)
            all_results.append(result)
            total_files += 1
            
            if result['valid']:
                valid_files += 1
                print(f"  ✅ Valid ({result['info'].get('type', 'unknown')} workflow)")
                if result['info'].get('job_count'):
                    print(f"     Jobs: {result['info']['job_count']}, Steps: {result['info']['total_steps']}")
            else:
                print(f"  ❌ Invalid")
                for error in result['errors']:
                    print(f"     Error: {error}")
            
            for warning in result['warnings']:
                print(f"     Warning: {warning}")
    
    # Validate composite actions
    if actions_dir.exists():
        print(f"\n📁 Validating composite actions in {actions_dir}")
        for action_dir in actions_dir.iterdir():
            if not action_dir.is_dir():
                continue
                
            action_file = action_dir / 'action.yml'
            if action_file.exists():
                print(f"\n🔍 Validating {action_dir.name}/action.yml...")
                result = validate_composite_action(action_file)
                all_results.append(result)
                total_files += 1
                
                if result['valid']:
                    valid_files += 1
                    print(f"  ✅ Valid composite action")
                    print(f"     Inputs: {result['info']['input_count']}, Outputs: {result['info']['output_count']}, Steps: {result['info']['step_count']}")
                else:
                    print(f"  ❌ Invalid")
                    for error in result['errors']:
                        print(f"     Error: {error}")
                
                for warning in result['warnings']:
                    print(f"     Warning: {warning}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Validation Summary")
    print(f"Total files: {total_files}")
    print(f"Valid files: {valid_files}")
    print(f"Invalid files: {total_files - valid_files}")
    
    if total_files - valid_files > 0:
        print("\n❌ Validation failed!")
        sys.exit(1)
    else:
        print("\n✅ All files are valid!")
        sys.exit(0)

if __name__ == '__main__':
    main()