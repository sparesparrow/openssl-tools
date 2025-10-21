# OpenSSL Tools - Reusable Modules Guide

This document describes the reusable Python modules copied from `~/Desktop/oms/` and integrated into `openssl-tools`.

## 📦 **Available Modules**

### **1. Foundation Modules** (`openssl_tools.foundation`)

#### **Version Manager** (`version_manager.py`)
**Source**: `~/Desktop/oms/openssl-conan-base/openssl_base/version_manager.py`

**Purpose**: Manages OpenSSL versioning with FIPS metadata support.

**Key Functions**:
```python
from openssl_tools.foundation import get_openssl_version, parse_openssl_version

# Generate version with FIPS metadata
version = get_openssl_version("3.6.0", is_fips=True)
# Result: "3.6.0+fips.20241217T143022.abc12345"

# Parse version string
parsed = parse_openssl_version("3.6.0+fips.20241217T143022.abc12345")
# Result: {
#   "semantic": "3.6.0",
#   "metadata": {
#     "build_type": "fips",
#     "timestamp": "20241217T143022", 
#     "git_hash": "abc12345"
#   }
# }
```

#### **Profile Deployer** (`profile_deployer.py`)
**Source**: `~/Desktop/oms/openssl-conan-base/openssl_base/profile_deployer.py`

**Purpose**: Manages Conan profile deployment and discovery.

**Key Functions**:
```python
from openssl_tools.foundation import deploy_openssl_profiles, list_openssl_profiles

# Deploy profiles to ~/.conan2/profiles/
deploy_openssl_profiles(force=True, verbose=True)

# List available OpenSSL profiles
profiles = list_openssl_profiles()
# Result: ["linux-gcc11-fips", "windows-msvc193", "macos-arm64"]
```

### **2. Security Modules** (`openssl_tools.security`)

#### **SBOM Generator** (`sbom_generator.py`)
**Source**: `~/Desktop/oms/openssl-conan-base/openssl_base/sbom_generator.py`

**Purpose**: Generates CycloneDX SBOMs with FIPS compliance metadata.

**Key Functions**:
```python
from openssl_tools.security import generate_openssl_sbom
from pathlib import Path

# Generate SBOM with FIPS metadata
sbom = generate_openssl_sbom(
    package_name="openssl",
    version="3.6.0+fips.20241217T143022.abc12345",
    is_fips=True,
    fips_cert="FIPS-140-3-Cert-4985",
    dependencies=[
        {
            "type": "library",
            "name": "zlib",
            "version": "1.2.13",
            "purl": "pkg:conan/zlib@1.2.13"
        }
    ],
    output_path=Path("sbom.json")
)
```

### **3. Automation Modules** (`openssl_tools.automation`)

#### **Conan Orchestrator** (`conan_orchestrator.py`)
**Source**: `~/Desktop/oms/openssl-tools/scripts/conan/conan_orchestrator.py`

**Purpose**: Advanced CI/CD automation with comprehensive build management.

**Key Classes**:
```python
from openssl_tools.automation import ConanOrchestrator, BuildConfig, BuildType, Platform
from pathlib import Path

# Initialize orchestrator
orchestrator = ConanOrchestrator(Path("."))

# Set up Conan remote
orchestrator.setup_conan_remote()

# Build package
result = orchestrator.build_package("linux-gcc11-fips", test=True)

# Upload package
orchestrator.upload_package("openssl", "3.6.0")

# Generate build report
report_path = orchestrator.generate_report([result])
```

### **4. Testing Modules** (`openssl_tools.testing`)

#### **Quality Manager** (`quality_manager.py`)
**Source**: `~/Desktop/oms/openssl-tools/openssl_tools/testing/quality_manager.py`

**Purpose**: Comprehensive code quality management with static analysis, coverage, and quality gates.

**Key Classes**:
```python
from openssl_tools.testing.quality_manager import CodeQualityManager
from pathlib import Path

# Initialize quality manager
cqm = CodeQualityManager(Path("."))

# Set up quality configuration
cqm.setup_quality_config()

# Run static analysis
analysis_results = cqm.run_static_analysis()

# Run coverage analysis
coverage_results = cqm.run_coverage_analysis()

# Check quality gates
gate_results = cqm.check_quality_gates(analysis_results, coverage_results)

# Generate comprehensive report
report_path = cqm.generate_quality_report(analysis_results, coverage_results, gate_results)
```

#### **Fuzz Manager** (`fuzz_manager.py`)
**Source**: `~/Desktop/oms/openssl-tools/openssl_tools/testing/fuzz_manager.py`

**Purpose**: Manages fuzz corpora package operations.

**Key Classes**:
```python
from openssl_tools.testing.fuzz_manager import FuzzCorporaManager
from pathlib import Path

# Initialize fuzz manager
fuzz_manager = FuzzCorporaManager()

# Build fuzz corpora package
success = fuzz_manager.build_package("linux-gcc11-fips")

# Set up corpora for fuzz tests
fuzz_manager.setup_corpora_for_fuzz_tests(Path("./fuzz-tests"))
```

### **5. Statistics Modules** (`openssl_tools.statistics`)

#### **BN Random Range** (`bn_rand_range.py`)
**Source**: `~/Desktop/oms/openssl-tools/openssl_tools/statistics/bn_rand_range.py`

**Purpose**: Generates statistical test data for OpenSSL's BigNumber random range testing.

**Usage**:
```bash
# Generate test data for OpenSSL
python -m openssl_tools.statistics.bn_rand_range > test/bn_rand_range.h
```

## 🔧 **Integration Examples**

### **In Conan Recipes**

```python
from conan import ConanFile
from openssl_tools.foundation import get_openssl_version
from openssl_tools.security import generate_openssl_sbom

class OpenSSLConan(ConanFile):
    name = "openssl"
    version = "3.6.0"
    
    def set_version(self):
        # Use version manager for FIPS builds
        if self.options.enable_fips:
            self.version = get_openssl_version(self.version, is_fips=True)
    
    def generate(self):
        # Generate SBOM
        if self.options.enable_fips:
            generate_openssl_sbom(
                package_name=self.name,
                version=self.version,
                is_fips=True,
                fips_cert="FIPS-140-3-Cert-4985"
            )
```

### **In CI/CD Pipelines**

```python
from openssl_tools.automation import ConanOrchestrator
from openssl_tools.testing.quality_manager import CodeQualityManager

# Build and test
orchestrator = ConanOrchestrator(Path("."))
build_result = orchestrator.build_package("linux-gcc11-fips", test=True)

# Quality assurance
cqm = CodeQualityManager(Path("."))
analysis_results = cqm.run_static_analysis()
coverage_results = cqm.run_coverage_analysis()
gate_results = cqm.check_quality_gates(analysis_results, coverage_results)

# Upload if quality gates pass
if gate_results["status"] == "PASSED":
    orchestrator.upload_package("openssl", "3.6.0")
```

### **In Custom Commands**

```python
from conan import ConanFile
from openssl_tools.foundation import deploy_openssl_profiles, list_openssl_profiles

class MyCommand(ConanFile):
    def run(self):
        # Deploy profiles
        deploy_openssl_profiles(force=True)
        
        # List available profiles
        profiles = list_openssl_profiles()
        print(f"Available profiles: {', '.join(profiles)}")
```

## 📋 **Dependencies**

### **Required Python Packages**
```txt
# Foundation modules
pathlib  # Built-in
subprocess  # Built-in
datetime  # Built-in

# Security modules  
uuid  # Built-in
json  # Built-in

# Automation modules
yaml  # pip install pyyaml
dataclasses  # Built-in (Python 3.7+)
enum  # Built-in

# Testing modules
scipy  # pip install scipy (for statistics)
xml.etree.ElementTree  # Built-in
```

### **External Tools**
- **Conan 2.x**: Package manager
- **clang-tidy**: Static analysis
- **cppcheck**: Static analysis  
- **SonarQube**: Code quality
- **gcov/lcov**: Coverage analysis
- **Artifactory/Cloudsmith**: Package repository

## 🚀 **Quick Start**

### **1. Install Dependencies**
```bash
pip install pyyaml scipy
```

### **2. Use in Your Project**
```python
# Import what you need
from openssl_tools.foundation import get_openssl_version, deploy_openssl_profiles
from openssl_tools.security import generate_openssl_sbom
from openssl_tools.automation import ConanOrchestrator

# Deploy profiles
deploy_openssl_profiles()

# Generate FIPS version
version = get_openssl_version("3.6.0", is_fips=True)

# Initialize orchestrator
orchestrator = ConanOrchestrator(Path("."))
```

### **3. Run Quality Checks**
```python
from openssl_tools.testing.quality_manager import CodeQualityManager

cqm = CodeQualityManager(Path("."))
cqm.setup_quality_config()
analysis_results = cqm.run_static_analysis()
```

## 📚 **Further Reading**

- [OpenSSL Tools README](README.md) - Main documentation
- [Conan 2.x Documentation](https://docs.conan.io/2.0/) - Package manager docs
- [CycloneDX Specification](https://cyclonedx.org/) - SBOM format
- [FIPS 140-3 Standard](https://csrc.nist.gov/publications/detail/fips/140/3/final) - Security standard

## 🤝 **Contributing**

These modules are designed to be reusable across the OpenSSL ecosystem. When making changes:

1. **Maintain backward compatibility**
2. **Add comprehensive tests**
3. **Update documentation**
4. **Follow OpenSSL coding standards**

## 📄 **License**

Apache-2.0 (same as OpenSSL)

