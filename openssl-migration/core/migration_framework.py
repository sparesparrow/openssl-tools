"""
OpenSSL Migration Framework

Core framework for migrating OpenSSL utility repositories from shell/Perl
to modern Python implementations using subprocess, pathlib, and click.
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import click
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class MigrationConfig:
    """Configuration for migration process."""
    source_repo: str
    target_dir: Path
    script_types: List[str]  # ['shell', 'perl', 'python']
    preserve_structure: bool = True
    add_tests: bool = True
    add_documentation: bool = True
    use_click: bool = True
    use_pathlib: bool = True
    use_subprocess: bool = True
    output_format: str = "modern"  # 'modern', 'compatible', 'minimal'


@dataclass
class ScriptInfo:
    """Information about a script to be migrated."""
    name: str
    path: Path
    script_type: str  # 'shell', 'perl', 'python'
    size: int
    lines: int
    dependencies: List[str]
    functions: List[str]
    description: Optional[str] = None
    migration_status: str = "pending"  # 'pending', 'in_progress', 'completed', 'failed'
    migration_notes: Optional[str] = None


class MigrationFramework:
    """
    Main framework for migrating OpenSSL utility repositories.
    
    This class provides the core functionality for analyzing, converting,
    and migrating scripts from various formats to modern Python.
    """
    
    def __init__(self, config: MigrationConfig):
        """
        Initialize the migration framework.
        
        Args:
            config: Migration configuration
        """
        self.config = config
        self.scripts: List[ScriptInfo] = []
        self.migration_log: List[Dict[str, Any]] = []
        
        # Ensure target directory exists
        self.config.target_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Initialized migration framework for {config.source_repo}")
    
    def analyze_repository(self, repo_path: Union[str, Path]) -> List[ScriptInfo]:
        """
        Analyze a repository and identify scripts to migrate.
        
        Args:
            repo_path: Path to the repository to analyze
            
        Returns:
            List of ScriptInfo objects for all found scripts
        """
        repo_path = Path(repo_path)
        if not repo_path.exists():
            raise FileNotFoundError(f"Repository path does not exist: {repo_path}")
        
        logger.info(f"Analyzing repository: {repo_path}")
        
        scripts = []
        
        # Find all script files
        for script_type in self.config.script_types:
            patterns = {
                'shell': ['*.sh', '*.bash'],
                'perl': ['*.pl', '*.pm'],
                'python': ['*.py']
            }
            
            for pattern in patterns.get(script_type, []):
                for script_path in repo_path.rglob(pattern):
                    if self._should_migrate_script(script_path):
                        script_info = self._analyze_script(script_path, script_type)
                        scripts.append(script_info)
        
        self.scripts = scripts
        logger.info(f"Found {len(scripts)} scripts to migrate")
        
        return scripts
    
    def _should_migrate_script(self, script_path: Path) -> bool:
        """
        Determine if a script should be migrated.
        
        Args:
            script_path: Path to the script
            
        Returns:
            True if script should be migrated
        """
        # Skip test files, documentation, and very small files
        skip_patterns = [
            'test', 'spec', 'doc', 'example', 'sample',
            'README', 'CHANGELOG', 'LICENSE'
        ]
        
        script_name = script_path.name.lower()
        for pattern in skip_patterns:
            if pattern in script_name:
                return False
        
        # Skip very small files (likely not substantial scripts)
        if script_path.stat().st_size < 100:
            return False
        
        return True
    
    def _analyze_script(self, script_path: Path, script_type: str) -> ScriptInfo:
        """
        Analyze a single script and extract information.
        
        Args:
            script_path: Path to the script
            script_type: Type of script ('shell', 'perl', 'python')
            
        Returns:
            ScriptInfo object with script details
        """
        try:
            with open(script_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            lines = content.split('\n')
            functions = self._extract_functions(content, script_type)
            dependencies = self._extract_dependencies(content, script_type)
            description = self._extract_description(content, script_type)
            
            script_info = ScriptInfo(
                name=script_path.name,
                path=script_path,
                script_type=script_type,
                size=script_path.stat().st_size,
                lines=len(lines),
                dependencies=dependencies,
                functions=functions,
                description=description
            )
            
            logger.debug(f"Analyzed script: {script_path.name}")
            return script_info
            
        except Exception as e:
            logger.error(f"Error analyzing script {script_path}: {e}")
            return ScriptInfo(
                name=script_path.name,
                path=script_path,
                script_type=script_type,
                size=0,
                lines=0,
                dependencies=[],
                functions=[],
                description=f"Error analyzing: {e}"
            )
    
    def _extract_functions(self, content: str, script_type: str) -> List[str]:
        """Extract function names from script content."""
        functions = []
        
        if script_type == 'shell':
            # Extract shell functions
            import re
            func_pattern = r'^\s*(\w+)\s*\(\s*\)\s*\{'
            functions = re.findall(func_pattern, content, re.MULTILINE)
        
        elif script_type == 'perl':
            # Extract Perl subroutines
            import re
            sub_pattern = r'^\s*sub\s+(\w+)'
            functions = re.findall(sub_pattern, content, re.MULTILINE)
        
        elif script_type == 'python':
            # Extract Python functions
            import re
            func_pattern = r'^\s*def\s+(\w+)\s*\('
            functions = re.findall(func_pattern, content, re.MULTILINE)
        
        return functions
    
    def _extract_dependencies(self, content: str, script_type: str) -> List[str]:
        """Extract dependencies from script content."""
        dependencies = []
        
        if script_type == 'shell':
            # Extract external commands
            import re
            cmd_pattern = r'(\w+)\s+'
            commands = re.findall(cmd_pattern, content)
            # Filter out common shell built-ins
            built_ins = {'echo', 'cd', 'ls', 'pwd', 'mkdir', 'rm', 'cp', 'mv', 'if', 'for', 'while', 'do', 'done', 'then', 'else', 'fi'}
            dependencies = [cmd for cmd in commands if cmd not in built_ins and len(cmd) > 2]
        
        elif script_type == 'perl':
            # Extract Perl modules
            import re
            use_pattern = r'use\s+([\w:]+)'
            dependencies = re.findall(use_pattern, content)
        
        elif script_type == 'python':
            # Extract Python imports
            import re
            import_pattern = r'(?:from\s+(\w+)\s+import|import\s+(\w+))'
            matches = re.findall(import_pattern, content)
            dependencies = [match[0] or match[1] for match in matches]
        
        return list(set(dependencies))  # Remove duplicates
    
    def _extract_description(self, content: str, script_type: str) -> Optional[str]:
        """Extract description from script content."""
        lines = content.split('\n')
        
        # Look for common comment patterns
        for line in lines[:20]:  # Check first 20 lines
            line = line.strip()
            
            if script_type == 'shell':
                if line.startswith('#') and len(line) > 3:
                    return line[1:].strip()
            
            elif script_type == 'perl':
                if line.startswith('#') and len(line) > 3:
                    return line[1:].strip()
            
            elif script_type == 'python':
                if line.startswith('"""') or line.startswith("'''"):
                    # Extract docstring
                    return line[3:].strip()
                elif line.startswith('#') and len(line) > 3:
                    return line[1:].strip()
        
        return None
    
    def generate_migration_plan(self) -> Dict[str, Any]:
        """
        Generate a detailed migration plan.
        
        Returns:
            Dictionary containing migration plan details
        """
        plan = {
            'total_scripts': len(self.scripts),
            'by_type': {},
            'estimated_effort': {},
            'dependencies': set(),
            'recommendations': []
        }
        
        # Group scripts by type
        for script in self.scripts:
            script_type = script.script_type
            if script_type not in plan['by_type']:
                plan['by_type'][script_type] = []
            plan['by_type'][script_type].append(script.name)
            
            # Collect all dependencies
            plan['dependencies'].update(script.dependencies)
        
        # Estimate effort
        for script_type, scripts in plan['by_type'].items():
            count = len(scripts)
            if script_type == 'shell':
                plan['estimated_effort'][script_type] = f"{count * 2} hours (medium complexity)"
            elif script_type == 'perl':
                plan['estimated_effort'][script_type] = f"{count * 3} hours (high complexity)"
            elif script_type == 'python':
                plan['estimated_effort'][script_type] = f"{count * 1} hours (low complexity - modernization)"
        
        # Generate recommendations
        if 'shell' in plan['by_type']:
            plan['recommendations'].append("Shell scripts should be converted to use subprocess for external commands")
        
        if 'perl' in plan['by_type']:
            plan['recommendations'].append("Perl scripts should be converted to use appropriate Python libraries")
        
        plan['recommendations'].append("All scripts should use pathlib for file operations")
        plan['recommendations'].append("CLI scripts should use click for command-line interfaces")
        
        return plan
    
    def migrate_script(self, script_info: ScriptInfo) -> bool:
        """
        Migrate a single script to Python.
        
        Args:
            script_info: Information about the script to migrate
            
        Returns:
            True if migration was successful
        """
        try:
            logger.info(f"Migrating script: {script_info.name}")
            
            # Create target directory structure
            target_path = self._get_target_path(script_info)
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Generate Python code
            python_code = self._generate_python_code(script_info)
            
            # Write the migrated script
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(python_code)
            
            # Update script info
            script_info.migration_status = "completed"
            script_info.migration_notes = f"Migrated to {target_path}"
            
            # Log migration
            self.migration_log.append({
                'timestamp': datetime.now().isoformat(),
                'script': script_info.name,
                'status': 'completed',
                'target_path': str(target_path)
            })
            
            logger.info(f"Successfully migrated: {script_info.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to migrate {script_info.name}: {e}")
            script_info.migration_status = "failed"
            script_info.migration_notes = str(e)
            
            self.migration_log.append({
                'timestamp': datetime.now().isoformat(),
                'script': script_info.name,
                'status': 'failed',
                'error': str(e)
            })
            
            return False
    
    def _get_target_path(self, script_info: ScriptInfo) -> Path:
        """Get the target path for a migrated script."""
        # Preserve directory structure if requested
        if self.config.preserve_structure:
            relative_path = script_info.path.relative_to(script_info.path.parents[1])
            target_path = self.config.target_dir / relative_path.with_suffix('.py')
        else:
            target_path = self.config.target_dir / f"{script_info.path.stem}.py"
        
        return target_path
    
    def _generate_python_code(self, script_info: ScriptInfo) -> str:
        """Generate Python code for a script."""
        # This is a simplified version - in practice, you'd want more sophisticated conversion
        template = self._get_python_template(script_info)
        
        # Replace placeholders with actual content
        code = template.format(
            script_name=script_info.name,
            description=script_info.description or "Migrated script",
            functions=self._generate_functions(script_info),
            dependencies=self._generate_imports(script_info)
        )
        
        return code
    
    def _get_python_template(self, script_info: ScriptInfo) -> str:
        """Get Python template based on script type and configuration."""
        if self.config.use_click:
            template = '''"""
{description}

Migrated from {script_name}
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Any
import click
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

{dependencies}

{functions}

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--dry-run', is_flag=True, help='Show what would be done without executing')
def main(verbose: bool, dry_run: bool):
    """Main entry point for the migrated script."""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info("Starting migrated script")
    
    if dry_run:
        logger.info("Dry run mode - no changes will be made")
        return
    
    # Add your migrated logic here
    pass

if __name__ == '__main__':
    main()
'''
        else:
            template = '''"""
{description}

Migrated from {script_name}
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

{dependencies}

{functions}

def main():
    """Main entry point for the migrated script."""
    logger.info("Starting migrated script")
    
    # Add your migrated logic here
    pass

if __name__ == '__main__':
    main()
'''
        
        return template
    
    def _generate_imports(self, script_info: ScriptInfo) -> str:
        """Generate import statements based on dependencies."""
        imports = []
        
        # Standard library imports
        standard_imports = ['os', 'sys', 'subprocess', 'pathlib', 'logging']
        if self.config.use_click:
            standard_imports.append('click')
        
        for imp in standard_imports:
            imports.append(f"import {imp}")
        
        # Add imports for dependencies
        for dep in script_info.dependencies:
            if dep not in standard_imports:
                imports.append(f"import {dep}")
        
        return '\n'.join(imports)
    
    def _generate_functions(self, script_info: ScriptInfo) -> str:
        """Generate function stubs for migrated functions."""
        functions = []
        
        for func_name in script_info.functions:
            func_code = f'''
def {func_name}():
    """
    Migrated function: {func_name}
    
    TODO: Implement the migrated functionality
    """
    logger.info(f"Executing function: {func_name}")
    
    # Add your migrated logic here
    pass
'''
            functions.append(func_code)
        
        return '\n'.join(functions)
    
    def migrate_all(self) -> Dict[str, Any]:
        """
        Migrate all identified scripts.
        
        Returns:
            Dictionary with migration results
        """
        results = {
            'total': len(self.scripts),
            'completed': 0,
            'failed': 0,
            'skipped': 0
        }
        
        logger.info(f"Starting migration of {len(self.scripts)} scripts")
        
        for script_info in self.scripts:
            if script_info.migration_status == "pending":
                script_info.migration_status = "in_progress"
                
                if self.migrate_script(script_info):
                    results['completed'] += 1
                else:
                    results['failed'] += 1
            else:
                results['skipped'] += 1
        
        logger.info(f"Migration completed: {results['completed']} successful, {results['failed']} failed")
        
        return results
    
    def generate_report(self) -> str:
        """Generate a detailed migration report."""
        report = []
        report.append("# OpenSSL Migration Report")
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append(f"Source Repository: {self.config.source_repo}")
        report.append(f"Target Directory: {self.config.target_dir}")
        report.append("")
        
        # Summary
        report.append("## Summary")
        report.append(f"- Total Scripts: {len(self.scripts)}")
        
        by_status = {}
        for script in self.scripts:
            status = script.migration_status
            by_status[status] = by_status.get(status, 0) + 1
        
        for status, count in by_status.items():
            report.append(f"- {status.title()}: {count}")
        
        report.append("")
        
        # Detailed results
        report.append("## Detailed Results")
        for script in self.scripts:
            report.append(f"### {script.name}")
            report.append(f"- Type: {script.script_type}")
            report.append(f"- Size: {script.size} bytes")
            report.append(f"- Lines: {script.lines}")
            report.append(f"- Functions: {', '.join(script.functions) if script.functions else 'None'}")
            report.append(f"- Status: {script.migration_status}")
            if script.migration_notes:
                report.append(f"- Notes: {script.migration_notes}")
            report.append("")
        
        return '\n'.join(report)
    
    def save_report(self, output_path: Optional[Path] = None) -> Path:
        """Save the migration report to a file."""
        if output_path is None:
            output_path = self.config.target_dir / "migration_report.md"
        
        report_content = self.generate_report()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        logger.info(f"Migration report saved to: {output_path}")
        return output_path
