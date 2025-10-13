# Conan profile for CI Linux Clang builds
# Used for Clang-specific builds in CI

[settings]
os=Linux
arch=x86_64
compiler=clang
compiler.version=15
compiler.libcxx=libstdc++11
build_type=Release

[options]
# OpenSSL specific options for Clang CI
openssl/*:shared=True
openssl/*:fips=False
openssl/*:enable_quic=True
openssl/*:enable_demos=True
openssl/*:enable_h3demo=True
openssl/*:enable_unit_test=True
openssl/*:enable_buildtest_c++=True

# Sanitizer builds
openssl/*:enable_asan=False
openssl/*:enable_ubsan=False
openssl/*:enable_msan=False
openssl/*:enable_tsan=False

[buildenv]
# Clang environment
CC=clang-15
CXX=clang++-15
CFLAGS=-O2 -g -fstack-protector-strong
CXXFLAGS=-O2 -g -fstack-protector-strong

# OpenSSL CI specific
OSSL_RUN_CI_TESTS=1
HARNESS_JOBS=4

[conf]
tools.system.package_manager:mode=install
tools.system.package_manager:sudo=True
tools.env:CONAN_CPU_COUNT=4
tools.build:jobs=4