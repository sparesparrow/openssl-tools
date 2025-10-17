from conan import ConanFile
from conan.tools.files import copy
import os

class OpenSSLToolsConan(ConanFile):
    name = "openssl-tools"
    version = "1.2.0"
    description = "OpenSSL build tools, automation scripts, and infrastructure components"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/openssl-tools"
    homepage = "https://github.com/sparesparrow/openssl-tools"
    topics = ("openssl", "build-tools", "automation", "ci-cd")

    # Export Python package sources for python_requires
    exports_sources = "scripts/*", "profiles/*", "docker/*", "templates/*", ".cursor/*", "openssl_tools/**"
    
    def build_openssl(self, conanfile):
        """Main build orchestration method"""
        settings = conanfile.settings
        options = conanfile.options
        
        # Platform-specific configure
        config_args = self._get_configure_args(settings, options)
        
        # FIPS support
        if options.get_safe("enable_fips"):
            config_args.append("enable-fips")
        
        conanfile.run(f"perl Configure {' '.join(config_args)}")
        
        # Ninja nebo make
        if self._has_ninja(conanfile):
            conanfile.run("ninja -j")
        else:
            from conan.tools.gnu import Autotools
            autotools = Autotools(conanfile)
            autotools.make(args=["-j"])
    
    def _get_configure_args(self, settings, options):
        args = []
        if settings.os == "Windows":
            args.append("VC-WIN64A" if settings.arch == "x86_64" else "VC-WIN32")
        elif settings.os == "Linux":
            args.append(f"linux-{settings.arch}")
            if options.get_safe("fPIC", True):
                args.append("-fPIC")
        elif settings.os == "Macos":
            args.append(f"darwin64-{settings.arch}")
        return args
    
    def _has_ninja(self, conanfile):
        try:
            conanfile.run("ninja --version", capture=True)
            return True
        except:
            return False