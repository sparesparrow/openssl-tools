
1







from conan import ConanFile
from conan.tools.files import copy
import os

class OpenSSLToolsConan(ConanFile):
    name = "openssl-tools"
    version = "1.3.1"
    description = "OpenSSL build tools, automation scripts, and infrastructure components"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/openssl-tools"
    homepage = "https://github.com/sparesparrow/openssl-tools"
    topics = ("openssl", "build-tools", "automation", "ci-cd")

    # Package settings
    package_type = "python-require"
    # Note: python-require packages should not have settings (binary-agnostic)

    # Export sources
    exports_sources = (
        "scripts/*",
        "templates/*",
        "openssl_tools/**",
        "*.md",
        "pyproject.toml"
    )

    python_requires = "openssl-base/1.0.1@sparesparrow/stable"

    def package(self):
        """Package orchestration components"""

        # Copy scripts
#        copy(self, "**", src=os.path.join(self.source_folder, "scripts"),
 #            dst=os.path.join(self.package_folder, "scripts"))

        # Copy templates
  #      copy(self, "**", src=os.path.join(self.source_folder, "templates"),
   #          dst=os.path.join(self.package_folder, "templates"))

        # Copy the Python package
        copy(self, "openssl_tools/*", 
             src=self.source_folder, 
             dst=os.path.join(self.package_folder, "python"))

        # Copy license and readme
        copy(self, "LICENSE*", 
             src=self.source_folder, 
             dst=self.package_folder, 
             keep_path=False)
        copy(self, "README*", 
             src=self.source_folder, 
             dst=self.package_folder, 
             keep_path=False)
    



    def package_info(self):
        """Package information for consumers"""
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []                                                                                             
        self.cpp_info.includedirs = []
                                                                                                  
        python_path = os.path.join(self.package_folder, "python")                                                                                  
        self.runenv_info.define("PYTHONPATH", python_path)                                                                                         
                                                                              
        self.cpp_info.set_property("pkg_config_name", "openssl-tools")   
        self.runenv_info.define("OPENSSL_TOOLS_VERSION", self.version)
        self.runenv_info.define("OPENSSL_TOOLS_ROOT", self.package_folder)
        #self.runenv_info.prepend_path("PYTHONPATH", self.package_folder)
                                                                 │
    def generate(self):
        python_path = os.path.join(self.package_folder, "python")                                                 │
	self.runenv_info.define("PYTHONPATH", python_path)                
