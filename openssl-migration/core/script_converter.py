"""
Script Converter for OpenSSL Migration

Converts shell and Perl scripts to modern Python implementations
using subprocess, pathlib, and click libraries.
"""

import re
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import logging

logger = logging.getLogger(__name__)


class ScriptConverter:
    """
    Converts scripts from various formats to Python.
    
    This class provides specialized conversion logic for different
    script types and patterns commonly found in OpenSSL utilities.
    """
    
    def __init__(self):
        """Initialize the script converter."""
        self.conversion_rules = self._load_conversion_rules()
        self.pattern_mappings = self._load_pattern_mappings()
    
    def _load_conversion_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load conversion rules for different script types."""
        return {
            'shell': {
                'shebang': r'^#!/bin/(?:bash|sh)',
                'variables': r'\$(\w+)',
                'command_substitution': r'\$\(([^)]+)\)',
                'conditionals': r'if\s+\[([^\]]+)\]',
                'loops': r'for\s+(\w+)\s+in\s+([^;]+)',
                'functions': r'(\w+)\s*\(\s*\)\s*\{',
                'external_commands': r'(\w+)\s+',
            },
            'perl': {
                'shebang': r'^#!/usr/bin/perl',
                'variables': r'\$(\w+)',
                'subroutines': r'sub\s+(\w+)',
                'modules': r'use\s+([\w:]+)',
                'conditionals': r'if\s*\(([^)]+)\)',
                'loops': r'for\s*\([^;]*;\s*([^;]+);\s*[^)]*\)',
                'file_operations': r'(open|close|read|write)',
            }
        }
    
    def _load_pattern_mappings(self) -> Dict[str, Dict[str, str]]:
        """Load pattern mappings for conversion."""
        return {
            'shell_to_python': {
                'echo': 'print',
                'cd': 'os.chdir',
                'pwd': 'os.getcwd',
                'mkdir': 'Path.mkdir',
                'rm': 'Path.unlink',
                'cp': 'shutil.copy',
                'mv': 'shutil.move',
                'ls': 'list(Path.iterdir())',
                'grep': 're.search',
                'sed': 're.sub',
                'awk': 'str.split',
            },
            'perl_to_python': {
                'print': 'print',
                'chdir': 'os.chdir',
                'mkdir': 'Path.mkdir',
                'unlink': 'Path.unlink',
                'copy': 'shutil.copy',
                'move': 'shutil.move',
                'opendir': 'Path.iterdir',
                'open': 'open',
                'close': 'file.close',
                'read': 'file.read',
                'write': 'file.write',
            }
        }
    
    def convert_shell_script(self, content: str, script_name: str) -> str:
        """
        Convert a shell script to Python.
        
        Args:
            content: Shell script content
            script_name: Name of the script
            
        Returns:
            Converted Python code
        """
        logger.info(f"Converting shell script: {script_name}")
        
        # Remove shebang
        content = re.sub(r'^#!/bin/(?:bash|sh).*\n', '', content)
        
        # Convert variables
        content = self._convert_shell_variables(content)
        
        # Convert command substitution
        content = self._convert_command_substitution(content)
        
        # Convert conditionals
        content = self._convert_shell_conditionals(content)
        
        # Convert loops
        content = self._convert_shell_loops(content)
        
        # Convert functions
        content = self._convert_shell_functions(content)
        
        # Convert external commands
        content = self._convert_external_commands(content)
        
        # Generate Python wrapper
        python_code = self._generate_python_wrapper(content, script_name, 'shell')
        
        return python_code
    
    def convert_perl_script(self, content: str, script_name: str) -> str:
        """
        Convert a Perl script to Python.
        
        Args:
            content: Perl script content
            script_name: Name of the script
            
        Returns:
            Converted Python code
        """
        logger.info(f"Converting Perl script: {script_name}")
        
        # Remove shebang
        content = re.sub(r'^#!/usr/bin/perl.*\n', '', content)
        
        # Convert variables
        content = self._convert_perl_variables(content)
        
        # Convert subroutines
        content = self._convert_perl_subroutines(content)
        
        # Convert modules
        content = self._convert_perl_modules(content)
        
        # Convert conditionals
        content = self._convert_perl_conditionals(content)
        
        # Convert loops
        content = self._convert_perl_loops(content)
        
        # Convert file operations
        content = self._convert_perl_file_operations(content)
        
        # Generate Python wrapper
        python_code = self._generate_python_wrapper(content, script_name, 'perl')
        
        return python_code
    
    def _convert_shell_variables(self, content: str) -> str:
        """Convert shell variables to Python variables."""
        # Convert $VAR to VAR
        content = re.sub(r'\$(\w+)', r'\1', content)
        
        # Convert ${VAR} to VAR
        content = re.sub(r'\$\{(\w+)\}', r'\1', content)
        
        return content
    
    def _convert_command_substitution(self, content: str) -> str:
        """Convert shell command substitution to subprocess calls."""
        def replace_command_sub(match):
            command = match.group(1)
            return f'subprocess.check_output("{command}", shell=True, text=True).strip()'
        
        content = re.sub(r'\$\(([^)]+)\)', replace_command_sub, content)
        return content
    
    def _convert_shell_conditionals(self, content: str) -> str:
        """Convert shell conditionals to Python conditionals."""
        def replace_conditional(match):
            condition = match.group(1)
            # Convert shell test conditions to Python
            condition = re.sub(r'-f\s+(\w+)', r'Path("\1").is_file()', condition)
            condition = re.sub(r'-d\s+(\w+)', r'Path("\1").is_dir()', condition)
            condition = re.sub(r'-e\s+(\w+)', r'Path("\1").exists()', condition)
            condition = re.sub(r'-z\s+(\w+)', r'not \1', condition)
            condition = re.sub(r'-n\s+(\w+)', r'\1', condition)
            return f'if {condition}:'
        
        content = re.sub(r'if\s+\[([^\]]+)\]', replace_conditional, content)
        return content
    
    def _convert_shell_loops(self, content: str) -> str:
        """Convert shell loops to Python loops."""
        def replace_for_loop(match):
            var = match.group(1)
            items = match.group(2)
            return f'for {var} in {items}:'
        
        content = re.sub(r'for\s+(\w+)\s+in\s+([^;]+)', replace_for_loop, content)
        return content
    
    def _convert_shell_functions(self, content: str) -> str:
        """Convert shell functions to Python functions."""
        def replace_function(match):
            func_name = match.group(1)
            return f'def {func_name}():'
        
        content = re.sub(r'(\w+)\s*\(\s*\)\s*\{', replace_function, content)
        return content
    
    def _convert_external_commands(self, content: str) -> str:
        """Convert external commands to subprocess calls."""
        mappings = self.pattern_mappings['shell_to_python']
        
        for shell_cmd, python_equiv in mappings.items():
            if shell_cmd in ['echo', 'print']:
                # Handle echo commands
                content = re.sub(rf'echo\s+"([^"]*)"', r'print("\1")', content)
                content = re.sub(rf'echo\s+\$(\w+)', r'print(\1)', content)
            elif shell_cmd in ['cd', 'pwd']:
                # Handle directory operations
                content = re.sub(rf'cd\s+(\w+)', r'os.chdir("\1")', content)
                content = re.sub(r'pwd', 'os.getcwd()', content)
            elif shell_cmd in ['mkdir', 'rm', 'cp', 'mv']:
                # Handle file operations
                content = re.sub(rf'mkdir\s+(\w+)', r'Path("\1").mkdir(parents=True, exist_ok=True)', content)
                content = re.sub(rf'rm\s+(\w+)', r'Path("\1").unlink()', content)
                content = re.sub(rf'cp\s+(\w+)\s+(\w+)', r'shutil.copy("\1", "\2")', content)
                content = re.sub(rf'mv\s+(\w+)\s+(\w+)', r'shutil.move("\1", "\2")', content)
        
        return content
    
    def _convert_perl_variables(self, content: str) -> str:
        """Convert Perl variables to Python variables."""
        # Convert $var to var
        content = re.sub(r'\$(\w+)', r'\1', content)
        
        # Convert @array to array
        content = re.sub(r'@(\w+)', r'\1', content)
        
        # Convert %hash to hash
        content = re.sub(r'%(\w+)', r'\1', content)
        
        return content
    
    def _convert_perl_subroutines(self, content: str) -> str:
        """Convert Perl subroutines to Python functions."""
        def replace_subroutine(match):
            sub_name = match.group(1)
            return f'def {sub_name}():'
        
        content = re.sub(r'sub\s+(\w+)', replace_subroutine, content)
        return content
    
    def _convert_perl_modules(self, content: str) -> str:
        """Convert Perl modules to Python imports."""
        def replace_module(match):
            module = match.group(1)
            # Convert Perl module names to Python equivalents
            module_mapping = {
                'File::Path': 'pathlib',
                'File::Copy': 'shutil',
                'Getopt::Long': 'argparse',
                'POSIX': 'os',
                'Cwd': 'os',
            }
            
            python_module = module_mapping.get(module, module.lower().replace('::', '.'))
            return f'import {python_module}'
        
        content = re.sub(r'use\s+([\w:]+)', replace_module, content)
        return content
    
    def _convert_perl_conditionals(self, content: str) -> str:
        """Convert Perl conditionals to Python conditionals."""
        def replace_conditional(match):
            condition = match.group(1)
            # Convert Perl conditions to Python
            condition = re.sub(r'-f\s+(\w+)', r'Path("\1").is_file()', condition)
            condition = re.sub(r'-d\s+(\w+)', r'Path("\1").is_dir()', condition)
            condition = re.sub(r'-e\s+(\w+)', r'Path("\1").exists()', condition)
            return f'if {condition}:'
        
        content = re.sub(r'if\s*\(([^)]+)\)', replace_conditional, content)
        return content
    
    def _convert_perl_loops(self, content: str) -> str:
        """Convert Perl loops to Python loops."""
        def replace_for_loop(match):
            condition = match.group(1)
            return f'for {condition}:'
        
        content = re.sub(r'for\s*\([^;]*;\s*([^;]+);\s*[^)]*\)', replace_for_loop, content)
        return content
    
    def _convert_perl_file_operations(self, content: str) -> str:
        """Convert Perl file operations to Python file operations."""
        mappings = self.pattern_mappings['perl_to_python']
        
        for perl_op, python_equiv in mappings.items():
            if perl_op == 'open':
                # Convert Perl open to Python open
                content = re.sub(r'open\s*\(\s*(\w+),\s*["\']([^"\']+)["\']\s*\)', 
                               r'\1 = open("\2", "r")', content)
            elif perl_op == 'close':
                # Convert Perl close to Python close
                content = re.sub(r'close\s*\(\s*(\w+)\s*\)', r'\1.close()', content)
            elif perl_op == 'read':
                # Convert Perl read to Python read
                content = re.sub(r'read\s*\(\s*(\w+),\s*(\w+),\s*(\d+)\s*\)', 
                               r'\2 = \1.read(\3)', content)
            elif perl_op == 'write':
                # Convert Perl write to Python write
                content = re.sub(r'write\s*\(\s*(\w+),\s*(\w+)\s*\)', 
                               r'\1.write(\2)', content)
        
        return content
    
    def _generate_python_wrapper(self, content: str, script_name: str, script_type: str) -> str:
        """Generate Python wrapper code."""
        wrapper = f'''"""
{script_name}

Migrated from {script_type} script.
Generated by OpenSSL Migration Framework.
"""

import os
import sys
import subprocess
import shutil
import re
from pathlib import Path
from typing import List, Optional, Dict, Any
import click
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Migrated code from {script_type} script
{content}

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--dry-run', is_flag=True, help='Show what would be done without executing')
def main(verbose: bool, dry_run: bool):
    """
    Main entry point for the migrated script.
    
    This function serves as the entry point for the migrated {script_type} script.
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info(f"Starting migrated script: {script_name}")
    
    if dry_run:
        logger.info("Dry run mode - no changes will be made")
        return
    
    try:
        # Add your migrated logic here
        # This is where the converted script logic would go
        pass
        
    except Exception as e:
        logger.error(f"Error executing migrated script: {{e}}")
        sys.exit(1)
    
    logger.info("Script completed successfully")

if __name__ == '__main__':
    main()
'''
        return wrapper
    
    def analyze_script_complexity(self, content: str, script_type: str) -> Dict[str, Any]:
        """
        Analyze the complexity of a script for migration planning.
        
        Args:
            content: Script content
            script_type: Type of script ('shell', 'perl', 'python')
            
        Returns:
            Dictionary with complexity analysis
        """
        analysis = {
            'lines': len(content.split('\n')),
            'size': len(content),
            'complexity_score': 0,
            'features': [],
            'difficulty': 'low'
        }
        
        # Count various features
        if script_type == 'shell':
            # Count shell-specific features
            features = {
                'functions': len(re.findall(r'(\w+)\s*\(\s*\)\s*\{', content)),
                'conditionals': len(re.findall(r'if\s+\[', content)),
                'loops': len(re.findall(r'for\s+\w+\s+in', content)),
                'external_commands': len(re.findall(r'(\w+)\s+', content)),
                'command_substitution': len(re.findall(r'\$\([^)]+\)', content)),
                'variables': len(re.findall(r'\$\w+', content))
            }
        
        elif script_type == 'perl':
            # Count Perl-specific features
            features = {
                'subroutines': len(re.findall(r'sub\s+\w+', content)),
                'modules': len(re.findall(r'use\s+[\w:]+', content)),
                'conditionals': len(re.findall(r'if\s*\(', content)),
                'loops': len(re.findall(r'for\s*\(', content)),
                'file_operations': len(re.findall(r'(open|close|read|write)', content)),
                'variables': len(re.findall(r'\$\w+', content))
            }
        
        else:
            features = {}
        
        analysis['features'] = features
        
        # Calculate complexity score
        complexity_score = sum(features.values())
        analysis['complexity_score'] = complexity_score
        
        # Determine difficulty
        if complexity_score < 10:
            analysis['difficulty'] = 'low'
        elif complexity_score < 25:
            analysis['difficulty'] = 'medium'
        else:
            analysis['difficulty'] = 'high'
        
        return analysis
    
    def suggest_improvements(self, content: str, script_type: str) -> List[str]:
        """
        Suggest improvements for the migrated script.
        
        Args:
            content: Script content
            script_type: Type of script
            
        Returns:
            List of improvement suggestions
        """
        suggestions = []
        
        if script_type == 'shell':
            # Check for common shell script issues
            if re.search(r'rm\s+-rf', content):
                suggestions.append("Consider using Path.unlink() with proper error handling instead of rm -rf")
            
            if re.search(r'curl\s+', content):
                suggestions.append("Consider using requests library instead of curl for HTTP operations")
            
            if re.search(r'grep\s+', content):
                suggestions.append("Consider using re module for pattern matching instead of grep")
            
            if re.search(r'awk\s+', content):
                suggestions.append("Consider using pandas or built-in string methods instead of awk")
        
        elif script_type == 'perl':
            # Check for common Perl script issues
            if re.search(r'open\s*\(\s*\w+,\s*["\']<["\']', content):
                suggestions.append("Consider using pathlib.Path for file operations")
            
            if re.search(r'print\s+', content):
                suggestions.append("Consider using logging instead of print statements")
            
            if re.search(r'Getopt::Long', content):
                suggestions.append("Consider using click for command-line argument parsing")
        
        # General suggestions
        suggestions.extend([
            "Add proper error handling with try-except blocks",
            "Use type hints for better code documentation",
            "Add comprehensive logging instead of print statements",
            "Consider using dataclasses for structured data",
            "Add unit tests for the migrated functionality"
        ])
        
        return suggestions
