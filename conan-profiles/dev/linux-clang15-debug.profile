[settings]
os=Linux
arch=x86_64
compiler=clang
compiler.version=15
compiler.libcxx=libstdc++11
build_type=Debug

[conf]
tools.cmake.cmaketoolchain:generator=Ninja
tools.system.package_manager:mode=install
tools.system.package_manager:sudo=True

[buildenv]
CC=clang
CXX=clang++
CFLAGS=-O0 -g -DDEBUG
CXXFLAGS=-O0 -g -DDEBUG