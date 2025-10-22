#!/usr/bin/env python3
"""
Conan CLI - Unified command-line interface for Conan development
Cross-platform replacement for bash scripts
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import Optional

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from conan_orchestrator import ConanOrchestrator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ConanCLI:
    """Unified Conan CLI interface"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.orchestrator = ConanOrchestrator(self.project_root)
    
    def install(self, profile: Optional[str] = None, verbose: bool = False, clean: bool = False):
        """Install Conan dependencies"""
        print("🚀 Installing Conan dependencies...")
        
        if profile:
            print(f"📋 Profile: {profile}")
        else:
            print(f"📋 Profile: {self.orchestrator._get_default_profile()} (default)")
        
        success = self.orchestrator.install(profile=profile, verbose=verbose, clean=clean)
        
        if success:
            print("\n✅ Installation complete!")
            print("💡 Next step: Run 'conan-cli build' to build the package")
        else:
            print("\n❌ Installation failed!")
            sys.exit(1)
    
    def build(self, profile: Optional[str] = None, verbose: bool = False, clean: bool = False, test: bool = False):
        """Build Conan package"""
        print("🔨 Building Conan package...")
        
        if profile:
            print(f"📋 Profile: {profile}")
        else:
            print(f"📋 Profile: {self.orchestrator._get_default_profile()} (default)")
        
        success = self.orchestrator.build(profile=profile, verbose=verbose, clean=clean, test=test)
        
        if success:
            print("\n✅ Build complete!")
            print("📁 Build artifacts: build/ and package/ directories")
        else:
            print("\n❌ Build failed!")
            sys.exit(1)
    
    def test(self, profile: Optional[str] = None, verbose: bool = False):
        """Run Conan tests"""
        print("🧪 Running Conan tests...")
        
        if profile:
            print(f"📋 Profile: {profile}")
        else:
            print(f"📋 Profile: {self.orchestrator._get_default_profile()} (default)")
        
        success = self.orchestrator.test(profile=profile, verbose=verbose)
        
        if success:
            print("\n✅ Tests completed successfully!")
        else:
            print("\n❌ Tests failed!")
            sys.exit(1)
    
    def setup(self, force: bool = False):
        """Set up Conan development environment"""
        print("🚀 Setting up Conan development environment...")
        
        success = self.orchestrator.setup_environment(force=force)
        
        if success:
            print("\n✅ Development environment ready!")
            print("\n🎯 Quick commands:")
            print("  conan-cli install    - Install dependencies")
            print("  conan-cli build      - Build package")
            print("  conan-cli install -p linux-clang15  - Use specific profile")
            print("  conan-cli build -t   - Build and test")
            print("\n📚 For more options, use: conan-cli --help")
        else:
            print("\n❌ Setup failed!")
            sys.exit(1)
    
    def list_profiles(self):
        """List available profiles"""
        print("📋 Available Conan profiles:")
        print()
        
        for name, profile in self.orchestrator.profiles.items():
            print(f"  {name:20} - {profile.os:8} {profile.compiler:12} {profile.compiler_version:4} ({profile.build_type:7})")
        
        print()
        print("💡 Use: conan-cli install -p <profile> or conan-cli build -p <profile>")
    
    def info(self):
        """Show environment information"""
        print("🔍 Conan Development Environment Info:")
        print()
        
        self.orchestrator.show_info()
        
        print()
        print("📋 Available profiles:")
        for name in self.orchestrator.profiles.keys():
            print(f"  - {name}")
        
        print()
        print("💡 Use 'conan-cli list-profiles' for detailed profile information")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Conan CLI - Cross-platform Conan development tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  conan-cli setup                    # Set up development environment
  conan-cli install                  # Install dependencies (default profile)
  conan-cli build                    # Build package (default profile)
  conan-cli install -p linux-clang15 # Use specific profile
  conan-cli build -t                 # Build and test
  conan-cli test                     # Run tests only
  conan-cli list-profiles            # Show available profiles
  conan-cli info                     # Show environment info
        """
    )
    
    parser.add_argument("command", 
                       choices=["setup", "install", "build", "test", "list-profiles", "info"],
                       help="Command to execute")
    parser.add_argument("-p", "--profile", 
                       help="Conan profile to use")
    parser.add_argument("-v", "--verbose", 
                       action="store_true", 
                       help="Verbose output")
    parser.add_argument("-c", "--clean", 
                       action="store_true", 
                       help="Clean before operation")
    parser.add_argument("-t", "--test", 
                       action="store_true", 
                       help="Run tests after build")
    parser.add_argument("-f", "--force", 
                       action="store_true", 
                       help="Force setup (recreate environment)")
    
    args = parser.parse_args()
    
    # Initialize CLI
    cli = ConanCLI()
    
    # Execute command
    try:
        if args.command == "setup":
            cli.setup(force=args.force)
        elif args.command == "install":
            cli.install(profile=args.profile, verbose=args.verbose, clean=args.clean)
        elif args.command == "build":
            cli.build(profile=args.profile, verbose=args.verbose, clean=args.clean, test=args.test)
        elif args.command == "test":
            cli.test(profile=args.profile, verbose=args.verbose)
        elif args.command == "list-profiles":
            cli.list_profiles()
        elif args.command == "info":
            cli.info()
        else:
            logger.error(f"Unknown command: {args.command}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()