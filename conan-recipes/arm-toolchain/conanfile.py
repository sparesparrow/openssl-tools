import os
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, copy, download
from conan.tools.scm import Version


class ArmToolchainPackage(ConanFile):
    name = "arm-toolchain"
    version = "13.2"
    license = "ARM-GNU-Toolchain-EULA"
    url = "https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads"
    description = (
        "ARM GNU prebuilt cross-compilation toolchain for Linux x86_64 targeting "
        "Linux ARM (32/64). Packaged as a Conan tool_require."
    )
    settings = "os", "arch"
    package_type = "application"
    exports_sources = "LICENSE*"

    def _archs32(self) -> list:
        return ["armv6", "armv7", "armv7hf"]

    def _archs64(self) -> list:
        return ["armv8", "armv8.3"]

    def _get_toolchain(self, target_arch: str):
        if target_arch in self._archs32():
            return (
                "arm-none-linux-gnueabihf",
                "df0f4927a67d1fd366ff81e40bd8c385a9324fbdde60437a512d106215f257b3",
            )
        return (
            "aarch64-none-linux-gnu",
            "12fcdf13a7430655229b20438a49e8566e26551ba08759922cdaf4695b0d4e23",
        )

    def validate(self):
        # Build machine (settings == settings_build for --build-require)
        if self.settings.os != "Linux" or self.settings.arch != "x86_64":
            raise ConanInvalidConfiguration(
                f"This toolchain can only run on Linux-x86_64 (got {self.settings.os}-{self.settings.arch})."
            )

        # Target machine (comes from host profile via settings_target)
        valid_archs = self._archs32() + self._archs64()
        if getattr(self, "settings_target", None) is None:
            raise ConanInvalidConfiguration(
                "settings_target is missing. Create with --build-require and provide host profile."
            )
        if self.settings_target.os != "Linux" or self.settings_target.arch not in valid_archs:
            allowed = ",".join(valid_archs)
            raise ConanInvalidConfiguration(
                f"This toolchain only supports building for Linux-({allowed}). "
                f"Got {self.settings_target.os}-{self.settings_target.arch}."
            )
        if self.settings_target.compiler != "gcc":
            raise ConanInvalidConfiguration(
                f"Only gcc is supported for target compiler (got {self.settings_target.compiler})."
            )
        ver = Version(str(self.settings_target.compiler.version))
        if ver >= Version("14") or ver < Version("13"):
            raise ConanInvalidConfiguration(
                f"Only gcc 13.X is supported for target compiler (got {self.settings_target.compiler.version})."
            )

    def source(self):
        # License is behind an EULA gate; store a reference/license placeholder
        download(
            self,
            "https://developer.arm.com/GetEula?Id=37988a7c-c40e-4b78-9fd1-62c20b507aa8",
            "LICENSE",
            verify=False,
        )

    def build(self):
        toolchain, sha = self._get_toolchain(str(self.settings_target.arch))
        url = (
            "https://developer.arm.com/-/media/Files/downloads/gnu/13.2.rel1/binrel/"
            f"arm-gnu-toolchain-13.2.rel1-x86_64-{toolchain}.tar.xz"
        )
        get(self, url, sha256=sha, strip_root=True)

    def package_id(self):
        # Make package id depend on target settings, keep only arch to split 32/64
        self.info.settings_target = self.settings_target
        self.info.settings_target.rm_safe("os")
        self.info.settings_target.rm_safe("compiler")
        self.info.settings_target.rm_safe("build_type")

    def package(self):
        toolchain, _ = self._get_toolchain(str(self.settings_target.arch))
        for dir_name in [toolchain, "bin", "include", "lib", "libexec"]:
            copy(
                self,
                pattern=f"{dir_name}/*",
                src=self.build_folder,
                dst=self.package_folder,
                keep_path=True,
            )
        copy(
            self,
            "LICENSE",
            src=self.build_folder,
            dst=os.path.join(self.package_folder, "licenses"),
            keep_path=False,
        )

    def package_info(self):
        toolchain, _ = self._get_toolchain(str(self.settings_target.arch))
        self.cpp_info.bindirs.append(os.path.join(self.package_folder, toolchain, "bin"))
        self.conf_info.define(
            "tools.build:compiler_executables",
            {"c": f"{toolchain}-gcc", "cpp": f"{toolchain}-g++", "asm": f"{toolchain}-as"},
        )


