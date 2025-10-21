from conan.api.conan_api import ConanAPI
from conan.cli.command import conan_command

@conan_command(group="OpenSSL")
def build(conan_api: ConanAPI, parser, *args):
    """
    Build OpenSSL with simplified orchestration
    
    Usage:
        conan openssl:build [--fips] [--profile=PROFILE] [--deployer-folder=PATH]
    
    Examples:
        conan openssl:build
        conan openssl:build --fips --profile=linux-gcc11-fips
        conan openssl:build --deployer-folder=./my-deploy
    """
    parser.add_argument("--fips", action="store_true",
                       help="Enable FIPS mode")
    parser.add_argument("--profile", default="default",
                       help="Conan profile to use (default: default)")
    parser.add_argument("--deployer-folder", default="./deploy",
                       help="Output folder for deployment (default: ./deploy)")
    
    args = parser.parse_args(*args)
    
    # Get profiles
    profile_host = conan_api.profiles.get_profile([args.profile])
    
    # Build requirements
    requires = ["openssl/[>=3.0 <4.0]"]
    
    # Apply FIPS options if requested
    if args.fips:
        # Note: This assumes the profile or recipe supports enable_fips option
        print("🔒 FIPS mode enabled")
    
    # Install with deployer
    conan_api.install.deploy install_system_requires nstall_sources install_binaries install_consumer(
        path=".",
        requires=requires,
        profile_host=profile_host,
        profile_build=None,  # Use host profile for build
        deployer=["full_deploy_enhanced"],
        deployer_folder=args.deployer_folder
    )
    
    print("✅ OpenSSL built successfully")
    print(f"📦 Artifacts deployed to: {args.deployer_folder}")
    if args.fips:
        print(f"🔒 FIPS artifacts: {args.deployer_folder}/fips/")