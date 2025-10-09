[settings]
os=Linux
arch=x86_64
compiler=gcc
compiler.version=14
compiler.libcxx=libstdc++11
build_type=Release

[conf]
tools.cmake.cmaketoolchain:generator=Ninja
tools.system.package_manager:mode=install
tools.system.package_manager:sudo=True

[buildenv]
CC=gcc
CXX=g++
CFLAGS=-O2 -g
CXXFLAGS=-O2 -g