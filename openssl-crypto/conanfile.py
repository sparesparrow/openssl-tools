from conan import ConanFile
from conan.tools.files import copy, save, get, chdir
from conan.tools.system import package_manager
from conan.tools.cmake import cmake_layout
import os
import json

class OpenSSLCryptoConan(ConanFile):
    name = "openssl-crypto"
    version = "3.2.0"
    description = "OpenSSL cryptographic library component"
    
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "fips": [True, False],
        "enable_fips_module": [True, False]
    }
    default_options = {
        "shared": True,
        "fPIC": True,
        "fips": False,
        "enable_fips_module": False
    }
    
    def requirements(self):
        self.requires("zlib/1.2.13")
        
    def system_requirements(self):
        if self.settings.os == "Linux":
            package_manager.Apt(self).install(["build-essential", "perl"], update=True, check=True)
    
    def layout(self):
        """Conan 2.0 requirement for proper path handling"""
        cmake_layout(self)
    
    def generate(self):
        """Conan 2.0 compliance - OpenSSL uses its own Configure system"""
        pass
    
    def source(self):
        # First try to copy from local openssl-source
        local_source = os.path.join(os.path.dirname(self.recipe_folder), "openssl-source")
        if os.path.exists(local_source) and os.path.exists(os.path.join(local_source, "Configure")):
            self.output.info(f"Using local OpenSSL source from: {local_source}")
            copy(self, "*", src=local_source, dst=self.source_folder, keep_path=True)
        else:
            # Download OpenSSL source
            self.output.info("Downloading OpenSSL source...")
            get(self, 
                "https://github.com/openssl/openssl/archive/refs/heads/master.tar.gz",
                destination=self.source_folder,
                strip_root=True)
    
    def build(self):
        # Verify Configure script exists
        if not os.path.exists(os.path.join(self.source_folder, "Configure")):
            raise Exception(f"Configure script not found in source folder: {self.source_folder}")
        
        configure_args = [
            "linux-x86_64",
            "shared" if self.options.shared else "no-shared",
            "no-ssl3", "no-comp", "no-hw", "no-engine", "no-dso",
            f"--prefix={self.package_folder}",
            f"--openssldir={self.package_folder}/ssl"
        ]
        
        # Add FIPS support if enabled
        if self.options.fips:
            configure_args.append("enable-fips")
            self.output.info("🔒 FIPS mode enabled")
        
        if self.options.enable_fips_module:
            configure_args.append("enable-fips-module")
            self.output.info("🔒 FIPS module enabled")
        
        self.output.info(f"Configuring OpenSSL crypto with: {' '.join(configure_args)}")
        self.run(f"perl Configure {' '.join(configure_args)}")
        
        self.output.info("Building crypto libraries...")
        self.run("make -j$(nproc || echo 4)")
        
        self.output.info("OpenSSL crypto build completed successfully")
    
    def package(self):
        # Copy crypto libraries
        copy(self, "libcrypto*", src=self.build_folder, 
             dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        
        # Copy headers
        copy(self, "*.h", src=os.path.join(self.build_folder, "include"), 
             dst=os.path.join(self.package_folder, "include"), keep_path=True)
        
        # Generate component manifest
        manifest = {
            "component": self.name,
            "version": self.version,
            "build_info": {
                "libraries": ["libcrypto"],
                "headers": ["include/openssl/*.h"],
                "dependencies": ["zlib"],
                "built_at": "BUILD_TIMESTAMP_PLACEHOLDER"
            }
        }
        save(self, os.path.join(self.package_folder, "component-manifest.json"), 
             json.dumps(manifest, indent=2))
        
        self.output.info("✅ OpenSSL Crypto component packaged successfully")
    
    def package_info(self):
        self.cpp_info.libs = ["crypto"]
        self.cpp_info.names["cmake_find_package"] = "OpenSSL"
        self.cpp_info.components["crypto"].libs = ["crypto"]
        self.cpp_info.components["crypto"].includedirs = ["include"]
