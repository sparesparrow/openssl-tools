[settings]
os=Windows
arch=x86
compiler=msvc
compiler.version=193
compiler.runtime=dynamic
build_type=Release

[conf]
tools.cmake.cmaketoolchain:generator=Visual Studio 17 2022
tools.system.package_manager:mode=install
tools.system.package_manager:sudo=False

[buildenv]
CC=cl
CXX=cl