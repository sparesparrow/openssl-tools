# Conan profile for CI macOS x86_64 builds

[settings]
os=Macos
arch=x86_64
compiler=apple-clang
compiler.version=14
compiler.libcxx=libc++
build_type=Release

[options]
# OpenSSL specific options for macOS CI
openssl/*:shared=True
openssl/*:fips=True
openssl/*:enable_quic=True
openssl/*:enable_lms=True
openssl/*:enable_demos=True
openssl/*:enable_h3demo=True
openssl/*:enable_unit_test=True

[buildenv]
# macOS environment
CC=clang
CXX=clang++
CFLAGS=-O2 -g
CXXFLAGS=-O2 -g

# OpenSSL CI specific
OSSL_RUN_CI_TESTS=1
HARNESS_JOBS=4

[conf]
tools.system.package_manager:mode=install
tools.env:CONAN_CPU_COUNT=4
tools.build:jobs=4
