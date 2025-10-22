#!/usr/bin/env python3
"""
OpenSSL Repository Migration Example

This script demonstrates how to use the OpenSSL Migration Framework
to migrate utility repositories from shell/Perl to modern Python.

Usage:
    python migrate_openssl_repos.py --help
    python migrate_openssl_repos.py --analyze openssl/installer
    python migrate_openssl_repos.py --migrate openssl/tools --target migrated-tools
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import click
import logging

# Add the parent directory to the path to import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from openssl_migration.core.migration_framework import MigrationFramework, MigrationConfig
from openssl_migration.installer.migrator import OpenSSLInstallerMigrator, InstallerConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.pass_context
def cli(ctx, verbose: bool):
    """OpenSSL Repository Migration Example"""
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)


@cli.command()
@click.argument('repo_path', type=click.Path(exists=True, path_type=Path))
@click.option('--output', '-o', type=click.Path(path_type=Path),
              help='Output file for analysis report')
@click.option('--format', 'output_format', 
              type=click.Choice(['json', 'markdown', 'yaml']),
              default='json', help='Output format')
@click.pass_context
def analyze(ctx, repo_path: Path, output: Optional[Path], output_format: str):
    """
    Analyze an OpenSSL repository and identify scripts to migrate.
    
    REPO_PATH: Path to the repository to analyze
    """
    logger.info(f"Analyzing repository: {repo_path}")
    
    # Create migration configuration
    config = MigrationConfig(
        source_repo=str(repo_path),
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
        scripts = framework.analyze_repository(repo_path)
        
        if not scripts:
            click.echo("No scripts found to migrate.")
            return
        
        # Generate migration plan
        plan = framework.generate_migration_plan()
        
        # Display results
        click.echo(f"\n📊 Analysis Results for {repo_path.name}:")
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
        if output:
            if output_format == 'json':
                with open(output, 'w', encoding='utf-8') as f:
                    json.dump(plan, f, indent=2, default=str)
            elif output_format == 'markdown':
                report = framework.generate_report()
                with open(output, 'w', encoding='utf-8') as f:
                    f.write(report)
            elif output_format == 'yaml':
                import yaml
                with open(output, 'w', encoding='utf-8') as f:
                    yaml.dump(plan, f, default_flow_style=False)
            
            click.echo(f"\n📄 Analysis report saved to: {output}")
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        click.echo(f"❌ Analysis failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('repo_path', type=click.Path(exists=True, path_type=Path))
@click.option('--target', '-t', type=click.Path(path_type=Path),
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
def migrate(ctx, repo_path: Path, target: Path, script_types: List[str],
            preserve_structure: bool, add_tests: bool, add_docs: bool,
            use_click: bool, use_pathlib: bool, use_subprocess: bool,
            output_format: str, parallel: int, dry_run: bool):
    """
    Migrate scripts from an OpenSSL repository to Python.
    
    REPO_PATH: Path to the repository to migrate
    """
    logger.info(f"Migrating repository: {repo_path}")
    
    # Create migration configuration
    config = MigrationConfig(
        source_repo=str(repo_path),
        target_dir=target,
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
        scripts = framework.analyze_repository(repo_path)
        
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
@click.argument('repo_path', type=click.Path(exists=True, path_type=Path))
@click.option('--target', '-t', type=click.Path(path_type=Path),
              default=Path.cwd() / 'migrated-installer', 
              help='Target directory for migrated installer')
@click.option('--preserve-perl-compatibility', is_flag=True,
              help='Preserve Perl compatibility features')
@click.option('--add-modern-features', is_flag=True, default=True,
              help='Add modern Python features')
@click.option('--use-conan-integration', is_flag=True, default=True,
              help='Add Conan package manager integration')
@click.option('--add-docker-support', is_flag=True, default=True,
              help='Add Docker container support')
@click.option('--create-package', is_flag=True,
              help='Create a complete installer package')
@click.option('--dry-run', is_flag=True, help='Show what would be done without executing')
@click.pass_context
def migrate_installer(ctx, repo_path: Path, target: Path, preserve_perl_compatibility: bool,
                     add_modern_features: bool, use_conan_integration: bool,
                     add_docker_support: bool, create_package: bool, dry_run: bool):
    """
    Migrate OpenSSL installer scripts with specialized handling.
    
    REPO_PATH: Path to the OpenSSL installer repository
    """
    logger.info(f"Migrating OpenSSL installer: {repo_path}")
    
    # Create installer migration configuration
    config = InstallerConfig(
        source_repo=str(repo_path),
        target_dir=target,
        preserve_perl_compatibility=preserve_perl_compatibility,
        add_modern_features=add_modern_features,
        use_conan_integration=use_conan_integration,
        add_docker_support=add_docker_support
    )
    
    # Initialize installer migrator
    migrator = OpenSSLInstallerMigrator(config)
    
    try:
        if dry_run:
            click.echo("Dry run mode - showing what would be migrated:")
            # This would show what would be migrated
            click.echo("  Installer scripts would be converted to Python")
            click.echo("  Modern features would be added")
            if use_conan_integration:
                click.echo("  Conan integration would be added")
            if add_docker_support:
                click.echo("  Docker support would be added")
            return
        
        # Migrate installer scripts
        results = migrator.migrate_installer_scripts()
        
        # Display results
        click.echo(f"\n✅ Installer migration completed:")
        click.echo(f"  Total: {results['total']}")
        click.echo(f"  Migrated: {results['migrated']}")
        click.echo(f"  Failed: {results['failed']}")
        click.echo(f"  Skipped: {results['skipped']}")
        
        # Generate modern installer
        modern_installer_path = target / 'openssl_installer.py'
        if migrator.generate_modern_installer(modern_installer_path):
            click.echo(f"  Modern installer generated: {modern_installer_path}")
        
        # Create installer package if requested
        if create_package:
            package_dir = target / 'openssl-installer-package'
            if migrator.create_installer_package(package_dir):
                click.echo(f"  Installer package created: {package_dir}")
        
        if results['failed'] > 0:
            click.echo(f"\n⚠️  {results['failed']} scripts failed to migrate.")
            sys.exit(1)
        
    except Exception as e:
        logger.error(f"Installer migration failed: {e}")
        click.echo(f"❌ Installer migration failed: {e}", err=True)
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
def convert_script(ctx, script_path: Path, script_type: Optional[str], output: Optional[Path],
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
        
        # Import converter
        from openssl_migration.core.script_converter import ScriptConverter
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
def generate_script(ctx, script_type: str, output: Optional[Path], name: Optional[str],
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
        # Import generator
        from openssl_migration.core.python_generator import PythonGenerator
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
@click.option('--repos', multiple=True, 
              help='Repository paths to migrate (can be specified multiple times)')
@click.option('--target-base', type=click.Path(path_type=Path),
              default=Path.cwd() / 'migrated-repos',
              help='Base directory for migrated repositories')
@click.option('--config-file', type=click.Path(exists=True, path_type=Path),
              help='Configuration file for migration settings')
@click.option('--parallel', '-j', default=1, help='Number of parallel migrations')
@click.option('--dry-run', is_flag=True, help='Show what would be done without executing')
@click.pass_context
def migrate_all(ctx, repos: List[str], target_base: Path, config_file: Optional[Path],
                parallel: int, dry_run: bool):
    """
    Migrate multiple OpenSSL repositories in batch.
    
    This command can migrate multiple repositories at once using
    configuration files and batch processing.
    """
    logger.info("Starting batch migration of OpenSSL repositories")
    
    # Load configuration if provided
    config = {}
    if config_file:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    
    # Default repositories if none specified
    if not repos:
        repos = [
            'openssl/installer',
            'openssl/tools',
            'openssl/perftools',
            'openssl/release-metadata',
            'openssl/openssl-docs',
            'openssl/openssl-book'
        ]
    
    # Process each repository
    results = {}
    
    for repo in repos:
        repo_path = Path(repo)
        if not repo_path.exists():
            click.echo(f"⚠️  Repository not found: {repo_path}")
            continue
        
        click.echo(f"\n🔄 Processing repository: {repo_path.name}")
        
        # Determine target directory
        target_dir = target_base / repo_path.name
        
        # Determine script types based on repository
        script_types = ['shell', 'perl']
        if repo_path.name in ['installer']:
            script_types = ['perl', 'shell']
        elif repo_path.name in ['tools']:
            script_types = ['shell', 'perl']
        elif repo_path.name in ['perftools']:
            script_types = ['shell', 'python']
        
        # Create migration configuration
        migration_config = MigrationConfig(
            source_repo=str(repo_path),
            target_dir=target_dir,
            script_types=script_types,
            preserve_structure=True,
            add_tests=True,
            add_documentation=True,
            use_click=True,
            use_pathlib=True,
            use_subprocess=True,
            output_format='modern'
        )
        
        # Initialize migration framework
        framework = MigrationFramework(migration_config)
        
        try:
            if dry_run:
                click.echo(f"  Dry run - would migrate to: {target_dir}")
                continue
            
            # Analyze and migrate
            scripts = framework.analyze_repository(repo_path)
            if scripts:
                migration_results = framework.migrate_all()
                results[repo_path.name] = migration_results
                
                click.echo(f"  ✅ Completed: {migration_results['completed']}")
                click.echo(f"  ❌ Failed: {migration_results['failed']}")
            else:
                click.echo(f"  ℹ️  No scripts found to migrate")
                results[repo_path.name] = {'total': 0, 'completed': 0, 'failed': 0, 'skipped': 0}
        
        except Exception as e:
            logger.error(f"Failed to migrate {repo_path.name}: {e}")
            click.echo(f"  ❌ Failed: {e}")
            results[repo_path.name] = {'error': str(e)}
    
    # Display summary
    click.echo(f"\n📊 Batch Migration Summary:")
    total_completed = 0
    total_failed = 0
    
    for repo_name, result in results.items():
        if 'error' in result:
            click.echo(f"  {repo_name}: ❌ {result['error']}")
        else:
            completed = result.get('completed', 0)
            failed = result.get('failed', 0)
            total_completed += completed
            total_failed += failed
            click.echo(f"  {repo_name}: ✅ {completed} completed, ❌ {failed} failed")
    
    click.echo(f"\n🎯 Overall Results:")
    click.echo(f"  Total completed: {total_completed}")
    click.echo(f"  Total failed: {total_failed}")
    
    if total_failed > 0:
        click.echo(f"\n⚠️  {total_failed} scripts failed to migrate.")
        sys.exit(1)


if __name__ == '__main__':
    cli()
