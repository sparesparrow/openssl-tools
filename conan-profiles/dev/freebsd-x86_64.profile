[settings]
os=FreeBSD
arch=x86_64
compiler=gcc
compiler.version=11
compiler.libcxx=libstdc++11
build_type=Release

[conf]
tools.cmake.cmaketoolchain:generator=Ninja

[buildenv]
CC=gcc
CXX=g++
CFLAGS=-O2 -g
CXXFLAGS=-O2 -g