#!/usr/bin/env python3
"""
OpenSSL Migration Framework Demo

This script demonstrates the capabilities of the OpenSSL Migration Framework
by creating sample scripts and showing the migration process.
"""

import os
import sys
import tempfile
from pathlib import Path
import click
import logging

# Add the current directory to the path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from core.migration_framework import MigrationFramework, MigrationConfig
    from core.script_converter import ScriptConverter
    from core.python_generator import PythonGenerator
    from installer.migrator import OpenSSLInstallerMigrator, InstallerConfig
except ImportError:
    # Handle relative imports for demo
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    
    from core.migration_framework import MigrationFramework, MigrationConfig
    from core.script_converter import ScriptConverter
    from core.python_generator import PythonGenerator
    from installer.migrator import OpenSSLInstallerMigrator, InstallerConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_sample_scripts(temp_dir: Path) -> None:
    """Create sample scripts for demonstration."""
    
    # Create sample shell script
    shell_script = temp_dir / "install.sh"
    shell_content = '''#!/bin/bash
# OpenSSL Installation Script
PREFIX="/usr/local"
echo "Installing OpenSSL to $PREFIX"

# Check if source directory exists
if [ ! -d "openssl-source" ]; then
    echo "Error: openssl-source directory not found"
    exit 1
fi

cd openssl-source

# Configure OpenSSL
echo "Configuring OpenSSL..."
./Configure --prefix=$PREFIX --openssldir=$PREFIX/ssl

# Build OpenSSL
echo "Building OpenSSL..."
make -j$(nproc)

# Run tests
echo "Running tests..."
make test

# Install OpenSSL
echo "Installing OpenSSL..."
sudo make install

echo "OpenSSL installation completed successfully"
'''
    
    with open(shell_script, 'w') as f:
        f.write(shell_content)
    os.chmod(shell_script, 0o755)
    
    # Create sample Perl script
    perl_script = temp_dir / "configure.pl"
    perl_content = '''#!/usr/bin/perl
use strict;
use warnings;
use File::Path qw(make_path);
use File::Copy;

my $prefix = "/usr/local";
my $openssl_dir = "openssl-source";

print "Configuring OpenSSL installation\\n";

# Check if source directory exists
unless (-d $openssl_dir) {
    die "Error: $openssl_dir directory not found\\n";
}

# Change to source directory
chdir $openssl_dir or die "Cannot change to $openssl_dir: $!\\n";

# Run configure
print "Running Configure script...\\n";
my $configure_cmd = "./Configure --prefix=$prefix --openssldir=$prefix/ssl";
system($configure_cmd) == 0 or die "Configure failed: $!\\n";

# Create directories
print "Creating installation directories...\\n";
make_path("$prefix/bin", "$prefix/lib", "$prefix/include");

print "Configuration completed successfully\\n";
'''
    
    with open(perl_script, 'w') as f:
        f.write(perl_content)
    os.chmod(perl_script, 0o755)
    
    # Create sample Python script (for modernization)
    python_script = temp_dir / "build.py"
    python_content = '''#!/usr/bin/env python3
import os
import sys
import subprocess

def build_openssl():
    """Build OpenSSL from source."""
    print("Building OpenSSL...")
    
    # Change to source directory
    os.chdir("openssl-source")
    
    # Run make
    result = subprocess.run(["make"], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Build failed: {result.stderr}")
        sys.exit(1)
    
    print("Build completed successfully")

if __name__ == "__main__":
    build_openssl()
'''
    
    with open(python_script, 'w') as f:
        f.write(python_content)
    os.chmod(python_script, 0o755)
    
    logger.info(f"Created sample scripts in {temp_dir}")


@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def demo(verbose: bool):
    """Demonstrate the OpenSSL Migration Framework."""
    
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    click.echo("🚀 OpenSSL Migration Framework Demo")
    click.echo("=" * 50)
    
    # Create temporary directory for demo
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create sample scripts
        click.echo("\n📝 Creating sample scripts...")
        create_sample_scripts(temp_path)
        
        # List created scripts
        click.echo("\n📋 Sample scripts created:")
        for script in temp_path.glob("*"):
            click.echo(f"  {script.name} ({script.stat().st_size} bytes)")
        
        # Demo 1: Analyze repository
        click.echo("\n🔍 Demo 1: Repository Analysis")
        click.echo("-" * 30)
        
        config = MigrationConfig(
            source_repo=str(temp_path),
            target_dir=temp_path / "migrated",
            script_types=['shell', 'perl', 'python'],
            preserve_structure=True,
            add_tests=True,
            add_documentation=True,
            use_click=True,
            use_pathlib=True,
            use_subprocess=True,
            output_format='modern'
        )
        
        framework = MigrationFramework(config)
        scripts = framework.analyze_repository(temp_path)
        
        click.echo(f"Found {len(scripts)} scripts:")
        for script in scripts:
            click.echo(f"  {script.name} ({script.script_type}) - {script.lines} lines")
            if script.functions:
                click.echo(f"    Functions: {', '.join(script.functions)}")
            if script.dependencies:
                click.echo(f"    Dependencies: {', '.join(script.dependencies[:3])}")
        
        # Generate migration plan
        plan = framework.generate_migration_plan()
        click.echo(f"\n📊 Migration Plan:")
        click.echo(f"  Total scripts: {plan['total_scripts']}")
        for script_type, effort in plan['estimated_effort'].items():
            click.echo(f"  {script_type}: {effort}")
        
        # Demo 2: Convert single script
        click.echo("\n🔄 Demo 2: Single Script Conversion")
        click.echo("-" * 40)
        
        converter = ScriptConverter()
        
        # Convert shell script
        shell_script = temp_path / "install.sh"
        with open(shell_script, 'r') as f:
            shell_content = f.read()
        
        click.echo("Converting shell script to Python...")
        python_code = converter.convert_shell_script(shell_content, "install.sh")
        
        # Save converted script
        converted_script = temp_path / "install_converted.py"
        with open(converted_script, 'w') as f:
            f.write(python_code)
        
        click.echo(f"✅ Converted script saved: {converted_script.name}")
        click.echo(f"   Original: {len(shell_content.split())} lines")
        click.echo(f"   Converted: {len(python_code.split())} lines")
        
        # Demo 3: Generate new script
        click.echo("\n🛠️  Demo 3: Generate New Script")
        click.echo("-" * 35)
        
        generator = PythonGenerator()
        
        click.echo("Generating new installer script...")
        config_dict = {
            'name': 'OpenSSL Demo Installer',
            'description': 'Demo installer generated by the framework',
            'use_click': True,
            'use_pathlib': True,
            'use_subprocess': True
        }
        
        generated_code = generator.generate_installer_script(config_dict)
        
        # Save generated script
        generated_script = temp_path / "generated_installer.py"
        with open(generated_script, 'w') as f:
            f.write(generated_code)
        
        click.echo(f"✅ Generated script saved: {generated_script.name}")
        click.echo(f"   Generated: {len(generated_code.split())} lines")
        
        # Demo 4: Installer migration
        click.echo("\n📦 Demo 4: Installer Migration")
        click.echo("-" * 35)
        
        installer_config = InstallerConfig(
            source_repo=str(temp_path),
            target_dir=temp_path / "migrated-installer",
            preserve_perl_compatibility=False,
            add_modern_features=True,
            use_conan_integration=True,
            add_docker_support=True
        )
        
        installer_migrator = OpenSSLInstallerMigrator(installer_config)
        
        click.echo("Migrating installer scripts...")
        results = installer_migrator.migrate_installer_scripts()
        
        click.echo(f"✅ Installer migration completed:")
        click.echo(f"   Total: {results['total']}")
        click.echo(f"   Migrated: {results['migrated']}")
        click.echo(f"   Failed: {results['failed']}")
        
        # Demo 5: Show generated files
        click.echo("\n📁 Demo 5: Generated Files")
        click.echo("-" * 30)
        
        migrated_dir = temp_path / "migrated"
        if migrated_dir.exists():
            click.echo("Migrated files:")
            for file in migrated_dir.rglob("*.py"):
                click.echo(f"  {file.relative_to(temp_path)}")
        
        installer_dir = temp_path / "migrated-installer"
        if installer_dir.exists():
            click.echo("Installer migration files:")
            for file in installer_dir.rglob("*.py"):
                click.echo(f"  {file.relative_to(temp_path)}")
        
        # Demo 6: Show code snippets
        click.echo("\n💻 Demo 6: Code Snippets")
        click.echo("-" * 30)
        
        if converted_script.exists():
            click.echo("Converted shell script snippet:")
            with open(converted_script, 'r') as f:
                lines = f.readlines()
                for i, line in enumerate(lines[:20], 1):
                    click.echo(f"  {i:2d}: {line.rstrip()}")
                if len(lines) > 20:
                    click.echo(f"  ... ({len(lines) - 20} more lines)")
        
        click.echo("\n🎉 Demo completed successfully!")
        click.echo("\nThe OpenSSL Migration Framework provides:")
        click.echo("  ✅ Repository analysis and planning")
        click.echo("  ✅ Script conversion (shell/Perl → Python)")
        click.echo("  ✅ Modern Python code generation")
        click.echo("  ✅ Specialized installer migration")
        click.echo("  ✅ Comprehensive error handling")
        click.echo("  ✅ CLI interface with click")
        click.echo("  ✅ Following the Way of Python principles")


if __name__ == '__main__':
    demo()
