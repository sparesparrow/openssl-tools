from conan import ConanFile
from conan.tools.files import copy, save, get
from conan.tools.cmake import cmake_layout
import os
import json

class OpenSSLSSLConan(ConanFile):
    name = "openssl-ssl"
    version = "3.2.0"
    description = "OpenSSL SSL/TLS library component"
    
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": True,
        "fPIC": True
    }
    
    def requirements(self):
        self.requires(f"openssl-crypto/{self.version}")
    
    def layout(self):
        """Conan 2.0 requirement for proper path handling"""
        cmake_layout(self)
    
    def generate(self):
        """Conan 2.0 compliance - OpenSSL uses its own Configure system"""
        pass
    
    def source(self):
        # Copy from local openssl-source or download
        local_source = os.path.join(os.path.dirname(self.recipe_folder), "openssl-source")
        if os.path.exists(local_source) and os.path.exists(os.path.join(local_source, "Configure")):
            self.output.info(f"Using local OpenSSL source from: {local_source}")
            copy(self, "*", src=local_source, dst=self.source_folder, keep_path=True)
        else:
            self.output.info("Downloading OpenSSL source...")
            get(self, 
                "https://github.com/openssl/openssl/archive/refs/heads/master.tar.gz",
                destination=self.source_folder,
                strip_root=True)
    
    def build(self):
        configure_args = [
            "linux-x86_64",
            "shared" if self.options.shared else "no-shared",
            "no-comp", "no-hw", "no-engine",
            f"--prefix={self.package_folder}",
            f"--openssldir={self.package_folder}/ssl"
        ]
        
        self.output.info(f"Configuring OpenSSL SSL with: {' '.join(configure_args)}")
        self.run(f"perl Configure {' '.join(configure_args)}")
        self.run("make -j$(nproc || echo 4)")
    
    def package(self):
        copy(self, "libssl*", src=self.build_folder, 
             dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        
        manifest = {
            "component": "openssl-ssl", 
            "version": self.version,
            "libraries": ["libssl"],
            "dependencies": ["openssl-crypto"]
        }
        save(self, os.path.join(self.package_folder, "component-manifest.json"),
             json.dumps(manifest, indent=2))
    
    def package_info(self):
        self.cpp_info.libs = ["ssl"]
        self.cpp_info.components["ssl"].libs = ["ssl"]
        self.cpp_info.components["ssl"].requires = ["openssl-crypto::crypto"]
