# Hermetic Linux GCC 11 Profile
# Ensures completely reproducible builds with pinned toolchain

[settings]
os=Linux
arch=x86_64
compiler=gcc
compiler.version=11
compiler.libcxx=libstdc++11
build_type=Release

[conf]
# Pin exact tool versions for reproducibility
tools.cmake.cmaketoolchain:generator=Ninja
tools.cmake.cmake_program=/usr/bin/cmake
tools.build.cross_building:can_run=False

# Hermetic compiler settings - exact paths
tools.env:CC=/usr/bin/gcc-11
tools.env:CXX=/usr/bin/g++-11
tools.env:CMAKE_C_COMPILER=/usr/bin/gcc-11
tools.env:CMAKE_CXX_COMPILER=/usr/bin/g++-11
tools.env:AR=/usr/bin/gcc-ar-11
tools.env:RANLIB=/usr/bin/gcc-ranlib-11

# Reproducible build flags
tools.env:CFLAGS=-ffile-prefix-map=$PWD=. -fdebug-prefix-map=$PWD=. -D_GLIBCXX_USE_CXX11_ABI=1 -fPIC
tools.env:CXXFLAGS=-ffile-prefix-map=$PWD=. -fdebug-prefix-map=$PWD=. -D_GLIBCXX_USE_CXX11_ABI=1 -fPIC -std=c++17
tools.env:LDFLAGS=-Wl,--as-needed

# Compiler cache configuration
tools.env:CCACHE_DIR=/cache/ccache
tools.env:CCACHE_MAXSIZE=5G
tools.env:CCACHE_COMPRESS=true
tools.env:CCACHE_COMPRESSLEVEL=6
tools.env:CCACHE_HASHDIR=true

# Build parallelization
tools.cmake.cmaketoolchain:jobs=8
tools.build:jobs=8

# Package cache optimization
tools.cache:default_cache_folder=/cache/conan

[buildenv]
# Minimal, controlled environment
PATH=/usr/bin:/bin:/usr/lib/ccache
LD_LIBRARY_PATH=
PKG_CONFIG_PATH=
PYTHONPATH=

# Force specific toolchain
CC=/usr/bin/gcc-11
CXX=/usr/bin/g++-11
AR=/usr/bin/gcc-ar-11
RANLIB=/usr/bin/gcc-ranlib-11

# Reproducible environment
SOURCE_DATE_EPOCH=1640995200
TZ=UTC
LANG=C.UTF-8
LC_ALL=C.UTF-8