[settings]
os=Linux
arch=x86_64
compiler=gcc
compiler.version=11
compiler.libcxx=libstdc++11
build_type=Release

[options]
openssl-tools/*:enable_review_tools=True
openssl-tools/*:enable_release_tools=True
openssl-tools/*:enable_statistics_tools=True
openssl-tools/*:enable_utils=True

[conf]
# Build optimization
tools.cmake.cmaketoolchain:jobs=8
tools.system.package_manager:mode=install
tools.system.package_manager:sudo=True

# Caching configuration
tools.cache:download_cache=True
tools.cache:download_cache_timeout=600
tools.cache:download_cache_retry=3

# Compiler caching
tools.env:CCACHE_DIR=/tmp/ccache
tools.env:CCACHE_MAXSIZE=5G
tools.env:CCACHE_COMPRESS=1
tools.env:CCACHE_HARDLINK=1
tools.env:CCACHE_SLOPPINESS=pch_defines,time_macros

# Build environment
tools.env:MAKEFLAGS=-j8
tools.env:CONAN_CPU_COUNT=8

# Reproducible builds
tools.env:SOURCE_DATE_EPOCH=0
tools.env:TZ=UTC

# Build optimization flags
tools.env:CFLAGS=-O2 -g -pipe -Wall -Werror=format-security -Wp,-D_FORTIFY_SOURCE=2 -fexceptions -fstack-protector-strong --param=ssp-buffer-size=4 -grecord-gcc-switches -m64 -mtune=generic -fPIC
tools.env:CXXFLAGS=-O2 -g -pipe -Wall -Werror=format-security -Wp,-D_FORTIFY_SOURCE=2 -fexceptions -fstack-protector-strong --param=ssp-buffer-size=4 -grecord-gcc-switches -m64 -mtune=generic -fPIC
tools.env:LDFLAGS=-Wl,-z,relro -Wl,--as-needed

[buildenv]
CC=ccache gcc
CXX=ccache g++
AR=gcc-ar
RANLIB=gcc-ranlib
STRIP=strip