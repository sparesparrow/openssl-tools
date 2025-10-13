[settings]
os=Macos
arch=armv8
compiler=apple-clang
compiler.version=14.0
compiler.libcxx=libc++
build_type=Release

[conf]
tools.cmake.cmaketoolchain:generator=Ninja

[buildenv]
CC=clang
CXX=clang++
CFLAGS=-O2 -g
CXXFLAGS=-O2 -g