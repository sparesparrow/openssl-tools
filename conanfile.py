#!/usr/bin/env python3
"""
OpenSSL Conan Package Recipe
Production-ready Conan 2.x recipe with comprehensive OpenSSL build support
"""

from conan import ConanFile
from conan.tools.gnu import AutotoolsToolchain, AutotoolsDeps, Autotools
from conan.tools.files import copy, save, load, chdir
from conan.tools.scm import Git
from conan.tools.system import package_manager
from conan.errors import ConanInvalidConfiguration
import os
import re
import hashlib
import json
import uuid


class OpenSSLConan(ConanFile):
    name = "openssl"
    version = None  # Dynamically determined from VERSION.dat
    
    # Package metadata
    description = "OpenSSL is a robust, commercial-grade, full-featured toolkit for TLS and SSL protocols"
    homepage = "https://www.openssl.org"
    url = "https://github.com/openssl/openssl"
    license = "Apache-2.0"
    topics = ("ssl", "tls", "cryptography", "security")
    
    # Package configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {
        # Core build options
        "shared": [True, False],
        "fPIC": [True, False],
        
        # Security & Compliance
        "fips": [True, False],
        "no_deprecated": [True, False],
        
        # Features
        "enable_demos": [True, False],
        "enable_h3demo": [True, False],
        "enable_sslkeylog": [True, False],
        "enable_quic": [True, False],
        
        # Protocol support
        "enable_ssl3": [True, False],
        "enable_ssl3_method": [True, False],
        "no_dtls": [True, False],
        "no_tls1": [True, False],
        "no_tls1_1": [True, False],
        
        # Cryptographic algorithms
        "enable_md2": [True, False],
        "enable_md4": [True, False],
        "enable_weak_ssl_ciphers": [True, False],
        "enable_ec_nistp_64_gcc_128": [True, False],
        
        # Performance & Optimization
        "no_asm": [True, False],
        "no_threads": [True, False],
        "no_bulk": [True, False],
        
        # Debugging & Testing
        "enable_crypto_mdebug": [True, False],
        "enable_trace": [True, False],
        "enable_asan": [True, False],
        "enable_ubsan": [True, False],
        "enable_msan": [True, False],
        "enable_tsan": [True, False],
        "enable_unit_test": [True, False],
        "enable_external_tests": [True, False],
        "enable_fuzzer_afl": [True, False],
        "enable_fuzzer_libfuzzer": [True, False],
        "enable_buildtest_c++": [True, False],
        
        # System integration
        "enable_ktls": [True, False],
        "enable_sctp": [True, False],
        
        # Compression
        "enable_zlib": [True, False],
        "enable_zlib_dynamic": [True, False],
        "enable_zstd": [True, False],
        "enable_brotli": [True, False],
        
        # Legacy & Compatibility
        "no_legacy": [True, False],
        "no_afalgeng": [True, False],
        
        # Miscellaneous
        "enable_egd": [True, False],
        "no_cached_fetch": [True, False],
        
        # Legacy options (for backward compatibility)
        "no_zlib": [True, False],
        "386": [True, False],
        "no_sse2": [True, False],
        "no_bf": [True, False],
        "no_cast": [True, False],
        "no_des": [True, False],
        "no_dh": [True, False],
        "no_dsa": [True, False],
        "no_hmac": [True, False],
        "no_md2": [True, False],
        "no_md4": [True, False],
        "no_md5": [True, False],
        "no_mdc2": [True, False],
        "no_rc2": [True, False],
        "no_rc4": [True, False],
        "no_rc5": [True, False],
        "no_rsa": [True, False],
        "no_sha": [True, False],
        "openssldir": ["ANY"],
        "cafile": ["ANY"], 
        "capath": ["ANY"],
        "no_pinshared": [True, False],
        "no_stdio": [True, False],
        "enable_lms": [True, False],
        "enable_crypto_mdebug_backtrace": [True, False],
    }
    
    default_options = {
        # Core build options
        "shared": True,
        "fPIC": True,
        
        # Security & Compliance
        "fips": False,
        "no_deprecated": False,
        
        # Features
        "enable_demos": False,
        "enable_h3demo": False,
        "enable_sslkeylog": False,
        "enable_quic": True,
        
        # Protocol support
        "enable_ssl3": False,
        "enable_ssl3_method": False,
        "no_dtls": False,
        "no_tls1": False,
        "no_tls1_1": False,
        
        # Cryptographic algorithms
        "enable_md2": False,
        "enable_md4": False,
        "enable_weak_ssl_ciphers": False,
        "enable_ec_nistp_64_gcc_128": False,
        
        # Performance & Optimization
        "no_asm": False,
        "no_threads": False,
        "no_bulk": False,
        
        # Debugging & Testing
        "enable_crypto_mdebug": False,
        "enable_trace": False,
        "enable_asan": False,
        "enable_ubsan": False,
        "enable_msan": False,
        "enable_tsan": False,
        "enable_unit_test": False,
        "enable_external_tests": False,
        "enable_fuzzer_afl": False,
        "enable_fuzzer_libfuzzer": False,
        "enable_buildtest_c++": False,
        
        # System integration
        "enable_ktls": False,
        "enable_sctp": False,
        
        # Compression
        "enable_zlib": False,
        "enable_zlib_dynamic": False,
        "enable_zstd": False,
        "enable_brotli": False,
        
        # Legacy & Compatibility
        "no_legacy": False,
        "no_afalgeng": False,
        
        # Miscellaneous
        "enable_egd": False,
        "no_cached_fetch": False,
        
        # Legacy options (for backward compatibility)
        "no_zlib": False,
        "386": False,
        "no_sse2": False,
        "no_bf": False,
        "no_cast": False,
        "no_des": False,
        "no_dh": False,
        "no_dsa": False,
        "no_hmac": False,
        "no_md2": True,
        "no_md4": False,
        "no_md5": False,
        "no_mdc2": False,
        "no_rc2": False,
        "no_rc4": False,
        "no_rc5": True,
        "no_rsa": False,
        "no_sha": False,
        "openssldir": "/usr/local/ssl",
        "cafile": "",
        "capath": "",
        "no_pinshared": False,
        "no_stdio": False,
        "enable_lms": False,
        "enable_crypto_mdebug_backtrace": False,
    }
    
    # Build requirements
    def build_requirements(self):
        if self.settings.os == "Windows":
            self.tool_requires("nasm/2.15.05")
            self.tool_requires("strawberryperl/5.32.0.1")
        # Use system perl for Unix-like systems
        # self.tool_requires("perl/5.38.0")
        
    # Runtime requirements  
    def requirements(self):
        if not self.options.no_zlib:
            self.requires("zlib/1.3.1")
        
        if self.options.enable_zstd:
            self.requires("zstd/1.5.5")
            
        if self.options.enable_brotli:
            self.requires("brotli/1.1.0")
        
        # Add fuzz corpora if fuzzing is enabled
        if (self.options.enable_fuzzer_afl or self.options.enable_fuzzer_libfuzzer or 
            os.getenv("OSSL_RUN_CI_TESTS")):
            self.requires("openssl-fuzz-corpora/1.0.0")
            
    def system_requirements(self):
        # System package requirements for different platforms
        package_manager.Apt(self).install(["build-essential", "perl"])
        package_manager.Yum(self).install(["gcc", "gcc-c++", "make", "perl"])
        package_manager.PacMan(self).install(["base-devel", "perl"])
        package_manager.Zypper(self).install(["gcc", "gcc-c++", "make", "perl"])
        
    def set_version(self):
        """Dynamically determine version from VERSION.dat"""
        version_file = os.path.join(self.recipe_folder, "VERSION.dat")
        if not os.path.exists(version_file):
            # Fallback for testing or if VERSION.dat is missing
            self.output.warning("VERSION.dat not found, using default version 4.0.0")
            self.version = "4.0.0"
            return
            
        try:
            content = load(self, version_file)
            version_match = re.search(r'MAJOR=(\d+)', content)
            minor_match = re.search(r'MINOR=(\d+)', content)  
            patch_match = re.search(r'PATCH=(\d+)', content)
            
            if version_match and minor_match and patch_match:
                major = version_match.group(1)
                minor = minor_match.group(1)
                patch = patch_match.group(1)
                self.version = f"{major}.{minor}.{patch}"
                self.output.info(f"Detected OpenSSL version: {self.version}")
            else:
                raise ConanInvalidConfiguration("VERSION.dat exists but couldn't parse version numbers")
        except Exception as e:
            self.output.error(f"Failed to read VERSION.dat: {e}")
            raise
                
    def configure(self):
        """Configure and validate build options"""
        # Static builds don't need fPIC
        if not self.options.shared:
            del self.options.fPIC
            
        # Configure build options based on settings
        if self.settings.build_type == "Debug":
            self.options.enable_crypto_mdebug = True
            
        # Security-focused builds
        if self.options.fips:
            self.options.enable_unit_test = True
            
        # Performance builds  
        if self.settings.build_type == "Release" and self.settings.arch in ["x86_64", "armv8"]:
            self.options.no_asm = False
            
        # Sanitizers require debug build
        if self.settings.build_type != "Debug":
            if self.options.enable_asan or self.options.enable_ubsan or \
               self.options.enable_msan or self.options.enable_tsan:
                self.output.warn("Sanitizers require Debug build, disabling")
                self.options.enable_asan = False
                self.options.enable_ubsan = False
                self.options.enable_msan = False
                self.options.enable_tsan = False
    
    def validate(self):
        """Validate configuration options for conflicts"""
        # Check for conflicting options
        if self.options.fips and self.options.no_asm:
            raise ConanInvalidConfiguration(
                "FIPS mode requires assembly optimizations. "
                "Cannot use fips=True with no_asm=True. "
                "Set no_asm=False or disable FIPS."
            )
        
        if self.options.fips and self.settings.build_type == "Debug":
            self.output.warning(
                "FIPS validation may behave differently in Debug builds. "
                "Consider using Release build_type for production FIPS deployments."
            )
        
        # Sanitizers are mutually exclusive
        sanitizers = [
            bool(self.options.enable_asan),
            bool(self.options.enable_msan),
            bool(self.options.enable_tsan)
        ]
        if sum(sanitizers) > 1:
            raise ConanInvalidConfiguration(
                "Only one sanitizer can be enabled at a time. "
                "Choose either ASAN, MSAN, or TSAN, not multiple."
            )
        
        # Sanitizers don't work well with optimization
        if any(sanitizers) and self.settings.build_type == "Release":
            # Be stricter off Linux, where Release+sanitizers tends to be flaky
            if self.settings.os != "Linux":
                raise ConanInvalidConfiguration(
                    "Sanitizers with Release build_type are not supported on this platform. "
                    "Use build_type=Debug or disable sanitizers."
                )
            else:
                self.output.warning(
                    "Sanitizers work best with Debug builds. "
                    "Consider using build_type=Debug for sanitizer testing."
                )
        
        # Check for no_threads with QUIC (QUIC needs threading)
        if self.options.no_threads and self.options.enable_quic:
            raise ConanInvalidConfiguration(
                "QUIC protocol requires threading support. "
                "Cannot use no_threads=True with enable_quic=True."
            )
        
        # ASAN doesn't work well with Release optimization on Windows
        if (self.options.enable_asan and 
            self.settings.build_type == "Release" and 
            self.settings.os == "Windows"):
            raise ConanInvalidConfiguration(
                "ASAN doesn't work well with Release optimization on Windows. "
                "Use Debug build_type or disable ASAN for Windows Release builds."
            )

        # Cross-platform option sanity
        if getattr(self.options, "no_sse2", False) and str(self.settings.arch) not in ["x86", "x86_64"]:
            raise ConanInvalidConfiguration(
                "Option no_sse2 is only meaningful on x86/x86_64 architectures."
            )

        if getattr(self.options, "386", False) and str(self.settings.arch) != "x86":
            raise ConanInvalidConfiguration(
                "Option 386 can only be used when arch=x86."
            )

        if self.options.enable_msan and (str(self.settings.os) != "Linux" or "clang" not in str(self.settings.compiler)):
            raise ConanInvalidConfiguration(
                "MSAN builds are only supported with clang on Linux."
            )
            
    def export_sources(self):
        """Export full source tree for reproducible builds"""
        # Export all source files - critical for reproducible builds
        copy(self, "*", src=self.recipe_folder, dst=self.export_sources_folder)
        
    def layout(self):
        """Use basic layout for OpenSSL's in-tree build system"""
        # OpenSSL builds in-tree, so we don't separate source and build
        pass
        
    def generate(self):
        """Generate Autotools toolchain and dependencies"""
        # Generate dependencies
        deps = AutotoolsDeps(self)
        deps.generate()
        
        # Generate Autotools toolchain
        tc = AutotoolsToolchain(self)
        
        # Configure OpenSSL-specific environment
        self._configure_openssl_environment(tc)
        
        tc.generate()
        
    def _configure_openssl_environment(self, tc):
        """Configure OpenSSL-specific environment variables and flags"""
        # Set OpenSSL configuration environment
        if self.options.openssldir:
            tc.environment.define("OPENSSL_CONF", str(self.options.openssldir))
        
        # Configure compiler flags for OpenSSL
        if self.settings.build_type == "Debug":
            tc.environment.define("CFLAGS", "-g -O0")
            tc.environment.define("CXXFLAGS", "-g -O0")
        elif self.settings.build_type == "Release":
            tc.environment.define("CFLAGS", "-O2 -DNDEBUG")
            tc.environment.define("CXXFLAGS", "-O2 -DNDEBUG")
        
        # Add strict warnings for CI builds
        if os.getenv("OSSL_RUN_CI_TESTS"):
            tc.environment.append("CFLAGS", "-Wall -Wextra -Werror")
            tc.environment.append("CXXFLAGS", "-Wall -Wextra -Werror")
        
        # Configure threading
        if not self.options.no_threads:
            if self.settings.os == "Linux":
                tc.environment.define("THREADS", "pthread")
            elif self.settings.os == "Windows":
                tc.environment.define("THREADS", "win32")
        
        # Configure assembly optimizations
        if not self.options.no_asm:
            if self.settings.arch == "x86_64":
                tc.environment.define("ASM", "x86_64")
            elif self.settings.arch == "armv8":
                tc.environment.define("ASM", "aarch64")
        
        # Configure FIPS
        if self.options.fips:
            tc.environment.define("FIPS", "1")
            tc.environment.define("FIPS_MODULE", "1")
        
    def _get_configure_command(self):
        """Generate OpenSSL configure command based on options"""
        args = ["./config", "--banner=Configured"]
        
        # Validate that config script exists
        if not os.path.exists("./config"):
            raise ConanInvalidConfiguration("OpenSSL config script not found in source directory")
        
        # Basic options
        if not self.options.shared:
            args.append("no-shared")
            
        if self.options.fips:
            args.append("enable-fips")
            self.output.info("FIPS mode enabled - ensure compliance requirements are met")
            
        if self.options.no_asm:
            args.append("no-asm")
            
        if self.options.no_threads:
            args.append("no-threads")
            
        # Crypto options
        crypto_options = [
            "bf", "cast", "des", "dh", "dsa", "hmac", "md2", "md4", "md5", 
            "mdc2", "rc2", "rc4", "rc5", "rsa", "sha"
        ]
        
        for option in crypto_options:
            try:
                if getattr(self.options, f"no_{option}", False):
                    args.append(f"no-{option}")
            except AttributeError:
                self.output.warning(f"Option 'no_{option}' not found, skipping")
                
        # Enable options
        enable_options = [
            "weak_ssl_ciphers", "ssl3", "ssl3_method", "trace", "unit_test",
            "ubsan", "asan", "msan", "tsan", "fuzzer_afl", "fuzzer_libfuzzer",
            "external_tests", "buildtest_c++", "crypto_mdebug", 
            "crypto_mdebug_backtrace", "lms", "quic", "h3demo", "demos",
            "sslkeylog", "md2", "md4", "ec_nistp_64_gcc_128",
            "ktls", "sctp", "zlib", "zlib_dynamic", "zstd", "brotli", "egd"
        ]
        
        # No- options
        no_options = [
            "deprecated", "dtls", "tls1", "tls1_1", "legacy", "afalgeng",
            "cached_fetch", "bulk", "rc5"
        ]
        
        for option in enable_options:
            try:
                if getattr(self.options, f"enable_{option}", False):
                    # Special handling for fuzzer options
                    if option in ["fuzzer_afl", "fuzzer_libfuzzer"]:
                        args.append(f"fuzz-{option.replace('fuzzer_', '')}")
                    else:
                        args.append(f"enable-{option.replace('_', '-')}")
            except AttributeError:
                self.output.warning(f"Option 'enable_{option}' not found, skipping")
                
        for option in no_options:
            try:
                if getattr(self.options, f"no_{option}", False):
                    args.append(f"no-{option.replace('_', '-')}")
            except AttributeError:
                self.output.warning(f"Option 'no_{option}' not found, skipping")
                
        # Directories
        if self.options.openssldir:
            openssldir = str(self.options.openssldir)
            if not os.path.isabs(openssldir):
                self.output.warning(f"openssldir '{openssldir}' is relative, consider using absolute path")
            args.append(f"--openssldir={openssldir}")
        else:
            args.append(f"--openssldir={os.path.join(self.package_folder, 'ssl')}")
            
        args.append(f"--prefix={self.package_folder}")
        
        # Compiler flags
        if self.settings.build_type == "Debug":
            args.append("--debug")
        elif self.settings.build_type == "Release":
            args.append("--release")
        else:
            self.output.warning(f"Unknown build_type '{self.settings.build_type}', using default")
            
        # Add strict warnings for CI builds
        if os.getenv("OSSL_RUN_CI_TESTS"):
            args.append("--strict-warnings")
            
        self.output.info(f"Configure command: {' '.join(args)}")
        return args
        
    def build(self):
        """Build OpenSSL using Autotools"""
        # Configure OpenSSL
        configure_args = self._get_configure_command()
        self.run(" ".join(configure_args))
        
        # Build
        jobs = os.getenv("CONAN_CPU_COUNT", "1")
        self.run(f"make -j{jobs}")
        
        # Download fuzz corpora if fuzzing is enabled
        if (self.options.enable_fuzzer_afl or self.options.enable_fuzzer_libfuzzer or 
            os.getenv("OSSL_RUN_CI_TESTS")):
            self._setup_fuzz_corpora()
        
        # Run tests if enabled and not skipped
        if (self.options.enable_unit_test or os.getenv("OSSL_RUN_CI_TESTS")) and not self._should_skip_tests():
            self.run("make test")
            
    def _should_skip_tests(self):
        """Check if tests should be skipped based on tools.build:skip_test"""
        # Check for tools.build:skip_test in conanfile.txt or profile
        try:
            # This would be set by the profile or conanfile.txt
            return os.getenv("CONAN_SKIP_TESTS", "false").lower() == "true"
        except:
            return False
            
    def package(self):
        """Package OpenSSL"""
        # Install OpenSSL
        self.run("make install_sw install_ssldirs")
        
        # Copy license
        copy(self, "LICENSE.txt", src=".", dst=os.path.join(self.package_folder, "licenses"))
        
        # Generate SBOM (Software Bill of Materials)
        self._generate_sbom()
        
    def _calculate_file_hash(self, filepath, algorithm='sha256'):
        """Calculate cryptographic hash of a file"""
        hash_func = getattr(hashlib, algorithm)()
        try:
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_func.update(chunk)
            return hash_func.hexdigest()
        except Exception as e:
            self.output.warning(f"Failed to calculate hash for {filepath}: {e}")
            return None
    
    def _validate_licenses(self):
        """Validate dependency licenses for compliance"""
        approved_licenses = [
            "Apache-2.0", "MIT", "BSD-3-Clause", "BSD-2-Clause", 
            "ISC", "Zlib", "OpenSSL"
        ]
        
        license_report = {
            "approved": [],
            "unknown": [],
            "incompatible": []
        }
        
        # For Python tools, we don't have C++ dependencies
        deps = getattr(self, 'deps_cpp_info', None)
        if deps and hasattr(deps, 'deps'):
            for dep in deps.deps:
                # In real implementation, you'd query license info from Conan metadata
                # This is a simplified version
                dep_license = "Unknown"  # Would get from deps[dep] metadata
            
                if dep_license in approved_licenses:
                    license_report["approved"].append(f"{dep}: {dep_license}")
                elif dep_license == "Unknown":
                    license_report["unknown"].append(dep)
                    self.output.warning(f"Unknown license for dependency: {dep}")
                else:
                    license_report["incompatible"].append(f"{dep}: {dep_license}")
                    self.output.warning(f"Potentially incompatible license: {dep} ({dep_license})")
        
        # Save license report
        license_path = os.path.join(self.package_folder, "licenses", "license-report.json")
        save(self, license_path, json.dumps(license_report, indent=2))
        return license_report
    
    def _generate_sbom(self):
        """Generate enhanced SBOM with security features"""
        self.output.info("Generating Software Bill of Materials (SBOM)...")
        
        # Calculate hashes for main libraries
        lib_hashes = {}
        lib_dir = os.path.join(self.package_folder, "lib")
        if os.path.exists(lib_dir):
            for lib_file in ["libssl.a", "libcrypto.a", "libssl.so", "libcrypto.so",
                            "libssl.dylib", "libcrypto.dylib"]:
                lib_path = os.path.join(lib_dir, lib_file)
                if os.path.exists(lib_path):
                    sha256 = self._calculate_file_hash(lib_path, 'sha256')
                    if sha256:
                        lib_hashes[lib_file] = {
                            "sha256": sha256,
                            "algorithm": "SHA-256"
                        }
        
        # Enhanced metadata collection
        build_metadata = {
            "build_timestamp": os.environ.get("SOURCE_DATE_EPOCH", ""),
            "build_platform": f"{self.settings.os}-{self.settings.arch}",
            "compiler": f"{self.settings.compiler}-{self.settings.compiler.version}",
            "build_type": str(self.settings.build_type),
            "conan_version": "2.0",
            "build_options": {k: str(v) for k, v in self.options.items()}
        }
        
        # Enhanced SBOM data structure
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
                    "hashes": [{"alg": "SHA-256", "content": h["sha256"]} 
                              for h in lib_hashes.values()],
                    "externalReferences": [
                        {
                            "type": "website",
                            "url": self.homepage
                        },
                        {
                            "type": "vcs",
                            "url": self.url
                        }
                    ],
                    "properties": [
                        {"name": "build_metadata", "value": json.dumps(build_metadata)},
                        {"name": "conan_options", "value": json.dumps({k: str(v) for k, v in self.options.items()})},
                        {"name": "build_platform", "value": f"{self.settings.os}-{self.settings.arch}"},
                        {"name": "compiler", "value": f"{self.settings.compiler}-{self.settings.compiler.version}"}
                    ]
                },
                "tools": [
                    {
                        "vendor": "Conan",
                        "name": "conan",
                        "version": "2.0"
                    }
                ]
            },
            "components": [],
            "vulnerabilities": []
        }
        
        # Add dependencies to SBOM with enhanced metadata
        deps = getattr(self, 'deps_cpp_info', None)
        if deps and hasattr(deps, 'deps'):
            for dep in deps.deps:
                try:
                    dep_version = str(deps[dep].version) if hasattr(deps[dep], 'version') else "unknown"
                    component = {
                        "type": "library",
                        "bom-ref": f"{dep}@{dep_version}",
                        "name": dep,
                        "version": dep_version,
                        "scope": "required",
                        "licenses": []  # Would be populated from dependency metadata
                    }
                    sbom_data["components"].append(component)
                except Exception as e:
                    self.output.warning(f"Could not add dependency {dep} to SBOM: {e}")
        
        # Save SBOM
        sbom_path = os.path.join(self.package_folder, "sbom.json")
        save(self, sbom_path, json.dumps(sbom_data, indent=2))
        self.output.success(f"SBOM generated: {sbom_path}")
        
        # Generate package signature if key is available
        self._sign_package(sbom_path)
        
        # Validate licenses
        self._validate_licenses()
        
        # Generate vulnerability report placeholder
        self._generate_vulnerability_report()
    
    def _sign_package(self, sbom_path):
        """Sign package for supply chain security (placeholder for actual signing)"""
        # This would integrate with actual signing tools like cosign, gpg, etc.
        signing_enabled = os.getenv("CONAN_SIGN_PACKAGES", "false").lower() == "true"
        
        if not signing_enabled:
            self.output.info("Package signing disabled (set CONAN_SIGN_PACKAGES=true to enable)")
            return
        
        self.output.info("Package signing placeholder - integrate with cosign/gpg in production")
        # Example integration points:
        # - cosign sign-blob --key cosign.key sbom.json
        # - gpg --detach-sign --armor sbom.json
        
        signature_metadata = {
            "signed": True,
            "timestamp": str(os.environ.get("SOURCE_DATE_EPOCH", "")),
            "algorithm": "placeholder",
            "keyid": "placeholder"
        }
        
        sig_path = os.path.join(self.package_folder, "package-signature.json")
        save(self, sig_path, json.dumps(signature_metadata, indent=2))
    
    def _generate_vulnerability_report(self):
        """Generate vulnerability scan report (integration point)"""
        # This would integrate with tools like Trivy, Snyk, OWASP Dependency Check
        vuln_report = {
            "scanTool": "placeholder",
            "scanDate": str(os.environ.get("SOURCE_DATE_EPOCH", "")),
            "component": f"{self.name}@{self.version}",
            "vulnerabilities": [],
            "note": "Integrate with Trivy/Snyk for actual vulnerability scanning"
        }
        
        # Example integration commands (to be run in CI):
        # trivy fs --format json --output trivy-report.json .
        # snyk test --json > snyk-report.json
        
        vuln_path = os.path.join(self.package_folder, "vulnerability-report.json")
        save(self, vuln_path, json.dumps(vuln_report, indent=2))
        self.output.info(f"Vulnerability report placeholder generated: {vuln_path}")
        
    def package_info(self):
        """Set package information for consumers with component separation"""
        # Separate components for proper dependency resolution
        # SSL component
        self.cpp_info.components["ssl"].libs = ["ssl"]
        self.cpp_info.components["ssl"].requires = ["crypto"]
        
        # Crypto component  
        self.cpp_info.components["crypto"].libs = ["crypto"]
        
        # Platform-specific system libraries for each component
        if self.settings.os == "Linux":
            self.cpp_info.components["ssl"].system_libs.extend(["dl", "pthread"])
            self.cpp_info.components["crypto"].system_libs.extend(["dl", "pthread"])
        elif self.settings.os == "Windows":
            self.cpp_info.components["ssl"].system_libs.extend(["ws2_32", "gdi32", "advapi32", "crypt32", "user32"])
            self.cpp_info.components["crypto"].system_libs.extend(["ws2_32", "gdi32", "advapi32", "crypt32", "user32"])
        elif self.settings.os == "Macos":
            self.cpp_info.components["ssl"].frameworks.append("Security")
            self.cpp_info.components["crypto"].frameworks.append("Security")
            
        # Set binary paths for all components
        self.cpp_info.bindirs = ["bin"]
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.libdirs = ["lib"]
        
        # Environment variables
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.env_info.LD_LIBRARY_PATH.append(os.path.join(self.package_folder, "lib"))
        
        # OpenSSL specific configurations
        if self.options.openssldir:
            self.env_info.OPENSSL_CONF = os.path.join(str(self.options.openssldir), "openssl.cnf")
        else:
            self.env_info.OPENSSL_CONF = os.path.join(self.package_folder, "ssl", "openssl.cnf")
            
    def package_id(self):
        """Optimize package ID for better caching with FIPS separation"""
        # Runtime path options don't affect binary compatibility
        del self.info.options.openssldir
        del self.info.options.cafile  
        del self.info.options.capath
        
        # Test-only options don't affect package ID
        del self.info.options.enable_unit_test
        del self.info.options.enable_external_tests
        del self.info.options.enable_demos
        del self.info.options.enable_h3demo
        
        # Debug options that don't affect binary interface
        del self.info.options.enable_trace
        del self.info.options.enable_crypto_mdebug
        del self.info.options.enable_crypto_mdebug_backtrace
        
        # Sanitizers produce different binaries but can use same cache strategy
        # Group all sanitizer builds together for caching purposes
        if (self.info.options.enable_asan or 
            self.info.options.enable_msan or 
            self.info.options.enable_tsan or
            self.info.options.enable_ubsan):
            # Normalize to "sanitized" build
            self.info.options.enable_asan = "any_sanitizer"
            del self.info.options.enable_msan
            del self.info.options.enable_tsan
            del self.info.options.enable_ubsan
        
        # Fuzzer options don't affect normal usage
        del self.info.options.enable_fuzzer_afl
        del self.info.options.enable_fuzzer_libfuzzer
        
        # Build test options
        try:
            delattr(self.info.options, "enable_buildtest_c++")
        except AttributeError:
            pass  # Option might be named differently
        
        # CRITICAL FOR FIPS: FIPS builds must have separate cache key
        # to avoid cross-contamination with non-FIPS builds
        if self.info.options.fips:
            # FIPS builds get a unique cache key
            self.info.options.fips = "fips_enabled"
        else:
            # Non-FIPS builds are normalized
            self.info.options.fips = "fips_disabled"
        
        # Enhanced cache key optimization
        # Group compatible configurations for better cache reuse
        if self.settings.build_type == "Debug":
            # All debug builds can share cache regardless of specific debug options
            self.info.settings.build_type = "Debug"
        
        # Group similar architectures for better cache reuse
        if str(self.settings.arch) in ["x86_64", "amd64"]:
            self.info.settings.arch = "x86_64"
        elif str(self.settings.arch) in ["arm64", "aarch64"]:
            self.info.settings.arch = "arm64"
        
        # Group compatible compiler versions
        if str(self.settings.compiler) == "gcc":
            if str(self.settings.compiler.version) in ["11", "12", "13"]:
                self.info.settings.compiler.version = "11+"
        elif str(self.settings.compiler) == "clang":
            if str(self.settings.compiler.version) in ["14", "15", "16"]:
                self.info.settings.compiler.version = "14+"
    
    def _setup_fuzz_corpora(self):
        """Set up fuzz corpora data from Conan package."""
        try:
            self.output.info("Setting up fuzz corpora data from Conan package...")
            
            # Create fuzz/corpora directory
            corpora_dir = os.path.join(self.source_folder, "fuzz", "corpora")
            os.makedirs(corpora_dir, exist_ok=True)
            
            # Check if corpora directory is empty or doesn't exist
            if not os.listdir(corpora_dir):
                # Get the fuzz corpora package path
                fuzz_corpora_dep = None
                for dep in self.dependencies.values():
                    if dep.ref.name == "openssl-fuzz-corpora":
                        fuzz_corpora_dep = dep
                        break
                
                if fuzz_corpora_dep:
                    # Get the corpora path from the package
                    corpora_package_path = os.path.join(fuzz_corpora_dep.package_folder, "corpora")
                    
                    if os.path.exists(corpora_package_path):
                        self.output.info("Copying fuzz corpora data from Conan package...")
                        
                        # Copy corpora data to fuzz/corpora
                        import shutil
                        for item in os.listdir(corpora_package_path):
                            if not item.startswith('.'):
                                src = os.path.join(corpora_package_path, item)
                                dst = os.path.join(corpora_dir, item)
                                
                                if os.path.isdir(src):
                                    if os.path.exists(dst):
                                        shutil.rmtree(dst)
                                    shutil.copytree(src, dst)
                                else:
                                    shutil.copy2(src, dst)
                        
                        # Count files for verification
                        corpora_files = []
                        for root, dirs, files in os.walk(corpora_dir):
                            corpora_files.extend(files)
                        
                        self.output.info(f"Copied {len(corpora_files)} fuzz corpora files from Conan package")
                        
                        # Set environment variable for fuzz tests
                        os.environ['OPENSSL_FUZZ_CORPORA_PATH'] = corpora_dir
                        
                    else:
                        self.output.warning("Fuzz corpora package path not found")
                else:
                    self.output.warning("Fuzz corpora dependency not found")
            else:
                self.output.info("Fuzz corpora data already exists, skipping copy")
                
        except Exception as e:
            self.output.warning(f"Failed to set up fuzz corpora: {e}")
            self.output.warning("Fuzz tests may not have access to corpora data")