#!/usr/bin/env python3
"""
OpenSSL Configure Script - Python Implementation
Replaces the traditional Perl Configure script with a Python implementation
"""

import sys
import os
import platform
from typing import List, Dict, Set, Optional


class OpenSSLConfigurer:
    """OpenSSL configuration generator."""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.machine = platform.machine().lower()
        self.is_64bit = sys.maxsize > 2**32
        
        # Default build configuration
        self.build_config = {
            'shared': True,
            'static': True,
            'threads': True,
            'asm': True,
            'fips': False,
            'no_shared': False,
            'no_static': False,
            'no_threads': False,
            'no_asm': False,
            'enable_fips': False,
        }
        
        self.enabled_features: Set[str] = set()
        self.disabled_features: Set[str] = set()
        self.defines: Dict[str, str] = {}
        self.includes: List[str] = []
        self.libdirs: List[str] = []
        self.libs: List[str] = []
        self.target: Optional[str] = None
        self.debug = False
        self.quiet = False

    def detect_platform(self) -> str:
        """Detect the build platform and return appropriate target."""
        system = self.system
        machine = self.machine

        # Platform mapping
        platform_map = {
            ('linux', 'x86_64'): 'linux-x86_64',
            ('linux', 'i386'): 'linux-x86',
            ('linux', 'i686'): 'linux-x86',
            ('linux', 'aarch64'): 'linux-aarch64',
            ('linux', 'armv7l'): 'linux-armv4',
            ('darwin', 'x86_64'): 'darwin64-x86_64-cc',
            ('darwin', 'arm64'): 'darwin64-arm64-cc',
            ('freebsd', 'x86_64'): 'BSD-x86_64',
            ('openbsd', 'x86_64'): 'BSD-x86_64',
            ('netbsd', 'x86_64'): 'BSD-x86_64',
            ('windows', 'x86_64'): 'VC-WIN64A',
            ('windows', 'i386'): 'VC-WIN32',
            ('windows', 'amd64'): 'VC-WIN64A',
        }

        return platform_map.get((system, machine), 'linux-x86_64')

    def parse_arguments(self, args: List[str]) -> None:
        """Parse command line arguments."""
        i = 0
        while i < len(args):
            arg = args[i]

            if arg.startswith('no-'):
                # Disabled feature
                feature = arg[3:]  # Remove 'no-' prefix
                self.disabled_features.add(feature)
                if feature in self.build_config:
                    self.build_config[feature] = False
            elif arg.startswith('enable-'):
                # Enabled feature
                feature = arg[7:]  # Remove 'enable-' prefix
                self.enabled_features.add(feature)
                if f"enable_{feature}" in self.build_config:
                    self.build_config[f"enable_{feature}"] = True
                elif feature in self.build_config:
                    self.build_config[feature] = True
            elif arg.startswith('-D'):
                # Define
                define = arg[2:]
                if '=' in define:
                    key, value = define.split('=', 1)
                    self.defines[key] = value
                else:
                    self.defines[define] = ''
            elif arg.startswith('-I'):
                # Include directory
                self.includes.append(arg[2:])
            elif arg.startswith('-L'):
                # Library directory
                self.libdirs.append(arg[2:])
            elif arg.startswith('-l'):
                # Library
                self.libs.append(arg[2:])
            elif arg == '--help' or arg == '-h':
                self.show_help()
                sys.exit(0)
            elif arg == '--debug':
                self.debug = True
            elif arg == '--quiet':
                self.quiet = True
            elif not arg.startswith('-'):
                # Target/platform specification
                if not self.target:
                    self.target = arg
                else:
                    print(f"Warning: Multiple targets specified, using {self.target}", file=sys.stderr)
            else:
                print(f"Warning: Unknown option {arg}", file=sys.stderr)

            i += 1

    def show_help(self) -> None:
        """Display help information."""
        help_text = """
OpenSSL Configure Script

Usage: python configure.py [options] [target]

Options:
    no-<feature>        Disable feature
    enable-<feature>    Enable feature
    -D<define>          Add preprocessor define
    -I<dir>            Add include directory
    -L<dir>            Add library directory
    -l<lib>            Add library
    --debug            Enable debug output
    --quiet            Suppress non-essential output
    --help             Show this help

Common features:
    no-shared          Build static libraries only
    no-threads         Disable threading support
    no-asm            Disable assembly optimizations
    enable-fips        Enable FIPS mode

Common targets:
    linux-x86_64       Linux x86_64
    darwin64-x86_64-cc macOS x86_64
    VC-WIN64A         Windows x86_64
"""
        print(help_text)

    def validate_configuration(self) -> bool:
        """Validate the build configuration."""
        errors = []

        # Check for conflicting options
        if self.build_config['no_shared'] and self.build_config['shared']:
            errors.append("Cannot specify both 'no-shared' and 'shared'")

        if self.build_config['no_threads'] and self.build_config['threads']:
            errors.append("Cannot specify both 'no-threads' and 'threads'")

        if self.build_config['no_asm'] and self.build_config['asm']:
            errors.append("Cannot specify both 'no-asm' and 'asm'")

        if errors:
            for error in errors:
                print(f"Error: {error}", file=sys.stderr)
            return False

        return True

    def generate_config_files(self) -> None:
        """Generate configuration files."""
        self.generate_configdata_pm()
        self.generate_buildinfo_h()
        self.generate_makefile()

    def generate_configdata_pm(self) -> None:
        """Generate configdata.pm file."""
        if not self.quiet:
            print("Generating configdata.pm...")

        with open('configdata.pm', 'w') as f:
            f.write("# Generated by configure.py\n")
            f.write("# Do not edit manually\n\n")

            f.write("package configdata;\n\n")

            # Write configuration data
            f.write("our %config = (\n")
            for key, value in self.build_config.items():
                f.write(f"    '{key}' => {value},\n")
            f.write(");\n\n")

            # Write target information
            f.write(f"our $target = '{self.target or 'unknown'}';\n\n")

            # Write defines
            f.write("our %defines = (\n")
            for key, value in self.defines.items():
                f.write(f"    '{key}' => '{value}',\n")
            f.write(");\n\n")

            f.write("1;\n")

    def generate_buildinfo_h(self) -> None:
        """Generate buildinf.h header file."""
        if not self.quiet:
            print("Generating buildinf.h...")

        # Create include directory if it doesn't exist
        os.makedirs('include/openssl', exist_ok=True)

        # Import the build info generator
        sys.path.insert(0, 'util/python')
        try:
            from mkbuildinf import BuildInfoGenerator

            generator = BuildInfoGenerator()
            generator.quiet = self.quiet
            info = generator.get_build_info()
            generator.generate_header_file(info, 'include/openssl/buildinf.h')
        except ImportError:
            # Fallback if mkbuildinf.py is not available
            with open('include/openssl/buildinf.h', 'w') as f:
                f.write("/* Generated build information */\n")
                f.write("#define OPENSSL_BUILDINFO_PLATFORM \"unknown\"\n")

    def generate_makefile(self) -> None:
        """Generate or update Makefile."""
        if not self.quiet:
            print("Generating Makefile...")

        # For now, create a basic Makefile template
        # In a full implementation, this would process build.info files
        makefile_content = """
# Generated by configure.py
# Do not edit manually

PLATFORM = {platform}
CONFIG = {config}
DEFINES = {defines}
INCLUDES = {includes}
LIBDIRS = {libdirs}
LIBS = {libs}

all: build

build:
\t@echo "Building OpenSSL..."
\t# Build commands would go here

clean:
\t@echo "Cleaning..."
\t# Clean commands would go here

install:
\t@echo "Installing..."
\t# Install commands would go here

.PHONY: all build clean install
"""

        config_str = ' '.join(f"{k}={v}" for k, v in self.build_config.items())
        defines_str = ' '.join(f"-D{k}={v}" for k, v in self.defines.items())
        includes_str = ' '.join(f"-I{d}" for d in self.includes)
        libdirs_str = ' '.join(f"-L{d}" for d in self.libdirs)
        libs_str = ' '.join(f"-l{l}" for l in self.libs)

        makefile_content = makefile_content.format(
            platform=self.target or 'unknown',
            config=config_str,
            defines=defines_str,
            includes=includes_str,
            libdirs=libdirs_str,
            libs=libs_str
        )

        with open('Makefile', 'w') as f:
            f.write(makefile_content)

    def show_configuration_summary(self) -> None:
        """Display configuration summary."""
        print("\n" + "="*50)
        print("OpenSSL Configuration Summary")
        print("="*50)
        print(f"Target: {self.target}")
        print(f"Platform: {self.system} {self.machine}")
        print(f"64-bit: {self.is_64bit}")

        print("\nBuild Options:")
        for key, value in sorted(self.build_config.items()):
            print(f"  {key}: {value}")

        if self.defines:
            print("\nDefines:")
            for key, value in sorted(self.defines.items()):
                print(f"  {key}={value}")

        if self.includes:
            print("\nInclude directories:")
            for inc in self.includes:
                print(f"  {inc}")

        if self.libdirs:
            print("\nLibrary directories:")
            for libdir in self.libdirs:
                print(f"  {libdir}")

        if self.libs:
            print("\nLibraries:")
            for lib in self.libs:
                print(f"  {lib}")

        print("\nConfiguration completed successfully!")
        print("Run 'make' to build OpenSSL.")

    def run(self, args: List[str]) -> int:
        """Main execution method."""
        # Detect platform if no target specified
        if not self.target:
            self.target = self.detect_platform()

        # Parse command line arguments
        self.parse_arguments(args)

        if self.debug:
            print(f"Debug: Target = {self.target}")
            print(f"Debug: System = {self.system}")
            print(f"Debug: Machine = {self.machine}")

        # Validate configuration
        if not self.validate_configuration():
            return 1

        # Generate configuration files
        self.generate_config_files()

        # Show summary
        if not self.quiet:
            self.show_configuration_summary()

        return 0


def main():
    """Main entry point."""
    configurer = OpenSSLConfigurer()
    sys.exit(configurer.run(sys.argv[1:]))


if __name__ == '__main__':
    main()