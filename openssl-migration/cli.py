"""
OpenSSL Migration CLI

Command-line interface for migrating OpenSSL utility repositories
from shell/Perl scripts to modern Python implementations.
"""

import os
import sys
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
import click
import logging

from .core.migration_framework import MigrationFramework, MigrationConfig
from .core.script_converter import ScriptConverter
from .core.python_generator import PythonGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--config', help='Configuration file path')
@click.pass_context
def cli(ctx, verbose: bool, config: Optional[str]):
    """
    OpenSSL Migration Framework
    
    Migrate OpenSSL utility repositories from shell/Perl scripts
    to modern Python implementations using subprocess, pathlib, and click.
    
    Follows the Way of Python: Beautiful, Explicit, Simple.
    """
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    ctx.obj['config'] = config
    
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose mode enabled")


@cli.command()
@click.argument('source_repo', type=click.Path(exists=True, path_type=Path))
@click.option('--target-dir', '-t', type=click.Path(path_type=Path), 
              default=Path.cwd() / 'migrated', help='Target directory for migrated scripts')
@click.option('--script-types', multiple=True, 
              type=click.Choice(['shell', 'perl', 'python']),
              default=['shell', 'perl'], help='Types of scripts to migrate')
@click.option('--preserve-structure', is_flag=True, default=True,
              help='Preserve original directory structure')
@click.option('--add-tests', is_flag=True, default=True,
              help='Add test files for migrated scripts')
@click.option('--add-docs', is_flag=True, default=True,
              help='Add documentation for migrated scripts')
@click.option('--use-click', is_flag=True, default=True,
              help='Use click for command-line interfaces')
@click.option('--use-pathlib', is_flag=True, default=True,
              help='Use pathlib for file operations')
@click.option('--use-subprocess', is_flag=True, default=True,
              help='Use subprocess for external commands')
@click.option('--output-format', 
              type=click.Choice(['modern', 'compatible', 'minimal']),
              default='modern', help='Output format style')
@click.option('--dry-run', is_flag=True, help='Show what would be done without executing')
@click.pass_context
def analyze(ctx, source_repo: Path, target_dir: Path, script_types: List[str],
            preserve_structure: bool, add_tests: bool, add_docs: bool,
            use_click: bool, use_pathlib: bool, use_subprocess: bool,
            output_format: str, dry_run: bool):
    """
    Analyze a repository and identify scripts to migrate.
    
    SOURCE_REPO: Path to the repository to analyze
    """
    logger.info(f"Analyzing repository: {source_repo}")
    
    # Create migration configuration
    config = MigrationConfig(
        source_repo=str(source_repo),
        target_dir=target_dir,
        script_types=list(script_types),
        preserve_structure=preserve_structure,
        add_tests=add_tests,
        add_documentation=add_docs,
        use_click=use_click,
        use_pathlib=use_pathlib,
        use_subprocess=use_subprocess,
        output_format=output_format
    )
    
    # Initialize migration framework
    framework = MigrationFramework(config)
    
    try:
        # Analyze repository
        scripts = framework.analyze_repository(source_repo)
        
        if not scripts:
            click.echo("No scripts found to migrate.")
            return
        
        # Generate migration plan
        plan = framework.generate_migration_plan()
        
        # Display results
        click.echo(f"\n📊 Analysis Results:")
        click.echo(f"Total scripts found: {plan['total_scripts']}")
        
        for script_type, script_list in plan['by_type'].items():
            click.echo(f"  {script_type}: {len(script_list)} scripts")
        
        click.echo(f"\n⏱️  Estimated effort:")
        for script_type, effort in plan['estimated_effort'].items():
            click.echo(f"  {script_type}: {effort}")
        
        click.echo(f"\n💡 Recommendations:")
        for recommendation in plan['recommendations']:
            click.echo(f"  • {recommendation}")
        
        # Show detailed script list
        if ctx.obj['verbose']:
            click.echo(f"\n📋 Detailed Script List:")
            for script in scripts:
                click.echo(f"  {script.name} ({script.script_type})")
                click.echo(f"    Size: {script.size} bytes, Lines: {script.lines}")
                if script.functions:
                    click.echo(f"    Functions: {', '.join(script.functions)}")
                if script.dependencies:
                    click.echo(f"    Dependencies: {', '.join(script.dependencies[:5])}")
                click.echo()
        
        # Save analysis report
        if not dry_run:
            report_path = framework.save_report()
            click.echo(f"\n📄 Analysis report saved to: {report_path}")
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        click.echo(f"❌ Analysis failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('source_repo', type=click.Path(exists=True, path_type=Path))
@click.option('--target-dir', '-t', type=click.Path(path_type=Path),
              default=Path.cwd() / 'migrated', help='Target directory for migrated scripts')
@click.option('--script-types', multiple=True,
              type=click.Choice(['shell', 'perl', 'python']),
              default=['shell', 'perl'], help='Types of scripts to migrate')
@click.option('--preserve-structure', is_flag=True, default=True,
              help='Preserve original directory structure')
@click.option('--add-tests', is_flag=True, default=True,
              help='Add test files for migrated scripts')
@click.option('--add-docs', is_flag=True, default=True,
              help='Add documentation for migrated scripts')
@click.option('--use-click', is_flag=True, default=True,
              help='Use click for command-line interfaces')
@click.option('--use-pathlib', is_flag=True, default=True,
              help='Use pathlib for file operations')
@click.option('--use-subprocess', is_flag=True, default=True,
              help='Use subprocess for external commands')
@click.option('--output-format',
              type=click.Choice(['modern', 'compatible', 'minimal']),
              default='modern', help='Output format style')
@click.option('--parallel', '-j', default=1, help='Number of parallel migrations')
@click.option('--dry-run', is_flag=True, help='Show what would be done without executing')
@click.pass_context
def migrate(ctx, source_repo: Path, target_dir: Path, script_types: List[str],
            preserve_structure: bool, add_tests: bool, add_docs: bool,
            use_click: bool, use_pathlib: bool, use_subprocess: bool,
            output_format: str, parallel: int, dry_run: bool):
    """
    Migrate scripts from a repository to Python.
    
    SOURCE_REPO: Path to the repository to migrate
    """
    logger.info(f"Migrating repository: {source_repo}")
    
    # Create migration configuration
    config = MigrationConfig(
        source_repo=str(source_repo),
        target_dir=target_dir,
        script_types=list(script_types),
        preserve_structure=preserve_structure,
        add_tests=add_tests,
        add_documentation=add_docs,
        use_click=use_click,
        use_pathlib=use_pathlib,
        use_subprocess=use_subprocess,
        output_format=output_format
    )
    
    # Initialize migration framework
    framework = MigrationFramework(config)
    
    try:
        # Analyze repository first
        scripts = framework.analyze_repository(source_repo)
        
        if not scripts:
            click.echo("No scripts found to migrate.")
            return
        
        click.echo(f"Found {len(scripts)} scripts to migrate")
        
        if dry_run:
            click.echo("Dry run mode - showing what would be migrated:")
            for script in scripts:
                target_path = framework._get_target_path(script)
                click.echo(f"  {script.name} → {target_path}")
            return
        
        # Perform migration
        with click.progressbar(scripts, label='Migrating scripts') as bar:
            results = framework.migrate_all()
        
        # Display results
        click.echo(f"\n✅ Migration completed:")
        click.echo(f"  Total: {results['total']}")
        click.echo(f"  Completed: {results['completed']}")
        click.echo(f"  Failed: {results['failed']}")
        click.echo(f"  Skipped: {results['skipped']}")
        
        # Save migration report
        report_path = framework.save_report()
        click.echo(f"\n📄 Migration report saved to: {report_path}")
        
        if results['failed'] > 0:
            click.echo(f"\n⚠️  {results['failed']} scripts failed to migrate. Check the report for details.")
            sys.exit(1)
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        click.echo(f"❌ Migration failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('script_path', type=click.Path(exists=True, path_type=Path))
@click.option('--script-type', type=click.Choice(['shell', 'perl', 'python']),
              help='Type of script (auto-detected if not specified)')
@click.option('--output', '-o', type=click.Path(path_type=Path),
              help='Output file path (default: script_name.py)')
@click.option('--use-click', is_flag=True, default=True,
              help='Use click for command-line interface')
@click.option('--use-pathlib', is_flag=True, default=True,
              help='Use pathlib for file operations')
@click.option('--use-subprocess', is_flag=True, default=True,
              help='Use subprocess for external commands')
@click.option('--dry-run', is_flag=True, help='Show what would be done without executing')
@click.pass_context
def convert(ctx, script_path: Path, script_type: Optional[str], output: Optional[Path],
            use_click: bool, use_pathlib: bool, use_subprocess: bool, dry_run: bool):
    """
    Convert a single script to Python.
    
    SCRIPT_PATH: Path to the script to convert
    """
    logger.info(f"Converting script: {script_path}")
    
    # Auto-detect script type if not specified
    if not script_type:
        if script_path.suffix == '.sh':
            script_type = 'shell'
        elif script_path.suffix == '.pl':
            script_type = 'perl'
        elif script_path.suffix == '.py':
            script_type = 'python'
        else:
            click.echo("❌ Could not determine script type. Please specify --script-type", err=True)
            sys.exit(1)
    
    # Determine output path
    if not output:
        output = script_path.parent / f"{script_path.stem}.py"
    
    try:
        # Read script content
        with open(script_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Initialize converter
        converter = ScriptConverter()
        
        # Convert script
        if script_type == 'shell':
            python_code = converter.convert_shell_script(content, script_path.name)
        elif script_type == 'perl':
            python_code = converter.convert_perl_script(content, script_path.name)
        elif script_type == 'python':
            click.echo("Script is already Python. Consider using --modernize for improvements.")
            return
        else:
            click.echo(f"❌ Unsupported script type: {script_type}", err=True)
            sys.exit(1)
        
        if dry_run:
            click.echo("Dry run mode - showing converted code:")
            click.echo(python_code)
            return
        
        # Write converted script
        with open(output, 'w', encoding='utf-8') as f:
            f.write(python_code)
        
        click.echo(f"✅ Script converted successfully: {output}")
        
        # Show conversion statistics
        original_lines = len(content.split('\n'))
        converted_lines = len(python_code.split('\n'))
        
        click.echo(f"📊 Conversion statistics:")
        click.echo(f"  Original lines: {original_lines}")
        click.echo(f"  Converted lines: {converted_lines}")
        click.echo(f"  Expansion ratio: {converted_lines / original_lines:.2f}x")
        
    except Exception as e:
        logger.error(f"Conversion failed: {e}")
        click.echo(f"❌ Conversion failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('script_type', type=click.Choice(['installer', 'build_tool', 'performance_tool']))
@click.option('--output', '-o', type=click.Path(path_type=Path),
              help='Output file path')
@click.option('--name', help='Script name')
@click.option('--description', help='Script description')
@click.option('--dry-run', is_flag=True, help='Show what would be done without executing')
@click.pass_context
def generate(ctx, script_type: str, output: Optional[Path], name: Optional[str],
             description: Optional[str], dry_run: bool):
    """
    Generate a new Python script from template.
    
    SCRIPT_TYPE: Type of script to generate (installer, build_tool, performance_tool)
    """
    logger.info(f"Generating {script_type} script")
    
    # Determine output path
    if not output:
        script_name = name or f"openssl_{script_type}"
        output = Path(f"{script_name}.py")
    
    # Create configuration
    config = {
        'name': name or f"OpenSSL {script_type.replace('_', ' ').title()}",
        'description': description or f"OpenSSL {script_type.replace('_', ' ')} utility",
        'use_click': True,
        'use_pathlib': True,
        'use_subprocess': True
    }
    
    try:
        # Initialize generator
        generator = PythonGenerator()
        
        # Generate script
        python_code = generator.generate_custom_script(script_type, config)
        
        if dry_run:
            click.echo("Dry run mode - showing generated code:")
            click.echo(python_code)
            return
        
        # Write generated script
        with open(output, 'w', encoding='utf-8') as f:
            f.write(python_code)
        
        click.echo(f"✅ Script generated successfully: {output}")
        
        # Make script executable
        os.chmod(output, 0o755)
        
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        click.echo(f"❌ Generation failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('source_repo', type=click.Path(exists=True, path_type=Path))
@click.option('--output', '-o', type=click.Path(path_type=Path),
              default=Path.cwd() / 'migration_plan.json',
              help='Output file for migration plan')
@click.option('--format', 'output_format', type=click.Choice(['json', 'yaml', 'markdown']),
              default='json', help='Output format')
@click.pass_context
def plan(ctx, source_repo: Path, output: Path, output_format: str):
    """
    Generate a detailed migration plan for a repository.
    
    SOURCE_REPO: Path to the repository to plan migration for
    """
    logger.info(f"Generating migration plan for: {source_repo}")
    
    # Create migration configuration
    config = MigrationConfig(
        source_repo=str(source_repo),
        target_dir=Path.cwd() / 'migrated',
        script_types=['shell', 'perl', 'python'],
        preserve_structure=True,
        add_tests=True,
        add_documentation=True,
        use_click=True,
        use_pathlib=True,
        use_subprocess=True,
        output_format='modern'
    )
    
    # Initialize migration framework
    framework = MigrationFramework(config)
    
    try:
        # Analyze repository
        scripts = framework.analyze_repository(source_repo)
        
        if not scripts:
            click.echo("No scripts found to migrate.")
            return
        
        # Generate migration plan
        plan = framework.generate_migration_plan()
        
        # Add detailed script information
        plan['scripts'] = []
        for script in scripts:
            script_info = {
                'name': script.name,
                'path': str(script.path),
                'type': script.script_type,
                'size': script.size,
                'lines': script.lines,
                'functions': script.functions,
                'dependencies': script.dependencies,
                'description': script.description
            }
            plan['scripts'].append(script_info)
        
        # Save plan
        if output_format == 'json':
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(plan, f, indent=2)
        elif output_format == 'yaml':
            import yaml
            with open(output, 'w', encoding='utf-8') as f:
                yaml.dump(plan, f, default_flow_style=False)
        elif output_format == 'markdown':
            # Generate markdown report
            report = framework.generate_report()
            with open(output, 'w', encoding='utf-8') as f:
                f.write(report)
        
        click.echo(f"✅ Migration plan saved to: {output}")
        
        # Display summary
        click.echo(f"\n📊 Migration Plan Summary:")
        click.echo(f"  Total scripts: {plan['total_scripts']}")
        for script_type, count in plan['by_type'].items():
            click.echo(f"  {script_type}: {count}")
        
    except Exception as e:
        logger.error(f"Plan generation failed: {e}")
        click.echo(f"❌ Plan generation failed: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()
