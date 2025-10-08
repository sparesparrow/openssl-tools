# OpenSSL Tools Development Patterns
## Based on openssl-tools Analysis

This document outlines the reusable development patterns, naming conventions, and design principles extracted from the openssl-tools repository analysis.

## 1. Repository Structure Patterns

### Core Directory Structure
```
project-root/
├── conanfile.py                 # Main Conan package definition
├── conf/                        # Configuration files (YAML)
│   ├── 1_artifactory.yaml      # Artifactory/package repository config
│   ├── 1_build.yaml            # Build configuration
│   └── 1_logging.yaml          # Logging configuration
├── launcher/                    # Launcher scripts and GUI tools
│   ├── conan_launcher.py       # Main launcher script
│   ├── buddy_*.bat             # Windows batch launchers
│   └── openssl_developer_buddy_*.py  # GUI launcher applications
├── core/                        # Core functionality modules
│   ├── artifactory_handler.py  # Package repository management
│   ├── config.py               # Configuration management
│   └── utilities.py            # Utility functions
├── conan/                       # Conan-specific functionality
│   ├── conan_functions.py      # Conan operations
│   ├── artifactory_functions.py # Artifactory integration
│   └── client_config.py        # Client configuration
└── util/                        # Utility modules
    ├── custom_logging.py       # Logging utilities
    ├── execute_command.py      # Command execution
    └── file_operations.py      # File operations
```

### Naming Conventions

#### Files and Directories
- **Configuration files**: `{priority}_{category}.yaml` (e.g., `1_artifactory.yaml`)
- **Launcher scripts**: `{tool}_{environment}_{action}.bat` (e.g., `buddy_fcs_CONAN_INIT.bat`)
- **Core modules**: `{functionality}_handler.py` or `{functionality}_module.py`
- **Utility modules**: `{functionality}.py` in util/ directory

#### Classes and Functions
- **Configuration classes**: `{Purpose}Configuration` (e.g., `ConanConfiguration`)
- **Handler classes**: `{Purpose}Handler` (e.g., `ArtifactoryHandler`)
- **Manager classes**: `{Purpose}Manager` (e.g., `ConfigLoaderManager`)
- **Utility functions**: `{action}_{object}` (e.g., `execute_command`, `setup_logging`)

## 2. Conan Package Patterns

### Conanfile.py Structure
```python
class ProjectConan(ConanFile):
    name = 'project-name'
    version = 'auto'  # or specific version
    description = 'Project description'
    topics = ('topic1', 'topic2')
    build_policy = 'missing'
    short_paths = True
    no_copy_source = True  # For Python packages
    
    # Dependencies
    build_requires = [
        'python-environment/version',
        'other-build-tools/version'
    ]
    requires = [
        'runtime-dependencies/version'
    ]
    python_requires = [
        'conan-base-package/version'
    ]
    python_requires_extend = 'conan-base-package.BaseConan'
    
    # SCM configuration
    scm = {
        'type': 'git',
        'url': 'auto',
        'revision': 'auto'
    }
    
    # Options and default_options
    options = {
        'feature_name': [True, False],
        'config_option': ['value1', 'value2']
    }
    default_options = {
        'feature_name': True,
        'config_option': 'value1'
    }
```

### Key Methods Pattern
```python
def set_version(self):
    """Dynamic version detection from git or files"""
    
def configure(self):
    """Configure options based on settings"""
    
def validate(self):
    """Validate configuration for conflicts"""
    
def export_sources(self):
    """Export source files"""
    
def layout(self):
    """Define build layout"""
    
def generate(self):
    """Generate build configuration"""
    
def build(self):
    """Build the package"""
    
def package(self):
    """Package the built artifacts"""
    
def package_info(self):
    """Set package information for consumers"""
    
def package_id(self):
    """Optimize package ID for caching"""
```

## 3. Configuration Management Patterns

### YAML Configuration Structure
```yaml
# conf/1_artifactory.yaml
artifactory:
  schema_version: '1.0'
  root: https://artifactory.example.com:443/artifactory
  user: username
  password: password
  conan_url: https://artifactory.example.com/artifactory/api/conan/repo
  conan_name: repo-name
  conan_paths: [
    /usr/local/bin/conan
    , /opt/conan/bin/conan
  ]

# conf/1_build.yaml
build:
  schema_version: '1.0'
  max_jobs: 4
  enable_ccache: true
  enable_sccache: false
  optimize_build: true
  reproducible_builds: true

# conf/1_logging.yaml
logging:
  schema_version: '1.0'
  level: INFO
  format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
  handlers:
    - type: console
    - type: file
      filename: build.log
```

### Configuration Loader Pattern
```python
class ConfigLoaderManager(ConfigurationBase):
    def _compute_key(self, **kwargs):
        # Compute cache key based on config files and arguments
        files = self.get_config_files(**kwargs)
        files_hash = list(map(lambda file: get_file_metadata(file)['MD5'], files))
        return get_tuple_from_dict({
            'config_files': tuple(files),
            'config_files_hash': tuple(files_hash),
            'additional_arguments': get_tuple_from_dict(additional_arguments),
            'environ': get_tuple_from_dict(dict(os.environ))
        })
    
    def _create_new_configuration(self, **kwargs):
        return ConfigLoaderInstance(self.get_config_files(**kwargs), 
                                  kwargs['additional_arguments'], 
                                  kwargs['ac_merge'])
```

## 4. Launcher System Patterns

### Main Launcher Script Pattern
```python
# launcher/conan_launcher.py
class Configuration:
    def __init__(self, config_data):
        self.data = config_data
        self.load_config()
    
    def load_config(self):
        # Load configuration from YAML files
        pass
    
    def save_config(self):
        # Save configuration to YAML files
        pass

def check_conan_validity(folder_path: Path):
    """Validate that folder contains valid conanfile.py"""
    
def add_packages_paths_to_search_paths(packages):
    """Add package paths to PYTHONPATH and sys.path"""
    
def prepare_package_script_arguments(repository_root, arguments):
    """Prepare script arguments with package path resolution"""
    
def run_package_python_script(repository_root, arguments, wait_till_finish=True):
    """Run Python script with proper environment setup"""
```

### GUI Launcher Pattern
```python
# launcher/openssl_developer_buddy_launcher.py
class Configuration:
    latest_version = '2.0'
    data = {
        'version': latest_version,
        'git_repository': '',
        'remote_setup': '',
    }
    
    def load_config(self):
        # Load from config.yaml
        pass
    
    def save_config(self):
        # Save to config.yaml
        pass

def path_using_dialog():
    """Use GUI dialog to select repository path"""
    
# Main execution
if __name__ == '__main__':
    setup_logging_from_config()
    configuration = Configuration()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Tool Launcher')
    parser.add_argument('-s', '--storedPath', action='store_true', default=True)
    parser.add_argument('-c', '--conanSetup', action='store_true', default=False)
    parser.add_argument('-u', '--update', action='store_true', default=False)
    
    # Setup Conan if needed
    if configuration.data['remote_setup'] != 'passed' or options.conanSetup:
        setup_artifactory_remote()
        setup_parallel_download()
    
    # Get repository path
    if Path(configuration.data['git_repository']).exists() and options.storedPath:
        repository_root = configuration.data['git_repository']
    else:
        repository_root = path_using_dialog()
    
    # Validate and run
    check_conan_validity(Path(repository_root))
    run_package_python_script(repository_root, script_arguments, False)
```

## 5. Artifactory Integration Patterns

### Artifactory Handler Pattern
```python
class ArtifactoryHandler:
    def __init__(self, config_loader):
        self.config = config_loader
        self.connector = None
    
    def _jfrog_authentication(self, repository_path) -> ArtifactoryPath:
        """Authenticate with JFrog Artifactory"""
        artifactory_path = ArtifactoryPath(
            self.config.artifactory.root + '/' + repository_path,
            auth=(self.config.artifactory.user, self.config.artifactory.password)
        )
        return artifactory_path
    
    def connect_to_artifactory(self, repository_path) -> ArtifactoryPath:
        """Connect to Artifactory repository"""
        return self._jfrog_authentication(repository_path)
    
    def get_all_in_path(self, repository_path, target):
        """Download all files from Artifactory path"""
        pass
    
    @staticmethod
    def store_single_file(p, target):
        """Download single file from Artifactory"""
        pass
```

### Conan Artifactory Functions
```python
def setup_artifactory_remote():
    """Setup Artifactory as Conan remote"""
    execute_command(f'{get_default_conan()} remote clean')
    execute_command(f'{get_default_conan()} remote add {artifactory_configuration.nga_conan_name} {artifactory_configuration.nga_conan_url}')
    execute_command(f'{get_default_conan()} user -p {artifactory_configuration.password} -r {artifactory_configuration.nga_conan_name} {artifactory_configuration.user}')

def enable_conan_remote():
    """Enable Artifactory remote"""
    execute_command(f'{get_default_conan()} remote enable {artifactory_configuration.nga_conan_name}')

def disable_conan_remote():
    """Disable Artifactory remote"""
    execute_command(f'{get_default_conan()} remote disable {artifactory_configuration.nga_conan_name}')
```

## 6. Build Optimization Patterns

### Conan Functions with Caching
```python
class ConanConfiguration(ConfigurationBase):
    def __init__(self, conan_tracker=ConanConfigurationTracker()):
        super(ConanConfiguration, self).__init__()
        self.conan_tracker = conan_tracker
    
    def _compute_key(self, **kwargs):
        """Compute cache key for Conan configuration"""
        repo_path = Path(kwargs['repository_path']).resolve()
        conan_lock, exists = self.get_conan_lock(repo_path)
        if exists:
            conan_lock_hash = get_file_metadata(conan_lock)['MD5']
        else:
            conan_lock_hash = None
        return repo_path, get_file_metadata(self.get_conanfile(repo_path))['MD5'], conan_lock_hash
    
    def _create_new_configuration(self, **kwargs):
        """Create new Conan configuration with caching"""
        conan_loader = ConanJsonLoader(kwargs['repository_path'])
        packages = conan_loader.filter_skipped().values()
        # Process packages and return configuration
        return packages_old
```

### Build Optimization Setup
```python
def setup_parallel_download(download_threads=-1):
    """Setup parallel downloads for Conan"""
    execute_command(f'{get_default_conan()} config set general.parallel_download={psutil.cpu_count() if download_threads == -1 else download_threads}')

def remove_conan_lock_files(conan_home=None):
    """Remove Conan lock files for clean builds"""
    if not conan_home:
        conan_home, _ = get_conan_home()
    for path in Path(conan_home).glob('**/_.count'):
        path.unlink(missing_ok=True)
    for path in Path(conan_home).glob('**/_.count.lock'):
        path.unlink(missing_ok=True)
```

## 7. SBOM and Security Patterns

### Enhanced SBOM Generation
```python
def _generate_sbom(self):
    """Generate Software Bill of Materials with security features"""
    sbom_data = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "serialNumber": f"urn:uuid:{uuid.uuid4()}",
        "version": 1,
        "metadata": {
            "timestamp": str(os.environ.get("SOURCE_DATE_EPOCH", "")),
            "component": {
                "type": "library",
                "bom-ref": f"{self.name}@{self.version}",
                "name": self.name,
                "version": str(self.version),
                "description": self.description,
                "licenses": [{"license": {"id": "Apache-2.0"}}],
                "hashes": [{"alg": "SHA-256", "content": h["sha256"]} for h in lib_hashes.values()],
                "externalReferences": [
                    {"type": "website", "url": self.homepage},
                    {"type": "vcs", "url": self.url}
                ],
                "properties": [
                    {"name": "build_metadata", "value": json.dumps(build_metadata)},
                    {"name": "conan_options", "value": json.dumps({k: str(v) for k, v in self.options.items()})},
                    {"name": "build_platform", "value": f"{self.settings.os}-{self.settings.arch}"}
                ]
            }
        },
        "components": [],
        "vulnerabilities": []
    }
    
    # Add dependencies and save SBOM
    save(self, sbom_path, json.dumps(sbom_data, indent=2))
```

### Package Signing Pattern
```python
def _sign_package(self, sbom_path):
    """Sign package for supply chain security"""
    signing_enabled = os.getenv("CONAN_SIGN_PACKAGES", "false").lower() == "true"
    
    if not signing_enabled:
        self.output.info("Package signing disabled (set CONAN_SIGN_PACKAGES=true to enable)")
        return
    
    # Integration points for cosign/gpg signing
    signature_metadata = {
        "signed": True,
        "timestamp": str(os.environ.get("SOURCE_DATE_EPOCH", "")),
        "algorithm": "placeholder",
        "keyid": "placeholder"
    }
    
    sig_path = os.path.join(self.package_folder, "package-signature.json")
    save(self, sig_path, json.dumps(signature_metadata, indent=2))
```

## 8. Error Handling and Logging Patterns

### Custom Logging Setup
```python
def setup_logging_from_config():
    """Setup logging from configuration files"""
    config_loader = get_config_loader()
    logging_config = config_loader.logging
    
    logging.basicConfig(
        level=getattr(logging, logging_config.level),
        format=logging_config.format,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(logging_config.handlers[1].filename)
        ]
    )

def execute_command(command, cwd=None, continuous_print=True, print_out=True, print_command=True, print_err_code=True):
    """Execute command with proper error handling and logging"""
    if print_command:
        log.info(f"Executing command: {command}")
    
    try:
        result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, shell=True)
        
        if continuous_print and print_out:
            print(result.stdout)
        
        if result.stderr and print_err_code:
            print(result.stderr)
        
        return result.returncode, result.stdout.splitlines()
    except Exception as e:
        log.error(f"Command execution failed: {e}")
        return 1, [str(e)]
```

## 9. File Operations Patterns

### File Operations Utilities
```python
def ensure_target_exists(target):
    """Ensure target directory exists"""
    os.makedirs(os.path.dirname(target), exist_ok=True)

def get_file_metadata(filepath):
    """Get file metadata including MD5 hash"""
    import hashlib
    
    with open(filepath, 'rb') as f:
        content = f.read()
        md5_hash = hashlib.md5(content).hexdigest()
    
    stat = os.stat(filepath)
    return {
        'MD5': md5_hash,
        'size': stat.st_size,
        'mtime': stat.st_mtime
    }

def symlink_with_check(source, target, is_directory=False):
    """Create symlink with proper error handling"""
    try:
        if os.path.exists(target):
            if os.path.islink(target):
                os.unlink(target)
            elif os.path.isdir(target):
                shutil.rmtree(target)
            else:
                os.remove(target)
        
        if is_directory:
            os.symlink(source, target, target_is_directory=True)
        else:
            os.symlink(source, target)
    except Exception as e:
        log.error(f"Failed to create symlink {source} -> {target}: {e}")
        raise
```

## 10. Application Patterns

### Main Application Structure
```python
if __name__ == '__main__':
    multiprocessing.freeze_support()
    setup_logging_from_config()
    
    # Handle multi-core processing
    if len(sys.argv) > 2 and (sys.argv[1] == '-m' or sys.argv[1] == '--multiCore'):
        from project.miscellaneous.process_pool import run as pool_run
        sys.exit(pool_run(sys.argv[2:]))
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Tool Description')
    parser.add_argument('-a', '--setupArtifactory', action='store_true', default=False)
    parser.add_argument('-u', '--updateOnly', action='store_true', default=True)
    parser.add_argument('-c', '--runWithConan', nargs=2, dest='conan_arguments')
    parser.add_argument('-p', '--runWithPython', nargs=2, dest='python_arguments')
    parser.add_argument('-s', '--runScript', nargs=2, dest='script_arguments')
    
    options = parser.parse_args(sys.argv[1:])
    
    # Setup environment
    os.environ['PATH'] = str(top_level_path(__file__)) + os.pathsep + os.environ['PATH']
    remove_conan_lock_files()
    enable_conan_remote()
    
    # Handle different execution modes
    if options.setupArtifactory:
        setup_artifactory_remote()
        sys.exit()
    
    if options.conan_arguments:
        # Handle Conan commands
        pass
    
    if options.python_arguments:
        # Handle Python commands
        pass
    
    if options.script_arguments:
        # Handle script execution
        pass
    
    # Default behavior
    if options.updateOnly:
        check_for_updates(False)
        sys.exit()
```

## Implementation Guidelines

1. **Follow the directory structure** exactly as shown
2. **Use the naming conventions** consistently
3. **Implement all key methods** in conanfile.py
4. **Set up configuration management** with YAML files
5. **Create launcher scripts** for easy tool execution
6. **Implement proper error handling** and logging
7. **Add SBOM generation** with security features
8. **Set up build optimization** and caching
9. **Integrate with package repositories** (Artifactory)
10. **Follow the application structure** for main scripts

These patterns provide a robust foundation for Python-based development tools with Conan integration, following the proven patterns from openssl-tools.