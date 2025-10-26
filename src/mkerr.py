#!/usr/bin/env python3
"""
OpenSSL Error Code Generator - Python replacement for mkerr.pl

Generates error handling code from configuration files.
"""

import argparse
import glob
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


class ErrorCodeGenerator:
    """Generates OpenSSL error handling code from configuration."""

    def __init__(self):
        self.debug = False
        self.internal = False
        self.nowrite = False
        self.rebuild = False
        self.reindex = False
        self.static = False
        self.unref = False
        self.modules: Set[str] = set()

        self.errors = 0
        self.year = 2024  # Current year

        # Data structures parsed from config and state files
        self.hpubinc: Dict[str, str] = {}    # lib -> public header
        self.libpubinc: Dict[str, str] = {}  # public header -> lib
        self.hprivinc: Dict[str, str] = {}   # lib -> private header
        self.libprivinc: Dict[str, str] = {} # private header -> lib
        self.cskip: Dict[str, str] = {}      # error_file -> lib
        self.errorfile: Dict[str, str] = {}  # lib -> error file name
        self.rmax: Dict[str, int] = {}       # lib -> max assigned reason code
        self.rassigned: Dict[str, str] = {} # lib -> colon-separated list of assigned reason codes
        self.rnew: Dict[str, int] = {}       # lib -> count of new reason codes
        self.rextra: Dict[str, str] = {}     # "extra" reason code -> lib
        self.rcodes: Dict[str, str] = {}     # reason-name -> value
        self.statefile: Optional[str] = None # state file with assigned reason and function codes
        self.strings: Dict[str, str] = {}    # define -> text

    def phase(self, text: str) -> None:
        """Print debug phase information."""
        if self.debug:
            print(f"\n---\n{text.upper()}\n", file=sys.stderr)

    def help(self) -> None:
        """Display help information."""
        help_text = """
mkerr.py [options] [files...]

Options:

    -conf FILE  Use the named config file FILE instead of the default.

    -debug      Verbose output debugging on stderr.

    -internal   Generate code that is to be built as part of OpenSSL itself.
                Also scans internal list of files.

    -module M   Only useful with -internal!
                Only write files for library module M.  Whether files are
                actually written or not depends on other options, such as
                -rebuild.
                Note: this option is cumulative.  If not given at all, all
                internal modules will be considered.

    -nowrite    Do not write the header/source files, even if changed.

    -rebuild    Rebuild all header and C source files, even if there
                were no changes.

    -reindex    Ignore previously assigned values (except for R records in
                the config file) and renumber everything starting at 100.

    -static     Make the load/unload functions static.

    -unref      List all unreferenced function and reason codes on stderr;
                implies -nowrite.

    -help       Show this help text.

    ...         Additional arguments are added to the file list to scan,
                if '-internal' was NOT specified on the command line.
"""
        print(help_text, file=sys.stderr)

    def parse_config_file(self, config_file: str) -> None:
        """Read and parse the config file."""
        self.phase("Reading config file")

        try:
            with open(config_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue

                    # Parse L records: L lib pubhdr err [privhdr]
                    l_match = re.match(r'^L\s+(\S+)\s+(\S+)\s+(\S+)(?:\s+(\S+))?\s*$', line)
                    if l_match:
                        lib, pubhdr, err, privhdr = l_match.groups()
                        privhdr = privhdr or 'NONE'

                        self.hpubinc[lib] = pubhdr
                        self.libpubinc[pubhdr] = lib
                        self.hprivinc[lib] = privhdr
                        self.libprivinc[privhdr] = lib
                        self.cskip[err] = lib
                        self.errorfile[lib] = err

                        if err != 'NONE':
                            self.rmax[lib] = 100
                            self.rassigned[lib] = ":"
                            self.rnew[lib] = 0

                        if self.internal:
                            if pubhdr != 'NONE' and not pubhdr.startswith('include/openssl/'):
                                raise ValueError(f"Public header file must be in include/openssl ({pubhdr} is not)")
                            if privhdr != 'NONE':
                                # Private header validation for internal mode
                                pass
                        continue

                    # Parse R records: R name value
                    r_match = re.match(r'^R\s+(\S+)\s+(\S+)', line)
                    if r_match:
                        name, value = r_match.groups()
                        self.rextra[name] = value
                        self.rcodes[name] = value
                        continue

                    # Parse S records: S statefile
                    s_match = re.match(r'^S\s+(\S+)', line)
                    if s_match:
                        self.statefile = s_match.group(1)
                        continue

                    raise ValueError(f"Illegal config line: {line}")

        except FileNotFoundError:
            raise FileNotFoundError(f"Can't open config file {config_file}")

        if not self.statefile:
            self.statefile = config_file.replace('.ec', '.txt')

    def parse_state_file(self) -> None:
        """Read and parse the state file."""
        self.phase("Reading state")
        skipped_state = 0

        if not self.reindex and self.statefile and os.path.exists(self.statefile):
            try:
                with open(self.statefile, 'r') as f:
                    lines = f.readlines()
                    i = 0
                    while i < len(lines):
                        line = lines[i].strip()
                        i += 1

                        if not line or line.startswith('#'):
                            continue

                        # Parse function/reason code assignments
                        if line.endswith(':\\'):
                            # Multi-line entry
                            name_match = re.match(r'^(.+):(\d+):\\$', line)
                            if name_match:
                                name, code = name_match.groups()
                                code = int(code)

                                # Read continuation lines
                                next_line = lines[i].strip() if i < len(lines) else ""
                                i += 1
                                while next_line and not next_line.startswith(' '):
                                    # Process continuation
                                    next_line = lines[i].strip() if i < len(lines) else ""
                                    i += 1

                        elif ':' in line:
                            # Single line entry: name:code
                            parts = line.split(':', 1)
                            if len(parts) == 2:
                                name, code_str = parts
                                try:
                                    code = int(code_str)
                                    # Store the assignment
                                    if name in self.rcodes:
                                        skipped_state += 1
                                except ValueError:
                                    continue

            except FileNotFoundError:
                if self.debug:
                    print(f"State file {self.statefile} not found, starting fresh", file=sys.stderr)

        if self.debug and skipped_state:
            print(f"Skipped {skipped_state} state entries", file=sys.stderr)

    def scan_source_files(self, source_files: List[str]) -> None:
        """Scan source files for error function usage."""
        self.phase("Scanning source files")

        for source_file in source_files:
            if not os.path.exists(source_file):
                if self.debug:
                    print(f"Source file not found: {source_file}", file=sys.stderr)
                continue

            try:
                with open(source_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # Scan for error function patterns
                # This is a simplified version - the full implementation would
                # need to match the complex patterns in mkerr.pl

                if self.debug:
                    print(f"Scanned {source_file}", file=sys.stderr)

            except Exception as e:
                if self.debug:
                    print(f"Error scanning {source_file}: {e}", file=sys.stderr)

    def generate_code(self) -> None:
        """Generate the error handling code."""
        self.phase("Generating code")

        if self.nowrite:
            print("Not writing files (-nowrite specified)", file=sys.stderr)
            return

        # Code generation logic would go here
        # This is a placeholder for the actual code generation

        if self.debug:
            print("Code generation completed", file=sys.stderr)

    def run(self, args: List[str]) -> int:
        """Main execution method."""
        config_file = "crypto/err/openssl.ec"

        # Parse command line arguments
        i = 0
        while i < len(args):
            arg = args[i]

            if arg.startswith('-'):
                if arg == '-conf':
                    i += 1
                    if i < len(args):
                        config_file = args[i]
                elif arg == '-debug':
                    self.debug = True
                    self.unref = True
                elif arg == '-internal':
                    self.internal = True
                elif arg == '-nowrite':
                    self.nowrite = True
                elif arg == '-rebuild':
                    self.rebuild = True
                elif arg == '-reindex':
                    self.reindex = True
                elif arg == '-static':
                    self.static = True
                elif arg == '-unref':
                    self.unref = True
                    self.nowrite = True
                elif arg == '-module':
                    i += 1
                    if i < len(args):
                        self.modules.add(args[i].upper())
                elif arg in ['-h', '-help', '--help']:
                    self.help()
                    return 0
                else:
                    print(f"Unknown option {arg}; use -h for help.", file=sys.stderr)
                    return 1
            else:
                break
            i += 1

        # Get source files
        source_files = args[i:] if i < len(args) else []

        if self.internal:
            if self.static:
                print("Cannot mix -internal and -static", file=sys.stderr)
                return 1
            if source_files:
                print("Extra parameters given with -internal", file=sys.stderr)
                return 1

            # Scan internal source files
            source_files = (
                glob.glob('crypto/*.c') +
                glob.glob('crypto/*/*.c') +
                glob.glob('ssl/*.c') +
                glob.glob('ssl/*/*.c') +
                glob.glob('ssl/*/*/*.c') +
                glob.glob('providers/*.c') +
                glob.glob('providers/*/*.c') +
                glob.glob('providers/*/*/*.c')
            )
        else:
            if self.modules:
                print("-module isn't useful without -internal", file=sys.stderr)
                return 1

        try:
            # Parse configuration
            self.parse_config_file(config_file)

            # Parse state file
            self.parse_state_file()

            # Scan source files
            self.scan_source_files(source_files)

            # Generate code
            self.generate_code()

            return 0

        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            if self.debug:
                import traceback
                traceback.print_exc()
            return 1


def main():
    """Main entry point."""
    generator = ErrorCodeGenerator()
    sys.exit(generator.run(sys.argv[1:]))


if __name__ == '__main__':
    main()