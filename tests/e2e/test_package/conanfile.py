#!/usr/bin/env python3
"""
OpenSSL Test Package
Validates that OpenSSL package is correctly built and exported
"""

from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.files import copy
import os


class OpenSSLTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps", "CMakeToolchain"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.15]")

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        # Run the test executable
        self.run(os.path.join(self.cpp.build.bindirs[0], "test_openssl"))
        
        # Additional validation
        self._validate_headers()
        self._validate_libraries()
        self._validate_environment()

    def _validate_headers(self):
        """Validate that OpenSSL headers are properly exported"""
        self.output.info("Validating OpenSSL headers...")
        
        # Check for key header files
        include_dir = self.deps_cpp_info["openssl"].includedirs[0]
        key_headers = [
            "openssl/ssl.h",
            "openssl/crypto.h",
            "openssl/evp.h",
            "openssl/err.h",
            "openssl/bio.h",
            "openssl/rand.h"
        ]
        
        for header in key_headers:
            header_path = os.path.join(include_dir, header)
            if not os.path.exists(header_path):
                raise Exception(f"Required header not found: {header}")
        
        self.output.success("✓ All required headers found")

    def _validate_libraries(self):
        """Validate that OpenSSL libraries are properly exported"""
        self.output.info("Validating OpenSSL libraries...")
        
        # Check for key library files
        lib_dir = self.deps_cpp_info["openssl"].libdirs[0]
        
        # Check for both static and shared libraries
        lib_files = os.listdir(lib_dir)
        
        ssl_libs = [f for f in lib_files if f.startswith("libssl") or f.startswith("ssl")]
        crypto_libs = [f for f in lib_files if f.startswith("libcrypto") or f.startswith("crypto")]
        
        if not ssl_libs:
            raise Exception("SSL library not found")
        if not crypto_libs:
            raise Exception("Crypto library not found")
            
        self.output.success(f"✓ Found SSL libraries: {ssl_libs}")
        self.output.success(f"✓ Found Crypto libraries: {crypto_libs}")

    def _validate_environment(self):
        """Validate OpenSSL environment configuration"""
        self.output.info("Validating OpenSSL environment...")
        
        # Check environment variables
        env_vars = self.deps_env_info["openssl"].vars
        if "OPENSSL_CONF" in env_vars:
            self.output.info(f"✓ OPENSSL_CONF: {env_vars['OPENSSL_CONF']}")
        
        # Check PATH
        path_vars = self.deps_env_info["openssl"].PATH
        if path_vars:
            self.output.info(f"✓ PATH updated with: {path_vars}")
        
        self.output.success("✓ Environment configuration validated")